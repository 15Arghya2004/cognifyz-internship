# Learning Notes

Concepts samjhe hue, apne shabdon mein. Ye file har naye concept ke saath
update karni hai. Agar yahan likh nahi paa raha, matlab samjha nahi.

---

## `def` vs function call

- `def naam():` — function **banata** hai. Ek baar likhte hain. **Chalta nahi.**
- `naam()` — function **chalata** hai. Jitni baar likho, utni baar chalega.
- Proof: `practice/demo1_def_vs_call.py` chala ke dekha — `def` ke andar ka
  print `def` ki line paar karne pe nahi chala.
- Recipe likhna (`def`) aur khana banana (`naam()`) do alag kaam hain.
- Guessing game mein: `get_guess` define 1 baar, chala 6 baar (kyunki call
  `while` loop ke andar hai). `play` define 1 baar, chala 1 baar.

## `import`

- Python ka core chhota hai. Extra tools "module" naam ke dabbon mein hain.
- `import random` = us dabbe ko kholna.
- `random.randint(1, 100)` = dabbe ke andar ka function. Dot = "ke andar ka".
- Bina import kiye use karo to: `NameError: name 'random' is not defined`
- Standard library free aati hai (random, math, os, json, datetime).
  Bahar ke packages ke liye `pip install` chahiye.

## `input()` hamesha string deta hai

- User `42` type kare to bhi Python ke liye wo `"42"` (text) hai, number nahi.
- Number banane ke liye `int()` lagana padta hai.
- Ye is task ka sabse important sabak hai.

## `try` / `except`

```python
try:
    return int(raw)
except ValueError:
    print("galat input")
```

- `try:` — "ye line chalane ki koshish karo, fail ho sakti hai"
- `except ValueError:` — "agar YE error aaye, program mat maro, ye karo"
- Khali `except:` NAHI likhna — wo apne bugs bhi chhupa deta hai, aur Ctrl+C
  bhi pakad leta hai.
- `raw` koi keyword nahi hai — wo mera rakha hua variable ka naam hai.

## Error ke naam (exception types)

| Error | Kab aata hai |
|-------|--------------|
| `ValueError` | Type sahi, value bekaar. `int("hello")` |
| `TypeError` | Type hi galat. `5 + "abc"` |
| `ZeroDivisionError` | `10 / 0` |
| `FileNotFoundError` | File exist nahi karti |
| `NameError` | Aisa naam use kiya jo banaya hi nahi |

## Counter aur initialization

- `attempts = 0` pehle likhna **zaroori** hai.
- `attempts += 1` ka matlab `attempts = attempts + 1` — purani value chahiye.
- Bina initialize kiye: `NameError`

## `continue` vs `break`

- `continue` — "iss round ka baaki hissa chhodo, loop ke shuru mein wapas jao"
- `break` — "loop poora khatam karo, bahar niklo"

## `return`

- Function ke **andar** likha jaata hai.
- Do kaam: value bahar bhejta hai + us function ko wahin khatam kar deta hai.
- "Program khatam" ka matlab NAHI hai.
- `guess = get_guess()` — jo return hua wo `guess` mein aa ke baith gaya.
- Har function ko `return` nahi chahiye. `play()` kuch wapas nahi bhejta,
  isliye usko `guess = play()` ki tarah nahi bulate.

## Boolean

- `guess < secret` pehle `True` ya `False` banta hai.
- `if` us `True`/`False` ko dekh ke faisla karta hai.
- `practice/demo2_secret_dikhao.py` isko screen pe dikhata hai.

---

## Abhi bhi confusion hai (yahan likhna hai)

- (khali — jab kuch samajh na aaye to yahan note karna, fir poochna)
