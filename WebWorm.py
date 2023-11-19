import argparse


def main():
    parser = argparse.ArgumentParser(
        description="WebWorm: A tool to scrape and download files from a website."
    )

    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        help='Comma-separated list of file extensions to scrape (e.g., "jpg,png,docx"). '
        "If not specified, all files will be scraped.",
    )

    parser.add_argument(
        "-d",
        "--depth",
        type=int,
        default=1,
        help="The maximum depth to crawl the website. Default is 1.",
    )

    args = parser.parse_args()

    extensions = []
    if args.extensions:
        extensions = [
            "." + ext if not ext.startswith(".") else ext
            for ext in args.extensions.split(",")
        ]

    if extensions:
        print(f"Scraping for files with extensions: {', '.join(extensions)}")
    else:
        print("Scraping for all files.")

    print(f"Maximum crawl depth: {args.depth}")


if __name__ == "__main__":
    main()
