<div align="center">

# 📝 Task 3 — Console Task Manager

**Cognifyz Technologies · Software Development Internship · Level 2**

![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Install](https://img.shields.io/badge/Install-Kuch%20nahi-success?style=for-the-badge)
![Concept](https://img.shields.io/badge/Concept-Class%20%2B%20CRUD-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

Terminal mein chalne wala to-do manager.
Task **banao**, **dekho**, **badlo**, **delete karo**.

</div>

---

## 🚀 Chalao

```bash
python task3_task_manager_crud/task_manager.py
```

Bas. Na install, na setup. Sirf Python 3.6+ chahiye.

---

## 🎬 Chalta hua kaisa dikhta hai

<div align="center">

![CRUD demo](assets/crud_demo.gif)

*Do task banaye → table dekha → ek done kiya → doosra delete kiya*

</div>

---

## 📋 Menu

```
====================================================
  TASK MANAGER  -  Cognifyz Internship Task 3
====================================================
  1. Naya task banao (Create)
  2. Tasks dekho (Read)
  3. Task edit karo (Update)
  4. Task done mark karo
  5. Task delete karo (Delete)
  0. Exit
```

| Dabao | Hota kya hai |
|:---:|---|
| `1` | Title, description, priority aur due date poochta hai |
| `2` | Sab tasks table mein — All / Pending / Done / Overdue filter ke saath |
| `3` | Ek task chuno, phir jo field badalni ho wahi badlo |
| `4` | Task pe ✔ laga do |
| `5` | Delete — pehle detail dikhata hai, phir confirm poochta hai |
| `0` | Bahar |

---

## 📦 Ek task mein kya-kya hota hai

| Field | Kya hai | Example |
|---|---|---|
| `id` | apne aap milta hai | `1` |
| `title` | naam — **zaroori** | `Internship Task 3 submit karo` |
| `description` | extra detail — optional | `README banakar push karna hai` |
| `priority` | High / Medium / Low | `High` |
| `status` | pending / done | `pending` |
| `due_date` | kab tak — optional | `2026-08-22` |
| `created_at` | kab banaya — apne aap | `2026-08-19 21:17:24` |

Table apne aap sort ho jaata hai:

> **pending pehle → phir High priority → phir jiski date sabse jaldi hai**

Aur jiski date nikal chuki ho, uspe **`OVERDUE`** laal mein aa jaata hai.

---

## 🛡️ Galat input daalo to kya hota hai

Program **kabhi crash nahi hota**. Har galti pe seedha bata deta hai aur dobara poochta hai.

<div align="center">

![Validation demo](assets/validation_demo.gif)

*Menu mein `9`, priority mein `Urgent`, date mein `25-08-2026`, ID mein `99` — sab sambhal liye*

</div>

---

## 🧠 Code ki 3 main baatein

### 1. Ek task = ek object

Purana tareeka — teen alag lists:

```python
titles     = ["Gym jao", "Python padho"]
priorities = ["Medium", "High"]
statuses   = ["done", "pending"]
```

Index 0 delete karo to **teenon** se karna padega. Ek bhool gaye → data gadbad, aur program batayega bhi nahi.

Naya tareeka — sab kuch ek `Task` object ke andar:

```python
class Task:
    def __init__(self, task_id, title, description="", priority="Medium",
                 due_date=None, status="pending", created_at=None):
        self.id = task_id
        self.title = title
        ...
```

Ab sirf **ek** list: `tasks = [Task, Task, Task]`. Delete karo → poora task ek saath gaya.

### 2. ID kabhi repeat nahi hote

```python
def next_id(tasks):
    if not tasks:
        return 1
    return max(task.id for task in tasks) + 1
```

`len(tasks) + 1` galat hota. 3 task hain, beech wala delete kiya → `len` 2 → naya id 3 milega, jo pehle se hai. `max + 1` ye bug hone hi nahi deta.

### 3. Validation ke do tareeke

```python
try:
    return int(raw)          # int() ka rule PYTHON ka hai
except ValueError:
    print("  -> Sirf number likho, jaise 3.")
```

```python
if raw.lower() in lowered:   # High/Medium/Low ka rule APNA hai
    return lowered[raw.lower()]
```

> **Rule tumhara apna hai → `if`. Rule Python ka hai → `try/except`.**

---

## 🔗 Task 5 se kya lena-dena

Task 5 isi app ko **file mein save** karne wala banata hai. Uske liye do methods pehle se rakh diye hain:

```python
task.to_dict()          # object     -> dictionary  (file mein likhne ke liye)
Task.from_dict(data)    # dictionary -> object      (file se wapas laane ke liye)
```

Task 3 mein inhe use nahi karte. Task 5 mein sirf save/load add hoga — `Task` class ko haath lagane ki zaroorat nahi padegi.

---

<details>
<summary><b>🧪 Testing — 44/44 checks pass (click karo)</b></summary>

PDF ka step 6 kehta hai *"Test the application with various scenarios."*

**Automated checks:**

| Kya check kiya | Result |
|---|:---:|
| Naya task hamesha `pending`, priority `Medium` | ✅ |
| Done task kabhi `OVERDUE` nahi dikhta | ✅ |
| Aaj ki due date `OVERDUE` nahi hai (kal se hai) | ✅ |
| Beech wala task delete karne par bhi ID repeat nahi | ✅ |
| `to_dict` → `from_dict` mein saaton field wapas aate hain | ✅ |
| Adhoori dictionary se bhi object ban jaata hai | ✅ |
| Sort order: pending + High + jaldi-due sabse upar | ✅ |
| `25-08-2026`, `2026/08/25`, `hello`, `2026-13-01`, `2026-02-30` reject | ✅ |
| Lamba title truncate, khaali table pe crash nahi | ✅ |

**Haath se chalake dekhe gaye scenarios:**

- Menu mein `9` → *"0 se 5 ke beech ka option chuno"*, program chalta raha
- Due date `25-08-2026` → format error, dobara poocha
- Update ke liye ID `99` → *"ID 99 ka koi task nahi mila"*, menu par wapas
- Due date khaali chhodi → task bina due date ke ban gaya
- Delete pe `n` → cancel, task salamat
- Sab delete karke Read → *"list khaali hai"*, crash nahi

</details>

<details>
<summary><b>⚙️ Design decisions — kyun aisa banaya</b></summary>

- **`tasks` list function mein pass hoti hai, global nahi** — global se test karna mushkil hota, aur Task 5 mein file se load karna gandha ho jaata.
- **`datetime.strptime` use kiya, `date.fromisoformat` nahi** — `fromisoformat` Python 3.7+ hai. `strptime` 3.6 pe bhi chalta hai, isliye README ka "3.6+" claim sach hai.
- **Delete kiya hua ID dobara nahi milta** — warna purane screenshot galat task ko point karne lagte.
- **`__repr__` likha** — iske bina `print(task)` memory address deta hai, debug karte waqt bekaar.
- **`sorted()` use kiya, `.sort()` nahi** — `sorted()` nayi list banata hai, original ka order salamat rehta hai.

</details>

<details>
<summary><b>⚠️ Ek limitation (jaan-boojh kar)</b></summary>

**Data save nahi hota.** Program band = tasks gayab.

Ye bug nahi hai — Task 3 ki requirement hi yahi hai: *"using arrays or lists for data storage"*. **Task 5** exactly isi ko file I/O se theek karta hai.

</details>

---

## 📁 Files

```
task3_task_manager_crud/
├── README.md
├── task_manager.py            <- poora program
└── assets/
    ├── crud_demo.gif
    └── validation_demo.gif
```

<div align="center">

**Arghya Mahajan** · [github.com/15Arghya2004](https://github.com/15Arghya2004)

</div>
