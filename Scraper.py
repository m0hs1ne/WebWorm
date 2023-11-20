import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


class WebScraper:
    def __init__(self, url, depth, extensions=None):
        self.url = url
        self.depth = depth
        self.extensions = extensions if extensions else []
        self.visited_urls = set()
        self.downloaded_files = set()

    def is_valid_url(self, url):
        return (
            urlparse(url).netloc == urlparse(self.url).netloc
            and url not in self.visited_urls
        )

    def get_page_content(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.HTTPError as e:
            print(f"{RED}HTTP error occurred: {e}{RESET}")
            return None

    def download_files(self, urls, download_dir="results"):
        download_dir = os.path.join(download_dir, urlparse(self.url).netloc)
        os.makedirs(download_dir, exist_ok=True)

        for url in urls:
            filename = os.path.basename(urlparse(url).path)
            file_path = os.path.join(download_dir, filename)
            try:
                with requests.get(url, stream=True) as response:
                    response.raise_for_status()
                    with open(file_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)
                        print(f"{GREEN}Downloaded file: {url}{RESET}")
            except requests.exceptions.HTTPError as e:
                print(f"{RED}HTTP error occurred: {e}{RESET}")

    def extract_files(self, soup, url):
        links_attributes = ["href", "src"]
        for tag in soup.find_all(True, href=True) + soup.find_all(True, src=True):
            for attribute in links_attributes:
                if tag.has_attr(attribute):
                    link = tag[attribute]
                    parsed_link = urlparse(link)
                    if "." in os.path.basename(parsed_link.path):
                        if not self.extensions or any(
                            [link.endswith(ext) for ext in self.extensions]
                        ):
                            file_url = urljoin(url, link)
                            if file_url not in self.downloaded_files:
                                self.downloaded_files.add(file_url)

    def crawl_to_links(self, soup, url, current_depth):
        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            if self.is_valid_url(link):
                self.scrape_page(link, current_depth + 1)

    def scrape_page(self, url, current_depth):
        if current_depth > self.depth or not self.is_valid_url(url):
            return
        self.visited_urls.add(url)
        content = self.get_page_content(url)
        if content is None:
            return

        soup = BeautifulSoup(content, "html.parser")
        self.extract_files(soup, url)
        self.crawl_to_links(soup, url, current_depth)

    def start_scraping(self):
        self.scrape_page(self.url, current_depth=1)
        if len(self.downloaded_files) > 0:
            print(f"{YELLOW}Discovered {len(self.downloaded_files)} files.{RESET}")
            userRes = input("Do you want to download them? (y/n): ").strip().lower()
            if userRes == "y":
                self.download_files(self.downloaded_files)
            else:
                print(f"{RED}Download aborted.{RESET}")
        else:
            print(f"{YELLOW}No files found.{RESET}")
