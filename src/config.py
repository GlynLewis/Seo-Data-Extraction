import os
from dotenv import load_dotenv

# Try to load the .env file, but don't raise an error if it's not found
load_dotenv(verbose=True)

# DataForSEO credentials
DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN', 'admin@superlewis.com')
DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD', 'ab0d272e760b2521')

# Google Custom Search API credentials
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY','AIzaSyCRVOxLnLyPhUHTC7Kptdfqoc-XkmBim7Q')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID','169645a78955f41cb')

# Print the values for debugging (remove this in production)
print(f"DATAFORSEO_LOGIN: {DATAFORSEO_LOGIN}")
print(f"DATAFORSEO_PASSWORD: {DATAFORSEO_PASSWORD}")
print(f"GOOGLE_API_KEY: {GOOGLE_API_KEY}")
print(f"GOOGLE_CSE_ID: {GOOGLE_CSE_ID}")