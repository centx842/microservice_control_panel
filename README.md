# NASTP Control Panel

A modern PyQt5-based microservice management application featuring an animated splash screen and comprehensive control interface for managing distributed services.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🚀 Features

### ✨ **Animated Splash Screen**
- Custom animated NASTP logo (GIF support)
- Real-time loading status updates
- Frameless, transparent design
- Fixed size (prevents window resizing)
- Auto-transitions to main application

### 🎛️ **Microservice Management**
- **Start/Stop Services**: Individual or bulk operations
- **Auto-Start Configuration**: Automatically launch critical services
- **Real-time Status Monitoring**: Live service state tracking
- **Process Management**: Safe termination and cleanup
- **Service Validation**: Automatic file existence checking

### ⚙️ **Configuration Management**
- **Settings Dialog**: Easy configuration editing
- **Database Integration**: PostgreSQL support (optional)
- **Mock Mode**: Database-free operation for development
- **Flexible Configuration**: JSON-style config management

### 🖥️ **Modern UI Design**
- **Responsive Layout**: Splitter-based interface
- **Status Logging**: Real-time activity monitoring
- **Color-coded Indicators**: Visual service status (🟢/🔴)
- **Professional Styling**: Modern flat design with hover effects

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Operating System**: Windows 10/11, Linux, or macOS
- **QGIS Version**: 3.22.16 (if integrating with QGIS)
- **PostgreSQL**: Optional (for database mode)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd SplashScreenDB-master
```

### 2. Set Up Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
```
PyQt5>=5.15.0
psycopg2-binary>=2.9.0  # Optional: for PostgreSQL support
```

### 4. Configure Execution Policy (Windows PowerShell)
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 🎯 Quick Start

### Run the Application
```bash
# Standard mode (no database required)
python claude_v4.py

# Database mode (requires PostgreSQL setup)
python claude_v4_with_db.py
```

### First Launch
1. The animated NASTP splash screen appears
2. Loading status updates in real-time
3. Main control panel opens automatically
4. Microservices are auto-created if missing

## 📁 Project Structure

```
SplashScreenDB-master/
├── claude_v4.py              # Main application (database-free)
├── claude_v4_with_db.py      # Full version with PostgreSQL
├── claude_v3.py              # Previous version
├── claude_splash.py          # Minimal splash screen
├── gemini_splash.py          # Alternative implementation
├── nastp-logo.gif            # Animated logo file
├── logo.png                  # Fallback static logo
├── .venv/                    # Virtual environment
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### 🔧 **Main Components**

| File | Description | Database | UI Features |
|------|-------------|----------|-------------|
| `claude_v4.py` | **Primary application** | None (Mock data) | Full UI + Animated splash |
| `claude_v4_with_db.py` | **Production version** | PostgreSQL | Full UI + Database integration |
| `claude_v3.py` | **Legacy version** | PostgreSQL | Basic UI |
| `claude_splash.py` | **Minimal demo** | None | Splash screen only |

## ⚡ Usage Guide

### 🖥️ **Main Control Panel**

#### **Service Management**
- **View Services**: Left panel shows all configured microservices
- **Service Status**: 
  - 🟢 **Green dot**: Service running
  - 🔴 **Red dot**: Service stopped
- **Individual Control**:
  - Select service → Click "▶️ Start Selected" or "⏹️ Stop Selected"
- **Bulk Operations**:
  - "🚀 Start All": Launch all services
  - "⏹️ Stop All": Terminate all services

#### **Status Monitoring**
- **Real-time Log**: Bottom panel shows service activity
- **Timestamps**: Each action is timestamped
- **Process IDs**: Shows PID for running services
- **Error Handling**: Displays failure messages

### ⚙️ **Settings Configuration**

Click the **"⚙️ Settings"** button to access:

| Setting | Description | Example |
|---------|-------------|---------|
| **App Name** | Application title | `NASTP Control Panel` |
| **App Version** | Version identifier | `2.0.0` |
| **Microservices** | Comma-separated service files | `auth_service.py,data_service.py` |
| **Auto Start** | Services to launch automatically | `auth_service.py,data_service.py` |
| **Log Level** | Logging verbosity | `INFO`, `DEBUG`, `ERROR` |
| **Max Workers** | Thread pool size | `8` |

### 🎨 **Customizing the Logo**

1. **Replace the logo file**:
   ```bash
   # Replace with your animated GIF
   cp your-logo.gif nastp-logo.gif
   ```

2. **Update the code** (if needed):
   ```python
   # In load_logo() method
   logo_path = "your-custom-logo.gif"
   ```

3. **Supported formats**:
   - **GIF**: Animated or static
   - **PNG/JPG**: Static images (fallback)

## 🗄️ Database Configuration

### **PostgreSQL Setup** (Optional)

For the full database version (`claude_v4_with_db.py`):

1. **Install PostgreSQL**
2. **Create Database**:
   ```sql
   CREATE DATABASE myapp_db;
   CREATE USER postgres WITH PASSWORD 'password';
   GRANT ALL PRIVILEGES ON DATABASE myapp_db TO postgres;
   ```

3. **Update Connection Settings**:
   ```python
   # In ConfigLoader class
   self.default_connection = {
       'host': 'localhost',
       'port': 5432,
       'database': 'myapp_db',
       'user': 'postgres',
       'password': 'your_password'
   }
   ```

### **Database Schema**

The application automatically creates:

```sql
CREATE TABLE config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔧 Troubleshooting

### **Common Issues**

#### **1. Qt Metadata Warnings**
```
Found invalid metadata in lib ... Invalid metadata version
```
**Solution**: These are harmless Qt warnings and don't affect functionality.

#### **2. PostgreSQL Connection Failed**
```
PostgreSQL connection failed
```
**Solutions**:
- Use `claude_v4.py` for database-free operation
- Check PostgreSQL service is running
- Verify connection credentials
- Ensure database exists

#### **3. Missing Microservice Files**
```
Missing microservice files: ['auth_service.py', ...]
```
**Solution**: The application automatically creates dummy service files.

#### **4. Execution Policy Error (Windows)**
```
cannot be loaded because running scripts is disabled
```
**Solution**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### **5. Virtual Environment Issues**
```bash
# Recreate virtual environment
rm -rf .venv  # or rmdir /s .venv on Windows
python -m venv .venv
# Reactivate and reinstall dependencies
```

### **Debug Mode**

Enable detailed logging:
```python
# Add to main() function
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🧪 Development

### **Running Different Versions**

```bash
# Minimal splash screen demo
python claude_splash.py

# Full application (no database)
python claude_v4.py

# Full application (with PostgreSQL)
python claude_v4_with_db.py

# Legacy version
python claude_v3.py

# Alternative implementation
python gemini_splash.py
```

### **Creating Custom Microservices**

Template for new services:
```python
# my_service.py
import time
import sys

def main():
    print("Starting my_service...")
    while True:
        print("my_service is running...")
        time.sleep(10)

if __name__ == "__main__":
    main()
```

### **Extending the Application**

1. **Add new UI components** in `MainWindow` class
2. **Extend configuration** in the settings dialog
3. **Add service types** by modifying the microservices list
4. **Customize splash screen** by editing `SplashScreen` class

## 🎨 UI Customization

### **Color Schemes**

Modify the stylesheet constants:
```python
# Primary colors
PRIMARY_BLUE = "#3498db"
SUCCESS_GREEN = "#27ae60"
ERROR_RED = "#e74c3c"
DARK_GRAY = "#2c3e50"
```

### **Window Dimensions**

```python
# Splash screen size
SPLASH_WIDTH = 250
SPLASH_HEIGHT = 280

# Main window size
MAIN_WIDTH = 800
MAIN_HEIGHT = 600
```

## 📱 Platform-Specific Notes

### **Windows**
- Requires PowerShell execution policy configuration
- Virtual environment activation uses `.ps1` scripts
- Process termination uses Windows APIs

### **Linux/macOS**
- Uses Unix process groups for service management
- Virtual environment activation uses shell scripts
- Supports SIGTERM/SIGKILL for graceful shutdown

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature-name`
3. **Make your changes**
4. **Test thoroughly** with both database and mock modes
5. **Submit a pull request**

### **Code Style**
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Document all public methods
- Add docstrings for classes

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5** for the GUI framework
- **PostgreSQL** for database support
- **NASTP** for project requirements and logo

## 📞 Support

For issues and questions:
- **Create an issue** on the repository
- **Check the troubleshooting section** above
- **Review the code comments** for implementation details

---

**Version**: 2.0.0  
**Last Updated**: 2024  
**Compatibility**: Python 3.8+, PyQt5 5.15+, QGIS 3.22.16 