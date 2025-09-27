# Lab: Combined Tkinter & PyQt5

This starter was generated from your zip to help you follow the assignment.

## 1) Create repo & invite collaborator
```bash
git init
git add .
git commit -m "Initial commit (starter layout)"
git branch -M main
git remote add origin https://github.com/USERNAME/Lab4-Student1FullName_Student2FullName.git
git push -u origin main
```

## 2) Create feature branches
- Tkinter:
  ```bash
  git checkout -b feature-tkinter
  ```
- PyQt:
  ```bash
  git checkout -b feature-pyqt
  ```

## 3) Set up environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
# On Linux you may need system package for Tkinter:
# sudo apt-get install python3-tk
```

## 4) Run each UI
- Tkinter:
  ```bash
  python run_tk.py
  ```
- PyQt5:
  ```bash
  python run_pyqt.py
  ```

## 5) Integrate to a shared backend (recommended)
The Tkinter app in `submission/part4_database.py` already has a full SQLite backend
(e.g., `create_student`, `read_students`, `update_student`, `delete_student`, `register_student`, etc.).

To make both UIs share the same data layer, import these functions inside the PyQt UI (`submission/part3_pyqt5.py`) and call them from the button handlers instead of using in-memory/JSON data.
Example patch inside `part3_pyqt5.py`:
```python
# at top of file
from submission.part4_database import (
    init_db, create_student, create_instructor, create_course,
    read_students, read_instructors, read_courses,
    update_student, update_instructor, update_course,
    delete_student, delete_instructor, delete_course,
    register_student, export_csvs, backup_db,
)

# in __init__ or first run:
init_db()  # ensures 'school.db' exists
```

Then, in your PyQt handlers (e.g., `add_student`, `add_instructor`, `add_course`), call the above functions
and refresh the PyQt table by re-reading from `read_students()`/`read_instructors()`/`read_courses()`.

## 6) Open PRs and merge
- Push each feature branch:
  ```bash
  git push -u origin feature-tkinter
  git push -u origin feature-pyqt
  ```
- Open PRs on GitHub from each feature branch to `main`, review, resolve conflicts, and merge.

## 7) Tag v1.0
```bash
git tag -a v1.0 -m "Final release with Tkinter and PyQt UIs"
git push origin v1.0
```


## Included OOP task
- `submission/part1_oop.py` — keep this in the repo if your lab requires it.
