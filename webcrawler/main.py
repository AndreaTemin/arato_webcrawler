import os
from crawler import Crawler
import time

NUMBER_OF_THREADS = 16

def main():
    entry_point =  input("Enter the website URL: ")
    local_folder = input("Enter the folder path to save pages: ")

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)

    # The Crawler class now manages its own worker processes.
    crawler = Crawler(
        entry_url=entry_point,
        folder_path=local_folder,
        num_workers=NUMBER_OF_THREADS
    )
    crawler.start()

if __name__ == "__main__":
    start = time.time()
    main()
    execution_time = time.time() - start
    print(f"{execution_time = }")