import os
import sys
from urllib.parse import urlparse
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QFileDialog, QProgressBar, QMessageBox, QApplication, QLabel)
from PyQt6.QtCore import Qt
from src.csv_handler import read_csv, write_csv
from src.gui.worker import Worker

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
        self.results_table = QTableWidget(0, 17)
        self.results_table.setHorizontalHeaderLabels([
            "First Name", "Last Name", "Email", "Organization Name", "Title",
            "Website URL", "Phone Number", "LinkedIn URL", "Is WordPress", "Domain Rank",
            "API Phone Numbers", "API Emails", "Total Pages", "Indexed Pages",
            "External Links Count", "Referring Domains", "Status"
        ])
        self.results_table.setSortingEnabled(False)
        layout.addWidget(self.results_table)

        self.data = []
        self.results = []
        self.resume_file = 'resume.json'

    def is_valid_url(self, url):
        if not url or url.isspace():
            return False
        url = url.strip()
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def upload_csv(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Upload CSV", "", "CSV Files (*.csv)")
        if file_name:
            all_data = read_csv(file_name)
            if all_data is not None and isinstance(all_data, list):
                self.data = []
                invalid_count = 0
                empty_count = 0
                for row in all_data:
                    url = row.get('website_url')
                    if url is None or (isinstance(url, str) and not url.strip()):
                        empty_count += 1
                        continue
                    
                    if isinstance(url, float):
                        url = str(url).rstrip('0').rstrip('.')
                    elif not isinstance(url, str):
                        url = str(url)
                    
                    url = url.strip()
                    if self.is_valid_url(url):
                        row['website_url'] = url
                        self.data.append(row)
                    else:
                        invalid_count += 1
                
                if self.data:
                    self.process_button.setEnabled(True)
                    self.update_table_with_input_data()
                    QMessageBox.information(self, "Upload Successful", 
                                            f"CSV file loaded with {len(self.data)} valid entries.\n"
                                            f"{invalid_count} entries were skipped due to invalid URLs.\n"
                                            f"{empty_count} entries were skipped due to empty URL fields.")
                else:
                    QMessageBox.warning(self, "Upload Failed", "No valid entries found in the CSV file.")
            else:
                QMessageBox.warning(self, "Upload Failed", "Failed to load the CSV file. Please check the file format.")

    def update_table_with_input_data(self):
        self.results_table.setRowCount(len(self.data))
        for i, row in enumerate(self.data):
            for j, key in enumerate(['first_name', 'last_name', 'email', 'organization_name', 'title',
                                     'website_url', 'phone_number', 'linkedin_url']):
                value = row.get(key, '')
                self.results_table.setItem(i, j, QTableWidgetItem(str(value) if value is not None else ''))
            # Initialize WordPress data columns with empty values
            for j in range(8, self.results_table.columnCount()):
                self.results_table.setItem(i, j, QTableWidgetItem(''))

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
        for result in results:
            website = result['website']
            for row in range(self.results_table.rowCount()):
                if self.results_table.item(row, 5).text() == website:  # Assuming website URL is in column 5
                    self.results_table.setItem(row, 7, QTableWidgetItem(result.get('linkedin_url', '')))
                    self.results_table.setItem(row, 8, QTableWidgetItem(str(result['is_wordpress'])))
                    
                    if result['is_wordpress'] is True:
                        for j, key in enumerate(['domain_rank', 'api_phone_numbers', 'api_emails',
                                                 'total_pages', 'indexed_pages', 'external_links_count', 
                                                 'referring_domains']):
                            value = result.get(key, '')
                            self.results_table.setItem(row, j + 9, QTableWidgetItem(str(value)))
                    else:
                        for j in range(9, 16):
                            self.results_table.setItem(row, j, QTableWidgetItem('N/A'))
                    
                    self.results_table.setItem(row, 16, QTableWidgetItem(result['status']))
                    break
        
        if results:
            self.results_table.scrollToItem(self.results_table.item(len(results) - 1, 0))

    def export_results(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Results", "", "CSV Files (*.csv)")
        if file_name:
            results_with_data = []
            for i in range(self.results_table.rowCount()):
                row_data = {}
                for j in range(self.results_table.columnCount()):
                    item = self.results_table.item(i, j)
                    header = self.results_table.horizontalHeaderItem(j).text()
                    row_data[header] = item.text() if item else ''
                results_with_data.append(row_data)
            
            success = write_csv(results_with_data, file_name)
            if success:
                QMessageBox.information(self, "Export Successful", f"Results exported to {file_name}")
            else:
                QMessageBox.warning(self, "Export Failed", "Failed to export results. Please try again.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())