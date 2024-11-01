import sys
import logging
import argparse
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def main():
    parser = argparse.ArgumentParser(description='SEO Data Extraction Tool')
    parser.add_argument(
        '--log-level',
        default='ERROR',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: ERROR)'
    )
    
    args = parser.parse_args()
    
    # Set the log level for the root logger
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))
    
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
