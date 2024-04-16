Simple Web Crawler

This is a Python script that allows you to download all pages of a website into a designated local folder. It uses the `requests` library to fetch web pages and the `BeautifulSoup` library to parse HTML content.

Features

- Downloads all pages of a website recursively.
- Saves pages in a designated local folder.
- Handles redirects and avoids revisiting already visited URLs.
- Allows setting a maximum depth for the crawl to prevent infinite loops.

Installations

1. Clone the repository:

   git clone https://github.com/AndreaTemin/arato_webcrawler.git

2. Install dependencies:
   
   pip install -r requirements.txt

Usage

1. Run the webcrawler script:

   python main.py

2. Enter the website URL when prompted.
3. Enter the folder path where you want to save the pages.

The script will start crawling the website, downloading pages recursively and saving them in the specified folder.

