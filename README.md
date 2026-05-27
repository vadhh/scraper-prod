# Books to Scrape - Web Scraper

A Python web scraper that extracts all book listings from [Books to Scrape](https://books.toscrape.com) and exports them to a clean, formatted Excel file. Built with rate-limit and CAPTCHA resilience.

## Features

- Scrapes **all 1000 books** across all 50 categories
- Extracts: Title, Price, Availability, Star Rating (1-5), Category, URL
- Removes duplicates automatically
- Outputs a formatted `.xlsx` file sorted by category
- **Rate-limit handling** — exponential backoff with jitter on 429/503 responses
- **CAPTCHA detection** — detects Cloudflare, reCAPTCHA, hCaptcha challenges and retries with rotated identity
- **User-Agent rotation** — randomizes browser fingerprint per request
- **Proxy support** — route traffic through a proxy to avoid IP bans
- **Checkpoint/resume** — saves progress after each category; resume interrupted scrapes with `--resume`
- Configurable request delays to stay under radar

## Project Structure

```
├── scraper.py      # CLI entrypoint
├── config.py       # Constants, user agents, CAPTCHA signatures
├── session.py      # HTTP session with retry, rate-limit & CAPTCHA handling
├── parser.py       # HTML parsing and category/book extraction
├── exporter.py     # Excel file generation
├── progress.py     # Checkpoint save/load for resumable scraping
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
```

## Usage

**Basic run:**
```bash
python scraper.py
```

**With proxy:**
```bash
python scraper.py --proxy http://user:pass@host:port
```

**Custom delays (slower to avoid detection):**
```bash
python scraper.py --min-delay 2.0 --max-delay 5.0
```

**Resume after interruption:**
```bash
python scraper.py --resume
```

**Fresh start (ignore checkpoint):**
```bash
python scraper.py --fresh
```

**Custom output file:**
```bash
python scraper.py --output my_books.xlsx
```

## How It Handles Anti-Scraping

| Defense | Strategy |
|---|---|
| **Rate limiting (429)** | Exponential backoff respecting `Retry-After` header |
| **Service unavailable (503)** | Exponential backoff with jitter |
| **CAPTCHA / Cloudflare** | Detection via page signatures, UA rotation, extended cooldown, proxy fallback |
| **IP blocking** | Proxy support (`--proxy`), configurable delays |
| **Browser fingerprinting** | Rotating realistic User-Agent strings + full browser headers |
| **Connection errors** | Automatic retry with backoff (up to 5 attempts) |
| **Interrupted scrape** | Checkpoint file saves progress per category; `--resume` to continue |

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

- **requests** — HTTP requests with session management
- **BeautifulSoup4** — HTML parsing
- **openpyxl** — Excel file generation
- **lxml** — Fast HTML parser backend
