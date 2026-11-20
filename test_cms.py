"""
Unit and Integration Test Suite for Classroom Management System (CMS).
"""

import os
import tempfile
import unittest
from academic_manager import AcademicManager
from attendance_manager import AttendanceManager
from database import Database
from reports import ReportService
from student_manager import StudentManager


class TestClassroomManagementSystem(unittest.TestCase):
    """Test all database schemas, calculations, and services."""

    def setUp(self):
        # Create an isolated temporary SQLite database for tests
        self.temp_db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.temp_db_file.close()
        self.db = Database(self.temp_db_file.name)
        self.db.init_database(seed=True)

        self.student_mgr = StudentManager(self.db)
        self.attendance_mgr = AttendanceManager(self.db)
        self.academic_mgr = AcademicManager(self.db)
        self.report_svc = ReportService(self.db)

    def tearDown(self):
        if os.path.exists(self.temp_db_file.name):
            try:
                os.remove(self.temp_db_file.name)
            except PermissionError:
                pass

    def test_database_initialization_and_seeding(self):
        """Verify that tables, views, and seed data are populated properly."""
        students = self.student_mgr.list_students()
        self.assertGreaterEqual(len(students), 8)
        self.assertEqual(students[0]["student_id"], "STU-1001")

        courses = self.student_mgr.list_courses()
        self.assertGreaterEqual(len(courses), 4)

    def test_student_crud(self):
        """Test adding, editing, and deleting student."""
        # Add student
        new_id = self.student_mgr.add_student(
            student_id="STU-9999",
            first_name="Test",
            last_name="User",
            email="test.user@school.edu",
            enrollment_date="2026-11-01",
            gender="Male",
        )
        self.assertIsNotNone(new_id)

        stu = self.student_mgr.get_student_by_code("STU-9999")
        self.assertIsNotNone(stu)
        self.assertEqual(stu["first_name"], "Test")

        # Update student
        self.student_mgr.update_student(
            pk=stu["id"],
            student_id="STU-9999",
            first_name="TestUpdated",
            last_name="User",
            email="test.user@school.edu",
            enrollment_date="2026-11-01",
        )
        updated_stu = self.student_mgr.get_student_by_id(stu["id"])
        self.assertEqual(updated_stu["first_name"], "TestUpdated")

        # Delete student
        self.student_mgr.delete_student(stu["id"])
        deleted_stu = self.student_mgr.get_student_by_id(stu["id"])
        self.assertIsNone(deleted_stu)

    def test_attendance_recording_and_summary(self):
        """Test recording attendance and calculating attendance rates."""
        # Enroll Alice (id=1) in Course 1
        self.attendance_mgr.mark_attendance(
            student_id=1,
            course_id=1,
            attendance_date="2026-11-19",
            status="Present",
            remarks="Present on time",
        )

        sheet = self.attendance_mgr.get_attendance_sheet(course_id=1, attendance_date="2026-11-19")
        alice_entry = next((s for s in sheet if s["student_pk"] == 1), None)
        self.assertIsNotNone(alice_entry)
        self.assertEqual(alice_entry["status"], "Present")

        # Test batch attendance
        batch_records = [
            {"student_id": 1, "status": "Late", "remarks": "Late bus"},
            {"student_id": 2, "status": "Absent", "remarks": "Sick"},
        ]
        self.attendance_mgr.batch_mark_attendance(1, "2026-11-20", batch_records)

        sheet_day2 = self.attendance_mgr.get_attendance_sheet(course_id=1, attendance_date="2026-11-20")
        alice_d2 = next((s for s in sheet_day2 if s["student_pk"] == 1), None)
        brian_d2 = next((s for s in sheet_day2 if s["student_pk"] == 2), None)
        self.assertEqual(alice_d2["status"], "Late")
        self.assertEqual(brian_d2["status"], "Absent")

    def test_academics_and_grading(self):
        """Test creating assessment, entering grades, and GPA calculation."""
        # Create an assessment
        asm_id = self.academic_mgr.create_assessment(
            course_id=1,
            title="Unit Test 1",
            assessment_type="Quiz",
            max_marks=50.0,
            weight_percentage=10.0,
            due_date="2026-11-25",
        )
        self.assertGreater(asm_id, 0)

        # Record grade for student 1
        self.academic_mgr.record_grade(asm_id, 1, 45.0, "Great work!")

        # Verify gradebook
        gradebook = self.academic_mgr.get_assessment_gradebook(asm_id)
        stu1_grade = next((g for g in gradebook if g["student_pk"] == 1), None)
        self.assertIsNotNone(stu1_grade)
        self.assertEqual(stu1_grade["marks_obtained"], 45.0)
        self.assertEqual(stu1_grade["percentage"], 90.0)

        # Check transcript calculation
        transcript = self.academic_mgr.get_full_student_transcript(1)
        self.assertIn("courses", transcript)
        self.assertGreater(transcript["cumulative_gpa"], 3.0)

    def test_reports_generation(self):
        """Test report card text and CSV export functions."""
        report_text = self.report_svc.generate_student_report_card_text(1)
        self.assertIn("OFFICIAL REPORT CARD", report_text)
        self.assertIn("Alice Johnson", report_text)
        self.assertIn("CS-101", report_text)

        # CSV export test
        temp_csv = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        temp_csv.close()
        try:
            self.report_svc.export_students_csv(temp_csv.name)
            self.assertTrue(os.path.exists(temp_csv.name))
            self.assertGreater(os.path.getsize(temp_csv.name), 50)
        finally:
            if os.path.exists(temp_csv.name):
                os.remove(temp_csv.name)


if __name__ == "__main__":
    unittest.main()
