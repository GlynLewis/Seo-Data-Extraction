import aiohttp
import asyncio
from src.config import DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, GOOGLE_API_KEY, GOOGLE_CSE_ID
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import re
import gzip
import brotli
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TIMEOUT = 10
MAX_SITEMAP_DEPTH = 2
MAX_URLS_PER_SITEMAP = 10000

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

    async def __aenter__(self):
        logger.info("Initializing DataForSEO client session")
        if not self.session:
            self.session = aiohttp.ClientSession(auth=self.auth, headers=BROWSER_HEADERS)
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
                    await asyncio.sleep(0.25)
                except Exception as e:
                    logger.error(f"Error closing session: {str(e)}")
                finally:
                    self.session = None
                    self._is_closing = False

    def _extract_domain(self, url):
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        return domain

    def _normalize_url(self, url):
        """Ensure URL has a protocol."""
        if not url.startswith(('http://', 'https://')):
            return 'https://' + url
        return url

    async def _decode_content(self, response):
        """Helper method to decode response content based on Content-Type and Content-Encoding."""
        try:
            content_type = response.headers.get('Content-Type', '').lower()
            content_encoding = response.headers.get('Content-Encoding', '').lower()
            raw_content = await response.read()

            # Try to decode based on content encoding
            if content_encoding == 'br':
                try:
                    return brotli.decompress(raw_content).decode('utf-8')
                except Exception as e:
                    # If brotli decompression fails, try direct decoding
                    return raw_content.decode('utf-8')
            elif content_encoding == 'gzip':
                try:
                    return gzip.decompress(raw_content).decode('utf-8')
                except Exception as e:
                    # If gzip decompression fails, try direct decoding
                    return raw_content.decode('utf-8')
            else:
                # No compression or unknown compression, decode directly
                return raw_content.decode('utf-8')
        except Exception as e:
            logger.error(f"Error decoding content: {str(e)}")
            raise

    async def get_website_data(self, url):
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        logger.info(f"Fetching website data for {url}")
        endpoint = f"{self.BASE_URL}/domain_analytics/technologies/domain_technologies/live"
        
        data = [{
            "target": domain,
            "limit": 1
        }]
        
        response = await self._make_request(endpoint, data)
        if response and response[0]:
            logger.info(f"Successfully retrieved website data for {url}")
            result = response[0]
            technologies = result.get('technologies', {})
            cms_items = []

            # Extract CMS information from the correct path in the response
            if 'cms' in technologies:
                cms_items = technologies['cms']
            elif 'content' in technologies and 'cms' in technologies['content']:
                cms_items = technologies['content']['cms']
            logger.warning(f"CMS Result {cms_items}")

            # Determine CMS value based on the three cases
            if cms_items:
                # Check if any CMS is WordPress (case-insensitive)
                if any('wordpress' in item.lower() for item in cms_items):
                    cms_value = 'Wordpress'  # WordPress detected
                else:
                    # Not WordPress, return the actual CMS name
                    cms_value = cms_items[0]  # Use the first CMS found
            else:
                cms_value = 'Error'  # No CMS detected

            return {
                'cms': cms_value,
                'domain_rank': result.get('domain_rank'),
                'phone_numbers': result.get('phone_numbers', []) or [],
                'emails': result.get('emails', []) or []
            }
        logger.warning(f"No website data found for {url}")
        return {
            'cms': 'Error',
            'domain_rank': None,
            'phone_numbers': [],
            'emails': []
        }

    async def get_backlink_data(self, url):
        url = self._normalize_url(url)
        domain = self._extract_domain(url)
        logger.info(f"Fetching backlink data for {url}")
        endpoint = f"{self.BASE_URL}/backlinks/summary/live"
        data = [{
            "target": domain,
            "limit": 1
        }]
        response = await self._make_request(endpoint, data)
        if response and response[0]:
            logger.info(f"Successfully retrieved backlink data for {url}")
            return {
                'backlinks': response[0].get('external_links_count', 0),
                'backlink_domains': response[0].get('referring_domains', 0)
            }
        logger.warning(f"No backlink data found for {url}")
        return {'backlinks': 0, 'backlink_domains': 0}

    async def get_indexed_pages(self, url):
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
                indexed_pages = int(result.get('searchInformation', {}).get('totalResults', 0))
                logger.info(f"Found {indexed_pages} indexed pages for {domain}")
                return indexed_pages
        except Exception as e:
            logger.error(f"Error fetching indexed pages for {url}: {str(e)}")
            return 0

    async def get_robots_txt(self, url):
        url = self._normalize_url(url)
        robots_url = urljoin(url, '/robots.txt')

        logger.info(f"Fetching robots.txt from {robots_url}")

        try:
            async with self.session.get(robots_url, timeout=TIMEOUT) as response:
                if response.status == 200:
                    try:
                        content = await self._decode_content(response)
                        logger.info(f"Successfully retrieved robots.txt for {url}")
                        return content, "Robots.txt found"
                    except Exception as e:
                        logger.error(f"Error decoding robots.txt content: {str(e)}")
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

    def get_sitemaps(self, robots_txt):
        sitemaps = []
        if robots_txt:
            for line in robots_txt.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemaps.append(line.split(': ')[1].strip())
        return sitemaps

    async def try_default_sitemaps(self, url):
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
        for path in default_paths:
            sitemap_url = urljoin(url, path)
            try:
                async with self.session.get(sitemap_url, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        logger.info(f"Found default sitemap at {sitemap_url}")
                        sitemaps.append(sitemap_url)
            except Exception as e:
                logger.error(f"Could not access {sitemap_url}: {str(e)}")
                continue

        return sitemaps

    async def parse_sitemap(self, url, depth=0):
        if depth > MAX_SITEMAP_DEPTH:
            logger.warning(f"Maximum sitemap depth reached for {url}")
            return []

        logger.info(f"Parsing sitemap at {url} (depth: {depth})")
        try:
            async with self.session.get(url, timeout=TIMEOUT) as response:
                try:
                    content = await self._decode_content(response)
                    soup = BeautifulSoup(content, 'lxml-xml')

                    urls = []

                    sitemapindex = soup.find('sitemapindex')
                    if sitemapindex:
                        logger.info(f"Found sitemap index at {url}")
                        sitemap_urls = [loc.text for loc in sitemapindex.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
                        tasks = [self.parse_sitemap(u, depth+1) for u in sitemap_urls]
                        nested_urls = await asyncio.gather(*tasks)
                        urls = [url for sublist in nested_urls for url in sublist if sublist]
                    else:
                        urls = [loc.text for loc in soup.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
                        logger.info(f"Found {len(urls)} URLs in sitemap at {url}")

                    return urls
                except Exception as e:
                    logger.error(f"Error processing sitemap content: {str(e)}")
                    return []
        except Exception as e:
            logger.error(f"Error fetching sitemap {url}: {str(e)}")
            return []

    async def get_total_pages(self, url):
        url = self._normalize_url(url)
        logger.info(f"Getting total pages count for {url}")
        robots_txt, status = await self.get_robots_txt(url)
        
        # First try to get sitemaps from robots.txt
        sitemaps = self.get_sitemaps(robots_txt) if robots_txt is not None else []
        
        # If no sitemaps found in robots.txt, try default locations
        if not sitemaps:
            logger.info("No sitemaps found in robots.txt, trying default locations...")
            sitemaps = await self.try_default_sitemaps(url)
        
        if not sitemaps:
            logger.warning(f"No sitemaps found for {url}")
            return 0, "No sitemaps found in robots.txt or default locations"
        
        logger.info(f"Found {len(sitemaps)} sitemaps for {url}")
        tasks = [self.parse_sitemap(sitemap) for sitemap in sitemaps]
        url_lists = await asyncio.gather(*tasks)
        total_urls = set()
        for urls in url_lists:
            total_urls.update(urls)
        
        if not total_urls:
            logger.warning(f"No URLs found in sitemaps for {url}")
            return 0, "No URLs found in sitemaps"
        
        logger.info(f"Found total of {len(total_urls)} unique URLs for {url}")
        return len(total_urls), "Total pages counted from sitemaps"

    async def get_page_data(self, url):
        url = self._normalize_url(url)
        logger.info(f"Getting page data for {url}")
        total_pages, total_pages_status = await self.get_total_pages(url)
        indexed_pages = await self.get_indexed_pages(url)
        return {
            'total_pages': total_pages,
            'indexed_pages': indexed_pages,
            'status': total_pages_status
        }

    async def _make_request(self, endpoint, data):
        logger.info(f"Making API request to {endpoint}")
        try:
            async with self.session.post(endpoint, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                tasks = result.get('tasks', [])
                if tasks and tasks[0]['status_code'] == 20000:
                    logger.info(f"Successful API response from {endpoint}")
                    return tasks[0].get('result', [])
                else:
                    error_message = tasks[0]['status_message'] if tasks else "Unknown error"
                    logger.error(f"API request failed: {error_message}")
                    return None
        except aiohttp.ClientResponseError as e:
            logger.error(f"API request failed with status {e.status}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
        return None
