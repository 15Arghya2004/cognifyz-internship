<div align="center">

# 🕸️ Task 6 — Interactive Web Scraper

**Cognifyz Technologies · Software Development Internship · Level 3**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-JSON%20API-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React%20%2B%20Vite-Dashboard-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Checks](https://img.shields.io/badge/Tests-38%2F38%20pass-brightgreen?style=for-the-badge)

Ek asli web scraper — **terminal se bhi chalta hai, browser dashboard se bhi.**
Scraping `requests` + `BeautifulSoup` se hoti hai. Koi API shortcut nahi.

</div>

---

## 🚀 Quick Start

**1. Python dependencies:**

```bash
pip install -r task6_web_scraper/requirements.txt
```

**2. Dashboard dependencies:**

```bash
cd task6_web_scraper/frontend
npm install
```

**3. Chalao — ek command:**

```powershell
.\task6_web_scraper\run.ps1        # Windows
```

```bash
./task6_web_scraper/run.sh         # Linux / macOS
```

Backend `http://localhost:8000` par, dashboard `http://localhost:5173` par khulega.

**Sirf terminal chahiye? Dashboard ki zaroorat hi nahi:**

```bash
python task6_web_scraper/book_scraper.py
```

---

## 🖥️ Dashboard

<div align="center">

![Dashboard with Books results](assets/dashboard-books.jpg)

*Books to Scrape se 20 records — live GBP→INR conversion ke saath*

</div>

Workflow seedha hai, aur user ko `requests`, `BeautifulSoup`, ya FastAPI kuch samajhne ki zaroorat nahi:

```
Source chuno  →  Health verify  →  Scrape  →  Results  →  Filter  →  Export
```

| Panel | Kya karta hai |
|---|---|
| **Source rail** | Books ya Quotes chuno — switch karte hi purana data clear ho jaata hai |
| **Health checklist** | HTTPS, domain, HTTP status, HTML structure, records extracted, required fields — har step alag se pass/fail |
| **Scrape control** | `CURRENT` (ek page) · `PAGES` (jitne chaho) · `ALL` (safety limit tak) |
| **Result register** | Source-aware table — Books ke liye price/rating/stock, Quotes ke liye author/tags |
| **Filters** | Title/quote search, max price, min rating, category, in-stock only, author, tag |
| **Exports** | CSV · JSON · PDF — hamesha **current filtered set** par |
| **Structure probe** | Kisi bhi safe HTTPS page ke headings, links, forms, tables gin kar batata hai |

---

## 🌐 Supported Sources

| Source | URL | Fields | Page ceiling |
|---|---|---|:---:|
| Books to Scrape | `https://books.toscrape.com/` | title, price, rating, availability, URL, category | 50 |
| Quotes to Scrape | `https://quotes.toscrape.com/` | quote, author, tags, author URL | 10 |

Dono sites **scraping practice ke liye hi banayi gayi hain** — inka `robots.txt` kisi page ko block nahi karta.

> **Ek imaandar baat:** Books to Scrape ek **global practice catalogue** hai, Indian book catalogue nahi. Koi verified Indian source nahi mil paaya, isliye koi Indian book ya INR price **banaya nahi gaya**. Jo hai wahi likha hai.

A source ko **verified** tabhi kehte hain jab **isi run mein** uske saare health steps pass ho jayein. Sirf select karne se verified nahi hota, aur har scrape se pehle verification dobara chalti hai.

---

## 🔒 Safety

Scraper sirf wahi karta hai jo karna chahiye:

| Control | Kya rokta hai |
|---|---|
| HTTPS-only | plain HTTP requests |
| Domain allowlist | registered source ke bahar ka koi bhi host |
| localhost / loopback reject | `localhost`, `127.0.0.1`, `::1` |
| Private / link-local / reserved IP reject | internal network scanning |
| DNS resolution check | aisa hostname jo andar ki IP par resolve hota ho |
| **Redirect validation** | redirect ke baad ki **final URL** bhi wahi rules se guzarti hai |
| Timeout · retries · backoff | 20s timeout, 2 retries, badhta hua gap |
| Request delay | har request ke beech 1 second — server par bojh nahi |
| Safe download path | export folder ke bahar koi file serve nahi hoti |

Errors user ko **padhne laayak message** ke roop mein milte hain — raw Python traceback kabhi nahi.

---

## 💱 Currency

Books ke prices **GBP mein hi rehte hain** (source wahi deta hai), aur uske saath live INR value bhi dikhti hai. Rate [Frankfurter](https://www.frankfurter.app/) se aata hai, hardcode **bilkul nahi**.

- Rate ek baar fetch hokar cache ho jaata hai
- Fail ho jaye to dobara koshish hoti hai (5 minute cooldown ke saath)
- Kabhi na mile to dashboard saaf kehta hai **"INR conversion unavailable"** — jhootha number nahi dikhata

*Live run mein observe kiya gaya:* `£51.77 → ₹6720.26`, yaani `1 GBP ≈ ₹129.81`.

---

## 📤 Exports

Files yahan banti hain: `task6_web_scraper/exports/`

| Format | Kya milta hai |
|---|---|
| **CSV** | flat, machine-readable — `title, price_inr, price, original_currency, rating, availability, category, url` |
| **JSON** | structured report — `{ report, statistics, results }` |
| **PDF** | professional report — summary metrics, results table, repeating headers, timestamps, page numbers |

Teenon **current filtered results** par chalte hain, poore dataset par nahi.

---

## 🧪 Testing

```bash
python -m unittest discover -s task6_web_scraper/tests -v
python -m py_compile task6_web_scraper/book_scraper.py
python -m py_compile task6_web_scraper/api.py
```

```
Ran 38 tests
OK
```

Saare tests **offline** chalte hain — HTML fixtures aur mocks se, internet ki zaroorat nahi.

<details>
<summary><b>38 tests kya cover karte hain</b></summary>

| Group | Coverage |
|---|---|
| Parsing | Books aur Quotes fields, relative → absolute URLs, pagination, khaali HTML |
| Validation | required fields, invalid records, khaali source health fail |
| URL safety | HTTPS-only, domain allowlist, localhost, loopback, private IP |
| Fetch | HTML result + request counting, **redirect to another domain reject**, same-domain redirect allow |
| Input | non-finite values (`nan`, `inf`, `-inf`) reject |
| Export | CSV/JSON content, directory auto-create |
| Source state | switch karne par results/stats clear, failed health par verification clear |
| **API contract** | currency enrichment, JSON/PDF export shape, source switch isolation |
| **Regressions** | results-before-scrape, zero-match filter, clear-filters recovery, export messages, FX retry |

</details>

---

## 🔌 API Contract

Dashboard scraping khud nahi karta — sab kuch isi API se hota hai, aur API wahi `book_scraper.py` engine wrap karta hai.

| Method | Endpoint | Kaam |
|---|---|---|
| `GET` | `/api/health` | service alive check |
| `GET` | `/api/sources` | source list + current source |
| `POST` | `/api/sources/{id}/verify` | health check chalao, step-by-step result |
| `POST` | `/api/scrape` | `current` / `custom` / `all` mode mein scrape |
| `POST` | `/api/filter` | scraped dataset par in-memory filter |
| `GET` | `/api/results` | current result set |
| `POST` | `/api/probe` | kisi safe HTTPS page ka structure |
| `POST` | `/api/export` | CSV / JSON / PDF banao |
| `GET` | `/api/download/{filename}` | export file securely serve karo |

Har endpoint **hamesha valid JSON** deta hai — success par bhi, error par bhi. Errors readable message ke saath aate hain.

---

<details>
<summary><b>🐛 Jo asli bugs pakde aur theek kiye (click karo)</b></summary>

Ye project ka sabse seekhne wala hissa raha. Har bug asli tha, reproduce hua, aur uske liye test likha gaya.

### 1. Redirect ke baad ka URL check nahi ho raha tha — *security*

Purana code request bhejne se **pehle** URL validate karta tha, par redirect ke baad ki **final URL** check nahi karta tha. Matlab: allowed source → redirect → bahar ka domain, aur uska data chupchaap parse ho jaata.

**Fix:** `response.url` ab usi safety system se guzarti hai. Same-domain redirect allowed, bahar wala reject.

### 2. `"Unexpected end of JSON input"` — *frontend contract*

Dashboard startup par yahi error dikhta tha. Frontend ka shared helper ye karta tha:

```ts
const data = await response.json();          // pehle parse
if (!response.ok) throw new Error(...);      // phir status check
```

Backend band ho to **Vite proxy `HTTP 502` aur 0-byte body** deta hai (ye measure karke confirm kiya). Khaali body par `.json()` `SyntaxError` phenkta hai, aur asli 502 kahin kho jaata hai.

**Fix:** pehle body ko text ki tarah padho, JSON parse sirf tab karo jab body khaali na ho, aur non-OK par backend ka apna message dikhao. Ab backend band ho to seedha likha aata hai:

> *"Backend unavailable. Make sure the scraper API is running on port 8000."*

### 3. Filter se zero result = user phans jaata tha

Filter agar kuch match na kare to backend `LAST_RESULTS` ko khaali kar deta tha, aur guard `if not LAST_RESULTS` par tha. Iska matlab **"Clear filters" bhi 409 de deta tha** — *"Scrape results before filtering."* User ko dobara scrape karna padta.

**Fix — invariant saaf kiya:**

```
_base_results  =  jo scrape hua (nahi badalta)
LAST_RESULTS   =  jo abhi dikh raha hai (filter se badalta hai)
```

"Scrape hua kya" ab `_base_results` se poocha jaata hai. Export ke do alag message bhi hain — *"scrape pehle karo"* aur *"filter kuch match nahi kar raha"*.

Live testing mein iska **doosra aadha hissa** bhi mila: frontend ke saare filter controls `disabled={!records.length}` par the, to zero-match ke baad search box, Filter, Apply aur Clear — chaaron **dead** ho jaate the. Wahi invariant frontend mein bhi lagaya (`disabled={!stats}`).

<div align="center">

![Zero match filter state](assets/zero-match-filter.jpg)

*Ab zero-match apna alag state dikhata hai — "20 records collected · 0 matching the current filter" — aur Clear filters kaam karta hai*

</div>

### 4. Exchange rate ek baar fail hua to hamesha ke liye band

`attempted` flag request se **pehle** set hota tha aur failure par kabhi clear nahi hota tha. Ek network blip = poore process ke liye INR band.

**Fix:** cache successful rate ko rakhta hai, failure 5 minute baad dobara try hoti hai.

### 5. Purana backend chupchaap frontend ko serve kar raha tha

Agar port 8000 pehle se busy ho, to naya uvicorn bind fail karta tha (error sirf uski window mein), aur Vite **purane** backend se baat karta rehta tha — purane API contract ke saath.

**Fix:** `run.ps1` aur `run.sh` ab **8000 aur 5173 dono check karte hain**, PID batate hain, aur start hone se mana kar dete hain:

```
Port 8000 is already in use, so the backend (uvicorn) cannot start cleanly.
  Held by PID 6328 (python3)
  Stop it with:  kill 6328

Startup cancelled so the dashboard does not attach to an old backend.
```

### 6. Text export mein khaali description `None` ban jaata tha

`value if value != "" else None` har khaali field ko `None` bana deta tha. Par khaali **description** ka matlab `None` nahi, `""` hai. Saath mein `data.get("description", "")` bhi galat tha — `get` default sirf tab deta hai jab **key hi na ho**, value `None` hone par nahi.

**Sabak:** `None` aur `""` ek cheez nahi hain.

</details>

<details>
<summary><b>⚙️ Design decisions</b></summary>

- **Ek hi readable file mein scraper engine** — koi manager class, adapter framework, ya factory pattern nahi. Flow upar se neeche padha ja sakta hai: constants → model → fetching → parsing → display → actions → menu.
- **API scraper ko wrap karta hai, dohrata nahi.** React mein ek line bhi scraping logic nahi hai.
- **CLI zinda hai.** Dashboard usko replace nahi karta — dono ek hi engine par chalte hain.
- **Har scrape se pehle verification.** Site badal jaye to scrape shuru hi nahi hota.
- **Filter server-side, scraped data par** — dobara request nahi jaati, site par bojh nahi padta.
- **Statistics asli hain** — pages, HTTP requests, valid/invalid records, elapsed time. Koi banaya hua metric nahi.

</details>

---

## 📁 Files

```
task6_web_scraper/
├── README.md
├── requirements.txt
├── book_scraper.py            <- scraping engine + CLI (source of truth)
├── api.py                     <- FastAPI wrapper around the engine
├── run.ps1 / run.sh           <- one-command startup, with port guards
├── assets/                    <- dashboard screenshots
├── exports/                   <- generated CSV/JSON/PDF (gitignored)
├── tests/
│   ├── test_scraper.py
│   └── test_api.py
└── frontend/
    ├── package.json
    ├── vite.config.ts         <- proxies /api to port 8000
    └── src/
        ├── main.tsx           <- the whole dashboard
        └── styles.css
```

---

## ⚠️ Limitations

- Sirf do registered sources poori tarah supported hain. Custom URL **safe structure probe** ke liye hai, automatic scraping ke liye nahi.
- Koi database, cache, ya concurrency nahi — jaan-boojh kar, kyunki ye ek internship task hai.
- Dono practice sites ka HTML badal jaye to parser update karna padega. Health check us case ko pakad lega.
- Server-side state single-process hai — ek hi result set sabhi browser tabs ke liye.

<div align="center">

**Arghya Mahajan** · [github.com/15Arghya2004](https://github.com/15Arghya2004)

</div>
