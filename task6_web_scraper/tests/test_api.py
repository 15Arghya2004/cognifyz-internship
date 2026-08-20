import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from task6_web_scraper import api


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.old_results = list(api.scraper.LAST_RESULTS)
        self.old_stats = api.scraper.LAST_STATS
        self.old_source = api.scraper.CURRENT_SOURCE
        self.old_export_dir = api.scraper.EXPORT_DIR
        self.old_base_results = list(api._base_results)
        self.old_rate = api._gbp_to_inr.copy()
        api.scraper.LAST_RESULTS[:] = [{
            "title": "Test Book",
            "price": 10.0,
            "rating": 4,
            "availability": "In stock",
            "category": "Travel",
            "url": "https://books.toscrape.com/book",
        }]
        api.scraper.LAST_STATS = {
            "pages_requested": 1,
            "http_requests": 1,
            "records_found": 1,
            "valid_records": 1,
            "invalid_records": 0,
            "elapsed_seconds": 0.2,
        }
        api.scraper.CURRENT_SOURCE = "1"
        api._base_results = list(api.scraper.LAST_RESULTS)
        api._gbp_to_inr = {"attempted": True, "rate": 80.0, "updated_at": "2026-08-20T00:00:00+00:00"}

    def tearDown(self):
        api.scraper.LAST_RESULTS[:] = self.old_results
        api.scraper.LAST_STATS = self.old_stats
        api.scraper.CURRENT_SOURCE = self.old_source
        api.scraper.EXPORT_DIR = self.old_export_dir
        api._base_results = self.old_base_results
        api._gbp_to_inr = self.old_rate

    def test_currency_enrichment_uses_cached_rate(self):
        records = api._records_for_response(api.scraper.LAST_RESULTS, "1")
        self.assertEqual(records[0]["price_inr"], 800.0)
        self.assertEqual(records[0]["original_currency"], "GBP")

    def test_json_export_is_structured(self):
        with tempfile.TemporaryDirectory() as temp:
            api.scraper.EXPORT_DIR = Path(temp)
            result = api.export(api.ExportRequest(format="json"))
            payload = json.loads((Path(temp) / result["filename"]).read_text(encoding="utf-8"))
        self.assertIn("report", payload)
        self.assertIn("statistics", payload)
        self.assertEqual(len(payload["results"]), 1)

    def test_pdf_export_creates_report(self):
        with tempfile.TemporaryDirectory() as temp:
            api.scraper.EXPORT_DIR = Path(temp)
            result = api.export(api.ExportRequest(format="pdf"))
            path = Path(temp) / result["filename"]
            self.assertTrue(path.exists())
            self.assertTrue(path.read_bytes().startswith(b"%PDF"))

    def test_source_switch_clears_api_state(self):
        with patch.object(api.scraper, "run_source_health", return_value=(True, [])):
            api.verify("2")
        self.assertEqual(api.scraper.CURRENT_SOURCE, "2")
        self.assertEqual(api.scraper.LAST_RESULTS, [])
        self.assertIsNone(api.scraper.LAST_STATS)


BOOK_A = {
    "title": "Cheap Book",
    "price": 10.0,
    "rating": 4,
    "availability": "In stock",
    "category": "Travel",
    "url": "https://books.toscrape.com/a",
}
BOOK_B = {
    "title": "Pricey Book",
    "price": 50.0,
    "rating": 2,
    "availability": "In stock",
    "category": "History",
    "url": "https://books.toscrape.com/b",
}


class ContractRegressionTests(unittest.TestCase):
    """Regressions for the frontend/backend contract fixes."""

    def setUp(self):
        self.old_results = list(api.scraper.LAST_RESULTS)
        self.old_stats = api.scraper.LAST_STATS
        self.old_source = api.scraper.CURRENT_SOURCE
        self.old_export_dir = api.scraper.EXPORT_DIR
        self.old_base_results = list(api._base_results)
        self.old_rate = dict(api._gbp_to_inr)

        api.scraper.LAST_RESULTS[:] = [dict(BOOK_A), dict(BOOK_B)]
        api.scraper.LAST_STATS = {
            "pages_requested": 1,
            "http_requests": 1,
            "records_found": 2,
            "valid_records": 2,
            "invalid_records": 0,
            "elapsed_seconds": 0.2,
        }
        api.scraper.CURRENT_SOURCE = "1"
        api._base_results = [dict(BOOK_A), dict(BOOK_B)]
        # Fixed rate so no test ever reaches the network.
        api._gbp_to_inr = {"rate": 80.0, "updated_at": "2026-08-20T00:00:00+00:00", "last_attempt": None}

    def tearDown(self):
        api.scraper.LAST_RESULTS[:] = self.old_results
        api.scraper.LAST_STATS = self.old_stats
        api.scraper.CURRENT_SOURCE = self.old_source
        api.scraper.EXPORT_DIR = self.old_export_dir
        api._base_results = self.old_base_results
        api._gbp_to_inr = self.old_rate

    def _no_scrape_yet(self):
        api.scraper.LAST_RESULTS[:] = []
        api._base_results = []

    # -------------------------------------------------- GET /api/results

    def test_results_before_scrape_is_valid_json_empty_state(self):
        self._no_scrape_yet()
        payload = api.results()
        self.assertEqual(payload["records"], [])
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["stats"]["record_count"], 0)
        self.assertIn("currency", payload)
        json.dumps(payload)  # must be serialisable, never an empty body

    def test_results_after_scrape_returns_the_records(self):
        payload = api.results()
        self.assertEqual(payload["count"], 2)
        self.assertEqual(payload["records"][0]["price_inr"], 800.0)

    # -------------------------------------------------- POST /api/filter

    def test_filter_without_any_scrape_is_409(self):
        self._no_scrape_yet()
        with self.assertRaises(HTTPException) as caught:
            api.filter_results(api.FilterRequest(source_id="1"))
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIn("before filtering", caught.exception.detail)

    def test_filter_with_zero_matches_returns_valid_empty_json(self):
        payload = api.filter_results(api.FilterRequest(source_id="1", query="no-such-title"))
        self.assertEqual(payload["records"], [])
        self.assertEqual(payload["count"], 0)
        self.assertEqual(payload["stats"]["record_count"], 0)
        json.dumps(payload)
        # The displayed view is empty, but the scraped dataset survives.
        self.assertEqual(api.scraper.LAST_RESULTS, [])
        self.assertEqual(len(api._base_results), 2)

    def test_clear_filters_after_zero_match_restores_the_dataset(self):
        api.filter_results(api.FilterRequest(source_id="1", query="no-such-title"))
        restored = api.filter_results(api.FilterRequest(source_id="1"))
        self.assertEqual(restored["count"], 2)
        self.assertEqual(len(api.scraper.LAST_RESULTS), 2)

    def test_second_filter_applies_to_the_full_dataset_not_the_previous_view(self):
        api.filter_results(api.FilterRequest(source_id="1", max_price=20.0))
        widened = api.filter_results(api.FilterRequest(source_id="1", max_price=100.0))
        self.assertEqual(widened["count"], 2)

    # -------------------------------------------------- POST /api/export

    def test_export_after_zero_match_blames_the_filter_not_a_missing_scrape(self):
        api.filter_results(api.FilterRequest(source_id="1", query="no-such-title"))
        with self.assertRaises(HTTPException) as caught:
            api.export(api.ExportRequest(format="csv"))
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIn("filter", caught.exception.detail.lower())
        self.assertNotIn("Scrape a source before exporting", caught.exception.detail)

    def test_export_without_any_scrape_says_scrape_first(self):
        self._no_scrape_yet()
        with self.assertRaises(HTTPException) as caught:
            api.export(api.ExportRequest(format="csv"))
        self.assertEqual(caught.exception.status_code, 409)
        self.assertIn("before exporting", caught.exception.detail)

    def test_export_works_again_after_filters_are_cleared(self):
        api.filter_results(api.FilterRequest(source_id="1", query="no-such-title"))
        api.filter_results(api.FilterRequest(source_id="1"))
        with tempfile.TemporaryDirectory() as temp:
            api.scraper.EXPORT_DIR = Path(temp)
            result = api.export(api.ExportRequest(format="csv"))
            self.assertTrue((Path(temp) / result["filename"]).exists())

    # -------------------------------------------------- currency retry

    def test_currency_retries_after_failure_and_then_caches_success(self):
        api._gbp_to_inr = {"rate": None, "updated_at": None, "last_attempt": None}

        with patch.object(api.requests, "get", side_effect=api.requests.RequestException("down")):
            first = api._currency_context()
        self.assertFalse(first["available"])
        self.assertIsNone(first["rate"])

        # Inside the cooldown the network must not be touched again.
        with patch.object(api.requests, "get", side_effect=AssertionError("must not retry yet")) as blocked:
            second = api._currency_context()
        self.assertFalse(second["available"])
        self.assertEqual(blocked.call_count, 0)

        # Once the cooldown has passed the lookup is retried and cached.
        api._gbp_to_inr["last_attempt"] = None
        ok = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {"rates": {"INR": 129.81}})
        with patch.object(api.requests, "get", return_value=ok):
            third = api._currency_context()
        self.assertTrue(third["available"])
        self.assertAlmostEqual(third["rate"], 129.81)

        # A cached rate is never re-fetched.
        with patch.object(api.requests, "get", side_effect=AssertionError("must not refetch")) as refetch:
            fourth = api._currency_context()
        self.assertAlmostEqual(fourth["rate"], 129.81)
        self.assertEqual(refetch.call_count, 0)


if __name__ == "__main__":
    unittest.main()
