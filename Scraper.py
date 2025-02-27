import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException
import os
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import List, Set, Optional
from urllib.robotparser import RobotFileParser
from tqdm import tqdm
import http.cookiejar
from itertools import product

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='webworm.log'
)
logger = logging.getLogger("WebScraper")


class WebScraper:
    def __init__(
        self, 
        url: str, 
        depth: int, 
        extensions: Optional[List[str]] = None,
        max_threads: int = 10,
        user_agent: str = "WebWorm/1.0",
        respect_robots_txt: bool = True,
        max_file_size: Optional[int] = None,
        cookies: Optional[str] = None,
        cookies_file: Optional[str] = None,
        output_dir: str = "results"
    ):
        self.url = url
        self.depth = depth
        self.extensions = extensions if extensions else []
        self.visited_urls: Set[str] = set()
        self.downloaded_files: Set[str] = set()
        self.max_threads = max_threads
        self.user_agent = user_agent
        self.respect_robots_txt = respect_robots_txt
        self.max_file_size = max_file_size  # in bytes
        self.robots_parser = RobotFileParser()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})
        self.output_dir = output_dir
        
        # Initialize robots.txt parser if needed
        if self.respect_robots_txt:
            self._setup_robots_txt()
        
        # Setup session with cookies if provided
        if cookies:
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    self.session.cookies.set(name, value)
                    logger.debug(f"Added cookie: {name}={value}")
        
        if cookies_file:
            try:
                cookie_jar = http.cookiejar.MozillaCookieJar(cookies_file)
                cookie_jar.load()
                self.session.cookies.update(cookie_jar)
                logger.info(f"Loaded cookies from {cookies_file}")
            except Exception as e:
                logger.warning(f"Failed to load cookies from file: {e}")
    
    def _setup_robots_txt(self) -> None:
        """Set up and fetch robots.txt if respect_robots_txt is enabled."""
        try:
            robots_url = urljoin(self.url, "/robots.txt")
            self.robots_parser.set_url(robots_url)
            self.robots_parser.read()
            logger.info(f"Loaded robots.txt from {robots_url}")
        except Exception as e:
            logger.warning(f"Failed to load robots.txt: {e}")
            # If we can't load robots.txt, we'll assume it doesn't exist
            pass

    def is_allowed_by_robots(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots_txt:
            return True
        
        return self.robots_parser.can_fetch(self.user_agent, url)

    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and should be visited."""
        return (
            urlparse(url).netloc == urlparse(self.url).netloc
            and url not in self.visited_urls
            and self.is_allowed_by_robots(url)
        )

    def get_page_content(self, url: str) -> Optional[bytes]:
        """Fetch the content of a URL."""
        try:
            logger.debug(f"Fetching {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.content
        except HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            print(f"{RED}HTTP error occurred: {e}{RESET}")
        except ConnectionError:
            logger.error(f"Connection error occurred: can't connect to {url}")
            print(f"{RED}Connection error occurred: can't connect to {url}{RESET}")
        except Timeout:
            logger.error(f"Timeout error occurred when connecting to {url}")
            print(f"{RED}Timeout error occurred when connecting to {url}{RESET}")
        except RequestException as e:
            logger.error(f"Unexpected error occurred: {e}")
            print(f"{RED}Unexpected error occurred: {e}{RESET}")
        return None

    def download_files(self, urls: Set[str], download_dir: str = "results") -> None:
        """Download files in parallel using ThreadPoolExecutor."""
        download_dir = os.path.join(download_dir, urlparse(self.url).netloc)
        os.makedirs(download_dir, exist_ok=True)

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(self._download_file, url, download_dir))
            
            with tqdm(total=len(futures), desc="Downloading files") as pbar:
                for _ in [future.result() for future in futures]:
                    pbar.update(1)

    def _download_file(self, url: str, download_dir: str) -> bool:
        """Download a single file."""
        filename = os.path.basename(urlparse(url).path)
        file_path = os.path.join(download_dir, filename)
        try:
            # Stream the file to check its size first
            with self.session.get(url, stream=True) as response:
                response.raise_for_status()
                
                # Check file size if max_file_size is set
                if self.max_file_size:
                    content_length = response.headers.get('Content-Length')
                    if content_length and int(content_length) > self.max_file_size:
                        logger.warning(f"File {url} exceeds maximum file size ({self.max_file_size} bytes)")
                        print(f"{YELLOW}Skipped {url}: exceeds maximum file size{RESET}")
                        return False
                
                # Download the file
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                logger.info(f"Downloaded file: {url}")
                print(f"{GREEN}Downloaded file: {url}{RESET}")
                return True
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error when downloading {url}: {e}")
            print(f"{RED}HTTP error occurred when downloading {url}: {e}{RESET}")
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            print(f"{RED}Error downloading {url}: {e}{RESET}")
        return False

    def extract_files(self, soup: BeautifulSoup, url: str) -> None:
        """Extract file URLs from a page."""
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

    def scrape_page(self, url: str, current_depth: int) -> None:
        """Scrape a single page recursively."""
        if current_depth > self.depth or not self.is_valid_url(url):
            return
        
        logger.info(f"Scraping {url} at depth {current_depth}")
        self.visited_urls.add(url)
        content = self.get_page_content(url)
        if content is None:
            return

        # Check content type before parsing to avoid errors with binary files
        try:
            # Try to detect if this is a binary file or text content
            is_binary = False
            # Check the first few bytes for null bytes or other binary indicators
            sample = content[:1000]
            if b'\x00' in sample:
                is_binary = True
            
            # Or use content-type from headers if available
            if hasattr(content, 'headers') and 'content-type' in content.headers:
                content_type = content.headers['content-type'].lower()
                if 'text/html' not in content_type and 'application/json' not in content_type:
                    is_binary = True
            
            if is_binary:
                logger.debug(f"Skipping binary content at {url}")
                return
                
            soup = BeautifulSoup(content, "html.parser")
            self.extract_files(soup, url)
            
        except Exception as e:
            logger.error(f"Error parsing content from {url}: {e}")
            print(f"{RED}Error parsing content from {url}: {e}{RESET}")
            return
        
        if current_depth < self.depth:
            # Collect links for the next depth level
            links_to_crawl = []
            try:
                for tag in soup.find_all("a", href=True):
                    link = urljoin(url, tag["href"])
                    if self.is_valid_url(link):
                        links_to_crawl.append((link, current_depth + 1))
                
                # Process links in parallel with a limit to prevent too many threads
                max_links = 100  # Limit to prevent too many threads
                if len(links_to_crawl) > max_links:
                    print(f"{YELLOW}Too many links found ({len(links_to_crawl)}). Limiting to {max_links}.{RESET}")
                    links_to_crawl = links_to_crawl[:max_links]
                    
                # Process in batches to prevent excessive thread creation
                batch_size = 10
                for i in range(0, len(links_to_crawl), batch_size):
                    batch = links_to_crawl[i:i+batch_size]
                    with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
                        futures = []
                        for link_args in batch:
                            futures.append(executor.submit(self.scrape_page, *link_args))
                        
                        # Wait for all futures to complete
                        for future in futures:
                            try:
                                future.result()
                            except Exception as e:
                                logger.error(f"Error in thread: {e}")
                                
            except Exception as e:
                logger.error(f"Error processing links from {url}: {e}")
                print(f"{RED}Error processing links from {url}: {e}{RESET}")

    def start_scraping(self) -> None:
        """Start the scraping process."""
        print(f"{GREEN}Starting to scrape {self.url} with depth {self.depth}{RESET}")
        logger.info(f"Starting to scrape {self.url} with depth {self.depth}")
        
        # Enumerate directories if requested
        if hasattr(self, 'enumerate_dirs') and self.enumerate_dirs:
            discovered_dirs = self.enumerate_directories(self.url)
            # Add discovered directories to the scraping queue
            for dir_url in discovered_dirs:
                if dir_url not in self.visited_urls:
                    self.scrape_page(dir_url, current_depth=1)
        
        # Start the main crawling process
        self.scrape_page(self.url, current_depth=1)
        
        if len(self.downloaded_files) > 0:
            print(f"{YELLOW}Discovered {len(self.downloaded_files)} files.{RESET}")
            for file in self.downloaded_files:
                print(f"  - {file}")
            
            userRes = input("Do you want to download them? (y/n): ").strip().lower()
            if userRes == "y":
                self.download_files(self.downloaded_files, self.output_dir)
            else:
                print(f"{RED}Download aborted.{RESET}")
                logger.info("Download aborted by user")
        else:
            print(f"{YELLOW}No files found.{RESET}")
            logger.info("No files found")
        
        print(f"{GREEN}Crawling complete: Visited {len(self.visited_urls)} pages{RESET}")
        logger.info(f"Crawling complete: Visited {len(self.visited_urls)} pages")

    def enumerate_directories(self, base_url: str) -> List[str]:
        """Attempt to enumerate directories by common patterns."""
        logger.info(f"Starting directory enumeration for {base_url}")
        print(f"{YELLOW}Enumerating directories for {base_url}...{RESET}")
        
        # Common directory names to try
        common_dirs = [
            "admin", "backup", "backups", "data", "db", "debug", "files", 
            "images", "img", "js", "css", "static", "upload", "uploads",
            "private", "secrets", "api", "v1", "v2", "docs", "documentation"
        ]
        
        # Common file patterns that might exist
        common_files = [
            "index.html", "index.php", "config.php", "config.js", ".env",
            "README.md", "robots.txt", "sitemap.xml", ".git/HEAD"
        ]
        
        discovered_urls = []
        base_path = urlparse(base_url).path
        base_domain = f"{urlparse(base_url).scheme}://{urlparse(base_url).netloc}"
        
        # If base path doesn't end with /, add it for directory tests
        if not base_path.endswith('/'):
            base_path = base_path + '/'
        
        # Try common directories
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = []
            
            # Try directories
            for directory in common_dirs:
                test_url = urljoin(base_domain, base_path + directory + "/")
                futures.append(executor.submit(self._test_url_exists, test_url))
            
            # Try files
            for file in common_files:
                test_url = urljoin(base_domain, base_path + file)
                futures.append(executor.submit(self._test_url_exists, test_url))
            
            for future in futures:
                result = future.result()
                if result:
                    discovered_urls.append(result)
                    
        if discovered_urls:
            print(f"{GREEN}Discovered {len(discovered_urls)} directories/files:{RESET}")
            for url in discovered_urls:
                print(f"  - {url}")
        else:
            print(f"{YELLOW}No additional directories discovered.{RESET}")
            
        return discovered_urls

    def _test_url_exists(self, url: str) -> Optional[str]:
        """Test if a URL exists by sending a HEAD request."""
        try:
            resp = self.session.head(url, timeout=5, allow_redirects=True)
            if resp.status_code == 200:
                logger.info(f"Found directory/file: {url}")
                return url
        except Exception:
            pass
        return None
