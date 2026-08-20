import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from task6_web_scraper import book_scraper as scraper


BOOKS_HTML = """
<html><body>
  <ul class="breadcrumb"><li><a>Home</a></li><li><a>Books</a></li><li><a>Travel</a></li></ul>
  <article class="product_pod">
    <p class="star-rating Three"></p>
    <h3><a href="a-light/book_1/index.html" title="A Light in the Attic">A Light...</a></h3>
    <div class="product_price">
      <p class="price_color">£51.77</p>
      <p class="instock availability">In stock</p>
    </div>
  </article>
  <li class="next"><a href="page-2.html">next</a></li>
</body></html>
"""

QUOTES_HTML = """
<html><body>
  <div class="quote">
    <span class="text">The world as we have created it is a process of our thinking.</span>
    <small class="author">Albert Einstein</small>
    <span><a href="/author/Albert-Einstein">(about)</a></span>
    <div class="tags"><a class="tag">change</a><a class="tag">thinking</a></div>
  </div>
  <li class="next"><a href="/page/2/">Next</a></li>
</body></html>
"""


class ParsingTests(unittest.TestCase):
    def test_books_fields_and_relative_url(self):
        books = scraper.parse_books(BOOKS_HTML, "https://books.toscrape.com/catalogue/page-1.html")
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0]["title"], "A Light in the Attic")
        self.assertEqual(books[0]["price"], 51.77)
        self.assertEqual(books[0]["rating"], 3)
        self.assertEqual(books[0]["availability"], "In stock")
        self.assertEqual(books[0]["category"], "Travel")
        self.assertEqual(books[0]["url"], "https://books.toscrape.com/catalogue/a-light/book_1/index.html")

    def test_books_next_page(self):
        self.assertEqual(
            scraper.next_page_url(BOOKS_HTML, "https://books.toscrape.com/catalogue/page-1.html"),
            "https://books.toscrape.com/catalogue/page-2.html",
        )

    def test_quotes_fields_and_relative_author_url(self):
        quotes = scraper.parse_quotes(QUOTES_HTML, "https://quotes.toscrape.com/")
        self.assertEqual(len(quotes), 1)
        self.assertIn("world as we have created it", quotes[0]["quote"])
        self.assertEqual(quotes[0]["author"], "Albert Einstein")
        self.assertEqual(quotes[0]["tags"], ["change", "thinking"])
        self.assertEqual(quotes[0]["author_url"], "https://quotes.toscrape.com/author/Albert-Einstein")

    def test_quotes_next_page(self):
        self.assertEqual(
            scraper.next_page_url(QUOTES_HTML, "https://quotes.toscrape.com/"),
            "https://quotes.toscrape.com/page/2/",
        )

    def test_empty_html_returns_no_records(self):
        self.assertEqual(scraper.parse_books("", "https://books.toscrape.com/"), [])
        self.assertEqual(scraper.parse_quotes("", "https://quotes.toscrape.com/"), [])


class ValidationTests(unittest.TestCase):
    def test_valid_records(self):
        valid, invalid = scraper.validate_records([{"title": "Book", "price": 10.0}], ("title", "price"))
        self.assertEqual(valid, [{"title": "Book", "price": 10.0}])
        self.assertEqual(invalid, [])

    def test_missing_fields_are_invalid(self):
        valid, invalid = scraper.validate_records([{"title": "Book", "price": None}], ("title", "price"))
        self.assertEqual(valid, [])
        self.assertEqual(invalid[0][1], ["price"])

    def test_empty_records_are_allowed_for_record_validation(self):
        self.assertEqual(scraper.validate_records([], ("title",)), ([], []))

    def test_empty_source_fails_health(self):
        result = SimpleNamespace(url="https://books.toscrape.com/", status_code=200, content_type="text/html", text="<html></html>")
        steps, valid, invalid = scraper.validate_source(scraper.SOURCES["1"], result)
        self.assertFalse(all(ok for ok, _ in steps))
        self.assertEqual(valid, [])
        self.assertEqual(invalid, [])

    def test_valid_source_passes_health(self):
        result = SimpleNamespace(url="https://books.toscrape.com/catalogue/page-1.html", status_code=200, content_type="text/html", text=BOOKS_HTML)
        steps, valid, invalid = scraper.validate_source(scraper.SOURCES["1"], result)
        self.assertTrue(all(ok for ok, _ in steps))
        self.assertEqual(len(valid), 1)
        self.assertEqual(invalid, [])


class UrlSafetyTests(unittest.TestCase):
    def test_valid_https_url(self):
        self.assertEqual(scraper.validate_url("https://books.toscrape.com/"), "https://books.toscrape.com/")

    def test_verified_source_requires_allowed_domain(self):
        with self.assertRaises(scraper.ScrapeError):
            scraper.validate_url("https://example.com/", "books.toscrape.com", verified_source=True)

    def test_rejects_http(self):
        with self.assertRaises(scraper.ScrapeError):
            scraper.validate_url("http://books.toscrape.com/")

    def test_rejects_localhost(self):
        with self.assertRaises(scraper.ScrapeError):
            scraper.validate_url("https://localhost/")

    def test_rejects_loopback(self):
        with self.assertRaises(scraper.ScrapeError):
            scraper.validate_url("https://127.0.0.1/")

    def test_rejects_private_ip(self):
        with self.assertRaises(scraper.ScrapeError):
            scraper.validate_url("https://192.168.1.5/")


class InputTests(unittest.TestCase):
    def test_ask_float_rejects_non_finite_values(self):
        with patch("builtins.input", side_effect=["nan", "inf", "-inf", "25.50"]):
            self.assertEqual(scraper.ask_float("Price: "), 25.50)


class ExportTests(unittest.TestCase):
    def test_csv_and_json_exports(self):
        old_dir = scraper.EXPORT_DIR
        records = [{"title": "Book", "price": 10.0, "tags": ["one", "two"]}]
        with tempfile.TemporaryDirectory() as temp:
            scraper.EXPORT_DIR = Path(temp)
            csv_path = scraper.export_csv(records, ("title", "price", "tags"), "1")
            json_path = scraper.export_json(records, "1")
            self.assertTrue(csv_path.exists())
            self.assertIn("title,price,tags", csv_path.read_text(encoding="utf-8"))
            self.assertIn("one, two", csv_path.read_text(encoding="utf-8"))
            self.assertEqual(json.loads(json_path.read_text(encoding="utf-8")), records)
        scraper.EXPORT_DIR = old_dir

    def test_export_creates_directory(self):
        old_dir = scraper.EXPORT_DIR
        with tempfile.TemporaryDirectory() as temp:
            scraper.EXPORT_DIR = Path(temp) / "exports"
            path = scraper.export_json([], "2")
            self.assertTrue(path.parent.exists())
        scraper.EXPORT_DIR = old_dir


class FetchTests(unittest.TestCase):
    @patch.object(scraper, "_polite_wait")
    @patch.object(scraper.requests, "get")
    def test_fetch_returns_html_result_and_counts_request(self, mock_get, _mock_wait):
        mock_get.return_value = SimpleNamespace(
            status_code=200,
            url="https://books.toscrape.com/",
            headers={"content-type": "text/html"},
            apparent_encoding="utf-8",
            encoding="utf-8",
            text=BOOKS_HTML,
        )
        stats = {"http_requests": 0}
        result = scraper.fetch("https://books.toscrape.com/", "books.toscrape.com", True, stats)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(stats["http_requests"], 1)

    def test_fetch_rejects_redirect_to_other_domain(self):
        response = SimpleNamespace(
            status_code=200,
            url="https://evil.example/",
            headers={"content-type": "text/html"},
            apparent_encoding="utf-8",
            encoding="utf-8",
            text=BOOKS_HTML,
        )
        with patch.object(scraper, "_polite_wait"), patch.object(scraper.requests, "get", return_value=response):
            with self.assertRaises(scraper.ScrapeError):
                scraper.fetch("https://books.toscrape.com/", "books.toscrape.com", True)

    def test_fetch_accepts_redirect_within_allowed_domain(self):
        response = SimpleNamespace(
            status_code=200,
            url="https://books.toscrape.com/catalogue/page-2.html",
            headers={"content-type": "text/html"},
            apparent_encoding="utf-8",
            encoding="utf-8",
            text=BOOKS_HTML,
        )
        with patch.object(scraper, "_polite_wait"), patch.object(scraper.requests, "get", return_value=response):
            result = scraper.fetch("https://books.toscrape.com/", "books.toscrape.com", True)
        self.assertEqual(result.url, response.url)


class SourceStateTests(unittest.TestCase):
    def test_switching_source_clears_previous_results_and_stats(self):
        old_source = scraper.CURRENT_SOURCE
        old_results = list(scraper.LAST_RESULTS)
        old_stats = scraper.LAST_STATS
        try:
            scraper.CURRENT_SOURCE = "1"
            scraper.LAST_RESULTS[:] = [{"title": "Old book"}]
            scraper.LAST_STATS = {"records_found": 1}
            with patch.object(scraper, "ask_int", return_value=2), patch.object(scraper, "run_source_health", return_value=True):
                scraper.action_choose_source()
            self.assertEqual(scraper.CURRENT_SOURCE, "2")
            self.assertEqual(scraper.LAST_RESULTS, [])
            self.assertIsNone(scraper.LAST_STATS)
        finally:
            scraper.CURRENT_SOURCE = old_source
            scraper.LAST_RESULTS[:] = old_results
            scraper.LAST_STATS = old_stats

    @patch.object(scraper, "fetch", side_effect=scraper.ScrapeError("network failure"))
    def test_failed_health_check_clears_previous_verification(self, _mock_fetch):
        scraper.VERIFIED_SOURCES.add("1")
        try:
            with self.assertRaises(scraper.ScrapeError):
                scraper.run_source_health("1", quiet=True)
            self.assertNotIn("1", scraper.VERIFIED_SOURCES)
        finally:
            scraper.VERIFIED_SOURCES.discard("1")


if __name__ == "__main__":
    unittest.main()
