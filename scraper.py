import argparse
import logging

from session import ScraperSession, CaptchaDetectedError, RateLimitError
from parser import get_categories, scrape_category
from exporter import save_to_excel
from progress import save_progress, load_progress, clear_progress

log = logging.getLogger()
log.setLevel(logging.INFO)

_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

_console = logging.StreamHandler()
_console.setFormatter(_fmt)
log.addHandler(_console)

_file = logging.FileHandler("scraper.log", encoding="utf-8")
_file.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
log.addHandler(_file)


def remove_duplicates(books):
    seen = set()
    unique = []
    for book in books:
        if book["URL"] not in seen:
            seen.add(book["URL"])
            unique.append(book)
    return unique


def main():
    parser = argparse.ArgumentParser(description="Books to Scrape — Web Scraper")
    parser.add_argument("--proxy", help="Proxy URL (e.g. http://user:pass@host:port)")
    parser.add_argument("--min-delay", type=float, default=1.0, help="Min delay between requests in seconds (default: 1.0)")
    parser.add_argument("--max-delay", type=float, default=3.0, help="Max delay between requests in seconds (default: 3.0)")
    parser.add_argument("--output", default="books.xlsx", help="Output Excel filename (default: books.xlsx)")
    parser.add_argument("--resume", action="store_true", help="Resume from last checkpoint if interrupted")
    parser.add_argument("--fresh", action="store_true", help="Ignore checkpoint and start fresh")
    args = parser.parse_args()

    print("=" * 60)
    print("Books to Scrape - Web Scraper")
    print("  Rate-limit & CAPTCHA resilient")
    print("=" * 60)

    scraper = ScraperSession(
        proxy=args.proxy,
        min_delay=args.min_delay,
        max_delay=args.max_delay,
    )

    all_books = []
    completed_categories = []

    if args.resume and not args.fresh:
        all_books, completed_categories = load_progress()

    if args.fresh:
        clear_progress()

    log.info("Fetching categories...")
    categories = get_categories(scraper)
    log.info(f"Found {len(categories)} categories")

    remaining = [(n, u) for n, u in categories if n not in completed_categories]
    if completed_categories:
        log.info(f"Skipping {len(completed_categories)} already-scraped categories")

    for i, (name, url) in enumerate(remaining, len(completed_categories) + 1):
        log.info(f"[{i}/{len(categories)}] Scraping: {name} — {len(all_books)} books so far")
        try:
            books = scrape_category(scraper, name, url)
            all_books.extend(books)
            completed_categories.append(name)
            save_progress(all_books, completed_categories)
        except CaptchaDetectedError as e:
            log.error(str(e))
            log.error("Progress has been saved. Re-run with --resume to continue.")
            log.error("Tip: try a different --proxy or increase --min-delay / --max-delay")
            save_progress(all_books, completed_categories)
            return
        except RateLimitError as e:
            log.error(str(e))
            log.error("Progress has been saved. Re-run with --resume to continue.")
            save_progress(all_books, completed_categories)
            return

    log.info(f"Total books scraped: {len(all_books)}")

    all_books = remove_duplicates(all_books)
    log.info(f"After deduplication: {len(all_books)}")

    all_books.sort(key=lambda b: (b["Category"].lower(), b["Title"].lower()))

    save_to_excel(all_books, args.output)
    clear_progress()

    stats = scraper.stats()
    print("\n" + "=" * 60)
    print("  STATS")
    print(f"  Total requests:    {stats['requests']}")
    print(f"  Rate limits hit:   {stats['rate_limits_hit']}")
    print(f"  CAPTCHAs hit:      {stats['captchas_hit']}")
    print("=" * 60)
    print("Done!")


if __name__ == "__main__":
    main()
