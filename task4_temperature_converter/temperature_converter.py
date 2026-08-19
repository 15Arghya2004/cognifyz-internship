"""
Task 4 - Temperature Converter
Cognifyz Technologies | Software Development Internship | Level 2: Intermediate

User temperature daalta hai aur conversion ki direction chunta hai
(Celsius -> Fahrenheit ya Fahrenheit -> Celsius).

Python 3.6+ | Sirf standard library.
"""

# --------------------------------------------------------------- constants

ABS_ZERO_C = -273.15          # Celsius mein absolute zero
ABS_ZERO_F = -459.67          # Fahrenheit mein wahi point

SCALE_LIMITS = {
    "C": (ABS_ZERO_C, "Celsius"),
    "F": (ABS_ZERO_F, "Fahrenheit"),
}


# ------------------------------------------------------------- conversions

def celsius_to_fahrenheit(celsius):
    """F = (C x 9/5) + 32"""
    return (celsius * 9 / 5) + 32


def fahrenheit_to_celsius(fahrenheit):
    """C = (F - 32) x 5/9"""
    return (fahrenheit - 32) * 5 / 9


# ---------------------------------------------------------------- helpers

def describe(celsius):
    """Value ko rozmarra ke reference se jodta hai."""
    if celsius <= ABS_ZERO_C:
        return "absolute zero"
    if celsius < -20:
        return "extreme thand"
    if celsius < 0:
        return "freezing se neeche"
    if celsius == 0:
        return "paani jamta hai"
    if celsius < 15:
        return "thand"
    if celsius < 26:
        return "aaram dayak"
    if celsius < 35:
        return "garmi"
    if celsius < 100:
        return "bahut garam"
    if celsius == 100:
        return "paani ubalta hai (sea level)"
    return "boiling se upar"


def is_below_absolute_zero(value, scale):
    limit = SCALE_LIMITS[scale][0]
    return value < limit


def fmt(value):
    """2 decimal tak, par -0.00 jaisa bewakoof output na aaye."""
    rounded = round(value, 2)
    if rounded == 0:
        rounded = 0.0
    return "{0:.2f}".format(rounded)


# ------------------------------------------------------------ input helpers

def ask_number(prompt):
    """Decimal number leta hai. Galat input pe crash nahi karta."""
    while True:
        raw = input(prompt).strip()
        if raw.endswith(("c", "C", "f", "F")):     # "25c" bhi chal jaaye
            raw = raw[:-1].strip()
        try:
            return float(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 36.6 ya -12")


def ask_temperature(scale):
    """Number leta hai aur absolute zero se neeche wale value reject karta hai."""
    limit, name = SCALE_LIMITS[scale]
    while True:
        value = ask_number("{0} mein temperature: ".format(name))
        if is_below_absolute_zero(value, scale):
            print("  -> {0} se neeche temperature possible nahi hai "
                  "(absolute zero = {1}{2}).".format(name, limit, scale))
            continue
        return value


# ------------------------------------------------------------------ actions

def convert_c_to_f():
    celsius = ask_temperature("C")
    fahrenheit = celsius_to_fahrenheit(celsius)
    print("\n  Formula : F = (C x 9/5) + 32")
    print("  Hisaab  : ({0} x 9/5) + 32".format(fmt(celsius)))
    print("  Result  : {0} C  =  {1} F   ({2})".format(
        fmt(celsius), fmt(fahrenheit), describe(celsius)))


def convert_f_to_c():
    fahrenheit = ask_temperature("F")
    celsius = fahrenheit_to_celsius(fahrenheit)
    print("\n  Formula : C = (F - 32) x 5/9")
    print("  Hisaab  : ({0} - 32) x 5/9".format(fmt(fahrenheit)))
    print("  Result  : {0} F  =  {1} C   ({2})".format(
        fmt(fahrenheit), fmt(celsius), describe(celsius)))


def reference_table():
    """Jaldi check karne ke liye ek ready table."""
    print("\n  CELSIUS   FAHRENHEIT   MATLAB")
    print("  " + "-" * 46)
    for celsius in range(-40, 101, 10):
        print("  {0:>7}   {1:>10}   {2}".format(
            fmt(celsius), fmt(celsius_to_fahrenheit(celsius)),
            describe(celsius)))
    print("\n  Note: -40 wo ikloti value hai jahan dono scale barabar hote hain.")


# -------------------------------------------------------------------- menu

MENU = (
    ("1", "Celsius se Fahrenheit", convert_c_to_f),
    ("2", "Fahrenheit se Celsius", convert_f_to_c),
    ("3", "Reference table dekho", reference_table),
)


def show_menu():
    print("\n" + "=" * 46)
    print("  TEMPERATURE CONVERTER  -  Cognifyz Task 4")
    print("=" * 46)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    actions = {key: func for key, _, func in MENU}
    while True:
        show_menu()
        choice = input("\nChoice: ").strip()
        if choice == "0":
            print("\nBye!")
            break
        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 3 ke beech ka option chuno.")
            continue
        action()


if __name__ == "__main__":
    main()
