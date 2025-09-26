import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import threading
from queue import Queue, Empty
from utls import save_page


def worker(worker_id, queue:Queue, visited_urls:set, visited_lock, folder_path, domain):
    """A worker function to be run by each process."""
    print(f"[Worker-{worker_id}] Started and waiting for URLs.")
    while True:
        item = queue.get() # This will block
        if item is None:
            # "Poison pill" received, exit the loop.
            break

        url, depth = item
        try:
            print(f"[Worker-{worker_id}] lock requested")
            with visited_lock:
                if url in visited_urls or depth >= 7:
                    print(f"[Worker-{worker_id}] lock released")
                    continue
                
                visited_urls.add(url)
                print(f"[Worker-{worker_id}] lock released")

            print(f"[Worker-{worker_id}] Crawling: {url} (Depth: {depth})")
            html_content = fetch_page(url, worker_id)
            if html_content:
                download_page(url, html_content, folder_path, worker_id)
                links = extract_links(html_content)

                for link in links:
                    absolute_url = urljoin(url, link)
                    # Check if the link is within the same domain
                    if (urlparse(absolute_url).netloc == domain) and (absolute_url not in visited_urls):
                        queue.put((absolute_url, depth + 1)) if True else False
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
        visited_urls = set()
        visited_lock = threading.Lock()
        queue = Queue()

        # Add the entry point to the queue
        queue.put((self.entry_url, 0)) # 0 represents the depth

        # Create and start worker processes
        threads = []
        for i in range(self.num_workers):
            thread = threading.Thread(target=worker, args=(i, queue, visited_urls, visited_lock, self.folder_path, self.domain))
            thread.daemon = True  # Allows main process to exit even if workers are alive
            thread.start()
            threads.append(thread)

        # 1. Wait for all work in the queue to be processed.
        queue.join()

        # 2. Send a "poison pill" (None) to each worker to tell them to exit.
        for _ in range(self.num_workers):
            queue.put(None)

        # 3. Now, join the threads to wait for them to shut down cleanly.
        for t in threads:
            t.join()

        print("\nAll pages have been processed. Crawler finished.")


def extract_links(html_content) -> set:
    soup = BeautifulSoup(html_content, 'html.parser')
    links = soup.find_all('a', href=True)
    return {link.get('href') for link in links}

def download_page(url, content, folder_path, worker_id):
    filename = urlparse(url).path.strip('/').replace('/', '_') or 'index'
    filename += '.html'

    print(f"[Worker-{worker_id}] Downloading: {url}")
    save_page(file_path=os.path.join(folder_path, filename), content=content)

def fetch_page(url, worker_id):
    try:
        # Set a browser-like User-Agent and increase the timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # Increased timeout to 30 seconds
        print(f"[Worker-{worker_id}] fetching: {url}")
        response = requests.get(url, headers=headers, timeout=30, allow_redirects=False)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"[Worker-{worker_id}] Error - Couldn't fetch {url}: {e}")
    return None