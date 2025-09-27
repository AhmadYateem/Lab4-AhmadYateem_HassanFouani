"""Module part2_tkinter."""
import json, os, re, tkinter as tk
from tkinter import ttk, messagebox, filedialog
EMAIL_RE = re.compile('^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$')

def is_valid_email(email: str) -> bool:
    """Function is_valid_email.

:param email: Description of email.
:type email: Any
:return: Description of return value.
:rtype: Any"""
    return bool(EMAIL_RE.match(email))

def is_valid_age(age: str) -> bool:
    """Function is_valid_age.

:param age: Description of age.
:type age: Any
:return: Description of return value.
:rtype: Any"""
    try:
        return int(age) >= 0
    except Exception:
        return False
DATA = {'students': {}, 'instructors': {}, 'courses': {}}

def _missing_fields_message(pairs):
    """
    pairs: list of (Label, value)
    returns None if all present, else a friendly message string.
    """
    missing = [lbl for lbl, val in pairs if not str(val).strip()]
    if missing:
        return 'Missing data needed: ' + ', '.join((lbl.lower() for lbl in missing))
    return None

def _email_error_message(email):
    """Function _email_error_message.

:param email: Description of email.
:type email: Any
:return: Description of return value.
:rtype: Any"""
    if email and (not is_valid_email(email)):
        return 'Email is not written correctly.'
    return None

def refresh_all():
    """Function refresh_all.

:return: Description of return value.
:rtype: Any"""
    refresh_students()
    refresh_instructors()
    refresh_courses()
    refresh_dropdowns()

def _student_course_tokens(sid: str):
    """Function _student_course_tokens.

:param sid: Description of sid.
:type sid: Any
:return: Description of return value.
:rtype: Any"""
    cids = DATA['students'].get(sid, {}).get('courses', [])
    names = [DATA['courses'][cid]['name'] for cid in cids if cid in DATA['courses']]
    return cids + names

def _instructor_course_tokens(iid: str):
    """Function _instructor_course_tokens.

:param iid: Description of iid.
:type iid: Any
:return: Description of return value.
:rtype: Any"""
    cids = [cid for cid, c in DATA['courses'].items() if c.get('instructor_id') == iid]
    names = [DATA['courses'][cid]['name'] for cid in cids if cid in DATA['courses']]
    return cids + names

def refresh_students(query: str=''):
    """Function refresh_students.

:param query: Description of query.
:type query: Any
:return: Description of return value.
:rtype: Any"""
    for i in tree_students.get_children():
        tree_students.delete(i)
    q = (query or '').lower().strip()
    for sid, s in DATA['students'].items():
        course_bits = _student_course_tokens(sid)
        hay = ' '.join([sid, s['name'], s['email'], *course_bits]).lower()
        if q and q not in hay:
            continue
        tree_students.insert('', 'end', values=(sid, s['name'], s['age'], s['email']))

def refresh_instructors(query: str=''):
    """Function refresh_instructors.

:param query: Description of query.
:type query: Any
:return: Description of return value.
:rtype: Any"""
    for i in tree_instructors.get_children():
        tree_instructors.delete(i)
    q = (query or '').lower().strip()
    for iid, ins in DATA['instructors'].items():
        course_bits = _instructor_course_tokens(iid)
        hay = ' '.join([iid, ins['name'], ins['email'], *course_bits]).lower()
        if q and q not in hay:
            continue
        tree_instructors.insert('', 'end', values=(iid, ins['name'], ins['age'], ins['email']))

def refresh_courses(query: str=''):
    """Function refresh_courses.

:param query: Description of query.
:type query: Any
:return: Description of return value.
:rtype: Any"""
    for i in tree_courses.get_children():
        tree_courses.delete(i)
    q = (query or '').lower().strip()
    for cid, c in DATA['courses'].items():
        display = f"{cid} {c['name']} {c.get('instructor_id', '')}"
        if q and q not in display.lower():
            continue
        instructor_name = DATA['instructors'].get(c.get('instructor_id', ''), {}).get('name', '')
        tree_courses.insert('', 'end', values=(cid, c['name'], c.get('instructor_id', ''), instructor_name, ','.join(c.get('students', []))))

def refresh_dropdowns():
    """Function refresh_dropdowns.

:return: Description of return value.
:rtype: Any"""
    course_ids = list(DATA['courses'].keys())
    student_ids = list(DATA['students'].keys())
    instructor_ids = list(DATA['instructors'].keys())
    combo_course_assign['values'] = course_ids
    combo_instructor['values'] = instructor_ids
    combo_student['values'] = student_ids
    combo_course['values'] = course_ids

def add_student():
    """Function add_student.

:return: Description of return value.
:rtype: Any"""
    sid = e_sid.get().strip()
    name = e_sname.get().strip()
    age = e_sage.get().strip()
    email = e_semail.get().strip()
    missing_msg = _missing_fields_message([('ID', sid), ('Name', name), ('Age', age), ('Email', email)])
    if missing_msg:
        messagebox.showerror('Validation', missing_msg)
        return
    email_msg = _email_error_message(email)
    if email_msg:
        messagebox.showerror('Validation', email_msg)
        return
    if not is_valid_age(age):
        messagebox.showerror('Validation', 'Age must be a non-negative integer.')
        return
    DATA['students'][sid] = {'name': name, 'age': int(age), 'email': email, 'courses': []}
    refresh_students()
    refresh_dropdowns()

def add_instructor():
    """Function add_instructor.

:return: Description of return value.
:rtype: Any"""
    iid = e_iid.get().strip()
    name = e_iname.get().strip()
    age = e_iage.get().strip()
    email = e_iemail.get().strip()
    missing_msg = _missing_fields_message([('ID', iid), ('Name', name), ('Age', age), ('Email', email)])
    if missing_msg:
        messagebox.showerror('Validation', missing_msg)
        return
    email_msg = _email_error_message(email)
    if email_msg:
        messagebox.showerror('Validation', email_msg)
        return
    if not is_valid_age(age):
        messagebox.showerror('Validation', 'Age must be a non-negative integer.')
        return
    DATA['instructors'][iid] = {'name': name, 'age': int(age), 'email': email, 'courses': []}
    refresh_instructors()
    refresh_dropdowns()

def add_course():
    """Function add_course.

:return: Description of return value.
:rtype: Any"""
    cid = e_cid.get().strip()
    name = e_cname.get().strip()
    missing_msg = _missing_fields_message([('ID', cid), ('Name', name)])
    if missing_msg:
        messagebox.showerror('Validation', missing_msg)
        return
    DATA['courses'][cid] = {'name': name, 'instructor_id': None, 'students': []}
    refresh_courses()
    refresh_dropdowns()

def assign_instructor():
    """Function assign_instructor.

:return: Description of return value.
:rtype: Any"""
    cid = combo_course_assign.get().strip()
    iid = combo_instructor.get().strip()
    if not cid:
        messagebox.showerror('Validation', 'Select a course.')
        return
    if cid not in DATA['courses']:
        return
    DATA['courses'][cid]['instructor_id'] = iid if iid else None
    refresh_courses()

def register_student():
    """Function register_student.

:return: Description of return value.
:rtype: Any"""
    sid = combo_student.get().strip()
    cid = combo_course.get().strip()
    if not sid or not cid:
        messagebox.showerror('Validation', 'Select student and course.')
        return
    if sid not in DATA['students'] or cid not in DATA['courses']:
        return
    if sid not in DATA['courses'][cid]['students']:
        DATA['courses'][cid]['students'].append(sid)
    if cid not in DATA['students'][sid]['courses']:
        DATA['students'][sid]['courses'].append(cid)
    refresh_courses()

def delete_selected(tree, kind):
    """Function delete_selected.

:param tree: Description of tree.
:type tree: Any
:param kind: Description of kind.
:type kind: Any
:return: Description of return value.
:rtype: Any"""
    sel = tree.selection()
    if not sel:
        return
    key = tree.item(sel[0], 'values')[0]
    if kind == 'student':
        DATA['students'].pop(key, None)
        for c in DATA['courses'].values():
            if key in c.get('students', []):
                c['students'].remove(key)
        refresh_students()
        refresh_courses()
        refresh_dropdowns()
    elif kind == 'instructor':
        DATA['instructors'].pop(key, None)
        for c in DATA['courses'].values():
            if c.get('instructor_id') == key:
                c['instructor_id'] = None
        refresh_instructors()
        refresh_courses()
        refresh_dropdowns()
    elif kind == 'course':
        DATA['courses'].pop(key, None)
        for s in DATA['students'].values():
            if key in s.get('courses', []):
                s['courses'].remove(key)
        refresh_courses()
        refresh_dropdowns()

def save_json():
    """Function save_json.

:return: Description of return value.
:rtype: Any"""
    path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON', '*.json')])
    if not path:
        return
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, indent=2)
    messagebox.showinfo('Saved', f'Saved to {path}')

def load_json():
    """Function load_json.

:return: Description of return value.
:rtype: Any"""
    path = filedialog.askopenfilename(filetypes=[('JSON', '*.json')])
    if not path:
        return
    global DATA
    with open(path, 'r', encoding='utf-8') as f:
        DATA = json.load(f)
    refresh_all()
    messagebox.showinfo('Loaded', f'Loaded from {path}')
root = tk.Tk()
root.title('School Management System')
root.geometry('1100x720')
nb = ttk.Notebook(root)
nb.pack(fill='both', expand=True)
tab_s = ttk.Frame(nb)
nb.add(tab_s, text='Students')
frm_s = ttk.LabelFrame(tab_s, text='Student Form')
frm_s.pack(fill='x', padx=8, pady=8)
ttk.Label(frm_s, text='ID').grid(row=0, column=0)
e_sid = ttk.Entry(frm_s)
e_sid.grid(row=0, column=1)
ttk.Label(frm_s, text='Name').grid(row=0, column=2)
e_sname = ttk.Entry(frm_s)
e_sname.grid(row=0, column=3)
ttk.Label(frm_s, text='Age').grid(row=1, column=0)
e_sage = ttk.Entry(frm_s)
e_sage.grid(row=1, column=1)
ttk.Label(frm_s, text='Email').grid(row=1, column=2)
e_semail = ttk.Entry(frm_s)
e_semail.grid(row=1, column=3)
ttk.Button(frm_s, text='Add/Update', command=add_student).grid(row=0, column=4, padx=6)
ttk.Button(frm_s, text='Delete Selected', command=lambda: delete_selected(tree_students, 'student')).grid(row=1, column=4, padx=6)
ttk.Label(frm_s, text='Search').grid(row=2, column=0)
e_ssearch = ttk.Entry(frm_s)
e_ssearch.grid(row=2, column=1)
ttk.Button(frm_s, text='Go', command=lambda: refresh_students(e_ssearch.get())).grid(row=2, column=2)
tree_students = ttk.Treeview(tab_s, columns=('ID', 'Name', 'Age', 'Email'), show='headings', height=12)
for c in ('ID', 'Name', 'Age', 'Email'):
    tree_students.heading(c, text=c)
tree_students.pack(fill='both', expand=True, padx=8, pady=8)
tab_i = ttk.Frame(nb)
nb.add(tab_i, text='Instructors')
frm_i = ttk.LabelFrame(tab_i, text='Instructor Form')
frm_i.pack(fill='x', padx=8, pady=8)
ttk.Label(frm_i, text='ID').grid(row=0, column=0)
e_iid = ttk.Entry(frm_i)
e_iid.grid(row=0, column=1)
ttk.Label(frm_i, text='Name').grid(row=0, column=2)
e_iname = ttk.Entry(frm_i)
e_iname.grid(row=0, column=3)
ttk.Label(frm_i, text='Age').grid(row=1, column=0)
e_iage = ttk.Entry(frm_i)
e_iage.grid(row=1, column=1)
ttk.Label(frm_i, text='Email').grid(row=1, column=2)
e_iemail = ttk.Entry(frm_i)
e_iemail.grid(row=1, column=3)
ttk.Button(frm_i, text='Add/Update', command=add_instructor).grid(row=0, column=4, padx=6)
ttk.Button(frm_i, text='Delete Selected', command=lambda: delete_selected(tree_instructors, 'instructor')).grid(row=1, column=4, padx=6)
ttk.Label(frm_i, text='Search').grid(row=2, column=0)
e_isearch = ttk.Entry(frm_i)
e_isearch.grid(row=2, column=1)
ttk.Button(frm_i, text='Go', command=lambda: refresh_instructors(e_isearch.get())).grid(row=2, column=2)
tree_instructors = ttk.Treeview(tab_i, columns=('ID', 'Name', 'Age', 'Email'), show='headings', height=12)
for c in ('ID', 'Name', 'Age', 'Email'):
    tree_instructors.heading(c, text=c)
tree_instructors.pack(fill='both', expand=True, padx=8, pady=8)
tab_c = ttk.Frame(nb)
nb.add(tab_c, text='Courses')
frm_c = ttk.LabelFrame(tab_c, text='Course Form')
frm_c.pack(fill='x', padx=8, pady=8)
ttk.Label(frm_c, text='Course ID').grid(row=0, column=0)
e_cid = ttk.Entry(frm_c)
e_cid.grid(row=0, column=1)
ttk.Label(frm_c, text='Course Name').grid(row=0, column=2)
e_cname = ttk.Entry(frm_c)
e_cname.grid(row=0, column=3)
ttk.Button(frm_c, text='Add/Update', command=add_course).grid(row=0, column=4, padx=6)
assign = ttk.LabelFrame(tab_c, text='Assignments & Registrations')
assign.pack(fill='x', padx=8, pady=8)
ttk.Label(assign, text='Course').grid(row=0, column=0)
combo_course_assign = ttk.Combobox(assign, state='readonly')
combo_course_assign.grid(row=0, column=1)
ttk.Label(assign, text='Instructor').grid(row=0, column=2)
combo_instructor = ttk.Combobox(assign, state='readonly')
combo_instructor.grid(row=0, column=3)
ttk.Button(assign, text='Assign Instructor', command=assign_instructor).grid(row=0, column=4, padx=6)
ttk.Label(assign, text='Student').grid(row=1, column=0)
combo_student = ttk.Combobox(assign, state='readonly')
combo_student.grid(row=1, column=1)
ttk.Label(assign, text='Course').grid(row=1, column=2)
combo_course = ttk.Combobox(assign, state='readonly')
combo_course.grid(row=1, column=3)
ttk.Button(assign, text='Register', command=register_student).grid(row=1, column=4, padx=6)
tool = ttk.Frame(tab_c)
tool.pack(fill='x', padx=8, pady=8)
ttk.Button(tool, text='Save JSON', command=save_json).pack(side='left', padx=4)
ttk.Button(tool, text='Load JSON', command=load_json).pack(side='left', padx=4)
ttk.Label(tab_c, text='Search').pack(anchor='w', padx=10)
e_csearch = ttk.Entry(tab_c)
e_csearch.pack(anchor='w', padx=10, pady=4)
ttk.Button(tab_c, text='Go', command=lambda: refresh_courses(e_csearch.get())).pack(anchor='w', padx=10)
tree_courses = ttk.Treeview(tab_c, columns=('ID', 'Name', 'InstructorID', 'InstructorName', 'Students'), show='headings', height=12)
for c in ('ID', 'Name', 'InstructorID', 'InstructorName', 'Students'):
    tree_courses.heading(c, text=c)
tree_courses.pack(fill='both', expand=True, padx=8, pady=8)
ttk.Button(tab_c, text='Delete Selected', command=lambda: delete_selected(tree_courses, 'course')).pack(pady=8)
refresh_all()
root.mainloop()
