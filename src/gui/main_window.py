import os
import sys
import logging
from urllib.parse import urlparse
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QProgressBar, QMessageBox, QApplication, QLabel)
from PyQt6.QtCore import Qt
from src.csv_handler import read_csv, write_csv
from src.gui.worker import Worker
from src.constants import LAST_INPUT_DIRECTORY, update_last_input_directory
from src.utils import set_log_file

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WordPress SEO Data Extraction")
        self.setGeometry(100, 100, 1400, 600)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload CSV")
        self.upload_button.clicked.connect(self.upload_csv)
        button_layout.addWidget(self.upload_button)

        self.process_button = QPushButton("Process WordPress Sites")
        self.process_button.clicked.connect(self.process_urls)
        self.process_button.setEnabled(False)
        button_layout.addWidget(self.process_button)

        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

        # Progress bar and label
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        self.progress_label = QLabel("0/0 sites processed")
        progress_layout.addWidget(self.progress_label)
        layout.addLayout(progress_layout)

        # Results table
        self.results_table = QTableWidget(0, 14)
        self.results_table.setHorizontalHeaderLabels([
            "First Name", "Last Name", "Email", "Organization Name", "Title",
            "Website URL", "Phone Number", "LinkedIn URL", "CMS", "Domain Rank",
            "Total Pages", "Indexed Pages", "Backlinks", "Backlink Domains"
        ])
        self.results_table.setSortingEnabled(False)
        layout.addWidget(self.results_table)

        self.data = []
        self.results = []
        self.resume_file = 'resume.json'
        self.worker = None
        self.input_csv_path = None  # Store the input CSV path

    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                'Confirm Exit',
                'Processing is still running. Do you want to stop and exit?',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def is_valid_url(self, url):
        """Validate URL, accepting domain names without scheme"""
        if not url or url.isspace():
            return False

        url = url.strip()

        # Remove any scheme if present
        if url.startswith(('http://', 'https://')):
            parsed = urlparse(url)
            url = parsed.netloc

        # Basic domain validation
        parts = url.split('.')
        return len(parts) >= 2 and all(part for part in parts)

    def upload_csv(self):
        try:
            # Use the last input directory from config
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Upload CSV",
                LAST_INPUT_DIRECTORY,  # Use the stored directory
                "CSV Files (*.csv)"
            )

            if file_name:
                self.input_csv_path = file_name  # Store the input CSV path
                # Update window title with filename
                self.setWindowTitle(f"WordPress SEO Data Extraction    -    {os.path.basename(file_name)}")
                logger.info(f"Selected file: {file_name}")

                # Set up logging to file
                log_file = set_log_file(file_name)
                logger.info(f"Logging to file: {log_file}")

                # Update the last input directory in config
                new_directory = os.path.dirname(os.path.abspath(file_name))
                update_last_input_directory(new_directory)
                logger.info(f"Updated last input directory to: {new_directory}")

                all_data = read_csv(file_name)
                if all_data is not None:
                    logger.info(f"Successfully read {len(all_data)} records from CSV")
                    self.data = []
                    invalid_count = 0
                    empty_count = 0

                    for row in all_data:
                        url = row.get('website_url')
                        logger.info(f"Processing URL: {url}")

                        if url is None or (isinstance(url, str) and not url.strip()):
                            empty_count += 1
                            logger.info("Empty URL found")
                            continue

                        if isinstance(url, float):
                            url = str(url).rstrip('0').rstrip('.')
                        elif not isinstance(url, str):
                            url = str(url)

                        url = url.strip()
                        if self.is_valid_url(url):
                            row['website_url'] = url
                            self.data.append(row)
                            logger.info(f"Valid URL added: {url}")
                        else:
                            invalid_count += 1
                            logger.info(f"Invalid URL found: {url}")

                    if self.data:
                        self.process_button.setEnabled(True)
                        self.update_table_with_input_data()
                        message = (f"CSV file loaded with {len(self.data)} valid entries.\n"
                                 f"{invalid_count} entries were skipped due to invalid URLs.\n"
                                 f"{empty_count} entries were skipped due to empty URL fields.")
                        logger.info(message)
                        QMessageBox.information(self, "Upload Successful", message)
                    else:
                        message = "No valid entries found in the CSV file."
                        logger.error(message)
                        QMessageBox.warning(self, "Upload Failed", message)
                else:
                    message = "Failed to load the CSV file. Please check the file format and required columns."
                    logger.error(message)
                    QMessageBox.warning(self, "Upload Failed", message)

        except Exception as e:
            error_message = f"Error during CSV upload: {str(e)}"
            logger.error(error_message)
            QMessageBox.critical(self, "Error", error_message)

    def update_table_with_input_data(self):
        try:
            self.results_table.setRowCount(len(self.data))
            for i, row in enumerate(self.data):
                for j, key in enumerate(['first_name', 'last_name', 'email', 'organization_name', 'title',
                                         'website_url', 'phone_number', 'linkedin_url']):
                    value = row.get(key, '')
                    if isinstance(value, float):
                        value = str(int(value)) if value.is_integer() else str(value)
                    self.results_table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ''))
                # Initialize remaining columns with empty values
                for j in range(8, self.results_table.columnCount()):
                    self.results_table.setItem(i, j, QTableWidgetItem(''))
            logger.info(f"Updated table with {len(self.data)} rows")
        except Exception as e:
            logger.error(f"Error updating table: {str(e)}")

    def process_urls(self):
        if not self.data:
            QMessageBox.warning(self, "No Data", "Please upload a CSV file first.")
            return

        self.progress_bar.setValue(0)
        self.progress_label.setText(f"0/{len(self.data)} sites processed")
        self.process_button.setEnabled(False)
        self.export_button.setEnabled(False)

        # Reset the resume file
        if os.path.exists(self.resume_file):
            os.remove(self.resume_file)

        batch_size = 10  # You can adjust this value
        self.worker = Worker(data=self.data, batch_size=batch_size, resume_file=self.resume_file)
        self.worker.finished.connect(self.on_processing_finished)
        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.start()

    def update_progress(self, value, processed_count):
        self.progress_bar.setValue(value)
        self.progress_label.setText(f"{processed_count}/{len(self.data)} sites processed")

    def on_processing_finished(self, results, processed_count):
        self.results = results
        self.update_table_with_processed_data(results)
        self.process_button.setEnabled(True)
        self.export_button.setEnabled(True)
        QMessageBox.information(self, "Processing Complete", f"{processed_count}/{len(self.data)} URLs have been processed.")

    def show_error(self, message):
        QMessageBox.critical(self, "Error", message)

    def update_table_with_processed_data(self, results):
        try:
            for result in results:
                website = result['website']
                for row in range(self.results_table.rowCount()):
                    if self.results_table.item(row, 5).text() == website:  # Assuming website URL is in column 5
                        # Convert any float values to strings
                        linkedin_url = result.get('linkedin_url', '')
                        if isinstance(linkedin_url, float):
                            linkedin_url = str(int(linkedin_url)) if linkedin_url.is_integer() else str(linkedin_url)
                        self.results_table.setItem(row, 7, QTableWidgetItem(str(linkedin_url)))

                        # Update CMS column
                        self.results_table.setItem(row, 8, QTableWidgetItem(str(result.get('cms', 'Unknown'))))

                        # Update all data columns regardless of CMS status
                        for j, key in enumerate(['domain_rank', 'total_pages', 'indexed_pages',
                                                'backlinks', 'backlink_domains']):
                            value = result.get(key, 'N/A')
                            if isinstance(value, float):
                                value = str(int(value)) if value.is_integer() else str(value)
                            self.results_table.setItem(row, j + 9, QTableWidgetItem(str(value)))
                        break

            if results:
                self.results_table.scrollToItem(self.results_table.item(len(results) - 1, 0))
                logger.info(f"Updated table with {len(results)} processed results")
        except Exception as e:
            logger.error(f"Error updating table with processed data: {str(e)}")

    def export_results(self):
        try:
            if not self.input_csv_path:
                QMessageBox.warning(self, "Error", "No input CSV file found. Please upload a CSV file first.")
                return

            # Generate the output filename by inserting "_Out" before .csv
            base, ext = os.path.splitext(self.input_csv_path)
            output_filename = f"{base}_Out{ext}"

            logger.info(f"Exporting results to: {output_filename}")

            results_with_data = []
            for i in range(self.results_table.rowCount()):
                row_data = {}
                for j in range(self.results_table.columnCount()):
                    item = self.results_table.item(i, j)
                    header = self.results_table.horizontalHeaderItem(j).text()
                    row_data[header] = item.text() if item else ''
                results_with_data.append(row_data)

            success = write_csv(results_with_data, output_filename)
            if success:
                message = f"Results exported to {output_filename}"
                logger.info(message)
                QMessageBox.information(self, "Export Successful", message)
            else:
                message = "Failed to export results. Please try again."
                logger.error(message)
                QMessageBox.warning(self, "Export Failed", message)
        except Exception as e:
            error_message = f"Error during export: {str(e)}"
            logger.error(error_message)
            QMessageBox.critical(self, "Error", error_message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
