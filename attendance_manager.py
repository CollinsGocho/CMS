"""
Attendance Manager for Classroom Management System (CMS).
Handles daily attendance marking, batch records, student histories, and attendance analytics.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Tuple
from database import Database, db


class AttendanceManager:
    """Manages student attendance tracking and calculations."""

    VALID_STATUSES = ["Present", "Absent", "Late", "Excused"]

    def __init__(self, database: Optional[Database] = None):
        self.db = database or db

    def mark_attendance(
        self,
        student_id: int,
        course_id: int,
        attendance_date: str,
        status: str,
        remarks: Optional[str] = None,
    ) -> bool:
        """Record or update attendance for a single student on a given date."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status '{status}'. Must be one of {self.VALID_STATUSES}")

        query = """
        INSERT INTO attendance (student_id, course_id, attendance_date, status, remarks)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, course_id, attendance_date) 
        DO UPDATE SET status = excluded.status, remarks = excluded.remarks, recorded_at = CURRENT_TIMESTAMP
        """
        self.db.execute(query, (student_id, course_id, attendance_date, status, remarks))
        return True

    def batch_mark_attendance(
        self,
        course_id: int,
        attendance_date: str,
        records: List[Dict[str, Any]],
    ) -> int:
        """
        Mark attendance for multiple students for a specific course and date.
        records should be a list of dicts: [{'student_id': 1, 'status': 'Present', 'remarks': '...'}]
        """
        params_list = []
        for r in records:
            status = r.get("status", "Present")
            if status not in self.VALID_STATUSES:
                status = "Present"
            params_list.append((
                r["student_id"],
                course_id,
                attendance_date,
                status,
                r.get("remarks", ""),
            ))

        query = """
        INSERT INTO attendance (student_id, course_id, attendance_date, status, remarks)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, course_id, attendance_date)
        DO UPDATE SET status = excluded.status, remarks = excluded.remarks, recorded_at = CURRENT_TIMESTAMP
        """
        return self.db.executemany(query, params_list)

    def mark_all_present(self, course_id: int, attendance_date: str) -> int:
        """Convenience method to set all enrolled students of a course as Present for the date."""
        enrolled_students = self.db.fetchall(
            "SELECT student_id FROM enrollments WHERE course_id = ?", (course_id,)
        )
        records = [{"student_id": row["student_id"], "status": "Present", "remarks": "Marked all present"} for row in enrolled_students]
        return self.batch_mark_attendance(course_id, attendance_date, records)

    def get_attendance_sheet(self, course_id: int, attendance_date: str) -> List[Dict[str, Any]]:
        """
        Retrieve all enrolled students in a course along with their recorded status for a date.
        If attendance hasn't been recorded yet, status defaults to 'Not Recorded'.
        """
        query = """
        SELECT 
            s.id AS student_pk,
            s.student_id,
            s.first_name,
            s.last_name,
            COALESCE(a.status, 'Not Recorded') AS status,
            COALESCE(a.remarks, '') AS remarks,
            a.id AS attendance_id
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        LEFT JOIN attendance a ON a.student_id = s.id AND a.course_id = e.course_id AND a.attendance_date = ?
        WHERE e.course_id = ?
        ORDER BY s.student_id ASC
        """
        return self.db.query_as_dicts(query, (attendance_date, course_id))

    def get_attendance_dates(self, course_id: int) -> List[str]:
        """Fetch distinct session dates where attendance was recorded for a course."""
        query = """
        SELECT DISTINCT attendance_date 
        FROM attendance 
        WHERE course_id = ? 
        ORDER BY attendance_date DESC
        """
        rows = self.db.fetchall(query, (course_id,))
        return [row["attendance_date"] for row in rows]

    def get_student_attendance_summary(self, student_id: int) -> List[Dict[str, Any]]:
        """Fetch attendance summary across all enrolled courses for a given student."""
        query = """
        SELECT * FROM v_attendance_summary
        WHERE student_pk = ?
        ORDER BY course_code ASC
        """
        return self.db.query_as_dicts(query, (student_id,))

    def get_course_attendance_summary(self, course_id: int) -> List[Dict[str, Any]]:
        """Fetch overall attendance statistics for all students in a course."""
        query = """
        SELECT * FROM v_attendance_summary
        WHERE course_pk = ?
        ORDER BY student_name ASC
        """
        return self.db.query_as_dicts(query, (course_id,))

    def get_detailed_student_log(self, student_id: int, course_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get chronological attendance log for a student."""
        sql = """
        SELECT 
            a.attendance_date,
            c.course_code,
            c.course_name,
            a.status,
            a.remarks
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = ?
        """
        params: List[Any] = [student_id]
        if course_id:
            sql += " AND a.course_id = ?"
            params.append(course_id)

        sql += " ORDER BY a.attendance_date DESC"
        return self.db.query_as_dicts(sql, tuple(params))

    def get_low_attendance_warnings(self, threshold: float = 75.0) -> List[Dict[str, Any]]:
        """Identify students whose attendance rate falls below the designated percentage."""
        query = """
        SELECT 
            student_pk,
            student_id,
            student_name,
            course_pk,
            course_code,
            course_name,
            total_sessions,
            present_count,
            absent_count,
            attendance_percentage
        FROM v_attendance_summary
        WHERE total_sessions >= 2 AND attendance_percentage < ?
        ORDER BY attendance_percentage ASC
        """
        return self.db.query_as_dicts(query, (threshold,))
