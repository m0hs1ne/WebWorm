import requests
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, url, depth, extensions=None):
        self.url = url
        self.depth = depth
        self.extensions = extensions

    def start_scraping(self):
        pass