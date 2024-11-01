import aiohttp
import asyncio
from constants import (
    DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, GOOGLE_API_KEY, GOOGLE_CSE_ID,
    DEFAULT_TIMEOUT, MAX_SITEMAP_DEPTH, MAX_URLS_PER_SITEMAP, MAX_RETRIES,
    RETRY_DELAY, TCP_CONNECTOR_LIMIT, FORCE_CLOSE_CONNECTIONS, ENABLE_CLEANUP_CLOSED
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
WP_PATTERNS = [
    r'/wp-content/',
    r'/wp-includes/',
    r'wp-[a-zA-Z0-9-]+\.(?:js|css)',
    r'themes/[a-zA-Z0-9-]+/',
    r'plugins/[a-zA-Z0-9-]+/',
    r'wp-json/',
    r'xmlrpc.php',
    r'wp-login.php'
]

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
                    return False
                
                content = await self._decode_content(response)
                soup = BeautifulSoup(content, 'html.parser')
                
                # Check meta generator tag
                meta_generator = soup.find('meta', {'name': 'generator'})
                if meta_generator and 'wordpress' in meta_generator.get('content', '').lower():
                    return True
                
                # Check for WordPress patterns in HTML
                html_str = str(soup)
                for pattern in WP_PATTERNS:
                    if re.search(pattern, html_str, re.IGNORECASE):
                        return True
                
                # Check for wp-json API endpoint
                try:
                    wp_json_url = urljoin(url, '/wp-json/')
                    async with self.session.get(wp_json_url, timeout=REQUEST_TIMEOUT) as wp_response:
                        return wp_response.status == 200
                except:
                    pass
                
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
    async def _make_request(self, endpoint: str, data: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
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
                        return None
                        
                    tasks = result.get('tasks', [])
                    if not tasks:
                        logger.error("No tasks found in API response")
                        return None
                        
                    # Safely access first task
                    first_task = tasks[0] if tasks else None
                    if not first_task:
                        logger.error("Empty task in API response")
                        return None
                        
                    status_code = first_task.get('status_code')
                    if not status_code:
                        logger.error(f"No status code in task: {first_task}")
                        return None
                        
                    if status_code == 20000:
                        result_data = first_task.get('result', [])
                        if result_data:
                            logger.info(f"Successful API response from {endpoint}")
                            return result_data
                        else:
                            logger.warning(f"Empty result data from API for {endpoint}")
                            return None
                    else:
                        error_message = first_task.get('status_message', 'Unknown error')
                        logger.error(f"API request failed: {error_message}")
                        return None
                        
            except aiohttp.ClientResponseError as e:
                logger.error(f"API request failed with status {e.status}: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error during API request: {str(e)}")
                raise
            finally:
                # Force garbage collection after request
                gc.collect()

    async def get_website_data(self, url: str) -> Dict[str, Any]:
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        self._current_domain = domain  # Store current domain
        logger.info(f"Fetching website data for {url}")
        endpoint = f"{self.BASE_URL}/domain_analytics/technologies/domain_technologies/live"
        
        data = [{
            "target": domain,
            "limit": 1
        }]
        
        try:
            response = await self._make_request(endpoint, data)
            if response and isinstance(response, list) and len(response) > 0:
                logger.info(f"Successfully retrieved website data for {url}")
                result = response[0]
                technologies = result.get('technologies', {})
                cms_items = []

                if isinstance(technologies, dict):
                    if 'cms' in technologies:
                        cms_items = technologies['cms']
                    elif 'content' in technologies and isinstance(technologies['content'], dict):
                        cms = technologies['content'].get('cms', [])
                        if isinstance(cms, list):
                            cms_items = cms

                if cms_items and isinstance(cms_items, list):
                    if any('wordpress' in str(item).lower() for item in cms_items):
                        cms_value = 'Wordpress'
                    else:
                        cms_value = str(cms_items[0]) if cms_items else 'Error'
                else:
                    # If no CMS detected, try scraping for WordPress
                    logger.info(f"No CMS detected via API for {url}, attempting WordPress detection via scrape")
                    is_wordpress = await self.check_wordpress_via_scrape(url)
                    cms_value = 'Wordpress_SC' if is_wordpress else 'Error'

                return {
                    'cms': cms_value,
                    'domain_rank': result.get('domain_rank'),
                    'phone_numbers': result.get('phone_numbers', []) or [],
                    'emails': result.get('emails', []) or []
                }
        except Exception as e:
            logger.error(f"Error processing website data for {url}: {str(e)}")
            
            # Try scraping as a fallback
            logger.info(f"Attempting WordPress detection via scrape for {url} after API error")
            try:
                is_wordpress = await self.check_wordpress_via_scrape(url)
                return {
                    'cms': 'Wordpress_SC' if is_wordpress else 'Error',
                    'domain_rank': None,
                    'phone_numbers': [],
                    'emails': []
                }
            except Exception as scrape_error:
                logger.error(f"Error during scrape fallback for {url}: {str(scrape_error)}")
            
        logger.warning(f"No website data found for {url}")
        return {
            'cms': 'Error',
            'domain_rank': None,
            'phone_numbers': [],
            'emails': []
        }

    async def get_backlink_data(self, url: str) -> Dict[str, int]:
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
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
        domain = self._extract_domain(url)
        logger.info(f"Fetching indexed pages count for {domain}")
        query_params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': f'site:{domain}',
            'num': 1
        }

        try:
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
                    logger.error(f"Invalid sitemap {url} for domain {self._current_domain}")
                return is_valid
        except Exception as e:
            if self._current_domain:
                logger.error(f"Error checking sitemap {url} for domain {self._current_domain}: {str(e)}")
            else:
                logger.error(f"Error checking sitemap {url}: {str(e)}")
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
                        logger.error(f"Error processing sitemap {url} for domain {self._current_domain}: {str(e)}")
                    else:
                        logger.error(f"Error processing sitemap {url}: {str(e)}")
                    return []
        except Exception as e:
            if self._current_domain:
                logger.error(f"Error fetching sitemap {url} for domain {self._current_domain}: {str(e)}")
            else:
                logger.error(f"Error fetching sitemap {url}: {str(e)}")
            return []

    async def get_total_pages(self, url: str) -> Tuple[int, str]:
        url = self._normalize_url(url)
        logger.info(f"Getting total pages count for {url}")
        robots_txt, status = await self.get_robots_txt(url)
        
        sitemaps = self.get_sitemaps(robots_txt) if robots_txt is not None else []
        
        if not sitemaps:
            logger.info("No sitemaps found in robots.txt, trying default locations...")
            sitemaps = await self.try_default_sitemaps(url)
        
        if not sitemaps:
            logger.warning(f"No sitemaps found for {url}")
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

    async def get_page_data(self, url: str) -> Dict[str, Any]:
        url = self._normalize_url(url)
        logger.info(f"Getting page data for {url}")
        
        # Run both operations concurrently
        total_pages_task = self.get_total_pages(url)
        indexed_pages_task = self.get_indexed_pages(url)
        
        total_pages, total_pages_status = await total_pages_task
        indexed_pages = await indexed_pages_task
        
        return {
            'total_pages': total_pages,
            'indexed_pages': indexed_pages,
            'status': total_pages_status
        }
