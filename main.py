import sys
import logging
import argparse
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow

def setup_logging(log_level):
    """Configure logging based on command line argument."""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')
    
    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s:%(name)s:%(message)s'
    )
    
    # Set level for all existing loggers
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.setLevel(numeric_level)

def main():
    parser = argparse.ArgumentParser(description='SEO Data Extraction Tool')
    parser.add_argument(
        '--log-level',
        default='WARNING',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (default: WARNING)'
    )
    
    args = parser.parse_args()
    setup_logging(args.log_level)
    
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
