# ============================================
# TASK 1 - Number Guessing Game
# Cognifyz IT Solutions - Software Development Internship
# ============================================
#
# RULES:
# 1. Computer 1 se 100 ke beech ek secret number chunta hai
# 2. Player guess karta hai
# 3. Game batata hai guess kam hai ya zyada
# 4. Sahi guess pe game khatam, koshishon ki ginti batati hai
# 5. Galat input (jaise "hello") pe game crash nahi hota
# ============================================

import random


def get_guess():
    """Player se ek valid whole number leta hai.
    Galat input pe dobara poochta hai, crash nahi hota."""
    while True:
        raw = input("Apna guess (1-100): ")
        try:
            return int(raw)
        except ValueError:
            print("  -> Sirf whole number likho, jaise 42.")


def play():
    """Poora game chalata hai."""
    secret = random.randint(1, 100)
    attempts = 0

    print("Maine 1 se 100 ke beech ek number socha hai.")
    print("Guess karo, main batata rahunga zyada hai ya kam.\n")

    while True:
        guess = get_guess()

        if guess < 1 or guess > 100:
            print("  -> Range se bahar. 1 se 100 ke beech likho.")
            continue

        attempts += 1

        if guess < secret:
            print("  -> Bahut kam. Upar jao.")
        elif guess > secret:
            print("  -> Bahut zyada. Neeche aao.")
        else:
            print("\nSahi jawab! Number tha", secret)
            print("Tumne", attempts, "koshish mein jeet liya.")
            break


if __name__ == "__main__":
    play()

# ============================================
# TESTING - ye inputs try kar:
#   hello         -> error message aayega, crash nahi
#   3.5           -> error message aayega
#   150           -> "range se bahar", attempt count NAHI hoga
#   -5            -> "range se bahar"
#   (khali Enter) -> error message
#   50            -> normal guess
# ============================================
