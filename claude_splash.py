import sys
import time
import sqlite3
import json
import os
from PyQt5.QtWidgets import QApplication, QSplashScreen, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QPen
from PyQt5.QtCore import QRect


class ConfigLoader(QThread):
    """Background thread to handle configuration loading and database connection"""
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str)  # success, message

    def __init__(self):
        super().__init__()
        self.config_path = "config.json"
        self.db_path = "database.db"

    def run(self):
        try:
            # Step 1: Load configuration
            self.progress_update.emit("Loading configuration...")
            time.sleep(1)  # Simulate loading time

            config = self.load_config()
            if not config:
                self.finished.emit(False, "Configuration file not found or invalid")
                return

            # Step 2: Validate configuration
            self.progress_update.emit("Validating configuration...")
            time.sleep(0.5)

            if not self.validate_config(config):
                self.finished.emit(False, "Configuration validation failed")
                return

            # Step 3: Connect to database
            self.progress_update.emit("Connecting to database...")
            time.sleep(1)

            if not self.connect_database(config):
                self.finished.emit(False, "Database connection failed")
                return

            # Step 4: Final checks
            self.progress_update.emit("Finalizing setup...")
            time.sleep(0.5)

            self.finished.emit(True, "Setup completed successfully")

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")

    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default config if doesn't exist
                default_config = {
                    "database": {
                        "path": "database.db",
                        "timeout": 30
                    },
                    "app": {
                        "name": "MyApp",
                        "version": "1.0.0"
                    }
                }
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                return default_config
        except Exception:
            return None

    def validate_config(self, config):
        """Validate configuration structure"""
        required_keys = ["database", "app"]
        return all(key in config for key in required_keys)

    def connect_database(self, config):
        """Connect to database"""
        try:
            db_path = config.get("database", {}).get("path", self.db_path)
            timeout = config.get("database", {}).get("timeout", 30)

            # Create database if it doesn't exist
            conn = sqlite3.connect(db_path, timeout=timeout)

            # Create a simple test table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                )
            ''')

            conn.commit()
            conn.close()
            return True

        except Exception:
            return False


class SplashScreen(QSplashScreen):
    """Custom splash screen with transparent background and logo"""

    def __init__(self):
        # Create a transparent pixmap for the base
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.transparent)

        super().__init__(pixmap)

        # Remove window frame and make it stay on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Create the logo and status text
        self.setup_ui()

        # Initialize the config loader
        self.config_loader = ConfigLoader()
        self.config_loader.progress_update.connect(self.update_status)
        self.config_loader.finished.connect(self.on_loading_finished)

        # Center the splash screen
        self.center_on_screen()

    def setup_ui(self):
        """Setup the UI elements"""
        # Create main widget
        self.main_widget = QWidget()
        self.main_widget.setFixedSize(400, 300)

        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Logo label (you can replace this with your actual logo)
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 48px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                -webkit-background-clip: text;
                padding: 20px;
                border-radius: 10px;
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #3498db;
            }
        """)
        self.logo_label.setText("🚀 MyApp")

        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #34495e;
                font-size: 14px;
                font-weight: 500;
                background-color: rgba(255, 255, 255, 0.8);
                padding: 10px 20px;
                border-radius: 15px;
                border: 1px solid #bdc3c7;
            }
        """)

        # Add widgets to layout
        layout.addWidget(self.logo_label)
        layout.addWidget(self.status_label)

        self.main_widget.setLayout(layout)

        # Apply main widget style
        self.main_widget.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)

    def center_on_screen(self):
        """Center the splash screen on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

    def paintEvent(self, event):
        """Custom paint event to draw the splash screen"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw the main widget
        self.main_widget.render(painter)

        painter.end()

    def update_status(self, message):
        """Update the status message"""
        self.status_label.setText(message)
        self.repaint()  # Force repaint to show the update

    def on_loading_finished(self, success, message):
        """Handle loading completion"""
        if success:
            self.status_label.setText("✅ " + message)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 14px;
                    font-weight: 500;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 10px 20px;
                    border-radius: 15px;
                    border: 1px solid #27ae60;
                }
            """)
        else:
            self.status_label.setText("❌ " + message)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 14px;
                    font-weight: 500;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 10px 20px;
                    border-radius: 15px;
                    border: 1px solid #e74c3c;
                }
            """)

        self.repaint()

        # Close splash screen after 2 seconds
        QTimer.singleShot(2000, self.close)

    def start_loading(self):
        """Start the loading process"""
        self.config_loader.start()


def main():
    app = QApplication(sys.argv)

    # Create and show splash screen
    splash = SplashScreen()
    splash.show()

    # Start loading process
    splash.start_loading()

    # Run the application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()