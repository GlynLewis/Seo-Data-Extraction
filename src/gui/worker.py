import sys
from PyQt6.QtCore import QThread, pyqtSignal
from src.dataforseo_api import DataForSEOClient
import asyncio
import json
import os

class Worker(QThread):
    finished = pyqtSignal(list, int)
    progress = pyqtSignal(int, int)
    error = pyqtSignal(str)

    def __init__(self, data, batch_size=10, resume_file='resume.json'):
        super().__init__()
        self.data = data
        self.batch_size = batch_size
        self.resume_file = resume_file
        self.start_index = 0

    def run(self):
        try:
            results, processed_count = asyncio.run(self.async_run())
            self.finished.emit(results, processed_count)
        except Exception as e:
            self.error.emit(f"Error in Worker: {str(e)}")

    async def async_run(self):
        results = []
        processed_count = 0
        self.start_index = self.load_resume()
        
        if self.start_index >= len(self.data):
            self.start_index = 0

        try:
            async with DataForSEOClient() as client:
                for i in range(self.start_index, len(self.data), self.batch_size):
                    batch = self.data[i:i+self.batch_size]
                    batch_results = await self.process_batch(client, batch)
                    results.extend(batch_results)
                    
                    processed_count += len(batch_results)
                    self.save_resume(i + self.batch_size)
                    progress = min(100, int((i + self.batch_size) / len(self.data) * 100))
                    self.progress.emit(progress, processed_count)

            return results, processed_count
        except Exception as e:
            self.error.emit(f"Error during processing: {str(e)}")
            return results, processed_count

    async def process_batch(self, client, batch):
        batch_results = []
        for row in batch:
            website = row['website_url']
            linkedin_url = row.get('linkedin_url', '')
            try:
                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website

                website_data = await client.get_website_data(website)
                page_data = await client.get_page_data(website)
                
                is_wordpress = website_data['is_wordpress']
                status = website_data['status']
                
                if is_wordpress is True:
                    backlink_data = await client.get_backlink_data(website)

                    api_phone_numbers = '|'.join(website_data['phone_numbers']) if isinstance(website_data['phone_numbers'], list) else ''
                    api_emails = '|'.join(website_data['emails']) if isinstance(website_data['emails'], list) else ''

                    batch_results.append({
                        'website': website,
                        'linkedin_url': linkedin_url,
                        'is_wordpress': True,
                        'domain_rank': website_data['domain_rank'],
                        'api_phone_numbers': api_phone_numbers,
                        'api_emails': api_emails,
                        'total_pages': page_data['total_pages'],
                        'indexed_pages': page_data['indexed_pages'],
                        'external_links_count': backlink_data['external_links_count'],
                        'referring_domains': backlink_data['referring_domains'],
                        'status': status
                    })
                else:
                    batch_results.append({
                        'website': website,
                        'linkedin_url': linkedin_url,
                        'is_wordpress': False if is_wordpress is False else 'Unknown',
                        'status': 'No WordPress Detected in API Response'
                    })
            except Exception as e:
                error_msg = f"Error processing {website}: {str(e)}"
                self.error.emit(error_msg)
                batch_results.append({
                    'website': website,
                    'linkedin_url': linkedin_url,
                    'error': str(e),
                    'is_wordpress': 'Error',
                    'status': 'Error during processing'
                })

        return batch_results

    def save_resume(self, index):
        with open(self.resume_file, 'w') as f:
            json.dump({'last_processed_index': index}, f)

    def load_resume(self):
        if os.path.exists(self.resume_file):
            with open(self.resume_file, 'r') as f:
                data = json.load(f)
                return data.get('last_processed_index', 0)
        return 0