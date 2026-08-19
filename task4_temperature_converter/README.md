# Task 4 — Temperature Converter

**Cognifyz Technologies · Software Development Internship · Level 2: Intermediate**

> ⚠️ Yeh README temporary hai — baad mein Task 1/2 jaisa detail + animation ke saath rewrite hoga.

## Run

```bash
python task4_temperature_converter/temperature_converter.py
```

Python 3.6+ | koi library nahi chahiye.

## Kya karta hai

```
==============================================
  TEMPERATURE CONVERTER  -  Cognifyz Task 4
==============================================
  1. Celsius se Fahrenheit
  2. Fahrenheit se Celsius
  3. Reference table dekho
  0. Exit
```

Formulas:

```
F = (C x 9/5) + 32
C = (F - 32) x 5/9
```

## Kya khaas hai

- **Absolute zero guard** — `-273.15 C` / `-459.67 F` se neeche wali value reject hoti hai, kyunki wo physically possible nahi hai.
- **Har result ke saath hisaab dikhta hai**, sirf answer nahi.
- **`25c` ya `25` dono chalte hain** — trailing C/F apne aap hat jaata hai.
- **Galat input pe crash nahi** — dobara poochta hai.
- **Reference table** — -40 se 100 C tak ready conversion, plus har value ka matlab (paani jamta hai, fever range, etc).
- `-40` wo ikloti value hai jahan dono scales barabar hote hain — table mein highlight kiya gaya hai.

## Testing

30/30 automated checks pass:

| Group | Kya check kiya |
|---|---|
| Known points | 0/100 C, 32/212 F, 37 C = 98.6 F (body temp), -40 dono mein same, absolute zero |
| Roundtrip | `C -> F -> C` -273 se 200 tak exactly wapas aata hai |
| Absolute zero | -273.16 reject, -273.15 accept (boundary exact) |
| Formatting | 2 decimal, `-0.00` kabhi nahi aata, negative surakshit |

## Files

```
task4_temperature_converter/
├── README.md
└── temperature_converter.py
```
