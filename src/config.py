import os
import json
from dotenv import load_dotenv

# Try to load the .env file, but don't raise an error if it's not found
load_dotenv(verbose=True)

# Config file path for storing persistent settings
CONFIG_FILE = 'app_config.json'

def load_persistent_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_persistent_config(config_data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

# Load persistent settings
persistent_config = load_persistent_config()

# Last used directory (defaults to current directory if not found)
LAST_INPUT_DIRECTORY = persistent_config.get('last_input_directory', os.getcwd())

def update_last_input_directory(directory):
    global LAST_INPUT_DIRECTORY
    LAST_INPUT_DIRECTORY = directory
    persistent_config['last_input_directory'] = directory
    save_persistent_config(persistent_config)

# DataForSEO credentials
DATAFORSEO_LOGIN = os.getenv('DATAFORSEO_LOGIN', 'admin@superlewis.com')
DATAFORSEO_PASSWORD = os.getenv('DATAFORSEO_PASSWORD', 'ab0d272e760b2521')

# Google Custom Search API credentials
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY','AIzaSyCRVOxLnLyPhUHTC7Kptdfqoc-XkmBim7Q')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID','169645a78955f41cb')

# API Request Configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 10  # seconds
RETRY_MULTIPLIER = 2  # exponential backoff multiplier

# Request Timeouts (in seconds)
DEFAULT_TIMEOUT = 30
SITEMAP_TIMEOUT = 20
ROBOTS_TIMEOUT = 10

# Rate Limiting
REQUESTS_PER_SECOND = 2  # maximum number of requests per second
RATE_LIMIT_WINDOW = 1  # window size in seconds

# Sitemap Configuration
MAX_SITEMAP_DEPTH = 3  # maximum depth for recursive sitemap processing
MAX_URLS_PER_SITEMAP = 50000  # maximum number of URLs to process per sitemap

# Error Messages
ERROR_MESSAGES = {
    'auth_failed': 'Authentication failed. Please check your credentials.',
    'rate_limit': 'Rate limit exceeded. Please try again later.',
    'invalid_input': 'Invalid input parameters provided.',
    'service_error': 'Service temporarily unavailable.',
    'timeout': 'Request timed out. Please try again.',
    'network_error': 'Network error occurred. Please check your connection.',
}
