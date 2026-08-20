"""JSON API for the Task 6 scraper dashboard."""

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from . import book_scraper as scraper


app = FastAPI(title="Cognifyz Web Scraper API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

INR_RATE_URL = "https://api.frankfurter.app/latest?from=GBP&to=INR"
FX_RETRY_SECONDS = 300
_gbp_to_inr = {"rate": None, "updated_at": None, "last_attempt": None}
_base_results: list[dict] = []


class ScrapeRequest(BaseModel):
    source_id: str = "1"
    mode: str = "current"
    pages: int | None = Field(default=None, ge=1, le=50)


class FilterRequest(BaseModel):
    source_id: str = "1"
    query: str = ""
    author: str = ""
    tag: str = ""
    max_price: float | None = Field(default=None, ge=0)
    min_rating: int | None = Field(default=None, ge=1, le=5)
    only_stock: bool = False
    category: str = ""


class ProbeRequest(BaseModel):
    url: str | None = None
    source_id: str | None = None


class ExportRequest(BaseModel):
    format: str = "json"


def _currency_context() -> dict:
    """Fetch one live GBP/INR rate and cache it, with honest fallback.

    A single failure used to disable INR for the whole process, because the
    'attempted' flag was set before the request and never cleared again. Now a
    failure is simply retried later - at most once every FX_RETRY_SECONDS, so a
    dead rate service never turns into one slow lookup per request.
    """
    last_attempt = _gbp_to_inr.get("last_attempt")
    cooled_down = last_attempt is None or (time.monotonic() - last_attempt) >= FX_RETRY_SECONDS
    if _gbp_to_inr["rate"] is None and cooled_down:
        _gbp_to_inr["last_attempt"] = time.monotonic()
        try:
            response = requests.get(INR_RATE_URL, timeout=8)
            response.raise_for_status()
            payload = response.json()
            rate = float(payload["rates"]["INR"])
        except (requests.RequestException, KeyError, TypeError, ValueError):
            rate = None
        if rate is not None:
            _gbp_to_inr["rate"] = rate
            _gbp_to_inr["updated_at"] = datetime.now(timezone.utc).isoformat()
    return {
        "display_currency": "INR",
        "rate": _gbp_to_inr["rate"],
        "updated_at": _gbp_to_inr["updated_at"],
        "available": _gbp_to_inr["rate"] is not None,
    }


def _records_for_response(records: list[dict], source_id: str) -> list[dict]:
    context = _currency_context()
    if scraper.SOURCES[source_id]["type"] != "books":
        return records
    enriched = []
    for record in records:
        item = dict(record)
        item["original_currency"] = "GBP"
        item["price_inr"] = round(record["price"] * context["rate"], 2) if context["available"] and record.get("price") is not None else None
        enriched.append(item)
    return enriched


def _report_stats(records: list[dict], stats: dict | None) -> dict:
    prices = [record["price_inr"] for record in records if record.get("price_inr") is not None]
    ratings = [record["rating"] for record in records if record.get("rating") is not None]
    available = sum("in stock" in record.get("availability", "").lower() for record in records)
    return {
        **(stats or {}),
        "record_count": len(records),
        "average_price_inr": round(sum(prices) / len(prices), 2) if prices else None,
        "average_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
        "available_records": available,
    }


def _export_csv(records: list[dict], source_id: str, path: Path) -> None:
    source_type = scraper.SOURCES[source_id]["type"]
    fields = ("title", "price_inr", "price", "original_currency", "rating", "availability", "category", "url") if source_type == "books" else ("quote", "author", "tags", "author_url")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({field: ", ".join(record[field]) if isinstance(record.get(field), list) else record.get(field, "") for field in fields})


def _export_pdf(records: list[dict], source_id: str, stats: dict | None, path: Path) -> None:
    source = scraper.SOURCES[source_id]
    context = _currency_context()
    report_stats = _report_stats(records, stats)
    styles = getSampleStyleSheet()
    document = SimpleDocTemplate(str(path), pagesize=landscape(A4), rightMargin=12 * mm, leftMargin=12 * mm, topMargin=12 * mm, bottomMargin=12 * mm)
    story = [Paragraph("COGNIFYZ INTERACTIVE WEB SCRAPER", styles["Title"]), Paragraph("Scraping Report", styles["Heading2"]), Spacer(1, 5 * mm)]
    summary = [["Source", source["name"]], ["Generated", datetime.now().strftime("%d %b %Y %H:%M")], ["Records", str(report_stats["record_count"])], ["Valid", str(report_stats.get("valid_records", "N/A"))], ["Invalid", str(report_stats.get("invalid_records", "N/A"))], ["Average price (INR)", str(report_stats.get("average_price_inr") or "N/A")], ["Average rating", str(report_stats.get("average_rating") or "N/A")], ["Currency rate", "1 GBP = INR {0:.2f}".format(context["rate"]) if context["available"] else "INR conversion unavailable"]]
    story += [Table(summary, colWidths=[45 * mm, 75 * mm], style=TableStyle([("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#e9f1ef")), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd6d3")), ("VALIGN", (0, 0), (-1, -1), "TOP")])), Spacer(1, 7 * mm)]
    if source["type"] == "books":
        headers = ["#", "Book", "Price INR", "Original", "Rating", "Availability", "Category"]
        rows = [[str(index), record.get("title", ""), "INR {0}".format(record["price_inr"]) if record.get("price_inr") is not None else "N/A", "GBP {0}".format(record.get("price", "")), str(record.get("rating", "")), record.get("availability", ""), record.get("category", "")] for index, record in enumerate(records, 1)]
    else:
        headers = ["#", "Quote", "Author", "Tags"]
        rows = [[str(index), record.get("quote", ""), record.get("author", ""), ", ".join(record.get("tags", []))] for index, record in enumerate(records, 1)]
    def add_page_number(canvas, document):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(285 * mm, 8 * mm, "Page {0}".format(document.page))
        canvas.restoreState()

    table = Table([headers] + rows, repeatRows=1, colWidths=None)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10232e")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cbd6d3")), ("FONTSIZE", (0, 0), (-1, -1), 7), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story += [Paragraph("Results", styles["Heading2"]), table, Spacer(1, 5 * mm), Paragraph("Scrape information: {0} pages · {1} HTTP requests · {2:.2f}s · Source URL: {3}".format(report_stats.get("pages_requested", "N/A"), report_stats.get("http_requests", "N/A"), report_stats.get("elapsed_seconds", 0), source["base_url"]), styles["Normal"])]
    document.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def _error(exc: Exception) -> HTTPException:
    if isinstance(exc, scraper.ScrapeError):
        return HTTPException(status_code=502, detail=str(exc))
    return HTTPException(status_code=400, detail="Request could not be completed.")


def _source(source_id: str) -> dict:
    source = scraper.SOURCES.get(str(source_id))
    if source is None:
        raise HTTPException(status_code=404, detail="Unknown source.")
    return source


def _switch_source(source_id: str) -> None:
    global _base_results
    _source(source_id)
    if scraper.CURRENT_SOURCE != str(source_id):
        scraper.LAST_RESULTS.clear()
        scraper.LAST_STATS = None
        _base_results = []
        scraper.CURRENT_SOURCE = str(source_id)


def _stats() -> dict | None:
    stats = scraper.LAST_STATS
    if stats is None:
        return None
    return {key: value for key, value in stats.items() if key != "started_at"}


def _record_count() -> int:
    return len(scraper.LAST_RESULTS)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "service": "Cognifyz Web Scraper API", "current_source": scraper.CURRENT_SOURCE}


@app.get("/api/sources")
def sources() -> dict:
    return {
        "current_source": scraper.CURRENT_SOURCE,
        "sources": [
            {
                "id": key,
                "name": item["name"],
                "base_url": item["base_url"],
                "domain": item["domain"],
                "type": item["type"],
                "max_pages": item["max_pages"],
                "verified": key in scraper.VERIFIED_SOURCES,
            }
            for key, item in scraper.SOURCES.items()
        ],
    }


@app.post("/api/sources/{source_id}/verify")
def verify(source_id: str) -> dict:
    _switch_source(source_id)
    try:
        verified, steps = scraper.run_source_health(source_id, quiet=True, return_steps=True)
    except Exception as exc:
        raise _error(exc) from exc
    return {
        "verified": verified,
        "source_id": source_id,
        "steps": [{"ok": ok, "label": label} for ok, label in steps],
        "currency": _currency_context(),
    }


@app.post("/api/scrape")
def scrape(request: ScrapeRequest) -> dict:
    global _base_results
    _switch_source(request.source_id)
    source = _source(request.source_id)
    if request.mode not in {"current", "custom", "all"}:
        raise HTTPException(status_code=422, detail="Mode must be current, custom, or all.")
    if request.mode == "custom" and request.pages is None:
        raise HTTPException(status_code=422, detail="Pages is required for custom mode.")
    try:
        if not scraper.run_source_health(request.source_id, quiet=True):
            raise scraper.ScrapeError("Source verification failed. Scraping cancelled.")
        scraper.LAST_RESULTS, scraper.LAST_STATS = scraper.scrape_source(request.source_id, request.mode, request.pages)
        _base_results = list(scraper.LAST_RESULTS)
    except Exception as exc:
        raise _error(exc) from exc
    records = _records_for_response(scraper.LAST_RESULTS, request.source_id)
    return {
        "source_id": request.source_id,
        "source": source["name"],
        "records": records,
        "stats": _report_stats(records, _stats()),
        "currency": _currency_context(),
    }


@app.post("/api/filter")
def filter_results(request: FilterRequest) -> dict:
    global _base_results
    _switch_source(request.source_id)
    # _base_results is the untouched scraped dataset; LAST_RESULTS is only the
    # currently displayed view. Filtering down to zero is a valid state, so the
    # "did a scrape happen" question must be asked of _base_results.
    if not _base_results:
        raise HTTPException(status_code=409, detail="Scrape a source before filtering.")
    source = _source(request.source_id)
    records = _base_results
    if source["type"] == "books":
        records = [
            item for item in records
            if (not request.query or request.query.lower() in item["title"].lower())
            and (request.max_price is None or item.get("price") is not None and item["price"] <= request.max_price)
            and (request.min_rating is None or item.get("rating") is not None and item["rating"] >= request.min_rating)
            and (not request.only_stock or "in stock" in item.get("availability", "").lower())
            and (not request.category or request.category.lower() in item.get("category", "").lower())
        ]
    else:
        records = [
            item for item in records
            if (not request.query or request.query.lower() in item["quote"].lower())
            and (not request.author or request.author.lower() in item["author"].lower())
            and (not request.tag or request.tag.lower() in [tag.lower() for tag in item["tags"]])
        ]
    scraper.LAST_RESULTS = records
    response_records = _records_for_response(records, request.source_id)
    return {"source_id": request.source_id, "records": response_records, "count": len(response_records), "stats": _report_stats(response_records, _stats()), "currency": _currency_context()}


@app.get("/api/results")
def results() -> dict:
    records = _records_for_response(scraper.LAST_RESULTS, scraper.CURRENT_SOURCE)
    return {"source_id": scraper.CURRENT_SOURCE, "records": records, "stats": _report_stats(records, _stats()), "count": len(records), "currency": _currency_context()}


@app.post("/api/probe")
def probe(request: ProbeRequest) -> dict:
    source_id = str(request.source_id) if request.source_id else None
    url = request.url or (_source(source_id)["start_url"] if source_id else None)
    if not url:
        raise HTTPException(status_code=422, detail="A URL or source is required.")
    try:
        result, soup, headings, pagination = scraper.probe_site(url, source_id)
    except Exception as exc:
        raise _error(exc) from exc
    return {
        "url": result.url,
        "status": result.status_code,
        "content_type": result.content_type or "-",
        "title": soup.title.get_text(strip=True) if soup.title else "-",
        "links": len(soup.find_all("a")),
        "images": len(soup.find_all("img")),
        "forms": len(soup.find_all("form")),
        "tables": len(soup.find_all("table")),
        "pagination": pagination,
        "headings": headings[:8],
    }


@app.post("/api/export")
def export(request: ExportRequest) -> dict:
    if not _base_results:
        raise HTTPException(status_code=409, detail="Scrape a source before exporting.")
    if not scraper.LAST_RESULTS:
        raise HTTPException(
            status_code=409,
            detail="No records match the current filter. Clear or widen the filter, then export again.",
        )
    if request.format not in {"csv", "json", "pdf"}:
        raise HTTPException(status_code=422, detail="Format must be csv, json, or pdf.")
    try:
        source_id = scraper.CURRENT_SOURCE
        records = _records_for_response(scraper.LAST_RESULTS, source_id)
        path = scraper.EXPORT_DIR / "{0}_{1}.{2}".format(scraper.SOURCES[source_id]["type"], datetime.now().strftime("%Y%m%d_%H%M%S"), request.format)
        scraper.EXPORT_DIR.mkdir(exist_ok=True)
        if request.format == "csv":
            _export_csv(records, source_id, path)
        elif request.format == "json":
            payload = {"report": {"source": scraper.SOURCES[source_id]["name"], "source_url": scraper.SOURCES[source_id]["base_url"], "generated_at": datetime.now(timezone.utc).isoformat(), "currency": "INR", "record_count": len(records)}, "statistics": _report_stats(records, _stats()), "results": records}
            path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        else:
            _export_pdf(records, source_id, _stats(), path)
    except Exception as exc:
        raise _error(exc) from exc
    return {"format": request.format, "filename": path.name, "download_url": "/api/download/" + path.name}


@app.get("/api/download/{filename}")
def download(filename: str) -> FileResponse:
    export_dir = scraper.EXPORT_DIR.resolve()
    path = (export_dir / Path(filename).name).resolve()
    if path.parent != export_dir or not path.is_file():
        raise HTTPException(status_code=404, detail="Export file not found.")
    return FileResponse(path, filename=path.name, media_type="application/octet-stream")
