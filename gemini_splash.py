import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QDesktopWidget, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal


# --- Main Application Window (Placeholder) ---
# This is the window that will open after the splash screen finishes.
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
        self.setGeometry(100, 100, 800, 600)
        layout = QVBoxLayout()
        label = QLabel("Welcome to the Main Application!")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 20))
        layout.addWidget(label)
        self.setLayout(layout)


# --- Worker Thread for Background Tasks ---
# Handles time-consuming tasks like loading configs or DB connections.
class Worker(QThread):
    # Signals to communicate with the main thread
    progress = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        """Main work happens here."""
        try:
            self.progress.emit("Loading configuration...")
            time.sleep(1.5)  # Simulate loading a config file

            # --- YOUR CONFIG LOGIC HERE ---
            # if config_is_bad:
            #   raise ValueError("Configuration file is corrupted or missing.")

            self.progress.emit("Connecting to database...")
            time.sleep(1.5)  # Simulate connecting to a database

            # --- YOUR DATABASE CONNECTION LOGIC HERE ---
            # if db_connection_failed:
            #   raise ConnectionError("Could not connect to the database.")

            self.progress.emit("Finalizing setup...")
            time.sleep(1)  # Simulate final tasks

            self.finished.emit()

        except Exception as e:
            self.error.emit(f"An error occurred: {e}")


# --- Splash Screen Window ---
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init_ui()
        self.center_on_screen()

    def init_ui(self):
        """Initializes the user interface of the splash screen."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Logo
        self.logo_label = QLabel()
        # ❗ IMPORTANT: Create a 'logo.png' file (ideally 256x256 or similar)
        pixmap = QPixmap('logo.png')
        self.logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)

        # Status Text
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-size: 14pt;
                font-family: Arial;
            }
        """)

        layout.addWidget(self.logo_label)
        layout.addWidget(self.status_label)

    def center_on_screen(self):
        """Centers the splash screen on the user's monitor."""
        screen_geo = QDesktopWidget().screenGeometry()
        self.move(int((screen_geo.width() - self.width()) / 2),
                  int((screen_geo.height() - self.height()) / 2))

    def update_status(self, message):
        """Updates the status text."""
        self.status_label.setText(message)


def handle_error(message):
    """Displays an error message box and quits the application."""
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText("Initialization Failed")
    msg_box.setInformativeText(message)
    msg_box.setWindowTitle("Error")
    msg_box.exec_()
    app.quit()


# --- Main Execution ---
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create and show the splash screen
    splash = SplashScreen()
    splash.show()

    # Create the main window (but don't show it yet)
    main_win = MainWindow()

    # Create and start the worker thread
    worker = Worker()
    worker.progress.connect(splash.update_status)
    worker.finished.connect(lambda: (splash.close(), main_win.show()))
    worker.error.connect(handle_error)
    worker.start()

    sys.exit(app.exec_())