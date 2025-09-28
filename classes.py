import json

class Person:
    """Base class representing a person in the school management system.
    
    This class provides common attributes and functionality for all people
    in the system including students and instructors. It handles basic
    validation for name, age, and email format.
    
    :param name: Full name of the person
    :type name: str
    :param age: Age of the person in years
    :type age: int
    :param email: Email address of the person
    :type email: str
    :raises AssertionError: If name is not a string or is empty
    :raises AssertionError: If age is not an integer or is negative
    :raises AssertionError: If email is not a string or has invalid format
    """
    
    def __init__(self, name, age, email):
        """Constructor method for Person class.
        
        :param name: Full name of the person
        :type name: str
        :param age: Age of the person in years
        :type age: int
        :param email: Email address of the person
        :type email: str
        """
        assert type(name) == str, "Name must be a string"
        assert len(name)!=0, "Name cannot be left empty"
        assert type(age)== int, "Age must be an integer"
        assert(age>=0), "Age must be a positive value"
        assert type(email) == str, "Email must be a string"
        assert "@" in email and email[0] != "@", "Email must follow a valid format"
        self.name = name
        self.age = age
        self._email = email
    
    def to_dict(self):
        """Converts person object to dictionary format for serialization.
        
        :return: Dictionary containing person's basic information
        :rtype: dict
        """
        d = {"name": self.name, "age": self.age, "email": self._email}
        return d
    
    def from_dict(self,data):
        """Updates person object attributes from dictionary data.
        
        :param data: Dictionary containing person information
        :type data: dict
        """
        self.name = data["name"]
        self.age = data["age"]
        self._email = data["email"]

class Student(Person):
    """Represents a student in the school management system.
    
    Students can register for courses and maintain a list of their
    enrolled courses. Inherits basic person attributes from Person class.
    
    :param name: Full name of the student
    :type name: str
    :param age: Age of the student in years
    :type age: int
    :param email: Email address of the student
    :type email: str
    :param student_id: Unique identifier for the student
    :type student_id: str
    :param registered_courses: List of courses the student is registered for, defaults to None
    :type registered_courses: list, optional
    :raises AssertionError: If student_id is not a non-empty string
    """
    
    def __init__(self, name, age, email, student_id,registered_courses=None):
        """Constructor method for Student class.
        
        :param name: Full name of the student
        :type name: str
        :param age: Age of the student in years
        :type age: int
        :param email: Email address of the student
        :type email: str
        :param student_id: Unique identifier for the student
        :type student_id: str
        :param registered_courses: List of courses the student is registered for, defaults to None
        :type registered_courses: list, optional
        """
        assert (type(student_id)==str and len(student_id)!=0), "Student id must be a non empty string"
        super().__init__(name,age,email)
        self.student_id = student_id
        if registered_courses==None:
            self.registered_courses=[]
        else:
            self.registered_courses = registered_courses
    
    def register_course(self, course):
        """Registers the student for a specific course.
        
        Adds the course to the student's list of registered courses.
        The course must be a valid Course object.
        
        :param course: The course to register for
        :type course: Course
        :raises AssertionError: If course is not a valid Course object
        """
        assert type(course)==Course, "Course must be valid"
        self.registered_courses.append(course)
    
    def to_dict(self):
        """Converts student object to dictionary format for serialization.
        
        Creates a dictionary representation of the student including
        all registered course IDs for persistence purposes.
        
        :return: Dictionary containing student information and registered course IDs
        :rtype: dict
        """
        course_ids = []
        for course in self.registered_courses:
             course_ids.append(course.course_id)
        d = {"name" : self.name, "age" : self.age, "email": self._email, "student_id": self.student_id, "registered_courses": course_ids}
        return d
    
    def from_dict(self,data,courseDict = None):
        """Updates student object attributes from dictionary data with course reconstruction.
        
        Restores student information from dictionary and rebuilds course
        relationships using the provided course dictionary lookup.
        
        :param data: Dictionary containing student information
        :type data: dict
        :param courseDict: Dictionary mapping course IDs to Course objects, defaults to None
        :type courseDict: dict, optional
        """
        self.name = data["name"]
        self.age = data["age"]
        self._email = data["email"]
        self.student_id = data["student_id"]
        self.registered_courses = []
        if courseDict != None:
            for course_ID in data["registered_courses"]:
                 if course_ID in courseDict.keys():
                    self.registered_courses.append(courseDict[course_ID])

class Instructor(Person):
    """Represents an instructor in the school management system.
    
    Instructors can be assigned to teach multiple courses and maintain
    a list of their assigned courses. Inherits basic person attributes
    from Person class.
    
    :param name: Full name of the instructor
    :type name: str
    :param age: Age of the instructor in years
    :type age: int
    :param email: Email address of the instructor
    :type email: str
    :param instructor_id: Unique identifier for the instructor
    :type instructor_id: str
    :param assigned_courses: List of courses assigned to the instructor, defaults to None
    :type assigned_courses: list, optional
    :raises AssertionError: If instructor_id is not a non-empty string
    """
    
    def __init__(self, name, age, email, instructor_id,assigned_courses=None):
        """Constructor method for Instructor class.
        
        :param name: Full name of the instructor
        :type name: str
        :param age: Age of the instructor in years
        :type age: int
        :param email: Email address of the instructor
        :type email: str
        :param instructor_id: Unique identifier for the instructor
        :type instructor_id: str
        :param assigned_courses: List of courses assigned to the instructor, defaults to None
        :type assigned_courses: list, optional
        """
        assert type(instructor_id)==str and len(instructor_id)!=0, "Instructor id must be a non empty string"
        super().__init__(name,age,email)
        self.instructor_id = instructor_id
        if assigned_courses==None:
            self.assigned_courses=[]
        else:       
            self.assigned_courses = assigned_courses
    
    def assign_course(self,course):
        """Assigns a course to the instructor.
        
        Adds the course to the instructor's list of assigned courses.
        The course must be a valid Course object.
        
        :param course: The course to assign to the instructor
        :type course: Course
        :raises AssertionError: If course is not a valid Course object
        """
        assert type(course)==Course, "Course must be valid"
        self.assigned_courses.append(course)
    
    def to_dict(self):
        """Converts instructor object to dictionary format for serialization.
        
        Creates a dictionary representation of the instructor including
        all assigned course IDs for persistence purposes.
        
        :return: Dictionary containing instructor information and assigned course IDs
        :rtype: dict
        """
        course_ids = []
        for c in self.assigned_courses:
            course_ids.append(c.course_id)
        d = {"name": self.name, "age": self.age,"email": self._email, "instructor_id": self.instructor_id, "assigned_courses": course_ids}
        return d
    
    def from_dict(self,data,courseDict= None):
        """Updates instructor object attributes from dictionary data with course reconstruction.
        
        Restores instructor information from dictionary and rebuilds course
        relationships using the provided course dictionary lookup.
        
        :param data: Dictionary containing instructor information
        :type data: dict
        :param courseDict: Dictionary mapping course IDs to Course objects, defaults to None
        :type courseDict: dict, optional
        """
        self.name = data["name"]
        self.age = data["age"]
        self._email = data["email"]
        self.instructor_id = data["instructor_id"]
        self.assigned_courses = []
        if courseDict != None:
             for courseId in data["assigned_courses"]:
               if courseId in courseDict.keys():
                    self.assigned_courses.append(courseDict[courseId])

class Course:
    """Represents a course in the school management system.
    
    Courses can have an assigned instructor and maintain a list of
    enrolled students. Provides functionality for managing course
    enrollment and instructor assignments.
    
    :param course_id: Unique identifier for the course
    :type course_id: str
    :param course_name: Name or title of the course
    :type course_name: str
    :param instructor: Instructor assigned to teach the course
    :type instructor: Instructor or None
    :param enrolled_students: List of students enrolled in the course, defaults to None
    :type enrolled_students: list, optional
    :raises AssertionError: If course_id is not a non-empty string
    :raises AssertionError: If course_name is not a non-empty string
    :raises AssertionError: If instructor is provided but not an Instructor object
    """
    
    def __init__(self,course_id,course_name,instructor,enrolled_students=None):
        """Constructor method for Course class.
        
        :param course_id: Unique identifier for the course
        :type course_id: str
        :param course_name: Name or title of the course
        :type course_name: str
        :param instructor: Instructor assigned to teach the course
        :type instructor: Instructor or None
        :param enrolled_students: List of students enrolled in the course, defaults to None
        :type enrolled_students: list, optional
        """
        assert (type(course_id)== str and len(course_id)!=0), "Course id must be a non empty string"
        assert type(course_name) == str and len(course_name)!=0, "Course name must be a non empty string"
        if instructor is not None:
            assert type(instructor)==Instructor, "Instructor must actually be an instructor"
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        if enrolled_students==None:
            self.enrolled_students=[]
        else:
            self.enrolled_students= enrolled_students
    
    def add_student(self,student):
        """Adds a student to the course enrollment list.
        
        Enrolls the student in this course by adding them to the
        list of enrolled students. The student must be a valid Student object.
        
        :param student: The student to enroll in the course
        :type student: Student
        :raises AssertionError: If student is not a valid Student object
        """
        assert type(student)==Student, "Student must be a student"
        self.enrolled_students.append(student)
    
    def to_dict(self):
        """Converts course object to dictionary format for serialization.
        
        Creates a dictionary representation of the course with basic
        information for persistence purposes. Student and instructor
        relationships are handled separately.
        
        :return: Dictionary containing course ID and name
        :rtype: dict
        """
        d = {"course_id": self.course_id, "course_name": self.course_name}
        return d
    
    def from_dict(self,data):
        """Updates course object attributes from dictionary data.
        
        Restores basic course information from dictionary. Student
        and instructor relationships must be rebuilt separately.
        
        :param data: Dictionary containing course information
        :type data: dict
        """
        self.course_id = data["course_id"]
        self.course_name = data["course_name"]