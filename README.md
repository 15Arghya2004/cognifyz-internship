<div align="center">

# Cognifyz Technologies — Software Development Internship

**Arghya Mahajan** · B.Tech CSE (Cyber Security) · SRM Institute of Science & Technology

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

![Tasks](https://img.shields.io/badge/Tasks-6%20of%206-brightgreen?style=flat-square)
![Required](https://img.shields.io/badge/Required-only%204-lightgrey?style=flat-square)
![Levels](https://img.shields.io/badge/Levels-Beginner%20→%20Advanced-orange?style=flat-square)
![Install](https://img.shields.io/badge/Tasks%201–5-zero%20dependencies-success?style=flat-square)

### All six tasks · three levels · each with its own README

![All six tasks running](assets/showreel.gif)

</div>

---

## 🚀 Start in 60 seconds

```bash
git clone https://github.com/15Arghya2004/cognifyz-internship.git
cd cognifyz-internship
python task1_text_based_game/quiz_game.py
```

Tasks 1 through 5 need **nothing installed** — just Python 3.6 or above. Only Task 6 has additional dependencies.

---

## 📋 Tasks

| # | Level | Project | In one line |
|:-:|:-:|---|---|
| **1** | 🟢 Beginner | [Text-Based Games](task1_text_based_game/) | Number guessing game and a JSON-driven quiz |
| **2** | 🟢 Beginner | [Number Patterns](task2_number_pattern/) | Eight patterns including spiral, magic square, and Ulam prime spiral |
| **3** | 🟡 Intermediate | [Task Manager (CRUD)](task3_task_manager_crud/) | Full CRUD around a `Task` class |
| **4** | 🟡 Intermediate | [Health Temperature Toolkit](task4_temperature_converter/) | C↔F converter with fever, heat index and wind chill guidance |
| **5** | 🔴 Advanced | [Persistent Manager + Reminders](task5_task_manager_persistent/) | JSON-backed store with deadline briefing |
| **6** | 🔴 Advanced | [Interactive Web Scraper](task6_web_scraper/) | CLI, FastAPI service and a React dashboard |

The internship requirement was **any four tasks.** All six are included.

---

## 🔍 What each task does

<details open>
<summary><b>🟢 Level 1 — Beginner</b></summary>

**Task 1 · Text-Based Games** — Two games. The number guessing game demonstrates a `while` loop and `try/except` for input validation. The quiz reads a bank of 30 questions from a **JSON file**, supports topic and difficulty filters, picks five random questions per session, and persists high scores.

**Task 2 · Number Patterns** — Goes beyond the standard pyramid. Includes a **number spiral**, a **magic square** (Siamese method), and the **Ulam prime spiral**. Each pattern is **verified by its mathematical properties**, not by eye — every row, column and diagonal of the magic square must sum to the same value, and the spiral must contain each number from `1..n²` exactly once.

</details>

<details open>
<summary><b>🟡 Level 2 — Intermediate</b></summary>

**Task 3 · Console Task Manager** — The first object-oriented task. Priority, due date, overdue detection and automatic sorting. The README explains the *parallel-arrays problem* and shows how introducing a class eliminates it.

**Task 4 · Health Temperature Toolkit** — The task brief only required C↔F conversion. This project extends that with three health tools: a body-temperature check that **adjusts for the measurement site** (armpit vs rectal, for example), a heat-index calculator (NOAA formula), and a wind-chill calculator (NWS formula). **Every clinical value is cited** — Mayo Clinic, NIH StatPearls, NOAA and NWS.

</details>

<details open>
<summary><b>🔴 Level 3 — Advanced</b></summary>

**Task 5 · Persistent Manager + Reminders** — Task 3's application, now persisting to `tasks.json`. On every launch it presents a briefing: what is overdue, what is due today, and **what has changed since the last visit**. `--check` mode is designed to run daily under Windows Task Scheduler.

**Task 6 · Interactive Web Scraper** — Real HTML scraping (`requests` + `BeautifulSoup`), a FastAPI JSON layer, and a React dashboard. **For terminal users and browser users alike.** HTTPS-only, domain allowlist, private-IP rejection, redirect validation, and CSV / JSON / PDF exports. 38 tests.

</details>

---

## ▶️ Commands to run each task

```bash
# Level 1
python task1_text_based_game/guessing_game.py
python task1_text_based_game/quiz_game.py
python task2_number_pattern/pattern_generator.py

# Level 2
python task3_task_manager_crud/task_manager.py
python task4_temperature_converter/temperature_converter.py

# Level 3
python task5_task_manager_persistent/task_manager.py
python task5_task_manager_persistent/task_manager.py --check   # briefing only
```

**Task 6** requires dependencies:

```bash
pip install -r task6_web_scraper/requirements.txt

python task6_web_scraper/book_scraper.py        # terminal version
```

For the browser dashboard (one-time `cd task6_web_scraper/frontend && npm install`):

```powershell
.\task6_web_scraper\run.ps1      # Windows
```

```bash
./task6_web_scraper/run.sh       # Linux / macOS
```

---

## ✅ Testing

Every task ships with its own verification — no assumptions.

| Task | Checks | What is verified |
|:-:|:-:|---|
| 2 | property-based | magic square sums, spiral completeness, prime counts |
| 3 | 44 | CRUD, overdue logic, ID reuse, date validation |
| 4 | 72 | known reference points, NWS chart cells, formula validity ranges |
| 5 | 110 | escaping, atomic writes, corrupt-file recovery, briefing engine |
| 6 | **38** | parsing, URL safety, redirect rejection, API contract, regressions |

Task 6's suite lives in the repository and runs entirely offline:

```bash
python -m unittest discover -s task6_web_scraper/tests -v
# Ran 38 tests — OK
```

---

## 📁 Structure

```
cognifyz-internship/
├── README.md                    ← you are here
├── NOTES.md                     ← concepts learned, in my own words
├── assets/showreel.gif
│
├── task1_text_based_game/       README · guessing_game.py · quiz_game.py · questions.json
├── task2_number_pattern/        README · pattern_generator.py
├── task3_task_manager_crud/     README · task_manager.py
├── task4_temperature_converter/ README · temperature_converter.py
├── task5_task_manager_persistent/ README · task_manager.py
└── task6_web_scraper/           README · book_scraper.py · api.py · tests/ · frontend/
```

Every task folder ships with its own **README and animated demo**.
The `practice/` folders contain the small scripts written while learning — kept deliberately, they show the path from first attempt to the final code.

Runtime files (`tasks.json`, `highscores.json`, `exports/`, `node_modules/`, `dist/`) are covered by `.gitignore` — these are generated data, not source.

---

<div align="center">

**Arghya Mahajan**
[GitHub](https://github.com/15Arghya2004) · [LinkedIn](https://www.linkedin.com/in/arghya-mahajan)

</div>
