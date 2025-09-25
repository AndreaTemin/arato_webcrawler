import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import multiprocessing as mp
from utls import save_page


def worker(worker_id, queue, visited_urls, folder_path, domain):
    """A worker function to be run by each process."""
    print(f"[Worker-{worker_id}] Started and waiting for URLs.")
    while True:
        url, depth = queue.get()
        try:
            if url in visited_urls or depth >= 7:
                continue

            visited_urls[url] = 1
            print(f"[Worker-{worker_id}] Crawling: {url} (Depth: {depth})")

            html_content = fetch_page(url, worker_id)
            if html_content:
                download_page(url, html_content, folder_path, worker_id)
                links = extract_links(html_content)

                for link in links:
                    absolute_url = urljoin(url, link)
                    # Check if the link is within the same domain
                    if urlparse(absolute_url).netloc == domain:
                        queue.put((absolute_url, depth + 1))
        finally:
            queue.task_done()


class Crawler:
    def __init__(self, entry_url, folder_path, num_workers):
        self.entry_url = entry_url
        self.folder_path = folder_path
        self.num_workers = num_workers
        self.domain = urlparse(entry_url).netloc

    def start(self):
        """Starts the crawler manager and worker processes."""
        manager = mp.Manager()
        visited_urls = manager.dict()
        queue = mp.JoinableQueue()

        # Add the entry point to the queue
        queue.put((self.entry_url, 0))

        # Create and start worker processes
        processes = []
        for i in range(self.num_workers):
            process = mp.Process(target=worker, args=(i, queue, visited_urls, self.folder_path, self.domain))
            process.daemon = True  # Allows main process to exit even if workers are alive
            process.start()
            processes.append(process)

        # Wait for the queue to be empty
        queue.join()

        print("\nAll pages have been processed. Crawler finished.")


def extract_links(html_content) -> set:
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    return {link.get('href') for link in links}

def download_page(url, content, folder_path, worker_id):
    filename = urlparse(url).path.strip('/').replace('/', '_') or 'index'
    filename += '.html'

    save_page(file_path=os.path.join(folder_path, filename), content=content)
    print(f"[Worker-{worker_id}] Downloaded: {url}")

def fetch_page(url, worker_id):
    try:
        # Set a browser-like User-Agent and increase the timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Increased timeout to 30 seconds
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[Worker-{worker_id}] Error - Couldn't fetch {url}: {e}")
    return None