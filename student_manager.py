"""
Student and Course Manager for Classroom Management System (CMS).
Provides CRUD functionality for students, courses, enrollments, and high-level metrics.
"""

from typing import Any, Dict, List, Optional
from database import Database, db
from models import Course, Student


class StudentManager:
    """Manages student records, courses, and student enrollments."""

    def __init__(self, database: Optional[Database] = None):
        self.db = database or db

    # -------------------------------------------------------------
    # Student Operations
    # -------------------------------------------------------------
    def add_student(
        self,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        enrollment_date: str,
        gender: str = "Prefer not to say",
        date_of_birth: Optional[str] = None,
        phone: Optional[str] = None,
        status: str = "Active",
    ) -> int:
        """Register a new student."""
        query = """
        INSERT INTO students (student_id, first_name, last_name, email, gender, date_of_birth, phone, enrollment_date, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(
            query,
            (
                student_id.strip(),
                first_name.strip(),
                last_name.strip(),
                email.strip(),
                gender,
                date_of_birth,
                phone,
                enrollment_date,
                status,
            ),
        )

    def update_student(
        self,
        pk: int,
        student_id: str,
        first_name: str,
        last_name: str,
        email: str,
        enrollment_date: str,
        gender: str = "Prefer not to say",
        date_of_birth: Optional[str] = None,
        phone: Optional[str] = None,
        status: str = "Active",
    ) -> bool:
        """Update existing student details."""
        query = """
        UPDATE students
        SET student_id = ?, first_name = ?, last_name = ?, email = ?,
            gender = ?, date_of_birth = ?, phone = ?, enrollment_date = ?, status = ?
        WHERE id = ?
        """
        self.db.execute(
            query,
            (
                student_id.strip(),
                first_name.strip(),
                last_name.strip(),
                email.strip(),
                gender,
                date_of_birth,
                phone,
                enrollment_date,
                status,
                pk,
            ),
        )
        return True

    def delete_student(self, pk: int) -> bool:
        """Delete student and all associated records through cascading foreign keys."""
        query = "DELETE FROM students WHERE id = ?"
        self.db.execute(query, (pk,))
        return True

    def get_student_by_id(self, pk: int) -> Optional[Dict[str, Any]]:
        """Fetch student record by primary key."""
        query = "SELECT * FROM students WHERE id = ?"
        row = self.db.fetchone(query, (pk,))
        return dict(row) if row else None

    def get_student_by_code(self, student_id: str) -> Optional[Dict[str, Any]]:
        """Fetch student record by student code (e.g. 'STU-1001')."""
        query = "SELECT * FROM students WHERE student_id = ?"
        row = self.db.fetchone(query, (student_id.strip(),))
        return dict(row) if row else None

    def list_students(
        self, search_query: Optional[str] = None, status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List students with optional search filtering by name, ID, or email."""
        sql = "SELECT * FROM students WHERE 1=1"
        params: List[Any] = []

        if status and status != "All":
            sql += " AND status = ?"
            params.append(status)

        if search_query:
            term = f"%{search_query.strip()}%"
            sql += " AND (student_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR email LIKE ?)"
            params.extend([term, term, term, term])

        sql += " ORDER BY student_id ASC"
        return self.db.query_as_dicts(sql, tuple(params))

    # -------------------------------------------------------------
    # Course Operations
    # -------------------------------------------------------------
    def add_course(
        self,
        course_code: str,
        course_name: str,
        instructor: str,
        credit_hours: int = 3,
        semester: str = "Fall 2026",
    ) -> int:
        """Add a new course/subject to the curriculum."""
        query = """
        INSERT INTO courses (course_code, course_name, instructor, credit_hours, semester)
        VALUES (?, ?, ?, ?, ?)
        """
        return self.db.execute(
            query,
            (
                course_code.strip().upper(),
                course_name.strip(),
                instructor.strip(),
                credit_hours,
                semester.strip(),
            ),
        )

    def update_course(
        self,
        pk: int,
        course_code: str,
        course_name: str,
        instructor: str,
        credit_hours: int,
        semester: str,
    ) -> bool:
        """Update course details."""
        query = """
        UPDATE courses
        SET course_code = ?, course_name = ?, instructor = ?, credit_hours = ?, semester = ?
        WHERE id = ?
        """
        self.db.execute(
            query,
            (
                course_code.strip().upper(),
                course_name.strip(),
                instructor.strip(),
                credit_hours,
                semester.strip(),
                pk,
            ),
        )
        return True

    def delete_course(self, pk: int) -> bool:
        """Delete course and associated enrollments/attendance/assessments."""
        query = "DELETE FROM courses WHERE id = ?"
        self.db.execute(query, (pk,))
        return True

    def list_courses(self) -> List[Dict[str, Any]]:
        """List all active courses with enrolled student counts."""
        query = """
        SELECT 
            c.*,
            COUNT(e.student_id) AS enrolled_count
        FROM courses c
        LEFT JOIN enrollments e ON c.id = e.course_id
        GROUP BY c.id
        ORDER BY c.course_code ASC
        """
        return self.db.query_as_dicts(query)

    def get_course_by_id(self, pk: int) -> Optional[Dict[str, Any]]:
        """Fetch course details by primary key."""
        query = "SELECT * FROM courses WHERE id = ?"
        row = self.db.fetchone(query, (pk,))
        return dict(row) if row else None

    # -------------------------------------------------------------
    # Enrollment Operations
    # -------------------------------------------------------------
    def enroll_student(self, student_id: int, course_id: int) -> bool:
        """Enroll a student in a course."""
        query = "INSERT OR IGNORE INTO enrollments (student_id, course_id) VALUES (?, ?)"
        self.db.execute(query, (student_id, course_id))
        return True

    def unenroll_student(self, student_id: int, course_id: int) -> bool:
        """Remove a student from a course."""
        query = "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?"
        self.db.execute(query, (student_id, course_id))
        return True

    def get_enrolled_students(self, course_id: int) -> List[Dict[str, Any]]:
        """Get list of students enrolled in a specific course."""
        query = """
        SELECT 
            s.id AS student_pk,
            s.student_id,
            s.first_name,
            s.last_name,
            s.email,
            s.status,
            e.enrolled_at
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        WHERE e.course_id = ?
        ORDER BY s.student_id ASC
        """
        return self.db.query_as_dicts(query, (course_id,))

    def get_student_courses(self, student_id: int) -> List[Dict[str, Any]]:
        """Get courses that a specific student is enrolled in."""
        query = """
        SELECT 
            c.*,
            e.enrolled_at
        FROM enrollments e
        JOIN courses c ON e.course_id = c.id
        WHERE e.student_id = ?
        ORDER BY c.course_code ASC
        """
        return self.db.query_as_dicts(query, (student_id,))

    # -------------------------------------------------------------
    # Dashboard Overview Metrics
    # -------------------------------------------------------------
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Fetch key performance indicators for the classroom dashboard."""
        total_students = self.db.fetchone("SELECT COUNT(*) AS cnt FROM students WHERE status='Active'")
        total_courses = self.db.fetchone("SELECT COUNT(*) AS cnt FROM courses")
        total_assessments = self.db.fetchone("SELECT COUNT(*) AS cnt FROM assessments")
        
        # Overall Attendance percentage
        att_row = self.db.fetchone("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status='Present' THEN 1.0 WHEN status='Late' THEN 0.75 ELSE 0 END) as attended
            FROM attendance
        """)
        attendance_rate = 0.0
        if att_row and att_row["total"] and att_row["total"] > 0:
            attendance_rate = round((att_row["attended"] / att_row["total"]) * 100.0, 1)

        # Overall Academic Average percentage
        grade_row = self.db.fetchone("""
            SELECT AVG(g.marks_obtained / a.max_marks * 100.0) as avg_pct
            FROM grades g
            JOIN assessments a ON g.assessment_id = a.id
        """)
        academic_avg = round(grade_row["avg_pct"], 1) if grade_row and grade_row["avg_pct"] is not None else 0.0

        # Low attendance students (< 75%)
        low_att_row = self.db.fetchall("""
            SELECT student_id, student_name, course_code, attendance_percentage
            FROM v_attendance_summary
            WHERE total_sessions >= 2 AND attendance_percentage < 75.0
        """)

        return {
            "total_students": total_students["cnt"] if total_students else 0,
            "total_courses": total_courses["cnt"] if total_courses else 0,
            "total_assessments": total_assessments["cnt"] if total_assessments else 0,
            "overall_attendance_rate": attendance_rate,
            "overall_academic_avg": academic_avg,
            "low_attendance_warnings": [dict(r) for r in low_att_row],
        }
