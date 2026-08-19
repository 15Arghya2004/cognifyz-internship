# ============================================
# TASK 1 - Multiple Choice Quiz Game
# Cognifyz IT Solutions - Software Development Internship
# ============================================
#
# RULES:
# 1. Sawaal ek alag file (questions.json) mein rehte hain, code ke andar nahi.
#    Naya question set chahiye? Bas wo file badlo - code chhoona nahi padega.
# 2. Player topic aur difficulty chunta hai (ya "All" chun sakta hai).
# 3. Har game mein us filter se 5 RANDOM sawaal aate hain, bina repeat ke.
#    Isliye har baar khelna alag lagta hai.
# 4. Sahi jawab pe +1, galat pe sahi jawab dikha diya jata hai.
# 5. Galat input (jaise "Z") pe game crash nahi hota aur sawaal skip nahi hota.
# 6. Har topic+difficulty ka best score highscores.json mein save rehta hai.
#
# NOTE: guessing_game.py mein `while` loop hai kyunki wahan pata nahi kitne
# round chalenge. Yahan `for` loop hai kyunki sawaal fix 5 hain.
# ============================================

import json
import random
from pathlib import Path

# Ye file jis folder mein hai, wahi se data files uthao.
# Isse game kisi bhi folder se chalao, paths hamesha sahi rahenge.
HERE = Path(__file__).parent
QUESTIONS_FILE = HERE / "questions.json"
SCORES_FILE = HERE / "highscores.json"

QUESTIONS_PER_GAME = 5
VALID_CHOICES = ("A", "B", "C", "D")
ALL = "All"


# ---------------------------------------------------------------
# 1. QUESTION BANK LOAD KARNA
# ---------------------------------------------------------------

def is_valid_question(item):
    """Check karta hai ki ek sawaal ka format sahi hai ya nahi.
    Galat sawaal ko pehle hi pakad lena behtar hai, beech game mein crash hone se."""
    if not isinstance(item, dict):
        return False
    for field in ("question", "options", "answer", "topic", "difficulty"):
        if field not in item:
            return False
    if not isinstance(item["options"], dict):
        return False
    # Chaaron option hone chahiye
    for letter in VALID_CHOICES:
        if letter not in item["options"]:
            return False
    # Sahi jawab options mein se hi hona chahiye
    return item["answer"] in VALID_CHOICES


def load_questions():
    """questions.json padhta hai aur (bank_ka_naam, sawaalon_ki_list) return karta hai.
    File na mile ya kharab ho to crash nahi hota - saaf message deta hai."""
    try:
        with open(QUESTIONS_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Question file nahi mili:", QUESTIONS_FILE)
        print("questions.json isi folder mein honi chahiye.")
        return None, []
    except json.JSONDecodeError as error:
        print("questions.json padhi nahi ja saki - JSON format galat hai.")
        print("  ->", error)
        return None, []
    except OSError as error:
        print("questions.json kholi nahi ja saki.")
        print("  ->", error)
        return None, []

    name = data.get("name", "Question bank")
    raw = data.get("questions", [])

    good = []
    skipped = 0
    for item in raw:
        if is_valid_question(item):
            good.append(item)
        else:
            skipped += 1

    if skipped:
        print("Note:", skipped, "sawaal galat format ki wajah se chhod diye gaye.\n")

    return name, good


# ---------------------------------------------------------------
# 2. INPUT LENA (ek hi function, teen jagah use hota hai)
# ---------------------------------------------------------------

def ask_choice(prompt, choices):
    """User se list mein se ek option chunwata hai. 1, 2, 3... number se.
    Galat input pe dobara poochta hai, crash nahi hota.
    Ye function topic, difficulty aur A/B/C/D - teeno ke liye kaam aata hai."""
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


def ask_answer():
    """Player se ek valid option (A/B/C/D) leta hai.
    Chhote akshar aur extra space bhi chalte hain."""
    while True:
        raw = input("Tumhara jawab (A/B/C/D): ")
        choice = raw.strip().upper()

        if choice in VALID_CHOICES:
            return choice

        print("  -> Sirf A, B, C ya D likho.")


# ---------------------------------------------------------------
# 3. SAWAAL CHUNNA
# ---------------------------------------------------------------

def unique_values(questions, field):
    """Bank mein jo bhi topics (ya difficulties) hain, unki sorted list deta hai.
    Hardcode nahi kiya - naya bank aayega to menu apne aap badal jayega."""
    found = set()
    for item in questions:
        found.add(item[field])
    return sorted(found)


def filter_questions(questions, topic, difficulty):
    """Chune hue topic aur difficulty ke hisaab se sawaal chhaanta hai."""
    result = []
    for item in questions:
        if topic != ALL and item["topic"] != topic:
            continue
        if difficulty != ALL and item["difficulty"] != difficulty:
            continue
        result.append(item)
    return result


def pick_questions(pool, count):
    """Pool mein se random sawaal uthata hai - BINA repeat ke.

    random.sample() use kiya hai, random.choice() nahi.
    choice() ko 5 baar chalate to ek hi sawaal do baar aa sakta tha.
    sample() bina replacement ke uthata hai, isliye sab alag rehte hain."""
    if len(pool) <= count:
        # Utne sawaal hain hi nahi - jitne hain sabhi le lo, shuffle karke
        chosen = list(pool)
        random.shuffle(chosen)
        return chosen
    return random.sample(pool, count)


# ---------------------------------------------------------------
# 4. HIGH SCORE (file mein save)
# ---------------------------------------------------------------

def score_key(topic, difficulty):
    """Har topic+difficulty combination ka apna best score rehta hai."""
    return topic + " | " + difficulty


def load_high_scores():
    """Purane high scores padhta hai. File na ho to khali se shuru karo -
    ye error nahi hai, pehli baar khelne pe aisa hi hoga."""
    try:
        with open(SCORES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
        return {}
    except FileNotFoundError:
        return {}
    except (json.JSONDecodeError, OSError):
        print("Note: purane high scores padhe nahi ja sake, naye se shuru kar rahe hain.\n")
        return {}


def save_high_scores(scores):
    """High scores file mein likhta hai. Na likh paye to game fir bhi chalta rahe."""
    try:
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2, ensure_ascii=False)
        return True
    except OSError as error:
        print("Note: high score save nahi ho paya.")
        print("  ->", error)
        return False


# ---------------------------------------------------------------
# 5. GAME
# ---------------------------------------------------------------

def ask_question(number, total, item):
    """Ek sawaal poochta hai. True return karta hai agar jawab sahi tha."""
    print("\nSawaal", str(number) + "/" + str(total),
          "  [" + item["topic"] + " - " + item["difficulty"] + "]")
    print(item["question"])

    for letter in VALID_CHOICES:
        print(" ", letter + ")", item["options"][letter])

    choice = ask_answer()
    correct = item["answer"]

    if choice == correct:
        print("  -> Sahi!")
        return True

    print("  -> Galat. Sahi jawab tha", correct + ")", item["options"][correct])
    return False


def show_result(score, total, topic, difficulty, scores):
    """Final score, percentage, message aur high score dikhata hai."""
    percent = score / total * 100
    key = score_key(topic, difficulty)
    previous_best = scores.get(key, 0)

    print("\n" + "=" * 46)
    print("Quiz khatam!  [" + key + "]")
    print("Score:", score, "out of", total)
    print("Percentage:", round(percent, 1), "%")

    if percent == 100:
        print("Perfect! Sab sahi.")
    elif percent >= 60:
        print("Achha kaam. Thoda aur revision karo.")
    else:
        print("Practice ki zaroorat hai. Dobara try karo.")

    if score > previous_best:
        print("Naya high score! (pehle", previous_best, "tha)")
        scores[key] = score
        save_high_scores(scores)
    else:
        print("Is category ka best score:", previous_best)

    print("=" * 46)


def play():
    """Poora game chalata hai."""
    bank_name, questions = load_questions()

    if not questions:
        print("Ek bhi valid sawaal nahi mila. Game shuru nahi ho sakta.")
        return

    print("Multiple Choice Quiz")
    print("Bank:", bank_name, "-", len(questions), "sawaal available\n")

    print("Topic chuno:")
    topic = ask_choice("Topic number: ", [ALL] + unique_values(questions, "topic"))

    print("\nDifficulty chuno:")
    difficulty = ask_choice("Difficulty number: ", [ALL] + unique_values(questions, "difficulty"))

    pool = filter_questions(questions, topic, difficulty)

    if not pool:
        print("\nIs combination ke liye koi sawaal nahi hai. Dobara chalao.")
        return

    selected = pick_questions(pool, QUESTIONS_PER_GAME)
    total = len(selected)

    if total < QUESTIONS_PER_GAME:
        print("\nNote: is filter mein sirf", total, "sawaal hain,",
              "isliye poore", QUESTIONS_PER_GAME, "nahi mil paye.")

    print("\nChuna gaya:", topic, "-", difficulty, "|", total, "sawaal")
    print("Har sahi jawab ka 1 point.")

    scores = load_high_scores()
    score = 0

    for index, item in enumerate(selected, start=1):
        if ask_question(index, total, item):
            score += 1

    show_result(score, total, topic, difficulty, scores)


if __name__ == "__main__":
    play()

# ============================================
# TESTING - ye scenarios try kar:
#   Menu mein: 0, 99, "abc", (khali Enter) -> error message, dobara poochega
#   Jawab mein: Z, hello, (khali Enter)    -> error message, sawaal skip NAHI hoga
#   "  b  " ya "b"                          -> chalega (strip + upper)
#   Game do baar chalao, same filter pe     -> sawaal alag order/set mein aayenge
#   questions.json ka naam badal do         -> saaf message, crash nahi
#   questions.json mein ek comma hata do    -> JSON error message, crash nahi
#   Ek sawaal se "answer" field hata do     -> wo sawaal skip, baaki game chalega
# ============================================
