<div align="center">

# Cognifyz Technologies — Software Development Internship

**Arghya Mahajan** · B.Tech CSE (Cyber Security), SRM Institute of Science & Technology

![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tasks](https://img.shields.io/badge/Tasks-6%2F6%20complete-brightgreen?style=for-the-badge)
![Levels](https://img.shields.io/badge/Levels-Beginner%20%E2%86%92%20Advanced-orange?style=for-the-badge)

All six tasks across all three levels.
The internship requires a minimum of four.

</div>

---

## Tasks

| # | Level | Project | Folder | Status |
|:-:|---|---|---|:-:|
| 1 | Beginner | Text-Based Games — number guessing + JSON-driven quiz | [`task1_text_based_game/`](task1_text_based_game/) | ✅ |
| 2 | Beginner | Number Pattern Generator — 8 patterns incl. magic square & Ulam spiral | [`task2_number_pattern/`](task2_number_pattern/) | ✅ |
| 3 | Intermediate | Console Task Manager — full CRUD on a `Task` class | [`task3_task_manager_crud/`](task3_task_manager_crud/) | ✅ |
| 4 | Intermediate | Health Temperature Toolkit — C↔F plus fever, heat index, wind chill | [`task4_temperature_converter/`](task4_temperature_converter/) | ✅ |
| 5 | Advanced | Persistent Task Manager — JSON store + deadline reminders | [`task5_task_manager_persistent/`](task5_task_manager_persistent/) | ✅ |
| 6 | Advanced | Interactive Web Scraper — CLI + FastAPI + React dashboard | [`task6_web_scraper/`](task6_web_scraper/) | ✅ |

Har task ka apna README hai — screenshots, animated demos, design decisions aur jo bugs mile unke saath.

---

## What each task does

**Task 1 — Text-Based Games.** Do games. Number guessing (`while` loop, `try/except`) aur ek quiz jo apne sawaal ek JSON file se padhta hai — 30 questions, topic aur difficulty filter, random 5-of-N selection, high score file.

**Task 2 — Number Patterns.** Pyramid aur triangle se aage — **number spiral**, **magic square** (Siamese method), aur **Ulam prime spiral**. Har pattern property se verify kiya gaya, aankh se nahi: magic square ke saare row/column/diagonal sums barabar, spiral mein `1..n²` exactly ek baar, Ulam ke prime count sahi.

**Task 3 — Console Task Manager.** `Task` class ke saath poora CRUD. Priority, due date, overdue detection, auto-sorting. Ye task OOP introduce karta hai — aur *parallel arrays problem* dikhata hai jo class solve karti hai.

**Task 4 — Health Temperature Toolkit.** PDF ki requirement (C ↔ F) ke upar teen health tools. Body temperature check jo **measurement site** ke hisaab se adjust karta hai (bagal vs rectal), heat index (NOAA ka asli formula), aur wind chill (NWS). Har clinical number **cited** hai — Mayo Clinic, NIH StatPearls, NOAA, NWS.

**Task 5 — Persistent Task Manager.** Task 3 ka app, ab `tasks.json` mein save hota hai. Khulte hi briefing deta hai: kya overdue hai, kya aaj due hai, aur **pichhli visit ke baad kya badla**. `--check` mode Windows Task Scheduler se roz apne aap chal sakta hai.

**Task 6 — Interactive Web Scraper.** `requests` + `BeautifulSoup` se asli HTML scraping, ek FastAPI JSON layer, aur ek React dashboard. Terminal developers ke liye, browser users ke liye. HTTPS-only, domain allowlist, private-IP rejection, redirect validation, aur CSV/JSON/PDF export.

---

## Running the tasks

Tasks 1–5 ko kuch install nahi karna. Bas Python.

```bash
python task1_text_based_game/guessing_game.py
python task1_text_based_game/quiz_game.py
python task2_number_pattern/pattern_generator.py
python task3_task_manager_crud/task_manager.py
python task4_temperature_converter/temperature_converter.py
python task5_task_manager_persistent/task_manager.py
```

**Task 5** sirf reminder briefing bhi de sakta hai — isse Windows Task Scheduler mein daal sakte ho:

```bash
python task5_task_manager_persistent/task_manager.py --check
```

**Task 6** ko dependencies chahiye:

```bash
pip install -r task6_web_scraper/requirements.txt

# terminal version
python task6_web_scraper/book_scraper.py

# browser dashboard (pehli baar: cd task6_web_scraper/frontend && npm install)
.\task6_web_scraper\run.ps1      # Windows
./task6_web_scraper/run.sh       # Linux / macOS
```

Python version check:

```bash
python --version
```

Tasks 1–5 Python 3.6+ par chalte hain. Task 6 ke API layer ko 3.10+ chahiye (modern type syntax).

---

## Testing

Tasks 3, 4, 5 aur 6 ke saath automated checks hain. Task 6 ka suite repo mein hai:

```bash
python -m unittest discover -s task6_web_scraper/tests -v
```

```
Ran 38 tests
OK
```

Baaki tasks ke verification uske apne README mein documented hain — Task 3 ke 44 checks, Task 4 ke 72, Task 5 ke 110.

---

## Repository structure

```
cognifyz-internship/
├── README.md
├── .gitignore
├── NOTES.md                            <- concepts learned, in my own words
│
├── task1_text_based_game/
│   ├── README.md · guessing_game.py · quiz_game.py
│   ├── questions.json                  <- quiz bank (data, not code)
│   ├── assets/                         <- animated demos
│   └── practice/                       <- learning experiments, kept deliberately
│
├── task2_number_pattern/
│   ├── README.md · pattern_generator.py
│   └── assets/
│
├── task3_task_manager_crud/
│   ├── README.md · task_manager.py     <- Task class + CRUD, in memory
│   └── assets/
│
├── task4_temperature_converter/
│   ├── README.md · temperature_converter.py
│   └── assets/
│
├── task5_task_manager_persistent/
│   ├── README.md · task_manager.py     <- CRUD + tasks.json + reminders
│   └── assets/
│
└── task6_web_scraper/
    ├── README.md · requirements.txt
    ├── book_scraper.py                 <- scraping engine + CLI
    ├── api.py                          <- FastAPI wrapper
    ├── run.ps1 · run.sh                <- one-command startup with port guards
    ├── assets/                         <- dashboard screenshots
    ├── tests/                          <- 38 offline tests
    └── frontend/                       <- React + TypeScript + Vite dashboard
```

`practice/` folders mein chhote throwaway scripts hain jo koi concept seekhte waqt likhe gaye. Jaan-boojh kar rakhe hain — wo dikhate hain ki final code tak kaise pahuncha.

Runtime files (`tasks.json`, `highscores.json`, `exports/`, `node_modules/`, `dist/`) `.gitignore` mein hain — wo generated data hai, source nahi.

---

<div align="center">

**Arghya Mahajan** · [github.com/15Arghya2004](https://github.com/15Arghya2004)

</div>
