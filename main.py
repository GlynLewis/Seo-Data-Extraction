import sys
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)