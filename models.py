"""
Data models and dataclasses for Classroom Management System (CMS).
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Student:
    id: Optional[int] = None
    student_id: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    gender: Optional[str] = "Prefer not to say"
    date_of_birth: Optional[str] = None
    phone: Optional[str] = None
    enrollment_date: str = ""
    status: str = "Active"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class Course:
    id: Optional[int] = None
    course_code: str = ""
    course_name: str = ""
    instructor: str = ""
    credit_hours: int = 3
    semester: str = "Fall 2026"


@dataclass
class AttendanceRecord:
    id: Optional[int] = None
    student_id: int = 0
    course_id: int = 0
    attendance_date: str = ""
    status: str = "Present"  # Present, Absent, Late, Excused
    remarks: Optional[str] = None
    student_name: Optional[str] = None
    student_code: Optional[str] = None


@dataclass
class Assessment:
    id: Optional[int] = None
    course_id: int = 0
    title: str = ""
    assessment_type: str = "Assignment"  # Quiz, Assignment, Midterm, Final Exam, Project, Lab
    max_marks: float = 100.0
    weight_percentage: float = 20.0
    due_date: Optional[str] = None
    course_code: Optional[str] = None
    course_name: Optional[str] = None


@dataclass
class GradeRecord:
    id: Optional[int] = None
    assessment_id: int = 0
    student_id: int = 0
    marks_obtained: float = 0.0
    feedback: Optional[str] = None
    recorded_at: Optional[str] = None
    student_name: Optional[str] = None
    student_code: Optional[str] = None
    assessment_title: Optional[str] = None
    max_marks: Optional[float] = 100.0
    percentage: Optional[float] = 0.0
