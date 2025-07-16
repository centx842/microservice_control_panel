import sys
import time
import psycopg2
import subprocess
import threading
import os
from PyQt5.QtWidgets import (QApplication, QSplashScreen, QLabel, QVBoxLayout,
                             QWidget, QMainWindow, QListWidget, QListWidgetItem,
                             QPushButton, QHBoxLayout, QCheckBox, QDialog,
                             QFormLayout, QLineEdit, QSpinBox, QDialogButtonBox,
                             QMessageBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QPen, QIcon


class ConfigLoader(QThread):
    """Background thread to handle PostgreSQL connection and configuration loading"""
    progress_update = pyqtSignal(str)
    finished = pyqtSignal(bool, str, dict)  # success, message, config_data

    def __init__(self):
        super().__init__()
        self.config_data = {}
        # Default connection parameters (you can modify these)
        self.default_connection = {
            'host': 'localhost',
            'port': 5432,
            'database': 'myapp_db',
            'user': 'postgres',
            'password': 'password'
        }

    def run(self):
        try:
            # Step 1: Connect to PostgreSQL
            self.progress_update.emit("Connecting to PostgreSQL...")
            time.sleep(1)

            conn = self.connect_postgres()
            if not conn:
                self.finished.emit(False, "PostgreSQL connection failed", {})
                return

            # Step 2: Load configuration from database
            self.progress_update.emit("Loading configuration from database...")
            time.sleep(0.5)

            config = self.load_config_from_db(conn)
            if not config:
                self.finished.emit(False, "Failed to load configuration", {})
                return

            # Step 3: Validate microservices files
            self.progress_update.emit("Validating microservices...")
            time.sleep(0.5)

            if not self.validate_microservices(config):
                self.finished.emit(False, "Some microservice files are missing", config)
                return

            # Step 4: Initialize microservices
            self.progress_update.emit("Initializing microservices...")
            time.sleep(1)

            conn.close()
            self.finished.emit(True, "Setup completed successfully", config)

        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}", {})

    def connect_postgres(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.default_connection)

            # Create config table if it doesn't exist
            cursor = conn.cursor()
            cursor.execute('''
                           CREATE TABLE IF NOT EXISTS config
                           (
                               id
                               SERIAL
                               PRIMARY
                               KEY,
                               key
                               VARCHAR
                           (
                               255
                           ) UNIQUE NOT NULL,
                               value TEXT NOT NULL,
                               description TEXT,
                               created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                               )
                           ''')

            # Insert default configuration if table is empty
            cursor.execute("SELECT COUNT(*) FROM config")
            if cursor.fetchone()[0] == 0:
                default_configs = [
                    ('app_name', 'MyApp', 'Application name'),
                    ('app_version', '1.0.0', 'Application version'),
                    ('microservices', 'auth_service.py,data_service.py,api_service.py',
                     'Comma-separated list of microservice files'),
                    ('auto_start', 'auth_service.py,data_service.py', 'Auto-start microservices'),
                    ('log_level', 'INFO', 'Logging level'),
                    ('max_workers', '5', 'Maximum worker threads')
                ]

                for key, value, desc in default_configs:
                    cursor.execute(
                        "INSERT INTO config (key, value, description) VALUES (%s, %s, %s)",
                        (key, value, desc)
                    )

            conn.commit()
            return conn

        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def load_config_from_db(self, conn):
        """Load configuration from database"""
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM config")
            results = cursor.fetchall()

            config = {}
            for key, value in results:
                config[key] = value

            return config

        except Exception as e:
            print(f"Config loading error: {e}")
            return None

    def validate_microservices(self, config):
        """Validate that microservice files exist"""
        try:
            microservices = config.get('microservices', '').split(',')
            microservices = [ms.strip() for ms in microservices if ms.strip()]

            missing_files = []
            for service in microservices:
                if not os.path.exists(service):
                    missing_files.append(service)

            if missing_files:
                print(f"Missing microservice files: {missing_files}")
                # Create dummy files for demo
                for service in missing_files:
                    with open(service, 'w') as f:
                        f.write(f'''# {service}
import time
import sys

def main():
    print(f"Starting {service}...")
    while True:
        print(f"{service} is running...")
        time.sleep(10)

if __name__ == "__main__":
    main()
''')

            return True

        except Exception as e:
            print(f"Microservice validation error: {e}")
            return False


class SettingsDialog(QDialog):
    """Settings dialog for configuration management"""

    def __init__(self, config_data, parent=None):
        super().__init__(parent)
        self.config_data = config_data.copy()
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Create form layout
        form_layout = QFormLayout()

        # Configuration fields
        self.app_name_edit = QLineEdit(self.config_data.get('app_name', ''))
        self.app_version_edit = QLineEdit(self.config_data.get('app_version', ''))
        self.microservices_edit = QTextEdit(self.config_data.get('microservices', ''))
        self.microservices_edit.setMaximumHeight(100)
        self.auto_start_edit = QTextEdit(self.config_data.get('auto_start', ''))
        self.auto_start_edit.setMaximumHeight(100)
        self.log_level_edit = QLineEdit(self.config_data.get('log_level', ''))
        self.max_workers_edit = QSpinBox()
        self.max_workers_edit.setRange(1, 20)
        self.max_workers_edit.setValue(int(self.config_data.get('max_workers', 5)))

        form_layout.addRow("App Name:", self.app_name_edit)
        form_layout.addRow("App Version:", self.app_version_edit)
        form_layout.addRow("Microservices:", self.microservices_edit)
        form_layout.addRow("Auto Start:", self.auto_start_edit)
        form_layout.addRow("Log Level:", self.log_level_edit)
        form_layout.addRow("Max Workers:", self.max_workers_edit)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_config_data(self):
        """Get updated configuration data"""
        return {
            'app_name': self.app_name_edit.text(),
            'app_version': self.app_version_edit.text(),
            'microservices': self.microservices_edit.toPlainText(),
            'auto_start': self.auto_start_edit.toPlainText(),
            'log_level': self.log_level_edit.text(),
            'max_workers': str(self.max_workers_edit.value())
        }


class MainWindow(QMainWindow):
    """Main application window with microservice management"""

    def __init__(self, config_data):
        super().__init__()
        self.config_data = config_data
        self.running_services = {}  # Track running microservices
        self.setWindowTitle(f"{config_data.get('app_name', 'MyApp')} - Control Panel")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()
        self.load_microservices()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel(f"{self.config_data.get('app_name', 'MyApp')} Control Panel")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
            }
        """)

        settings_btn = QPushButton("⚙️ Settings")
        settings_btn.clicked.connect(self.open_settings)
        settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(settings_btn)

        # Splitter for microservices list and controls
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Microservices list
        left_widget = QWidget()
        left_layout = QVBoxLayout()

        services_label = QLabel("Microservices:")
        services_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.services_list = QListWidget()
        self.services_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)

        left_layout.addWidget(services_label)
        left_layout.addWidget(self.services_list)
        left_widget.setLayout(left_layout)

        # Right side - Controls
        right_widget = QWidget()
        right_layout = QVBoxLayout()

        controls_label = QLabel("Controls:")
        controls_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        # Control buttons
        self.start_btn = QPushButton("▶️ Start Selected")
        self.start_btn.clicked.connect(self.start_selected_service)

        self.stop_btn = QPushButton("⏹️ Stop Selected")
        self.stop_btn.clicked.connect(self.stop_selected_service)

        self.start_all_btn = QPushButton("🚀 Start All")
        self.start_all_btn.clicked.connect(self.start_all_services)

        self.stop_all_btn = QPushButton("⏹️ Stop All")
        self.stop_all_btn.clicked.connect(self.stop_all_services)

        # Status display
        status_label = QLabel("Status Log:")
        status_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        self.status_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: monospace;
            }
        """)

        # Style buttons
        button_style = """
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """

        stop_button_style = """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """

        self.start_btn.setStyleSheet(button_style)
        self.start_all_btn.setStyleSheet(button_style)
        self.stop_btn.setStyleSheet(stop_button_style)
        self.stop_all_btn.setStyleSheet(stop_button_style)

        right_layout.addWidget(controls_label)
        right_layout.addWidget(self.start_btn)
        right_layout.addWidget(self.stop_btn)
        right_layout.addWidget(self.start_all_btn)
        right_layout.addWidget(self.stop_all_btn)
        right_layout.addWidget(status_label)
        right_layout.addWidget(self.status_text)
        right_layout.addStretch()

        right_widget.setLayout(right_layout)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 400])

        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(splitter)

        central_widget.setLayout(main_layout)

        # Auto-start services
        self.auto_start_services()

    def load_microservices(self):
        """Load microservices from configuration"""
        microservices = self.config_data.get('microservices', '').split(',')
        microservices = [ms.strip() for ms in microservices if ms.strip()]

        for service in microservices:
            item = QListWidgetItem(f"🔴 {service}")
            item.setData(Qt.UserRole, service)
            self.services_list.addItem(item)

    def auto_start_services(self):
        """Auto-start specified services"""
        auto_start = self.config_data.get('auto_start', '').split(',')
        auto_start = [ms.strip() for ms in auto_start if ms.strip()]

        for service in auto_start:
            self.start_service(service)

    def start_service(self, service_name):
        """Start a microservice"""
        if service_name in self.running_services:
            self.log_status(f"Service {service_name} is already running")
            return

        try:
            # Start the service in a separate process
            process = subprocess.Popen([sys.executable, service_name])
            self.running_services[service_name] = process

            # Update UI
            self.update_service_status(service_name, True)
            self.log_status(f"Started {service_name} (PID: {process.pid})")

        except Exception as e:
            self.log_status(f"Failed to start {service_name}: {str(e)}")

    def stop_service(self, service_name):
        """Stop a microservice"""
        if service_name not in self.running_services:
            self.log_status(f"Service {service_name} is not running")
            return

        try:
            process = self.running_services[service_name]
            process.terminate()
            process.wait(timeout=5)
            del self.running_services[service_name]

            # Update UI
            self.update_service_status(service_name, False)
            self.log_status(f"Stopped {service_name}")

        except Exception as e:
            self.log_status(f"Failed to stop {service_name}: {str(e)}")

    def update_service_status(self, service_name, is_running):
        """Update service status in the list"""
        for i in range(self.services_list.count()):
            item = self.services_list.item(i)
            if item.data(Qt.UserRole) == service_name:
                status = "🟢" if is_running else "🔴"
                item.setText(f"{status} {service_name}")
                break

    def start_selected_service(self):
        """Start selected service"""
        current_item = self.services_list.currentItem()
        if current_item:
            service_name = current_item.data(Qt.UserRole)
            self.start_service(service_name)

    def stop_selected_service(self):
        """Stop selected service"""
        current_item = self.services_list.currentItem()
        if current_item:
            service_name = current_item.data(Qt.UserRole)
            self.stop_service(service_name)

    def start_all_services(self):
        """Start all services"""
        for i in range(self.services_list.count()):
            item = self.services_list.item(i)
            service_name = item.data(Qt.UserRole)
            self.start_service(service_name)

    def stop_all_services(self):
        """Stop all services"""
        for service_name in list(self.running_services.keys()):
            self.stop_service(service_name)

    def log_status(self, message):
        """Log status message"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.config_data, self)
        if dialog.exec_() == QDialog.Accepted:
            new_config = dialog.get_config_data()
            self.update_configuration(new_config)

    def update_configuration(self, new_config):
        """Update configuration in database"""
        # Here you would update the database with new configuration
        # For now, just update local config
        self.config_data.update(new_config)
        self.log_status("Configuration updated")
        QMessageBox.information(self, "Settings", "Configuration updated successfully!")

    def closeEvent(self, event):
        """Handle application close"""
        self.stop_all_services()
        event.accept()


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

        self.main_window = None

    def setup_ui(self):
        """Setup the UI elements"""
        # Create main widget
        self.main_widget = QWidget()
        self.main_widget.setFixedSize(400, 300)

        # Create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # Logo label
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid #3498db;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        # Load logo image
        self.load_logo()

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

    def load_logo(self):
        """Load and display the logo image"""
        logo_path = "logo.png"

        if os.path.exists(logo_path):
            # Load the logo image
            pixmap = QPixmap(logo_path)

            # Scale the logo to fit nicely (max 150x150)
            scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)

        else:
            # Fallback to text logo if image not found
            self.logo_label.setText("🚀 MyApp")
            self.logo_label.setStyleSheet(self.logo_label.styleSheet() + """
                QLabel {
                    color: #2c3e50;
                    font-size: 48px;
                    font-weight: bold;
                }
            """)

            # Create a sample logo.png for demonstration
            self.create_sample_logo(logo_path)

    def create_sample_logo(self, logo_path):
        """Create a sample logo.png file if it doesn't exist"""
        try:
            # Create a simple logo using QPixmap and QPainter
            pixmap = QPixmap(200, 200)
            pixmap.fill(Qt.transparent)

            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)

            # Draw a circular background
            painter.setBrush(QColor(52, 152, 219))  # Blue background
            painter.setPen(QPen(QColor(41, 128, 185), 4))  # Darker blue border
            painter.drawEllipse(20, 20, 160, 160)

            # Draw the rocket emoji-like shape
            painter.setBrush(QColor(255, 255, 255))  # White rocket
            painter.setPen(QPen(QColor(200, 200, 200), 2))

            # Simple rocket shape (triangle + rectangle)
            rocket_points = [
                (100, 40),  # Top point
                (85, 70),  # Left side
                (85, 140),  # Left bottom
                (115, 140),  # Right bottom
                (115, 70),  # Right side
            ]

            from PyQt5.QtGui import QPolygon
            from PyQt5.QtCore import QPoint

            rocket_polygon = QPolygon([QPoint(x, y) for x, y in rocket_points])
            painter.drawPolygon(rocket_polygon)

            # Add some flames at the bottom
            painter.setBrush(QColor(231, 76, 60))  # Red flames
            flame_points = [
                (90, 140),
                (85, 155),
                (95, 150),
                (100, 165),
                (105, 150),
                (115, 155),
                (110, 140)
            ]

            flame_polygon = QPolygon([QPoint(x, y) for x, y in flame_points])
            painter.drawPolygon(flame_polygon)

            painter.end()

            # Save the logo
            pixmap.save(logo_path, "PNG")
            print(f"Sample logo created: {logo_path}")

        except Exception as e:
            print(f"Could not create sample logo: {e}")

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
        self.repaint()

    def on_loading_finished(self, success, message, config_data):
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

            # Update logo with app name from config (only if using text fallback)
            app_name = config_data.get('app_name', 'MyApp')
            if not os.path.exists("logo.png"):
                self.logo_label.setText(f"🚀 {app_name}")

            self.repaint()

            # Create main window
            self.main_window = MainWindow(config_data)

            # Close splash screen after 2 seconds and show main window
            QTimer.singleShot(2000, self.show_main_window)

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

            # Close splash screen after showing error
            QTimer.singleShot(3000, self.close)

    def show_main_window(self):
        """Show the main window and close splash"""
        if self.main_window:
            self.main_window.show()
        self.close()

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