<div align="center">

# 🔺 Task 2 — Number Pattern Generator

**Eight number patterns, from simple nested loops to spiral algorithms and magic squares.**

[![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-3fb950?style=flat-square)](#-quick-start)
[![Patterns](https://img.shields.io/badge/patterns-8-8957e5?style=flat-square)](#-the-patterns)
[![Status](https://img.shields.io/badge/Task%202-Complete-3fb950?style=flat-square)](#)

</div>

---

## 🚀 Quick Start

```bash
cd cognifyz-internship/task2_number_pattern
python pattern_generator.py
```

No installation. No dependencies. Python 3.6 or above.

The program shows a menu of patterns; pick one, provide a size, and the pattern is drawn.

---

## ⭐ The Interesting Three

### 🌀 Number Spiral

Numbers from `1` to `n × n` written in a spiral, from the outer edge inwards.

<div align="center"><img src="assets/spiral_demo.gif" alt="Number spiral demo" width="700"></div>

This **cannot be produced by a nested loop alone** — the direction changes as the walk progresses. It needs a *direction vector* that rotates by 90° whenever the walk hits a wall or a filled cell:

```python
dr, dc = 0, 1                # (0,1)=right  (1,0)=down  (0,-1)=left  (-1,0)=up
...
if blocked:
    dr, dc = dc, -dr         # 90-degree turn in a single line
```

---

### 🔮 Magic Square

Every row, every column and **both diagonals** sum to the same value.

<div align="center"><img src="assets/magic_demo.gif" alt="Magic square demo" width="700"></div>

Built with the *Siamese method* — place `1` at the top-centre, then move up-and-right for each subsequent number. If the move goes off the grid, wrap around modulo `n`; if the target cell is already filled, drop one row instead.

```python
nr, nc = (r - 1) % n, (c + 1) % n     # up-and-right with wrap-around
if grid[nr][nc] != 0:
    nr, nc = (r + 1) % n, c           # target filled -> move down instead
```

> 💡 The distinguishing property of this pattern: the output can be **proved correct**. It is not a matter of "it looks right" — for `n = 11`, twenty-four separate sums all evaluate to exactly `671`.

---

### 🔢 Ulam Prime Spiral

Numbers laid out in a spiral, with only the **primes** marked — diagonal lines emerge on their own.

<div align="center"><img src="assets/ulam_demo.gif" alt="Ulam prime spiral demo" width="600"></div>

**Why this happens is still an open problem in mathematics.** Stanisław Ulam noticed it while doodling during a dull meeting in 1963.

---

## 🔺 The Patterns

From simple to complex, across three levels:

| # | Pattern | Size | Idea |
|---|---------|------|------|
| 1 | **Pyramid** | 1–15 | Nested loops + leading spaces |
| 2 | **Floyd's triangle** | 1–12 | A counter that does not reset between rows |
| 3 | **Palindrome pyramid** | 1–12 | Two inner loops — climb up, then back down |
| 4 | **Concentric rings** | 2–9 | Value derived from **distance**, not from a counter |
| 5 | **Multiplication grid** | 2–12 | A real multiplication table with headers |
| 6 | **Number spiral** | 2–12 | Direction vector plus boundary check |
| 7 | **Magic square** | 3–11 *(odd)* | Siamese method with modulo wrap-around |
| 8 | **Ulam prime spiral** | 5–25 *(odd)* | Spiral plus primality test |

<details>
<summary><b>See sample output (click)</b></summary>

```
Palindrome pyramid (n=5)        Concentric rings (n=4)
        1                       4 4 4 4 4 4 4
      1 2 1                     4 3 3 3 3 3 4
    1 2 3 2 1                   4 3 2 2 2 3 4
  1 2 3 4 3 2 1                 4 3 2 1 2 3 4
1 2 3 4 5 4 3 2 1               4 3 2 2 2 3 4
                                4 3 3 3 3 3 4
Floyd's triangle (n=5)          4 4 4 4 4 4 4
1
2 3                             Number spiral (n=5)
4 5 6                             1  2  3  4  5
7 8 9 10                         16 17 18 19  6
11 12 13 14 15                   15 24 25 20  7
                                 14 23 22 21  8
                                 13 12 11 10  9
```

</details>

---

## ➕ Adding a New Pattern

Two steps:

**1.** Write a function that takes `n` and prints the pattern:

```python
def my_pattern(n):
    for row in range(1, n + 1):
        for col in range(1, row + 1):
            print(col, end=" ")
        print()
```

**2.** Add an entry to `PATTERNS` with its size rules:

```python
PATTERNS = {
    ...
    "My pattern": {"fn": my_pattern, "min": 1, "max": 15, "odd": False},
}
```

The menu updates on its own, and `ask_size()` reads your `min` / `max` / `odd` rules from the spec directly. No `if / elif` chain is required.

> 💡 The dictionary stores `my_pattern`, **not** `my_pattern()`. Parentheses would *call* the function; without them the function itself is stored as a value, to be invoked later. That is why `spec["fn"](size)` works.

---

<details>
<summary><h2>📋 Internship Requirement (click to expand)</h2></summary>

From the internship task document:

> Create a program that generates and prints a number pattern using loops.
> Allow the pattern type to be selected, generate the pattern, and verify
> that the output is correct.

| Requirement | Where it is met |
|---|---|
| Generates and prints a number pattern | Eight pattern functions |
| Using loops | Every pattern uses nested loops; three go further with direction logic |
| Pattern type can be selected | Menu built from the `PATTERNS` registry |
| Output verified as correct | Property-based tests, see below |

</details>

<details>
<summary><h2>🧪 Test Results (click to expand)</h2></summary>

Output correctness was not judged by inspection — each pattern's **actual property** is checked.

### Magic square — 1..n² present, and every sum equal

| n | Sums checked | Every sum equals | 1..n² all present | Result |
|---|---|---|---|---|
| 3 | 8 | 15 | yes | PASS |
| 5 | 12 | 65 | yes | PASS |
| 7 | 16 | 175 | yes | PASS |
| 9 | 20 | 369 | yes | PASS |
| 11 | 24 | 671 | yes | PASS |

*(n rows + n columns + 2 diagonals)*

### Number spiral — each cell filled exactly once

| n | Check | Result |
|---|---|---|
| 2, 3, 5, 8, 12 | Flattened grid equals `1..n²` exactly once | PASS |

This test catches both missed cells and duplicate cells.

### Ulam spiral — `#` only on primes

| n | `#` count | Primes ≤ n² | Result |
|---|---|---|---|
| 5 | 9 | 9 | PASS |
| 9 | 22 | 22 | PASS |
| 17 | 61 | 61 | PASS |
| 25 | 114 | 114 | PASS |

`is_prime()` was independently validated against 22 known primes (2–79) — PASS.

### Others

| Pattern | Check | Result |
|---|---|---|
| Palindrome pyramid | Each row `row == row[::-1]`, and exactly n rows | PASS |
| Concentric rings | Grid `(2n-1)²`, centre = 1, corner = n | PASS |
| **All 8** | Run at their minimum size without crashing | PASS |

### Input validation

| Input | Where | Behaviour |
|-------|-------|-----------|
| `abc`, *(empty)* | Both prompts | "Enter a number", re-prompt |
| `0`, `99` | Pattern menu | "Enter a number between 1 and 8" |
| `0`, `-5`, `500` | Size prompt | Pattern-specific range message |
| `4` | Magic square size | "Size must be odd. Try 5 or 3." |

</details>

<details>
<summary><h2>🏗️ Design Notes (click to expand)</h2></summary>

### Nested loops — the core of this task

```python
for row in range(1, n + 1):        # outer: how many lines
    for col in range(1, row + 1):  # inner: how many numbers on this line
        print(col, end=" ")
    print()                        # end of line
```

Each iteration of the outer loop drives the inner loop to completion. The inner loop's limit depends on `row`, so each line is longer than the last.

`print(..., end=" ")` suppresses the automatic newline, keeping numbers on the same line. The bare `print()` after the inner loop terminates the line.

### Where nested loops are not enough

Spiral and Ulam patterns have no simple mapping from rows and columns — position advances by **direction**, not by index. That requires:

- A writable 2D grid — `[[0] * n for _ in range(n)]`
- A direction vector `(dr, dc)` and a turn rule — `dr, dc = dc, -dr`
- A boundary check and an "already filled" check

The magic square uses modulo wrap-around — `(r - 1) % n` — so an out-of-grid move re-enters from the opposite side.

### Every pattern carries its own rules

```python
PATTERNS = {
    "Magic square": {"fn": magic_square, "min": 3, "max": 11, "odd": True},
}
```

`ask_size()` reads those rules **from the spec** rather than hard-coding them. The constraint "the magic square only accepts odd sizes" is therefore stated in exactly one place — its own registry entry. A new pattern can bring its own rules without any change to `ask_size()`.

This is the same idea as Task 1's `questions.json` — **data is separated from logic**.

### Reuse from Task 1

`ask_choice()` is the same helper used in `quiz_game.py`. `ask_size()` mirrors the shape of `get_guess()`: `try/except ValueError` for the type conversion, followed by `if` for the domain rule.

Use `try/except` when the only way to know is to attempt the operation; use `if` when the rule can be checked in advance.

### Size caps

Each pattern has its own maximum. Ulam is capped at 25 (any smaller and the diagonal structure is not visible), magic square at 11 (larger sizes distort columns visually), Floyd at 12 (values reach 78). These are usability decisions expressed as data in `PATTERNS`.

</details>

---

<div align="center">

**Part of the [Cognifyz Software Development Internship](https://github.com/15Arghya2004/cognifyz-internship)**
Built by [Arghya Mahajan](https://github.com/15Arghya2004)

</div>
