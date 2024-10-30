import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QOperatingSystemVersion
from PyQt6.QtGui import QGuiApplication

def setup_macos(app: QApplication):
    if not isinstance(app, QApplication):
        raise TypeError("Expected QApplication instance")

    # Set the application name (appears in the menu bar)
    app.setApplicationName("SEO Data Extraction")

    # Set the "About" menu item
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ROHIT KABDWAL")
    app.setOrganizationDomain("rohitkabdwal.com")

    # Ensure the app uses the macOS menu bar
    app.setAttribute(Qt.ApplicationAttribute.AA_DontUseNativeMenuBar, False)

    # Enable high DPI scaling
    if QOperatingSystemVersion.current() >= QOperatingSystemVersion.MacOSBigSur:
        QGuiApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

    # Set macOS-specific stylesheet if needed
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            padding: 8px 16px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)

    print("macOS-specific setup complete")