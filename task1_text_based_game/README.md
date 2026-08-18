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

Not implemented yet.

## practice/

Small scripts written while learning, kept on purpose:

- `demo1_def_vs_call.py` — proves that `def` defines but does not run
- `demo2_secret_dikhao.py` — shows the secret number and the raw
  `True`/`False` value behind each comparison
