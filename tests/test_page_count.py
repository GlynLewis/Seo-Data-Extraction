import asyncio
import sys
import os
from urllib.request import urlopen
from urllib.parse import urlparse
import re
from bs4 import BeautifulSoup

# Add the parent directory of the script to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

async def get_robots_txt(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    scheme = parsed_url.scheme or 'https'
    robots_url = f"{scheme}://{domain}/robots.txt"
    
    try:
        with urlopen(robots_url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Could not fetch robots.txt for {url}: {str(e)}")
        return None

def get_sitemaps(robots_txt):
    sitemaps = []
    if robots_txt:
        for line in robots_txt.split('\n'):
            if line.lower().startswith('sitemap:'):
                sitemaps.append(line.split(': ')[1].strip())
    return sitemaps

async def parse_sitemap(url, depth=0):
    if depth > 2:  # MAX_SITEMAP_DEPTH
        return []

    try:
        with urlopen(url) as response:
            content = response.read()
            if response.info().get('Content-Type') == 'application/x-gzip':
                import gzip
                content = gzip.decompress(content)
            content = content.decode('utf-8')
        
        soup = BeautifulSoup(content, 'xml')
        
        urls = []
        
        sitemapindex = soup.find('sitemapindex')
        if sitemapindex:
            sitemap_urls = [loc.text for loc in sitemapindex.find_all('loc')[:10000]]  # MAX_URLS_PER_SITEMAP
            for u in sitemap_urls:
                urls.extend(await parse_sitemap(u, depth+1))
        else:
            urls = [loc.text for loc in soup.find_all('loc')[:10000]]  # MAX_URLS_PER_SITEMAP
        
        return urls
    except Exception as e:
        print(f"Error processing sitemap {url}: {str(e)}")
        return []

async def get_total_pages(url):
    robots_txt = await get_robots_txt(url)
    if not robots_txt:
        return 0
    
    sitemaps = get_sitemaps(robots_txt)
    if not sitemaps:
        return 0
    
    total_urls = set()
    for sitemap in sitemaps:
        urls = await parse_sitemap(sitemap)
        total_urls.update(urls)
    
    return len(total_urls)

async def get_google_indexed_pages(url):
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    search_url = f"https://www.google.com/search?q=site:{domain}&hl=en&filter=0"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        req = urllib.request.Request(search_url, headers=headers)
        with urlopen(req) as response:
            content = response.read().decode('utf-8')
        
        soup = BeautifulSoup(content, 'html.parser')
        
        result_stats = soup.find('div', {'id': 'result-stats'})
        if result_stats:
            match = re.search(r'About ([\d,]+) results', result_stats.text)
            if match:
                return int(match.group(1).replace(',', ''))
        
        return 0
    except Exception as e:
        print(f"Error fetching Google search results for {url}: {str(e)}")
        return 0

async def test_page_count(url):
    print(f"Testing page count for: {url}")
    
    # Get total pages from sitemap
    total_pages = await get_total_pages(url)
    print(f"Total pages found in sitemap: {total_pages}")
    
    # Get estimated indexed pages from Google
    indexed_pages = await get_google_indexed_pages(url)
    print(f"Estimated pages indexed by Google: {indexed_pages}")
    
    print(f"Test completed for {url}\n")

async def main():
    # List of websites to test
    websites = [
        "https://foundationinc.co"
    ]
    
    for website in websites:
        await test_page_count(website)

if __name__ == "__main__":
    asyncio.run(main())