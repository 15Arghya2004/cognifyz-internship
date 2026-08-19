# ============================================
# TASK 2 - Number Pattern Generator
# Cognifyz IT Solutions - Software Development Internship
# ============================================
#
# RULES:
# 1. Program 8 alag-alag number patterns bana sakta hai.
# 2. User menu se pattern chunta hai.
# 3. Har pattern ke apne size rules hain (kuch sirf odd size pe kaam karte hain).
#    Ye rules PATTERNS dictionary mein data ki tarah rakhe hain, code mein nahi.
# 4. Galat input (jaise "abc", 0, -5, 500, ya odd-only pattern pe even size)
#    pe program crash nahi hota.
#
# NOTE: Task 1 ke games mein ek loop tha. Yahan NESTED loop hai - loop ke
# andar loop. Bahar wala rows sambhalta hai, andar wala ek row ke numbers.
# Aakhri teen patterns nested loop se aage jaate hain - unme direction
# change aur 2D grid ka logic hai.
# ============================================


# ---------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------

def is_prime(number):
    """True agar number prime hai. 2 se sqrt tak divide karke dekhta hai."""
    if number < 2:
        return False
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            return False
        divisor += 1
    return True


def print_grid(grid, width=4):
    """2D list ko seedhe columns mein chhapta hai."""
    for row in grid:
        for value in row:
            print(format(value, ">" + str(width)), end="")
        print()


# ---------------------------------------------------------------
# LEVEL 1 - simple nested loops
# ---------------------------------------------------------------

def pyramid(n):
    """    1
          1 2
         1 2 3      -> aage space daal ke beech mein"""
    for row in range(1, n + 1):
        print(" " * (n - row), end="")
        for col in range(1, row + 1):
            print(col, end=" ")
        print()


def floyd_triangle(n):
    """1
       2 3
       4 5 6        -> ginti rukti nahi, chalti rehti hai"""
    number = 1
    for row in range(1, n + 1):
        for _ in range(row):
            print(number, end=" ")
            number += 1
        print()


def palindrome_pyramid(n):
    """      1
           1 2 1
         1 2 3 2 1  -> upar chadho, phir wapas utro"""
    for row in range(1, n + 1):
        print("  " * (n - row), end="")
        for col in range(1, row + 1):          # 1 se row tak
            print(col, end=" ")
        for col in range(row - 1, 0, -1):      # row-1 se wapas 1 tak
            print(col, end=" ")
        print()


# ---------------------------------------------------------------
# LEVEL 2 - grid se soch, counting se nahi
# ---------------------------------------------------------------

def concentric_rings(n):
    """5 5 5 5 5
       5 4 4 4 5     -> har cell ki value uski KINARE se doori hai.
       5 4 3 4 5        Yahan kuch gina nahi ja raha."""
    size = 2 * n - 1
    centre = n - 1
    for r in range(size):
        for c in range(size):
            distance = max(abs(r - centre), abs(c - centre))
            print(distance + 1, end=" ")
        print()


def multiplication_grid(n):
    """Asli pahada table, headers ke saath."""
    print("     |", end="")
    for col in range(1, n + 1):
        print(format(col, ">4"), end="")
    print()
    print("-----+" + "-" * (4 * n))
    for row in range(1, n + 1):
        print(format(row, ">4"), "|", sep="", end="")
        for col in range(1, n + 1):
            print(format(row * col, ">4"), end="")
        print()


# ---------------------------------------------------------------
# LEVEL 3 - algorithm, sirf loop nahi
# ---------------------------------------------------------------

def number_spiral(n):
    """1 se n*n tak, bahar se andar ghoomte hue.

    Nested loop se ye ban hi nahi sakta - kyunki direction badalti hai.
    (dr, dc) ek DIRECTION VECTOR hai: (0,1)=right, (1,0)=down,
    (0,-1)=left, (-1,0)=up. Jab deewar ya bhara cell aaye, mud jao."""
    grid = [[0] * n for _ in range(n)]
    r, c = 0, 0
    dr, dc = 0, 1                       # shuruat: right
    for value in range(1, n * n + 1):
        grid[r][c] = value
        nr, nc = r + dr, c + dc
        blocked = not (0 <= nr < n and 0 <= nc < n) or grid[nr][nc] != 0
        if blocked:
            dr, dc = dc, -dr            # 90 degree mudo
            nr, nc = r + dr, c + dc
        r, c = nr, nc
    print_grid(grid)


def magic_square(n):
    """Har row, column aur dono diagonals ka jod BARABAR aata hai.

    Siamese method: 1 ko top row ke beech mein rakho. Har agla number
    upar-daayen rakho. Grid se bahar nikal jao to doosri taraf se ghus jao
    (modulo). Cell pehle se bhara ho to ek neeche aa jao."""
    grid = [[0] * n for _ in range(n)]
    r, c = 0, n // 2
    for value in range(1, n * n + 1):
        grid[r][c] = value
        nr, nc = (r - 1) % n, (c + 1) % n     # upar-daayen, wrap around
        if grid[nr][nc] != 0:
            nr, nc = (r + 1) % n, c           # bhara hai -> neeche
        r, c = nr, nc
    print_grid(grid)

    total = sum(grid[0])
    print()
    print("Har row, column aur dono diagonals ka jod =", total)


def ulam_spiral(n):
    """Numbers spiral mein rakho, sirf PRIME wale mark karo.

    Diagonal lines apne aap ban jaati hain. Kyun - ye aaj tak
    solve nahi hua. Stanislaw Ulam ne 1963 mein notice kiya tha."""
    grid = [[False] * n for _ in range(n)]
    r = c = n // 2
    dr, dc = 0, 1
    value = 1
    step = 1
    grid[r][c] = is_prime(value)

    running = True
    while running:
        for _ in range(2):                    # har length do baar chalti hai
            for _ in range(step):
                r, c = r + dr, c + dc
                value += 1
                if not (0 <= r < n and 0 <= c < n):
                    running = False
                    break
                grid[r][c] = is_prime(value)
            if not running:
                break
            dr, dc = dc, -dr
        step += 1

    for row in grid:
        for cell in row:
            print("#" if cell else ".", end=" ")
        print()
    print()
    print("Har # ek prime number hai.")


# ---------------------------------------------------------------
# PATTERN REGISTRY
# Har pattern apne size rules KHUD carry karta hai - data ki tarah.
# Naya pattern add karna? Function likho aur yahan ek entry jodo.
# ---------------------------------------------------------------

PATTERNS = {
    "Pyramid":              {"fn": pyramid,             "min": 1, "max": 15, "odd": False},
    "Floyd's triangle":     {"fn": floyd_triangle,      "min": 1, "max": 12, "odd": False},
    "Palindrome pyramid":   {"fn": palindrome_pyramid,  "min": 1, "max": 12, "odd": False},
    "Concentric rings":     {"fn": concentric_rings,    "min": 2, "max": 9,  "odd": False},
    "Multiplication grid":  {"fn": multiplication_grid, "min": 2, "max": 12, "odd": False},
    "Number spiral":        {"fn": number_spiral,       "min": 2, "max": 12, "odd": False},
    "Magic square":         {"fn": magic_square,        "min": 3, "max": 11, "odd": True},
    "Ulam prime spiral":    {"fn": ulam_spiral,         "min": 5, "max": 25, "odd": True},
}


# ---------------------------------------------------------------
# INPUT - Task 1 wala hi tareeka
# ---------------------------------------------------------------

def ask_choice(prompt, choices):
    """List mein se ek option chunwata hai, number se.
    Galat input pe dobara poochta hai, crash nahi hota."""
    for number, choice in enumerate(choices, start=1):
        print(" ", str(number) + ")", choice)

    while True:
        raw = input(prompt)
        try:
            picked = int(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 1.")
            continue

        if 1 <= picked <= len(choices):
            return choices[picked - 1]

        print("  -> 1 se", len(choices), "ke beech likho.")


def ask_size(spec):
    """Pattern ke apne rules ke hisaab se size leta hai.
    Rules spec dictionary se aate hain - hardcode nahi hain."""
    low, high, odd_only = spec["min"], spec["max"], spec["odd"]

    if odd_only:
        print("Ye pattern sirf odd size pe banta hai (3, 5, 7 ...).")

    while True:
        raw = input("Size? (" + str(low) + "-" + str(high) + "): ")
        try:
            size = int(raw)
        except ValueError:
            print("  -> Sirf whole number likho, jaise 5.")
            continue

        if not low <= size <= high:
            print("  ->", low, "se", high, "ke beech likho.")
            continue

        if odd_only and size % 2 == 0:
            print("  -> Odd number chahiye. Try", size + 1, "ya", size - 1, ".")
            continue

        return size


# ---------------------------------------------------------------
# PROGRAM
# ---------------------------------------------------------------

def run():
    print("Number Pattern Generator")
    print(len(PATTERNS), "patterns available.\n")

    print("Pattern chuno:")
    name = ask_choice("Pattern number: ", list(PATTERNS))

    spec = PATTERNS[name]
    size = ask_size(spec)

    print("\n" + "=" * 46)
    print(name, "-", "size", size)
    print("=" * 46)
    spec["fn"](size)                   # registry se function nikal ke chalaya
    print("=" * 46)


if __name__ == "__main__":
    run()

# ============================================
# TESTING - ye inputs try kar:
#   Menu: 0, 99, "abc", (khali)   -> error message, dobara poochega
#   Size: 0, -5, 500, "paanch"    -> error message, dobara poochega
#   Magic square pe size 4        -> "Odd number chahiye", 5 ya 3 suggest karega
#   Har pattern apne min size pe  -> crash nahi hona chahiye
# ============================================
