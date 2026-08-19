# Cognifyz IT Solutions — Software Development Internship

Python tasks completed as part of the Software Development Internship
at Cognifyz IT Solutions Pvt. Ltd.

**Author:** Arghya Mahajan
**Language:** Python 3
**Dependencies:** None (Python standard library only)

The internship requires a minimum of 4 out of 6 tasks. This repository
contains the 4 tasks listed below.

## Tasks

| Task | Title | Folder | Status |
|------|-------|--------|--------|
| 1 | Basic Text-Based Game | `task1_text_based_game/` | Complete |
| 2 | Number Pattern Generator | `task2_number_pattern/` | Not Started |
| 3 | Console Task Manager (CRUD) | `task3_task_manager_crud/` | Not Started |
| 5 | Persistent Task Manager (File I/O) | `task5_task_manager_persistent/` | Not Started |

## How to run

Every program is a standalone script. Nothing to install.

```bash
python task1_text_based_game/guessing_game.py
python task1_text_based_game/quiz_game.py
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
│   └── practice/                   <- small experiments, not submission code
│       ├── demo1_def_vs_call.py
│       └── demo2_secret_dikhao.py
├── task2_number_pattern/
├── task3_task_manager_crud/
└── task5_task_manager_persistent/
```

The `practice/` folders hold small throwaway scripts written while learning
a concept. They are kept deliberately — they document how the final code
was arrived at.
