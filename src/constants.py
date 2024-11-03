import os
import json

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

# API Credentials from config
api_credentials = persistent_config.get('api_credentials', {})
DATAFORSEO_LOGIN = api_credentials.get('dataforseo_login', '')
DATAFORSEO_PASSWORD = api_credentials.get('dataforseo_password', '')
GOOGLE_API_KEY = api_credentials.get('google_api_key', '')
GOOGLE_CSE_ID = api_credentials.get('google_cse_id', '')

# API Request Configuration
MAX_RETRIES = 3
INITIAL_RETRY_DELAY = 2
MAX_RETRY_DELAY = 15
RETRY_MULTIPLIER = 2

# Request Timeouts (in seconds)
DEFAULT_TIMEOUT = 45
SITEMAP_TIMEOUT = 30
ROBOTS_TIMEOUT = 20

# Rate Limiting
REQUESTS_PER_SECOND = 1
RATE_LIMIT_WINDOW = 2

# Sitemap Configuration
MAX_SITEMAP_DEPTH = 2
MAX_URLS_PER_SITEMAP = 50000  # Google's sitemap limit

# Memory Management
CHUNK_SIZE = 10
CHUNK_DELAY = 5
MAX_CONCURRENT_REQUESTS = 3

# Connection Management
TCP_CONNECTOR_LIMIT = 50
FORCE_CLOSE_CONNECTIONS = True
ENABLE_CLEANUP_CLOSED = True

# Error Messages
ERROR_MESSAGES = {
    'auth_failed': 'Authentication failed. Please check your credentials.',
    'rate_limit': 'Rate limit exceeded. Please try again later.',
    'invalid_input': 'Invalid input parameters provided.',
    'service_error': 'Service temporarily unavailable.',
    'timeout': 'Request timed out. Please try again.',
    'network_error': 'Network error occurred. Please check your connection.',
}

# Last used directory (defaults to current directory if not found)
LAST_INPUT_DIRECTORY = persistent_config.get('last_input_directory', os.getcwd())

def update_last_input_directory(directory):
    global LAST_INPUT_DIRECTORY
    LAST_INPUT_DIRECTORY = directory
    persistent_config['last_input_directory'] = directory
    save_persistent_config(persistent_config)
