import sys
import cv2
import face_recognition
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QMessageBox, QDialog

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 300, 150)

        self.username_entry = QLineEdit()
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        username_label = QLabel("Username:")
        layout.addWidget(username_label)
        layout.addWidget(self.username_entry)

        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        layout.addWidget(self.password_entry)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_entry.text()
        password = self.password_entry.text()

        if username == "admin" and password == "admin":
            self.accept()  # Close the dialog and continue to the main application
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password. Please try again.")

class RegisterWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Registration")
        self.setGeometry(100, 100, 500, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.name_entry = QLineEdit()
        self.id_entry = QLineEdit()

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        heading_label = QLabel("Face Registration")
        heading_label.setFont(QFont("Helvetica", 16, QFont.Bold))

        layout.addWidget(heading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        name_label = QLabel("Enter Name:")
        layout.addWidget(name_label)
        layout.addWidget(self.name_entry)

        id_label = QLabel("Enter ID:")
        layout.addWidget(id_label)
        layout.addWidget(self.id_entry)

        register_button = QPushButton("Register Face")
        register_button.clicked.connect(self.register_face)
        layout.addWidget(register_button)

        heading_label = QLabel("________________________________")
        layout.addWidget(heading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        heading_label = QLabel("Use 's' Button to save face")
        layout.addWidget(heading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.central_widget.setLayout(layout)

    def register_face(self):
        name = self.name_entry.text()
        ref_id = self.id_entry.text()

        try:
            f = open("data/ref_name.pkl", "rb")
            ref_dictt = pickle.load(f)
            f.close()
        except:
            ref_dictt = {}

        ref_dictt[ref_id] = name

        f = open("data/ref_name.pkl", "wb")
        pickle.dump(ref_dictt, f)
        f.close()

        try:
            f = open("data/ref_embed.pkl", "rb")
            embed_dictt = pickle.load(f)
            f.close()
        except:
            embed_dictt = {}

        for i in range(5):
            key = cv2.waitKey(1)
            webcam = cv2.VideoCapture(0)

            while True:
                check, frame = webcam.read()
                cv2.imshow(f"Capturing Face ({i+1}/5) | (Use 's' Button to save face)", frame)
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                key = cv2.waitKey(1)

                if key == ord('s'):
                    face_locations = face_recognition.face_locations(rgb_small_frame)
                    if face_locations:
                        face_encoding = face_recognition.face_encodings(frame)[0]
                        if ref_id in embed_dictt:
                            embed_dictt[ref_id].append(face_encoding)
                        else:
                            embed_dictt[ref_id] = [face_encoding]
                        webcam.release()
                        cv2.waitKey(1)
                        cv2.destroyAllWindows()
                        break
                elif key == ord('q'):
                    QMessageBox.information(self, "Info", "Registration canceled.")
                    webcam.release()
                    cv2.destroyAllWindows()
                    return

        f = open("data/ref_embed.pkl", "wb")
        pickle.dump(embed_dictt, f)
        f.close()
        QMessageBox.information(self, "Info", "Registration completed successfully.")

def main():
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    
    # Show the login dialog first
    if login_dialog.exec_() == QDialog.Accepted:
        # If login is successful, proceed to the main application
        register_window = RegisterWindow()
        register_window.show()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()
