import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QTimer, QSize
import pyrebase
from time import sleep

class GrantPermissionApp(QMainWindow):

    def __init__(self):
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
        self.db = firebase.database()

        super().__init__()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_permission_status)
        self.timer.start(5000)

        self.setWindowTitle("Mobile phone")
        self.setGeometry(100, 100, 350, 578)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.status_label = QLabel("Somebody is asking for\nrelay unlock")
        font = QFont()
        font.setPointSize(18)
        self.status_label.setFont(font)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status_label)

        button_layout = QHBoxLayout()
        self.grant_button = QPushButton("Grant")
        self.grant_button.clicked.connect(self.grant_permission)
        button_layout.addWidget(self.grant_button)

        self.deny_button = QPushButton("Deny")
        self.deny_button.clicked.connect(self.deny_permission)
        button_layout.addWidget(self.deny_button)

        self.layout.addLayout(button_layout)

        # Add the new fingerprint button
        self.fingerprint_button = QPushButton()
        self.fingerprint_button.setIcon(QIcon('data/fpStand.jpg'))
        self.fingerprint_button.setIconSize(QSize(100, 100))
        self.layout.addWidget(self.fingerprint_button)

        self.apply_styles()

        # Variables to handle long press
        self.long_press_duration = 3000  # 3 seconds
        self.long_press_timer = QTimer(self)
        self.long_press_timer.timeout.connect(self.handle_fingerprint_long_press)
        self.fingerprint_button.pressed.connect(self.start_long_press_timer)
        self.fingerprint_button.released.connect(self.stop_long_press_timer)

        

    def apply_styles(self):
        # Stylesheet for QMainWindow
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
        """)

        # Stylesheet for buttons (same as before)
        button_style = """
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #005D99;
            }
            QPushButton:disabled {
                background-color: #dcdcdc;
                color: #777777;
            }
        """
        self.grant_button.setStyleSheet(button_style)
        self.deny_button.setStyleSheet(button_style)

    def check_permission_status(self):
        # Fetch the permission status from Firebase and update the UI
        status = self.db.child("permissions").get().val()
        if status == "pending":
            self.status_label.setText("Somebody is asking for\nrelay unlock")
            self.grant_button.setEnabled(True)
            self.deny_button.setEnabled(True)
        elif status == "granted":
            self.status_label.setText("Permission Granted")
            self.grant_button.setEnabled(False)
            self.deny_button.setEnabled(False)
        elif status == "denied":
            self.status_label.setText("Permission Denied")
            self.grant_button.setEnabled(False)
            self.deny_button.setEnabled(False)

    def grant_permission(self):
        self.db.child("permissions").set("granted")
        sleep(5)
        sys.exit(app.exec_())

    def deny_permission(self):
        self.db.child("permissions").set("denied")
        sleep(5)
        sys.exit(app.exec_())

    def start_long_press_timer(self):
        self.long_press_timer.start(self.long_press_duration)

    def stop_long_press_timer(self):
        self.long_press_timer.stop()

    def handle_fingerprint_long_press(self):
        # Handle the long press action here
        # Change the fingerprint image to fingerprint_access.jpg
        self.fingerprint_button.setIcon(QIcon('data/fpAccess.jpg'))
        self.db.child("permissions").set("granted")

        # Use QTimer to exit the app after 3 seconds
        exit_timer = QTimer(self)
        exit_timer.setSingleShot(True)
        exit_timer.timeout.connect(self.exit_app_after_delay)
        exit_timer.start(3000) 
   
    def exit_app_after_delay(self):
        sys.exit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GrantPermissionApp()
    window.show()
    sys.exit(app.exec_())
