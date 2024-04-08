import os
from crawler import Crawler


def main():
    entry_point =  input("Enter the website URL: ")
    local_folder = input("Enter the folder path to save pages: ")

    if not os.path.exists(local_folder):
        os.makedirs(local_folder)


    crawler = Crawler(entry_point, local_folder)
    crawler.start_crawl()


if __name__ == "__main__":
    main()