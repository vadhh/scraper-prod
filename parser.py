import logging
from urllib.parse import urljoin

from config import BASE_URL, CATALOGUE_URL, RATING_MAP

log = logging.getLogger(__name__)


def get_categories(scraper):
    soup = scraper.get(BASE_URL)
    sidebar = soup.find("ul", class_="nav-list")
    category_links = sidebar.find("ul").find_all("a")
    categories = []
    for link in category_links:
        name = link.text.strip()
        href = urljoin(BASE_URL, link["href"])
        categories.append((name, href))
    return categories


def parse_books_from_page(soup, category_name):
    books = []
    articles = soup.find_all("article", class_="product_pod")
    for article in articles:
        title_tag = article.find("h3").find("a")
        title = title_tag["title"]

        url = urljoin(CATALOGUE_URL, title_tag["href"])

        price_text = article.find("p", class_="price_color").text.strip()
        price = float(price_text.replace("£", "").replace("Â", ""))

        availability_tag = article.find("p", class_="instock")
        availability = "In Stock" if availability_tag else "Out of Stock"

        rating_tag = article.find("p", class_="star-rating")
        rating_class = [c for c in rating_tag["class"] if c != "star-rating"][0]
        star_rating = RATING_MAP.get(rating_class, 0)

        books.append({
            "Title": title,
            "Price": price,
            "Availability": availability,
            "Star Rating": star_rating,
            "Category": category_name,
            "URL": url,
        })
    return books


def scrape_category(scraper, name, url):
    books = []
    page_url = url
    page_num = 1

    while page_url:
        soup = scraper.get(page_url)
        if soup is None:
            log.warning(f"  Page {page_num}: failed to fetch, skipping rest of category")
            break
        page_books = parse_books_from_page(soup, name)
        books.extend(page_books)
        log.info(f"  Page {page_num}: {len(page_books)} books")

        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_href = next_btn.find("a")["href"]
            page_url = urljoin(page_url, next_href)
            page_num += 1
        else:
            page_url = None

    return books
