"""PyQt5 GUI for a simple school management system.

This module implements a desktop UI to manage students, instructors, and
courses. It supports adding/updating/deleting records, assigning instructors,
registering students into courses, simple search, and exporting data to JSON,
CSV, and plain-text "pretty" tables.
"""
import sys, os, json, csv, re
from PyQt5 import QtWidgets


def write_pretty_table(headers, rows, path):
    """Write a fixed-width plain-text table to ``path``.

    Columns are sized to the widest value so the output lines up in any text
    editor or terminal. The destination directory is created if needed.

    :param headers: Column headings, one per column.
    :type headers: list[str]
    :param rows: Table rows; each row is a list of values matching ``headers`` length.
    :type rows: list[list[object]]
    :param path: Destination file path for the generated table (``.txt`` recommended).
    :type path: str
    :return: None
    :rtype: None
    """
    import os
    widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(str(cell)))
    sep = '  '
    header_line = sep.join((f'{headers[i]:<{widths[i]}}' for i in range(len(headers))))
    divider = sep.join(('-' * widths[i] for i in range(len(headers))))
    lines = [header_line, divider]
    for r in rows:
        lines.append(sep.join((f'{str(r[i]):<{widths[i]}}' for i in range(len(headers)))))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


EMAIL_RE = re.compile('^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$')


def is_valid_email(email: str) -> bool:
    """Return ``True`` if ``email`` looks valid.

    A small regex is used to catch common mistakes (missing ``@``, spaces, etc.).
    It is not intended to be fully RFC-compliant.

    :param email: Email address to validate.
    :type email: str
    :return: ``True`` if the pattern matches, else ``False``.
    :rtype: bool
    """
    return bool(EMAIL_RE.match(email))


def is_valid_age(age: str) -> bool:
    """Return ``True`` if ``age`` parses to a non-negative integer.

    :param age: Age value as a string (e.g., ``"18"``).
    :type age: str
    :return: ``True`` for integers ``>= 0``, else ``False``.
    :rtype: bool
    """
    try:
        return int(age) >= 0
    except Exception:
        return False


DATA = {'students': {}, 'instructors': {}, 'courses': {}}


class Main(QtWidgets.QMainWindow):
    """Main application window with Students/Instructors/Courses tabs."""

    def __init__(self):
        """Initialize the main window and populate initial UI state.

        Sets title/size, builds widgets and layouts, and refreshes all tables/
        dropdowns to reflect the current in-memory ``DATA`` store.
        """
        super().__init__()
        self.setWindowTitle('School Management System')
        self.resize(1100, 720)
        self._build()
        self.refresh_all()

    def _build(self):
        """Create all tabs, forms, tables, and wire up signals/slots.

        This method constructs three tabs:
        - **Students**: add/update/delete + search
        - **Instructors**: add/update/delete + search
        - **Courses**: add/update, assign instructor, register student, search,
          export tools (JSON/CSV/"pretty" text)
        """
        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # ---------------- Students tab ----------------
        ts = QtWidgets.QWidget()
        tabs.addTab(ts, 'Students')
        s_layout = QtWidgets.QVBoxLayout(ts)

        s_form = QtWidgets.QGroupBox('Student Form')
        s_layout.addWidget(s_form)
        grid = QtWidgets.QGridLayout(s_form)

        self.s_id = QtWidgets.QLineEdit()
        self.s_id.setPlaceholderText('ID')
        self.s_name = QtWidgets.QLineEdit()
        self.s_name.setPlaceholderText('Name')
        self.s_age = QtWidgets.QLineEdit()
        self.s_age.setPlaceholderText('Age (non-negative)')
        self.s_email = QtWidgets.QLineEdit()
        self.s_email.setPlaceholderText('Email (e.g., name@example.com)')

        grid.addWidget(QtWidgets.QLabel('ID'), 0, 0)
        grid.addWidget(self.s_id, 0, 1)
        grid.addWidget(QtWidgets.QLabel('Name'), 0, 2)
        grid.addWidget(self.s_name, 0, 3)
        grid.addWidget(QtWidgets.QLabel('Age'), 1, 0)
        grid.addWidget(self.s_age, 1, 1)
        grid.addWidget(QtWidgets.QLabel('Email'), 1, 2)
        grid.addWidget(self.s_email, 1, 3)

        add_s = QtWidgets.QPushButton('Add/Update')
        add_s.clicked.connect(self.add_student)
        del_s = QtWidgets.QPushButton('Delete Selected')
        del_s.clicked.connect(lambda: self.delete_selected(self.s_table, 'student'))
        grid.addWidget(add_s, 0, 4)
        grid.addWidget(del_s, 1, 4)

        self.s_search = QtWidgets.QLineEdit()
        self.s_search.setPlaceholderText('Search by ID, name, email, course…')
        go_s = QtWidgets.QPushButton('Go')
        go_s.clicked.connect(lambda: self.refresh_students(self.s_search.text()))
        grid.addWidget(QtWidgets.QLabel('Search'), 2, 0)
        grid.addWidget(self.s_search, 2, 1)
        grid.addWidget(go_s, 2, 2)

        self.s_table = QtWidgets.QTableWidget(0, 4)
        self.s_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email'])
        self.s_table.horizontalHeader().setStretchLastSection(True)
        s_layout.addWidget(self.s_table)

        # ---------------- Instructors tab ----------------
        ti = QtWidgets.QWidget()
        tabs.addTab(ti, 'Instructors')
        i_layout = QtWidgets.QVBoxLayout(ti)

        i_form = QtWidgets.QGroupBox('Instructor Form')
        i_layout.addWidget(i_form)
        grid2 = QtWidgets.QGridLayout(i_form)

        self.i_id = QtWidgets.QLineEdit()
        self.i_id.setPlaceholderText('ID')
        self.i_name = QtWidgets.QLineEdit()
        self.i_name.setPlaceholderText('Name')
        self.i_age = QtWidgets.QLineEdit()
        self.i_age.setPlaceholderText('Age (non-negative)')
        self.i_email = QtWidgets.QLineEdit()
        self.i_email.setPlaceholderText('Email (e.g., name@example.com)')

        grid2.addWidget(QtWidgets.QLabel('ID'), 0, 0)
        grid2.addWidget(self.i_id, 0, 1)
        grid2.addWidget(QtWidgets.QLabel('Name'), 0, 2)
        grid2.addWidget(self.i_name, 0, 3)
        grid2.addWidget(QtWidgets.QLabel('Age'), 1, 0)
        grid2.addWidget(self.i_age, 1, 1)
        grid2.addWidget(QtWidgets.QLabel('Email'), 1, 2)
        grid2.addWidget(self.i_email, 1, 3)

        add_i = QtWidgets.QPushButton('Add/Update')
        add_i.clicked.connect(self.add_instructor)
        del_i = QtWidgets.QPushButton('Delete Selected')
        del_i.clicked.connect(lambda: self.delete_selected(self.i_table, 'instructor'))
        grid2.addWidget(add_i, 0, 4)
        grid2.addWidget(del_i, 1, 4)

        self.i_search = QtWidgets.QLineEdit()
        self.i_search.setPlaceholderText('Search by ID, name, email, course…')
        go_i = QtWidgets.QPushButton('Go')
        go_i.clicked.connect(lambda: self.refresh_instructors(self.i_search.text()))
        grid2.addWidget(QtWidgets.QLabel('Search'), 2, 0)
        grid2.addWidget(self.i_search, 2, 1)
        grid2.addWidget(go_i, 2, 2)

        self.i_table = QtWidgets.QTableWidget(0, 4)
        self.i_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email'])
        self.i_table.horizontalHeader().setStretchLastSection(True)
        i_layout.addWidget(self.i_table)

        # ---------------- Courses tab ----------------
        tc = QtWidgets.QWidget()
        tabs.addTab(tc, 'Courses')
        c_layout = QtWidgets.QVBoxLayout(tc)

        c_form = QtWidgets.QGroupBox('Course Form')
        c_layout.addWidget(c_form)
        grid3 = QtWidgets.QGridLayout(c_form)

        self.c_id = QtWidgets.QLineEdit()
        self.c_id.setPlaceholderText('Course ID')
        self.c_name = QtWidgets.QLineEdit()
        self.c_name.setPlaceholderText('Course Name')

        grid3.addWidget(QtWidgets.QLabel('Course ID'), 0, 0)
        grid3.addWidget(self.c_id, 0, 1)
        grid3.addWidget(QtWidgets.QLabel('Course Name'), 0, 2)
        grid3.addWidget(self.c_name, 0, 3)

        add_c = QtWidgets.QPushButton('Add/Update')
        add_c.clicked.connect(self.add_course)
        grid3.addWidget(add_c, 0, 4)

        assign = QtWidgets.QGroupBox('Assignments & Registrations')
        c_layout.addWidget(assign)
        grid4 = QtWidgets.QGridLayout(assign)

        self.course_combo_assign = QtWidgets.QComboBox()
        self.instructor_combo = QtWidgets.QComboBox()
        self.student_combo = QtWidgets.QComboBox()
        self.course_combo = QtWidgets.QComboBox()

        grid4.addWidget(QtWidgets.QLabel('Course'), 0, 0)
        grid4.addWidget(self.course_combo_assign, 0, 1)
        grid4.addWidget(QtWidgets.QLabel('Instructor'), 0, 2)
        grid4.addWidget(self.instructor_combo, 0, 3)
        btn_assign = QtWidgets.QPushButton('Assign Instructor')
        btn_assign.clicked.connect(self.assign_instructor)
        grid4.addWidget(btn_assign, 0, 4)

        grid4.addWidget(QtWidgets.QLabel('Student'), 1, 0)
        grid4.addWidget(self.student_combo, 1, 1)
        grid4.addWidget(QtWidgets.QLabel('Course'), 1, 2)
        grid4.addWidget(self.course_combo, 1, 3)
        btn_reg = QtWidgets.QPushButton('Register Student')
        btn_reg.clicked.connect(self.register_student)
        grid4.addWidget(btn_reg, 1, 4)

        tools = QtWidgets.QHBoxLayout()
        btn_save = QtWidgets.QPushButton('Save JSON')
        btn_save.clicked.connect(self.save_json)
        btn_load = QtWidgets.QPushButton('Load JSON')
        btn_load.clicked.connect(self.load_json)
        btn_csv = QtWidgets.QPushButton('Export CSVs')
        btn_csv.clicked.connect(self.export_csvs)
        tools.addWidget(btn_save)
        tools.addWidget(btn_load)
        tools.addWidget(btn_csv)
        c_layout.addLayout(tools)

        self.c_search = QtWidgets.QLineEdit()
        self.c_search.setPlaceholderText('Search by course id, name, instructor…')
        go_c = QtWidgets.QPushButton('Go')
        go_c.clicked.connect(lambda: self.refresh_courses(self.c_search.text()))
        sr = QtWidgets.QHBoxLayout()
        sr.addWidget(QtWidgets.QLabel('Search'))
        sr.addWidget(self.c_search)
        sr.addWidget(go_c)
        c_layout.addLayout(sr)

        self.c_table = QtWidgets.QTableWidget(0, 5)
        self.c_table.setHorizontalHeaderLabels(['ID', 'Name', 'InstructorID', 'InstructorName', 'Students'])
        self.c_table.horizontalHeader().setStretchLastSection(True)
        c_layout.addWidget(self.c_table)

        del_c = QtWidgets.QPushButton('Delete Selected Course')
        del_c.clicked.connect(lambda: self.delete_selected(self.c_table, 'course'))
        c_layout.addWidget(del_c)

    def refresh_all(self):
        """Refresh all tables and dropdowns from the in-memory data store."""
        self.refresh_students()
        self.refresh_instructors()
        self.refresh_courses()
        self.refresh_dropdowns()

    def refresh_students(self, q: str=''):
        """Populate the Students table, optionally filtered by a query.

        The search is case-insensitive and checks ID, name, email, and the
        student's course IDs/names.

        :param q: Free-text query to filter rows. Empty string shows all.
        :type q: str
        :return: None
        :rtype: None
        """
        self._fill_table(self.s_table, [])
        q = (q or '').lower().strip()
        rows = []
        for sid, s in DATA['students'].items():
            course_bits = _student_course_tokens(sid)
            hay = ' '.join([sid, s['name'], s['email'], *course_bits]).lower()
            if q and q not in hay:
                continue
            rows.append((sid, s['name'], s['age'], s['email']))
        self._fill_table(self.s_table, rows)

    def refresh_instructors(self, q: str=''):
        """Populate the Instructors table, optionally filtered by a query.

        The search is case-insensitive and checks ID, name, email, and the
        instructor's assigned course IDs/names.

        :param q: Free-text query to filter rows. Empty string shows all.
        :type q: str
        :return: None
        :rtype: None
        """
        self._fill_table(self.i_table, [])
        q = (q or '').lower().strip()
        rows = []
        for iid, ins in DATA['instructors'].items():
            course_bits = _instructor_course_tokens(iid)
            hay = ' '.join([iid, ins['name'], ins['email'], *course_bits]).lower()
            if q and q not in hay:
                continue
            rows.append((iid, ins['name'], ins['age'], ins['email']))
        self._fill_table(self.i_table, rows)

    def refresh_courses(self, q: str=''):
        """Populate the Courses table, optionally filtered by a query.

        The search is case-insensitive and checks course ID, name, and assigned
        instructor ID.

        :param q: Free-text query to filter rows. Empty string shows all.
        :type q: str
        :return: None
        :rtype: None
        """

        def inst_name(iid):
            """Return the instructor's name for an instructor ID.

            :param iid: Instructor ID.
            :type iid: str
            :return: Instructor's display name or empty string if not found.
            :rtype: str
            """
            return DATA['instructors'].get(iid, {}).get('name', '')
        rows = []
        for cid, c in DATA['courses'].items():
            disp = f"{cid} {c['name']} {c.get('instructor_id', '')}"
            if q and q.lower() not in disp.lower():
                continue
            rows.append((cid, c['name'], c.get('instructor_id', ''), inst_name(c.get('instructor_id', '')), ','.join(c.get('students', []))))
        self._fill_table(self.c_table, rows)

    def refresh_dropdowns(self):
        """Refresh all combo boxes (course, instructor, student pickers)."""

        def load_combo(combo, items):
            """Replace the contents of a ``QComboBox`` with the given items.

            :param combo: Combo box to update.
            :type combo: QtWidgets.QComboBox
            :param items: Items to insert (displayed as strings).
            :type items: list[str]
            :return: None
            :rtype: None
            """
            combo.clear()
            combo.addItems(items)
        load_combo(self.course_combo_assign, list(DATA['courses'].keys()))
        load_combo(self.instructor_combo, list(DATA['instructors'].keys()))
        load_combo(self.student_combo, list(DATA['students'].keys()))
        load_combo(self.course_combo, list(DATA['courses'].keys()))

    def _fill_table(self, table, rows):
        """Fill a ``QTableWidget`` with the provided rows.

        :param table: Table to populate.
        :type table: QtWidgets.QTableWidget
        :param rows: Iterable of row tuples/lists to insert.
        :type rows: list[list[object]] | list[tuple[object, ...]]
        :return: None
        :rtype: None
        """
        table.setRowCount(0)
        for r in rows:
            row = table.rowCount()
            table.insertRow(row)
            for c, val in enumerate(r):
                table.setItem(row, c, QtWidgets.QTableWidgetItem(str(val)))

    def _missing_fields_message(self, pairs):
        """Return a user-friendly message if any required fields are empty.

        :param pairs: List of ``(Label, value)`` tuples to validate.
        :type pairs: list[tuple[str, object]]
        :return: ``None`` if all present, otherwise an error message string.
        :rtype: str | None
        """
        missing = [lbl for lbl, val in pairs if not str(val).strip()]
        if missing:
            msg = 'Missing data needed: ' + ', '.join((lbl.lower() for lbl in missing))
            return msg
        return None

    def _email_error_message(self, email):
        """Return an email validation message or ``None`` if valid.

        :param email: Email address to check.
        :type email: str
        :return: ``'Email is not written correctly.'`` if invalid, else ``None``.
        :rtype: str | None
        """
        if email and (not is_valid_email(email)):
            return 'Email is not written correctly.'
        return None

    def add_student(self):
        """Add or update a student from the form fields.

        Performs required-field checks, email validation, and non-negative age
        validation. Updates the in-memory ``DATA`` store and refreshes the UI.
        """
        sid = self.s_id.text().strip()
        name = self.s_name.text().strip()
        age = self.s_age.text().strip()
        email = self.s_email.text().strip()

        missing_msg = self._missing_fields_message([('ID', sid), ('Name', name), ('Age', age), ('Email', email)])
        if missing_msg:
            QtWidgets.QMessageBox.critical(self, 'Validation', missing_msg)
            return
        email_msg = self._email_error_message(email)
        if email_msg:
            QtWidgets.QMessageBox.critical(self, 'Validation', email_msg)
            return
        if not is_valid_age(age):
            QtWidgets.QMessageBox.critical(self, 'Validation', 'Age must be a non-negative integer.')
            return

        DATA['students'][sid] = {'name': name, 'age': int(age), 'email': email, 'courses': []}
        self.refresh_students()
        self.refresh_dropdowns()

    def add_instructor(self):
        """Add or update an instructor from the form fields.

        Performs required-field checks, email validation, and non-negative age
        validation. Updates the in-memory ``DATA`` store and refreshes the UI.
        """
        iid = self.i_id.text().strip()
        name = self.i_name.text().strip()
        age = self.i_age.text().strip()
        email = self.i_email.text().strip()

        missing_msg = self._missing_fields_message([('ID', iid), ('Name', name), ('Age', age), ('Email', email)])
        if missing_msg:
            QtWidgets.QMessageBox.critical(self, 'Validation', missing_msg)
            return
        email_msg = self._email_error_message(email)
        if email_msg:
            QtWidgets.QMessageBox.critical(self, 'Validation', email_msg)
            return
        if not is_valid_age(age):
            QtWidgets.QMessageBox.critical(self, 'Validation', 'Age must be a non-negative integer.')
            return

        DATA['instructors'][iid] = {'name': name, 'age': int(age), 'email': email, 'courses': []}
        self.refresh_instructors()
        self.refresh_dropdowns()

    def add_course(self):
        """Add or update a course from the form fields.

        Requires a course ID and name. Updates the in-memory ``DATA`` store and
        refreshes the UI.
        """
        cid = self.c_id.text().strip()
        name = self.c_name.text().strip()
        missing_msg = self._missing_fields_message([('ID', cid), ('Name', name)])
        if missing_msg:
            QtWidgets.QMessageBox.critical(self, 'Validation', missing_msg)
            return
        DATA['courses'][cid] = {'name': name, 'instructor_id': None, 'students': []}
        self.refresh_courses()
        self.refresh_dropdowns()

    def assign_instructor(self):
        """Assign the selected instructor to the selected course."""
        cid = self.course_combo_assign.currentText().strip()
        iid = self.instructor_combo.currentText().strip()
        if not cid:
            QtWidgets.QMessageBox.critical(self, 'Validation', 'Select a course.')
            return
        if cid in DATA['courses']:
            DATA['courses'][cid]['instructor_id'] = iid if iid else None
        self.refresh_courses()

    def register_student(self):
        """Register the selected student into the selected course.

        Keeps both sides in sync:
        - Adds the student ID to the course's ``students`` list.
        - Adds the course ID to the student's ``courses`` list.
        """
        sid = self.student_combo.currentText().strip()
        cid = self.course_combo.currentText().strip()
        if not sid or not cid:
            QtWidgets.QMessageBox.critical(self, 'Validation', 'Select student and course.')
            return
        if sid in DATA['students'] and cid in DATA['courses']:
            if sid not in DATA['courses'][cid]['students']:
                DATA['courses'][cid]['students'].append(sid)
            if cid not in DATA['students'][sid]['courses']:
                DATA['students'][sid]['courses'].append(cid)
        self.refresh_courses()

    def delete_selected(self, table, kind):
        """Delete the currently selected row of the given table.

        Adjusts related data to keep the in-memory model consistent and then
        refreshes the affected tables and dropdowns.

        :param table: Source table (students, instructors, or courses table).
        :type table: QtWidgets.QTableWidget
        :param kind: One of ``'student'``, ``'instructor'``, or ``'course'``.
        :type kind: str
        :return: None
        :rtype: None
        """
        row = table.currentRow()
        if row < 0:
            return
        key = table.item(row, 0).text()
        if kind == 'student':
            DATA['students'].pop(key, None)
            for c in DATA['courses'].values():
                if key in c.get('students', []):
                    c['students'].remove(key)
            self.refresh_students()
            self.refresh_courses()
            self.refresh_dropdowns()
        elif kind == 'instructor':
            DATA['instructors'].pop(key, None)
            for c in DATA['courses'].values():
                if c.get('instructor_id') == key:
                    c['instructor_id'] = None
            self.refresh_instructors()
            self.refresh_courses()
            self.refresh_dropdowns()
        elif kind == 'course':
            DATA['courses'].pop(key, None)
            for s in DATA['students'].values():
                if key in s.get('courses', []):
                    s['courses'].remove(key)
            self.refresh_courses()
            self.refresh_dropdowns()

    def save_json(self):
        """Save the in-memory ``DATA`` store to a JSON file chosen by the user."""
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save JSON', '', 'JSON (*.json)')
        if not path:
            return
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(DATA, f, indent=2)
        QtWidgets.QMessageBox.information(self, 'Saved', f'Saved to {path}')

    def load_json(self):
        """Load the ``DATA`` store from a JSON file chosen by the user."""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load JSON', '', 'JSON (*.json)')
        if not path:
            return
        global DATA
        with open(path, 'r', encoding='utf-8') as f:
            DATA = json.load(f)
        self.refresh_all()
        QtWidgets.QMessageBox.information(self, 'Loaded', f'Loaded from {path}')

    def export_csvs(self):
        """Export CSV files and pretty text tables to a folder.

        Creates:
        - ``students.csv`` with ID, name, age, email, courses
        - ``instructors.csv`` with ID, name, age, email
        - ``courses.csv`` with course ID, name, instructor ID, students

        Also writes fixed-width text tables in ``pretty_tables`` for quick viewing.
        """
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Folder')
        if not folder:
            return

        # Students CSV
        headers_s = ['student_id', 'name', 'age', 'email', 'courses']
        rows_s = []
        for sid, s in DATA['students'].items():
            courses = ';'.join(s.get('courses', [])) or '-'
            rows_s.append([sid, s['name'], s['age'], s['email'], courses])
        with open(os.path.join(folder, 'students.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers_s)
            w.writerows(rows_s)

        # Instructors CSV
        headers_i = ['instructor_id', 'name', 'age', 'email']
        rows_i = [[iid, i['name'], i['age'], i['email']] for iid, i in DATA['instructors'].items()]
        with open(os.path.join(folder, 'instructors.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers_i)
            w.writerows(rows_i)

        # Courses CSV
        headers_c = ['course_id', 'name', 'instructor_id', 'students']
        rows_c = []
        for cid, c in DATA['courses'].items():
            students = ';'.join(c.get('students', [])) or '-'
            iid = c.get('instructor_id') or '-'
            rows_c.append([cid, c['name'], iid, students])
        with open(os.path.join(folder, 'courses.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.writer(f)
            w.writerow(headers_c)
            w.writerows(rows_c)

        # Pretty text tables
        pretty_dir = os.path.join(folder, 'pretty_tables')
        write_pretty_table(headers_s, rows_s, os.path.join(pretty_dir, 'students_pretty.txt'))
        write_pretty_table(headers_i, rows_i, os.path.join(pretty_dir, 'instructors_pretty.txt'))
        write_pretty_table(headers_c, rows_c, os.path.join(pretty_dir, 'courses_pretty.txt'))
        QtWidgets.QMessageBox.information(self, 'Export', f'Files saved to {folder} (CSV + pretty_tables/*.txt)')


def _student_course_tokens(sid: str):
    """Return the student's course IDs + names (used for search matching)."""
    cids = DATA['students'].get(sid, {}).get('courses', [])
    names = [DATA['courses'][cid]['name'] for cid in cids if cid in DATA['courses']]
    return cids + names


def _instructor_course_tokens(iid: str):
    """Return the instructor's assigned course IDs + names (for search)."""
    cids = [cid for cid, c in DATA['courses'].items() if c.get('instructor_id') == iid]
    names = [DATA['courses'][cid]['name'] for cid in cids if cid in DATA['courses']]
    return cids + names


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Main()
    w.show()
    sys.exit(app.exec_())
