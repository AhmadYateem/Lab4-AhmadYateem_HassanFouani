import tkinter as tk
from tkinter import ttk
import json
import os
from classes import Student, Instructor, Course

main_window = tk.Tk()
main_window.title("School Management System")

student_records = []
instructor_list = []
course_catalog = []

def populate_dropdown_widget(dropdown, items, attribute_name):
    """Populates a dropdown widget with items from a collection based on a specific attribute.
    
    :param dropdown: The dropdown widget to be populated
    :type dropdown: ttk.Combobox
    :param items: Collection of objects to extract values from
    :type items: list
    :param attribute_name: Name of the attribute to extract from each item
    :type attribute_name: str
    """
    options = []
    for item in items:
        options.append(getattr(item, attribute_name))
    dropdown['values'] = options

def find_person_by_name(collection, target_name):
    """Searches for a person in a collection by their name.
    
    :param collection: List of person objects to search through
    :type collection: list
    :param target_name: The name to search for
    :type target_name: str
    :return: The person object if found, None otherwise
    :rtype: object or None
    """
    for person in collection:
        if person.name == target_name:
            return person
    return None

def generate_default_id(prefix, collection_size):
    """Generates a default ID with a given prefix and collection size.
    
    :param prefix: The prefix to use for the ID
    :type prefix: str
    :param collection_size: The current size of the collection
    :type collection_size: int
    :return: A formatted ID string
    :rtype: str
    """
    return f"{prefix}{collection_size + 100}"

student_input_frame = tk.Frame(main_window)
student_input_frame.pack(pady=5)
tk.Label(student_input_frame, text="Add Student").grid(row=0, column=0)
student_name_field = tk.Entry(student_input_frame)
student_name_field.grid(row=0, column=1)
student_age_input = tk.Entry(student_input_frame)
student_age_input.grid(row=0, column=2)
student_email_entry = tk.Entry(student_input_frame)
student_email_entry.grid(row=0, column=3)
student_id_field = tk.Entry(student_input_frame)
student_id_field.grid(row=0, column=4)

def add_student():
    """Adds a new student to the system with input validation and default values.
    
    Creates a Student object from the input fields, applying default values
    when fields are empty or invalid. Updates the dropdown lists and refreshes
    the data table after adding the student.
    """
    name = student_name_field.get() or "John Doe"
    age_text = student_age_input.get()
    if age_text and age_text.isdigit():
        age = int(age_text)
    else:
        age = 22
    email = student_email_entry.get() or "student@university.edu"
    sid = student_id_field.get() or generate_default_id("STU", len(student_records))
    
    student = Student(name, age, email, sid)
    student_records.append(student)
    update_dropdown_lists()
    refresh_data_table()

tk.Button(student_input_frame, text="Add Student", command=add_student).grid(row=0, column=5)

instructor_input_frame = tk.Frame(main_window)
instructor_input_frame.pack(pady=5)
tk.Label(instructor_input_frame, text="Add Instructor").grid(row=0, column=0)
instructor_name_field = tk.Entry(instructor_input_frame)
instructor_name_field.grid(row=0, column=1)
instructor_age_input = tk.Entry(instructor_input_frame)  
instructor_age_input.grid(row=0, column=2)
instructor_email_entry = tk.Entry(instructor_input_frame)
instructor_email_entry.grid(row=0, column=3)
instructor_id_field = tk.Entry(instructor_input_frame)
instructor_id_field.grid(row=0, column=4)

def add_instructor():
    """Adds a new instructor to the system with input validation and default values.
    
    Creates an Instructor object from the input fields, applying default values
    when fields are empty or invalid. Updates the dropdown lists and refreshes
    the data table after adding the instructor.
    """
    name = instructor_name_field.get() or "Dr. Smith"
    age_text = instructor_age_input.get()
    if age_text and age_text.isdigit():
        age = int(age_text)
    else:
        age = 35
    email = instructor_email_entry.get() or "professor@university.edu"
    iid = instructor_id_field.get() or generate_default_id("PROF", len(instructor_list))
    
    instructor = Instructor(name, age, email, iid)
    instructor_list.append(instructor)
    update_dropdown_lists()
    refresh_data_table()

tk.Button(instructor_input_frame, text="Add Instructor", command=add_instructor).grid(row=0, column=5)

course_input_frame = tk.Frame(main_window)
course_input_frame.pack(pady=5)
tk.Label(course_input_frame, text="Add Course").grid(row=0, column=0)
course_id_input = tk.Entry(course_input_frame)
course_id_input.grid(row=0, column=1)
course_name_input = tk.Entry(course_input_frame)
course_name_input.grid(row=0, column=2)

instructor_selection = tk.StringVar()
instructor_dropdown_widget = ttk.Combobox(course_input_frame, textvariable=instructor_selection)
instructor_dropdown_widget.grid(row=0, column=3)

def add_new_course():
    """Adds a new course to the system and assigns an instructor if selected.
    
    Creates a Course object from the input fields with default values when empty.
    If an instructor is selected from the dropdown, assigns the course to that
    instructor. Updates dropdown lists and refreshes the data table.
    """
    cid = course_id_input.get() or generate_default_id("COURSE", len(course_catalog))
    cname = course_name_input.get() or "Introduction to Computing"
    
    selected_instructor = find_person_by_name(instructor_list, instructor_selection.get())
    
    course = Course(cid, cname, selected_instructor)
    course_catalog.append(course)
    if selected_instructor:
        selected_instructor.assign_course(course)
    update_dropdown_lists()
    refresh_data_table()

tk.Button(course_input_frame, text="Add Course", command=add_new_course).grid(row=0, column=4)

registration_frame = tk.Frame(main_window)
registration_frame.pack(pady=5)
tk.Label(registration_frame, text="Student Registration").grid(row=0, column=0)

student_selection = tk.StringVar()
student_dropdown_widget = ttk.Combobox(registration_frame, textvariable=student_selection)
student_dropdown_widget.grid(row=0, column=1)

course_selection = tk.StringVar()
course_dropdown_widget = ttk.Combobox(registration_frame, textvariable=course_selection)
course_dropdown_widget.grid(row=0, column=2)

def register_student_for_course():
    """Registers a selected student for a selected course.
    
    Finds the selected student and course from the dropdown selections,
    then creates a bidirectional relationship by registering the student
    for the course and adding the student to the course enrollment.
    Refreshes the data table to show updated information.
    """
    selected_student = find_person_by_name(student_records, student_selection.get())
    selected_course = None
    for c in course_catalog:
        if c.course_name == course_selection.get():
            selected_course = c
            break
    
    if selected_student and selected_course:
        selected_student.register_course(selected_course)
        selected_course.add_student(selected_student)
        refresh_data_table()

tk.Button(registration_frame, text="Register Student", command=register_student_for_course).grid(row=0, column=3)

assignment_frame = tk.Frame(main_window)
assignment_frame.pack(pady=5)
tk.Label(assignment_frame, text="Instructor Assignment").grid(row=0, column=0)

assign_instructor_selection = tk.StringVar()
instructor_assignment_dropdown = ttk.Combobox(assignment_frame, textvariable=assign_instructor_selection)
instructor_assignment_dropdown.grid(row=0, column=1)

assign_course_selection = tk.StringVar()
course_assignment_dropdown = ttk.Combobox(assignment_frame, textvariable=assign_course_selection)
course_assignment_dropdown.grid(row=0, column=2)

def assign_instructor_to_course():
    """Assigns a selected instructor to a selected course.
    
    Creates a bidirectional relationship between the instructor and course
    by assigning the course to the instructor and setting the instructor
    as the course's instructor. Refreshes the data table to reflect changes.
    """
    selected_instructor = find_person_by_name(instructor_list, assign_instructor_selection.get())
    selected_course = None
    for c in course_catalog:
        if c.course_name == assign_course_selection.get():
            selected_course = c
            break
    
    if selected_instructor and selected_course:
        selected_instructor.assign_course(selected_course)
        selected_course.instructor = selected_instructor
        refresh_data_table()

tk.Button(assignment_frame, text="Assign Instructor", command=assign_instructor_to_course).grid(row=0, column=3)

data_display_tree = ttk.Treeview(main_window)
data_display_tree["columns"] = ("Type", "Name", "Age", "Email", "ID", "Courses")
data_display_tree.column("#0", width=0, stretch=tk.NO)
data_display_tree.heading("Type", text="Type")
data_display_tree.heading("Name", text="Name") 
data_display_tree.heading("Age", text="Age")
data_display_tree.heading("Email", text="Email")
data_display_tree.heading("ID", text="ID")
data_display_tree.heading("Courses", text="Courses")
data_display_tree.pack(pady=10)

search_controls_frame = tk.Frame(main_window)
search_controls_frame.pack(pady=5)
tk.Label(search_controls_frame, text="Search Records:").grid(row=0, column=0)
search_input_field = tk.Entry(search_controls_frame)
search_input_field.grid(row=0, column=1)

search_criteria_var = tk.StringVar(value="Name")
search_type_selector = ttk.Combobox(search_controls_frame, textvariable=search_criteria_var, values=["Name", "ID", "Course"])
search_type_selector.grid(row=0, column=2)

def perform_search():
    """Performs a search operation based on the selected criteria and search query.
    
    Searches through students, instructors, and courses based on the selected
    search type (Name, ID, or Course). Clears the current table display and
    shows only matching results. If no query is provided, refreshes the entire
    table to show all records.
    """
    query = search_input_field.get().lower()
    search_type = search_criteria_var.get()
    
    for item in data_display_tree.get_children():
        data_display_tree.delete(item)
    
    if not query:
        refresh_data_table()
        return
        
    if search_type == "Name":
        for student in student_records:
            if query in student.name.lower():
                cs = ""
                for c in student.registered_courses:
                    if cs:
                        cs = cs + "," + c.course_name
                    else:
                        cs = c.course_name
                data_display_tree.insert("", "end", values=("Student", student.name, student.age, student._email, student.student_id, cs))
        for instructor in instructor_list:
            if query in instructor.name.lower():
                s = ""
                for c in instructor.assigned_courses:
                    if s:
                        s = s + "," + c.course_name
                    else:
                        s = c.course_name
                data_display_tree.insert("", "end", values=("Instructor", instructor.name, instructor.age, instructor._email, instructor.instructor_id, s))
        for course in course_catalog:
            if query in course.course_name.lower():
                iname = ""
                if course.instructor:
                    iname = course.instructor.name
                data_display_tree.insert("", "end", values=("Course", course.course_name, "", "", course.course_id, iname))
    elif search_type == "ID":
        for student in student_records:
            if query in student.student_id.lower():
                s = ""
                for c in student.registered_courses:
                    if s:
                        s = s + "," + c.course_name
                    else:
                        s = c.course_name
                data_display_tree.insert("", "end", values=("Student", student.name, student.age, student._email, student.student_id, s))
        for instructor in instructor_list:
            if query in instructor.instructor_id.lower():
                cs = ""
                for c in instructor.assigned_courses:
                    if cs:
                        cs += "," + c.course_name
                    else:
                        cs = c.course_name
                data_display_tree.insert("", "end", values=("Instructor", instructor.name, instructor.age, instructor._email, instructor.instructor_id, cs))
        for course in course_catalog:
            if query in course.course_id.lower():
                iname = ""
                if course.instructor:
                    iname = course.instructor.name
                data_display_tree.insert("", "end", values=("Course", course.course_name, "", "", course.course_id, iname))

tk.Button(search_controls_frame, text="Search", command=perform_search).grid(row=0, column=3)

def clear_search():
    """Clears the search input field and refreshes the data table.
    
    Removes any text from the search input field and displays all records
    in the data table by calling the refresh function.
    """
    search_input_field.delete(0, tk.END)
    refresh_data_table()

tk.Button(search_controls_frame, text="Clear", command=clear_search).grid(row=0, column=4)

action_buttons_frame = tk.Frame(main_window)
action_buttons_frame.pack(pady=5)

def edit_selected_record():
    """Edits the selected record in the data table using current input field values.
    
    Retrieves the selected item from the data table and updates its properties
    based on the corresponding input fields. Supports editing students and
    instructors by updating their name, age, and email if new values are provided.
    Refreshes the data table to show updated information.
    """
    selected = data_display_tree.selection()
    if not selected:
        return
    
    item = data_display_tree.item(selected[0])
    values = item['values']
    record_type = values[0]
    record_id = values[4]
    
    if record_type == "Student":
        for student in student_records:
            if student.student_id == record_id:
                new_name = student_name_field.get()
                if new_name:
                    student.name = new_name
                age_text = student_age_input.get()
                if age_text and age_text.isdigit():
                    student.age = int(age_text)
                new_email = student_email_entry.get()
                if new_email:
                    student._email = new_email
                break
    elif record_type == "Instructor":
        for instructor in instructor_list:
            if instructor.instructor_id == record_id:
                new_name = instructor_name_field.get()
                if new_name:
                    instructor.name = new_name
                age_text = instructor_age_input.get()
                if age_text and age_text.isdigit():
                    instructor.age = int(age_text)
                new_email = instructor_email_entry.get()
                if new_email:
                    instructor._email = new_email
                break
    refresh_data_table()

def delete_selected_record():
    """Deletes the selected record from the system and updates all related data.
    
    Removes the selected record (student, instructor, or course) from the system
    and cleans up all related associations. For students, removes them from course
    enrollments. For instructors, removes course assignments. For courses, removes
    them from student registrations and instructor assignments.
    
    :raises: None, but silently handles cases where no record is selected
    """
    selected = data_display_tree.selection()
    if not selected:
        return
        
    item = data_display_tree.item(selected[0])
    values = item['values']
    record_type = values[0]
    record_id = values[4]
    
    if record_type == "Student":
        new_students = []
        for s in student_records:
            if s.student_id != record_id:
                new_students.append(s)
        student_records.clear()
        for s in new_students:
            student_records.append(s)
        for course in course_catalog:
            filtered = []
            for s in course.enrolled_students:
                if s.student_id != record_id:
                    filtered.append(s)
            course.enrolled_students = filtered
    elif record_type == "Instructor":
        new_instructors = []
        for i in instructor_list:
            if i.instructor_id != record_id:
                new_instructors.append(i)
        instructor_list.clear()
        for i in new_instructors:
            instructor_list.append(i)
        for course in course_catalog:
            if course.instructor and course.instructor.instructor_id == record_id:
                course.instructor = None
    elif record_type == "Course":
        new_courses = []
        for c in course_catalog:
            if c.course_id != record_id:
                new_courses.append(c)
        course_catalog.clear()
        for c in new_courses:
            course_catalog.append(c)
        for student in student_records:
            kept = []
            for c in student.registered_courses:
                if c.course_id != record_id:
                    kept.append(c)
            student.registered_courses = kept
        for instructor in instructor_list:
            kept2 = []
            for c in instructor.assigned_courses:
                if c.course_id != record_id:
                    kept2.append(c)
            instructor.assigned_courses = kept2
    
    update_dropdown_lists()
    refresh_data_table()

def save_all_data():
    """Saves all system data to JSON files for persistence.
    
    Exports students, instructors, and courses to separate JSON files.
    Student and instructor data includes all their properties, while
    course data includes basic information and instructor associations.
    Creates three files: student_records.json, instructor_data.json,
    and course_catalog.json in the current directory.
    """
    student_data = []
    for s in student_records:
        student_data.append(s.to_dict())
    instructor_data = []
    for i in instructor_list:
        instructor_data.append(i.to_dict())
    course_data = []
    for course in course_catalog:
        course_dict = {"course_id": course.course_id, "course_name": course.course_name}
        if course.instructor:
            course_dict["instructor_id"] = course.instructor.instructor_id
        course_data.append(course_dict)
    
    base_dir = os.path.dirname(__file__)
    with open(os.path.join(base_dir, "student_records.json"), "w") as f:
        json.dump(student_data, f)
    with open(os.path.join(base_dir, "instructor_data.json"), "w") as f:
        json.dump(instructor_data, f)
    with open(os.path.join(base_dir, "course_catalog.json"), "w") as f:
        json.dump(course_data, f)
    DATA = {"students": {}, "instructors": {}, "courses": {}}
    for s in student_records:
        DATA["students"][s.student_id] = {"name": s.name, "age": s.age, "email": s._email, "courses": [c.course_id for c in s.registered_courses]}
    for i in instructor_list:
        DATA["instructors"][i.instructor_id] = {"name": i.name, "age": i.age, "email": i._email, "courses": [c.course_id for c in i.assigned_courses]}
    for c in course_catalog:
        DATA["courses"][c.course_id] = {"name": c.course_name, "instructor_id": (c.instructor.instructor_id if c.instructor else None), "students": [s.student_id for s in c.enrolled_students]}
    with open(os.path.join(base_dir, "data2.json"), "w") as f:
        json.dump(DATA, f)
    with open(os.path.join(base_dir, "data3.json"), "w") as f:
        json.dump(DATA, f)

def load_all_data():
    """Loads all system data from JSON files and reconstructs object relationships.
    
    Reads data from student_records.json, instructor_data.json, and course_catalog.json
    files if they exist. Reconstructs all objects and their relationships including
    course assignments, student registrations, and instructor-course associations.
    Updates dropdown lists and refreshes the data table after loading.
    
    :raises FileNotFoundError: Silently handled if JSON files don't exist
    """
    global student_records, instructor_list, course_catalog
    base_dir = os.path.dirname(__file__)
    candidates = [os.path.join(base_dir, "data2.json"), os.path.join(base_dir, "data3.json"), "data2.json", "data3.json"]
    path = None
    for p in candidates:
        if os.path.exists(p):
            path = p
            break
    if path:
        with open(path, "r") as f:
            DATA = json.load(f)
        instructor_list.clear()
        for iid, d in DATA.get("instructors", {}).items():
            instructor_list.append(Instructor(d["name"], d["age"], d["email"], iid))
        course_catalog.clear()
        inst_lookup = {i.instructor_id: i for i in instructor_list}
        for cid, d in DATA.get("courses", {}).items():
            inst = inst_lookup.get(d.get("instructor_id")) if d.get("instructor_id") else None
            cobj = Course(cid, d["name"], inst)
            course_catalog.append(cobj)
            if inst:
                inst.assign_course(cobj)
        student_records.clear()
        course_lookup = {c.course_id: c for c in course_catalog}
        for sid, d in DATA.get("students", {}).items():
            s = Student(d["name"], d["age"], d["email"], sid)
            for cid in d.get("courses", []):
                if cid in course_lookup:
                    s.register_course(course_lookup[cid])
                    course_lookup[cid].add_student(s)
            student_records.append(s)
        update_dropdown_lists()
        refresh_data_table()
        return
    def rpath(name):
        p = os.path.join(base_dir, name)
        return p if os.path.exists(p) else name
    if os.path.exists(rpath("instructor_data.json")):
        with open(rpath("instructor_data.json"), "r") as f:
            instructor_data = json.load(f)
        instructor_list.clear()
        for data in instructor_data:
            instructor = Instructor(data["name"], data["age"], data["email"], data["instructor_id"])
            instructor_list.append(instructor)
    if os.path.exists(rpath("course_catalog.json")):
        with open(rpath("course_catalog.json"), "r") as f:
            course_data = json.load(f)
        course_catalog.clear()
        for data in course_data:
            instructor = None
            for inst in instructor_list:
                if inst.instructor_id == data.get("instructor_id", ""):
                    instructor = inst
                    break
            course = Course(data["course_id"], data["course_name"], instructor)
            course_catalog.append(course)
            if instructor:
                instructor.assign_course(course)
    if os.path.exists(rpath("student_records.json")):
        with open(rpath("student_records.json"), "r") as f:
            student_data = json.load(f)
        student_records.clear()
        course_lookup = {}
        for c in course_catalog:
            course_lookup[c.course_id] = c
        for data in student_data:
            student = Student(data["name"], data["age"], data["email"], data["student_id"])
            rlist = data.get("registered_courses", [])
            for course_id in rlist:
                if course_id in course_lookup:
                    student.register_course(course_lookup[course_id])
                    course_lookup[course_id].add_student(student)
            student_records.append(student)
    
    update_dropdown_lists()
    refresh_data_table()

tk.Button(action_buttons_frame, text="Edit Record", command=edit_selected_record).grid(row=0, column=0, padx=5)
tk.Button(action_buttons_frame, text="Delete Record", command=delete_selected_record).grid(row=0, column=1, padx=5)
tk.Button(action_buttons_frame, text="Save Data", command=save_all_data).grid(row=0, column=2, padx=5)
tk.Button(action_buttons_frame, text="Load Data", command=load_all_data).grid(row=0, column=3, padx=5)

def update_dropdown_lists():
    """Updates all dropdown widgets with current data from the system.
    
    Refreshes the values in all combobox widgets to reflect the current
    state of students, instructors, and courses in the system. This ensures
    that dropdown selections remain synchronized with the available data
    after additions, deletions, or data loading operations.
    """
    populate_dropdown_widget(student_dropdown_widget, student_records, 'name')
    populate_dropdown_widget(course_dropdown_widget, course_catalog, 'course_name')
    populate_dropdown_widget(instructor_assignment_dropdown, instructor_list, 'name')
    populate_dropdown_widget(course_assignment_dropdown, course_catalog, 'course_name')
    populate_dropdown_widget(instructor_dropdown_widget, instructor_list, 'name')

def refresh_data_table():
    """Refreshes the main data table display with all current records.
    
    Clears the existing table contents and repopulates it with all students,
    instructors, and courses currently in the system. Formats the display
    to show relevant information including associated courses for students
    and instructors, and assigned instructors for courses.
    """
    for item in data_display_tree.get_children():
        data_display_tree.delete(item)
    
    for student in student_records:
        cs = ""
        for c in student.registered_courses:
            if cs:
                cs += "," + c.course_name
            else:
                cs = c.course_name
        data_display_tree.insert("", "end", values=("Student", student.name, student.age, student._email, student.student_id, cs))
    
    for instructor in instructor_list:
        s = ""
        for c in instructor.assigned_courses:
            if s:
                s = s + "," + c.course_name
            else:
                s = c.course_name
        data_display_tree.insert("", "end", values=("Instructor", instructor.name, instructor.age, instructor._email, instructor.instructor_id, s))
    
    for course in course_catalog:
        iname = ""
        if course.instructor:
            iname = course.instructor.name
        data_display_tree.insert("", "end", values=("Course", course.course_name, "", "", course.course_id, iname))

update_dropdown_lists()
refresh_data_table()

main_window.mainloop()