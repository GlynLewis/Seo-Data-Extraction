import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QOperatingSystemVersion
from PyQt6.QtGui import QGuiApplication

def setup_windows(app: QApplication):
    if not isinstance(app, QApplication):
        raise TypeError("Expected QApplication instance")

    # Set the application name
    app.setApplicationName("SEO Data Extraction")

    # Set the application version and organization details
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ROHIT KABDWAL")
    app.setOrganizationDomain("rohitkabdwal.com")

    # Enable Windows 10 high DPI scaling
    if QOperatingSystemVersion.current() >= QOperatingSystemVersion.Windows10:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Set Windows-specific stylesheet if needed
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #007ACC;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #005999;
        }
    """)

    print("Windows-specific setup complete")