"""
Task 6 - Interactive Web Scraper
Cognifyz Technologies | Software Development Internship | Level 3: Advanced

books.toscrape.com se book data fetch karke user-friendly tarike se dikhata hai.
Yeh site scraping practice ke liye hi banayi gayi hai - iska robots.txt kisi
bhi page ko block nahi karta, isliye ise scrape karna allowed hai.

Features:
  - Catalogue page-by-page browse
  - Title keyword se search (kai pages par)
  - Max price / min rating filter
  - Result CSV mein export
  - 'probe' mode: page ka structure check karne ke liye

Zaroori libraries:  pip install requests beautifulsoup4
Python 3.6+
"""

import csv
import re
import sys
import time

# ---- libraries ko dhang se check karo, crash ke bajaye saaf message do ----

try:
    import requests
except ImportError:
    sys.exit("\n'requests' library nahi mili.\nInstall karo:  pip install requests beautifulsoup4\n")

try:
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("\n'beautifulsoup4' library nahi mili.\nInstall karo:  pip install requests beautifulsoup4\n")


# --------------------------------------------------------------- constants

BASE = "https://books.toscrape.com"
CATALOGUE = BASE + "/catalogue/page-{0}.html"

HEADERS = {
    "User-Agent": "CognifyzInternship-Task6/1.0 (educational scraper; python-requests)"
}

TIMEOUT = 20            # seconds - hamesha timeout do, warna program latak sakta hai
DELAY = 1.0             # do requests ke beech ka gap - server par bojh na pade
MAX_PAGES = 50          # site par total 50 pages hain

RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
PRICE_RE = re.compile(r"[£$€]\s*([0-9]+(?:\.[0-9]{1,2})?)")


# ------------------------------------------------------------------- model

class Book:
    """Ek scraped book ka blueprint."""

    def __init__(self, title, price=None, rating=None, availability="", url=""):
        self.title = title
        self.price = price              # float ya None
        self.rating = rating            # 1-5 ya None
        self.availability = availability
        self.url = url

    def in_stock(self):
        return "in stock" in self.availability.lower()

    def stars(self):
        if self.rating is None:
            return "?"
        return "*" * self.rating + "." * (5 - self.rating)

    def to_row(self):
        return {
            "title": self.title,
            "price": "" if self.price is None else "{0:.2f}".format(self.price),
            "rating": "" if self.rating is None else self.rating,
            "availability": self.availability,
            "url": self.url,
        }

    def __repr__(self):
        return "Book({0!r}, price={1}, rating={2})".format(
            self.title, self.price, self.rating)


class ScrapeError(Exception):
    """Network ya parsing ki problem, jise user ko samajh aane laayak batana hai."""


# ------------------------------------------------------------------ fetching

_last_request_at = [0.0]


def polite_wait():
    """Do requests ke beech kam se kam DELAY second ka gap rakhta hai."""
    gap = time.time() - _last_request_at[0]
    if gap < DELAY:
        time.sleep(DELAY - gap)
    _last_request_at[0] = time.time()


def fetch(url):
    """URL ka HTML laata hai. Har network problem ko ScrapeError mein badalta hai."""
    polite_wait()
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        raise ScrapeError("Server ne {0} second mein jawab nahi diya.".format(TIMEOUT))
    except requests.exceptions.ConnectionError:
        raise ScrapeError("Connect nahi ho paaya. Internet ya firewall check karo.")
    except requests.exceptions.RequestException as exc:
        raise ScrapeError("Request fail ho gayi: {0}".format(exc))

    if response.status_code == 404:
        raise ScrapeError("Page maujood nahi hai (404).")
    if response.status_code != 200:
        raise ScrapeError("Server ne status {0} bheja.".format(response.status_code))

    response.encoding = response.apparent_encoding or response.encoding
    return response.text


# ------------------------------------------------------------------ parsing

def parse_price(text):
    """Kisi bhi text se pehli currency value nikaalta hai. Na mile to None."""
    match = PRICE_RE.search(text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def parse_rating(container):
    """
    'star-rating Three' jaise class se rating nikaalta hai.
    Class ka naam badal jaaye to None, crash nahi.
    """
    for element in container.find_all(True):
        classes = element.get("class") or []
        lowered = [c.lower() for c in classes]
        if any("star" in c for c in lowered):
            for word, value in RATING_WORDS.items():
                if word in lowered:
                    return value
    return None


def parse_availability(container):
    text = " ".join(container.get_text(" ", strip=True).split())
    if "out of stock" in text.lower():
        return "Out of stock"
    if "in stock" in text.lower():
        return "In stock"
    return ""


def parse_books(html):
    """
    Ek catalogue page ke HTML se Book objects banata hai.

    Anchor se shuru karte hain (h3 > a[title]) kyunki wahi sabse stable hai -
    poora title uske 'title' attribute mein hota hai. Phir uske aas-paas
    ke container se price, rating aur stock nikaalte hain. Isse class-name
    badalne par bhi parser poora nahi tootta.
    """
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for heading in soup.find_all("h3"):
        anchor = heading.find("a")
        if anchor is None:
            continue

        title = anchor.get("title") or anchor.get_text(strip=True)
        if not title:
            continue

        container = heading.find_parent(["article", "li", "div"]) or heading.parent
        text = container.get_text(" ", strip=True)

        href = anchor.get("href", "")
        if href and not href.startswith("http"):
            href = BASE + "/catalogue/" + href.replace("../", "")

        books.append(Book(
            title=title,
            price=parse_price(text),
            rating=parse_rating(container),
            availability=parse_availability(container),
            url=href,
        ))

    return books


def scrape_page(page):
    return parse_books(fetch(CATALOGUE.format(page)))


# ------------------------------------------------------------------ display

def show_books(books, limit=None):
    if not books:
        print("\n  (koi book nahi mili)")
        return

    shown = books if limit is None else books[:limit]

    print("\n  {0:>3}  {1:48}  {2:>8}  {3:7}  {4}".format(
        "#", "TITLE", "PRICE", "RATING", "STOCK"))
    print("  " + "-" * 84)
    for index, book in enumerate(shown, start=1):
        title = book.title if len(book.title) <= 48 else book.title[:45] + "..."
        price = "-" if book.price is None else "{0:.2f}".format(book.price)
        print("  {0:>3}  {1:48}  {2:>8}  {3:7}  {4}".format(
            index, title, price, book.stars(), book.availability or "-"))

    priced = [b.price for b in books if b.price is not None]
    print("\n  {0} results".format(len(books)), end="")
    if priced:
        print(" | price {0:.2f} - {1:.2f} | average {2:.2f}".format(
            min(priced), max(priced), sum(priced) / len(priced)), end="")
    print()
    if limit is not None and len(books) > limit:
        print("  (upar sirf pehle {0} dikhaye)".format(limit))


# ------------------------------------------------------------ input helpers

def ask_int(prompt, low, high, default=None):
    while True:
        raw = input(prompt).strip()
        if not raw and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("  -> Sirf number likho.")
            continue
        if low <= value <= high:
            return value
        print("  -> {0} se {1} ke beech ka number chahiye.".format(low, high))


def ask_float(prompt, default=None):
    while True:
        raw = input(prompt).strip()
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 25.50")


def ask_text(prompt):
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        print("  -> Khaali nahi chalega.")


def ask_yes_no(prompt):
    while True:
        raw = input("{0} (y/n): ".format(prompt)).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  -> y ya n likho.")


# ------------------------------------------------------------------ actions

LAST_RESULTS = []


def remember(books):
    del LAST_RESULTS[:]
    LAST_RESULTS.extend(books)


def action_browse():
    page = ask_int("Page number (1-{0}): ".format(MAX_PAGES), 1, MAX_PAGES)
    print("\n  Fetching page {0} ...".format(page))
    books = scrape_page(page)
    remember(books)
    show_books(books)


def action_search():
    keyword = ask_text("Title mein kya dhoondhna hai: ").lower()
    pages = ask_int("Kitne pages tak dekhun (1-10) [3]: ", 1, 10, default=3)

    found = []
    for page in range(1, pages + 1):
        print("  page {0}/{1} ...".format(page, pages))
        for book in scrape_page(page):
            if keyword in book.title.lower():
                found.append(book)

    remember(found)
    print("\n  '{0}' ke liye {1} result mile.".format(keyword, len(found)))
    show_books(found)


def action_filter():
    if not LAST_RESULTS:
        print("\n  Pehle browse ya search karo, phir filter lagega.")
        return

    max_price = ask_float("Max price (Enter = koi limit nahi): ")
    min_rating = ask_int("Min rating 1-5 (Enter = koi limit nahi): ", 1, 5, default=0)
    only_stock = ask_yes_no("Sirf 'in stock' wali dikhaun")

    result = []
    for book in LAST_RESULTS:
        if max_price is not None and (book.price is None or book.price > max_price):
            continue
        if min_rating and (book.rating is None or book.rating < min_rating):
            continue
        if only_stock and not book.in_stock():
            continue
        result.append(book)

    print("\n  {0} me se {1} book filter pass kar gayi.".format(
        len(LAST_RESULTS), len(result)))
    show_books(result)


def action_export():
    if not LAST_RESULTS:
        print("\n  Export karne ke liye pehle kuch scrape karo.")
        return

    filename = input("File name [books.csv]: ").strip() or "books.csv"
    fields = ["title", "price", "rating", "availability", "url"]
    try:
        with open(filename, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for book in LAST_RESULTS:
                writer.writerow(book.to_row())
    except OSError as exc:
        print("  -> File likhi nahi ja saki: {0}".format(exc))
        return
    print("  {0} rows '{1}' mein save ho gaye.".format(len(LAST_RESULTS), filename))


def action_probe():
    """
    Site ka structure check karta hai. Agar site ka HTML kabhi badal jaaye
    to yeh batayega ki kaun sa field parse nahi ho paa raha.
    """
    print("\n  Page 1 fetch kar raha hoon ...")
    html = fetch(CATALOGUE.format(1))
    print("  HTML mila: {0} characters".format(len(html)))

    books = parse_books(html)
    print("  Parse hui books: {0}".format(len(books)))
    if not books:
        print("  !! Ek bhi book nahi mili - site ka layout badal gaya hoga.")
        return

    for field in ("title", "price", "rating", "availability"):
        ok = sum(1 for b in books if getattr(b, field) not in (None, ""))
        flag = "OK " if ok == len(books) else "!! "
        print("  {0}{1:14} {2}/{3} books mein mila".format(
            flag, field, ok, len(books)))

    print("\n  Pehli book:")
    first = books[0]
    print("    title        : {0}".format(first.title))
    print("    price        : {0}".format(first.price))
    print("    rating       : {0}".format(first.rating))
    print("    availability : {0}".format(first.availability))
    print("    url          : {0}".format(first.url))


# -------------------------------------------------------------------- menu

MENU = (
    ("1", "Catalogue browse karo (ek page)", action_browse),
    ("2", "Title se search karo (kai pages)", action_search),
    ("3", "Last results par filter lagao", action_filter),
    ("4", "Results CSV mein save karo", action_export),
    ("5", "Site structure probe karo (debug)", action_probe),
)


def show_menu():
    print("\n" + "=" * 52)
    print("  BOOK SCRAPER  -  Cognifyz Internship Task 6")
    print("  Source: {0}".format(BASE))
    print("=" * 52)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    actions = {key: func for key, _, func in MENU}
    print("\nYeh scraper books.toscrape.com se data laata hai.")
    print("Har request ke beech {0} second ka gap rakha jaata hai.".format(DELAY))

    while True:
        show_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            print("\nBye!")
            break

        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 5 ke beech ka option chuno.")
            continue

        try:
            action()
        except ScrapeError as exc:
            print("\n  Problem: {0}".format(exc))
        except KeyboardInterrupt:
            print("\n  Ruk gaya.")


if __name__ == "__main__":
    main()
