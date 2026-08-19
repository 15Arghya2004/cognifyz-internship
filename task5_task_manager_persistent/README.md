<div align="center">

# 🔔 Task 5 — Persistent Task Manager + Reminders

**Cognifyz Technologies · Software Development Internship · Level 3**

![Python](https://img.shields.io/badge/Python-3.6%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Install](https://img.shields.io/badge/Install-Kuch%20nahi-success?style=for-the-badge)
![Checks](https://img.shields.io/badge/Checks-110%2F110%20pass-brightgreen?style=for-the-badge)
![Storage](https://img.shields.io/badge/Store-tasks.json-orange?style=for-the-badge)

Ek constant JSON file mein tasks jama hote rehte hain.
Har baar program khulte hi batata hai: **kya overdue hai, kya aaj due hai,
kya aane wala hai, aur pichhli baar ke baad kya badla.**

</div>

> Ye khud jaakar koi kaam nahi karta. Ye **yaad dilata hai** — kya karna hai, kab tak karna hai, aur kaunsi deadline nikal chuki hai.

---

## 🚀 Chalao

```bash
python task5_task_manager_persistent/task_manager.py
```

Sirf briefing chahiye, app nahi:

```bash
python task5_task_manager_persistent/task_manager.py --check
```

---

## 🎬 Briefing + automation

<div align="center">

![Briefing demo](assets/briefing_demo.gif)

*App khulte hi briefing → ek task done → phir `--check` mode, jise Task Scheduler roz chalata hai*

</div>

Briefing kuch aisi dikhti hai:

```
==============================================================
  AAJ KA BRIEFING  -  Wednesday, 19 August 2026
==============================================================

  Pichhli baar: 2 din pehle   (kul 6 baar khola)

  !! OVERDUE (2)
     #1   Resume update karo         High      4 din se overdue
     #2   Assignment submit karo     High      1 din se overdue

  >> AAJ DUE (1)
     #3   Task 5 ka README likho     High      aaj due

  .. AGLE 3 DIN (1)
     #4   Gym membership renew       Medium    2 din baad

  Pichhli visit ke baad: 1 overdue ho gaye, 1 complete hue, 1 naye bane.

  Kul 8 task | 7 pending | 1 done | 1 bina deadline
==============================================================
```

**"Pichhli visit ke baad" wali line hi is task ka dil hai.** Wo kisi alag log file se nahi aati — program `meta.last_opened`, har task ka `created_at`, aur `completed_at` compare karke khud nikaal leta hai.

---

## ⏰ Roz apne aap chalane ke liye (Windows Task Scheduler)

Python script **khud se nahi jaag sakta** — wo tabhi chalta hai jab koi use chalaye. Asli automation ke liye Windows ko bolna padta hai:

1. Start menu mein **Task Scheduler** kholo
2. **Create Basic Task** → naam do, jaise `Task reminders`
3. Trigger: **When I log on** (ya **Daily**, apna time chuno)
4. Action: **Start a program**
   - Program: `python`
   - Arguments: `"C:\Users\...\task5_task_manager_persistent\task_manager.py" --check`
5. Finish

Ab har login par briefing khud dikh jayegi.

> Exact command program ke andar bhi mil jaayega — **option 9 (File ki jaankari)** chalao, wo tumhare computer ka poora path likhkar de dega.

### `--check` mode ke do design decisions

**1. Wo `last_opened` ko haath nahi lagata.**
Agar lagata, to Task Scheduler roz chal-chalkar "pichhli visit ke baad kya badla" khud hi kha jaata — aur tum jab app kholte, tumhe kabhi kuch naya dikhta hi nahi. Isliye visit sirf tab record hoti hai jab **tum** app kholte ho.

**2. Wo exit code deta hai.**

| Code | Matlab |
|:---:|---|
| `0` | kuch urgent nahi |
| `1` | kuch overdue hai ya aaj due hai |
| `2` | file hi nahi khul paayi |

Isse aage jaakar tum batch script ya notification bhi jod sakte ho — `if errorlevel 1` chalake.

---

## 📦 Ek constant file — `tasks.json`

Sab kuch ek hi jagah: settings, history, aur tasks.

```json
{
  "name": "Cognifyz Internship - Task 5 task store",
  "version": 2,
  "meta": {
    "created_at": "2026-08-01 09:00:00",
    "last_opened": "2026-08-17 10:12:30",
    "open_count": 6,
    "remind_before_days": 3
  },
  "tasks": [
    {
      "id": 1,
      "title": "Resume update karo",
      "description": "placement portal ke liye",
      "priority": "High",
      "due_date": "2026-08-15",
      "status": "pending",
      "created_at": "2026-08-01 09:00:00",
      "completed_at": null
    }
  ]
}
```

Task 3 ke 7 fields ke saath ab **`completed_at`** bhi hai — sirf ye jaanna kaafi nahi tha ki task done hai, ye bhi pata hona chahiye ki **kab** done hua. Wahi "pichhli visit ke baad 2 complete hue" wali line banata hai.

`meta.remind_before_days` menu ke **option 8** se badal sakte ho — 3 din ki jagah 7 din, ya 0 (sirf overdue aur aaj due dikhe).

---

## 🔁 Purana data khoya nahi

Pehle version mein storage `tasks.txt` thi. Agar wo file tumhare paas hai, to program **pehli baar chalte hi**:

1. `tasks.txt` padhta hai (purane 7-field format aur naye 8-field, dono)
2. Data `tasks.json` mein le aata hai
3. Purani file ko `tasks.txt.migrated` naam de deta hai — **delete kabhi nahi karta**

`|` wale titles jinme escaping thi, wo bhi sahi-salamat aate hain. Text export (**option 7**) abhi bhi maujood hai, us poore escaping wale code ke saath.

---

## 🛟 File kharab ho jaye to

<div align="center">

![Recovery demo](assets/recovery_demo.gif)

*JSON ko jaan-boojh kar bigaada → program ne pakda, backup banaya, aur chalta raha*

</div>

1. Kharab file `tasks.json.bak` mein **bach jaati hai** (delete kabhi nahi)
2. Exact path bataya jaata hai
3. Khaali list se app chalu ho jaata hai

`.bak` pehle se ho to `.bak.1`, `.bak.2` banti hai — purana backup kabhi overwrite nahi hota.

---

<details>
<summary><b>🧪 Testing — 110/110 checks pass (click karo)</b></summary>

| Group | Kya check kiya |
|---|:---:|
| `completed_at` — mark_done set kare, mark_pending clear kare, dobara done karne par pehla time na badle | ✅ |
| `to_dict` ↔ `from_dict` roundtrip, purane 7-field dict bhi load ho | ✅ |
| JSON store save/load, meta preserve, `\|` wale title theek | ✅ |
| **Corrupt JSON ke 6 tareeke** — bad syntax, tasks list nahi, top-level array, bad id, bad date, duplicate id | ✅ |
| Har case: backup bana, content bacha, message mein path aaya | ✅ |
| **Migration** — v1 (7 field) aur v2 (8 field) dono lines, escaped `\|` bhi | ✅ |
| Migration ke baad purani file `.migrated` bani, delete nahi hui | ✅ |
| **Briefing engine** — overdue / aaj due / window ke andar / window ke bahar / bina deadline, sab alag-alag | ✅ |
| Done task past-due hone par bhi overdue mein **nahi** aata | ✅ |
| `newly_overdue` sirf wahi jinki deadline pichhli visit **ke baad** nikli | ✅ |
| `completed_since` aur `created_since` sirf last visit ke baad wale | ✅ |
| Window clamping — `-5`, `0`, `999`, `"abc"`, `None`, `"7"` sab par sahi behaviour | ✅ |
| Exit code source — overdue/aaj due par 1, sirf future par 0, done-overdue par 0 | ✅ |
| Text export roundtrip, `\|` + newline + backslash wale title | ✅ |
| Na likhne laayak path par saaf `StorageError` | ✅ |
| `human_gap` — abhi abhi / minute / ghante / kal / din | ✅ |

</details>

<details>
<summary><b>🐛 Ek bug jo testing ne pakda</b></summary>

Text export ka roundtrip test fail hua. Wajah:

```python
data = {name: (value if value != "" else None) for name, value in zip(names, fields)}
```

Maine har khaali field ko `None` bana diya tha. Par khaali **description** ka matlab `None` nahi, `""` hai — "khaali" aur "gayab" do alag cheezein hain. File se wapas aane par description `None` ban jaata tha.

Doosri galti isi se judi thi:

```python
description=data.get("description", "")
```

`get(key, default)` default tabhi deta hai jab **key hi na ho**. Yahan key thi, par value `None` thi — to `None` hi mila.

**Fix:**

```python
nullable = ("due_date", "created_at", "completed_at")   # sirf ye sach mein None ho sakte hain
description=data.get("description") or ""               # None ho to bhi "" mile
```

**Sabak:** `None` aur `""` ko ek jaisa mat maano. Aur `dict.get(key, default)` missing key ke liye hai, `None` value ke liye nahi.

</details>

<details>
<summary><b>⚙️ Design decisions</b></summary>

- **JSON primary** — kyunki ab sirf tasks nahi, `meta` bhi store karna hai (last opened, settings, count). Ek-line-ek-task wali text file mein ye nested data fit nahi baithta. JSON bhi ek text file hi hai — notepad mein khul jaati hai.
- **Text export bacha ke rakha** — PDF `"text file"` maangta hai, aur escaping wala kaam bekaar nahi jaana chahiye. Option 7 se milta hai.
- **Ek hi source of truth** — dono files ek saath likhna aasaan lagta hai par unke divergence ke bugs sabse gande hote hain. `tasks.json` hi asli hai.
- **`--check` read-only** — automation user ki history na kha jaye.
- **`meta` block file ke andar** — settings alag config file mein rakhne se do files sync karni padtin. Ek file, ek sach.
- **Briefing ka hisaab `build_briefing()` mein, printing `render_briefing()` mein** — logic alag hone se use test karna aasaan hai. 110 mein se 25 checks isi ek function ke hain, bina kuch print kiye.
- **Corrupt file delete kabhi nahi** — hamesha `.bak`. User ka data user ka hai.
- **`os.replace`, `os.rename` nahi** — Windows par `rename` maujood file ke upar fail ho jaata hai.

</details>

<details>
<summary><b>📂 Runtime files (git mein nahi jaati)</b></summary>

```
tasks.json           <- tumhara data
tasks.txt            <- text export (option 7)
tasks.json.bak       <- corrupt file ka backup, agar kabhi bana
tasks.txt.migrated   <- purana version, migration ke baad
```

Sab `.gitignore` mein hain — ye generated data hai, source code nahi.

</details>

---

## 📋 Menu

```
  1. Naya task banao (Create)        5. Task delete karo (Delete)
  2. Tasks dekho (Read)              6. Briefing dobara dikhao
  3. Task edit karo (Update)         7. Text file mein export karo
  4. Task done mark karo             8. Reminder settings
                                     9. File ki jaankari
  0. Exit
```

## 📁 Files

```
task5_task_manager_persistent/
├── README.md
├── task_manager.py
└── assets/
    ├── briefing_demo.gif
    └── recovery_demo.gif
```

<div align="center">

**Arghya Mahajan** · [github.com/15Arghya2004](https://github.com/15Arghya2004)

</div>
