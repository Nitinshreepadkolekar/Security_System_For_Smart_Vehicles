import sys
import socket
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

class RelayControlApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Relay")
        self.setGeometry(100, 100, 320, 446)  # Set the window size to match the image size
        self.setStyleSheet("background-color: #404040;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.switch_label = QLabel(self)
        self.switch_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.switch_label.setGeometry(0, 0, 320, 446)  # Adjust the size and position of the QLabel

        self.on_image = QPixmap("data/on.png")
        self.off_image = QPixmap("data/off.png")

        self.switch_label.setPixmap(self.off_image)

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('127.0.0.1', 12345))

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                # print(message)
                if message == '1':
                    self.switch_label.setPixmap(self.on_image)
                else:
                    self.switch_label.setPixmap(self.off_image)
            except ConnectionResetError:
                break

def main():
    app = QApplication(sys.argv)
    relay_control_app = RelayControlApp()
    relay_control_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
