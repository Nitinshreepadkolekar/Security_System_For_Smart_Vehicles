import sys
import subprocess
import cv2
import face_recognition
from time import sleep
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QMessageBox
import faceRegister as fr
from PyQt5.QtCore import Qt

from PyQt5.QtGui import QFont

def RecognitionWindow():
    # List of Python scripts to run
    scripts = ["faceRecognition.py", "relay_demo.py"]

    # Create a list to store the subprocess objects
    processes = []

    # Start each script in a separate process
    for script in scripts:
        process = subprocess.Popen(["python", script])
        processes.append(process)
        sleep(2)

    # Wait for all processes to finish
    for process in processes:
        process.wait()

def RegisterWindow():
    subprocess.Popen(["python", "faceRegister.py"])
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Face Recognition Based Relay Controller")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        heading_label = QLabel("Face Recognition Based Relay Controller")
        heading_label.setFont(QFont("Helvetica", 16, QFont.Bold))

        layout.addWidget(heading_label, alignment=Qt.AlignmentFlag.AlignCenter)

        admin_button = QPushButton("Admin Panel")
        admin_button.clicked.connect(RegisterWindow)
        layout.addWidget(admin_button, alignment=Qt.AlignmentFlag.AlignCenter)

        start_button = QPushButton("Start System")
        start_button.clicked.connect(RecognitionWindow)
        layout.addWidget(start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.central_widget.setLayout(layout)

def main():
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
