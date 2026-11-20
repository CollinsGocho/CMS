"""
Interactive Command Line Interface (CLI) for Classroom Management System (CMS).
"""

import os
import sys
from datetime import date
from academic_manager import AcademicManager
from attendance_manager import AttendanceManager
from database import db
from reports import ReportService
from student_manager import StudentManager


class ClassroomCLI:
    """Terminal-based user interface for CMS."""

    def __init__(self):
        self.db = db
        self.db.init_database(seed=True)
        self.student_mgr = StudentManager(self.db)
        self.attendance_mgr = AttendanceManager(self.db)
        self.academic_mgr = AcademicManager(self.db)
        self.report_svc = ReportService(self.db)

    def print_header(self, title: str):
        print("\n" + "=" * 70)
        print(f" {title.center(68)} ")
        print("=" * 70)

    def run(self):
        while True:
            self.print_header("CLASSROOM MANAGEMENT SYSTEM (CMS)")
            print(" [1] Dashboard & Key Metrics")
            print(" [2] Student Management (List, Add, Edit, Delete)")
            print(" [3] Course & Curriculum Management")
            print(" [4] Attendance Tracker (Daily Roll Call & History)")
            print(" [5] Academic Assessments & Gradebook")
            print(" [6] Student Report Cards & Transcripts")
            print(" [7] Reset / Re-seed Database")
            print(" [0] Exit Application")
            print("-" * 70)

            choice = input("Select an option (0-7): ").strip()

            if choice == "1":
                self.show_dashboard()
            elif choice == "2":
                self.manage_students()
            elif choice == "3":
                self.manage_courses()
            elif choice == "4":
                self.manage_attendance()
            elif choice == "5":
                self.manage_academics()
            elif choice == "6":
                self.show_report_cards()
            elif choice == "7":
                self.reset_database()
            elif choice == "0":
                print("\nExiting Classroom Management System. Goodbye!\n")
                sys.exit(0)
            else:
                print("\nInvalid choice. Please choose a valid option (0-7).")

    # -------------------------------------------------------------
    # 1. Dashboard
    # -------------------------------------------------------------
    def show_dashboard(self):
        self.print_header("DASHBOARD OVERVIEW")
        stats = self.student_mgr.get_dashboard_summary()
        print(f" Total Active Students : {stats['total_students']}")
        print(f" Total Active Courses  : {stats['total_courses']}")
        print(f" Total Assessments     : {stats['total_assessments']}")
        print(f" Overall Attendance    : {stats['overall_attendance_rate']}%")
        print(f" Overall Academic Avg  : {stats['overall_academic_avg']}%")

        print("\n--- Low Attendance Alerts (< 75%) ---")
        warnings = stats["low_attendance_warnings"]
        if warnings:
            for w in warnings:
                print(f" [!] {w['student_id']} - {w['student_name']} in {w['course_code']}: {w['attendance_percentage']}%")
        else:
            print(" [✓] All enrolled students have healthy attendance (>75%).")

        input("\nPress Enter to return to main menu...")

    # -------------------------------------------------------------
    # 2. Student Management
    # -------------------------------------------------------------
    def manage_students(self):
        while True:
            self.print_header("STUDENT MANAGEMENT")
            print(" [1] List All Students")
            print(" [2] Search Students")
            print(" [3] Add New Student")
            print(" [4] Delete Student")
            print(" [5] Export Student Directory (CSV)")
            print(" [0] Back to Main Menu")
            print("-" * 70)

            choice = input("Select (0-5): ").strip()
            if choice == "1":
                self.display_students_table(self.student_mgr.list_students())
            elif choice == "2":
                query = input("Enter search keyword (Name, ID, or Email): ").strip()
                self.display_students_table(self.student_mgr.list_students(search_query=query))
            elif choice == "3":
                self.add_student_form()
            elif choice == "4":
                self.delete_student_form()
            elif choice == "5":
                path = "students_export.csv"
                self.report_svc.export_students_csv(path)
                print(f"\n[✓] Student list exported successfully to: {os.path.abspath(path)}")
            elif choice == "0":
                break

    def display_students_table(self, students):
        if not students:
            print("\nNo student records found.")
            return
        print(f"\n{'ID':<5} | {'Student Code':<12} | {'Name':<22} | {'Email':<26} | {'Status'}")
        print("-" * 78)
        for s in students:
            full_name = f"{s['first_name']} {s['last_name']}"
            print(f"{s['id']:<5} | {s['student_id']:<12} | {full_name:<22} | {s['email']:<26} | {s['status']}")

    def add_student_form(self):
        print("\n--- Add New Student ---")
        code = input("Student ID (e.g. STU-1009): ").strip()
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        email = input("Email: ").strip()
        gender = input("Gender (Male/Female/Other): ").strip() or "Prefer not to say"
        dob = input("Date of Birth (YYYY-MM-DD): ").strip() or None
        phone = input("Phone: ").strip() or None
        enroll_date = input(f"Enrollment Date [{date.today()}]: ").strip() or str(date.today())

        try:
            new_id = self.student_mgr.add_student(
                student_id=code,
                first_name=first_name,
                last_name=last_name,
                email=email,
                enrollment_date=enroll_date,
                gender=gender,
                date_of_birth=dob,
                phone=phone,
            )
            print(f"\n[✓] Student created successfully with ID: {new_id}")
        except Exception as e:
            print(f"\n[X] Error creating student: {e}")

    def delete_student_form(self):
        stu_id = input("Enter Student Database ID to delete: ").strip()
        if not stu_id.isdigit():
            print("Invalid numeric ID.")
            return
        confirm = input(f"Are you sure you want to permanently delete student ID {stu_id}? (y/N): ")
        if confirm.lower() == "y":
            self.student_mgr.delete_student(int(stu_id))
            print("[✓] Student deleted successfully.")

    # -------------------------------------------------------------
    # 3. Course Management
    # -------------------------------------------------------------
    def manage_courses(self):
        while True:
            self.print_header("COURSE MANAGEMENT")
            courses = self.student_mgr.list_courses()
            print(f"{'ID':<4} | {'Code':<10} | {'Course Name':<28} | {'Instructor':<20} | {'Enrolled'}")
            print("-" * 75)
            for c in courses:
                print(f"{c['id']:<4} | {c['course_code']:<10} | {c['course_name']:<28} | {c['instructor']:<20} | {c['enrolled_count']}")

            print("\n [1] Add New Course")
            print(" [2] Enroll Student in Course")
            print(" [3] View Course Roster")
            print(" [0] Back to Main Menu")
            choice = input("Select (0-3): ").strip()

            if choice == "1":
                code = input("Course Code (e.g. CS-201): ").strip()
                name = input("Course Title: ").strip()
                instructor = input("Instructor Name: ").strip()
                credits = int(input("Credit Hours [3]: ") or 3)
                sem = input("Semester [Fall 2026]: ").strip() or "Fall 2026"
                try:
                    self.student_mgr.add_course(code, name, instructor, credits, sem)
                    print("[✓] Course added.")
                except Exception as e:
                    print(f"[X] Error: {e}")
            elif choice == "2":
                c_id = input("Enter Course ID: ").strip()
                s_id = input("Enter Student Database ID: ").strip()
                if c_id.isdigit() and s_id.isdigit():
                    self.student_mgr.enroll_student(int(s_id), int(c_id))
                    print("[✓] Student enrolled.")
            elif choice == "3":
                c_id = input("Enter Course ID: ").strip()
                if c_id.isdigit():
                    roster = self.student_mgr.get_enrolled_students(int(c_id))
                    print(f"\n--- Roster for Course {c_id} ({len(roster)} students) ---")
                    for s in roster:
                        print(f" {s['student_id']}: {s['first_name']} {s['last_name']} ({s['email']})")
                    input("\nPress Enter...")
            elif choice == "0":
                break

    # -------------------------------------------------------------
    # 4. Attendance Tracker
    # -------------------------------------------------------------
    def manage_attendance(self):
        while True:
            self.print_header("ATTENDANCE TRACKER")
            courses = self.student_mgr.list_courses()
            for c in courses:
                print(f" [{c['id']}] {c['course_code']} - {c['course_name']}")
            print(" [0] Back")

            c_choice = input("\nSelect Course ID to manage attendance: ").strip()
            if c_choice == "0":
                break
            if not c_choice.isdigit():
                continue
            course_id = int(c_choice)

            print("\n [1] Take Attendance for a Date")
            print(" [2] Mark All Enrolled Present for a Date")
            print(" [3] View Course Attendance Summary")
            print(" [4] Export Course Attendance (CSV)")
            sub_choice = input("Select (1-4): ").strip()

            att_date = input(f"Enter Attendance Date YYYY-MM-DD [{date.today()}]: ").strip() or str(date.today())

            if sub_choice == "1":
                sheet = self.attendance_mgr.get_attendance_sheet(course_id, att_date)
                if not sheet:
                    print("No students enrolled in this course.")
                    continue
                records = []
                print(f"\nRecording Attendance for {att_date}:")
                print("Options for each student: (P)resent, (A)bsent, (L)ate, (E)xcused")
                for s in sheet:
                    full_name = f"{s['first_name']} {s['last_name']}"
                    current = s['status']
                    prompt = f" {s['student_id']} - {full_name} [{current}]: "
                    val = input(prompt).strip().upper()
                    status_map = {"P": "Present", "A": "Absent", "L": "Late", "E": "Excused"}
                    final_status = status_map.get(val, current if current != "Not Recorded" else "Present")
                    records.append({"student_id": s["student_pk"], "status": final_status, "remarks": ""})
                self.attendance_mgr.batch_mark_attendance(course_id, att_date, records)
                print("[✓] Attendance records updated successfully.")

            elif sub_choice == "2":
                count = self.attendance_mgr.mark_all_present(course_id, att_date)
                print(f"[✓] Successfully marked all {count} enrolled students as Present for {att_date}.")

            elif sub_choice == "3":
                summary = self.attendance_mgr.get_course_attendance_summary(course_id)
                print(f"\n{'Student ID':<12} | {'Name':<22} | {'Present':<8} | {'Late':<6} | {'Absent':<8} | {'Attnd %'}")
                print("-" * 72)
                for r in summary:
                    print(f"{r['student_id']:<12} | {r['student_name']:<22} | {r['present_count']:<8} | {r['late_count']:<6} | {r['absent_count']:<8} | {r['attendance_percentage']}%")
                input("\nPress Enter to continue...")

            elif sub_choice == "4":
                filename = f"attendance_course_{course_id}.csv"
                self.report_svc.export_attendance_csv(course_id, filename)
                print(f"[✓] Exported to {os.path.abspath(filename)}")

    # -------------------------------------------------------------
    # 5. Academics & Gradebook
    # -------------------------------------------------------------
    def manage_academics(self):
        while True:
            self.print_header("ACADEMIC ASSESSMENTS & GRADEBOOK")
            courses = self.student_mgr.list_courses()
            for c in courses:
                print(f" [{c['id']}] {c['course_code']} - {c['course_name']}")
            print(" [0] Back")

            c_choice = input("\nSelect Course ID: ").strip()
            if c_choice == "0":
                break
            if not c_choice.isdigit():
                continue
            course_id = int(c_choice)

            assessments = self.academic_mgr.get_assessments_by_course(course_id)
            print(f"\n--- Assessments for Course {course_id} ---")
            if assessments:
                for a in assessments:
                    print(f" [{a['id']}] {a['title']} ({a['assessment_type']}) - Max: {a['max_marks']}, Weight: {a['weight_percentage']}%")
            else:
                print(" No assessments defined yet.")

            print("\n [1] Create New Assessment")
            print(" [2] Enter / Edit Grades for an Assessment")
            print(" [3] View Assessment Analytics")
            print(" [4] Export Gradebook (CSV)")
            print(" [0] Back")

            sub_choice = input("Select (0-4): ").strip()
            if sub_choice == "1":
                title = input("Assessment Title (e.g. Quiz 2): ").strip()
                atype = input("Type (Quiz/Assignment/Midterm/Final Exam/Project): ").strip() or "Quiz"
                max_m = float(input("Maximum Marks [100.0]: ") or 100.0)
                weight = float(input("Weight Percentage [20.0]: ") or 20.0)
                due = input(f"Due Date YYYY-MM-DD [{date.today()}]: ").strip() or str(date.today())
                self.academic_mgr.create_assessment(course_id, title, atype, max_m, weight, due)
                print("[✓] Assessment created.")

            elif sub_choice == "2":
                asm_id = input("Enter Assessment ID: ").strip()
                if not asm_id.isdigit():
                    continue
                asm = self.academic_mgr.get_assessment_by_id(int(asm_id))
                if not asm:
                    print("Assessment not found.")
                    continue
                gradebook = self.academic_mgr.get_assessment_gradebook(int(asm_id))
                print(f"\nGrading '{asm['title']}' (Max Marks: {asm['max_marks']})")
                for g in gradebook:
                    cur = g['marks_obtained']
                    val = input(f" {g['student_id']} - {g['student_name']} (Current: {cur}): ").strip()
                    if val != "":
                        try:
                            score = float(val)
                            fb = input(" Feedback (optional): ").strip()
                            self.academic_mgr.record_grade(int(asm_id), g["student_pk"], score, fb)
                        except Exception as e:
                            print(f"[X] Error: {e}")
                print("[✓] Grades saved.")

            elif sub_choice == "3":
                analytics = self.academic_mgr.get_course_academic_analytics(course_id)
                print("\n--- Assessment Analytics ---")
                for a in analytics["assessments"]:
                    print(f" {a['title']}: Submissions={a['submission_count']}, Avg={a['avg_marks']}/{a['max_marks']} ({a['avg_pct']}%), High={a['highest_marks']}, Low={a['lowest_marks']}")
                input("\nPress Enter...")

            elif sub_choice == "4":
                asm_id = input("Enter Assessment ID to export: ").strip()
                if asm_id.isdigit():
                    fname = f"gradebook_asm_{asm_id}.csv"
                    self.report_svc.export_gradebook_csv(int(asm_id), fname)
                    print(f"[✓] Exported to {os.path.abspath(fname)}")

    # -------------------------------------------------------------
    # 6. Report Cards & Transcripts
    # -------------------------------------------------------------
    def show_report_cards(self):
        students = self.student_mgr.list_students()
        self.print_header("STUDENT REPORT CARDS & TRANSCRIPTS")
        for s in students:
            print(f" [{s['id']}] {s['student_id']} - {s['first_name']} {s['last_name']}")
        s_choice = input("\nSelect Student ID to generate transcript: ").strip()
        if not s_choice.isdigit():
            return

        report_txt = self.report_svc.generate_student_report_card_text(int(s_choice))
        print(report_txt)

        save_choice = input("Save transcript to text file? (y/N): ").strip()
        if save_choice.lower() == "y":
            fname = f"report_card_student_{s_choice}.txt"
            with open(fname, "w", encoding="utf-8") as f:
                f.write(report_txt)
            print(f"[✓] Saved transcript to: {os.path.abspath(fname)}")
        input("\nPress Enter to return...")

    # -------------------------------------------------------------
    # 7. Reset / Re-seed Database
    # -------------------------------------------------------------
    def reset_database(self):
        confirm = input("Are you sure you want to re-seed the database with demo data? (y/N): ")
        if confirm.lower() == "y":
            self.db.init_database(seed=True)
            print("[✓] Database initialized and seeded successfully.")


if __name__ == "__main__":
    cli = ClassroomCLI()
    cli.run()
