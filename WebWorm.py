import argparse


def main():
    parser = argparse.ArgumentParser(
        description="WebWorm: A tool to scrape and download files from a website."
    )

    parser.add_argument(
        "-e",
        "--extensions",
        type=str,
        help='Comma-separated list of file extensions to scrape (e.g., "jpg,png,docx"). If not specified, all files will be scraped.',
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


if __name__ == "__main__":
    main()
