import sys
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from src.data_processor import DataForSEOClient
import asyncio
import json
import os
import platform

# Configure logging
logger = logging.getLogger(__name__)

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
        self.loop = None

    def run(self):
        try:
            # Create a new event loop for this thread
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # Run the async code and get results
            results, processed_count = self.loop.run_until_complete(self.async_run())

            # Emit results
            self.finished.emit(results, processed_count)

        except Exception as e:
            self.error.emit(f"Error in Worker: {str(e)}")
        finally:
            try:
                # Cancel all running tasks
                pending = asyncio.all_tasks(self.loop)
                for task in pending:
                    task.cancel()

                # Run the event loop one last time to clean up
                if pending:
                    self.loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))

                # Close the loop
                self.loop.close()
            except Exception as e:
                self.error.emit(f"Error cleaning up: {str(e)}")

    def stop(self):
        self._is_running = False
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)

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
                # Remove any existing protocol as the API client will handle
                if website.startswith(('http://', 'https://')):
                    website = website.split('://', 1)[1]

                # Get website data
                website_data = await client.get_website_data(website)
                
                # Add delay between API calls
                await asyncio.sleep(1.5)

                # Extract all needed values with defaults
                cms = website_data.get('cms', 'Error')
                domain_rank = website_data.get('domain_rank')
                total_pages = website_data.get('total_pages', 0)
                indexed_pages = website_data.get('indexed_pages', 0)
                backlinks = website_data.get('backlinks', 0)
                backlink_domains = website_data.get('backlink_domains', 0)

                # Create result dictionary with extracted values
                result = {
                    'website': website,
                    'linkedin_url': linkedin_url,
                    'cms': cms,
                    'domain_rank': domain_rank,
                    'total_pages': total_pages,
                    'indexed_pages': indexed_pages,
                    'backlinks': backlinks,
                    'backlink_domains': backlink_domains
                }

                batch_results.append(result)

            except Exception as e:
                logger.error()
                error_msg = f"Error processing {website}: {str(e)}"
                self.error.emit(error_msg)
                # Add error result to maintain order
                batch_results.append({
                    'website': website,
                    'linkedin_url': linkedin_url,
                    'cms': cms,
                    'domain_rank': domain_rank,
                    'total_pages': total_pages,
                    'indexed_pages': indexed_pages,
                    'backlinks': backlinks,
                    'backlink_domains': backlink_domains
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
