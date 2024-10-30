import aiohttp
import asyncio
from src.config import DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD, GOOGLE_API_KEY, GOOGLE_CSE_ID
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import gzip
from io import BytesIO

# logging.basicConfig(level=logging.INFO)

TIMEOUT = 10
MAX_SITEMAP_DEPTH = 2
MAX_URLS_PER_SITEMAP = 10000

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

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(auth=self.auth)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def _extract_domain(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    async def get_website_data(self, url):
        domain = self._extract_domain(url)
        endpoint = f"{self.BASE_URL}/domain_analytics/technologies/domain_technologies/live"
        data = [{"target": domain}]
        response = await self._make_request(endpoint, data)
        if response and response[0]:
            result = response[0]
            return {
                'is_wordpress': 'WordPress' in result.get('technologies', {}).get('content', {}).get('cms', []),
                'domain_rank': result.get('domain_rank'),
                'phone_numbers': result.get('phone_numbers', []) or [],
                'emails': result.get('emails', []) or []
            }
        return {
            'is_wordpress': False,
            'domain_rank': None,
            'phone_numbers': [],
            'emails': []
        }

    async def get_backlink_data(self, url):
        domain = self._extract_domain(url)
        endpoint = f"{self.BASE_URL}/backlinks/summary/live"
        data = [{"target": domain}]
        response = await self._make_request(endpoint, data)
        if response and response[0]:
            return {
                'external_links_count': response[0].get('external_links_count', 0),
                'referring_domains': response[0].get('referring_domains', 0)
            }
        return {'external_links_count': 0, 'referring_domains': 0}

    async def get_indexed_pages(self, url):
        domain = self._extract_domain(url)
        query_params = {
            'key': self.google_api_key,
            'cx': self.google_cse_id,
            'q': f'site:{domain}',
            'num': 1  # We only need the total count, not the actual results
        }
        
        try:
            async with self.session.get(self.GOOGLE_CSE_URL, params=query_params) as response:
                response.raise_for_status()
                result = await response.json()
                # logging.info(f"Google CSE API Response: {result}")
                
                indexed_pages = int(result.get('searchInformation', {}).get('totalResults', 0))
                return indexed_pages
        except Exception as e:
            # logging.error(f"Error fetching indexed pages for {url}: {str(e)}")
            return 0

    async def get_robots_txt(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        scheme = parsed_url.scheme or 'https'
        robots_url = f"{scheme}://{domain}/robots.txt"
        
        try:
            async with self.session.get(robots_url, timeout=TIMEOUT) as response:
                return await response.text()
        except Exception as e:
            # logging.error(f"Could not fetch robots.txt for {url}: {str(e)}")
            return None

    def get_sitemaps(self, robots_txt):
        sitemaps = []
        if robots_txt:
            for line in robots_txt.split('\n'):
                if line.lower().startswith('sitemap:'):
                    sitemaps.append(line.split(': ')[1].strip())
        return sitemaps

    async def parse_sitemap(self, url, depth=0):
        if depth > MAX_SITEMAP_DEPTH:
            # logging.warning(f"Max sitemap depth reached for {url}")
            return []

        try:
            async with self.session.get(url, timeout=TIMEOUT) as response:
                if response.headers.get('Content-Type') == 'application/x-gzip':
                    content = await response.read()
                    content = gzip.decompress(content)
                else:
                    content = await response.text()
            
            soup = BeautifulSoup(content, 'lxml-xml')
            
            urls = []
            
            sitemapindex = soup.find('sitemapindex')
            if sitemapindex:
                sitemap_urls = [loc.text for loc in sitemapindex.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
                tasks = [self.parse_sitemap(u, depth+1) for u in sitemap_urls]
                nested_urls = await asyncio.gather(*tasks)
                urls = [url for sublist in nested_urls for url in sublist if sublist]
            else:
                urls = [loc.text for loc in soup.find_all('loc')[:MAX_URLS_PER_SITEMAP]]
            
            if not urls:
                # logging.warning(f"No URLs found in sitemap: {url}")
                pass
            
            return urls
        except Exception as e:
            # logging.error(f"Error processing sitemap {url}: {str(e)}")
            return []

    async def get_total_pages(self, url):
        try:
            robots_txt = await self.get_robots_txt(url)
            if not robots_txt:
                # logging.warning(f"No robots.txt found for {url}")
                return 0
            
            sitemaps = self.get_sitemaps(robots_txt)
            if not sitemaps:
                # logging.warning(f"No sitemaps found in robots.txt for {url}")
                return 0
            
            tasks = [self.parse_sitemap(sitemap) for sitemap in sitemaps]
            url_lists = await asyncio.gather(*tasks)
            total_urls = set()
            for urls in url_lists:
                total_urls.update(urls)
            
            if not total_urls:
                # logging.warning(f"No valid URLs found in any sitemap for {url}")
                return 0
            
            return len(total_urls)
        except Exception as e:
            # logging.error(f"Error getting total pages for {url}: {str(e)}")
            return 0

    async def get_page_data(self, url):
        total_pages = await self.get_total_pages(url)
        indexed_pages = await self.get_indexed_pages(url)
        return {
            'total_pages': total_pages,
            'indexed_pages': indexed_pages,
        }

    async def _make_request(self, endpoint, data):
        try:
            async with self.session.post(endpoint, json=data) as response:
                response.raise_for_status()
                result = await response.json()
                # logging.info(f"API Response: {result}")
                tasks = result.get('tasks', [])
                if tasks and tasks[0]['status_code'] == 20000:
                    return tasks[0].get('result', [])
                else:
                    error_message = tasks[0]['status_message'] if tasks else "Unknown error"
                    # logging.error(f"API request failed: {error_message}")
                    return None
        except aiohttp.ClientResponseError as e:
            # logging.error(f"API request failed: {e}")
            pass
        except Exception as e:
            # logging.error(f"Unexpected error during API request: {e}")
            pass
        return None