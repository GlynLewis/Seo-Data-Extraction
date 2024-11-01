import pandas as pd
import os
from csv_handler import read_csv, write_csv
from data_processor import DataForSEOClient  # Updated import
import asyncio
import logging
import sys
import signal
from asyncio import Semaphore
from typing import List, Dict
import gc
from constants import MAX_CONCURRENT_REQUESTS, CHUNK_SIZE, CHUNK_DELAY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def process_single_website(website: str, index: int, total: int, client: DataForSEOClient, sem: Semaphore) -> Dict:
    """Process a single website with rate limiting"""
    async with sem:  # Use semaphore for rate limiting
        # Log Error at start of processing each URL
        logger.error(f"Processing website {index + 1}/{total}: {website}")
        result = {
            'website_url': website,
            'cms': 'Error',
            'domain_rank': None,
            'backlinks': None,
            'backlink_domains': None,
            'total_pages': None,
            'indexed_pages': None
        }
        
        try:
            # Add delay between requests to prevent rate limiting
            await asyncio.sleep(2)  # Increased delay between requests
            
            # Get website technology data
            website_data = await client.get_website_data(website)
            result['cms'] = website_data['cms']
            result['domain_rank'] = website_data['domain_rank']

            # Process sites with any CMS detected, excluding 'Error'
            if website_data['cms'] != 'Error':
                logger.error(f"{website_data['cms']} detected for {website}, gathering additional data")

                try:
                    # Add larger delay between API calls
                    await asyncio.sleep(1.5)  # Increased delay
                    backlink_data = await client.get_backlink_data(website)
                    result['backlinks'] = backlink_data['backlinks']
                    result['backlink_domains'] = backlink_data['backlink_domains']
                    
                    # Add larger delay between API calls
                    await asyncio.sleep(1.5)  # Increased delay
                    page_data = await client.get_page_data(website)
                    result['total_pages'] = page_data['total_pages']
                    result['indexed_pages'] = page_data['indexed_pages']

                    logger.error(f"Successfully processed website: {website}")
                except Exception as api_error:
                    logger.error(f"API error for {website}: {str(api_error)}")
                    # Keep partial results if we have them
            else:
                logger.error(f"Skipping CMS Error website: {website}")

        except Exception as e:
            error_msg = f"Error processing {website}: {str(e)}"
            logger.error(error_msg)
            
        return result

async def process_website_chunk(websites: List[Dict], start_idx: int, total_sites: int, 
                              client: DataForSEOClient, sem: Semaphore) -> List[Dict]:
    """Process a chunk of websites concurrently"""
    tasks = []
    for idx, row in enumerate(websites):
        absolute_idx = start_idx + idx
        website_url = row.get('website', '')  # Handle missing website field
        if not website_url:
            logger.error(f"Missing website URL for row {absolute_idx}")
            continue
        task = process_single_website(website_url, absolute_idx, total_sites, client, sem)
        tasks.append(task)
    
    try:
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out exceptions and None results
        valid_results = [r for r in chunk_results if isinstance(r, dict)]
        return valid_results
    except Exception as e:
        logger.error(f"Error processing chunk: {str(e)}")
        return []

async def process_websites(input_file: str, output_file: str):
    logger.error(f"Starting website processing from {input_file}")
    df = read_csv(input_file)
    if df is None:
        logger.error("Failed to read input CSV file")
        return

    # Convert DataFrame to list of dictionaries for easier processing
    websites = df.to_dict('records')
    total_sites = len(websites)
    results = []
    
    # Create rate limiting semaphore
    sem = Semaphore(MAX_CONCURRENT_REQUESTS)

    # Create intermediate file path for recovery
    base_path, ext = os.path.splitext(output_file)
    if not ext:
        ext = '.csv'
    recovery_file = f"{base_path}_recovery{ext}"

    async with DataForSEOClient() as client:
        # Process websites in chunks to avoid memory issues with large datasets
        for i in range(0, total_sites, CHUNK_SIZE):
            chunk = websites[i:i + CHUNK_SIZE]
            logger.error(f"Processing chunk {i//CHUNK_SIZE + 1}/{(total_sites + CHUNK_SIZE - 1)//CHUNK_SIZE}")
            
            try:
                chunk_results = await process_website_chunk(chunk, i, total_sites, client, sem)
                results.extend(chunk_results)
                
                # Write intermediate results to recovery file
                intermediate_df = pd.DataFrame(results)
                write_csv(intermediate_df, recovery_file)
                logger.error(f"Saved intermediate results for {len(results)}/{total_sites} websites to recovery file")
                
                # Force garbage collection between chunks
                gc.collect()
                
                # Add longer delay between chunks
                await asyncio.sleep(CHUNK_DELAY)
            except Exception as e:
                logger.error(f"Error processing chunk starting at index {i}: {str(e)}")
                # Force garbage collection after error
                gc.collect()
                continue

    # Write final results split by CMS type
    final_df = pd.DataFrame(results)
    write_csv(final_df, output_file)
    logger.error("Website processing completed")

def handle_shutdown(signum, frame):
    """Handle shutdown gracefully"""
    logger.error("Received shutdown signal, cleaning up...")
    for task in asyncio.all_tasks():
        task.cancel()
    asyncio.get_event_loop().stop()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Set up event loop with proper cleanup
    try:
        if sys.platform.startswith('win'):
            # Use ProactorEventLoop on Windows
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)
        else:
            loop = asyncio.get_event_loop()

        input_file = "data/input/sample_data.csv"
        output_file = "data/output/processed_data.csv"

        loop.run_until_complete(process_websites(input_file, output_file))
    finally:
        try:
            # Cancel all running tasks
            pending = asyncio.all_tasks(loop)
            for task in pending:
                task.cancel()
            # Run loop until tasks complete
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.close()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
