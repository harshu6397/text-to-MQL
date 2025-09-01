from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class Grade(str, Enum):
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D = "D"
    F = "F"


class Department(BaseModel):
    dept_id: str = Field(..., description="Department ID")
    name: str = Field(..., description="Department name")
    description: str = Field(..., description="Department description")
    head_of_dept: Optional[str] = Field(None, description="Head of department name")
    established_year: int = Field(..., description="Year department was established")


class Teacher(BaseModel):
    teacher_id: str = Field(..., description="Teacher ID")
    name: str = Field(..., description="Teacher full name")
    email: str = Field(..., description="Teacher email")
    department_id: str = Field(..., description="Department ID the teacher belongs to")
    hire_date: datetime = Field(..., description="Date teacher was hired")
    salary: float = Field(..., description="Teacher salary")
    specialization: str = Field(..., description="Teacher's area of specialization")


class Course(BaseModel):
    course_id: str = Field(..., description="Course ID")
    course_name: str = Field(..., description="Course name")
    course_code: str = Field(..., description="Course code (e.g., CS101)")
    department_id: str = Field(..., description="Department ID offering the course")
    teacher_id: str = Field(..., description="Teacher ID teaching the course")
    credits: int = Field(..., description="Number of credits")
    semester: str = Field(..., description="Semester (Fall/Spring/Summer)")
    year: int = Field(..., description="Academic year")
    description: str = Field(..., description="Course description")


class Student(BaseModel):
    student_id: str = Field(..., description="Student ID")
    name: str = Field(..., description="Student full name")
    email: str = Field(..., description="Student email")
    age: int = Field(..., description="Student age")
    department_id: str = Field(..., description="Department ID student belongs to")
    enrollment_date: datetime = Field(..., description="Date student enrolled")
    gpa: float = Field(..., description="Student GPA")
    year_level: int = Field(..., description="Year level (1-4)")


class Enrollment(BaseModel):
    enrollment_id: str = Field(..., description="Enrollment ID")
    student_id: str = Field(..., description="Student ID")
    course_id: str = Field(..., description="Course ID")
    semester: str = Field(..., description="Semester")
    year: int = Field(..., description="Academic year")
    grade: Optional[Grade] = Field(None, description="Grade received")
    enrollment_date: datetime = Field(..., description="Date of enrollment")
    completed: bool = Field(False, description="Whether course is completed")


class QueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    max_results: Optional[int] = Field(100, description="Maximum number of results")


class QueryResponse(BaseModel):
    success: bool = Field(..., description="Whether query was successful")
    query: str = Field(..., description="Original query")
    generated_mql: Optional[str] = Field(None, description="Generated MongoDB query in MongoDB console format (ready to run in MongoDB shell)")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    formatted_answer: Optional[str] = Field(None, description="Natural language formatted answer")
    error: Optional[str] = Field(None, description="Error message if any")
    execution_time: float = Field(..., description="Query execution time in seconds")
    workflow_steps: Optional[List[Dict[str, str]]] = Field(None, description="Workflow step status for debugging")
    collections_found: Optional[int] = Field(None, description="Number of collections discovered")
    schema_retrieved: Optional[int] = Field(None, description="Number of schemas retrieved")
