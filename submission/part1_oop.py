"""Core OOP models and utilities for a simple school management system.

This module defines the domain objects (``Person``, ``Student``, ``Instructor``,
``Course``) and helpers to validate input, serialize/deserialize data, and
export reports to CSV and plain-text "pretty" tables.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import json, csv, re


def write_pretty_table(headers: List[str], rows: List[List[Any]], path: str) -> None:
    """Write a fixed-width plain-text table to a file.

    Columns are sized to the widest value in each column so the result is easy
    to read in any text editor. The parent directory is created if needed.

    :param headers: Column headings, one per column.
    :type headers: list[str]
    :param rows: Table rows; each row is a list with the same length as ``headers``.
    :type rows: list[list[Any]]
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

    sep = "  "
    header_line = sep.join(f"{headers[i]:<{widths[i]}}" for i in range(len(headers)))
    divider = sep.join("-" * widths[i] for i in range(len(headers)))

    lines = [header_line, divider]
    for r in rows:
        lines.append(sep.join(f"{str(r[i]):<{widths[i]}}" for i in range(len(headers))))

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """Return ``True`` if the string looks like a valid email address.

    A simple regex is used to catch the most common mistakes (missing ``@``,
    spaces, no TLD, …). It is not meant to be 100% RFC-compliant.

    :param email: Email address to check.
    :type email: str
    :return: ``True`` if the email matches ``EMAIL_RE``, otherwise ``False``.
    :rtype: bool
    """
    return bool(EMAIL_RE.match(email))


def is_valid_age(age: int | str) -> bool:
    """Return ``True`` if ``age`` can be parsed as a non-negative integer.

    :param age: Age value or string representation (e.g., ``18`` or ``"18"``).
    :type age: int | str
    :return: ``True`` for ``age >= 0``, otherwise ``False`` (including parse errors).
    :rtype: bool
    """
    try:
        return int(age) >= 0
    except Exception:
        return False


@dataclass
class Person:
    """Base class for people in the system.

    :param name: Person's full name.
    :type name: str
    :param age: Person's age (non-negative integer).
    :type age: int
    :param _email: Contact email (stored "private" by convention).
    :type _email: str
    """
    name: str
    age: int
    _email: str

    def introduce(self) -> str:
        """Return a short self-introduction string.

        :return: A sentence like ``"Hi, I'm Alice, 20 years old."``.
        :rtype: str
        """
        return f"Hi, I'm {self.name}, {self.age} years old."


@dataclass
class Course:
    """A course offering with an optional instructor and enrolled students.

    :param course_id: Unique identifier for the course (e.g., ``CS101``).
    :type course_id: str
    :param course_name: Human-readable course name (e.g., ``Intro to CS``).
    :type course_name: str
    :param instructor: The assigned instructor, if any.
    :type instructor: Instructor | None
    :param enrolled_students: Students currently enrolled in the course.
    :type enrolled_students: list[Student]
    """
    course_id: str
    course_name: str
    instructor: Optional["Instructor"] = None
    enrolled_students: List["Student"] = field(default_factory=list)

    def add_student(self, student: "Student") -> None:
        """Enroll a student in this course (idempotent).

        If the student is already enrolled, nothing happens.

        :param student: The student to enroll.
        :type student: Student
        :return: None
        :rtype: None
        """
        if student not in self.enrolled_students:
            self.enrolled_students.append(student)


@dataclass
class Student(Person):
    """A student with an ID and a list of registered courses.

    :param student_id: Unique student identifier.
    :type student_id: str
    :param registered_courses: Courses the student is registered in.
    :type registered_courses: list[Course]
    """
    student_id: str
    registered_courses: List[Course] = field(default_factory=list)

    def register_course(self, course: Course) -> None:
        """Register the student in a course and keep both sides in sync.

        Adds the course to ``registered_courses`` and, if needed, calls
        ``course.add_student(self)``.

        :param course: Course to register for.
        :type course: Course
        :return: None
        :rtype: None
        """
        if course not in self.registered_courses:
            self.registered_courses.append(course)
            course.add_student(self)


@dataclass
class Instructor(Person):
    """An instructor with an ID and assigned courses.

    :param instructor_id: Unique instructor identifier.
    :type instructor_id: str
    :param assigned_courses: Courses this instructor teaches.
    :type assigned_courses: list[Course]
    """
    instructor_id: str
    assigned_courses: List[Course] = field(default_factory=list)

    def assign_course(self, course: Course) -> None:
        """Assign the instructor to a course and keep both sides in sync.

        Adds the course to ``assigned_courses`` and sets ``course.instructor``.

        :param course: Course to assign.
        :type course: Course
        :return: None
        :rtype: None
        """
        if course not in self.assigned_courses:
            self.assigned_courses.append(course)
            course.instructor = self


def to_json(
    students: List[Student],
    instructors: List[Instructor],
    courses: List[Course],
    path: str,
) -> None:
    """Serialize the current in-memory model to a JSON file.

    Students and instructors are stored with their basic fields. Course
    relationships are flattened to IDs to avoid recursion:

    * Each student stores a list of **course IDs** (``registered_courses``).
    * Each instructor stores a list of **course IDs** (``assigned_courses``).
    * Each course stores its ``instructor_id`` (or ``null``) and a list of
      enrolled **student IDs**.

    :param students: All students to include in the export.
    :type students: list[Student]
    :param instructors: All instructors to include in the export.
    :type instructors: list[Instructor]
    :param courses: All courses to include in the export.
    :type courses: list[Course]
    :param path: Destination JSON file path.
    :type path: str
    :return: None
    :rtype: None
    """

    def person_dump(p: Person) -> Dict[str, Any]:
        """Convert a ``Person`` (or subclass) to a serializable dictionary.

        For students/instructors, course relationships are converted to ID lists.

        :param p: Person instance to dump.
        :type p: Person
        :return: A JSON-serializable dict.
        :rtype: dict[str, Any]
        """
        d = asdict(p)
        if isinstance(p, Student):
            d["registered_courses"] = [c.course_id for c in p.registered_courses]
        if isinstance(p, Instructor):
            d["assigned_courses"] = [c.course_id for c in p.assigned_courses]
        return d

    payload = {
        "students": [person_dump(s) for s in students],
        "instructors": [person_dump(i) for i in instructors],
        "courses": [
            {
                "course_id": c.course_id,
                "course_name": c.course_name,
                "instructor_id": c.instructor.instructor_id if c.instructor else None,
                "enrolled_student_ids": [s.student_id for s in c.enrolled_students],
            }
            for c in courses
        ],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def from_json(path: str) -> Dict[str, List]:
    """Load students, instructors, and courses from a JSON export.

    This reconstructs objects and their relationships:

    * Instructors are created first and mapped by ``instructor_id``.
    * Students are created and mapped by ``student_id``.
    * Courses are created, then linked to their instructor and enrolled students.
    * Student ``registered_courses`` is synchronized from both directions
      (student→course and course→student).

    :param path: Path to a JSON file previously created by :func:`to_json`.
    :type path: str
    :return: A dict with keys ``'students'``, ``'instructors'``, ``'courses'``.
    :rtype: dict[str, list]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    instructors = [Instructor(**i) for i in data.get("instructors", [])]
    inst_map = {
        i["instructor_id"]: next(
            (x for x in instructors if x.instructor_id == i["instructor_id"])
        )
        for i in data.get("instructors", [])
    }

    students = [Student(**s) for s in data.get("students", [])]
    stud_map = {
        s["student_id"]: next(
            (x for x in students if x.student_id == s["student_id"])
        )
        for s in data.get("students", [])
    }

    courses: List[Course] = []
    for c in data.get("courses", []):
        course = Course(course_id=c["course_id"], course_name=c["course_name"])

        if c.get("instructor_id"):
            course.instructor = inst_map.get(c["instructor_id"])
            if course.instructor and course not in course.instructor.assigned_courses:
                course.instructor.assigned_courses.append(course)

        for sid in c.get("enrolled_student_ids", []):
            if sid in stud_map:
                course.add_student(stud_map[sid])
                stud_map[sid].register_course(course)

        courses.append(course)

    # Ensure student.registered_courses is fully resolved even if only IDs were stored
    for s in students:
        for cid in [
            cid for cid in getattr(s, "registered_courses", []) if isinstance(cid, str)
        ]:
            found = next((c for c in courses if c.course_id == cid), None)
            if found and found not in s.registered_courses:
                s.register_course(found)

    return {"students": students, "instructors": instructors, "courses": courses}


def export_csv(
    students: List[Student],
    instructors: List[Instructor],
    courses: List[Course],
    folder: str,
) -> None:
    """Export students, instructors, and courses to CSV and pretty text files.

    This creates three CSV files inside ``folder``:

    * ``students.csv``  basic student info and a ``;``-separated list of course IDs.
    * ``instructors.csv``  instructor info and assigned course IDs.
    * ``courses.csv``  course details, instructor ID (or ``-``), and enrolled student IDs.

    It also writes plain-text tables into ``folder/pretty_tables`` using
    :func:`write_pretty_table` for quick inspection in a terminal.

    :param students: Students to export.
    :type students: list[Student]
    :param instructors: Instructors to export.
    :type instructors: list[Instructor]
    :param courses: Courses to export.
    :type courses: list[Course]
    :param folder: Destination directory (created if it does not exist).
    :type folder: str
    :return: None
    :rtype: None
    """
    import os, csv

    os.makedirs(folder, exist_ok=True)

    # students.csv
    rows_s: List[List[Any]] = []
    for s in students:
        courses_str = ";".join(c.course_id for c in s.registered_courses) or "-"
        rows_s.append([s.student_id, s.name, s.age, s._email, courses_str])
    with open(os.path.join(folder, "students.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "name", "age", "email", "courses"])
        w.writerows(rows_s)

    # instructors.csv
    rows_i = [
        [i.instructor_id, i.name, i.age, i._email, ";".join(c.course_id for c in i.assigned_courses) or "-"]
        for i in instructors
    ]
    with open(os.path.join(folder, "instructors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["instructor_id", "name", "age", "email", "assigned_courses"])
        w.writerows(rows_i)

    # courses.csv
    rows_c: List[List[Any]] = []
    for c in courses:
        iid = c.instructor.instructor_id if c.instructor else "-"
        students_str = ";".join(s.student_id for s in c.enrolled_students) or "-"
        rows_c.append([c.course_id, c.course_name, iid, students_str])
    with open(os.path.join(folder, "courses.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["course_id", "course_name", "instructor_id", "enrolled_student_ids"])
        w.writerows(rows_c)

    # Pretty text tables for quick viewing
    pretty_dir = os.path.join(folder, "pretty_tables")
    write_pretty_table(
        ["student_id", "name", "age", "email", "courses"],
        rows_s,
        os.path.join(pretty_dir, "students_pretty.txt"),
    )
    write_pretty_table(
        ["instructor_id", "name", "age", "email", "assigned_courses"],
        rows_i,
        os.path.join(pretty_dir, "instructors_pretty.txt"),
    )
    write_pretty_table(
        ["course_id", "course_name", "instructor_id", "enrolled_student_ids"],
        rows_c,
        os.path.join(pretty_dir, "courses_pretty.txt"),
    )
