import sys
from PyQt6.QtCore import QThread, pyqtSignal
from src.dataforseo_api import DataForSEOClient
import asyncio
import json
import os
import platform

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
        self._is_running = True
        
        # Set up a new event loop for Windows
        if platform.system() == 'Windows':
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

    def run(self):
        try:
            if platform.system() == 'Windows':
                results, processed_count = self.loop.run_until_complete(self.async_run())
            else:
                results, processed_count = asyncio.run(self.async_run())
            self.finished.emit(results, processed_count)
        except Exception as e:
            self.error.emit(f"Error in Worker: {str(e)}")
        finally:
            if platform.system() == 'Windows':
                self.loop.close()

    def stop(self):
        self._is_running = False

    async def async_run(self):
        results = []
        processed_count = 0
        self.start_index = self.load_resume()
        
        if self.start_index >= len(self.data):
            self.start_index = 0

        try:
            async with DataForSEOClient() as client:
                for i in range(self.start_index, len(self.data), self.batch_size):
                    if not self._is_running:
                        break
                        
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
            if not self._is_running:
                break
                
            website = row['website_url']
            linkedin_url = row.get('linkedin_url', '')
            try:
                # Remove any existing protocol as the API client will handle adding https://
                if website.startswith(('http://', 'https://')):
                    website = website.split('://', 1)[1]

                website_data = await client.get_website_data(website)
                page_data = await client.get_page_data(website)
                
                is_wordpress = website_data['is_wordpress']
                status = website_data['status']
                
                if is_wordpress is True:
                    backlink_data = await client.get_backlink_data(website)

                    api_phone_numbers = '|'.join(website_data['phone_numbers']) if isinstance(website_data['phone_numbers'], list) else ''
                    api_emails = '|'.join(website_data['emails']) if isinstance(website_data['emails'], list) else ''

                    batch_results.append({
                        'website': website,  # Store without protocol
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
                        'website': website,  # Store without protocol
                        'linkedin_url': linkedin_url,
                        'is_wordpress': False if is_wordpress is False else 'Unknown',
                        'status': 'No WordPress Detected in API Response'
                    })
            except Exception as e:
                error_msg = f"Error processing {website}: {str(e)}"
                self.error.emit(error_msg)
                batch_results.append({
                    'website': website,  # Store without protocol
                    'linkedin_url': linkedin_url,
                    'error': str(e),
                    'is_wordpress': 'Error',
                    'status': 'Error during processing'
                })

        return batch_results

    def save_resume(self, index):
        try:
            with open(self.resume_file, 'w') as f:
                json.dump({'last_processed_index': index}, f)
        except Exception as e:
            self.error.emit(f"Error saving resume state: {str(e)}")

    def load_resume(self):
        try:
            if os.path.exists(self.resume_file):
                with open(self.resume_file, 'r') as f:
                    data = json.load(f)
                    return data.get('last_processed_index', 0)
        except Exception as e:
            self.error.emit(f"Error loading resume state: {str(e)}")
        return 0
