"""
Task 5 - Persistent Task Manager (File I/O)
Cognifyz Technologies | Software Development Internship | Level 3: Advanced

Task 3 wala CRUD app, ab data ko file mein save karta hai. Program band
karke dobara kholo to tasks wapas mil jaate hain.

Storage:
  tasks.txt   - primary storage, plain text, ek line = ek task
  tasks.json  - optional export (menu option 6)

Task 3 ki `Task` class jaisi ki taisi hai. Sirf save/load ka layer
upar se joda gaya hai - kyunki to_dict() aur from_dict() wahin bana
diye gaye the.

Python 3.6+ | Sirf standard library.
"""

import json
import os
from datetime import date, datetime

# --------------------------------------------------------------- constants

STATUS_PENDING = "pending"
STATUS_DONE = "done"
STATUSES = (STATUS_PENDING, STATUS_DONE)

PRIORITIES = ("High", "Medium", "Low")
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M:%S"

TITLE_WIDTH = 30

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(HERE, "tasks.txt")
JSON_FILE = os.path.join(HERE, "tasks.json")

SEPARATOR = "|"
FIELD_ORDER = ("id", "title", "description", "priority",
               "due_date", "status", "created_at")
FILE_VERSION = "1"

FILE_HEADER = (
    "# Cognifyz Internship - Task 5 data file\n"
    "# version {0}\n"
    "# {1}\n"
    "# '#' se shuru hone wali lines comment hain.\n"
).format(FILE_VERSION, SEPARATOR.join(FIELD_ORDER))


class StorageError(Exception):
    """File ki koi problem jise user ko samajh aane laayak batana hai."""


# ------------------------------------------------------------------- model

class Task:
    """Ek single to-do item ka blueprint. (Task 3 se bilkul same.)"""

    def __init__(self, task_id, title, description="", priority="Medium",
                 due_date=None, status=STATUS_PENDING, created_at=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = status
        self.created_at = created_at if created_at is not None else datetime.now()

    def is_done(self):
        return self.status == STATUS_DONE

    def mark_done(self):
        self.status = STATUS_DONE

    def is_overdue(self, today=None):
        if self.due_date is None or self.is_done():
            return False
        if today is None:
            today = date.today()
        return self.due_date < today

    def days_left(self, today=None):
        if self.due_date is None:
            return None
        if today is None:
            today = date.today()
        return (self.due_date - today).days

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.strftime(DATE_FMT) if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.strftime(DATETIME_FMT),
        }

    @classmethod
    def from_dict(cls, data):
        due_raw = data.get("due_date")
        created_raw = data.get("created_at")
        return cls(
            task_id=int(data["id"]),
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Medium"),
            due_date=datetime.strptime(due_raw, DATE_FMT).date() if due_raw else None,
            status=data.get("status", STATUS_PENDING),
            created_at=(datetime.strptime(created_raw, DATETIME_FMT)
                        if created_raw else None),
        )

    def __repr__(self):
        return "Task(id={0}, title={1!r}, status={2!r})".format(
            self.id, self.title, self.status)


# =========================================================================
# STORAGE  -  Task 5 ka asli naya hissa
# =========================================================================

# Problem: hum fields ko '|' se alag kar rahe hain. Agar title mein hi '|'
# aa gaya, ya user ne newline paste kar diya, to file ki structure toot
# jayegi aur load karte waqt fields shift ho jayenge.
#
# Solution: escaping. Likhte waqt khatarnaak characters ko badal do,
# padhte waqt wapas asli bana do.
#
#   \   ->  \\      (sabse pehle, warna baaki escapes double ho jayenge)
#   |   ->  \|
#   \n  ->  \n  (do characters: backslash aur n)
#   \r  ->  \r

def escape(text):
    """Ek field ko file mein likhne laayak banata hai."""
    text = text.replace("\\", "\\\\")
    text = text.replace(SEPARATOR, "\\" + SEPARATOR)
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    return text


def unescape(text):
    """escape() ka ulta. Left se right chalta hai, ek baar mein ek pair."""
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            nxt = text[index + 1]
            if nxt == "\\":
                out.append("\\")
                index += 2
                continue
            if nxt == SEPARATOR:
                out.append(SEPARATOR)
                index += 2
                continue
            if nxt == "n":
                out.append("\n")
                index += 2
                continue
            if nxt == "r":
                out.append("\r")
                index += 2
                continue
        out.append(char)
        index += 1
    return "".join(out)


def split_fields(line):
    """
    Line ko fields mein todta hai - par SIRF un '|' par jo escape nahi hue.
    Seedha line.split('|') karna bug hota: '\\|' ko bhi separator maan leta.
    """
    fields = []
    current = []
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line):
            current.append(char)
            current.append(line[index + 1])
            index += 2
            continue
        if char == SEPARATOR:
            fields.append("".join(current))
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    fields.append("".join(current))
    return [unescape(field) for field in fields]


def task_to_line(task):
    """Task object -> file ki ek line."""
    data = task.to_dict()
    parts = []
    for key in FIELD_ORDER:
        value = data[key]
        parts.append("" if value is None else escape(str(value)))
    return SEPARATOR.join(parts)


def line_to_task(line):
    """File ki ek line -> Task object. Galat line par ValueError."""
    fields = split_fields(line)
    if len(fields) != len(FIELD_ORDER):
        raise ValueError("{0} fields chahiye the, {1} mile".format(
            len(FIELD_ORDER), len(fields)))
    data = dict(zip(FIELD_ORDER, fields))
    if data["due_date"] == "":
        data["due_date"] = None
    if data["created_at"] == "":
        data["created_at"] = None
    return Task.from_dict(data)


def backup_path(path):
    """Aisa .bak naam dhoondhta hai jo pehle se maujood na ho."""
    candidate = path + ".bak"
    counter = 1
    while os.path.exists(candidate):
        candidate = "{0}.bak.{1}".format(path, counter)
        counter += 1
    return candidate


def save_tasks(tasks, path=DATA_FILE):
    """
    Atomic write: pehle .tmp file mein likho, phir rename karo.

    Seedha original file par likhne mein khatra hai - agar beech mein
    program band ho gaya to aadhi likhi file hi bachti hai aur purana
    data bhi chala jaata hai. rename ek hi step mein hota hai, isliye
    file ya to purani rehti hai ya poori nayi.
    """
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(FILE_HEADER)
            for task in sorted(tasks, key=lambda item: item.id):
                handle.write(task_to_line(task) + "\n")
        os.replace(temp, path)
    except OSError as exc:
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except OSError:
                pass
        raise StorageError("File save nahi ho paayi: {0}".format(exc))


def load_tasks(path=DATA_FILE):
    """
    File se tasks padhta hai.

    Return: (tasks, message)
      - file nahi hai        -> ([], "pehli baar" wala message)
      - file kharab hai      -> ([], backup bana diya wala message)
      - sab theek            -> (tasks, kitne load hue)

    Padhi na ja sakne wali file (permission wagera) par StorageError.
    """
    if not os.path.exists(path):
        return [], "Koi purani file nahi mili. Pehla task banate hi nayi ban jayegi."

    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw_lines = handle.readlines()
    except UnicodeDecodeError:
        return [], corrupt_recover(path, "file text file lag hi nahi rahi")
    except OSError as exc:
        raise StorageError("File padhi nahi ja saki: {0}".format(exc))

    tasks = []
    seen_ids = set()

    for number, raw in enumerate(raw_lines, start=1):
        line = raw.rstrip("\n").rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            task = line_to_task(line)
        except (ValueError, KeyError) as exc:
            return [], corrupt_recover(
                path, "line {0} padhi nahi ja saki ({1})".format(number, exc))
        if task.id in seen_ids:
            return [], corrupt_recover(
                path, "line {0} par ID {1} do baar aa gaya".format(number, task.id))
        seen_ids.add(task.id)
        tasks.append(task)

    return tasks, "{0} task file se load hue.".format(len(tasks))


def corrupt_recover(path, reason):
    """Kharab file ko bachao, saaf message do, khaali list se shuru karo."""
    backup = backup_path(path)
    try:
        os.replace(path, backup)
    except OSError as exc:
        raise StorageError(
            "File kharab hai ({0}) aur backup bhi nahi ban paaya: {1}".format(
                reason, exc))
    return ("File kharab thi ({0}).\n"
            "  Purani file yahan bacha di gayi hai:\n"
            "    {1}\n"
            "  Khaali list se shuru kar rahe hain.").format(reason, backup)


def export_json(tasks, path=JSON_FILE):
    """Optional export. json library escaping khud sambhal leti hai."""
    payload = {
        "name": "Cognifyz Internship - Task 5 export",
        "version": 1,
        "exported_at": datetime.now().strftime(DATETIME_FMT),
        "count": len(tasks),
        "tasks": [task.to_dict() for task in sorted(tasks, key=lambda t: t.id)],
    }
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.replace(temp, path)
    except OSError as exc:
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except OSError:
                pass
        raise StorageError("JSON export fail ho gaya: {0}".format(exc))


# --------------------------------------------------------------- utilities

def parse_date(text):
    return datetime.strptime(text.strip(), DATE_FMT).date()


def format_date(value):
    return value.strftime(DATE_FMT) if value else "-"


def shorten(text, width):
    if len(text) <= width:
        return text
    return text[:width - 3] + "..."


def next_id(tasks):
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def sort_key(task):
    due = task.due_date if task.due_date else date.max
    return (task.is_done(), PRIORITY_RANK.get(task.priority, 99), due, task.id)


# ------------------------------------------------------------ input helpers

def ask_text(prompt, required=True, default=None):
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        if default is not None:
            return default
        if not required:
            return ""
        print("  -> Yeh khaali nahi ho sakta.")


def ask_choice(prompt, options, default=None):
    lowered = {opt.lower(): opt for opt in options}
    shown = "/".join(options)
    while True:
        raw = input("{0} [{1}]: ".format(prompt, shown)).strip()
        if not raw and default is not None:
            return default
        if raw.lower() in lowered:
            return lowered[raw.lower()]
        print("  -> Inme se ek likho: {0}".format(shown))


def ask_date(prompt, default=None, allow_blank=True):
    while True:
        raw = input(prompt).strip()
        if not raw:
            if allow_blank:
                return default
            print("  -> Date zaroori hai.")
            continue
        try:
            return parse_date(raw)
        except ValueError:
            print("  -> Format galat hai. Aise likho: 2026-08-25")


def ask_int(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 3.")


def ask_yes_no(prompt):
    while True:
        raw = input("{0} (y/n): ".format(prompt)).strip().lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  -> y ya n likho.")


def pick_task(tasks, action):
    if not tasks:
        print("\nAbhi koi task nahi hai. Pehle option 1 se task add karo.")
        return None
    show_table(tasks)
    task_id = ask_int("\n{0} ke liye task ID: ".format(action))
    task = find_task(tasks, task_id)
    if task is None:
        print("  -> ID {0} ka koi task nahi mila.".format(task_id))
        return None
    return task


# ------------------------------------------------------------------ display

def status_box(task):
    return "[x]" if task.is_done() else "[ ]"


def note_for(task):
    if task.is_done():
        return "done"
    left = task.days_left()
    if left is None:
        return "-"
    if left < 0:
        return "OVERDUE {0}d".format(-left)
    if left == 0:
        return "aaj due"
    return "{0} din baaki".format(left)


def show_table(tasks):
    if not tasks:
        print("\n  (list khaali hai)")
        return

    header = "  {0:>3}  {1:3}  {2:8}  {3:{w}}  {4:12}  {5}".format(
        "ID", "ST", "PRIORITY", "TITLE", "DUE", "NOTE", w=TITLE_WIDTH)
    print()
    print(header)
    print("  " + "-" * (len(header) - 2))

    for task in sorted(tasks, key=sort_key):
        print("  {0:>3}  {1:3}  {2:8}  {3:{w}}  {4:12}  {5}".format(
            task.id, status_box(task), task.priority,
            shorten(task.title, TITLE_WIDTH), format_date(task.due_date),
            note_for(task), w=TITLE_WIDTH))

    done = sum(1 for t in tasks if t.is_done())
    overdue = sum(1 for t in tasks if t.is_overdue())
    print("\n  Total: {0} | Done: {1} | Pending: {2} | Overdue: {3}".format(
        len(tasks), done, len(tasks) - done, overdue))


def show_detail(task):
    print("\n  ID          : {0}".format(task.id))
    print("  Title       : {0}".format(task.title))
    print("  Description : {0}".format(task.description or "-"))
    print("  Priority    : {0}".format(task.priority))
    print("  Status      : {0}".format(task.status))
    print("  Due date    : {0}".format(format_date(task.due_date)))
    print("  Created at  : {0}".format(task.created_at.strftime(DATETIME_FMT)))
    if task.is_overdue():
        print("  !! Yeh task overdue hai.")


# --------------------------------------------------------------- C R U D

def persist(tasks):
    """Har badlaav ke turant baad save. Isse 'save karna bhool gaya' bug hi nahi hota."""
    try:
        save_tasks(tasks)
        print("  (file mein save ho gaya)")
    except StorageError as exc:
        print("  !! {0}".format(exc))
        print("  !! Badlaav sirf memory mein hai. File theek karke dobara koshish karo.")


def create_task(tasks):
    print("\n--- Naya task ---")
    title = ask_text("Title: ")
    description = ask_text("Description (Enter = skip): ", required=False)
    priority = ask_choice("Priority", PRIORITIES, default="Medium")
    due = ask_date("Due date YYYY-MM-DD (Enter = koi nahi): ")

    task = Task(next_id(tasks), title, description, priority, due)
    tasks.append(task)
    print("\nTask #{0} add ho gaya.".format(task.id))
    persist(tasks)


def read_tasks(tasks):
    if not tasks:
        print("\nAbhi koi task nahi hai. Pehle option 1 se task add karo.")
        return

    view = ask_choice("Kaun se dikhaun", ("All", "Pending", "Done", "Overdue"),
                      default="All")
    if view == "Pending":
        subset = [t for t in tasks if not t.is_done()]
    elif view == "Done":
        subset = [t for t in tasks if t.is_done()]
    elif view == "Overdue":
        subset = [t for t in tasks if t.is_overdue()]
    else:
        subset = tasks

    if not subset:
        print("\n  ({0} filter mein koi task nahi)".format(view))
        return

    show_table(subset)

    if ask_yes_no("\nKisi ek task ki poori detail dekhni hai"):
        task_id = ask_int("Task ID: ")
        task = find_task(subset, task_id)
        if task is None:
            print("  -> ID {0} is list mein nahi hai.".format(task_id))
        else:
            show_detail(task)


def update_task(tasks):
    task = pick_task(tasks, "Update")
    if task is None:
        return

    show_detail(task)
    field = ask_choice("\nKya badalna hai",
                       ("Title", "Description", "Priority", "Due", "Status"))

    if field == "Title":
        task.title = ask_text("Naya title [{0}]: ".format(task.title),
                              default=task.title)
    elif field == "Description":
        task.description = ask_text("Nayi description (Enter = khaali): ",
                                    required=False)
    elif field == "Priority":
        task.priority = ask_choice("Nayi priority", PRIORITIES,
                                   default=task.priority)
    elif field == "Due":
        task.due_date = ask_date(
            "Nayi due date YYYY-MM-DD (Enter = hata do): ", default=None)
    elif field == "Status":
        task.status = ask_choice("Naya status", STATUSES, default=task.status)

    print("\nTask #{0} update ho gaya.".format(task.id))
    persist(tasks)
    show_detail(task)


def complete_task(tasks):
    task = pick_task(tasks, "Done mark karne")
    if task is None:
        return
    if task.is_done():
        print("\nTask #{0} pehle se hi done hai.".format(task.id))
        return
    task.mark_done()
    print("\nTask #{0} done mark ho gaya: {1}".format(task.id, task.title))
    persist(tasks)


def delete_task(tasks):
    task = pick_task(tasks, "Delete")
    if task is None:
        return
    show_detail(task)
    if not ask_yes_no("\nPakka delete karna hai"):
        print("Delete cancel kar diya.")
        return
    tasks.remove(task)
    print("Task #{0} delete ho gaya.".format(task.id))
    persist(tasks)


# ------------------------------------------------------------ file actions

def do_export(tasks):
    if not tasks:
        print("\nExport karne ke liye pehle koi task banao.")
        return
    try:
        export_json(tasks)
    except StorageError as exc:
        print("  !! {0}".format(exc))
        return
    print("\n{0} task JSON mein export ho gaye:".format(len(tasks)))
    print("  {0}".format(JSON_FILE))


def file_info(tasks):
    print("\n--- File ki jaankari ---")
    for label, path in (("Text storage", DATA_FILE), ("JSON export", JSON_FILE)):
        print("\n  {0}".format(label))
        print("    Path   : {0}".format(path))
        if not os.path.exists(path):
            print("    Status : abhi bani nahi hai")
            continue
        try:
            size = os.path.getsize(path)
            changed = datetime.fromtimestamp(os.path.getmtime(path))
        except OSError as exc:
            print("    Status : padhi nahi ja saki ({0})".format(exc))
            continue
        print("    Status : maujood hai")
        print("    Size   : {0} bytes".format(size))
        print("    Changed: {0}".format(changed.strftime(DATETIME_FMT)))

    print("\n  Memory mein abhi {0} task hain.".format(len(tasks)))
    print("\n  tasks.txt ka format:")
    print("    {0}".format(SEPARATOR.join(FIELD_ORDER)))
    print("    '#' se shuru lines comment hain.")
    print("    '|' agar kisi title mein ho to file mein '\\|' likha jaata hai.")


# ------------------------------------------------------------------- menu

MENU = (
    ("1", "Naya task banao (Create)", create_task),
    ("2", "Tasks dekho (Read)", read_tasks),
    ("3", "Task edit karo (Update)", update_task),
    ("4", "Task done mark karo", complete_task),
    ("5", "Task delete karo (Delete)", delete_task),
    ("6", "JSON mein export karo", do_export),
    ("7", "File ki jaankari", file_info),
)


def show_menu():
    print("\n" + "=" * 52)
    print("  PERSISTENT TASK MANAGER  -  Cognifyz Task 5")
    print("=" * 52)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    actions = {key: func for key, _, func in MENU}

    print("\nWelcome! Yeh task manager data file mein save karta hai.")
    print("Storage: {0}".format(DATA_FILE))

    try:
        tasks, message = load_tasks()
    except StorageError as exc:
        print("\n!! {0}".format(exc))
        print("!! Program band kar raha hoon taaki data par khatra na ho.")
        return

    print("\n{0}".format(message))

    while True:
        show_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            print("\nBye! {0} task file mein save hain.".format(len(tasks)))
            break

        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 7 ke beech ka option chuno.")
            continue

        action(tasks)


if __name__ == "__main__":
    main()
