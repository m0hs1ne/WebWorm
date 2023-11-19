import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def print_banner():
    banner = f"""
{YELLOW}┌──────────────────────────────────────────────────────────────┐
│ █     █░▓█████  ▄▄▄▄    █     █░ ▒█████   ██▀███   ███▄ ▄███▓│
│▓█░ █ ░█░▓█   ▀ ▓█████▄ ▓█░ █ ░█░▒██▒  ██▒▓██ ▒ ██▒▓██▒▀█▀ ██▒│
│▒█░ █ ░█ ▒███   ▒██▒ ▄██▒█░ █ ░█ ▒██░  ██▒▓██ ░▄█ ▒▓██    ▓██░│
│░█░ █ ░█ ▒▓█  ▄ ▒██░█▀  ░█░ █ ░█ ▒██   ██░▒██▀▀█▄  ▒██    ▒██ │
│░░██▒██▓ ░▒████▒░▓█  ▀█▓░░██▒██▓ ░ ████▓▒░░██▓ ▒██▒▒██▒   ░██▒│
│░ ▓░▒ ▒  ░░ ▒░ ░░▒▓███▀▒░ ▓░▒ ▒  ░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░ ▒░   ░  ░│
│  ▒ ░ ░   ░ ░  ░▒░▒   ░   ▒ ░ ░    ░ ▒ ▒░   ░▒ ░ ▒░░  ░      ░│
│  ░   ░     ░    ░    ░   ░   ░  ░ ░ ░ ▒    ░░   ░ ░      ░   │
│    ░       ░  ░ ░          ░        ░ ░     ░            ░   │
│                      ░                                       │
└──────────────────────────────────────────────────────────────┘{RESET}
    """
    print(banner)


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
        help=f"{YELLOW}The URL of the website to scrape.{RESET}",
    )

    args = parser.parse_args()

    if not args.url.startswith("http"):
        print(f"{RED}Error: URL must start with 'http' or 'https'.{RESET}")
        exit(1)
    else:
        print(f"{GREEN}Scraping URL: {args.url}{RESET}")
    
    if args.depth < 1:
        print(f"{RED}Error: Depth must be greater than 0.{RESET}")
        exit(1)

    extensions = []
    if args.extensions:
        extensions = [
            "." + ext if not ext.startswith(".") else ext
            for ext in args.extensions.split(",")
        ]

    if extensions:
        print(
            f"{GREEN}Scraping for files with extensions: {', '.join(extensions)}{RESET}"
        )
    else:
        print(f"{GREEN}Scraping for all files.{RESET}")

    print(f"{GREEN}Maximum crawl depth: {args.depth}{RESET}")


if __name__ == "__main__":
    main()
