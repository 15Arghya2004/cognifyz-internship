# ============================================
# TASK 1 - Multiple Choice Quiz Game
# Cognifyz IT Solutions - Software Development Internship
# ============================================
#
# RULES:
# 1. Quiz mein fix 5 sawaal hain, har sawaal ke 4 options (A/B/C/D)
# 2. Player har sawaal ka ek option chunta hai
# 3. Sahi jawab pe score +1, galat pe sahi jawab bata diya jata hai
# 4. Sabhi sawaal khatam hone pe final score aur percentage dikhta hai
# 5. Galat input (jaise "Z" ya "hello") pe game crash nahi hota
#
# NOTE: guessing_game.py mein `while` loop hai kyunki wahan pata nahi
# kitne round chalenge. Yahan `for` loop hai kyunki sawaal fix 5 hain.
# ============================================


# Har sawaal ek dictionary hai, aur sabhi sawaal ek list mein hain.
QUESTIONS = [
    {
        "question": "Python mein input() function kya return karta hai?",
        "options": {"A": "Integer", "B": "String", "C": "Float", "D": "Boolean"},
        "answer": "B",
    },
    {
        "question": "Jab pata ho ki loop kitni baar chalana hai, to kaunsa loop best hai?",
        "options": {"A": "while", "B": "if", "C": "for", "D": "try"},
        "answer": "C",
    },
    {
        "question": "int(\"hello\") likhne pe Python kaunsa error deta hai?",
        "options": {"A": "TypeError", "B": "NameError", "C": "SyntaxError", "D": "ValueError"},
        "answer": "D",
    },
    {
        "question": "Bharat ki rajdhani kaunsi hai?",
        "options": {"A": "Mumbai", "B": "New Delhi", "C": "Kolkata", "D": "Chennai"},
        "answer": "B",
    },
    {
        "question": "Duniya ka sabse bada mahasagar kaunsa hai?",
        "options": {"A": "Atlantic", "B": "Indian", "C": "Pacific", "D": "Arctic"},
        "answer": "C",
    },
]

VALID_CHOICES = ("A", "B", "C", "D")


def get_answer():
    """Player se ek valid option (A/B/C/D) leta hai.
    Chhote akshar bhi chalte hain. Galat input pe dobara poochta hai."""
    while True:
        raw = input("Tumhara jawab (A/B/C/D): ")
        choice = raw.strip().upper()

        if choice in VALID_CHOICES:
            return choice

        print("  -> Sirf A, B, C ya D likho.")


def ask_question(number, total, item):
    """Ek sawaal poochta hai aur batata hai jawab sahi tha ya nahi.
    True return karta hai agar sahi, warna False."""
    print("\nSawaal", str(number) + "/" + str(total))
    print(item["question"])

    for letter in VALID_CHOICES:
        print(" ", letter + ")", item["options"][letter])

    choice = get_answer()
    correct = item["answer"]

    if choice == correct:
        print("  -> Sahi!")
        return True

    print("  -> Galat. Sahi jawab tha", correct + ")", item["options"][correct])
    return False


def show_result(score, total):
    """Final score, percentage aur ek message print karta hai."""
    percent = score / total * 100

    print("\n" + "=" * 40)
    print("Quiz khatam!")
    print("Score:", score, "out of", total)
    print("Percentage:", round(percent, 1), "%")

    if percent == 100:
        print("Perfect! Sab sahi.")
    elif percent >= 60:
        print("Achha kaam. Thoda aur revision karo.")
    else:
        print("Practice ki zaroorat hai. Dobara try karo.")

    print("=" * 40)


def play():
    """Poora quiz chalata hai."""
    total = len(QUESTIONS)
    score = 0

    print("Multiple Choice Quiz")
    print("Kul", total, "sawaal hain. Har sahi jawab ka 1 point.")

    for index, item in enumerate(QUESTIONS, start=1):
        if ask_question(index, total, item):
            score += 1

    show_result(score, total)


if __name__ == "__main__":
    play()

# ============================================
# TESTING - ye inputs try kar:
#   A / B / C / D   -> normal jawab
#   a               -> chalega, chhota akshar upar ho jata hai
#   "  b  "         -> chalega, extra space hat jati hai
#   Z               -> error message, dobara poochega
#   hello           -> error message, dobara poochega
#   (khali Enter)   -> error message, dobara poochega
#
# Expected: galat input kabhi bhi sawaal ko skip nahi karta
#           aur score ko affect nahi karta.
# ============================================
