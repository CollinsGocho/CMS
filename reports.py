"""
Reporting and Export Module for Classroom Management System (CMS).
Provides CSV exports, formatted text transcripts, and academic performance printouts.
"""

import csv
import io
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from academic_manager import AcademicManager
from attendance_manager import AttendanceManager
from database import Database, db
from student_manager import StudentManager


class ReportService:
    """Generates exports and formatted reports for students, attendance, and academics."""

    def __init__(self, database: Optional[Database] = None):
        self.db = database or db
        self.student_mgr = StudentManager(self.db)
        self.attendance_mgr = AttendanceManager(self.db)
        self.academic_mgr = AcademicManager(self.db)

    def export_students_csv(self, file_path: str) -> str:
        """Export all student records to a CSV file."""
        students = self.student_mgr.list_students()
        fieldnames = [
            "student_id",
            "first_name",
            "last_name",
            "email",
            "gender",
            "date_of_birth",
            "phone",
            "enrollment_date",
            "status",
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for s in students:
                writer.writerow(s)
        return file_path

    def export_attendance_csv(self, course_id: int, file_path: str) -> str:
        """Export course attendance summary to CSV."""
        course = self.student_mgr.get_course_by_id(course_id)
        c_code = course["course_code"] if course else "Course"
        summary = self.attendance_mgr.get_course_attendance_summary(course_id)

        fieldnames = [
            "student_id",
            "student_name",
            "course_code",
            "total_sessions",
            "present_count",
            "late_count",
            "absent_count",
            "excused_count",
            "attendance_percentage",
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in summary:
                writer.writerow(r)
        return file_path

    def export_gradebook_csv(self, assessment_id: int, file_path: str) -> str:
        """Export grades of an assessment to CSV."""
        rows = self.academic_mgr.get_assessment_gradebook(assessment_id)
        fieldnames = [
            "student_id",
            "student_name",
            "max_marks",
            "marks_obtained",
            "percentage",
            "letter_grade",
            "feedback",
        ]
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in rows:
                writer.writerow(r)
        return file_path

    def generate_student_report_card_text(self, student_id: int) -> str:
        """Generate a clean, beautiful plain-text academic and attendance transcript."""
        transcript = self.academic_mgr.get_full_student_transcript(student_id)
        if not transcript or not transcript.get("student"):
            return "Student record not found."

        s = transcript["student"]
        courses = transcript["courses"]
        gpa = transcript["cumulative_gpa"]
        status = transcript["overall_status"]

        buf = io.StringIO()
        line_sep = "=" * 78
        sub_sep = "-" * 78

        buf.write(f"\n{line_sep}\n")
        buf.write("           CLASSROOM MANAGEMENT SYSTEM - OFFICIAL REPORT CARD\n")
        buf.write(f"{line_sep}\n")
        buf.write(f" Student Name : {s['first_name']} {s['last_name']:<25} Student ID : {s['student_id']}\n")
        buf.write(f" Email        : {s['email']:<25} Date of Birth: {s.get('date_of_birth') or 'N/A'}\n")
        buf.write(f" Enrolled     : {s['enrollment_date']:<25} Status       : {s['status']}\n")
        buf.write(f" Issued Date  : {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        buf.write(f"{sub_sep}\n")
        buf.write(" ACADEMIC & ATTENDANCE PERFORMANCE SUMMARY:\n")
        buf.write(f"{sub_sep}\n")
        buf.write(
            f" {'Course Code':<12} | {'Course Name':<28} | {'Credits':<7} | {'Attnd %':<7} | {'Score %':<7} | {'Grade':<5} | {'Pts':<4}\n"
        )
        buf.write(f"{sub_sep}\n")

        for c in courses:
            c_name = (c["course_name"][:25] + "..") if len(c["course_name"]) > 28 else c["course_name"]
            buf.write(
                f" {c['course_code']:<12} | {c_name:<28} | {c['credit_hours']:<7} | {c['attendance_percentage']:>6.1f}% | {c['percentage']:>6.1f}% | {c['letter_grade']:<5} | {c['grade_point']:<4.1f}\n"
            )

        buf.write(f"{sub_sep}\n")
        buf.write(f" Cumulative GPA     : {gpa:.2f} / 4.00\n")
        buf.write(f" Total Credits Earned: {transcript['total_credit_hours']}\n")
        buf.write(f" Academic Standing  : {status}\n")
        buf.write(f"{sub_sep}\n\n")

        # Detailed breakdown per course
        buf.write(" DETAILED ASSESSMENT BREAKDOWN:\n")
        for c in courses:
            buf.write(f"\n  [ {c['course_code']} - {c['course_name']} ] (Instructor: {c['instructor']})\n")
            buf.write(f"  Attendance: {c['attendance_percentage']}% ({c['total_sessions']} sessions tracked)\n")
            if not c["assessments"]:
                buf.write("    (No assessments recorded yet)\n")
                continue
            buf.write(f"    {'Assessment':<30} | {'Type':<12} | {'Score':<10} | {'Weight':<8} | {'Feedback'}\n")
            buf.write("    " + "-" * 72 + "\n")
            for a in c["assessments"]:
                marks_str = f"{a['marks_obtained']}/{a['max_marks']}" if a["marks_obtained"] is not None else "Not Graded"
                fb = a.get("feedback") or ""
                buf.write(f"    {a['title']:<30} | {a['assessment_type']:<12} | {marks_str:<10} | {a['weight_percentage']:>5.1f}% | {fb}\n")

        buf.write(f"\n{line_sep}\n")
        buf.write(" End of Report Card\n")
        buf.write(f"{line_sep}\n")

        return buf.getvalue()
