"""
Task 4 - Health Temperature Toolkit
Cognifyz Technologies | Software Development Internship | Level 2: Intermediate

PDF ki core requirement: user temperature daale aur conversion ki direction
chune (Celsius <-> Fahrenheit). Wo option 1 hai.

Uske upar teen health-related tools banaye gaye hain:
  - Body temperature check (fever / hypothermia), measurement site aur
    umar ke hisaab se
  - Heat index  ("feels like" garmi)  + heat illness risk
  - Wind chill  ("feels like" thand)  + frostbite risk

!! Yeh medical device NAHI hai. Sirf public reference ranges dikhata hai.
   Kisi bhi health decision ke liye doctor se hi baat karo.

Saare numbers ke sources neeche comments mein diye gaye hain.

Python 3.6+ | Sirf standard library.
"""

import math

# =========================================================================
# CONSTANTS  -  har number ka source saath likha hai
# =========================================================================

ABS_ZERO_C = -273.15
ABS_ZERO_F = -459.67

SCALES = {
    "C": ("Celsius", ABS_ZERO_C),
    "F": ("Fahrenheit", ABS_ZERO_F),
}

# --- Body temperature ---------------------------------------------------
# Source: Mayo Clinic - Fever, symptoms & causes
#   traditional average 98.6 F (37 C)
#   oral reading 100 F (37.8 C) ya upar = fever
#   adult: 103 F (39.4 C) par doctor ko call karo
#   104 F (40 C) se neeche wale common viral fever aam taur par harmful nahi
# Source: StatPearls (NIH) - Hypothermia
#   hypothermia = core temp 35 C se neeche
#   mild 32-35 C | moderate 28-32 C | severe 28 C se neeche

# Boundary hamesha us unit se nikala gaya hai jisme source ne wo likha tha.
# Mayo Fahrenheit mein deta hai, StatPearls Celsius mein. Agar hum Mayo ka
# rounded "37.8 C" seedha use karte to theek 100 F ka reading "Normal"
# dikhta - jo galat hai. Isliye 100 F ko yahin convert kiya jaata hai.

FEVER_C      = (100.0 - 32) * 5 / 9    # Mayo: oral 100 F = fever      -> 37.7778 C
DOCTOR_C     = (103.0 - 32) * 5 / 9    # Mayo: adult 103 F = call doc  -> 39.4444 C
VERY_HIGH_C  = (104.0 - 32) * 5 / 9    # Mayo: 104 F se neeche aam     -> 40.0 C

BODY_BANDS = [
    # (is limit se kam ho to yeh band, label, note)
    (28.0,        "Severe hypothermia",   "Medical emergency. Turant help chahiye."),
    (32.0,        "Moderate hypothermia", "Medical emergency. Turant help chahiye."),
    (35.0,        "Mild hypothermia",     "Doctor ko dikhao."),
    (FEVER_C,     "Normal range",         "Sab theek lag raha hai."),
    (DOCTOR_C,    "Fever",                "Aaram karo, paani peeyo, nazar rakho."),
    (VERY_HIGH_C, "High fever",           "Doctor ko call karne wali range."),
    (999.0,       "Very high fever",      "Turant medical help lo."),
]

NORMAL_LOW_C = 35.0
NORMAL_HIGH_C = FEVER_C
AVERAGE_C = 37.0

# Source: Columbia Doctors - Fever Temperatures: Accuracy and Comparison
#   rectal aur ear   : oral se 0.3 se 0.6 C ZYADA
#   armpit aur forehead: oral se 0.3 se 0.6 C KAM
# Isliye site reading ko oral-equivalent banane ke liye ulta jodna padta hai.
# Value ek range hai, ek single number nahi - isliye program bhi range hi
# dikhata hai, jhoothi precision nahi.

SITES = {
    "1": ("Mooh (oral)",        0.0,  0.0),
    "2": ("Bagal (armpit)",    +0.3, +0.6),
    "3": ("Kaan (ear)",        -0.6, -0.3),
    "4": ("Rectal",            -0.6, -0.3),
    "5": ("Maatha (forehead)", +0.3, +0.6),
}

CORE_SITES = ("4",)      # rectal core temperature ke sabse kareeb hai

# Source: Mayo Clinic - infants ke liye alag rectal thresholds
AGE_GROUPS = {
    "1": ("Infant, 3 mahine se chhota",
          "Rectal 100.4 F (38.0 C) ya upar -> TURANT doctor ko dikhao."),
    "2": ("Baby, 3 se 6 mahine",
          "Rectal 102 F (38.9 C) se upar -> doctor ko dikhao."),
    "3": ("Baby, 7 se 24 mahine",
          "Rectal 102 F (38.9 C) se upar aur ek din se zyada -> doctor ko dikhao."),
    "4": ("Bachcha / Bada (2 saal se upar)",
          "103 F (39.4 C) ya upar -> doctor ko call karo."),
}

# --- Heat index ---------------------------------------------------------
# Source: NOAA Weather Prediction Center - Heat Index Equation
# Source: NWS - heat index classification bands

HEAT_BANDS = [
    (90.0,  "Caution",
     "Lambe exposure ya mehnat se thakaan ho sakti hai."),
    (103.0, "Extreme Caution",
     "Heat cramps, heat exhaustion ya heat stroke possible hai."),
    (125.0, "Danger",
     "Heat cramps / heat exhaustion likely, heat stroke possible."),
    (9999.0, "Extreme Danger",
     "Heat stroke ka bahut zyada khatra."),
]
HEAT_MIN_F = 80.0        # is se neeche NWS band define nahi karta
HEAT_TRUSTED_MAX_F = 112.0   # NOAA ke adjustments sirf 80-112 F ke liye documented hain

# --- Wind chill ---------------------------------------------------------
# Source: NWS - Understanding Wind Chill
#   formula sirf T <= 50 F aur wind > 3 mph par valid hai
# Source: NWS wind chill chart - frostbite times

WIND_CHILL_MAX_F = 50.0
WIND_CHILL_MIN_MPH = 3.0

FROSTBITE_BANDS = [
    (-51.0, "5 minute"),
    (-34.0, "10 minute"),
    (-18.0, "30 minute"),
]

MPH_PER_KMH = 0.621371


# =========================================================================
# CONVERSIONS  -  PDF ki core requirement
# =========================================================================

def celsius_to_fahrenheit(celsius):
    """F = (C x 9/5) + 32"""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit):
    """C = (F - 32) x 5/9"""
    return (fahrenheit - 32) * 5 / 9


def to_celsius(value, scale):
    return value if scale == "C" else fahrenheit_to_celsius(value)


def to_fahrenheit(value, scale):
    return value if scale == "F" else celsius_to_fahrenheit(value)


def both(celsius):
    """Ek Celsius value ko 'x C / y F' string banata hai."""
    return "{0} C / {1} F".format(fmt(celsius), fmt(celsius_to_fahrenheit(celsius)))


def fmt(value, places=1):
    """Saaf number - '-0.0' jaisa bewakoof output nahi aata."""
    rounded = round(value, places)
    if rounded == 0:
        rounded = 0.0
    return "{0:.{1}f}".format(rounded, places)


# =========================================================================
# BODY TEMPERATURE
# =========================================================================

def classify_body_temp(celsius):
    """Oral-equivalent Celsius -> (label, note). Bands upar constants mein hain."""
    for limit, label, note in BODY_BANDS:
        if celsius < limit:
            return label, note
    return BODY_BANDS[-1][1], BODY_BANDS[-1][2]


def oral_equivalent(celsius, site_key):
    """
    Site reading ko oral-equivalent range mein badalta hai.
    Ek single number nahi milta kyunki source khud ek range deta hai.
    """
    _, low_adj, high_adj = SITES[site_key]
    return celsius + low_adj, celsius + high_adj


def heat_or_cold_flag(celsius):
    if celsius < NORMAL_LOW_C:
        return "neeche"
    if celsius > NORMAL_HIGH_C:
        return "upar"
    return "andar"


# =========================================================================
# HEAT INDEX  -  NOAA Rothfusz regression
# =========================================================================

def rothfusz(t_f, rh):
    """NOAA ka poora heat index regression. T Fahrenheit mein, RH percent."""
    return (-42.379
            + 2.04901523 * t_f
            + 10.14333127 * rh
            - 0.22475541 * t_f * rh
            - 0.00683783 * t_f * t_f
            - 0.05481717 * rh * rh
            + 0.00122874 * t_f * t_f * rh
            + 0.00085282 * t_f * rh * rh
            - 0.00000199 * t_f * t_f * rh * rh)


def heat_index(t_f, rh):
    """
    NOAA ka poora algorithm:
      1. pehle simple Steadman formula, usko temperature ke saath average karo
      2. agar wo 80 F ya upar hai to poora regression lagao
      3. bahut kam ya bahut zyada humidity par chhota adjustment
    """
    simple = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))
    if (simple + t_f) / 2 < 80.0:
        return simple

    value = rothfusz(t_f, rh)

    if rh < 13 and 80 <= t_f <= 112:
        value -= ((13 - rh) / 4) * math.sqrt((17 - abs(t_f - 95.0)) / 17)
    elif rh > 85 and 80 <= t_f <= 87:
        value += ((rh - 85) / 10) * ((87 - t_f) / 5)

    return value


def heat_risk(hi_f):
    """Heat index (F) -> (label, note). 80 F se neeche NWS band nahi deta."""
    if hi_f < HEAT_MIN_F:
        return None, "80 F se neeche NWS koi risk band define nahi karta."
    for limit, label, note in HEAT_BANDS:
        if hi_f < limit:
            return label, note
    return HEAT_BANDS[-1][1], HEAT_BANDS[-1][2]


# =========================================================================
# WIND CHILL  -  NWS 2001 formula
# =========================================================================

def wind_chill(t_f, wind_mph):
    """WC = 35.74 + 0.6215T - 35.75(V^0.16) + 0.4275T(V^0.16)"""
    v16 = wind_mph ** 0.16
    return 35.74 + 0.6215 * t_f - 35.75 * v16 + 0.4275 * t_f * v16


def wind_chill_valid(t_f, wind_mph):
    """NWS: formula sirf T <= 50 F aur wind > 3 mph par valid hai."""
    if t_f > WIND_CHILL_MAX_F:
        return False, "Formula sirf 50 F (10 C) ya neeche valid hai."
    if wind_mph <= WIND_CHILL_MIN_MPH:
        return False, "Formula ke liye hawa 3 mph (4.8 km/h) se tez honi chahiye."
    return True, ""


def frostbite_time(wc_f):
    """Wind chill (F) -> exposed skin kitni der mein freeze ho sakti hai."""
    for limit, label in FROSTBITE_BANDS:
        if wc_f <= limit:
            return label
    return None


# =========================================================================
# INPUT HELPERS
# =========================================================================

def ask_number(prompt, low=None, high=None):
    """Decimal number leta hai. Galat input pe crash nahi karta."""
    while True:
        raw = input(prompt).strip().rstrip("cCfF%").strip()
        try:
            value = float(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 36.6 ya -12")
            continue
        if low is not None and value < low:
            print("  -> {0} se kam nahi ho sakta.".format(low))
            continue
        if high is not None and value > high:
            print("  -> {0} se zyada nahi ho sakta.".format(high))
            continue
        return value


def ask_scale(prompt="Scale (C ya F): "):
    while True:
        raw = input(prompt).strip().upper()
        if raw in SCALES:
            return raw
        print("  -> C ya F likho.")


def ask_temperature(prompt="Temperature: "):
    """Value + scale leta hai aur absolute zero se neeche reject karta hai."""
    while True:
        scale = ask_scale()
        value = ask_number("{0} ({1}): ".format(prompt.rstrip(": "), scale))
        name, limit = SCALES[scale]
        if value < limit:
            print("  -> Absolute zero ({0} {1}) se neeche possible nahi hai."
                  .format(limit, scale))
            continue
        return value, scale


def ask_from(prompt, options):
    """Numbered dictionary se ek option chunwata hai."""
    print()
    for key in sorted(options):
        print("   {0}) {1}".format(key, options[key][0]))
    while True:
        raw = input(prompt).strip()
        if raw in options:
            return raw
        print("  -> {0} me se ek number likho."
              .format("/".join(sorted(options))))


def ask_yes_no(prompt):
    while True:
        raw = input("{0} (y/n): ".format(prompt)).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  -> y ya n likho.")


def rule(char="-", width=60):
    print("  " + char * width)


# =========================================================================
# ACTIONS
# =========================================================================

def action_convert():
    """PDF ki core requirement: direction chuno aur convert karo."""
    print("\n--- Celsius <-> Fahrenheit ---")
    print("\n   1) Celsius se Fahrenheit")
    print("   2) Fahrenheit se Celsius")

    while True:
        direction = input("\nDirection (1/2): ").strip()
        if direction in ("1", "2"):
            break
        print("  -> 1 ya 2 likho.")

    source = "C" if direction == "1" else "F"
    name, limit = SCALES[source]

    while True:
        value = ask_number("\n{0} mein temperature: ".format(name))
        if value >= limit:
            break
        print("  -> Absolute zero ({0} {1}) se neeche possible nahi hai."
              .format(limit, source))

    print()
    rule()
    if direction == "1":
        result = celsius_to_fahrenheit(value)
        print("  Formula : F = (C x 9/5) + 32")
        print("  Hisaab  : ({0} x 9/5) + 32".format(fmt(value, 2)))
        print("  Result  : {0} C  =  {1} F".format(fmt(value, 2), fmt(result, 2)))
    else:
        result = fahrenheit_to_celsius(value)
        print("  Formula : C = (F - 32) x 5/9")
        print("  Hisaab  : ({0} - 32) x 5/9".format(fmt(value, 2)))
        print("  Result  : {0} F  =  {1} C".format(fmt(value, 2), fmt(result, 2)))
    rule()


def action_body_temp():
    """Fever / hypothermia check, site aur umar ke hisaab se."""
    print("\n--- Body temperature check ---")

    value, scale = ask_temperature("Reading")
    celsius = to_celsius(value, scale)

    site_key = ask_from("Kahan se naapa (1-5): ", SITES)
    age_key = ask_from("Kiska temperature hai (1-4): ", AGE_GROUPS)

    low_c, high_c = oral_equivalent(celsius, site_key)
    low_label, low_note = classify_body_temp(low_c)
    high_label, high_note = classify_body_temp(high_c)

    print()
    rule("=")
    print("  Reading      : {0}".format(both(celsius)))
    print("  Naapa gaya   : {0}".format(SITES[site_key][0]))
    print("  Kiska        : {0}".format(AGE_GROUPS[age_key][0]))
    rule()

    if site_key == "1":
        print("  Oral value   : {0}".format(both(celsius)))
    else:
        print("  Oral jaisa   : {0} se {1} C   ({2} se {3} F)".format(
            fmt(low_c), fmt(high_c),
            fmt(celsius_to_fahrenheit(low_c)), fmt(celsius_to_fahrenheit(high_c))))
        print("                 (source ek range deta hai, ek number nahi)")

    if low_label == high_label:
        print("  Category     : {0}".format(low_label))
        print("  Matlab       : {0}".format(low_note))
    else:
        print("  Category     : {0}  ya  {1}".format(low_label, high_label))
        print("  Matlab       : Reading do band ke beech aa raha hai -")
        print("                 pakka janne ke liye oral ya rectal se naapo.")

    print()
    print("  Normal range : {0} se {1}".format(
        both(NORMAL_LOW_C), both(NORMAL_HIGH_C)))
    print("  Umar ka rule : {0}".format(AGE_GROUPS[age_key][1]))

    if site_key not in CORE_SITES and low_c < NORMAL_LOW_C:
        print()
        print("  Note: hypothermia ki staging CORE temperature par hoti hai.")
        print("        Rectal reading core ke sabse kareeb hoti hai.")

    rule("=")
    print("  Yeh medical device nahi hai. Doctor se hi confirm karo.")


def action_heat_index():
    """Garmi + humidity -> 'feels like' + heat illness risk."""
    print("\n--- Heat index ('feels like' garmi) ---")

    value, scale = ask_temperature("Bahar ka temperature")
    t_f = to_fahrenheit(value, scale)
    rh = ask_number("Relative humidity (0-100 %): ", low=0, high=100)

    hi_f = heat_index(t_f, rh)
    hi_c = fahrenheit_to_celsius(hi_f)
    label, note = heat_risk(hi_f)

    print()
    rule("=")
    print("  Asli temp    : {0}".format(both(to_celsius(value, scale))))
    print("  Humidity     : {0} %".format(fmt(rh, 0)))
    print("  Feels like   : {0}".format(both(hi_c)))
    rule()
    if label is None:
        print("  Risk band    : -")
        print("  Note         : {0}".format(note))
    else:
        print("  Risk band    : {0}".format(label))
        print("  Matlab       : {0}".format(note))
    if t_f > HEAT_TRUSTED_MAX_F:
        rule()
        print("  Caution      : {0} F NOAA ke documented range (80-112 F) se bahar hai.".format(fmt(t_f)))
        print("                 Number sirf indicative maano.")
    rule("=")
    print("  Source: NOAA heat index equation + NWS risk bands.")


def action_wind_chill():
    """Thand + hawa -> 'feels like' + frostbite risk."""
    print("\n--- Wind chill ('feels like' thand) ---")

    value, scale = ask_temperature("Bahar ka temperature")
    t_f = to_fahrenheit(value, scale)

    unit = "1"
    print("\n   1) km/h")
    print("   2) mph")
    while True:
        unit = input("Hawa ki speed ka unit (1/2): ").strip()
        if unit in ("1", "2"):
            break
        print("  -> 1 ya 2 likho.")

    speed = ask_number("Hawa ki speed: ", low=0)
    wind_mph = speed * MPH_PER_KMH if unit == "1" else speed

    ok, reason = wind_chill_valid(t_f, wind_mph)
    print()
    rule("=")
    print("  Asli temp    : {0}".format(both(to_celsius(value, scale))))
    print("  Hawa         : {0} mph".format(fmt(wind_mph)))

    if not ok:
        rule()
        print("  Wind chill   : lagu nahi hota")
        print("  Kyun         : {0}".format(reason))
        rule("=")
        return

    wc_f = wind_chill(t_f, wind_mph)
    wc_c = fahrenheit_to_celsius(wc_f)
    minutes = frostbite_time(wc_f)

    print("  Feels like   : {0}".format(both(wc_c)))
    rule()
    if minutes is None:
        print("  Frostbite    : is level par NWS koi time nahi deta")
    else:
        print("  Frostbite    : khuli skin {0} mein freeze ho sakti hai".format(minutes))
    rule("=")
    print("  Source: NWS wind chill formula + frostbite chart.")


def action_reference():
    """Ready tables - jaldi dekhne ke liye."""
    print("\n--- Reference tables ---")

    print("\n  [1] Celsius <-> Fahrenheit")
    print("\n      CELSIUS   FAHRENHEIT")
    rule("-", 30)
    for c in range(-40, 101, 10):
        print("      {0:>7}   {1:>10}".format(fmt(c, 1), fmt(celsius_to_fahrenheit(c), 1)))
    print("\n      -40 wo ikloti value hai jahan dono scale barabar hain.")

    print("\n  [2] Body temperature bands (oral)")
    print("\n      RANGE                          CATEGORY")
    rule("-", 56)
    previous = -100.0
    for limit, label, _ in BODY_BANDS:
        low_text = "{0} C".format(fmt(previous)) if previous > -100 else "neeche"
        high_text = "{0} C".format(fmt(limit)) if limit < 900 else "upar"
        print("      {0:>10} se {1:<10}        {2}".format(low_text, high_text, label))
        previous = limit

    print("\n  [3] Heat index risk bands (NWS)")
    print("\n      HEAT INDEX (F)      BAND")
    rule("-", 46)
    previous = HEAT_MIN_F
    for limit, label, _ in HEAT_BANDS:
        high_text = fmt(limit, 0) if limit < 9000 else "upar"
        print("      {0:>6} se {1:<8}    {2}".format(fmt(previous, 0), high_text, label))
        previous = limit

    print("\n  [4] Frostbite times (NWS wind chill chart)")
    print("\n      WIND CHILL (F)      EXPOSED SKIN FREEZES IN")
    rule("-", 52)
    for limit, label in FROSTBITE_BANDS:
        print("      {0:>6} ya neeche      {1}".format(fmt(limit, 0), label))


# =========================================================================
# MENU
# =========================================================================

MENU = (
    ("1", "Celsius <-> Fahrenheit convert karo", action_convert),
    ("2", "Body temperature check karo", action_body_temp),
    ("3", "Heat index - garmi kitni lagegi", action_heat_index),
    ("4", "Wind chill - thand kitni lagegi", action_wind_chill),
    ("5", "Reference tables dekho", action_reference),
)


def show_menu():
    print("\n" + "=" * 58)
    print("  HEALTH TEMPERATURE TOOLKIT  -  Cognifyz Task 4")
    print("=" * 58)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    actions = {key: func for key, _, func in MENU}

    print("\nTemperature convert karo, aur health ke hisaab se samjho bhi.")
    print("Yeh medical device nahi hai - sirf public reference ranges dikhata hai.")

    while True:
        show_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            print("\nApna khayal rakho. Bye!")
            break

        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 5 ke beech ka option chuno.")
            continue

        action()


if __name__ == "__main__":
    main()
