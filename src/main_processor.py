import pandas as pd
from csv_handler import read_csv, write_csv
from dataforseo_api import DataForSEOClient
import asyncio
import logging
import sys
import signal

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def process_websites(input_file, output_file):
    logger.info(f"Starting website processing from {input_file}")
    df = read_csv(input_file)
    if df is None:
        logger.error("Failed to read input CSV file")
        return

    async with DataForSEOClient() as client:
        total_sites = len(df)
        for index, row in df.iterrows():
            website = row['website_url']
            logger.info(f"Processing website {index + 1}/{total_sites}: {website}")
            
            try:
                # Get website technology data
                website_data = await client.get_website_data(website)
                df.at[index, 'cms'] = website_data['cms']
                df.at[index, 'domain_rank'] = website_data['domain_rank']

                # Process sites with any CMS detected, excluding 'Error'
                if website_data['cms'] != 'Error':
                    logger.info(f"{website_data['cms']} detected for {website}, gathering additional data")

                    # Get backlink data
                    backlink_data = await client.get_backlink_data(website)
                    df.at[index, 'backlinks'] = backlink_data['backlinks']
                    df.at[index, 'backlink_domains'] = backlink_data['backlink_domains']

                    # Get page data (total and indexed pages)
                    page_data = await client.get_page_data(website)
                    df.at[index, 'total_pages'] = page_data['total_pages']
                    df.at[index, 'indexed_pages'] = page_data['indexed_pages']

                    logger.info(f"Successfully processed website: {website}")
                else:
                    logger.info(f"Skipping CMS Error website: {website}")

            except Exception as e:
                error_msg = f"Error processing {website}: {str(e)}"
                logger.error(error_msg)

    logger.info(f"Writing results to {output_file}")
    write_csv(df, output_file)
    logger.info("Website processing completed")

def handle_shutdown(signum, frame):
    """Handle shutdown gracefully"""
    logger.info("Received shutdown signal, cleaning up...")
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
