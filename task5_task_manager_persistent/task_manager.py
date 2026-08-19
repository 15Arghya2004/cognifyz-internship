"""
Task 5 - Persistent Task Manager with Reminders
Cognifyz Technologies | Software Development Internship | Level 3: Advanced

Task 3 wala CRUD app, ab:
  - data ek constant JSON file mein rehta hai (tasks.json)
  - har baar khulte hi briefing milti hai: kya overdue hai, kya aaj due hai,
    kya agle kuch din mein aa raha hai
  - pichhli visit ke baad kya badla, wo bhi batata hai
  - --check mode se Windows Task Scheduler ke saath roz apne aap chal sakta hai

Yeh khud jaakar koi kaam nahi karta - sirf yaad dilata hai ki kya karna hai
aur kab tak.

Files:
  tasks.json  - asli storage (ek hi constant file, sab kuch isme)
  tasks.txt   - optional text export (menu option 7)

Chalane ke tareeke:
  python task_manager.py            <- poora app
  python task_manager.py --check    <- sirf briefing, phir band

Python 3.6+ | Sirf standard library.
"""

import json
import os
import sys
import textwrap
from datetime import date, datetime, timedelta

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
STORE_FILE = os.path.join(HERE, "tasks.json")
TEXT_FILE = os.path.join(HERE, "tasks.txt")

STORE_VERSION = 2
DEFAULT_REMIND_DAYS = 3
MAX_REMIND_DAYS = 60

# tasks.txt export ka format (v1 mein 7 fields the, ab completed_at bhi hai)
SEPARATOR = "|"
TEXT_FIELDS_V1 = ("id", "title", "description", "priority",
                  "due_date", "status", "created_at")
TEXT_FIELDS_V2 = TEXT_FIELDS_V1 + ("completed_at",)

TEXT_HEADER = (
    "# Cognifyz Internship - Task 5 text export\n"
    "# version 2\n"
    "# {0}\n"
    "# '#' se shuru hone wali lines comment hain.\n"
).format(SEPARATOR.join(TEXT_FIELDS_V2))


class StorageError(Exception):
    """File ki koi problem jise user ko samajh aane laayak batana hai."""


# ------------------------------------------------------------------- model

class Task:
    """Ek single to-do item ka blueprint."""

    def __init__(self, task_id, title, description="", priority="Medium",
                 due_date=None, status=STATUS_PENDING, created_at=None,
                 completed_at=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.status = status
        self.created_at = created_at if created_at is not None else datetime.now()
        self.completed_at = completed_at

    # --- behaviour ---

    def is_done(self):
        return self.status == STATUS_DONE

    def mark_done(self, when=None):
        self.status = STATUS_DONE
        self.completed_at = when if when is not None else datetime.now()

    def mark_pending(self):
        self.status = STATUS_PENDING
        self.completed_at = None

    def set_status(self, status, when=None):
        """Status badlo aur completed_at ko us se consistent rakho."""
        if status == STATUS_DONE:
            if not self.is_done():
                self.mark_done(when)
        else:
            self.mark_pending()

    def is_overdue(self, today=None):
        if self.due_date is None or self.is_done():
            return False
        if today is None:
            today = date.today()
        return self.due_date < today

    def is_due_today(self, today=None):
        if self.due_date is None or self.is_done():
            return False
        if today is None:
            today = date.today()
        return self.due_date == today

    def days_left(self, today=None):
        if self.due_date is None:
            return None
        if today is None:
            today = date.today()
        return (self.due_date - today).days

    def became_overdue_after(self, moment, today=None):
        """Kya iski deadline 'moment' ke baad nikli hai (aur abhi tak pending hai)?"""
        if not self.is_overdue(today):
            return False
        if moment is None:
            return False
        return self.due_date >= moment.date()

    # --- serialisation ---

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date.strftime(DATE_FMT) if self.due_date else None,
            "status": self.status,
            "created_at": self.created_at.strftime(DATETIME_FMT),
            "completed_at": (self.completed_at.strftime(DATETIME_FMT)
                             if self.completed_at else None),
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            task_id=int(data["id"]),
            title=data["title"],
            # 'or' isliye, 'get(key, default)' nahi: agar key maujood ho par
            # value None ho (file se aane par hota hai) to default lagna chahiye.
            description=data.get("description") or "",
            priority=data.get("priority") or "Medium",
            due_date=parse_date_or_none(data.get("due_date")),
            status=data.get("status") or STATUS_PENDING,
            created_at=parse_datetime_or_none(data.get("created_at")),
            completed_at=parse_datetime_or_none(data.get("completed_at")),
        )

    def __repr__(self):
        return "Task(id={0}, title={1!r}, status={2!r})".format(
            self.id, self.title, self.status)


# --------------------------------------------------------------- parsing

def parse_date_or_none(text):
    if text is None or text == "":
        return None
    return datetime.strptime(str(text).strip(), DATE_FMT).date()


def parse_datetime_or_none(text):
    if text is None or text == "":
        return None
    return datetime.strptime(str(text).strip(), DATETIME_FMT)


def parse_date(text):
    return datetime.strptime(text.strip(), DATE_FMT).date()


def format_date(value):
    return value.strftime(DATE_FMT) if value else "-"


def format_moment(value):
    return value.strftime(DATETIME_FMT) if value else "-"


def human_gap(then, now):
    """Do time ke beech ka fark aam bhaasha mein."""
    if then is None:
        return "pehli baar"
    seconds = (now - then).total_seconds()
    if seconds < 0:
        return "abhi abhi"
    minutes = int(seconds // 60)
    if minutes < 1:
        return "abhi abhi"
    if minutes < 60:
        return "{0} minute pehle".format(minutes)
    hours = minutes // 60
    if hours < 24:
        return "{0} ghante pehle".format(hours)
    days = hours // 24
    if days == 1:
        return "kal"
    return "{0} din pehle".format(days)


# =========================================================================
# STORAGE  -  ek hi constant JSON file
# =========================================================================

def default_meta():
    now = datetime.now()
    return {
        "created_at": now.strftime(DATETIME_FMT),
        "last_opened": None,
        "open_count": 0,
        "remind_before_days": DEFAULT_REMIND_DAYS,
    }


def backup_path(path):
    """Aisa .bak naam dhoondhta hai jo pehle se maujood na ho."""
    candidate = path + ".bak"
    counter = 1
    while os.path.exists(candidate):
        candidate = "{0}.bak.{1}".format(path, counter)
        counter += 1
    return candidate


def atomic_write(path, text):
    """
    Pehle .tmp file mein likho, phir rename karo.

    Seedha original par likhne mein khatra hai - beech mein program band ho
    gaya to aadhi file bachti hai aur purana data bhi chala jaata hai.
    os.replace ek hi step mein hota hai: file ya poori purani rehti hai
    ya poori nayi.
    """
    temp = path + ".tmp"
    try:
        with open(temp, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(temp, path)
    except OSError as exc:
        if os.path.exists(temp):
            try:
                os.remove(temp)
            except OSError:
                pass
        raise StorageError("File likhi nahi ja saki: {0}".format(exc))


def save_store(tasks, meta, path=STORE_FILE):
    """Poora store (meta + tasks) ek JSON file mein."""
    payload = {
        "name": "Cognifyz Internship - Task 5 task store",
        "version": STORE_VERSION,
        "meta": meta,
        "tasks": [task.to_dict() for task in sorted(tasks, key=lambda t: t.id)],
    }
    atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def corrupt_recover(path, reason):
    """Kharab file ko bachao, saaf message do, khaali se shuru karo."""
    backup = backup_path(path)
    try:
        os.replace(path, backup)
    except OSError as exc:
        raise StorageError(
            "File kharab hai ({0}) aur backup bhi nahi ban paaya: {1}".format(
                reason, exc))
    # Reason mein kabhi-kabhi lamba parser error aa jaata hai, isliye wrap.
    wrapped = textwrap.fill(reason, width=64,
                            initial_indent="    ", subsequent_indent="    ")
    return ("File kharab thi:\n"
            "{0}\n"
            "  Purani file yahan bacha di gayi hai:\n"
            "    {1}\n"
            "  Khaali list se shuru kar rahe hain.").format(wrapped, backup)


def read_store(path=STORE_FILE):
    """
    JSON store padhta hai.
    Return: (tasks, meta, message). Kharab file par backup + khaali start.
    """
    try:
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (ValueError, UnicodeDecodeError) as exc:
        return [], default_meta(), corrupt_recover(
            path, "JSON padha nahi ja saka ({0})".format(exc))
    except OSError as exc:
        raise StorageError("File padhi nahi ja saki: {0}".format(exc))

    if not isinstance(payload, dict) or not isinstance(payload.get("tasks"), list):
        return [], default_meta(), corrupt_recover(
            path, "file ka structure galat hai")

    meta = default_meta()
    if isinstance(payload.get("meta"), dict):
        meta.update(payload["meta"])

    tasks = []
    seen = set()
    for index, item in enumerate(payload["tasks"], start=1):
        try:
            task = Task.from_dict(item)
        except (ValueError, KeyError, TypeError) as exc:
            return [], default_meta(), corrupt_recover(
                path, "task {0} padha nahi ja saka ({1})".format(index, exc))
        if task.id in seen:
            return [], default_meta(), corrupt_recover(
                path, "ID {0} do baar aa gaya".format(task.id))
        seen.add(task.id)
        tasks.append(task)

    return tasks, meta, "{0} task load hue.".format(len(tasks))


# ------------------------------------------------- purani tasks.txt migration

def escape(text):
    """Text export ke liye - '|' aur newline ko surakshit banata hai."""
    text = text.replace("\\", "\\\\")          # backslash sabse pehle
    text = text.replace(SEPARATOR, "\\" + SEPARATOR)
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    return text


def unescape(text):
    out = []
    index = 0
    while index < len(text):
        char = text[index]
        if char == "\\" and index + 1 < len(text):
            nxt = text[index + 1]
            if nxt == "\\":
                out.append("\\"); index += 2; continue
            if nxt == SEPARATOR:
                out.append(SEPARATOR); index += 2; continue
            if nxt == "n":
                out.append("\n"); index += 2; continue
            if nxt == "r":
                out.append("\r"); index += 2; continue
        out.append(char)
        index += 1
    return "".join(out)


def split_fields(line):
    """Sirf un '|' par todta hai jo escape nahi hue."""
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
    data = task.to_dict()
    parts = []
    for key in TEXT_FIELDS_V2:
        value = data[key]
        parts.append("" if value is None else escape(str(value)))
    return SEPARATOR.join(parts)


def line_to_task(line):
    """v1 (7 fields) aur v2 (8 fields) dono padh leta hai."""
    fields = split_fields(line)
    if len(fields) == len(TEXT_FIELDS_V1):
        names = TEXT_FIELDS_V1
    elif len(fields) == len(TEXT_FIELDS_V2):
        names = TEXT_FIELDS_V2
    else:
        raise ValueError("{0} ya {1} fields chahiye the, {2} mile".format(
            len(TEXT_FIELDS_V1), len(TEXT_FIELDS_V2), len(fields)))
    # Khaali string sirf un fields mein 'None' banti hai jo sach mein
    # nullable hain. title/description ke liye "" ka matlab "khaali", "gayab" nahi.
    nullable = ("due_date", "created_at", "completed_at")
    data = {}
    for name, value in zip(names, fields):
        data[name] = None if (value == "" and name in nullable) else value
    return Task.from_dict(data)


def read_text_file(path=TEXT_FILE):
    """Purani tasks.txt padhta hai. Sirf migration ke liye."""
    with open(path, "r", encoding="utf-8") as handle:
        lines = handle.readlines()
    tasks = []
    for number, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n").rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        try:
            tasks.append(line_to_task(line))
        except (ValueError, KeyError) as exc:
            raise ValueError("line {0}: {1}".format(number, exc))
    return tasks


def export_text(tasks, path=TEXT_FILE):
    body = TEXT_HEADER
    for task in sorted(tasks, key=lambda t: t.id):
        body += task_to_line(task) + "\n"
    atomic_write(path, body)


def load_or_migrate(store_path=STORE_FILE, text_path=TEXT_FILE):
    """
    Store kholta hai. Agar tasks.json nahi hai par purani tasks.txt hai,
    to usko padhkar JSON mein badal deta hai - taaki purana data na khoye.
    """
    if os.path.exists(store_path):
        return read_store(store_path)

    if os.path.exists(text_path):
        try:
            tasks = read_text_file(text_path)
        except (ValueError, OSError, UnicodeDecodeError) as exc:
            return [], default_meta(), (
                "Purani tasks.txt padhi nahi ja saki ({0}).\n"
                "  Use chhua nahi gaya. Khaali list se shuru kar rahe hain.").format(exc)

        meta = default_meta()
        save_store(tasks, meta, store_path)
        moved = text_path + ".migrated"
        note = ""
        try:
            if not os.path.exists(moved):
                os.replace(text_path, moved)
                note = "\n  Purani file yahan rakh di gayi: {0}".format(moved)
        except OSError:
            note = "\n  (purani tasks.txt jaise ki taisi hai)"
        return tasks, meta, (
            "Purani tasks.txt se {0} task tasks.json mein le aaye.{1}"
        ).format(len(tasks), note)

    return [], default_meta(), "Nayi file banegi. Pehla task banate hi save ho jayegi."


# =========================================================================
# REMINDER ENGINE
# =========================================================================

def build_briefing(tasks, meta, today=None, now=None):
    """
    Saara reminder-related hisaab ek jagah. Koi printing nahi -
    isse test karna aasaan rehta hai.
    """
    if today is None:
        today = date.today()
    if now is None:
        now = datetime.now()

    window = meta.get("remind_before_days", DEFAULT_REMIND_DAYS)
    try:
        window = int(window)
    except (TypeError, ValueError):
        window = DEFAULT_REMIND_DAYS
    window = max(0, min(window, MAX_REMIND_DAYS))

    last_opened = parse_datetime_or_none(meta.get("last_opened"))
    horizon = today + timedelta(days=window)

    pending = [t for t in tasks if not t.is_done()]

    overdue = sorted([t for t in pending if t.is_overdue(today)],
                     key=lambda t: (t.due_date, PRIORITY_RANK.get(t.priority, 9)))
    due_today = sorted([t for t in pending if t.is_due_today(today)],
                       key=lambda t: PRIORITY_RANK.get(t.priority, 9))
    upcoming = sorted([t for t in pending
                       if t.due_date is not None and today < t.due_date <= horizon],
                      key=lambda t: (t.due_date, PRIORITY_RANK.get(t.priority, 9)))
    no_deadline = [t for t in pending if t.due_date is None]

    newly_overdue = [t for t in overdue if t.became_overdue_after(last_opened, today)]
    completed_since = [t for t in tasks
                       if t.completed_at is not None
                       and last_opened is not None
                       and t.completed_at > last_opened]
    created_since = [t for t in tasks
                     if last_opened is not None and t.created_at > last_opened]

    return {
        "today": today,
        "now": now,
        "window": window,
        "last_opened": last_opened,
        "open_count": meta.get("open_count", 0),
        "overdue": overdue,
        "due_today": due_today,
        "upcoming": upcoming,
        "no_deadline": no_deadline,
        "pending_count": len(pending),
        "done_count": len(tasks) - len(pending),
        "total": len(tasks),
        "newly_overdue": newly_overdue,
        "completed_since": completed_since,
        "created_since": created_since,
    }


def needs_attention(briefing):
    """True agar aaj kuch aisa hai jise dekhna zaroori hai."""
    return bool(briefing["overdue"] or briefing["due_today"])


def briefing_line(task, today):
    left = task.days_left(today)
    if left is None:
        when = "koi deadline nahi"
    elif left < 0:
        when = "{0} din se overdue".format(-left)
    elif left == 0:
        when = "aaj due"
    elif left == 1:
        when = "kal due"
    else:
        when = "{0} din baad".format(left)
    title = task.title if len(task.title) <= 34 else task.title[:31] + "..."
    return "     #{0:<3} {1:34}  {2:8}  {3}".format(
        task.id, title, task.priority, when)


def render_briefing(briefing):
    """Briefing ko screen par dikhata hai."""
    today = briefing["today"]

    print()
    print("=" * 62)
    print("  AAJ KA BRIEFING  -  {0}".format(today.strftime("%A, %d %B %Y")))
    print("=" * 62)

    if briefing["total"] == 0:
        print("\n  Abhi koi task nahi hai. Option 1 se pehla task banao.")
        return

    if briefing["last_opened"] is None:
        print("\n  Pehli baar khola hai. Swagat hai!")
    else:
        print("\n  Pichhli baar: {0}   (kul {1} baar khola)".format(
            human_gap(briefing["last_opened"], briefing["now"]),
            briefing["open_count"]))

    if briefing["overdue"]:
        print("\n  !! OVERDUE ({0})".format(len(briefing["overdue"])))
        for task in briefing["overdue"]:
            print(briefing_line(task, today))

    if briefing["due_today"]:
        print("\n  >> AAJ DUE ({0})".format(len(briefing["due_today"])))
        for task in briefing["due_today"]:
            print(briefing_line(task, today))

    if briefing["upcoming"]:
        print("\n  .. AGLE {0} DIN ({1})".format(
            briefing["window"], len(briefing["upcoming"])))
        for task in briefing["upcoming"]:
            print(briefing_line(task, today))

    if not (briefing["overdue"] or briefing["due_today"] or briefing["upcoming"]):
        print("\n  Koi deadline sar par nahi hai. Aaram se.")

    changes = []
    if briefing["newly_overdue"]:
        changes.append("{0} overdue ho gaye".format(len(briefing["newly_overdue"])))
    if briefing["completed_since"]:
        changes.append("{0} complete hue".format(len(briefing["completed_since"])))
    if briefing["created_since"]:
        changes.append("{0} naye bane".format(len(briefing["created_since"])))
    if changes and briefing["last_opened"] is not None:
        print("\n  Pichhli visit ke baad: {0}.".format(", ".join(changes)))

    print("\n  Kul {0} task | {1} pending | {2} done | {3} bina deadline".format(
        briefing["total"], briefing["pending_count"],
        briefing["done_count"], len(briefing["no_deadline"])))
    print("=" * 62)


# --------------------------------------------------------------- utilities

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


def ask_int(prompt, low=None, high=None):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("  -> Sirf number likho, jaise 3.")
            continue
        if low is not None and value < low:
            print("  -> {0} se kam nahi.".format(low))
            continue
        if high is not None and value > high:
            print("  -> {0} se zyada nahi.".format(high))
            continue
        return value


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
    print("\n  ID           : {0}".format(task.id))
    print("  Title        : {0}".format(task.title))
    print("  Description  : {0}".format(task.description or "-"))
    print("  Priority     : {0}".format(task.priority))
    print("  Status       : {0}".format(task.status))
    print("  Due date     : {0}".format(format_date(task.due_date)))
    print("  Created at   : {0}".format(format_moment(task.created_at)))
    print("  Completed at : {0}".format(format_moment(task.completed_at)))
    if task.is_overdue():
        print("  !! Yeh task overdue hai.")


# --------------------------------------------------------------- C R U D

class Session:
    """Tasks + meta ek saath, taaki har jagah dono pass na karne padein."""

    def __init__(self, tasks, meta):
        self.tasks = tasks
        self.meta = meta

    def persist(self, quiet=False):
        try:
            save_store(self.tasks, self.meta)
            if not quiet:
                print("  (tasks.json mein save ho gaya)")
        except StorageError as exc:
            print("  !! {0}".format(exc))
            print("  !! Badlaav sirf memory mein hai.")


def create_task(session):
    print("\n--- Naya task ---")
    title = ask_text("Title: ")
    description = ask_text("Description (Enter = skip): ", required=False)
    priority = ask_choice("Priority", PRIORITIES, default="Medium")
    due = ask_date("Due date YYYY-MM-DD (Enter = koi nahi): ")

    task = Task(next_id(session.tasks), title, description, priority, due)
    session.tasks.append(task)
    print("\nTask #{0} add ho gaya.".format(task.id))
    if due is not None:
        left = task.days_left()
        if left < 0:
            print("  Dhyaan do: yeh date nikal chuki hai.")
        else:
            print("  Deadline tak {0} din hain.".format(left))
    session.persist()


def read_tasks(session):
    tasks = session.tasks
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


def update_task(session):
    task = pick_task(session.tasks, "Update")
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
        task.set_status(ask_choice("Naya status", STATUSES, default=task.status))

    print("\nTask #{0} update ho gaya.".format(task.id))
    session.persist()
    show_detail(task)


def complete_task(session):
    task = pick_task(session.tasks, "Done mark karne")
    if task is None:
        return
    if task.is_done():
        print("\nTask #{0} pehle se hi done hai ({1}).".format(
            task.id, format_moment(task.completed_at)))
        return
    task.mark_done()
    print("\nTask #{0} done mark ho gaya: {1}".format(task.id, task.title))
    if task.due_date is not None:
        left = task.days_left()
        if left < 0:
            print("  (deadline se {0} din baad)".format(-left))
        elif left == 0:
            print("  (theek deadline wale din)")
        else:
            print("  (deadline se {0} din pehle - shabaash)".format(left))
    session.persist()


def delete_task(session):
    task = pick_task(session.tasks, "Delete")
    if task is None:
        return
    show_detail(task)
    if not ask_yes_no("\nPakka delete karna hai"):
        print("Delete cancel kar diya.")
        return
    session.tasks.remove(task)
    print("Task #{0} delete ho gaya.".format(task.id))
    session.persist()


# ------------------------------------------------------------ extra actions

def show_briefing_again(session):
    render_briefing(build_briefing(session.tasks, session.meta))


def do_text_export(session):
    if not session.tasks:
        print("\nExport karne ke liye pehle koi task banao.")
        return
    try:
        export_text(session.tasks)
    except StorageError as exc:
        print("  !! {0}".format(exc))
        return
    print("\n{0} task text file mein export ho gaye:".format(len(session.tasks)))
    print("  {0}".format(TEXT_FILE))


def change_settings(session):
    print("\n--- Settings ---")
    current = session.meta.get("remind_before_days", DEFAULT_REMIND_DAYS)
    print("  Abhi briefing mein agle {0} din ke task dikhte hain.".format(current))
    days = ask_int("  Naya number (0-{0}): ".format(MAX_REMIND_DAYS),
                   low=0, high=MAX_REMIND_DAYS)
    session.meta["remind_before_days"] = days
    print("  Ab agle {0} din ke task dikhenge.".format(days))
    session.persist()


def file_info(session):
    print("\n--- File ki jaankari ---")
    for label, path in (("Task store (JSON)", STORE_FILE),
                        ("Text export", TEXT_FILE)):
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

    print("\n  Store banaya gaya : {0}".format(session.meta.get("created_at", "-")))
    print("  Pichhli baar khola: {0}".format(session.meta.get("last_opened") or "-"))
    print("  Kul baar khola    : {0}".format(session.meta.get("open_count", 0)))
    print("  Reminder window   : {0} din".format(
        session.meta.get("remind_before_days", DEFAULT_REMIND_DAYS)))
    print("  Memory mein tasks : {0}".format(len(session.tasks)))

    print("\n  Roz apne aap briefing chahiye? Ye command Task Scheduler mein daalo:")
    print("    python \"{0}\" --check".format(os.path.abspath(__file__)))


# ------------------------------------------------------------------- menu

MENU = (
    ("1", "Naya task banao (Create)", create_task),
    ("2", "Tasks dekho (Read)", read_tasks),
    ("3", "Task edit karo (Update)", update_task),
    ("4", "Task done mark karo", complete_task),
    ("5", "Task delete karo (Delete)", delete_task),
    ("6", "Briefing dobara dikhao", show_briefing_again),
    ("7", "Text file mein export karo", do_text_export),
    ("8", "Reminder settings", change_settings),
    ("9", "File ki jaankari", file_info),
)


def show_menu():
    print("\n" + "=" * 52)
    print("  TASK MANAGER + REMINDERS  -  Cognifyz Task 5")
    print("=" * 52)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def open_store():
    """Store kholta hai aur (session, message) deta hai."""
    tasks, meta, message = load_or_migrate()
    return Session(tasks, meta), message


def run_check_mode():
    """
    Sirf briefing print karke band ho jaata hai.

    Jaan-boojh kar last_opened update NAHI karta - warna Task Scheduler
    roz chalke 'pichhli visit ke baad kya badla' khud hi kha jaata,
    aur user ko wo kabhi dikhta hi nahi.

    Exit code:  0 = kuch urgent nahi   1 = overdue ya aaj due hai
    """
    try:
        session, message = open_store()
    except StorageError as exc:
        print("!! {0}".format(exc))
        return 2

    if session.tasks == [] and "kharab" in message:
        print(message)

    briefing = build_briefing(session.tasks, session.meta)
    render_briefing(briefing)
    print("\n  (--check mode: kuch save nahi kiya gaya)")
    return 1 if needs_attention(briefing) else 0


def run_app():
    try:
        session, message = open_store()
    except StorageError as exc:
        print("\n!! {0}".format(exc))
        print("!! Program band kar raha hoon taaki data par khatra na ho.")
        return 2

    print("\nTask manager + reminders")
    print("Store: {0}".format(STORE_FILE))
    print("\n{0}".format(message))

    render_briefing(build_briefing(session.tasks, session.meta))

    # Briefing dikha diya, ab visit record kar lo.
    session.meta["last_opened"] = datetime.now().strftime(DATETIME_FMT)
    session.meta["open_count"] = int(session.meta.get("open_count", 0)) + 1
    if session.tasks:
        session.persist(quiet=True)

    actions = {key: func for key, _, func in MENU}

    while True:
        show_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            print("\nBye! {0} task save hain.".format(len(session.tasks)))
            return 0

        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 9 ke beech ka option chuno.")
            continue

        action(session)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if "--check" in argv:
        return run_check_mode()
    if "--help" in argv or "-h" in argv:
        print(__doc__)
        return 0
    return run_app()


if __name__ == "__main__":
    sys.exit(main())
