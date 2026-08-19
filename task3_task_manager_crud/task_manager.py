"""
Task 3 - Console Task Manager (CRUD)
Cognifyz Technologies | Software Development Internship | Level 2: Intermediate

Ek console based to-do manager jo Create, Read, Update aur Delete
operations support karta hai.

Data ek Python list mein rehta hai (in-memory). Program band karte hi
data chala jaata hai - yeh jaan-boojh kar hai, kyunki Task 5 isi app ko
file I/O ke saath persistent banata hai.

Python 3.6+ | Sirf standard library.
"""

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


# ------------------------------------------------------------------- model

class Task:
    """Ek single to-do item ka blueprint."""

    def __init__(self, task_id, title, description="", priority="Medium",
                 due_date=None, status=STATUS_PENDING, created_at=None):
        self.id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date          # date object ya None
        self.status = status
        self.created_at = created_at if created_at is not None else datetime.now()

    # --- behaviour ---

    def is_done(self):
        return self.status == STATUS_DONE

    def mark_done(self):
        self.status = STATUS_DONE

    def mark_pending(self):
        self.status = STATUS_PENDING

    def is_overdue(self, today=None):
        """Due date nikal chuki hai aur task abhi bhi pending hai."""
        if self.due_date is None or self.is_done():
            return False
        if today is None:
            today = date.today()
        return self.due_date < today

    def days_left(self, today=None):
        """Due date tak kitne din bache. None agar due date set nahi hai."""
        if self.due_date is None:
            return None
        if today is None:
            today = date.today()
        return (self.due_date - today).days

    # --- Task 5 ke liye taiyaari: object <-> plain dictionary ---

    def to_dict(self):
        """Object ko aisi dictionary mein badalta hai jo file mein likhi ja sake."""
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
        """Dictionary se wapas Task object banata hai. to_dict() ka ulta."""
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


# --------------------------------------------------------------- utilities

def parse_date(text):
    """'2026-08-25' -> date object. Galat format pe ValueError uthata hai."""
    return datetime.strptime(text.strip(), DATE_FMT).date()


def format_date(value):
    return value.strftime(DATE_FMT) if value else "-"


def shorten(text, width):
    if len(text) <= width:
        return text
    return text[:width - 3] + "..."


def next_id(tasks):
    """Sabse bada id + 1. Khaali list pe 1."""
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1


def find_task(tasks, task_id):
    for task in tasks:
        if task.id == task_id:
            return task
    return None


def sort_key(task):
    """Pending pehle, phir High priority, phir jaldi wali due date."""
    due = task.due_date if task.due_date else date.max
    return (task.is_done(), PRIORITY_RANK.get(task.priority, 99), due, task.id)


# ------------------------------------------------------------ input helpers

def ask_text(prompt, required=True, default=None):
    """Text input. required=False ho to khaali Enter allowed hai."""
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
    """options mein se ek chunwata hai. Case matter nahi karta."""
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
    """YYYY-MM-DD leta hai. Khaali Enter = koi due date nahi."""
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
    """Whole number leta hai. Galat input pe crash nahi karta."""
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
    """User se task id maangta hai. None return kare to caller ruk jaaye."""
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
    """READ operation ka core - saare tasks ek table mein."""
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
            task.id,
            status_box(task),
            task.priority,
            shorten(task.title, TITLE_WIDTH),
            format_date(task.due_date),
            note_for(task),
            w=TITLE_WIDTH))

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

def create_task(tasks):
    """CREATE - naya task banakar list mein daalta hai."""
    print("\n--- Naya task ---")
    title = ask_text("Title: ")
    description = ask_text("Description (Enter = skip): ", required=False)
    priority = ask_choice("Priority", PRIORITIES, default="Medium")
    due = ask_date("Due date YYYY-MM-DD (Enter = koi nahi): ")

    task = Task(next_id(tasks), title, description, priority, due)
    tasks.append(task)
    print("\nTask #{0} add ho gaya.".format(task.id))


def read_tasks(tasks):
    """READ - filter chunkar tasks dikhata hai."""
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
    """UPDATE - chuni hui field badalta hai."""
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
    show_detail(task)


def complete_task(tasks):
    """UPDATE ka shortcut - seedha done mark karna."""
    task = pick_task(tasks, "Done mark karne")
    if task is None:
        return
    if task.is_done():
        print("\nTask #{0} pehle se hi done hai.".format(task.id))
        return
    task.mark_done()
    print("\nTask #{0} done mark ho gaya: {1}".format(task.id, task.title))


def delete_task(tasks):
    """DELETE - confirm karke list se hataata hai."""
    task = pick_task(tasks, "Delete")
    if task is None:
        return
    show_detail(task)
    if not ask_yes_no("\nPakka delete karna hai"):
        print("Delete cancel kar diya.")
        return
    tasks.remove(task)
    print("Task #{0} delete ho gaya.".format(task.id))


# ------------------------------------------------------------------- menu

MENU = (
    ("1", "Naya task banao (Create)", create_task),
    ("2", "Tasks dekho (Read)", read_tasks),
    ("3", "Task edit karo (Update)", update_task),
    ("4", "Task done mark karo", complete_task),
    ("5", "Task delete karo (Delete)", delete_task),
)


def show_menu():
    print("\n" + "=" * 52)
    print("  TASK MANAGER  -  Cognifyz Internship Task 3")
    print("=" * 52)
    for key, label, _ in MENU:
        print("  {0}. {1}".format(key, label))
    print("  0. Exit")


def main():
    tasks = []
    actions = {key: func for key, _, func in MENU}

    print("\nWelcome! Yeh in-memory task manager hai.")
    print("Data sirf program chalne tak rehta hai (Task 5 ise file mein save karega).")

    while True:
        show_menu()
        choice = input("\nChoice: ").strip()

        if choice == "0":
            print("\nBye! {0} task the list mein.".format(len(tasks)))
            break

        action = actions.get(choice)
        if action is None:
            print("  -> 0 se 5 ke beech ka option chuno.")
            continue

        action(tasks)


if __name__ == "__main__":
    main()
