import sys
import cv2
import numpy as np
import pickle
import socket
import pyrebase
import face_recognition
import subprocess
from time import sleep
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox

firebase_config = {
        "apiKey": "AIzaSyCApZc-n7Q9FoYDkOQdx4sFads53Wp3Xvs",
        "authDomain": "tkinterpro.firebaseapp.com",
        "databaseURL": "https://tkinterpro-default-rtdb.firebaseio.com",
        "projectId": "tkinterpro",
        "storageBucket": "tkinterpro.appspot.com",
        "messagingSenderId": "672171486478",
        "appId": "1:672171486478:web:f2378b2e4433b560767b5f",
        "measurementId": "G-GYE10SPK5H"
    }    
        
firebase = pyrebase.initialize_app(firebase_config)
db = firebase.database()
db.child("permissions").set("pending")

class StatusChecker(QThread):
    status_changed = pyqtSignal(str)  # Signal to notify the main thread of status changes

    def __init__(self, db):
        super().__init__()
        self.db = db
        self.running = True

    def run(self):
        while self.running:
            status = self.db.child("permissions").get().val()
            self.status_changed.emit(status)
            self.msleep(1000)  # Check status every 1 second


    
class FaceRecognitionApp(QMainWindow):
    def __init__(self):
        self.db = db
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 12345))
        server_socket.listen(1)
        self.client_socket, self.addr = server_socket.accept()

        super().__init__()

        # Initialize the status checker thread
        self.status_checker = StatusChecker(self.db)
        self.status_checker.status_changed.connect(self.handle_status_change)
        self.status_checker.start()

        self.setWindowTitle("Face Recognition")
        self.setGeometry(100, 100, 800, 800)

        self.unknown_counter = 0  # Counter for how long "Unknown" has been displayed
        self.notification_sent = False

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.default_image = QImage(r"data/camera_PH.jpg")  # Replace with the path to your default image
        self.default_pixmap = QPixmap.fromImage(self.default_image)

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setGeometry(10, 10, 780, 580)
        self.video_label.setPixmap(self.default_pixmap)

        self.start_button = QPushButton("Start Cam", self)
        self.start_button.setGeometry(10, 600, 100, 40)
        self.start_button.clicked.connect(self.start_camera)

        self.stop_button = QPushButton("Stop Cam", self)
        self.stop_button.setGeometry(120, 600, 100, 40)
        self.stop_button.clicked.connect(self.stop_camera)

        self.stop_button = QPushButton("Lock relay", self)
        self.stop_button.setGeometry(230, 600, 100, 40)
        self.stop_button.clicked.connect(self.lockRelay)

        self.quit_button = QPushButton("Quit", self)
        self.quit_button.setGeometry(350, 600, 100, 40)
        self.quit_button.clicked.connect(self.close)

        self.camera_active = False
        self.video_capture = cv2.VideoCapture(0)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_video)

        # Load reference data
        with open("data/ref_name.pkl", "rb") as f:
            self.ref_dictt = pickle.load(f)  # ref_dict=ref vs name

        with open("data/ref_embed.pkl", "rb") as f:
            self.embed_dictt = pickle.load(f)  # embed_dict- ref  vs embedding

        self.known_face_encodings = []  # encodingd of faces
        self.known_face_names = []  # ref_id of faces

        for ref_id, embed_list in self.embed_dictt.items():
            for embed in embed_list:
                self.known_face_encodings += [embed]
                self.known_face_names += [ref_id]
    
    def handle_status_change(self, status):
        if status.lower() == "granted":
            self.client_socket.send('1'.encode())
            sleep(5)
            self.db.child("permissions").set("pending")
            self.client_socket.send('0'.encode())
            


    def start_camera(self):
        self.camera_active = True
        self.notification_sent = False
        self.video_capture.open(0)
        self.timer.start(10)
        self.video_label.setPixmap(self.default_pixmap)

    def stop_camera(self):
        self.client_socket.send('0'.encode())
        self.camera_active = False
        self.video_capture.release()
        self.timer.stop()
        self.video_label.setPixmap(self.default_pixmap)

    def lockRelay(self):
        self.client_socket.send('0'.encode())

    def update_video(self):


        if self.camera_active:
            ret, frame = self.video_capture.read()
            if ret:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

                face_names = []
            
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"
                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        self.client_socket.send('1'.encode())
                        # on_off_var.set(1)  # Turn on the button
                    else:
                        self.client_socket.send('0'.encode())
                        # on_off_var.set(0)  # Turn off the button
                    if name == "Unknown":
                        self.unknown_counter += 1
                    else:
                        self.unknown_counter = 0

                    if self.unknown_counter >= 5:  # 30 frames at 10 fps = 3 seconds
                        print("Notification sent")
                        self.db.child("permissions").set("pending")
                        subprocess.Popen(["python", "mobile_phone.py"])
                        self.notification_sent = True
                        self.stop_camera()
                        # # Display a notification popup
                        # if not self.notification_sent:
                        #     reply = QMessageBox.question(self, 'Send Notification',
                        #                                  'Do you want to send a notification?',
                        #                                  QMessageBox.Yes | QMessageBox.No,
                        #                                  QMessageBox.No)
                        #     if reply == QMessageBox.Yes:
                                # print("Notification sent")
                                # self.db.child("permissions").set("pending")
                                # subprocess.Popen(["python", "mobile_phone.py"])
                                # self.notification_sent = True
                                # self.stop_camera()
                            # else:
                            #     print("Notification canceled")
                            #     self.notification_sent = True  # Mark as sent to avoid repeated popups

                    
                    face_names.append(name)

                for (top, right, bottom, left), name in zip(face_locations, face_names):
                    show_name = name if name == 'Unknown' else self.ref_dictt.get(name, 'Unknown')
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4

                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, show_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

                # Assuming frame is in BGR color format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame_rgb.shape
                bytes_per_line = 3 * width
                q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                self.video_label.setPixmap(pixmap)

                # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # img = cv2.resize(img, (800, 600))
                # img = Image.fromarray(img)
                # img = ImageTk.PhotoImage(image=img)
  

def main():
    app = QApplication(sys.argv)
    face_recognition_app = FaceRecognitionApp()
    face_recognition_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
