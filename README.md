# Books to Scrape - Web Scraper

A Python web scraper that extracts all book listings from [Books to Scrape](https://books.toscrape.com) and exports them to a clean, formatted Excel file.

## Features

- Scrapes **all 1000 books** across all 50 categories
- Extracts: Title, Price, Availability, Star Rating (1-5), Category, URL
- Removes duplicates automatically
- Outputs a formatted `.xlsx` file sorted by category
- Includes filters, alternating row colors, and frozen headers

## Setup

```bash
pip install -r requirements.txt
```

## Usage

```bash
python scraper.py
```

This generates `books.xlsx` in the project directory.

## Output Columns

| Column       | Description                        |
|--------------|------------------------------------|
| Title        | Full book title                    |
| Price        | Price in GBP (£)                   |
| Availability | "In Stock" or "Out of Stock"       |
| Star Rating  | 1–5 numeric rating                 |
| Category     | Book genre/category                |
| URL          | Direct link to the book page       |

## Tech Stack

- **requests** — HTTP requests
- **BeautifulSoup4** — HTML parsing
- **openpyxl** — Excel file generation
- **lxml** — Fast HTML parser backend
