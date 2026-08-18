# ============================================
# DEMO: Cheat mode - secret number pehle hi dikha deta hai
# Isse tu dekh sakta hai ki kam/zyada wala logic sahi hai ya nahi,
# AUR ye bhi ki if/elif/else andar se kaam kaise karta hai.
# ============================================

import random

secret = random.randint(1, 100)

print("=== CHEAT MODE ===")
print("Secret number hai:", secret)
print("Ab guess karo, aur check karo ki program sahi bol raha hai ya nahi\n")

raw = input("Apna guess: ")
guess = int(raw)

print("\nAb dekh Python andar kya soch raha hai:")
print("  guess =", guess)
print("  secret =", secret)
print("  guess < secret  ?  ", guess < secret)
print("  guess > secret  ?  ", guess > secret)
print("  guess == secret ?  ", guess == secret)

print("\nAur final faisla:")
if guess < secret:
    print("  -> Bahut kam")
elif guess > secret:
    print("  -> Bahut zyada")
else:
    print("  -> Sahi jawab!")

# ============================================
# Dhyan de: teeno comparison True/False dete hain.
# Ye BOOLEAN data type hai - sirf do value: True ya False.
# if/elif/else in True/False ko dekh ke faisla karta hai.
#
# NOTE: is file mein try/except nahi hai. Jaan-boojh ke.
# "hello" type kar ke dekh - crash hoga. Yahi wajah hai ki
# asli game mein try/except lagaya hai.
# ============================================
