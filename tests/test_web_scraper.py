import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch, MagicMock
from web_scraper import get_indexed_pages, get_robots_txt, get_sitemaps, count_urls_in_sitemap, get_total_pages

class TestWebScraper(unittest.TestCase):

    @patch('web_scraper.requests.get')
    def test_get_indexed_pages(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = '<div id="result-stats">About 1,000 results</div>'
        mock_get.return_value = mock_response

        result = get_indexed_pages('example.com')
        self.assertEqual(result, 1000)

    @patch('web_scraper.requests.get')
    def test_get_robots_txt(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = 'User-agent: *\nDisallow: /private/'
        mock_get.return_value = mock_response

        result = get_robots_txt('example.com')
        self.assertEqual(result, 'User-agent: *\nDisallow: /private/')

    def test_get_sitemaps(self):
        robots_txt = 'User-agent: *\nDisallow: /private/\nSitemap: https://example.com/sitemap.xml'
        result = get_sitemaps(robots_txt)
        self.assertEqual(result, ['https://example.com/sitemap.xml'])

    @patch('web_scraper.requests.get')
    def test_count_urls_in_sitemap(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = '''
        <?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
           <url>
              <loc>http://www.example.com/</loc>
           </url>
           <url>
              <loc>http://www.example.com/page1</loc>
           </url>
        </urlset>
        '''
        mock_get.return_value = mock_response

        result = count_urls_in_sitemap('https://example.com/sitemap.xml')
        self.assertEqual(result, 2)

    @patch('web_scraper.get_robots_txt')
    @patch('web_scraper.get_sitemaps')
    @patch('web_scraper.count_urls_in_sitemap')
    def test_get_total_pages(self, mock_count, mock_get_sitemaps, mock_get_robots):
        mock_get_robots.return_value = 'User-agent: *\nSitemap: https://example.com/sitemap.xml'
        mock_get_sitemaps.return_value = ['https://example.com/sitemap.xml']
        mock_count.return_value = 10

        result = get_total_pages('example.com')
        self.assertEqual(result, 10)

if __name__ == '__main__':
    unittest.main()