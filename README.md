<br/>
<p align="center">
  <a href="https://github.com/m0hs1ne/WebWorm">
    <img src="https://i.ibb.co/M9pxvcJ/Screenshot-from-2023-11-20-14-13-15.png" alt="Logo">
  </a>

  <h3 align="center">"WebWorm – Dig Deep, Download Easy!"</h3>

  <p align="center">
    Web scraping tool designed to effortlessly navigate websites and automatically download all types of files.
    <br/>
    <br/>
  </p>
</p>



## Table Of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
    * [Creating A Pull Request](#creating-a-pull-request)
* [Authors](#authors)

## About The Project

![Screen Shot](https://i.ibb.co/QpF8Jdp/Screenshot-from-2023-11-20-14-11-06.png)

`WebWorm` is a python script that scrapes and downloads files from a specified website URL. It allows configuring the depth of website crawling and the file extensions to scrape. It also has an option to detect technologies used by the website.

## Getting Started

This is an example of how you may run the script.

### Prerequisites

- Ensure you have Python installed on your system.

### Installation

1. Clone the repository:
```sh
git clone https://github.com/m0hs1ne/WebWorm.git
```

2. Install the required packages:
```sh
pip install -r requirements.txt
```

3. Run the script:
```sh
python3 webworm.py -u <url> -d <depth> -e <extensions> -t <technologies>
```

## Usage

```sh
usage: WebWorm.py [-h] [-e EXTENSIONS] [-d DEPTH] [-t] url

positional arguments:
  url                   The URL of the website to scrape.

options:
  -h, --help            show this help message and exit
  -e EXTENSIONS, --extensions EXTENSIONS
                        Comma-separated list of file extensions to scrape (e.g., "jpg,png,docx"). If not specified, all files will be scraped.
  -d DEPTH, --depth DEPTH
                        The maximum depth to crawl the website. Default is 1.
  -t, --tech            Detect technologies used on the website.
```
using the `-t` flag will detect technologies used by the website.

![-t](https://i.ibb.co/QK1hYtR/Screenshot-from-2023-11-20-16-02-33.png)

## Roadmap

- [ ] Add support for scraping multiple websites.
- [ ] Request with session cookies.
- [ ] enumerate directories.
- [ ] check for possible keys and secrets in js files.

## Contributing

Your contributions are welcome! Whether you're fixing bugs, adding new features, or improving documentation, we appreciate your help in making WebWorm better.

### Creating A Pull Request

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request


## Authors
- [m0hs1ne](https://github.com/m0hs1ne) - Initial work

