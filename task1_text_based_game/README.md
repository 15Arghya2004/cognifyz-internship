# Task 1 — Basic Text-Based Game

## Requirement (from the internship task document)

Develop a simple text-based game, such as a quiz or a guessing game.
Define the game rules, use conditional statements to control the game flow,
then test and debug the program for correctness.

## What is implemented

Two separate games, both satisfying the requirement:

| File | Game | Main concept |
|------|------|--------------|
| `guessing_game.py` | Number guessing (1–100) | `while` loop — unknown number of rounds |
| `quiz_game.py` | Multiple-choice quiz, data-driven | `for` loop — fixed number of questions |

`quiz_game.py` reads its questions from `questions.json`. The questions are
data, not code — a different question set can be dropped in without editing
the program.

## Game 1 — Number Guessing Game

### Rules

1. The computer picks a secret number between 1 and 100.
2. The player enters a guess.
3. The program replies "too low" or "too high".
4. On a correct guess the game ends and reports the number of attempts.
5. Invalid input does not crash the game and does not count as an attempt.

### Run

```bash
python guessing_game.py
```

### Test cases

| Input | Expected behaviour | Reason |
|-------|--------------------|--------|
| `50` | "too low" or "too high" | Normal path |
| `hello` | Error message, asks again | `ValueError` caught |
| `3.5` | Error message, asks again | `int()` rejects decimal strings |
| `150` | "out of range", attempt NOT counted | Range check runs before the counter |
| `-5` | "out of range" | `guess < 1` is true |
| *(empty Enter)* | Error message | Empty string is not an integer |

### Bugs found and fixed during development

**Bug 1 — type mismatch.** `input()` always returns a **string**, never a
number. The first version compared the raw string against the secret
integer, which raises:

```
TypeError: '<' not supported between instances of 'str' and 'int'
```

Fixed by converting with `int()`, and wrapping that conversion in
`try/except ValueError` so non-numeric input is handled instead of
crashing.

**Bug 2 — attempt counter in the wrong place.** The counter was originally
incremented *before* the range check, so out-of-range input inflated the
attempt count without being a real guess. Moving `attempts += 1` to after
the `continue` fixed it. Verified: a run with 6 inputs, 3 of them invalid,
reported 3 attempts.

This second bug did not crash anything — it just produced a wrong number.
Those are the harder ones to notice.

## Game 2 — Quiz Game

### Rules

1. Questions live in `questions.json`, not inside the program.
2. The player selects a topic and a difficulty (or `All` for either).
3. Each game draws **5 random questions** from the filtered pool, with no
   repeats inside a single game.
4. A correct answer adds one point; a wrong answer reveals the correct option.
5. Invalid input never crashes the game and never skips a question.
6. The best score for each topic + difficulty combination is stored in
   `highscores.json`.

### Run

```bash
python quiz_game.py
```

`questions.json` must sit next to `quiz_game.py`. The program resolves both
data files relative to its own location, so it can be run from any directory.

### Question bank format

```json
{
  "name": "Default bank — Python basics & general knowledge",
  "version": 1,
  "questions": [
    {
      "id": "py-e-01",
      "topic": "Python",
      "difficulty": "easy",
      "question": "Python mein input() function kya return karta hai?",
      "options": { "A": "Integer", "B": "String", "C": "Float", "D": "Boolean" },
      "answer": "B"
    }
  ]
}
```

To use a different question set, replace `questions.json` with another file
in this shape. No code changes are required. The topic and difficulty menus
are built from whatever values appear in the file, so a bank containing a new
topic will show that topic in the menu automatically.

The bundled bank holds 30 questions — 5 for each combination of two topics
(Python, General Knowledge) and three difficulties (easy, medium, hard).

### Test cases

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

Verified: across 200 simulated selections no game contained a duplicate
question. All 14 Python questions in the bank were checked by executing the
expressions they ask about.

### Why a `for` loop here and a `while` loop in the guessing game

This is the main reason both games exist in this task.

| | `guessing_game.py` | `quiz_game.py` |
|---|---|---|
| Loop | `while True` | `for item in selected` |
| Reason | The number of rounds is unknown until the player wins | The number of questions is fixed at 5 |

Rule of thumb: when the number of repetitions is known in advance, use `for`;
when it depends on a condition, use `while`.

### Design note — questions are data, not code

Keeping the questions in a JSON file rather than a Python list means the
program never has to change when the content changes. `total = len(selected)`
adjusts automatically, and the menus are derived from the file rather than
hard-coded, so the data file remains the single source of truth.

### Design note — `random.sample()` rather than `random.choice()`

`random.choice()` picks from the whole pool every time, so calling it five
times can return the same question twice. `random.sample()` draws without
replacement, which is what a quiz needs. Because `random.sample()` raises
`ValueError` when asked for more items than the pool holds, the pool size is
checked first and a shuffled copy is used when the filter matches fewer than
five questions.

### Input validation — two different tools, on purpose

The answer prompt only needs a membership test, because the set of valid
answers is known up front:

```python
choice = raw.strip().upper()
if choice in VALID_CHOICES:
    return choice
```

The menu prompt also has to convert text to a number, and that conversion can
fail, so it needs both:

```python
try:
    picked = int(raw)          # Python's rule: can this text become a number?
except ValueError:
    ...
if 1 <= picked <= len(choices):   # our rule: is it a valid menu position?
    ...
```

Use `if` when the rule can be checked in advance; use `try/except` when the
only way to know is to attempt the operation.

## practice/

Small scripts written while learning, kept on purpose:

- `demo1_def_vs_call.py` — proves that `def` defines but does not run
- `demo2_secret_dikhao.py` — shows the secret number and the raw
  `True`/`False` value behind each comparison
