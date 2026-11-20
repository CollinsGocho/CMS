"""
Academic and Grades Manager for Classroom Management System (CMS).
Handles assessments, grade recording, weighted score computation, GPA, and transcripts.
"""

from typing import Any, Dict, List, Optional, Tuple
from database import Database, db


class AcademicManager:
    """Manages assessments, grading, weighted averages, and academic performance."""

    GRADE_SCALE = [
        (93.0, "A", 4.0, "Excellent"),
        (90.0, "A-", 3.7, "Very Good"),
        (87.0, "B+", 3.3, "Good"),
        (83.0, "B", 3.0, "Above Average"),
        (80.0, "B-", 2.7, "Average"),
        (77.0, "C+", 2.3, "Satisfactory"),
        (70.0, "C", 2.0, "Pass"),
        (60.0, "D", 1.0, "Barely Pass"),
        (0.0, "F", 0.0, "Fail"),
    ]

    def __init__(self, database: Optional[Database] = None):
        self.db = database or db

    @classmethod
    def get_letter_grade(cls, percentage: float) -> Tuple[str, float, str]:
        """Convert percentage (0-100) to Letter Grade, Grade Points (4.0 scale), and Description."""
        for min_pct, letter, points, desc in cls.GRADE_SCALE:
            if percentage >= min_pct:
                return letter, points, desc
        return "F", 0.0, "Fail"

    # -------------------------------------------------------------
    # Assessment Operations
    # -------------------------------------------------------------
    def create_assessment(
        self,
        course_id: int,
        title: str,
        assessment_type: str,
        max_marks: float,
        weight_percentage: float = 20.0,
        due_date: Optional[str] = None,
    ) -> int:
        """Create a new academic evaluation item (Exam, Quiz, Project, etc.)."""
        query = """
        INSERT INTO assessments (course_id, title, assessment_type, max_marks, weight_percentage, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        return self.db.execute(
            query,
            (
                course_id,
                title.strip(),
                assessment_type,
                max_marks,
                weight_percentage,
                due_date,
            ),
        )

    def update_assessment(
        self,
        assessment_id: int,
        title: str,
        assessment_type: str,
        max_marks: float,
        weight_percentage: float,
        due_date: Optional[str] = None,
    ) -> bool:
        """Update an existing assessment's details."""
        query = """
        UPDATE assessments
        SET title = ?, assessment_type = ?, max_marks = ?, weight_percentage = ?, due_date = ?
        WHERE id = ?
        """
        self.db.execute(
            query,
            (
                title.strip(),
                assessment_type,
                max_marks,
                weight_percentage,
                due_date,
                assessment_id,
            ),
        )
        return True

    def delete_assessment(self, assessment_id: int) -> bool:
        """Delete an assessment and all associated student grades."""
        query = "DELETE FROM assessments WHERE id = ?"
        self.db.execute(query, (assessment_id,))
        return True

    def get_assessments_by_course(self, course_id: int) -> List[Dict[str, Any]]:
        """List all assessments configured for a specific course."""
        query = """
        SELECT a.*, c.course_code, c.course_name
        FROM assessments a
        JOIN courses c ON a.course_id = c.id
        WHERE a.course_id = ?
        ORDER BY a.due_date ASC, a.id ASC
        """
        return self.db.query_as_dicts(query, (course_id,))

    def get_assessment_by_id(self, assessment_id: int) -> Optional[Dict[str, Any]]:
        """Fetch details of a single assessment."""
        query = """
        SELECT a.*, c.course_code, c.course_name
        FROM assessments a
        JOIN courses c ON a.course_id = c.id
        WHERE a.id = ?
        """
        row = self.db.fetchone(query, (assessment_id,))
        return dict(row) if row else None

    # -------------------------------------------------------------
    # Grade Recording Operations
    # -------------------------------------------------------------
    def record_grade(
        self,
        assessment_id: int,
        student_id: int,
        marks_obtained: float,
        feedback: Optional[str] = None,
    ) -> bool:
        """Record or update a student's score for an assessment."""
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment ID {assessment_id} does not exist.")

        if marks_obtained < 0 or marks_obtained > assessment["max_marks"]:
            raise ValueError(
                f"Marks obtained ({marks_obtained}) must be between 0 and maximum marks ({assessment['max_marks']})."
            )

        query = """
        INSERT INTO grades (assessment_id, student_id, marks_obtained, feedback)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(assessment_id, student_id)
        DO UPDATE SET marks_obtained = excluded.marks_obtained, 
                      feedback = excluded.feedback, 
                      recorded_at = CURRENT_TIMESTAMP
        """
        self.db.execute(query, (assessment_id, student_id, marks_obtained, feedback))
        return True

    def batch_record_grades(
        self,
        assessment_id: int,
        grade_records: List[Dict[str, Any]],
    ) -> int:
        """
        Record marks for multiple students on an assessment.
        grade_records: [{'student_id': 1, 'marks_obtained': 85.5, 'feedback': 'Good'}]
        """
        assessment = self.get_assessment_by_id(assessment_id)
        if not assessment:
            raise ValueError(f"Assessment ID {assessment_id} does not exist.")

        params_list = []
        for item in grade_records:
            marks = float(item["marks_obtained"])
            if 0 <= marks <= assessment["max_marks"]:
                params_list.append((
                    assessment_id,
                    item["student_id"],
                    marks,
                    item.get("feedback", ""),
                ))

        query = """
        INSERT INTO grades (assessment_id, student_id, marks_obtained, feedback)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(assessment_id, student_id)
        DO UPDATE SET marks_obtained = excluded.marks_obtained, 
                      feedback = excluded.feedback, 
                      recorded_at = CURRENT_TIMESTAMP
        """
        return self.db.executemany(query, params_list)

    def get_assessment_gradebook(self, assessment_id: int) -> List[Dict[str, Any]]:
        """
        Get all enrolled students for this assessment's course and their recorded marks.
        """
        query = """
        SELECT 
            s.id AS student_pk,
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            asm.id AS assessment_id,
            asm.max_marks,
            asm.weight_percentage,
            g.id AS grade_id,
            g.marks_obtained,
            ROUND((g.marks_obtained / asm.max_marks) * 100.0, 1) AS percentage,
            g.feedback,
            g.recorded_at
        FROM assessments asm
        JOIN enrollments e ON asm.course_id = e.course_id
        JOIN students s ON e.student_id = s.id
        LEFT JOIN grades g ON g.assessment_id = asm.id AND g.student_id = s.id
        WHERE asm.id = ?
        ORDER BY s.student_id ASC
        """
        rows = self.db.query_as_dicts(query, (assessment_id,))
        for row in rows:
            if row["marks_obtained"] is not None:
                letter, gpa, desc = self.get_letter_grade(row["percentage"])
                row["letter_grade"] = letter
                row["grade_point"] = gpa
            else:
                row["letter_grade"] = "N/A"
                row["grade_point"] = 0.0
        return rows

    # -------------------------------------------------------------
    # Student Academic Calculations & Transcripts
    # -------------------------------------------------------------
    def get_student_course_academic_summary(self, student_id: int, course_id: int) -> Dict[str, Any]:
        """
        Calculate weighted average, total percentage, letter grade, and grade points
        for a student in a specific course based on all graded assessments.
        """
        query = """
        SELECT 
            asm.id AS assessment_id,
            asm.title,
            asm.assessment_type,
            asm.max_marks,
            asm.weight_percentage,
            g.marks_obtained,
            ROUND((g.marks_obtained / asm.max_marks) * 100.0, 2) AS percentage,
            g.feedback
        FROM assessments asm
        LEFT JOIN grades g ON asm.id = g.assessment_id AND g.student_id = ?
        WHERE asm.course_id = ?
        ORDER BY asm.id ASC
        """
        assessments = self.db.query_as_dicts(query, (student_id, course_id))
        
        total_weight = 0.0
        weighted_score_accum = 0.0

        for a in assessments:
            if a["marks_obtained"] is not None:
                total_weight += a["weight_percentage"]
                weighted_score_accum += (a["marks_obtained"] / a["max_marks"]) * a["weight_percentage"]

        if total_weight > 0:
            course_percentage = round((weighted_score_accum / total_weight) * 100.0, 2)
        else:
            course_percentage = 0.0

        letter, gpa_point, description = self.get_letter_grade(course_percentage)

        return {
            "assessments": assessments,
            "graded_weight_total": total_weight,
            "course_percentage": course_percentage,
            "letter_grade": letter if total_weight > 0 else "N/A",
            "grade_point": gpa_point if total_weight > 0 else 0.0,
            "performance_description": description if total_weight > 0 else "No grades entered",
        }

    def get_full_student_transcript(self, student_id: int) -> Dict[str, Any]:
        """
        Build an all-inclusive academic and attendance transcript for a student.
        Computes overall cumulative GPA weighted by course credit hours.
        """
        # Student info
        student_info = self.db.fetchone("SELECT * FROM students WHERE id = ?", (student_id,))
        if not student_info:
            return {}

        # Enrolled courses
        courses = self.db.query_as_dicts("""
            SELECT c.* 
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = ?
            ORDER BY c.course_code ASC
        """, (student_id,))

        courses_summary = []
        total_credit_points = 0.0
        total_credit_hours = 0

        for c in courses:
            academic_data = self.get_student_course_academic_summary(student_id, c["id"])
            
            # Attendance for this course
            att_data = self.db.fetchone("""
                SELECT 
                    total_sessions, present_count, late_count, absent_count, excused_count, attendance_percentage
                FROM v_attendance_summary
                WHERE student_pk = ? AND course_pk = ?
            """, (student_id, c["id"]))

            credits = c["credit_hours"]
            grade_point = academic_data["grade_point"]

            if academic_data["graded_weight_total"] > 0:
                total_credit_hours += credits
                total_credit_points += grade_point * credits

            courses_summary.append({
                "course_code": c["course_code"],
                "course_name": c["course_name"],
                "instructor": c["instructor"],
                "credit_hours": credits,
                "semester": c["semester"],
                "percentage": academic_data["course_percentage"],
                "letter_grade": academic_data["letter_grade"],
                "grade_point": grade_point,
                "attendance_percentage": att_data["attendance_percentage"] if att_data else 0.0,
                "total_sessions": att_data["total_sessions"] if att_data else 0,
                "assessments": academic_data["assessments"],
            })

        cumulative_gpa = round(total_credit_points / total_credit_hours, 2) if total_credit_hours > 0 else 0.0
        overall_letter, _, _ = self.get_letter_grade(cumulative_gpa / 4.0 * 100.0 if cumulative_gpa else 0)

        return {
            "student": dict(student_info),
            "courses": courses_summary,
            "cumulative_gpa": cumulative_gpa,
            "total_credit_hours": total_credit_hours,
            "overall_status": "Good Standing" if cumulative_gpa >= 2.0 else "Academic Warning",
        }

    def get_course_academic_analytics(self, course_id: int) -> Dict[str, Any]:
        """Class statistics: highest, lowest, average, distribution."""
        query = """
        SELECT 
            asm.id AS assessment_id,
            asm.title,
            asm.assessment_type,
            asm.max_marks,
            COUNT(g.id) AS submission_count,
            ROUND(AVG(g.marks_obtained), 2) AS avg_marks,
            ROUND(AVG(g.marks_obtained / asm.max_marks * 100.0), 1) AS avg_pct,
            MAX(g.marks_obtained) AS highest_marks,
            MIN(g.marks_obtained) AS lowest_marks
        FROM assessments asm
        LEFT JOIN grades g ON asm.id = g.assessment_id
        WHERE asm.course_id = ?
        GROUP BY asm.id
        """
        return {"assessments": self.db.query_as_dicts(query, (course_id,))}
