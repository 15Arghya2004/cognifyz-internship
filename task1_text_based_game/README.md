<div align="center">

# 🎮 Task 1 — Text-Based Games

**Two console games written in pure Python — a number guessing game and a data-driven quiz.**

[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-3fb950?style=flat-square)](#-quick-start)
[![Status](https://img.shields.io/badge/Task%201-Complete-3fb950?style=flat-square)](#)
[![Internship](https://img.shields.io/badge/Cognifyz-Internship-1F3864?style=flat-square)](https://github.com/15Arghya2004/cognifyz-internship)

</div>

---

## 🚀 Quick Start

No installation. No `pip install`. No virtual environment. Just Python.

```bash
# 1. Repo clone karo
git clone https://github.com/15Arghya2004/cognifyz-internship.git

# 2. Is folder mein aao
cd cognifyz-internship/task1_text_based_game

# 3. Koi bhi game chalao
python guessing_game.py
python quiz_game.py
```

> **Requirement:** Python 3.6 or above. Check with `python --version`.
> On some systems the command is `python3` instead of `python`.

---

## 🎯 The Games

| Game | What it is | Core idea |
|------|-----------|-----------|
| 🔢 **`guessing_game.py`** | Guess a secret number between 1 and 100 | `while` loop — rounds are unlimited until you win |
| ❓ **`quiz_game.py`** | 5 random multiple-choice questions, pick topic & difficulty | `for` loop — question count is fixed |

---

## 🔢 Number Guessing Game

<div align="center">
  <img src="assets/guessing_demo.gif" alt="Guessing game demo" width="700">
</div>

**Kaise khelna hai** — computer 1 se 100 ke beech ek number sochta hai. Aap guess karo, wo batayega
zyada hai ya kam. Jeetne pe koshishon ki ginti dikhegi.

**Kya khaas hai**

- ✅ `hello`, `3.5`, khali Enter — kuch bhi daalo, game **crash nahi hota**
- ✅ `150` ya `-5` daalo to "range se bahar" — aur wo koshish **count nahi hoti**
- ✅ Upar wale demo mein 9 input diye gaye, par score **7 koshish** hi bata raha hai

```bash
python guessing_game.py
```

---

## ❓ Quiz Game

<div align="center">
  <img src="assets/quiz_demo.gif" alt="Quiz game demo" width="700">
</div>

**Kaise khelna hai** — topic chuno, difficulty chuno, phir 5 random sawaal aayenge.
Har sahi jawab ka 1 point. Aakhir mein score, percentage aur high score.

**Kya khaas hai**

- 🎲 **Har game alag** — 30 sawaal ke bank mein se 5 random, bina repeat ke
- 🏷️ **Topic filter** — Python / General Knowledge / All
- 📊 **Difficulty filter** — easy / medium / hard / All
- 🏆 **High score** — har topic+difficulty ka best score save rehta hai
- 📝 **Sawaal alag file mein** — code chhue bina naya quiz bana sakte ho
- ✅ Galat input (`Z`, `hello`, khali) pe sawaal **skip nahi hota**

```bash
python quiz_game.py
```

---

## 📝 Apne Sawaal Daalo

Sawaal `questions.json` mein hain — **code ke andar nahi**. Naya quiz banane ke liye
bas is file mein sawaal add/badal do. Python file ko haath lagane ki zaroorat nahi.

```json
{
  "name": "Mera naya question bank",
  "version": 1,
  "questions": [
    {
      "id": "net-e-01",
      "topic": "Networking",
      "difficulty": "easy",
      "question": "HTTP ka default port kaunsa hai?",
      "options": { "A": "21", "B": "80", "C": "443", "D": "22" },
      "answer": "B"
    }
  ]
}
```

**Har sawaal mein ye 6 cheezein honi chahiye:**

| Field | Matlab |
|-------|--------|
| `id` | Unique naam, jaise `net-e-01` |
| `topic` | Koi bhi topic — menu mein **apne aap** aa jayega |
| `difficulty` | `easy` / `medium` / `hard` (ya jo aap chaho) |
| `question` | Sawaal ka text |
| `options` | Exactly chaar — `A`, `B`, `C`, `D` |
| `answer` | Sahi option ka letter |

> 💡 Naya topic daaloge to menu mein wo **khud dikhne lagega** — code badalne ki zaroorat nahi.
> Menu bank se banta hai, hardcoded nahi hai.
>
> ⚠️ Koi sawaal galat format mein hua to game crash nahi hoga — wo sawaal skip ho jayega
> aur baaki game normally chalega.

**Bundled bank:** 30 sawaal — 2 topics × 3 difficulties × 5 sawaal.

---

## 📂 Files

```
task1_text_based_game/
├── guessing_game.py     # Game 1
├── quiz_game.py         # Game 2
├── questions.json       # Quiz ka question bank (data)
├── highscores.json      # Khelne par khud banti hai (git mein nahi jaati)
├── assets/              # README ke demo GIFs
└── practice/            # Seekhte waqt likhi chhoti scripts
    ├── demo1_def_vs_call.py
    └── demo2_secret_dikhao.py
```

---

<details>
<summary><h2>📋 Internship Requirement (click to expand)</h2></summary>

From the internship task document:

> Develop a simple text-based game, such as a quiz or a guessing game.
> Define the game rules, use conditional statements to control the game flow,
> then test and debug the program for correctness.

Both games satisfy the requirement independently.

| File | Game | Main concept |
|------|------|--------------|
| `guessing_game.py` | Number guessing (1–100) | `while` loop — unknown number of rounds |
| `quiz_game.py` | Multiple-choice quiz, data-driven | `for` loop — fixed number of questions |

</details>

<details>
<summary><h2>🧪 Test Cases (click to expand)</h2></summary>

### Guessing game

| Input | Expected behaviour | Reason |
|-------|--------------------|--------|
| `50` | "too low" or "too high" | Normal path |
| `hello` | Error message, asks again | `ValueError` caught |
| `3.5` | Error message, asks again | `int()` rejects decimal strings |
| `150` | "out of range", attempt NOT counted | Range check runs before the counter |
| `-5` | "out of range" | `guess < 1` is true |
| *(empty Enter)* | Error message | Empty string is not an integer |

### Quiz game

| Input / condition | Expected behaviour | Reason |
|-------------------|--------------------|--------|
| `B` | Accepted, scored | Normal path |
| `b` / `  b  ` | Accepted, scored | `.upper()` and `.strip()` normalise the input |
| `Z`, `hello`, *(empty)* | Error message, asks again | Not in `("A","B","C","D")` |
| Menu input `0`, `99`, `abc` | Error message, asks again | Range check plus `int()` conversion |
| Two runs, same filter | Different question order/set | `random.sample()` per game |
| `questions.json` missing | Clear message, no traceback | `FileNotFoundError` handled |
| `questions.json` malformed | Message with the parse error | `json.JSONDecodeError` handled |
| A question missing `answer` | That question skipped, game continues | Validated on load |
| Filter matches fewer than 5 | Plays with what exists, states the count | Guard before `random.sample()` |

Verified: across 200 simulated selections no game contained a duplicate question.
All 14 Python questions in the bank were checked by executing the expressions they ask about.

</details>

<details>
<summary><h2>🐛 Bugs Found and Fixed (click to expand)</h2></summary>

**Bug 1 — type mismatch.** `input()` always returns a **string**, never a number.
The first version compared the raw string against the secret integer, which raises:

```
TypeError: '<' not supported between instances of 'str' and 'int'
```

Fixed by converting with `int()`, and wrapping that conversion in `try/except ValueError`
so non-numeric input is handled instead of crashing.

**Bug 2 — attempt counter in the wrong place.** The counter was originally incremented
*before* the range check, so out-of-range input inflated the attempt count without being a
real guess. Moving `attempts += 1` to after the `continue` fixed it. Verified: a run with
6 inputs, 3 of them invalid, reported 3 attempts.

This second bug did not crash anything — it just produced a wrong number.
Those are the harder ones to notice.

</details>

<details>
<summary><h2>🏗️ Design Notes (click to expand)</h2></summary>

### Why a `for` loop here and a `while` loop there

This is the main reason both games exist in this task.

| | `guessing_game.py` | `quiz_game.py` |
|---|---|---|
| Loop | `while True` | `for item in selected` |
| Reason | The number of rounds is unknown until the player wins | The number of questions is fixed at 5 |

Rule of thumb: when the number of repetitions is known in advance, use `for`;
when it depends on a condition, use `while`.

### Questions are data, not code

Keeping the questions in a JSON file rather than a Python list means the program never has
to change when the content changes. `total = len(selected)` adjusts automatically, and the
menus are derived from the file rather than hard-coded, so the data file remains the single
source of truth.

### `random.sample()` rather than `random.choice()`

`random.choice()` picks from the whole pool every time, so calling it five times can return
the same question twice. `random.sample()` draws without replacement, which is what a quiz
needs. Because `random.sample()` raises `ValueError` when asked for more items than the pool
holds, the pool size is checked first and a shuffled copy is used when the filter matches
fewer than five questions.

### Input validation — two different tools, on purpose

The answer prompt only needs a membership test, because the set of valid answers is known
up front:

```python
choice = raw.strip().upper()
if choice in VALID_CHOICES:
    return choice
```

The menu prompt also has to convert text to a number, and that conversion can fail, so it
needs both:

```python
try:
    picked = int(raw)             # Python's rule: can this text become a number?
except ValueError:
    ...
if 1 <= picked <= len(choices):   # our rule: is it a valid menu position?
    ...
```

Use `if` when the rule can be checked in advance; use `try/except` when the only way to know
is to attempt the operation.

### File paths

Both data files are resolved relative to the script's own location:

```python
HERE = Path(__file__).parent
QUESTIONS_FILE = HERE / "questions.json"
```

This means the game can be launched from any working directory, not just from inside
`task1_text_based_game/`.

</details>

---

<div align="center">

**Part of the [Cognifyz Software Development Internship](https://github.com/15Arghya2004/cognifyz-internship)**
Built by [Arghya Mahajan](https://github.com/15Arghya2004)

</div>
