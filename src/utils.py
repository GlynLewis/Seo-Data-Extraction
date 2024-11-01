import asyncio
import logging
import time
import os
from functools import wraps
from typing import Callable, TypeVar, Any
from aiohttp import ClientError, ClientResponseError
from src.config import (
    MAX_RETRIES,
    INITIAL_RETRY_DELAY,
    MAX_RETRY_DELAY,
    RETRY_MULTIPLIER,
    ERROR_MESSAGES,
    REQUESTS_PER_SECOND
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variable to store current log file path
_current_log_file = None

def set_log_file(csv_path: str) -> str:
    """
    Sets up logging to a file based on the input CSV path.
    Args:
        csv_path: Path to the input CSV file
    Returns:
        str: Path to the log file
    """
    global _current_log_file
    
    # Create log file path by replacing .csv extension with .log
    log_path = os.path.splitext(csv_path)[0] + '.log'
    
    # Store the current log file path
    _current_log_file = log_path
    
    # Remove existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up new file handler
    file_handler = logging.FileHandler(log_path, mode='w')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(file_handler)
    
    # Also add a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(console_handler)
    
    return log_path

def get_current_log_file() -> str:
    """Returns the current log file path"""
    return _current_log_file

# Type variable for generic return type
T = TypeVar('T')

class APIError(Exception):
    """Base exception for API related errors"""
    pass

class RateLimitError(APIError):
    """Raised when rate limit is exceeded"""
    pass

class AuthenticationError(APIError):
    """Raised when authentication fails"""
    pass

class ServiceError(APIError):
    """Raised when service is unavailable"""
    pass

# Rate limiting implementation
class RateLimiter:
    def __init__(self, requests_per_second: int):
        self.requests_per_second = requests_per_second
        self.last_request_time = 0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time
            if time_since_last_request < 1.0 / self.requests_per_second:
                delay = (1.0 / self.requests_per_second) - time_since_last_request
                await asyncio.sleep(delay)
            self.last_request_time = time.time()

# Global rate limiter instance
rate_limiter = RateLimiter(REQUESTS_PER_SECOND)

def with_retry(
    max_retries: int = MAX_RETRIES,
    initial_delay: float = INITIAL_RETRY_DELAY,
    max_delay: float = MAX_RETRY_DELAY,
    multiplier: float = RETRY_MULTIPLIER
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that implements exponential backoff retry logic for async functions.
    
    Args:
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        multiplier: Multiplier for exponential backoff
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    # Acquire rate limit before making request
                    await rate_limiter.acquire()
                    
                    return await func(*args, **kwargs)

                except ClientResponseError as e:
                    last_exception = e
                    if e.status == 401:
                        raise AuthenticationError(ERROR_MESSAGES['auth_failed'])
                    elif e.status == 429:
                        raise RateLimitError(ERROR_MESSAGES['rate_limit'])
                    elif e.status >= 500:
                        if attempt == max_retries:
                            raise ServiceError(ERROR_MESSAGES['service_error'])
                    else:
                        # Don't retry for other status codes
                        raise

                except ClientError as e:
                    last_exception = e
                    logger.warning(f"Network error on attempt {attempt + 1}: {str(e)}")
                    if attempt == max_retries:
                        raise APIError(ERROR_MESSAGES['network_error']) from e

                except asyncio.TimeoutError as e:
                    last_exception = e
                    logger.warning(f"Timeout error on attempt {attempt + 1}")
                    if attempt == max_retries:
                        raise APIError(ERROR_MESSAGES['timeout']) from e

                except Exception as e:
                    # Log unexpected errors but don't retry
                    logger.error(f"Unexpected error: {str(e)}")
                    raise

                if attempt < max_retries:
                    sleep_time = min(delay, max_delay)
                    logger.info(f"Retrying in {sleep_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(sleep_time)
                    delay *= multiplier

            # If we get here, we've exhausted all retries
            raise last_exception

        return wrapper
    return decorator

def validate_response(response_data: dict) -> bool:
    """
    Validates the response data from the API.
    
    Args:
        response_data: Response data from the API
        
    Returns:
        bool: True if response is valid, False otherwise
    """
    if not isinstance(response_data, dict):
        return False
    
    tasks = response_data.get('tasks', [])
    if not tasks or not isinstance(tasks, list):
        return False
    
    task = tasks[0]
    if not isinstance(task, dict):
        return False
    
    return task.get('status_code') == 20000

def extract_error_message(response_data: dict) -> str:
    """
    Extracts error message from API response.
    
    Args:
        response_data: Response data from the API
        
    Returns:
        str: Error message
    """
    try:
        tasks = response_data.get('tasks', [])
        if tasks and isinstance(tasks, list):
            task = tasks[0]
            if isinstance(task, dict):
                return task.get('status_message', 'Unknown error')
    except Exception:
        pass
    
    return 'Failed to extract error message from response'
