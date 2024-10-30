import pandas as pd
from csv_handler import read_csv, write_csv
from web_scraper import get_total_pages, get_google_indexed_pages
from dataforseo_api import DataForSEOClient
import asyncio
import logging

# logging.basicConfig(level=logging.INFO)

async def process_websites(input_file, output_file):
    df = read_csv(input_file)
    if df is None:
        # logging.error("Error reading input file. Exiting.")
        return

    async with DataForSEOClient() as client:
        for index, row in df.iterrows():
            website = row['website_url']
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
            
            try:
                website_data = await client.get_website_data(website)
                backlink_data = await client.get_backlink_data(website)

                df.at[index, 'is_wordpress'] = website_data['is_wordpress']
                df.at[index, 'domain_rank'] = website_data['domain_rank']
                
                # Only process WordPress sites
                if website_data['is_wordpress']:
                    df.at[index, 'api_phone_numbers'] = '|'.join(website_data['phone_numbers']) if website_data['phone_numbers'] else ''
                    df.at[index, 'api_emails'] = '|'.join(website_data['emails']) if website_data['emails'] else ''
                    df.at[index, 'external_links_count'] = backlink_data['external_links_count']
                    df.at[index, 'referring_domains'] = backlink_data['referring_domains']

                    total_pages = get_total_pages(website)
                    indexed_pages = get_google_indexed_pages(website)
                    
                    df.at[index, 'total_pages'] = total_pages
                    df.at[index, 'indexed_pages'] = indexed_pages
                    df.at[index, 'status'] = "WordPress site processed"

                    # logging.info(f"Processed WordPress site: {website}")
                    # logging.info(f"Domain Rank: {website_data['domain_rank']}")
                #     logging.info(f"Phone Numbers: {website_data['phone_numbers']}")
                #     logging.info(f"Emails: {website_data['emails']}")
                #     logging.info(f"Total pages: {total_pages}")
                #     logging.info(f"Indexed pages: {indexed_pages}")
                #     logging.info(f"External links: {backlink_data['external_links_count']}")
                #     logging.info(f"Referring domains: {backlink_data['referring_domains']}")
                # else:
                    df.at[index, 'status'] = "Not a WordPress site"
                    # hi
                    # logging.info(f"Skipped non-WordPress site: {website}")

            except Exception as e:
                # logging.error(f"Error processing {website}: {str(e)}")
                df.at[index, 'status'] = f"Error: {str(e)}"

    write_csv(df, output_file)
    # logging.info(f"Results written to {output_file}")

if __name__ == "__main__":
    input_file = "data/input/sample_data.csv"
    output_file = "data/output/processed_data.csv"
    asyncio.run(process_websites(input_file, output_file))