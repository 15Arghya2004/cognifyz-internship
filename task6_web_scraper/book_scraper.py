"""Task 6: an interactive HTML web scraper for two practice websites."""

import csv
import ipaddress
import json
import math
import re
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# ------------------------------------------------------------ constants

SOURCES = {
    "1": {
        "name": "Books to Scrape",
        "base_url": "https://books.toscrape.com/",
        "start_url": "https://books.toscrape.com/catalogue/page-1.html",
        "domain": "books.toscrape.com",
        "type": "books",
        "required_fields": ("title", "price", "rating", "availability", "url"),
        "display_fields": ("title", "price", "rating", "availability", "url", "category"),
        "max_pages": 50,
    },
    "2": {
        "name": "Quotes to Scrape",
        "base_url": "https://quotes.toscrape.com/",
        "start_url": "https://quotes.toscrape.com/",
        "domain": "quotes.toscrape.com",
        "type": "quotes",
        "required_fields": ("quote", "author", "tags", "author_url"),
        "display_fields": ("quote", "author", "tags", "author_url"),
        "max_pages": 10,
    },
}

TIMEOUT = 20
RETRIES = 2
BACKOFF = 0.8
REQUEST_DELAY = 1.0
HEADERS = {
    "User-Agent": "CognifyzInternship-Task6/2.0 (educational scraper; python-requests)"
}
EXPORT_DIR = Path(__file__).resolve().parent / "exports"
PRICE_RE = re.compile(r"[£$€]\s*([0-9]+(?:\.[0-9]{1,2})?)")
RATING_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}

CURRENT_SOURCE = "1"
LAST_RESULTS = []
LAST_STATS = None
VERIFIED_SOURCES = set()
LAST_REQUEST_AT = 0.0


class ScrapeError(Exception):
    """An expected problem that should be shown without a traceback."""


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
            value = float(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 25.50")
            continue
        if math.isfinite(value):
            return value
        print("  -> Finite number likho, jaise 25.50")


def ask_text(prompt, required=True):
    while True:
        raw = input(prompt).strip()
        if raw or not required:
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


# ------------------------------------------------------------ HTTP and URL safety

def _host_is_allowed(host, allowed_domain):
    host = (host or "").lower()
    domain = (allowed_domain or "").lower()
    return host == domain or host.endswith("." + domain)


def _host_is_unsafe(host):
    host = (host or "").strip().lower()

    # Reject localhost names before checking DNS or IP formats.
    if not host or host in ("localhost", "localhost.localdomain"):
        return True

    # Reject literal loopback, private, link-local, and reserved IPs.
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None:
        return address.is_loopback or address.is_private or address.is_link_local or address.is_reserved

    # Resolve hostnames and reject any unsafe address they return.
    try:
        resolved = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in resolved:
        try:
            address = ipaddress.ip_address(info[4][0])
        except ValueError:
            continue
        if address.is_loopback or address.is_private or address.is_link_local or address.is_reserved:
            return True
    return False


def validate_url(url, allowed_domain=None, verified_source=False):
    """Allow only HTTPS and protect custom probes from local targets."""
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ScrapeError("Sirf HTTPS URLs allowed hain.")
    if not parsed.hostname:
        raise ScrapeError("URL mein domain missing hai.")

    host = parsed.hostname
    if verified_source:
        if not _host_is_allowed(host, allowed_domain):
            raise ScrapeError("Domain allowlist se match nahi hua: {0}".format(host))
    elif _host_is_unsafe(host):
        raise ScrapeError("Local/private/internal URL safety ke liye reject kiya gaya.")
    return url


def _polite_wait():
    global LAST_REQUEST_AT
    gap = time.time() - LAST_REQUEST_AT
    if gap < REQUEST_DELAY:
        time.sleep(REQUEST_DELAY - gap)
    LAST_REQUEST_AT = time.time()


def fetch(url, allowed_domain=None, verified_source=False, stats=None):
    """Fetch HTML with timeout, retries, backoff, and friendly errors."""
    validate_url(url, allowed_domain, verified_source)
    last_error = None

    for attempt in range(RETRIES + 1):
        _polite_wait()
        if stats is not None:
            stats["http_requests"] += 1
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        except requests.exceptions.Timeout:
            last_error = "Server ne {0} second mein jawab nahi diya.".format(TIMEOUT)
        except requests.exceptions.ConnectionError:
            last_error = "Connect nahi ho paaya. Internet ya firewall check karo."
        except requests.exceptions.RequestException as exc:
            last_error = "Request fail ho gayi: {0}".format(exc)
        else:
            if response.status_code == 404:
                raise ScrapeError("Page maujood nahi hai (404).")
            if response.status_code >= 500 and attempt < RETRIES:
                last_error = "Server ne status {0} bheja.".format(response.status_code)
            elif response.status_code != 200:
                raise ScrapeError("Server ne status {0} bheja.".format(response.status_code))
            else:
                response.encoding = response.apparent_encoding or response.encoding
                # Redirects must stay within the same URL safety rules.
                validate_url(response.url, allowed_domain, verified_source)
                return SimpleNamespace(
                    url=response.url,
                    status_code=response.status_code,
                    content_type=response.headers.get("content-type", ""),
                    text=response.text,
                )

        if attempt < RETRIES:
            time.sleep(BACKOFF * (attempt + 1))

    raise ScrapeError(last_error or "Request fail ho gayi.")


# ------------------------------------------------------------ parsing

def parse_price(text):
    match = PRICE_RE.search(text)
    if not match:
        return None
    try:
        return float(match.group(1))
    except ValueError:
        return None


def parse_rating(container):
    """Convert the site's word rating into a number."""
    for element in container.find_all(True):
        classes = [item.lower() for item in element.get("class", [])]
        for word, value in RATING_WORDS.items():
            if "star" in " ".join(classes) and word in classes:
                return value
    return None


def parse_availability(container):
    text = " ".join(container.get_text(" ", strip=True).split()).lower()
    if "out of stock" in text:
        return "Out of stock"
    if "in stock" in text:
        return "In stock"
    return ""


def parse_books(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    breadcrumb = soup.select("ul.breadcrumb li a")
    category = breadcrumb[-1].get_text(strip=True) if len(breadcrumb) >= 3 else ""
    books = []

    for heading in soup.find_all("h3"):
        anchor = heading.find("a")
        if anchor is None:
            continue
        title = anchor.get("title") or anchor.get_text(strip=True)
        if not title:
            continue
        container = heading.find_parent(["article", "li", "div"]) or heading.parent
        books.append({
            "title": title,
            "price": parse_price(container.get_text(" ", strip=True)),
            "rating": parse_rating(container),
            "availability": parse_availability(container),
            "url": urljoin(base_url, anchor.get("href", "")),
            "category": category,
        })
    return books


def parse_quotes(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    quotes = []
    for container in soup.select("div.quote"):
        quote_el = container.select_one("span.text")
        author_el = container.select_one("small.author")
        author_link = container.select_one("span a[href]")
        quotes.append({
            "quote": quote_el.get_text(strip=True) if quote_el else "",
            "author": author_el.get_text(strip=True) if author_el else "",
            "tags": [tag.get_text(strip=True) for tag in container.select("a.tag")],
            "author_url": urljoin(base_url, author_link.get("href", "")) if author_link else "",
        })
    return quotes


def parse_source(html, page_url, source):
    if source["type"] == "books":
        return parse_books(html, page_url)
    return parse_quotes(html, page_url)


# ------------------------------------------------------------ validation and health

def missing_value(value):
    return value is None or value == "" or value == []


def validate_records(records, required_fields):
    valid = []
    invalid = []
    for record in records:
        missing = [field for field in required_fields if missing_value(record.get(field))]
        if missing:
            invalid.append((record, missing))
        else:
            valid.append(record)
    return valid, invalid


def validate_source(source, result):
    """Return health steps and parsed records without changing verification state."""
    steps = [
        (True, "HTTPS"),
        (True, "Domain: {0}".format(source["domain"])),
        (result.status_code == 200, "HTTP {0}".format(result.status_code)),
    ]
    content_type = result.content_type.lower()
    steps.append(("html" in content_type or not content_type, "Expected HTML"))

    soup = BeautifulSoup(result.text, "html.parser")
    steps.append((bool(soup.find()), "HTML structure"))
    if source["type"] == "books":
        structure_found = bool(soup.find("h3") and soup.select_one("article.product_pod"))
    else:
        structure_found = bool(soup.select_one("div.quote span.text"))
    steps.append((structure_found, "Expected structure"))

    records = parse_source(result.text, result.url, source)
    steps.append((bool(records), "Records extracted ({0})".format(len(records))))
    valid, invalid = validate_records(records, source["required_fields"])
    if records:
        label = "Required fields"
        steps.append((not invalid, label if not invalid else "{0}: {1}".format(label, ", ".join(invalid[0][1]))))
    return steps, valid, invalid


def print_health(steps):
    for ok, label in steps:
        print("  {0} {1}".format("[OK]" if ok else "[!!]", label))


def run_source_health(source_key, quiet=False, return_steps=False):
    source = SOURCES[source_key]
    VERIFIED_SOURCES.discard(source_key)
    if not quiet:
        print("\nChecking source: {0}".format(source["name"]))
    result = fetch(source["start_url"], source["domain"], verified_source=True)
    steps, _, _ = validate_source(source, result)
    if not quiet:
        print_health(steps)
    if not (steps and all(ok for ok, _ in steps)):
        if not quiet:
            print("\nSource validation failed.")
            for ok, label in steps:
                if not ok:
                    print("  Reason: {0}".format(label))
            print("\nScraping cancelled.")
        return (False, steps) if return_steps else False
    VERIFIED_SOURCES.add(source_key)
    if not quiet:
        print("\nSource verified.")
    return (True, steps) if return_steps else True


# ------------------------------------------------------------ pagination and scraping

def next_page_url(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    return urljoin(page_url, next_link.get("href", "")) if next_link else None


def scrape_source(source_key, mode, custom_pages=None):
    source = SOURCES[source_key]
    stats = {
        "pages_requested": 0,
        "http_requests": 0,
        "records_found": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "started_at": time.perf_counter(),
    }
    records = []
    url = source["start_url"]
    max_pages = 1 if mode == "current" else source["max_pages"]
    if mode == "custom":
        max_pages = custom_pages

    try:
        while url and stats["pages_requested"] < max_pages:
            result = fetch(url, source["domain"], verified_source=True, stats=stats)
            stats["pages_requested"] += 1
            page_records = parse_source(result.text, result.url, source)
            valid, invalid = validate_records(page_records, source["required_fields"])
            stats["records_found"] += len(page_records)
            stats["valid_records"] += len(valid)
            stats["invalid_records"] += len(invalid)
            records.extend(valid)
            print("  Page {0} OK  {1} valid items".format(stats["pages_requested"], len(valid)))
            if mode == "current":
                break
            url = next_page_url(result.text, result.url)
    finally:
        stats["elapsed_seconds"] = time.perf_counter() - stats["started_at"]
    return records, stats


# ------------------------------------------------------------ display and filtering

def stars(value):
    return "?" if value is None else "*" * int(value) + "." * (5 - int(value))


def show_records(records, source_key, limit=15):
    source = SOURCES[source_key]
    if not records:
        print("\n  (koi result nahi mila)")
        return

    if source["type"] == "books":
        print("\n  {0:>3}  {1:44}  {2:>8}  {3:7}  {4}".format("#", "TITLE", "PRICE", "RATING", "STOCK"))
        print("  " + "-" * 80)
        for index, book in enumerate(records[:limit], start=1):
            title = book["title"] if len(book["title"]) <= 44 else book["title"][:41] + "..."
            price = "-" if book["price"] is None else "{0:.2f}".format(book["price"])
            print("  {0:>3}  {1:44}  {2:>8}  {3:7}  {4}".format(index, title, price, stars(book["rating"]), book["availability"]))
        priced = [book["price"] for book in records if book.get("price") is not None]
        summary = "\n  {0} results".format(len(records))
        if priced:
            summary += " | price {0:.2f} - {1:.2f} | average {2:.2f}".format(min(priced), max(priced), sum(priced) / len(priced))
        print(summary)
    else:
        print("\n  {0:>3}  {1:54}  {2:18}  {3}".format("#", "QUOTE", "AUTHOR", "TAGS"))
        print("  " + "-" * 96)
        for index, quote in enumerate(records[:limit], start=1):
            text = quote["quote"] if len(quote["quote"]) <= 54 else quote["quote"][:51] + "..."
            tags = ", ".join(quote["tags"])
            tags = tags if len(tags) <= 24 else tags[:21] + "..."
            print("  {0:>3}  {1:54}  {2:18}  {3}".format(index, text, quote["author"], tags))
        print("\n  {0} results".format(len(records)))
    if len(records) > limit:
        print("  (upar sirf pehle {0} dikhaye)".format(limit))


def show_stats(source_key, stats):
    if stats is None:
        print("\n  Abhi koi scrape run nahi hua.")
        return
    print("\nSCRAPE REPORT\n--------------------------------")
    print("Source          : {0}".format(SOURCES[source_key]["name"]))
    print("Pages scraped   : {0}".format(stats["pages_requested"]))
    print("Items found     : {0}".format(stats["records_found"]))
    print("Valid items     : {0}".format(stats["valid_records"]))
    print("Invalid items   : {0}".format(stats["invalid_records"]))
    print("HTTP requests   : {0}".format(stats["http_requests"]))
    print("Elapsed time    : {0:.2f} sec".format(stats["elapsed_seconds"]))
    print("--------------------------------")


def filter_books(records):
    keyword = ask_text("Title search (Enter = skip): ", required=False).lower()
    max_price = ask_float("Max price (Enter = koi limit nahi): ")
    min_rating = ask_int("Min rating 1-5 (Enter = koi limit nahi): ", 1, 5, default=0)
    only_stock = ask_yes_no("Sirf 'in stock' wali dikhaun")
    result = []
    for book in records:
        if keyword and keyword not in book["title"].lower():
            continue
        if max_price is not None and (book["price"] is None or book["price"] > max_price):
            continue
        if min_rating and (book["rating"] is None or book["rating"] < min_rating):
            continue
        if only_stock and "in stock" not in book["availability"].lower():
            continue
        result.append(book)
    return result


def filter_quotes(records):
    quote_text = ask_text("Quote search (Enter = skip): ", required=False).lower()
    author = ask_text("Author search (Enter = skip): ", required=False).lower()
    tag = ask_text("Tag filter (Enter = skip): ", required=False).lower()
    result = []
    for quote in records:
        if quote_text and quote_text not in quote["quote"].lower():
            continue
        if author and author not in quote["author"].lower():
            continue
        if tag and tag not in [item.lower() for item in quote["tags"]]:
            continue
        result.append(quote)
    return result


# ------------------------------------------------------------ export

def export_path(source_key, extension):
    EXPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    return EXPORT_DIR / "{0}_{1}.{2}".format(SOURCES[source_key]["type"], timestamp, extension)


def export_csv(records, fields, source_key):
    path = export_path(source_key, "csv")
    try:
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            for record in records:
                row = {}
                for field in fields:
                    value = record.get(field, "")
                    row[field] = ", ".join(map(str, value)) if isinstance(value, list) else value
                writer.writerow(row)
    except OSError as exc:
        raise ScrapeError("CSV export fail ho gaya: {0}".format(exc))
    return path


def export_json(records, source_key):
    path = export_path(source_key, "json")
    try:
        with path.open("w", encoding="utf-8") as handle:
            json.dump(records, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    except OSError as exc:
        raise ScrapeError("JSON export fail ho gaya: {0}".format(exc))
    return path


# ------------------------------------------------------------ actions and probe

def action_choose_source():
    global CURRENT_SOURCE, LAST_STATS
    print("\nVerified Web Sources")
    for key, source in SOURCES.items():
        print("  {0}. {1} ({2})".format(key, source["name"], source["base_url"]))
    selected_source = str(ask_int("\nSource chuno: ", 1, len(SOURCES)))
    if selected_source != CURRENT_SOURCE:
        LAST_RESULTS.clear()
        LAST_STATS = None
    CURRENT_SOURCE = selected_source
    print("\nSelected: {0}".format(SOURCES[CURRENT_SOURCE]["name"]))
    if run_source_health(CURRENT_SOURCE):
        print("Ready to scrape.")


def action_scrape():
    global LAST_RESULTS, LAST_STATS
    if not run_source_health(CURRENT_SOURCE):
        return
    source = SOURCES[CURRENT_SOURCE]
    print("\nPagination\n  1. Current page\n  2. Custom number of pages\n  3. All available pages")
    choice = ask_int("\nMode: ", 1, 3)
    mode = "current" if choice == 1 else "custom" if choice == 2 else "all"
    pages = ask_int("Kitne pages (1-{0}): ".format(source["max_pages"]), 1, source["max_pages"]) if mode == "custom" else None
    print("\nScraping {0} ...".format(source["name"]))
    LAST_RESULTS, LAST_STATS = scrape_source(CURRENT_SOURCE, mode, pages)
    show_records(LAST_RESULTS, CURRENT_SOURCE)
    show_stats(CURRENT_SOURCE, LAST_STATS)


def action_filter():
    global LAST_RESULTS
    if not LAST_RESULTS:
        print("\n  Pehle scrape karo, phir filter lagega.")
        return
    if SOURCES[CURRENT_SOURCE]["type"] == "books":
        LAST_RESULTS = filter_books(LAST_RESULTS)
    else:
        LAST_RESULTS = filter_quotes(LAST_RESULTS)
    print("\n  {0} result filter ke baad bache.".format(len(LAST_RESULTS)))
    show_records(LAST_RESULTS, CURRENT_SOURCE)


def action_export():
    if not LAST_RESULTS:
        print("\n  Export karne ke liye pehle kuch scrape karo.")
        return
    print("\nExport format\n  1. CSV\n  2. JSON\n  3. Dono")
    choice = ask_int("\nFormat: ", 1, 3)
    fields = SOURCES[CURRENT_SOURCE]["display_fields"]
    if choice in (1, 3):
        print("  CSV save hua: {0}".format(export_csv(LAST_RESULTS, fields, CURRENT_SOURCE)))
    if choice in (2, 3):
        print("  JSON save hua: {0}".format(export_json(LAST_RESULTS, CURRENT_SOURCE)))


def action_health():
    run_source_health(CURRENT_SOURCE)


def action_stats():
    show_stats(CURRENT_SOURCE, LAST_STATS)


def probe_site(url, source_key=None):
    allowed_domain = SOURCES[source_key]["domain"] if source_key else None
    result = fetch(url, allowed_domain, verified_source=source_key is not None)
    soup = BeautifulSoup(result.text, "html.parser")
    headings = [heading.get_text(" ", strip=True) for heading in soup.find_all(["h1", "h2", "h3"])]
    pagination = bool(soup.select_one("li.next a") or soup.find("a", string=lambda text: text and "next" in text.lower()))
    return result, soup, headings, pagination


def action_probe():
    print("\nProbe type\n  1. Current verified source\n  2. Custom HTTPS URL")
    choice = ask_int("\nChoice: ", 1, 2)
    if choice == 1:
        url = SOURCES[CURRENT_SOURCE]["start_url"]
        source_key = CURRENT_SOURCE
    else:
        url = ask_text("URL: ")
        validate_url(url)
        source_key = None
    result, soup, headings, pagination = probe_site(url, source_key)
    print("\nSITE STRUCTURE PROBE\n--------------------------------")
    print("URL          : {0}".format(result.url))
    print("Status       : {0}".format(result.status_code))
    print("Content type : {0}".format(result.content_type or "-"))
    print("Page title   : {0}".format(soup.title.get_text(strip=True) if soup.title else "-"))
    print("Links        : {0}".format(len(soup.find_all("a"))))
    print("Images       : {0}".format(len(soup.find_all("img"))))
    print("Forms        : {0}".format(len(soup.find_all("form"))))
    print("Tables       : {0}".format(len(soup.find_all("table"))))
    print("Pagination   : {0}".format("detected" if pagination else "not detected"))
    print("Headings     :")
    for heading in headings[:8]:
        print("  - {0}".format(heading))
    if source_key:
        records = parse_source(result.text, result.url, SOURCES[source_key])
        valid, invalid = validate_records(records, SOURCES[source_key]["required_fields"])
        print("Parser       : {0} records, {1} valid, {2} invalid".format(len(records), len(valid), len(invalid)))
    print("--------------------------------")


# ------------------------------------------------------------ menu

MENU = (
    ("1", "Verified source chuno", action_choose_source),
    ("2", "Source scrape karo", action_scrape),
    ("3", "Last results par search/filter lagao", action_filter),
    ("4", "Results export karo (CSV/JSON)", action_export),
    ("5", "Source health validate karo", action_health),
    ("6", "Scraping statistics dekho", action_stats),
    ("7", "Site structure probe karo", action_probe),
)


def show_menu():
    source = SOURCES[CURRENT_SOURCE]
    verification = "verified this run" if CURRENT_SOURCE in VERIFIED_SOURCES else "not verified in this run"
    print("\n" + "=" * 56)
    print("        COGNIFYZ INTERACTIVE WEB SCRAPER")
    print("=" * 56)
    print("  Current source: {0}".format(source["name"]))
    print("  Verification : {0}".format(verification))
    print("\n  Verified Web Sources")
    for key, item in SOURCES.items():
        print("    {0}. {1}".format(key, item["name"]))
    print("\n  Actions")
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    actions = {key: function for key, _, function in MENU}
    print("\nYeh tool HTML web scraping karta hai: Requests -> BeautifulSoup -> data.")
    print("Har request ke beech responsible delay rakha jaata hai.")
    while True:
        show_menu()
        choice = input("\nChoice: ").strip()
        if choice == "0":
            print("\nBye!")
            return 0
        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 7 ke beech ka option chuno.")
            continue
        try:
            action()
        except ScrapeError as exc:
            print("\n  Problem: {0}".format(exc))
        except KeyboardInterrupt:
            print("\n  Ruk gaya.")


if __name__ == "__main__":
    sys.exit(main())
