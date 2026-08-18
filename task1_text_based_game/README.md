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
| `quiz_game.py` | Multiple-choice quiz | `for` loop — fixed number of questions |

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

1. The quiz has a fixed set of 5 multiple-choice questions.
2. Each question offers four options, labelled A, B, C and D.
3. A correct answer adds one point; a wrong answer reveals the correct option.
4. After the last question the program reports the score and the percentage.
5. Invalid input does not crash the game and does not skip the question.

### Run

```bash
python quiz_game.py
```

### Test cases

| Input | Expected behaviour | Reason |
|-------|--------------------|--------|
| `B` | Accepted, scored | Normal path |
| `b` | Accepted, scored | `.upper()` normalises the case |
| `  b  ` | Accepted, scored | `.strip()` removes surrounding spaces |
| `Z` | Error message, asks again | Not in `("A", "B", "C", "D")` |
| `hello` | Error message, asks again | Same range check |
| *(empty Enter)* | Error message, asks again | Empty string is not a valid choice |

Verified: a run answering `Z`, `hello`, *(empty)* and then `  b  ` on question 1
still scored that question once and did not skip it.

### Why a `for` loop here and a `while` loop in the guessing game

This is the main reason both games exist in this task.

| | `guessing_game.py` | `quiz_game.py` |
|---|---|---|
| Loop | `while True` | `for item in QUESTIONS` |
| Reason | The number of rounds is unknown until the player wins | The number of questions is fixed at 5 |

Rule of thumb: when the number of repetitions is known in advance, use `for`;
when it depends on a condition, use `while`.

### Design note — questions are data, not code

The questions live in a `QUESTIONS` list of dictionaries at the top of the file,
separate from the game logic. Adding or removing a question means editing that
list only — `total = len(QUESTIONS)` adjusts automatically and no other line
changes. Hard-coding each question inside the loop would have required copying
the same block of code for every new question.

### Input validation — different from the guessing game

The guessing game needs `try/except ValueError` because it converts the input
to an integer with `int()`, which can fail. The quiz game never converts
anything, so a membership test is enough:

```python
choice = raw.strip().upper()
if choice in VALID_CHOICES:
    return choice
```

Catching an exception where a simple check suffices would be the wrong tool.

## practice/

Small scripts written while learning, kept on purpose:

- `demo1_def_vs_call.py` — proves that `def` defines but does not run
- `demo2_secret_dikhao.py` — shows the secret number and the raw
  `True`/`False` value behind each comparison
