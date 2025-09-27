"""School database: SQLite backend + a tiny Tkinter app.

This module contains two parts:

- **Database layer (SQLite):** tables for students, instructors, courses, and
  registrations, with foreign keys turned on. You will find small helper
  functions for the usual CRUD actions (create/read/update/delete), plus
  utilities to export CSV files and to make timestamped database backups.

- **Desktop UI (Tkinter):** a simple, tabbed window (``App``) that lets you
  add people and courses, assign instructors, register students, and run the
  export/backup tools—without touching SQL.

**Why this exists:** its a compact example of how to wire a GUI to a real
database. The focus is on clarity: straightforward schema, clean functions,
and a minimal interface that shows the full round-trip from UI → database → files.
"""


import os, sqlite3, csv, datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

DB_FILE = 'school.db'
SCHEMA = '\nPRAGMA foreign_keys = ON;\nCREATE TABLE IF NOT EXISTS students (\n   student_id TEXT PRIMARY KEY,\n    name TEXT NOT NULL,\n    age INTEGER NOT NULL CHECK(age >= 0),\n    email TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS instructors (\n    instructor_id TEXT PRIMARY KEY,\n    name TEXT NOT NULL,\n    age INTEGER NOT NULL CHECK(age >= 0),\n    email TEXT NOT NULL\n);\nCREATE TABLE IF NOT EXISTS courses (\n    course_id TEXT PRIMARY KEY,\n    course_name TEXT NOT NULL,\n    instructor_id TEXT,\n    FOREIGN KEY(instructor_id) REFERENCES instructors(instructor_id) ON DELETE SET NULL\n);\nCREATE TABLE IF NOT EXISTS registrations (\n    student_id TEXT NOT NULL,\n    course_id TEXT NOT NULL,\n    PRIMARY KEY(student_id, course_id),\n    FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,\n    FOREIGN KEY(course_id) REFERENCES courses(course_id) ON DELETE CASCADE\n);\n'


def conn():
    """Open a SQLite connection to :data:`DB_FILE` with foreign keys enabled.

    :return: An open connection configured with ``PRAGMA foreign_keys=ON``.
    :rtype: sqlite3.Connection
    """
    c = sqlite3.connect(DB_FILE)
    c.execute('PRAGMA foreign_keys = ON')
    return c


def init_db():
    """Create tables if they do not exist (safe to call multiple times)."""
    with conn() as c:
        c.executescript(SCHEMA)


def create_student(sid, name, age, email):
    """Insert or replace a student.

    :param sid: Unique student ID.
    :type sid: str
    :param name: Student full name.
    :type name: str
    :param age: Student age; coerced to ``int`` and must be ``>= 0``.
    :type age: int | str
    :param email: Student email address.
    :type email: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO students(student_id,name,age,email) VALUES (?,?,?,?)', (sid, name, int(age), email))


def create_instructor(iid, name, age, email):
    """Insert or replace an instructor.

    :param iid: Unique instructor ID.
    :type iid: str
    :param name: Instructor full name.
    :type name: str
    :param age: Instructor age; coerced to ``int`` and must be ``>= 0``.
    :type age: int | str
    :param email: Instructor email address.
    :type email: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO instructors(instructor_id,name,age,email) VALUES (?,?,?,?)', (iid, name, int(age), email))


def create_course(cid, cname, iid=None):
    """Insert or replace a course.

    :param cid: Unique course ID.
    :type cid: str
    :param cname: Human-readable course name.
    :type cname: str
    :param iid: Optional instructor ID to assign (``None`` to leave unassigned).
    :type iid: str | None
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('INSERT OR REPLACE INTO courses(course_id,course_name,instructor_id) VALUES (?,?,?)', (cid, cname, iid))


def read_students(q: str=''):
    """Read students, optionally filtered by a LIKE query.

    :param q: Filter text; matches ID, name, or email (case-insensitive).
    :type q: str
    :return: Rows as ``(student_id, name, age, email)`` tuples.
    :rtype: list[tuple]
    """
    with conn() as c:
        if q:
            ql = f'%{q}%'
            return c.execute('SELECT student_id,name,age,email FROM students\n                                WHERE student_id LIKE ? OR name LIKE ? OR email LIKE ?', (ql, ql, ql)).fetchall()
        return c.execute('SELECT student_id,name,age,email FROM students').fetchall()


def read_instructors(q: str=''):
    """Read instructors, optionally filtered by a LIKE query.

    :param q: Filter text; matches ID, name, or email (case-insensitive).
    :type q: str
    :return: Rows as ``(instructor_id, name, age, email)`` tuples.
    :rtype: list[tuple]
    """
    with conn() as c:
        if q:
            ql = f'%{q}%'
            return c.execute('SELECT instructor_id,name,age,email FROM instructors\n                                WHERE instructor_id LIKE ? OR name LIKE ? OR email LIKE ?', (ql, ql, ql)).fetchall()
        return c.execute('SELECT instructor_id,name,age,email FROM instructors').fetchall()


def read_courses(q: str=''):
    """Read courses, optionally filtered by course ID or name.

    :param q: Filter text; matches course ID or course name (case-insensitive).
    :type q: str
    :return: Rows as ``(course_id, course_name, instructor_id|'')`` tuples.
    :rtype: list[tuple]
    """
    with conn() as c:
        if q:
            ql = f'%{q}%'
            return c.execute("SELECT course_id,course_name,IFNULL(instructor_id,'') FROM courses\n                                WHERE course_id LIKE ? OR course_name LIKE ?", (ql, ql)).fetchall()
        return c.execute("SELECT course_id,course_name,IFNULL(instructor_id,'') FROM courses").fetchall()


def get_course_name(cid):
    """Return the course name for a given course ID, or ``''`` if not found.

    :param cid: Course ID.
    :type cid: str
    :return: Course name or empty string.
    :rtype: str
    """
    with conn() as c:
        row = c.execute('SELECT course_name FROM courses WHERE course_id=?', (cid,)).fetchone()
        return row[0] if row else ''


def update_student(sid, name, age, email):
    """Update an existing student.

    :param sid: Student ID.
    :type sid: str
    :param name: New student name.
    :type name: str
    :param age: New age; coerced to ``int`` and must be ``>= 0``.
    :type age: int | str
    :param email: New email.
    :type email: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('UPDATE students SET name=?,age=?,email=? WHERE student_id=?', (name, int(age), email, sid))


def update_instructor(iid, name, age, email):
    """Update an existing instructor.

    :param iid: Instructor ID.
    :type iid: str
    :param name: New instructor name.
    :type name: str
    :param age: New age; coerced to ``int`` and must be ``>= 0``.
    :type age: int | str
    :param email: New email.
    :type email: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('UPDATE instructors SET name=?,age=?,email=? WHERE instructor_id=?', (name, int(age), email, iid))


def update_course(cid, cname, iid):
    """Update a course's name and assigned instructor.

    :param cid: Course ID.
    :type cid: str
    :param cname: New course name.
    :type cname: str
    :param iid: Instructor ID to assign (or ``None`` to unassign).
    :type iid: str | None
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('UPDATE courses SET course_name=?, instructor_id=? WHERE course_id=?', (cname, iid, cid))


def delete_student(sid):
    """Delete a student by ID (registrations cascade).

    :param sid: Student ID to delete.
    :type sid: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('DELETE FROM students WHERE student_id=?', (sid,))


def delete_instructor(iid):
    """Delete an instructor by ID (courses keep ``NULL`` instructor).

    :param iid: Instructor ID to delete.
    :type iid: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('DELETE FROM instructors WHERE instructor_id=?', (iid,))


def delete_course(cid):
    """Delete a course by ID (registrations cascade).

    :param cid: Course ID to delete.
    :type cid: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('DELETE FROM courses WHERE course_id=?', (cid,))


def register_student(sid, cid):
    """Register a student in a course (ignored if already registered).

    :param sid: Student ID.
    :type sid: str
    :param cid: Course ID.
    :type cid: str
    :return: None
    :rtype: None
    """
    with conn() as c:
        c.execute('INSERT OR IGNORE INTO registrations(student_id, course_id) VALUES (?,?)', (sid, cid))


def export_csvs(folder: str):
    """Export database data to CSV files in ``folder``.

    Creates three files:
    - ``students.csv``: student fields + ``;``-separated course IDs
    - ``instructors.csv``: instructor fields
    - ``courses.csv``: course fields + ``;``-separated student IDs

    :param folder: Destination directory (created if missing).
    :type folder: str
    :return: None
    :rtype: None
    """
    os.makedirs(folder, exist_ok=True)
    with conn() as c:
        students = c.execute('SELECT student_id,name,age,email FROM students').fetchall()
        with open(os.path.join(folder, 'students.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['student_id', 'name', 'age', 'email', 'courses'])
            for sid, name, age, email in students:
                courses = [row[0] for row in c.execute('SELECT course_id FROM registrations WHERE student_id=?', (sid,)).fetchall()]
                w.writerow([sid, name, age, email, ';'.join(courses) or '-'])
        instructors = c.execute('SELECT instructor_id,name,age,email FROM instructors').fetchall()
        with open(os.path.join(folder, 'instructors.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['instructor_id', 'name', 'age', 'email'])
            w.writerows(instructors)
        courses = c.execute("SELECT course_id,course_name,IFNULL(instructor_id,'-') FROM courses").fetchall()
        with open(os.path.join(folder, 'courses.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(['course_id', 'name', 'instructor_id', 'students'])
            for cid, cname, iid in courses:
                studs = [row[0] for row in c.execute('SELECT student_id FROM registrations WHERE course_id=?', (cid,)).fetchall()]
                w.writerow([cid, cname, iid, ';'.join(studs) or '-'])


def backup_db(folder: str) -> str:
    """Create a timestamped copy of the database in ``folder``.

    Backup file name format: ``school-YYYYMMDD-HHMMSS.db``.

    :param folder: Destination folder (created if needed).
    :type folder: str
    :return: Full path to the backup file.
    :rtype: str
    """
    os.makedirs(folder, exist_ok=True)
    ts = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    dest = os.path.join(folder, f'school-{ts}.db')
    with open(DB_FILE, 'rb') as src, open(dest, 'wb') as dst:
        dst.write(src.read())
    return dest


class App:
    """Minimal Tkinter application exposing CRUD and export actions."""
    def __init__(self, root):
        """Build the UI, initialize the DB, and load data.

        :param root: Tk root window.
        :type root: tkinter.Tk
        """
        self.root = root
        self.root.title('School Management System (Tkinter + SQLite)')
        self.root.geometry('1100x720')
        init_db()
        self.build_ui()
        self.refresh_all()

    def build_ui(self):
        """Create tabs, forms, tables, and hook up buttons/handlers."""
        nb = ttk.Notebook(self.root)
        nb.pack(fill='both', expand=True)
        self.tab_s = ttk.Frame(nb)
        nb.add(self.tab_s, text='Students')
        fs = ttk.LabelFrame(self.tab_s, text='Student Form')
        fs.pack(fill='x', padx=8, pady=8)
        ttk.Label(fs, text='ID').grid(row=0, column=0)
        self.s_id = ttk.Entry(fs)
        self.s_id.grid(row=0, column=1)
        ttk.Label(fs, text='Name').grid(row=0, column=2)
        self.s_name = ttk.Entry(fs)
        self.s_name.grid(row=0, column=3)
        ttk.Label(fs, text='Age').grid(row=1, column=0)
        self.s_age = ttk.Entry(fs)
        self.s_age.grid(row=1, column=1)
        ttk.Label(fs, text='Email').grid(row=1, column=2)
        self.s_email = ttk.Entry(fs)
        self.s_email.grid(row=1, column=3)
        ttk.Button(fs, text='Add/Update', command=self.add_student).grid(row=0, column=4, padx=6)
        ttk.Button(fs, text='Delete Selected', command=lambda: self.delete_selected(self.tree_s, 'student')).grid(row=1, column=4, padx=6)
        ttk.Label(fs, text='Search').grid(row=2, column=0)
        self.s_q = ttk.Entry(fs)
        self.s_q.grid(row=2, column=1)
        ttk.Button(fs, text='Go', command=lambda: self.refresh_students(self.s_q.get())).grid(row=2, column=2)
        self.tree_s = ttk.Treeview(self.tab_s, columns=('ID', 'Name', 'Age', 'Email'), show='headings', height=12)
        for c in ('ID', 'Name', 'Age', 'Email'):
            self.tree_s.heading(c, text=c)
        self.tree_s.pack(fill='both', expand=True, padx=8, pady=8)
        self.tab_i = ttk.Frame(nb)
        nb.add(self.tab_i, text='Instructors')
        fi = ttk.LabelFrame(self.tab_i, text='Instructor Form')
        fi.pack(fill='x', padx=8, pady=8)
        ttk.Label(fi, text='ID').grid(row=0, column=0)
        self.i_id = ttk.Entry(fi)
        self.i_id.grid(row=0, column=1)
        ttk.Label(fi, text='Name').grid(row=0, column=2)
        self.i_name = ttk.Entry(fi)
        self.i_name.grid(row=0, column=3)
        ttk.Label(fi, text='Age').grid(row=1, column=0)
        self.i_age = ttk.Entry(fi)
        self.i_age.grid(row=1, column=1)
        ttk.Label(fi, text='Email').grid(row=1, column=2)
        self.i_email = ttk.Entry(fi)
        self.i_email.grid(row=1, column=3)
        ttk.Button(fi, text='Add/Update', command=self.add_instructor).grid(row=0, column=4, padx=6)
        ttk.Button(fi, text='Delete Selected', command=lambda: self.delete_selected(self.tree_i, 'instructor')).grid(row=1, column=4, padx=6)
        ttk.Label(fi, text='Search').grid(row=2, column=0)
        self.i_q = ttk.Entry(fi)
        self.i_q.grid(row=2, column=1)
        ttk.Button(fi, text='Go', command=lambda: self.refresh_instructors(self.i_q.get())).grid(row=2, column=2)
        self.tree_i = ttk.Treeview(self.tab_i, columns=('ID', 'Name', 'Age', 'Email'), show='headings', height=12)
        for c in ('ID', 'Name', 'Age', 'Email'):
            self.tree_i.heading(c, text=c)
        self.tree_i.pack(fill='both', expand=True, padx=8, pady=8)
        self.tab_c = ttk.Frame(nb)
        nb.add(self.tab_c, text='Courses')
        fc = ttk.LabelFrame(self.tab_c, text='Course Form')
        fc.pack(fill='x', padx=8, pady=8)
        ttk.Label(fc, text='Course ID').grid(row=0, column=0)
        self.c_id = ttk.Entry(fc)
        self.c_id.grid(row=0, column=1)
        ttk.Label(fc, text='Course Name').grid(row=0, column=2)
        self.c_name = ttk.Entry(fc)
        self.c_name.grid(row=0, column=3)
        ttk.Button(fc, text='Add/Update', command=self.add_course).grid(row=0, column=4, padx=6)
        assign = ttk.LabelFrame(self.tab_c, text='Assignments & Registrations')
        assign.pack(fill='x', padx=8, pady=8)
        ttk.Label(assign, text='Course').grid(row=0, column=0)
        self.combo_course_assign = ttk.Combobox(assign, state='readonly')
        self.combo_course_assign.grid(row=0, column=1)
        ttk.Label(assign, text='Instructor').grid(row=0, column=2)
        self.combo_instructor = ttk.Combobox(assign, state='readonly')
        self.combo_instructor.grid(row=0, column=3)
        ttk.Button(assign, text='Assign Instructor', command=self.assign_instructor).grid(row=0, column=4, padx=6)
        ttk.Label(assign, text='Student').grid(row=1, column=0)
        self.combo_student = ttk.Combobox(assign, state='readonly')
        self.combo_student.grid(row=1, column=1)
        ttk.Label(assign, text='Course').grid(row=1, column=2)
        self.combo_course = ttk.Combobox(assign, state='readonly')
        self.combo_course.grid(row=1, column=3)
        ttk.Button(assign, text='Register Student', command=self.register_student).grid(row=1, column=4, padx=6)
        tools = ttk.Frame(self.tab_c)
        tools.pack(fill='x', padx=8, pady=8)
        ttk.Button(tools, text='Export CSVs', command=self.export_csvs).pack(side='left', padx=4)
        ttk.Button(tools, text='Backup DB', command=self.backup_db).pack(side='left', padx=4)
        ttk.Label(self.tab_c, text='Search').pack(anchor='w', padx=10)
        self.c_q = ttk.Entry(self.tab_c)
        self.c_q.pack(anchor='w', padx=10, pady=4)
        ttk.Button(self.tab_c, text='Go', command=lambda: self.refresh_courses(self.c_q.get())).pack(anchor='w', padx=10)
        self.tree_c = ttk.Treeview(self.tab_c, columns=('ID', 'Name', 'InstructorID', 'InstructorName'), show='headings', height=12)
        for c in ('ID', 'Name', 'InstructorID', 'InstructorName'):
            self.tree_c.heading(c, text=c)
        self.tree_c.pack(fill='both', expand=True, padx=8, pady=8)
        ttk.Button(self.tab_c, text='Delete Selected', command=lambda: self.delete_selected(self.tree_c, 'course')).pack(pady=8)

    def refresh_all(self):
        """Refresh all tables and comboboxes from the database."""
        self.refresh_students()
        self.refresh_instructors()
        self.refresh_courses()
        self.refresh_dropdowns()

    def refresh_students(self, q: str=''):
        """Reload the Students table.

        :param q: Optional filter (substring of ID, name, or email).
        :type q: str
        """
        for i in self.tree_s.get_children():
            self.tree_s.delete(i)
        rows = read_students(q)
        for r in rows:
            self.tree_s.insert('', 'end', values=r)

    def refresh_instructors(self, q: str=''):
        """Reload the Instructors table.

        :param q: Optional filter (substring of ID, name, or email).
        :type q: str
        """
        for i in self.tree_i.get_children():
            self.tree_i.delete(i)
        rows = read_instructors(q)
        for r in rows:
            self.tree_i.insert('', 'end', values=r)

    def refresh_courses(self, q: str=''):
        """Reload the Courses table.

        :param q: Optional filter (substring of course ID or name).
        :type q: str
        """
        for i in self.tree_c.get_children():
            self.tree_c.delete(i)
        rows = read_courses(q)
        inst = {iid: name for iid, name, _, _ in read_instructors('')}
        for cid, cname, iid in rows:
            self.tree_c.insert('', 'end', values=(cid, cname, iid or '', inst.get(iid or '', '')))

    def refresh_dropdowns(self):
        """Refresh all combobox values with current IDs from the database."""
        self.combo_course_assign['values'] = [cid for cid, _, _ in read_courses('')]
        self.combo_instructor['values'] = [iid for iid, _, _, _ in read_instructors('')]
        self.combo_student['values'] = [sid for sid, _, _, _ in read_students('')]
        self.combo_course['values'] = [cid for cid, _, _ in read_courses('')]

    def add_student(self):
        """Add or update a student from form inputs."""
        sid = self.s_id.get().strip()
        name = self.s_name.get().strip()
        age = self.s_age.get().strip()
        email = self.s_email.get().strip()
        if not sid or not name or (not age) or (not email):
            messagebox.showerror('Validation', 'Fill all student fields.')
            return
        try:
            create_student(sid, name, age, email)
            self.refresh_students()
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def add_instructor(self):
        """Add or update an instructor from form inputs."""
        iid = self.i_id.get().strip()
        name = self.i_name.get().strip()
        age = self.i_age.get().strip()
        email = self.i_email.get().strip()
        if not iid or not name or (not age) or (not email):
            messagebox.showerror('Validation', 'Fill all instructor fields.')
            return
        try:
            create_instructor(iid, name, age, email)
            self.refresh_instructors()
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def add_course(self):
        """Add or update a course from form inputs."""
        cid = self.c_id.get().strip()
        cname = self.c_name.get().strip()
        if not cid or not cname:
            messagebox.showerror('Validation', 'Fill all course fields.')
            return
        try:
            create_course(cid, cname, None)
            self.refresh_courses()
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def delete_selected(self, tree, kind):
        """Delete the selected row from the given tree and refresh the UI.

        :param tree: Treeview instance (students, instructors, or courses).
        :type tree: tkinter.ttk.Treeview
        :param kind: One of ``'student'``, ``'instructor'``, or ``'course'``.
        :type kind: str
        """
        sel = tree.selection()
        if not sel:
            return
        key = tree.item(sel[0], 'values')[0]
        try:
            if kind == 'student':
                delete_student(key)
                self.refresh_students()
                self.refresh_courses()
                self.refresh_dropdowns()
            elif kind == 'instructor':
                delete_instructor(key)
                self.refresh_instructors()
                self.refresh_courses()
                self.refresh_dropdowns()
            elif kind == 'course':
                delete_course(key)
                self.refresh_courses()
                self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def assign_instructor(self):
        """Assign the selected instructor to the selected course."""
        cid = self.combo_course_assign.get().strip()
        iid = self.combo_instructor.get().strip() or None
        if not cid:
            messagebox.showerror('Validation', 'Select a course.')
            return
        try:
            cname = get_course_name(cid) or ''
            update_course(cid, cname, iid)
            self.refresh_courses()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def register_student(self):
        """Register the selected student in the selected course."""
        sid = self.combo_student.get().strip()
        cid = self.combo_course.get().strip()
        if not sid or not cid:
            messagebox.showerror('Validation', 'Select student and course.')
            return
        try:
            register_student(sid, cid)
            self.refresh_courses()
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def export_csvs(self):
        """Ask for a folder and export CSVs via :func:`export_csvs`."""
        folder = filedialog.askdirectory()
        if not folder:
            return
        try:
            export_csvs(folder)
            messagebox.showinfo('Export', f'CSV files saved to {folder}')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def backup_db(self):
        """Ask for a folder and create a timestamped DB backup."""
        folder = filedialog.askdirectory()
        if not folder:
            return
        try:
            path = backup_db(folder)
            messagebox.showinfo('Backup', f'Backed up to {path}')
        except Exception as e:
            messagebox.showerror('Error', str(e))


if __name__ == '__main__':
    root = tk.Tk()
    App(root)
    root.mainloop()
