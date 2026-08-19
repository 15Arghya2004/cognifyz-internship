# Task 6 — Interactive Web Scraper

**Cognifyz Technologies · Software Development Internship · Level 3: Advanced**

> ⚠️ Yeh README temporary hai — baad mein detail + animation ke saath rewrite hoga.

> ⚠️ **Verification status:** parsing logic 30/30 offline tests pass karti hai, par
> **live site ke against abhi tak run nahi hui** — jis sandbox mein yeh likhi gayi
> uske paas internet nahi tha. Pehli baar chalane par option `5` (probe) chalao,
> wo bata dega ki har field sahi parse ho raha hai ya nahi.

## Install

Yeh pehla task hai jise external libraries chahiye:

```bash
pip install -r task6_web_scraper/requirements.txt
```

ya

```bash
pip install requests beautifulsoup4
```

## Run

```bash
python task6_web_scraper/book_scraper.py
```

## Kya karta hai

`books.toscrape.com` se book data laata hai — yeh site scraping practice ke
liye hi banayi gayi hai, iska `robots.txt` kisi page ko block nahi karta.

```
====================================================
  BOOK SCRAPER  -  Cognifyz Internship Task 6
  Source: https://books.toscrape.com
====================================================
  1. Catalogue browse karo (ek page)
  2. Title se search karo (kai pages)
  3. Last results par filter lagao
  4. Results CSV mein save karo
  5. Site structure probe karo (debug)
  0. Exit
```

Har book se nikalta hai: **title, price, rating (1-5), stock status, URL**.

## Engineering notes

- **Politeness** — har request ke beech 1 second ka gap, apna User-Agent set,
  20 second timeout. Server pe bojh nahi daalte.
- **Class names pe depend nahi karta.** Parser `h3 > a[title]` se shuru hota hai
  (poora title wahi milta hai), phir aas-paas ke container se price regex se aur
  rating `star` wale class-substring se nikaalta hai. Site ke CSS class rename
  ho jaayein to bhi parser kaam karta rahega — yeh cheez test se prove ki gayi hai.
- **Har network error user-friendly message banta hai** — timeout, connection
  fail, 404, koi aur status. Raw traceback kabhi nahi dikhta.
- **Library missing ho to saaf instruction milta hai**, `ImportError` traceback nahi.
- **Field na mile to `None`**, galat data nahi. `probe` mode batata hai kitne
  books mein kaun sa field mila.

## Testing

30/30 offline checks pass — asli site ke jaise HTML fixture par:

| Group | Kya check kiya |
|---|---|
| Normal parsing | title (full, `title` attribute se), price, rating word→number, stock, relative URL → absolute |
| **Resilience** | **saare CSS class rename karke bhi wahi data nikla** |
| Degraded page | price/rating missing → `None`, crash nahi, table phir bhi banta hai |
| Empty/garbage | khaali HTML, bina anchor ke `h3` → `[]`, exception nahi |
| Price regex | `£`, `$`, `€`, integer price, "free" → `None` |

## Files

```
task6_web_scraper/
├── README.md
├── requirements.txt
└── book_scraper.py
```
