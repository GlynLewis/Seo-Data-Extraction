import aiohttp
import asyncio
from src.constants import (
    DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, GOOGLE_API_KEY, GOOGLE_CSE_ID,
    DEFAULT_TIMEOUT, MAX_SITEMAP_DEPTH, MAX_URLS_PER_SITEMAP, MAX_RETRIES,
    INITIAL_RETRY_DELAY, TCP_CONNECTOR_LIMIT, FORCE_CLOSE_CONNECTIONS, ENABLE_CLEANUP_CLOSED
)
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import gzip
import brotli
from io import BytesIO
import logging
from typing import Optional, Tuple, List, Dict, Any
import backoff
import gc

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Request timeout configuration
REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT, connect=15)

# Modern browser User-Agent
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

# WordPress detection patterns
# Improved WordPress patterns for specific files
WP_PATTERNS = [
    r'/wp-content/themes/.+?/',  # Specific WordPress theme paths
    r'/wp-includes/js/wp-emoji-release.min.js',  # Unique WordPress script
    r'wp-json',  # WordPress JSON API
    r'wp-admin',  # Admin path
    r'wp-login.php',  # WordPress login page
]

# Negative patterns to identify non-WordPress CMSs (like Drupal or Wix)
NON_WP_PATTERNS = [
    r'/sites/default/',  # Drupal
    r'drupal\.js',       # Drupal
    r'/modules/',        # Drupal
    r'wixstatic\.com',   # Wix
    r'apps\.wix\.com',   # Wix apps
]

# Custom exception for SSL errors
class SSLError(Exception):
    pass

class DataForSEOClient:
    BASE_URL = "https://api.dataforseo.com/v3"
    GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"
    
    def __init__(self):
        self.login = DATAFORSEO_LOGIN
        self.password = DATAFORSEO_PASSWORD
        self.google_api_key = GOOGLE_API_KEY
        self.google_cse_id = GOOGLE_CSE_ID
        
        if not self.login or not self.password:
            raise ValueError("DataForSEO credentials are missing. Please check your configuration.")
        
        if not self.google_api_key or not self.google_cse_id:
            raise ValueError("Google Custom Search API credentials are missing. Please check your configuration.")
        
        self.auth = aiohttp.BasicAuth(self.login, self.password)
        self.session = None
        self._cleanup_lock = asyncio.Lock()
        self._is_closing = False
        self._request_semaphore = asyncio.Semaphore(TCP_CONNECTOR_LIMIT)
        self._session_lock = asyncio.Lock()
        self._current_domain = None  # Track current domain being processed
        self._processed_backlinks = set()  # Track domains we've already fetched backlinks for

    async def __aenter__(self):
        logger.info("Initializing DataForSEO client session")
        async with self._session_lock:
            if not self.session:
                connector = aiohttp.TCPConnector(
                    limit=TCP_CONNECTOR_LIMIT,
                    force_close=FORCE_CLOSE_CONNECTIONS,
                    enable_cleanup_closed=ENABLE_CLEANUP_CLOSED
                )
                self.session = aiohttp.ClientSession(
                    auth=self.auth,
                    headers=BROWSER_HEADERS,
                    timeout=REQUEST_TIMEOUT,
                    connector=connector
                )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        """Safely close the client session."""
        async with self._cleanup_lock:
            if not self._is_closing and self.session:
                self._is_closing = True
                logger.info("Closing DataForSEO client session")
                try:
                    await self.session.close()
                    # Wait for underlying connections to close
                    await asyncio.sleep(0.5)  # Increased wait time
                    # Force garbage collection
                    gc.collect()
                except Exception as e:
                    logger.error(f"Error closing session: {str(e)}")
                finally:
                    self.session = None
                    self._is_closing = False

    def _extract_domain(self, url: str) -> str:
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed_url = urlparse(url)
        return parsed_url.netloc

    def _normalize_url(self, url: str) -> str:
        """Ensure URL has a protocol."""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

    async def _decode_content(self, response: aiohttp.ClientResponse) -> str:
        """Helper method to decode response content based on Content-Type and Content-Encoding."""
        try:
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            raw_content = await response.read()

            if content_encoding == 'br':
                try:
                    return brotli.decompress(raw_content).decode('utf-8')
                except Exception:
                    return raw_content.decode('utf-8')
            elif content_encoding == 'gzip':
                try:
                    return gzip.decompress(raw_content).decode('utf-8')
                except Exception:
                    return raw_content.decode('utf-8')
            else:
                return raw_content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decoding content: {str(e)}")
            raise

    async def check_wordpress_via_scrape(self, url: str) -> bool:
        """Check if a website is using WordPress by scraping the page."""
        try:
            async with self.session.get(url, timeout=REQUEST_TIMEOUT) as response:
                if response.status != 200:
                    logger.info(f"{url} returned non-200 status: {response.status}")
                    return False

                content = await self._decode_content(response)
                soup = BeautifulSoup(content, 'html.parser')

                # Check meta generator tag for WordPress and log details
                meta_generator = soup.find('meta', {'name': 'generator'})
                if meta_generator and meta_generator.get('content'):
                    meta_content = meta_generator.get('content', '').lower()
                    logger.info(f"{url} meta generator tag content: {meta_content}")
                    if 'wordpress' in meta_content:
                        logger.info(f"{url} identified as WordPress by meta generator tag: {meta_content}")
                        return True
                    else:
                        logger.info(f"{url} meta generator tag found but not WordPress: {meta_content}")
                else:
                    logger.info(f"{url} has no meta generator tag")

                # Convert HTML to a string for regex matching
                html_str = str(soup)

                # Check for WordPress-specific patterns in HTML content
                for pattern in WP_PATTERNS:
                    if re.search(pattern, html_str, re.IGNORECASE):
                        logger.info(f"{url} matched WordPress pattern: {pattern}")

                        # Try accessing wp-json endpoint to confirm WordPress
                        try:
                            wp_json_url = urljoin(url, '/wp-json/')
                            async with self.session.get(wp_json_url, timeout=REQUEST_TIMEOUT) as wp_response:
                                if wp_response.status == 200:
                                    logger.info(f"{url} confirmed as WordPress by wp-json endpoint.")
                                    return True
                                else:
                                    logger.info(f"{url} wp-json endpoint returned non-200 status: {wp_response.status}")
                        except Exception as e:
                            logger.error(f"Error accessing wp-json for {url}: {str(e)}")
                        return True  # WordPress pattern match without needing wp-json confirmation

                # If any non-WordPress patterns are found, return False immediately
                for pattern in NON_WP_PATTERNS:
                    if re.search(pattern, html_str, re.IGNORECASE):
                        logger.info(f"{url} matched non-WordPress pattern: {pattern}")
                        return False

                # If no positive WordPress patterns are conclusively detected
                logger.info(f"No conclusive WordPress patterns found for {url}")
                return False

        except Exception as e:
            logger.error(f"Error checking WordPress via scrape for {url}: {str(e)}")
            return False

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=MAX_RETRIES,
        max_time=90  # Increased from 60
    )
    async def _make_request(self, endpoint: str, data: List[Dict[str, Any]], retry_with_www: bool = False) -> Optional[List[Dict[str, Any]]]:
        """Make API request with retry logic and rate limiting."""
        async with self._request_semaphore:
            logger.info(f"Making API request to {endpoint}")
            try:
                async with self.session.post(endpoint, json=data, timeout=REQUEST_TIMEOUT) as response:
                    response.raise_for_status()
                    result = await response.json()

                    # Validate response structure
                    if not isinstance(result, dict):
                        logger.error(f"Invalid response format from API: {result}")
                        return []

                    tasks = result.get('tasks', [])
                    if not tasks:
                        logger.error("No tasks found in API response")
                        return []

                    # Safely access first task
                    first_task = tasks[0] if tasks else None
                    if not first_task:
                        logger.error("Empty task in API response")
                        return []
                        
                    status_code = first_task.get('status_code')
                    if not status_code:
                        logger.error(f"No status code in task: {first_task}")
                        return []
                        
                    if status_code == 20000:
                        result_data = first_task.get('result', [])
                        if result_data:
                            logger.info(f"Successful API response from {endpoint}")
                            return result_data
                        else:
                            logger.warning(f"Empty result data from API for {endpoint}")
                            return []
                    else:
                        error_message = first_task.get('status_message', 'Unknown error')
                        logger.error(f"API request failed: {error_message}")
                        
                        # If SSL error and not already retrying with www, suggest retry
                        if not retry_with_www and 'SSL' in error_message:
                            raise SSLError("SSL verification failed")
                        return []
                        
            except aiohttp.ClientResponseError as e:
                logger.error(f"API request failed with status {e.status}: {str(e)}")
                if not retry_with_www and 'SSL' in str(e):
                    raise SSLError("SSL verification failed")
                return []
            except Exception as e:
                logger.error(f"Unexpected error during API request: {str(e)}")
                if not retry_with_www and 'SSL' in str(e):
                    raise SSLError("SSL verification failed")
                return []
            finally:
                # Force garbage collection after request
                gc.collect()

    async def get_website_data(self, url: str) -> Dict[str, Any]:
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        self._current_domain = domain

        logger.error("\n" + "-"*80 + "\n")  # Separator line
        logger.error(f"Fetching website data for {url}")

        # Initialize result dictionary with default values
        result = {
            'cms': 'Error',
            'domain_rank': None,
            'phone_numbers': [],
            'backlinks': 0,
            'backlink_domains': 0,
            'indexed_pages': 0,
            'total_pages': 0
        }

        # First try WordPress detection via scraping
        try:
            is_wordpress = await self.check_wordpress_via_scrape(url)
            if not is_wordpress and not url.startswith('https://www.'):
                # Try scraping with www prefix
                www_url = f"https://www.{domain}"
                is_wordpress = await self.check_wordpress_via_scrape(www_url)

            # result dictionary set cms
            result['cms'] = 'WordPress' if is_wordpress else 'Error'

            # Only get API data for WordPress sites
            if is_wordpress:
                logger.info(f"WordPress detected via scraping for {url}")

                # get domain Rank via DataForSeo API
                try:
                    # Get domain rank via DataForSEO API
                    tech_response = await self._make_request(
                        f"{self.BASE_URL}/domain_analytics/technologies/domain_technologies/live",
                        [{"target": domain, "limit": 1}]
                    )

                    # Log the tech_response
                    # logger.error(f"Tech Response for {url}: {tech_response}")

                    # Validate tech_response
                    if (tech_response and isinstance(tech_response, list) and
                        len(tech_response) > 0 and tech_response[0] and
                        isinstance(tech_response[0], dict)):
                        result['domain_rank'] = tech_response[0].get('domain_rank')
                    else:
                        logger.error(f"No technology data found for {url}. API response: {tech_response}")

                except Exception as e:
                    logger.error(f"Error processing domain rank for {url}: {str(e)}")

                # Get page data
                try:
                    page_data = await self.get_page_data(url)
                    result['indexed_pages'] = page_data.get('indexed_pages', 0)
                    result['total_pages'] = page_data.get('total_pages', 0)

                except Exception as e:
                    logger.error(f"Error processing page data for {url}: {str(e)}")

                # Get backlink data if not already processed
                try:
                    if domain not in self._processed_backlinks:
                        backlink_data = await self.get_backlink_data(url)
                        result['backlinks'] = backlink_data.get('backlinks', 0)
                        result['backlink_domains'] = backlink_data.get('backlink_domains', 0)
                        self._processed_backlinks.add(domain)

                except Exception as e:
                    logger.error(f"Error processing backlink data for {url}: {str(e)}")

        except Exception as e:
            logger.error(f"Error during WordPress scraping for {url}: {str(e)}")

        return result

    async def get_backlink_data(self, url: str) -> Dict[str, int]:
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        
        # Check if we've already processed this domain
        if domain in self._processed_backlinks:
            logger.info(f"Skipping backlink data fetch for {url} - already processed")
            return {'backlinks': 0, 'backlink_domains': 0}
            
        logger.info(f"Fetching backlink data for {url}")
        endpoint = f"{self.BASE_URL}/backlinks/summary/live"
        data = [{
            "target": domain,
            "limit": 1
        }]
        try:
            response = await self._make_request(endpoint, data)
            if response and isinstance(response, list) and len(response) > 0:
                logger.info(f"Successfully retrieved backlink data for {url}")
                result = response[0]
                self._processed_backlinks.add(domain)
                return {
                    'backlinks': result.get('external_links_count', 0),
                    'backlink_domains': result.get('referring_domains', 0)
                }
        except Exception as e:
            logger.error(f"Error processing backlink data for {url}: {str(e)}")
            
        logger.warning(f"No backlink data found for {url}")
        return {'backlinks': 0, 'backlink_domains': 0}

    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=MAX_RETRIES
    )
    async def get_indexed_pages(self, url: str) -> int:
        try:
            domain = self._extract_domain(url)
            logger.info(f"Fetching indexed pages count for {domain}")
            query_params = {
                'key': self.google_api_key,
                'cx': self.google_cse_id,
                'q': f'site:{domain}',
                'num': 1
            }

            async with self.session.get(self.GOOGLE_CSE_URL, params=query_params) as response:
                response.raise_for_status()
                result = await response.json()
                if isinstance(result, dict) and 'searchInformation' in result:
                    total_results = result['searchInformation'].get('totalResults', '0')
                    indexed_pages = int(total_results) if total_results.isdigit() else 0
                    logger.info(f"Found {indexed_pages} indexed pages for {domain}")
                    return indexed_pages
                else:
                    logger.warning(f"Invalid response format from Google CSE for {domain}")
                    return 0
        except Exception as e:
            logger.error(f"Error fetching indexed pages for {url}: {str(e)}")
            return 0

    async def get_robots_txt(self, url: str) -> Tuple[Optional[str], str]:
        url = self._normalize_url(url)
        robots_url = urljoin(url, '/robots.txt')

        logger.info(f"Fetching robots.txt from {robots_url}")

        try:
            async with self.session.get(robots_url, timeout=REQUEST_TIMEOUT) as response:
                if response.status == 200:
                    try:
                        content = await self._decode_content(response)
                        logger.info(f"Successfully retrieved robots.txt for {url}")
                        return content, "Robots.txt found"
                    except Exception as e:
                        logger.error(f"Error decoding robots.txt content for {url}: {str(e)}")
                        return None, f"Error decoding robots.txt content: {str(e)}"
                elif response.status == 403:
                    logger.warning(f"Access forbidden (403) for robots.txt at {url}")
                    return "", "Robots.txt access forbidden (403)"
                elif response.status == 404:
                    logger.warning(f"Robots.txt not found (404) at {url}")
                    return "", "Robots.txt not found (404)"
                else:
                    logger.warning(f"Unexpected status code {response.status} for robots.txt at {url}")
                    return None, f"Unexpected status code {response.status} for robots.txt"
        except asyncio.TimeoutError:
            logger.error(f"Timeout while fetching robots.txt for {url}")
            return None, "Timeout while fetching robots.txt"
        except Exception as e:
            logger.error(f"Error fetching robots.txt for {url}: {str(e)}")
            return None, f"Error fetching robots.txt: {str(e)}"

    def get_sitemaps(self, robots_txt: Optional[str]) -> List[str]:
        sitemaps = []
        if robots_txt:
            for line in robots_txt.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemaps.append(line.split(': ')[1].strip())
        return sitemaps

    async def try_default_sitemaps(self, url: str) -> List[str]:
        """Try to access common default sitemap locations."""
        default_paths = [
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/wp-sitemap.xml',
            '/sitemaps.xml',
            '/sitemap/',
            '/sitemap/sitemap.xml'
        ]

        sitemaps = []
        tasks = []
        for path in default_paths:
            sitemap_url = urljoin(url, path)
            tasks.append(self._check_sitemap(sitemap_url))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for sitemap_url, is_valid in zip(default_paths, results):
            if isinstance(is_valid, bool) and is_valid:
                full_url = urljoin(url, sitemap_url)
                sitemaps.append(full_url)
                logger.info(f"Found valid sitemap at {full_url}")
        
        return sitemaps

    async def _check_sitemap(self, url: str) -> bool:
        """Check if a sitemap URL is valid."""
        try:
            async with self.session.get(url, timeout=REQUEST_TIMEOUT) as response:
                is_valid = response.status == 200
                if not is_valid and self._current_domain:
                    logger.warning(f"Invalid sitemap {url} for domain {self._current_domain}")
                return is_valid
        except Exception as e:
            if self._current_domain:
                logger.warning(f"Error checking sitemap {url} for domain {self._current_domain}: {str(e)}")
            else:
                logger.warning(f"Error checking sitemap {url}: {str(e)}")
            return False

    async def parse_sitemap(self, url: str, depth: int = 0) -> List[str]:
        if depth > MAX_SITEMAP_DEPTH:
            logger.warning(f"Maximum sitemap depth reached for {url}")
            return []

        logger.info(f"Parsing sitemap at {url} (depth: {depth})")
        try:
            async with self.session.get(url, timeout=REQUEST_TIMEOUT) as response:
                try:
                    content = await self._decode_content(response)
                    soup = BeautifulSoup(content, 'lxml-xml')

                    urls = []
                    sitemapindex = soup.find('sitemapindex')
                    
                    if sitemapindex:
                        logger.info(f"Found sitemap index at {url}")
                        sitemap_urls = [loc.text for loc in sitemapindex.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
                        tasks = [self.parse_sitemap(u, depth+1) for u in sitemap_urls]
                        nested_urls = await asyncio.gather(*tasks, return_exceptions=True)
                        for result in nested_urls:
                            if isinstance(result, list):
                                urls.extend(result)
                    else:
                        urls = [loc.text for loc in soup.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
                        logger.info(f"Found {len(urls)} URLs in sitemap at {url}")

                    return urls
                except Exception as e:
                    if self._current_domain:
                        logger.warning(f"Error processing sitemap {url} for domain {self._current_domain}: {str(e)}")
                    else:
                        logger.warning(f"Error processing sitemap {url}: {str(e)}")
                    return []
        except Exception as e:
            if self._current_domain:
                logger.warning(f"Error fetching sitemap {url} for domain {self._current_domain}: {str(e)}")
            else:
                logger.warning(f"Error fetching sitemap {url}: {str(e)}")
            return []

    async def get_total_pages(self, url: str) -> Tuple[int, str]:
        url = self._normalize_url(url)
        logger.info(f"Getting total pages count for {url}")
        
        try:
            robots_txt, status = await self.get_robots_txt(url)
            
            sitemaps = self.get_sitemaps(robots_txt) if robots_txt is not None else []
            
            if not sitemaps:
                logger.info("No sitemaps found in robots.txt, trying default locations...")
                sitemaps = await self.try_default_sitemaps(url)
            
            if not sitemaps:
                logger.error(f"No sitemaps found for {url}")
                return 0, "No sitemaps found in robots.txt or default locations"
            
            logger.info(f"Found {len(sitemaps)} sitemaps for {url}")
            tasks = [self.parse_sitemap(sitemap) for sitemap in sitemaps]
            url_lists = await asyncio.gather(*tasks, return_exceptions=True)
            total_urls = set()
            
            for result in url_lists:
                if isinstance(result, list):
                    total_urls.update(result)
            
            if not total_urls:
                logger.warning(f"No URLs found in sitemaps for {url}")
                return 0, "No URLs found in sitemaps"
            
            logger.info(f"Found total of {len(total_urls)} unique URLs for {url}")
            return len(total_urls), "Total pages counted from sitemaps"
        except Exception as e:
            logger.error(f"Error in get_total_pages for {url}: {str(e)}")
            return 0, f"Error getting total pages: {str(e)}"

    async def get_page_data(self, url: str) -> Dict[str, Any]:
        url = self._normalize_url(url)
        logger.info(f"Getting page data for {url}")

        try:
            # Create tasks for concurrent execution
            total_pages_task = asyncio.create_task(self.get_total_pages(url))
            indexed_pages_task = asyncio.create_task(self.get_indexed_pages(url))
            
            # Wait for both tasks to complete
            total_pages_result, indexed_pages = await asyncio.gather(
                total_pages_task,
                indexed_pages_task,
                return_exceptions=True
            )
            
            # Handle total_pages_result
            if isinstance(total_pages_result, Exception):
                logger.error(f"Error getting total pages: {str(total_pages_result)}")
                total_pages, status = 0, f"Error: {str(total_pages_result)}"
            else:
                total_pages, status = total_pages_result
            
            # Handle indexed_pages
            if isinstance(indexed_pages, Exception):
                logger.error(f"Error getting indexed pages: {str(indexed_pages)}")
                indexed_pages = 0
            
            return {
                'total_pages': total_pages,
                'indexed_pages': indexed_pages,
                'status': status
            }
        except Exception as e:
            logger.error(f"Error getting page data for {url}: {str(e)}")
            return {
                'total_pages': 0,
                'indexed_pages': 0,
                'status': f"Error: {str(e)}"
            }

# Custom exception for SSL errors
class SSLError(Exception):
    pass
