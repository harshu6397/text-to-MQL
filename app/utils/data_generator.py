import random
from datetime import datetime
from faker import Faker
from app.core.database import db_manager
from app.utils.logger import logger
fake = Faker()


class DataGenerator:
    def __init__(self):
        self.departments_data = []
        self.teachers_data = []
        self.courses_data = []
        self.students_data = []
        self.enrollments_data = []

    def generate_departments(self, count: int = 5):
        """Generate department data"""
        dept_names = [
            "Computer Science", "Mathematics", "Physics", "Chemistry", 
            "Biology", "English Literature", "History", "Economics"
        ]
        
        for i in range(min(count, len(dept_names))):
            dept_name = dept_names[i]
            dept_data = {
                "dept_id": f"DEPT_{i+1:03d}",
                "name": dept_name,
                "description": f"Department of {dept_name} offering undergraduate and graduate programs",
                "head_of_dept": fake.name(),
                "established_year": random.randint(1950, 2020)
            }
            self.departments_data.append(dept_data)

    def generate_teachers(self, count: int = 20):
        """Generate teacher data"""
        specializations = [
            "Machine Learning", "Data Structures", "Algorithms", "Database Systems",
            "Calculus", "Linear Algebra", "Statistics", "Quantum Physics",
            "Organic Chemistry", "Molecular Biology", "Creative Writing", "World History"
        ]
        
        for i in range(count):
            dept = random.choice(self.departments_data)
            hire_date = fake.date_between(start_date='-10y', end_date='today')
            teacher_data = {
                "teacher_id": f"TCH_{i+1:03d}",
                "name": fake.name(),
                "email": fake.email(),
                "department_id": dept["dept_id"],
                "hire_date": datetime.combine(hire_date, datetime.min.time()),
                "salary": random.randint(50000, 120000),
                "specialization": random.choice(specializations)
            }
            self.teachers_data.append(teacher_data)

    def generate_courses(self, count: int = 30):
        """Generate course data"""
        course_templates = [
            ("Introduction to Programming", "CS101"),
            ("Data Structures", "CS201"), 
            ("Database Systems", "CS301"),
            ("Machine Learning", "CS401"),
            ("Calculus I", "MATH101"),
            ("Linear Algebra", "MATH201"),
            ("Statistics", "MATH301"),
            ("Physics I", "PHYS101"),
            ("Quantum Mechanics", "PHYS301"),
            ("Organic Chemistry", "CHEM201"),
            ("World History", "HIST101"),
            ("Economics Principles", "ECON101")
        ]
        
        semesters = ["Fall", "Spring", "Summer"]
        years = [2023, 2024, 2025]
        
        for i in range(count):
            course_name, course_code = random.choice(course_templates)
            teacher = random.choice(self.teachers_data)
            
            course_data = {
                "course_id": f"CRS_{i+1:03d}",
                "course_name": course_name,
                "course_code": f"{course_code}_{random.randint(1,9)}",
                "department_id": teacher["department_id"],
                "teacher_id": teacher["teacher_id"],
                "credits": random.choice([3, 4, 6]),
                "semester": random.choice(semesters),
                "year": random.choice(years),
                "description": f"Comprehensive course covering {course_name.lower()} concepts and applications"
            }
            self.courses_data.append(course_data)

    def generate_students(self, count: int = 100):
        """Generate student data"""
        for i in range(count):
            dept = random.choice(self.departments_data)
            enrollment_date = fake.date_between(start_date='-4y', end_date='today')
            
            student_data = {
                "student_id": f"STU_{i+1:03d}",
                "name": fake.name(),
                "email": fake.email(),
                "age": random.randint(18, 28),
                "department_id": dept["dept_id"],
                "enrollment_date": datetime.combine(enrollment_date, datetime.min.time()),
                "gpa": round(random.uniform(2.0, 4.0), 2),
                "year_level": random.randint(1, 4)
            }
            self.students_data.append(student_data)

    def generate_enrollments(self, count: int = 300):
        """Generate enrollment data"""
        grades = ["A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F"]
        
        for i in range(count):
            student = random.choice(self.students_data)
            course = random.choice(self.courses_data)
            enroll_date = fake.date_between(start_date='-2y', end_date='today')
            
            enrollment_data = {
                "enrollment_id": f"ENR_{i+1:03d}",
                "student_id": student["student_id"],
                "course_id": course["course_id"],
                "semester": course["semester"],
                "year": course["year"],
                "grade": random.choice(grades) if random.random() > 0.3 else None,
                "enrollment_date": datetime.combine(enroll_date, datetime.min.time()),
                "completed": random.choice([True, False])
            }
            self.enrollments_data.append(enrollment_data)

    async def insert_data_to_db(self):
        """Insert all generated data to MongoDB"""
        try:
            # Insert departments
            if self.departments_data:
                await db_manager.get_collection("departments").insert_many(self.departments_data)
                logger.info(f"Inserted {len(self.departments_data)} departments")

            # Insert teachers
            if self.teachers_data:
                await db_manager.get_collection("teachers").insert_many(self.teachers_data)
                logger.info(f"Inserted {len(self.teachers_data)} teachers")

            # Insert courses
            if self.courses_data:
                await db_manager.get_collection("courses").insert_many(self.courses_data)
                logger.info(f"Inserted {len(self.courses_data)} courses")

            # Insert students
            if self.students_data:
                await db_manager.get_collection("students").insert_many(self.students_data)
                logger.info(f"Inserted {len(self.students_data)} students")

            # Insert enrollments
            if self.enrollments_data:
                await db_manager.get_collection("enrollments").insert_many(self.enrollments_data)
                logger.info(f"Inserted {len(self.enrollments_data)} enrollments")

        except Exception as e:
            logger.error(f"Error inserting data: {e}")
            raise

    async def generate_all_data(self):
        """Generate all sample data"""
        logger.info("Starting data generation...")
        
        self.generate_departments(5)
        self.generate_teachers(20)
        self.generate_courses(30)
        self.generate_students(100)
        self.generate_enrollments(300)
        
        await self.insert_data_to_db()
        logger.info("Sample data generation completed!")

    async def clear_all_data(self):
        """Clear all data from collections"""
        try:
            collections = ["departments", "teachers", "courses", "students", "enrollments"]
            for collection_name in collections:
                await db_manager.get_collection(collection_name).delete_many({})
                logger.info(f"Cleared {collection_name} collection")
        except Exception as e:
            logger.error(f"Error clearing data: {e}")
