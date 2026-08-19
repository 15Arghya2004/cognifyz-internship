<div align="center">

# 🌡️ Task 4 — Health Temperature Toolkit

**Cognifyz Technologies · Software Development Internship · Level 2**

![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Install](https://img.shields.io/badge/Install-Kuch%20nahi-success?style=for-the-badge)
![Checks](https://img.shields.io/badge/Checks-72%2F72%20pass-brightgreen?style=for-the-badge)
![Sources](https://img.shields.io/badge/Numbers-Cited-blue?style=for-the-badge)

Temperature convert karo — **aur samjho bhi ki us number ka matlab kya hai.**

</div>

> ⚠️ **Yeh medical device nahi hai.** Program sirf public reference ranges dikhata hai.
> Kisi bhi health decision ke liye doctor se hi baat karo.

---

## 🚀 Chalao

```bash
python task4_temperature_converter/temperature_converter.py
```

Bas. Na install, na setup. Sirf Python 3.6+ chahiye.

---

## 📋 Menu

```
==========================================================
  HEALTH TEMPERATURE TOOLKIT  -  Cognifyz Task 4
==========================================================
  1. Celsius <-> Fahrenheit convert karo
  2. Body temperature check karo
  3. Heat index - garmi kitni lagegi
  4. Wind chill - thand kitni lagegi
  5. Reference tables dekho
  0. Exit
```

**Option 1 hi PDF ki asli requirement hai** — user temperature daale, direction chune, convert ho jaye. Baaki chaar uske upar bane health tools hain.

---

## 🩺 Body temperature check

<div align="center">

![Body temperature demo](assets/body_demo.gif)

*Bagal ka 37.3 C → oral jaisa 37.6–37.9 C → do band ke beech · phir 103 F oral → High fever*

</div>

Program teen cheezein poochta hai: **reading**, **kahan se naapa**, aur **kiska**.

### Kahan se naapa — ye kyun maayne rakhta hai

Alag jagah se naapa hua temperature alag aata hai:

| Kahan se | Mooh ke muqable |
|---|---|
| Rectal | 0.3 – 0.6 °C **zyada** |
| Kaan (ear) | 0.3 – 0.6 °C **zyada** |
| Bagal (armpit) | 0.3 – 0.6 °C **kam** |
| Maatha (forehead) | 0.3 – 0.6 °C **kam** |

Isliye program pehle reading ko **oral-equivalent** mein badalta hai, phir category batata hai.

> **Ek design decision:** source ek **range** deta hai (0.3 se 0.6), ek fixed number nahi. Isliye program bhi range hi dikhata hai — jhoothi precision nahi banata. Aur agar wo range do category ke beech pad jaye, to saaf-saaf bata deta hai: *"pakka janne ke liye oral ya rectal se naapo."*

### Categories

| Range (oral) | Category |
|---|---|
| 28 °C se neeche | Severe hypothermia |
| 28 – 32 °C | Moderate hypothermia |
| 32 – 35 °C | Mild hypothermia |
| 35 °C – 100 °F | Normal range |
| 100 – 103 °F | Fever |
| 103 – 104 °F | High fever |
| 104 °F se upar | Very high fever |

Aur umar ke hisaab se alag rule bhi dikhta hai — 3 mahine se chhote bachche ka rectal `100.4 F` bhi turant doctor wali baat hai.

---

## ☀️❄️ Heat index aur wind chill

<div align="center">

![Weather demo](assets/weather_demo.gif)

*38 °C + 70% humidity → feels like 62.5 °C (Extreme Danger) · phir −25 °C + 40 km/h hawa · phir 20 °C par formula khud mana kar deta hai*

</div>

**Heat index** = temperature + humidity → "feels like". Pasina evaporate nahi ho pata jab humidity zyada ho, isliye sharir thanda nahi ho pata.

**Wind chill** = temperature + hawa → "feels like". Hawa skin ke paas ki garam parat uda deti hai.

Dono NOAA/NWS ke asli formulas hain, aur dono se health risk nikalta hai — heat stroke ka risk band, ya khuli skin kitni der mein freeze ho sakti hai.

> **Sabse important cheez jo yahan seekhi:** har formula ki ek **validity range** hoti hai.
> Wind chill sirf `50 F` (10 °C) se neeche aur `3 mph` se tez hawa par valid hai. Us range ke bahar program jawab dene se **mana kar deta hai** — galat number dene se behtar hai keh dena ki "yeh lagu nahi hota."

---

## 📚 Har number ka source

Koi bhi number yaadash se nahi likha gaya. Sab verify karke liya gaya hai:

| Kya | Source |
|---|---|
| Fever (oral) ≥ 100 °F · adult doctor ≥ 103 °F · 104 °F wali baat | [Mayo Clinic — Fever](https://www.mayoclinic.org/diseases-conditions/fever/symptoms-causes/syc-20352759) |
| Infant rectal thresholds (100.4 °F / 102 °F) | [Mayo Clinic — Fever](https://www.mayoclinic.org/diseases-conditions/fever/symptoms-causes/syc-20352759) |
| Hypothermia < 35 °C · mild 32–35 · moderate 28–32 · severe < 28 | [StatPearls, NIH](https://www.ncbi.nlm.nih.gov/books/NBK545239/) |
| Site offsets (rectal/ear/armpit/forehead vs oral) | [Columbia Doctors](https://www.columbiadoctors.org/health-library/article/fever-temperatures-accuracy-comparison/) |
| Rothfusz heat index equation + humidity adjustments | [NOAA Weather Prediction Center](https://www.wpc.ncep.noaa.gov/html/heatindex_equation.shtml) |
| Heat index bands (80 / 90 / 103 / 125 °F) | [NWS](https://www.weather.gov/ama/heatindex) |
| Wind chill formula + validity range | [NWS](https://www.weather.gov/safety/cold-wind-chill-chart) |
| Frostbite times (−18 / −34 / −51 °F) | [NWS wind chill chart](https://www.weather.gov/media/safety/windchillchart3.pdf) |

---

<details>
<summary><b>🐛 Ek asli bug jo testing ne pakda (click karo)</b></summary>

Pehle maine fever ka boundary `37.8 C` likha tha — kyunki Mayo ki site par `100 F (37.8 C)` likha hai.

Par `37.8 C` sirf **rounded display** hai. Asli conversion:

```
100 F = (100 - 32) x 5/9 = 37.7778 C
```

`37.7778 < 37.8`, isliye theek **100 F ka reading "Normal range" dikhta tha** — jabki source ke hisaab se wo fever hai. Ek rounding se aaya hua correctness bug.

**Fix:** har boundary ab us unit se nikala jaata hai jisme source ne wo likha tha —

```python
FEVER_C     = (100.0 - 32) * 5 / 9    # Mayo Fahrenheit mein deta hai
DOCTOR_C    = (103.0 - 32) * 5 / 9
VERY_HIGH_C = (104.0 - 32) * 5 / 9    # theek 40.0 C nikalta hai
```

Hypothermia ke numbers StatPearls ne Celsius mein diye the, to wo Celsius mein hi rakhe gaye.

**Sabak:** rounded value ko threshold mat banao. Source jis unit mein number deta hai, boundary bhi wahin se nikaalo.

</details>

<details>
<summary><b>🧪 Testing — 72/72 checks pass</b></summary>

| Group | Kya check kiya |
|---|:---:|
| C ↔ F reference points (0, 100, 37, −40, absolute zero) | ✅ |
| Roundtrip `C → F → C` exactly wapas, −273 se 200 tak | ✅ |
| **Wind chill vs NWS chart** — 8 cells, including NWS ka apna example (0 °F + 15 mph = −19 °F) | ✅ |
| Wind chill validity: 51 °F reject / 50 °F accept, 3 mph reject / 3.1 accept | ✅ |
| Frostbite bands −18 / −34 / −51 °F par exactly badalte hain | ✅ |
| **Heat index equation** — independently dobara likhkar match kiya | ✅ |
| Heat index branch: 80 °F se neeche simple formula, upar full regression | ✅ |
| Humidity adjustments sirf stated range mein lagte hain | ✅ |
| Heat index humidity ke saath badhta hai (monotonic) | ✅ |
| Risk bands 80 / 90 / 103 / 125 °F par exactly badalte hain | ✅ |
| Body temp bands dono taraf se — Celsius aur Fahrenheit boundaries | ✅ |
| Site offsets aur straddle detection | ✅ |

</details>

<details>
<summary><b>⚙️ Design decisions</b></summary>

- **Range dikhate hain, single number nahi** — site offset ek range hai, to jawab bhi range hai. Ek fake "average" banana data ko jhootha bana deta.
- **Formula validity enforce ki** — wind chill 50 °F ke upar, heat index 80 °F ke neeche: program mana kar deta hai. NOAA khud kehta hai ki range ke bahar result meaningless ho sakta hai.
- **112 °F ke upar caution** — NOAA ke adjustments 80–112 °F ke liye documented hain, to us se upar program bata deta hai ki number sirf indicative hai.
- **Hypothermia par note** — uski staging **core** temperature par hoti hai. Rectal core ke sabse kareeb hai, isliye baaki sites par program ye caveat dikhata hai.
- **Koi medical advice nahi** — sirf category aur "doctor ko dikhao" wala reference. Fever ka number dekhkar dawai suggest karna galat bhi hai aur risky bhi.
- **km/h aur mph dono** — user ka unit user chune, program andar convert kar le.

</details>

---

## 📁 Files

```
task4_temperature_converter/
├── README.md
├── temperature_converter.py
└── assets/
    ├── body_demo.gif
    └── weather_demo.gif
```

<div align="center">

**Arghya Mahajan** · [github.com/15Arghya2004](https://github.com/15Arghya2004)

</div>
