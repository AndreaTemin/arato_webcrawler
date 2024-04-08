import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests 
from utls import save_page


class Crawler:
    def __init__(self, entry_url, folder_path):
        self.entry_url = entry_url
        self.folder_path = folder_path
        self.visited_urls = set()
        max

    def start_crawl(self):
        self.crawl_page(self.entry_url)

    def crawl_page(self, url):
        if url in self.visited_urls:
            print(f"The page {url}, has already been visited")
            return
        
        self.visited_urls.add(url)
        
        html_content = self.fetch_page(url)
        if html_content:
            self.download_page(url, html_content)
            links = self.extract_links(html_content)
            
            # remove duplicates
            links = set(links)
            # difference between sets, remove possible duplicate, avoids possible loops
            links.difference_update(self.visited_urls)
            
            for link in links:
                absolute_url = urljoin(url, link)
                if urlparse(absolute_url).netloc == urlparse(url).netloc:
                    self.crawl_page(absolute_url)


    def extract_links(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a', href=True)
        return [link.get('href') for link in links]




    def download_page(self, url, content):
        # getting the name of the file from the url after the .com
        filename = urlparse(url).path.replace('/', '_') + '.html'

        
        # storing the page locally 
        save_page(
            file_path = os.path.join(self.folder_path, filename),
            content = content
        )
        print(f"The page {url} has been downloaded")


    def fetch_page(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.text
            
        except Exception as e:
            print(f"Error - Culdn't fetch {url}: {e}")
        return None