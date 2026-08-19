# Cognifyz IT Solutions — Software Development Internship

Python tasks completed as part of the Software Development Internship
at Cognifyz IT Solutions Pvt. Ltd.

**Author:** Arghya Mahajan
**Language:** Python 3
**Dependencies:** Standard library only, except Task 6 (`requests`, `beautifulsoup4`)

The internship requires a minimum of 4 out of 6 tasks. All 6 are being
attempted, one level at a time.

## Tasks

| Task | Level | Title | Folder | Status |
|------|-------|-------|--------|--------|
| 1 | Beginner | Basic Text-Based Game | `task1_text_based_game/` | Complete |
| 2 | Beginner | Number Pattern Generator | `task2_number_pattern/` | Complete |
| 3 | Intermediate | Console Task Manager (CRUD) | `task3_task_manager_crud/` | Complete |
| 4 | Intermediate | Temperature Converter | `task4_temperature_converter/` | Complete |
| 5 | Advanced | Persistent Task Manager (File I/O) | `task5_task_manager_persistent/` | Not started |
| 6 | Advanced | Interactive Web Scraper | `task6_web_scraper/` | Draft — needs live run |

Folders for tasks that have not been started yet do not exist in the
repository. They are listed above only to show the full plan.

## How to run

Every program is a standalone script. Nothing to install.

```bash
python task1_text_based_game/guessing_game.py
python task1_text_based_game/quiz_game.py
python task2_number_pattern/pattern_generator.py
python task3_task_manager_crud/task_manager.py
python task4_temperature_converter/temperature_converter.py
```

Task 6 needs two libraries first:

```bash
pip install -r task6_web_scraper/requirements.txt
python task6_web_scraper/book_scraper.py
```

Requires Python 3.6 or above. Check with:

```bash
python --version
```

## Repository structure

```
cognifyz-internship/
├── README.md
├── .gitignore
├── NOTES.md                        <- concepts learned, in my own words
├── task1_text_based_game/
│   ├── README.md
│   ├── guessing_game.py
│   ├── quiz_game.py
│   ├── questions.json              <- quiz question bank (data, not code)
│   ├── assets/                     <- demo recordings for the README
│   └── practice/                   <- small experiments, not submission code
│       ├── demo1_def_vs_call.py
│       └── demo2_secret_dikhao.py
├── task2_number_pattern/
│   ├── README.md
│   ├── pattern_generator.py
│   └── assets/
├── task3_task_manager_crud/
│   ├── README.md
│   └── task_manager.py             <- Task class + CRUD, in-memory list
├── task4_temperature_converter/
│   ├── README.md
│   └── temperature_converter.py
├── task5_task_manager_persistent/  <- placeholder, not started
└── task6_web_scraper/
    ├── README.md
    ├── requirements.txt
    └── book_scraper.py             <- needs `pip install requests beautifulsoup4`
```

The `practice/` folders hold small throwaway scripts written while learning
a concept. They are kept deliberately — they document how the final code
was arrived at.
