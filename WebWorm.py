import argparse
from Scraper import WebScraper
from TechDetector import detect_tech
import logging

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='webworm.log'
)
logger = logging.getLogger("WebWorm")


def print_banner():
    # Use raw string to fix invalid escape sequence
    banner = fr"""
{YELLOW}__        __   _  __        __                   
\ \      / /__| |_\ \      / /__  _ __ _ __ ___  
 \ \ /\ / / _ \ '_ \ \ /\ / / _ \| '__| '_ ` _ \ 
  \ V  V /  __/ |_) \ V  V / (_) | |  | | | | | |
   \_/\_/ \___|_.__/ \_/\_/ \___/|_|  |_| |_| |_|{RESET}
    """
    print(banner)


def format_size(size_bytes: int) -> str:
    """Format bytes to human-readable size"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024**2:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024**3:
        return f"{size_bytes/1024**2:.1f} MB"
    else:
        return f"{size_bytes/1024**3:.1f} GB"


def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description=f"{GREEN}WebWorm: A tool to scrape and download files from a website.{RESET}"
    )

    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        help=f'{YELLOW}Comma-separated list of file extensions to scrape (e.g., "jpg,png,docx"). If not specified, all files will be scraped.{RESET}',
    )
    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1,
        help=f"{YELLOW}The maximum depth to crawl the website. Default is 1.{RESET}",
    )
    parser.add_argument(
        "url",
        type=str,
        nargs="?",  # Make URL optional
        help=f"{YELLOW}The URL of the website to scrape.{RESET}",
    )
    parser.add_argument(
        "-t",
        "--tech",
        action="store_true",
        help=f"{YELLOW}Detect technologies used on the website.{RESET}",
    )
    
    # New arguments
    parser.add_argument(
        "--threads",
        type=int,
        default=10,
        help=f"{YELLOW}Number of threads to use for crawling and downloading (default: 10).{RESET}"
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default="WebWorm/1.0",
        help=f"{YELLOW}Custom User-Agent string (default: WebWorm/1.0).{RESET}"
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help=f"{YELLOW}Ignore robots.txt restrictions (not recommended).{RESET}"
    )
    parser.add_argument(
        "--max-file-size",
        type=str,
        help=f"{YELLOW}Maximum file size to download (e.g. '10MB', '1GB').{RESET}"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results",
        help=f"{YELLOW}Directory to save downloaded files (default: results).{RESET}"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help=f"{YELLOW}Enable verbose logging.{RESET}"
    )
    parser.add_argument(
        "-u", 
        "--urls-file",
        type=str,
        help=f"{YELLOW}Path to a file containing URLs to scrape (one per line).{RESET}"
    )
    # Add new arguments for cookie handling
    parser.add_argument(
        "--cookies",
        type=str,
        help=f"{YELLOW}Cookies to use in format 'name1=value1; name2=value2'{RESET}"
    )
    parser.add_argument(
        "--cookies-file",
        type=str,
        help=f"{YELLOW}Path to a Netscape-format cookies file (as exported from browser){RESET}"
    )

    # Add these arguments
    parser.add_argument(
        "--enumerate-dirs",
        action="store_true",
        help=f"{YELLOW}Attempt to discover common directories.{RESET}"
    )

    args = parser.parse_args()

    # Set log level based on verbose flag
    if args.verbose:
        for handler in logging.root.handlers:
            handler.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
        logger.debug("Verbose mode enabled")

    # URL validation
    if not args.urls_file and not args.url.startswith("http"):
        print(f"{RED}Error: URL must start with 'http' or 'https'.{RESET}")
        logger.error(f"Invalid URL format: {args.url}")
        exit(1)

    # Technology detection
    if args.tech:
        logger.info(f"Detecting technologies on {args.url}")
        techs = detect_tech(args.url)
        print(f"{BLUE}{techs}{RESET}")
        exit(0)

    # Depth validation
    if args.depth < 1:
        print(f"{RED}Error: Depth must be greater than 0.{RESET}")
        logger.error(f"Invalid depth: {args.depth}")
        exit(1)

    # Parse file extensions
    extensions = []
    if args.extensions:
        extensions = [
            "." + ext if not ext.startswith(".") else ext
            for ext in args.extensions.split(",")
        ]

    # Parse max file size
    max_file_size = None
    if args.max_file_size:
        size = args.max_file_size.upper()
        if size.endswith("KB"):
            max_file_size = int(float(size[:-2]) * 1024)
        elif size.endswith("MB"):
            max_file_size = int(float(size[:-2]) * 1024 * 1024)
        elif size.endswith("GB"):
            max_file_size = int(float(size[:-2]) * 1024 * 1024 * 1024)
        elif size.endswith("B"):
            max_file_size = int(size[:-1])
        else:
            try:
                max_file_size = int(size)
            except ValueError:
                print(f"{RED}Error: Invalid file size format. Use 10MB, 1GB, etc.{RESET}")
                logger.error(f"Invalid file size format: {args.max_file_size}")
                exit(1)
        print(f"{GREEN}Max file size: {format_size(max_file_size)}{RESET}")

    # Log configuration
    if extensions:
        print(f"{GREEN}Scraping for files with extensions: {', '.join(extensions)}{RESET}")
        logger.info(f"Scraping for file extensions: {extensions}")
    else:
        print(f"{GREEN}Scraping for all files.{RESET}")
        logger.info("Scraping for all files")
    
    print(f"{GREEN}Maximum crawl depth: {args.depth}{RESET}")
    print(f"{GREEN}Using {args.threads} threads{RESET}")
    print(f"{GREEN}User-Agent: {args.user_agent}{RESET}")
    print(f"{GREEN}Respecting robots.txt: {not args.ignore_robots}{RESET}")
    
    logger.info(f"Starting scrape with depth={args.depth}, threads={args.threads}")

    # Handle multiple URLs
    urls_to_scrape = []
    if args.urls_file:
        try:
            with open(args.urls_file, 'r') as f:
                urls_to_scrape = [line.strip() for line in f if line.strip() and line.strip().startswith('http')]
            if not urls_to_scrape:
                print(f"{RED}No valid URLs found in the file.{RESET}")
                exit(1)
            print(f"{GREEN}Loaded {len(urls_to_scrape)} URLs to scrape{RESET}")
        except Exception as e:
            print(f"{RED}Error reading URLs file: {e}{RESET}")
            exit(1)
    else:
        urls_to_scrape = [args.url]

    # Process each URL with error handling
    for url in urls_to_scrape:
        try:
            print(f"\n{GREEN}Processing URL: {url}{RESET}")
            # Create and start the scraper for this URL
            scraper = WebScraper(
                url, 
                args.depth, 
                extensions,
                max_threads=args.threads,
                user_agent=args.user_agent,
                respect_robots_txt=not args.ignore_robots,
                max_file_size=max_file_size,
                cookies=args.cookies,
                cookies_file=args.cookies_file,
                output_dir=args.output_dir
            )
            
            # Set additional flags for new features
            scraper.enumerate_dirs = args.enumerate_dirs if 'enumerate_dirs' in args else False
            
            scraper.start_scraping()
            
        except KeyboardInterrupt:
            print(f"{RED}Crawling interrupted. Moving to next URL.{RESET}")
            continue
        except Exception as e:
            print(f"{RED}Error processing {url}: {e}{RESET}")
            logger.error(f"Error processing {url}: {e}")
            continue


if __name__ == "__main__":
    main()
