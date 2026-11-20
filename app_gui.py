"""
Classroom Management System (CMS) - Graphical User Interface (GUI)
Modern Tkinter / ttk desktop application with tabs for Dashboard, Students,
Courses, Attendance Tracking, Academics & Gradebook, and Report Cards.
"""

from datetime import date
import os
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Any, Dict, List, Optional
from academic_manager import AcademicManager
from attendance_manager import AttendanceManager
from database import db
from reports import ReportService
from student_manager import StudentManager


class ClassroomGUI:
    """Main desktop application window for CMS."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Classroom Management System (CMS)")
        self.root.geometry("1150x750")
        self.root.minsize(980, 650)

        # Initialize backend services
        self.db = db
        self.db.init_database(seed=True)
        self.student_mgr = StudentManager(self.db)
        self.attendance_mgr = AttendanceManager(self.db)
        self.academic_mgr = AcademicManager(self.db)
        self.report_svc = ReportService(self.db)

        # Apply modern theme styling
        self._setup_styles()

        # Build UI layout
        self._build_header()
        self._build_tabs()

        # Load initial dashboard data
        self.refresh_dashboard()

    # -------------------------------------------------------------
    # Styling & Visual Design
    # -------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        # Colors
        self.c_primary = "#1e3a8a"      # Navy Blue
        self.c_secondary = "#2563eb"    # Accent Blue
        self.c_bg = "#f8fafc"           # Light slate
        self.c_card_bg = "#ffffff"
        self.c_text = "#0f172a"
        self.c_muted = "#64748b"

        self.root.configure(bg=self.c_bg)

        # Style configurations
        style.configure(".", font=("Segoe UI", 10))
        style.configure("TNotebook", background=self.c_bg)
        style.configure("TNotebook.Tab", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", self.c_secondary)])

        style.configure("Treeview", rowheight=28, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), padding=[6, 4])
        style.map("Treeview", background=[("selected", "#dbeafe")], foreground=[("selected", "#1e3a8a")])

        style.configure("Primary.TButton", font=("Segoe UI", 9, "bold"), background=self.c_secondary, foreground="#ffffff", padding=[10, 5])
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=self.c_primary, height=64)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text="🎓 Classroom Management System",
            font=("Segoe UI", 16, "bold"),
            bg=self.c_primary,
            fg="#ffffff",
            padx=20,
            pady=12,
        )
        title_label.pack(side=tk.LEFT)

        subtitle_label = tk.Label(
            header_frame,
            text="Student Attendance & Academic Records Tracker",
            font=("Segoe UI", 10, "italic"),
            bg=self.c_primary,
            fg="#cbd5e1",
            pady=16,
        )
        subtitle_label.pack(side=tk.LEFT)

        btn_reseed = tk.Button(
            header_frame,
            text="↺ Reset / Seed Demo Data",
            font=("Segoe UI", 9),
            bg="#334155",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=4,
            command=self._confirm_reseed,
        )
        btn_reseed.pack(side=tk.RIGHT, padx=20)

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # 1. Dashboard Tab
        self.tab_dashboard = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dashboard, text=" 📊 Dashboard ")
        self._init_dashboard_tab()

        # 2. Students Tab
        self.tab_students = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_students, text=" 👥 Students ")
        self._init_students_tab()

        # 3. Courses Tab
        self.tab_courses = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_courses, text=" 📚 Courses & Roster ")
        self._init_courses_tab()

        # 4. Attendance Tab
        self.tab_attendance = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_attendance, text=" 📅 Attendance Tracker ")
        self._init_attendance_tab()

        # 5. Academics Tab
        self.tab_academics = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_academics, text=" 📝 Academics & Grades ")
        self._init_academics_tab()

        # 6. Report Cards Tab
        self.tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reports, text=" 📜 Report Cards & Transcripts ")
        self._init_reports_tab()

        # Refresh tab on selection
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _on_tab_changed(self, event):
        selected_idx = self.notebook.index(self.notebook.select())
        if selected_idx == 0:
            self.refresh_dashboard()
        elif selected_idx == 1:
            self.refresh_students_list()
        elif selected_idx == 2:
            self.refresh_courses_list()
        elif selected_idx == 3:
            self.refresh_attendance_dropdowns()
        elif selected_idx == 4:
            self.refresh_academics_dropdowns()
        elif selected_idx == 5:
            self.refresh_reports_dropdown()

    # =============================================================
    # TAB 1: DASHBOARD
    # =============================================================
    def _init_dashboard_tab(self):
        frame = self.tab_dashboard

        # KPI Metrics Cards Container
        cards_frame = tk.Frame(frame, bg=self.c_bg)
        cards_frame.pack(fill=tk.X, padx=16, pady=16)

        # 4 Cards
        self.card_students = self._create_kpi_card(cards_frame, "ACTIVE STUDENTS", "0", "#0284c7")
        self.card_courses = self._create_kpi_card(cards_frame, "COURSES / SUBJECTS", "0", "#6366f1")
        self.card_attendance = self._create_kpi_card(cards_frame, "AVG ATTENDANCE RATE", "0.0%", "#10b981")
        self.card_academics = self._create_kpi_card(cards_frame, "AVG ACADEMIC SCORE", "0.0%", "#f59e0b")

        self.card_students.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        self.card_courses.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        self.card_attendance.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)
        self.card_academics.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        # Alerts & Overview split
        middle_frame = tk.Frame(frame, bg=self.c_bg)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=10)

        # Left: Low Attendance Warnings (< 75%)
        alert_box = tk.LabelFrame(
            middle_frame,
            text=" ⚠️ Attendance Alerts (Students < 75% Attendance) ",
            font=("Segoe UI", 10, "bold"),
            fg="#dc2626",
            bg="#ffffff",
            padx=10,
            pady=10,
        )
        alert_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        columns = ("student_id", "name", "course", "att_rate")
        self.tree_alerts = ttk.Treeview(alert_box, columns=columns, show="headings", height=8)
        self.tree_alerts.heading("student_id", text="Student ID")
        self.tree_alerts.heading("name", text="Student Name")
        self.tree_alerts.heading("course", text="Course")
        self.tree_alerts.heading("att_rate", text="Attendance %")

        self.tree_alerts.column("student_id", width=100)
        self.tree_alerts.column("name", width=160)
        self.tree_alerts.column("course", width=90)
        self.tree_alerts.column("att_rate", width=100, anchor=tk.CENTER)
        self.tree_alerts.pack(fill=tk.BOTH, expand=True)

        # Right: Quick Launch shortcuts
        quick_box = tk.LabelFrame(
            middle_frame,
            text=" ⚡ Quick Actions ",
            font=("Segoe UI", 10, "bold"),
            fg=self.c_text,
            bg="#ffffff",
            padx=15,
            pady=15,
        )
        quick_box.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(8, 0), ipadx=20)

        actions = [
            ("➕ Register New Student", lambda: self.notebook.select(1)),
            ("📅 Mark Today's Attendance", lambda: self.notebook.select(3)),
            ("📝 Enter Assessment Marks", lambda: self.notebook.select(4)),
            ("📜 View Official Transcripts", lambda: self.notebook.select(5)),
        ]
        for text, cmd in actions:
            btn = tk.Button(
                quick_box,
                text=text,
                font=("Segoe UI", 10),
                bg="#f1f5f9",
                fg=self.c_text,
                activebackground="#e2e8f0",
                relief=tk.GROOVE,
                pady=8,
                command=cmd,
            )
            btn.pack(fill=tk.X, pady=6)

    def _create_kpi_card(self, parent, title: str, initial_value: str, accent_color: str):
        card = tk.Frame(parent, bg="#ffffff", bd=1, relief=tk.SOLID, highlightbackground="#e2e8f0")
        
        # Color accent strip
        strip = tk.Frame(card, bg=accent_color, height=4)
        strip.pack(fill=tk.X, side=tk.TOP)

        lbl_title = tk.Label(card, text=title, font=("Segoe UI", 8, "bold"), fg=self.c_muted, bg="#ffffff", pady=8)
        lbl_title.pack()

        lbl_val = tk.Label(card, text=initial_value, font=("Segoe UI", 20, "bold"), fg=self.c_text, bg="#ffffff")
        lbl_val.pack(pady=(0, 10))
        card.val_label = lbl_val  # type: ignore
        return card

    def refresh_dashboard(self):
        stats = self.student_mgr.get_dashboard_summary()
        self.card_students.val_label.config(text=str(stats["total_students"]))  # type: ignore
        self.card_courses.val_label.config(text=str(stats["total_courses"]))  # type: ignore
        self.card_attendance.val_label.config(text=f"{stats['overall_attendance_rate']}%")  # type: ignore
        self.card_academics.val_label.config(text=f"{stats['overall_academic_avg']}%")  # type: ignore

        # Populate alerts tree
        for item in self.tree_alerts.get_children():
            self.tree_alerts.delete(item)

        warnings = stats["low_attendance_warnings"]
        for w in warnings:
            self.tree_alerts.insert(
                "",
                tk.END,
                values=(
                    w["student_id"],
                    w["student_name"],
                    w["course_code"],
                    f"{w['attendance_percentage']}%",
                ),
            )

    # =============================================================
    # TAB 2: STUDENTS MANAGEMENT
    # =============================================================
    def _init_students_tab(self):
        frame = self.tab_students

        # Top Control Bar (Search & Buttons)
        top_bar = tk.Frame(frame, bg=self.c_bg)
        top_bar.pack(fill=tk.X, padx=16, pady=10)

        tk.Label(top_bar, text="Search:", font=("Segoe UI", 10, "bold"), bg=self.c_bg).pack(side=tk.LEFT)
        self.student_search_var = tk.StringVar()
        self.student_search_var.trace_add("write", lambda *args: self.refresh_students_list())
        search_entry = ttk.Entry(top_bar, textvariable=self.student_search_var, width=28)
        search_entry.pack(side=tk.LEFT, padx=8)

        # Action Buttons
        btn_add = tk.Button(top_bar, text="➕ Add Student", bg="#16a34a", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=4, command=self._dialog_add_student)
        btn_add.pack(side=tk.RIGHT, padx=4)

        btn_edit = tk.Button(top_bar, text="✏️ Edit Selected", bg="#2563eb", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=4, command=self._dialog_edit_student)
        btn_edit.pack(side=tk.RIGHT, padx=4)

        btn_del = tk.Button(top_bar, text="🗑️ Delete", bg="#dc2626", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=4, command=self._delete_selected_student)
        btn_del.pack(side=tk.RIGHT, padx=4)

        btn_export = tk.Button(top_bar, text="📥 Export CSV", bg="#475569", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=4, command=self._export_students_csv)
        btn_export.pack(side=tk.RIGHT, padx=4)

        # Students Treeview
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        columns = ("id", "student_id", "name", "email", "gender", "dob", "phone", "enrolled", "status")
        self.tree_students = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_students.heading("id", text="PK")
        self.tree_students.heading("student_id", text="Student ID")
        self.tree_students.heading("name", text="Full Name")
        self.tree_students.heading("email", text="Email")
        self.tree_students.heading("gender", text="Gender")
        self.tree_students.heading("dob", text="DOB")
        self.tree_students.heading("phone", text="Phone")
        self.tree_students.heading("enrolled", text="Enrolled")
        self.tree_students.heading("status", text="Status")

        self.tree_students.column("id", width=40, anchor=tk.CENTER)
        self.tree_students.column("student_id", width=95, anchor=tk.CENTER)
        self.tree_students.column("name", width=150)
        self.tree_students.column("email", width=180)
        self.tree_students.column("gender", width=80, anchor=tk.CENTER)
        self.tree_students.column("dob", width=95, anchor=tk.CENTER)
        self.tree_students.column("phone", width=110)
        self.tree_students.column("enrolled", width=95, anchor=tk.CENTER)
        self.tree_students.column("status", width=80, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree_students.yview)
        self.tree_students.configure(yscrollcommand=scrollbar.set)
        self.tree_students.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_students_list(self):
        for item in self.tree_students.get_children():
            self.tree_students.delete(item)

        query = self.student_search_var.get().strip()
        students = self.student_mgr.list_students(search_query=query if query else None)
        for s in students:
            full_name = f"{s['first_name']} {s['last_name']}"
            self.tree_students.insert(
                "",
                tk.END,
                values=(
                    s["id"],
                    s["student_id"],
                    full_name,
                    s["email"],
                    s["gender"] or "-",
                    s["date_of_birth"] or "-",
                    s["phone"] or "-",
                    s["enrollment_date"],
                    s["status"],
                ),
            )

    def _dialog_add_student(self):
        self._show_student_form_dialog("Add New Student")

    def _dialog_edit_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student from the list to edit.")
            return
        student_pk = int(self.tree_students.item(selected[0])["values"][0])
        student_data = self.student_mgr.get_student_by_id(student_pk)
        if student_data:
            self._show_student_form_dialog("Edit Student Details", student_data)

    def _show_student_form_dialog(self, title: str, student: Optional[Dict[str, Any]] = None):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("450x520")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        fields = [
            ("Student ID (e.g. STU-1009):", "student_id", student["student_id"] if student else ""),
            ("First Name:", "first_name", student["first_name"] if student else ""),
            ("Last Name:", "last_name", student["last_name"] if student else ""),
            ("Email Address:", "email", student["email"] if student else ""),
            ("Date of Birth (YYYY-MM-DD):", "dob", student.get("date_of_birth") or "" if student else "2005-01-01"),
            ("Phone Number:", "phone", student.get("phone") or "" if student else "+1-555-0199"),
            ("Enrollment Date:", "enroll", student["enrollment_date"] if student else str(date.today())),
        ]

        entries = {}
        for idx, (label_txt, key, def_val) in enumerate(fields):
            lbl = tk.Label(dlg, text=label_txt, font=("Segoe UI", 9, "bold"))
            lbl.pack(anchor=tk.W, padx=25, pady=(8, 2))
            ent = ttk.Entry(dlg, width=40)
            ent.insert(0, def_val)
            ent.pack(padx=25, pady=(0, 4))
            entries[key] = ent

        # Gender & Status
        lbl_g = tk.Label(dlg, text="Gender:", font=("Segoe UI", 9, "bold"))
        lbl_g.pack(anchor=tk.W, padx=25, pady=(8, 2))
        combo_gender = ttk.Combobox(dlg, values=["Male", "Female", "Other", "Prefer not to say"], state="readonly", width=38)
        combo_gender.set(student.get("gender") or "Prefer not to say" if student else "Prefer not to say")
        combo_gender.pack(padx=25, pady=(0, 4))

        def save():
            try:
                sid = entries["student_id"].get().strip()
                fn = entries["first_name"].get().strip()
                ln = entries["last_name"].get().strip()
                em = entries["email"].get().strip()
                en_date = entries["enroll"].get().strip()

                if not (sid and fn and ln and em and en_date):
                    messagebox.showerror("Validation Error", "Please fill in all required fields (ID, Name, Email, Enrollment Date).", parent=dlg)
                    return

                if student:
                    self.student_mgr.update_student(
                        pk=student["id"],
                        student_id=sid,
                        first_name=fn,
                        last_name=ln,
                        email=em,
                        enrollment_date=en_date,
                        gender=combo_gender.get(),
                        date_of_birth=entries["dob"].get().strip() or None,
                        phone=entries["phone"].get().strip() or None,
                    )
                else:
                    self.student_mgr.add_student(
                        student_id=sid,
                        first_name=fn,
                        last_name=ln,
                        email=em,
                        enrollment_date=en_date,
                        gender=combo_gender.get(),
                        date_of_birth=entries["dob"].get().strip() or None,
                        phone=entries["phone"].get().strip() or None,
                    )
                self.refresh_students_list()
                dlg.destroy()
                messagebox.showinfo("Success", "Student record saved successfully!")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to save student: {ex}", parent=dlg)

        btn_save = tk.Button(dlg, text="💾 Save Student", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6, command=save)
        btn_save.pack(fill=tk.X, padx=25, pady=16)

    def _delete_selected_student(self):
        selected = self.tree_students.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student to delete.")
            return
        values = self.tree_students.item(selected[0])["values"]
        student_pk = int(values[0])
        student_code = values[1]
        student_name = values[2]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {student_code} ({student_name})?\nAll attendance and grade history for this student will be permanently removed."):
            self.student_mgr.delete_student(student_pk)
            self.refresh_students_list()
            self.refresh_dashboard()
            messagebox.showinfo("Deleted", "Student successfully deleted.")

    def _export_students_csv(self):
        path = os.path.join(os.path.dirname(__file__), "students_export.csv")
        self.report_svc.export_students_csv(path)
        messagebox.showinfo("Export Successful", f"Students exported to:\n{os.path.abspath(path)}")

    # =============================================================
    # TAB 3: COURSES & ROSTER
    # =============================================================
    def _init_courses_tab(self):
        frame = self.tab_courses

        # Split: Left Courses, Right Roster
        split_frame = tk.Frame(frame, bg=self.c_bg)
        split_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=12)

        # Left: Courses
        left_box = tk.LabelFrame(split_frame, text=" 📚 Courses / Subjects ", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=10, pady=10)
        left_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        c_top = tk.Frame(left_box, bg="#ffffff")
        c_top.pack(fill=tk.X, pady=(0, 8))
        tk.Button(c_top, text="➕ Add Course", bg="#16a34a", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=8, pady=3, command=self._dialog_add_course).pack(side=tk.RIGHT)

        cols_c = ("id", "code", "name", "instructor", "credits", "enrolled")
        self.tree_courses = ttk.Treeview(left_box, columns=cols_c, show="headings", selectmode="browse")
        self.tree_courses.heading("id", text="ID")
        self.tree_courses.heading("code", text="Code")
        self.tree_courses.heading("name", text="Course Title")
        self.tree_courses.heading("instructor", text="Instructor")
        self.tree_courses.heading("credits", text="Credits")
        self.tree_courses.heading("enrolled", text="Enrolled")

        self.tree_courses.column("id", width=35, anchor=tk.CENTER)
        self.tree_courses.column("code", width=75)
        self.tree_courses.column("name", width=140)
        self.tree_courses.column("instructor", width=120)
        self.tree_courses.column("credits", width=55, anchor=tk.CENTER)
        self.tree_courses.column("enrolled", width=65, anchor=tk.CENTER)

        self.tree_courses.pack(fill=tk.BOTH, expand=True)
        self.tree_courses.bind("<<TreeviewSelect>>", self._on_course_selected)

        # Right: Enrolled Students Roster
        right_box = tk.LabelFrame(split_frame, text=" 📋 Course Class Roster ", font=("Segoe UI", 10, "bold"), bg="#ffffff", padx=10, pady=10)
        right_box.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        r_top = tk.Frame(right_box, bg="#ffffff")
        r_top.pack(fill=tk.X, pady=(0, 8))
        tk.Button(r_top, text="➕ Enroll Student", bg="#2563eb", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=8, pady=3, command=self._dialog_enroll_student).pack(side=tk.LEFT)
        tk.Button(r_top, text="➖ Remove Student", bg="#dc2626", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=8, pady=3, command=self._unenroll_student).pack(side=tk.RIGHT)

        cols_r = ("student_pk", "code", "name", "email", "enrolled_at")
        self.tree_roster = ttk.Treeview(right_box, columns=cols_r, show="headings", selectmode="browse")
        self.tree_roster.heading("student_pk", text="PK")
        self.tree_roster.heading("code", text="Student ID")
        self.tree_roster.heading("name", text="Student Name")
        self.tree_roster.heading("email", text="Email")
        self.tree_roster.heading("enrolled_at", text="Enrolled Date")

        self.tree_roster.column("student_pk", width=35, anchor=tk.CENTER)
        self.tree_roster.column("code", width=85)
        self.tree_roster.column("name", width=130)
        self.tree_roster.column("email", width=160)
        self.tree_roster.column("enrolled_at", width=90, anchor=tk.CENTER)
        self.tree_roster.pack(fill=tk.BOTH, expand=True)

    def refresh_courses_list(self):
        for item in self.tree_courses.get_children():
            self.tree_courses.delete(item)

        courses = self.student_mgr.list_courses()
        for c in courses:
            self.tree_courses.insert(
                "",
                tk.END,
                values=(
                    c["id"],
                    c["course_code"],
                    c["course_name"],
                    c["instructor"],
                    c["credit_hours"],
                    c["enrolled_count"],
                ),
            )

    def _on_course_selected(self, event):
        selected = self.tree_courses.selection()
        if not selected:
            return
        course_id = int(self.tree_courses.item(selected[0])["values"][0])
        self._refresh_roster(course_id)

    def _refresh_roster(self, course_id: int):
        for item in self.tree_roster.get_children():
            self.tree_roster.delete(item)
        roster = self.student_mgr.get_enrolled_students(course_id)
        for s in roster:
            name = f"{s['first_name']} {s['last_name']}"
            self.tree_roster.insert("", tk.END, values=(s["student_pk"], s["student_id"], name, s["email"], s["enrolled_at"]))

    def _dialog_add_course(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Add New Course")
        dlg.geometry("400x380")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        fields = [
            ("Course Code (e.g. CS-201):", "code", ""),
            ("Course Title:", "title", ""),
            ("Instructor Name:", "instructor", ""),
            ("Credit Hours:", "credits", "3"),
            ("Semester:", "semester", "Fall 2026"),
        ]
        entries = {}
        for lbl_txt, key, def_val in fields:
            tk.Label(dlg, text=lbl_txt, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=25, pady=(8, 2))
            ent = ttk.Entry(dlg, width=35)
            ent.insert(0, def_val)
            ent.pack(padx=25, pady=(0, 4))
            entries[key] = ent

        def save():
            try:
                c_code = entries["code"].get().strip()
                c_title = entries["title"].get().strip()
                c_inst = entries["instructor"].get().strip()
                c_credits = int(entries["credits"].get().strip())
                c_sem = entries["semester"].get().strip()

                if not (c_code and c_title and c_inst):
                    messagebox.showerror("Validation Error", "All fields are required.", parent=dlg)
                    return
                self.student_mgr.add_course(c_code, c_title, c_inst, c_credits, c_sem)
                self.refresh_courses_list()
                dlg.destroy()
                messagebox.showinfo("Success", "Course created successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Could not create course: {e}", parent=dlg)

        tk.Button(dlg, text="💾 Save Course", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6, command=save).pack(fill=tk.X, padx=25, pady=16)

    def _dialog_enroll_student(self):
        selected_course = self.tree_courses.selection()
        if not selected_course:
            messagebox.showwarning("Select Course", "Please select a course on the left first.")
            return
        course_id = int(self.tree_courses.item(selected_course[0])["values"][0])
        course_name = self.tree_courses.item(selected_course[0])["values"][2]

        all_students = self.student_mgr.list_students()
        enrolled_ids = {s["student_pk"] for s in self.student_mgr.get_enrolled_students(course_id)}
        not_enrolled = [s for s in all_students if s["id"] not in enrolled_ids]

        if not not_enrolled:
            messagebox.showinfo("All Enrolled", "All active students are already enrolled in this course.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Enroll Student - {course_name}")
        dlg.geometry("400x200")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text="Select Student to Enroll:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, padx=25, pady=(20, 8))
        choices = [f"{s['id']}: {s['student_id']} - {s['first_name']} {s['last_name']}" for s in not_enrolled]
        combo = ttk.Combobox(dlg, values=choices, state="readonly", width=38)
        combo.current(0)
        combo.pack(padx=25, pady=(0, 15))

        def confirm_enroll():
            selected_str = combo.get()
            s_pk = int(selected_str.split(":")[0])
            self.student_mgr.enroll_student(s_pk, course_id)
            self._refresh_roster(course_id)
            self.refresh_courses_list()
            dlg.destroy()
            messagebox.showinfo("Enrolled", "Student enrolled successfully.")

        tk.Button(dlg, text="Enroll Now", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=5, command=confirm_enroll).pack(fill=tk.X, padx=25)

    def _unenroll_student(self):
        selected_course = self.tree_courses.selection()
        selected_roster = self.tree_roster.selection()
        if not (selected_course and selected_roster):
            messagebox.showwarning("Selection Required", "Select both a course and a student from the roster.")
            return
        course_id = int(self.tree_courses.item(selected_course[0])["values"][0])
        student_pk = int(self.tree_roster.item(selected_roster[0])["values"][0])
        student_name = self.tree_roster.item(selected_roster[0])["values"][2]

        if messagebox.askyesno("Unenroll", f"Remove {student_name} from this course?"):
            self.student_mgr.unenroll_student(student_pk, course_id)
            self._refresh_roster(course_id)
            self.refresh_courses_list()

    # =============================================================
    # TAB 4: ATTENDANCE TRACKER
    # =============================================================
    def _init_attendance_tab(self):
        frame = self.tab_attendance

        # Filter bar: Course, Date, Action buttons
        filter_bar = tk.Frame(frame, bg="#ffffff", bd=1, relief=tk.SOLID, highlightbackground="#e2e8f0")
        filter_bar.pack(fill=tk.X, padx=16, pady=12)

        inner = tk.Frame(filter_bar, bg="#ffffff", padx=12, pady=10)
        inner.pack(fill=tk.X)

        tk.Label(inner, text="Course:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_att_course = ttk.Combobox(inner, state="readonly", width=25)
        self.combo_att_course.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_att_course.bind("<<ComboboxSelected>>", lambda e: self.load_attendance_sheet())

        tk.Label(inner, text="Date (YYYY-MM-DD):", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.att_date_var = tk.StringVar(value=str(date.today()))
        ent_date = ttk.Entry(inner, textvariable=self.att_date_var, width=14)
        ent_date.pack(side=tk.LEFT, padx=(0, 15))

        btn_load = tk.Button(inner, text="🔄 Load Sheet", bg="#2563eb", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=3, command=self.load_attendance_sheet)
        btn_load.pack(side=tk.LEFT, padx=(0, 8))

        btn_all_present = tk.Button(inner, text="✓ Mark All Present", bg="#16a34a", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=3, command=self._mark_all_present)
        btn_all_present.pack(side=tk.LEFT, padx=(0, 8))

        btn_save = tk.Button(inner, text="💾 Save Attendance", bg="#0f766e", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=12, pady=3, command=self._save_attendance_sheet)
        btn_save.pack(side=tk.RIGHT, padx=4)

        btn_export = tk.Button(inner, text="📥 Export CSV", bg="#475569", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=3, command=self._export_attendance_csv)
        btn_export.pack(side=tk.RIGHT, padx=4)

        # Interactive Attendance Sheet
        sheet_frame = tk.Frame(frame)
        sheet_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        cols = ("student_pk", "code", "name", "status", "remarks")
        self.tree_attendance = ttk.Treeview(sheet_frame, columns=cols, show="headings", selectmode="browse")
        self.tree_attendance.heading("student_pk", text="PK")
        self.tree_attendance.heading("code", text="Student ID")
        self.tree_attendance.heading("name", text="Student Name")
        self.tree_attendance.heading("status", text="Attendance Status (Double-Click or Click Below to Change)")
        self.tree_attendance.heading("remarks", text="Remarks / Notes")

        self.tree_attendance.column("student_pk", width=40, anchor=tk.CENTER)
        self.tree_attendance.column("code", width=100, anchor=tk.CENTER)
        self.tree_attendance.column("name", width=180)
        self.tree_attendance.column("status", width=180, anchor=tk.CENTER)
        self.tree_attendance.column("remarks", width=250)

        self.tree_attendance.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_attendance.bind("<Double-1>", self._on_attendance_row_double_click)

        # Quick Status Toggle Bar below table
        toggle_bar = tk.Frame(frame, bg=self.c_bg)
        toggle_bar.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Label(toggle_bar, text="Set Selected Student Status to:", font=("Segoe UI", 9, "bold"), bg=self.c_bg).pack(side=tk.LEFT, padx=(0, 8))
        for status, color in [("Present", "#16a34a"), ("Late", "#d97706"), ("Absent", "#dc2626"), ("Excused", "#6366f1")]:
            btn = tk.Button(
                toggle_bar,
                text=status,
                bg=color,
                fg="#ffffff",
                font=("Segoe UI", 9, "bold"),
                relief=tk.FLAT,
                padx=10,
                pady=2,
                command=lambda s=status: self._set_selected_student_status(s),
            )
            btn.pack(side=tk.LEFT, padx=4)

    def refresh_attendance_dropdowns(self):
        courses = self.student_mgr.list_courses()
        self.att_course_lookup = {f"{c['course_code']} - {c['course_name']}": c["id"] for c in courses}
        course_names = list(self.att_course_lookup.keys())
        self.combo_att_course["values"] = course_names
        if course_names and not self.combo_att_course.get():
            self.combo_att_course.current(0)
            self.load_attendance_sheet()

    def _get_current_att_course_id(self) -> Optional[int]:
        txt = self.combo_att_course.get()
        return self.att_course_lookup.get(txt)

    def load_attendance_sheet(self):
        course_id = self._get_current_att_course_id()
        if not course_id:
            return
        att_date = self.att_date_var.get().strip()

        for item in self.tree_attendance.get_children():
            self.tree_attendance.delete(item)

        sheet = self.attendance_mgr.get_attendance_sheet(course_id, att_date)
        for s in sheet:
            name = f"{s['first_name']} {s['last_name']}"
            self.tree_attendance.insert(
                "",
                tk.END,
                values=(
                    s["student_pk"],
                    s["student_id"],
                    name,
                    s["status"],
                    s["remarks"],
                ),
            )

    def _set_selected_student_status(self, new_status: str):
        selected = self.tree_attendance.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student row from the table first.")
            return
        for item in selected:
            vals = list(self.tree_attendance.item(item)["values"])
            vals[3] = new_status
            self.tree_attendance.item(item, values=vals)

    def _on_attendance_row_double_click(self, event):
        selected = self.tree_attendance.selection()
        if not selected:
            return
        # Cycle through statuses: Present -> Late -> Absent -> Excused -> Present
        cycle = {"Present": "Late", "Late": "Absent", "Absent": "Excused", "Excused": "Present", "Not Recorded": "Present"}
        item = selected[0]
        vals = list(self.tree_attendance.item(item)["values"])
        cur = vals[3]
        vals[3] = cycle.get(cur, "Present")
        self.tree_attendance.item(item, values=vals)

    def _mark_all_present(self):
        for item in self.tree_attendance.get_children():
            vals = list(self.tree_attendance.item(item)["values"])
            vals[3] = "Present"
            self.tree_attendance.item(item, values=vals)

    def _save_attendance_sheet(self):
        course_id = self._get_current_att_course_id()
        if not course_id:
            messagebox.showerror("Error", "Please select a course.")
            return
        att_date = self.att_date_var.get().strip()
        records = []
        for item in self.tree_attendance.get_children():
            vals = self.tree_attendance.item(item)["values"]
            student_pk = int(vals[0])
            status = str(vals[3])
            remarks = str(vals[4]) if len(vals) > 4 else ""
            if status != "Not Recorded":
                records.append({"student_id": student_pk, "status": status, "remarks": remarks})

        if not records:
            messagebox.showinfo("No Records", "No records to save.")
            return

        self.attendance_mgr.batch_mark_attendance(course_id, att_date, records)
        self.refresh_dashboard()
        messagebox.showinfo("Saved", f"Successfully recorded attendance for {len(records)} students on {att_date}!")

    def _export_attendance_csv(self):
        course_id = self._get_current_att_course_id()
        if not course_id:
            return
        fname = os.path.join(os.path.dirname(__file__), f"attendance_course_{course_id}.csv")
        self.report_svc.export_attendance_csv(course_id, fname)
        messagebox.showinfo("Exported", f"Attendance summary exported to:\n{os.path.abspath(fname)}")

    # =============================================================
    # TAB 5: ACADEMICS & GRADEBOOK
    # =============================================================
    def _init_academics_tab(self):
        frame = self.tab_academics

        # Control Panel: Course Dropdown, Assessment Dropdown, Action buttons
        ctrl_frame = tk.Frame(frame, bg="#ffffff", bd=1, relief=tk.SOLID, highlightbackground="#e2e8f0")
        ctrl_frame.pack(fill=tk.X, padx=16, pady=12)

        inner = tk.Frame(ctrl_frame, bg="#ffffff", padx=12, pady=10)
        inner.pack(fill=tk.X)

        tk.Label(inner, text="Course:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_acad_course = ttk.Combobox(inner, state="readonly", width=24)
        self.combo_acad_course.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_acad_course.bind("<<ComboboxSelected>>", self._on_academic_course_changed)

        tk.Label(inner, text="Assessment:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 4))
        self.combo_acad_assessment = ttk.Combobox(inner, state="readonly", width=28)
        self.combo_acad_assessment.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_acad_assessment.bind("<<ComboboxSelected>>", lambda e: self.load_gradebook())

        btn_add_asm = tk.Button(inner, text="➕ Create Assessment", bg="#16a34a", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=3, command=self._dialog_create_assessment)
        btn_add_asm.pack(side=tk.LEFT, padx=(0, 8))

        btn_grade = tk.Button(inner, text="✏️ Enter/Edit Grade", bg="#2563eb", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=3, command=self._dialog_enter_grade)
        btn_grade.pack(side=tk.LEFT, padx=(0, 8))

        btn_export = tk.Button(inner, text="📥 Export CSV", bg="#475569", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=3, command=self._export_gradebook_csv)
        btn_export.pack(side=tk.RIGHT, padx=4)

        # Assessment Stats Ribbon
        self.stat_ribbon = tk.Label(frame, text="Select an assessment to view grade statistics.", font=("Segoe UI", 9, "italic"), bg="#e2e8f0", fg=self.c_text, pady=6)
        self.stat_ribbon.pack(fill=tk.X, padx=16, pady=(0, 8))

        # Gradebook Table
        tree_frame = tk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        cols = ("student_pk", "code", "name", "marks", "max_marks", "percentage", "letter", "feedback")
        self.tree_grades = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")

        self.tree_grades.heading("student_pk", text="PK")
        self.tree_grades.heading("code", text="Student ID")
        self.tree_grades.heading("name", text="Student Name")
        self.tree_grades.heading("marks", text="Score Obtained")
        self.tree_grades.heading("max_marks", text="Max Marks")
        self.tree_grades.heading("percentage", text="Percentage %")
        self.tree_grades.heading("letter", text="Letter Grade")
        self.tree_grades.heading("feedback", text="Instructor Feedback")

        self.tree_grades.column("student_pk", width=35, anchor=tk.CENTER)
        self.tree_grades.column("code", width=90, anchor=tk.CENTER)
        self.tree_grades.column("name", width=160)
        self.tree_grades.column("marks", width=100, anchor=tk.CENTER)
        self.tree_grades.column("max_marks", width=80, anchor=tk.CENTER)
        self.tree_grades.column("percentage", width=95, anchor=tk.CENTER)
        self.tree_grades.column("letter", width=85, anchor=tk.CENTER)
        self.tree_grades.column("feedback", width=240)

        self.tree_grades.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.tree_grades.bind("<Double-1>", lambda e: self._dialog_enter_grade())

    def refresh_academics_dropdowns(self):
        courses = self.student_mgr.list_courses()
        self.acad_course_lookup = {f"{c['course_code']} - {c['course_name']}": c["id"] for c in courses}
        course_names = list(self.acad_course_lookup.keys())
        self.combo_acad_course["values"] = course_names
        if course_names and not self.combo_acad_course.get():
            self.combo_acad_course.current(0)
            self._on_academic_course_changed(None)

    def _on_academic_course_changed(self, event):
        course_str = self.combo_acad_course.get()
        course_id = self.acad_course_lookup.get(course_str)
        if not course_id:
            return
        assessments = self.academic_mgr.get_assessments_by_course(course_id)
        self.acad_asm_lookup = {f"[{a['id']}] {a['title']} ({a['assessment_type']})": a["id"] for a in assessments}
        asm_names = list(self.acad_asm_lookup.keys())
        self.combo_acad_assessment["values"] = asm_names
        if asm_names:
            self.combo_acad_assessment.current(0)
            self.load_gradebook()
        else:
            self.combo_acad_assessment.set("")
            for item in self.tree_grades.get_children():
                self.tree_grades.delete(item)
            self.stat_ribbon.config(text="No assessments found for this course. Click 'Create Assessment' above.")

    def _get_current_assessment_id(self) -> Optional[int]:
        txt = self.combo_acad_assessment.get()
        return self.acad_asm_lookup.get(txt)

    def load_gradebook(self):
        asm_id = self._get_current_assessment_id()
        if not asm_id:
            return

        for item in self.tree_grades.get_children():
            self.tree_grades.delete(item)

        gradebook = self.academic_mgr.get_assessment_gradebook(asm_id)
        scores = [g["marks_obtained"] for g in gradebook if g["marks_obtained"] is not None]

        for g in gradebook:
            marks_str = str(g["marks_obtained"]) if g["marks_obtained"] is not None else "Not Graded"
            pct_str = f"{g['percentage']}%" if g["marks_obtained"] is not None else "-"
            self.tree_grades.insert(
                "",
                tk.END,
                values=(
                    g["student_pk"],
                    g["student_id"],
                    g["student_name"],
                    marks_str,
                    g["max_marks"],
                    pct_str,
                    g["letter_grade"],
                    g["feedback"] or "",
                ),
            )

        if scores:
            avg_score = round(sum(scores) / len(scores), 2)
            high_score = max(scores)
            low_score = min(scores)
            asm_info = self.academic_mgr.get_assessment_by_id(asm_id)
            max_m = asm_info["max_marks"] if asm_info else 100.0
            avg_pct = round((avg_score / max_m) * 100, 1)
            self.stat_ribbon.config(
                text=f"📊 Submissions: {len(scores)}/{len(gradebook)} | Class Average: {avg_score}/{max_m} ({avg_pct}%) | Highest: {high_score} | Lowest: {low_score}"
            )
        else:
            self.stat_ribbon.config(text="No submissions scored yet for this assessment.")

    def _dialog_create_assessment(self):
        course_str = self.combo_acad_course.get()
        course_id = self.acad_course_lookup.get(course_str)
        if not course_id:
            messagebox.showwarning("Course Required", "Select a course first.")
            return

        dlg = tk.Toplevel(self.root)
        dlg.title("Create New Assessment")
        dlg.geometry("400x420")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        fields = [
            ("Assessment Title (e.g. Midterm 2):", "title", ""),
            ("Maximum Marks:", "max_marks", "100.0"),
            ("Grade Weight % (e.g. 20):", "weight", "20.0"),
            ("Due Date (YYYY-MM-DD):", "due_date", str(date.today())),
        ]
        entries = {}
        for lbl_txt, key, def_val in fields:
            tk.Label(dlg, text=lbl_txt, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=25, pady=(8, 2))
            ent = ttk.Entry(dlg, width=35)
            ent.insert(0, def_val)
            ent.pack(padx=25, pady=(0, 4))
            entries[key] = ent

        tk.Label(dlg, text="Assessment Type:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=25, pady=(8, 2))
        combo_type = ttk.Combobox(dlg, values=["Quiz", "Assignment", "Midterm", "Final Exam", "Project", "Lab"], state="readonly", width=33)
        combo_type.current(0)
        combo_type.pack(padx=25, pady=(0, 15))

        def save():
            try:
                title = entries["title"].get().strip()
                max_m = float(entries["max_marks"].get().strip())
                weight = float(entries["weight"].get().strip())
                due = entries["due_date"].get().strip() or None
                atype = combo_type.get()

                if not title:
                    messagebox.showerror("Error", "Title cannot be empty.", parent=dlg)
                    return

                new_id = self.academic_mgr.create_assessment(course_id, title, atype, max_m, weight, due)
                self._on_academic_course_changed(None)
                # Select the new assessment
                for idx, val in enumerate(self.combo_acad_assessment["values"]):
                    if f"[{new_id}]" in val:
                        self.combo_acad_assessment.current(idx)
                        self.load_gradebook()
                        break
                dlg.destroy()
                messagebox.showinfo("Success", "Assessment created!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}", parent=dlg)

        tk.Button(dlg, text="💾 Create Assessment", bg="#16a34a", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6, command=save).pack(fill=tk.X, padx=25)

    def _dialog_enter_grade(self):
        selected = self.tree_grades.selection()
        if not selected:
            messagebox.showwarning("Select Student", "Please select a student from the gradebook table.")
            return

        asm_id = self._get_current_assessment_id()
        if not asm_id:
            return

        asm = self.academic_mgr.get_assessment_by_id(asm_id)
        if not asm:
            return

        vals = self.tree_grades.item(selected[0])["values"]
        student_pk = int(vals[0])
        student_code = vals[1]
        student_name = vals[2]
        current_marks = str(vals[3]) if vals[3] != "Not Graded" else ""
        current_feedback = str(vals[7])

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Grade Entry - {student_name}")
        dlg.geometry("400x320")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f"Assessment: {asm['title']}", font=("Segoe UI", 10, "bold"), fg=self.c_primary).pack(pady=(15, 2))
        tk.Label(dlg, text=f"Student: {student_code} - {student_name}", font=("Segoe UI", 10)).pack(pady=(0, 10))

        tk.Label(dlg, text=f"Marks Obtained (Max: {asm['max_marks']}):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=25, pady=(5, 2))
        ent_marks = ttk.Entry(dlg, width=35)
        ent_marks.insert(0, current_marks)
        ent_marks.pack(padx=25, pady=(0, 8))
        ent_marks.focus_set()

        tk.Label(dlg, text="Feedback / Comments:", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W, padx=25, pady=(5, 2))
        ent_fb = ttk.Entry(dlg, width=35)
        ent_fb.insert(0, current_feedback)
        ent_fb.pack(padx=25, pady=(0, 15))

        def save():
            try:
                score = float(ent_marks.get().strip())
                fb = ent_fb.get().strip()
                self.academic_mgr.record_grade(asm_id, student_pk, score, fb)
                self.load_gradebook()
                self.refresh_dashboard()
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to record grade: {e}", parent=dlg)

        tk.Button(dlg, text="💾 Save Grade", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, pady=6, command=save).pack(fill=tk.X, padx=25)

    def _export_gradebook_csv(self):
        asm_id = self._get_current_assessment_id()
        if not asm_id:
            return
        fname = os.path.join(os.path.dirname(__file__), f"gradebook_asm_{asm_id}.csv")
        self.report_svc.export_gradebook_csv(asm_id, fname)
        messagebox.showinfo("Exported", f"Gradebook exported to:\n{os.path.abspath(fname)}")

    # =============================================================
    # TAB 6: REPORT CARDS & TRANSCRIPTS
    # =============================================================
    def _init_reports_tab(self):
        frame = self.tab_reports

        # Top bar: Student selector & action buttons
        top_bar = tk.Frame(frame, bg="#ffffff", bd=1, relief=tk.SOLID, highlightbackground="#e2e8f0")
        top_bar.pack(fill=tk.X, padx=16, pady=12)

        inner = tk.Frame(top_bar, bg="#ffffff", padx=12, pady=10)
        inner.pack(fill=tk.X)

        tk.Label(inner, text="Select Student:", font=("Segoe UI", 9, "bold"), bg="#ffffff").pack(side=tk.LEFT, padx=(0, 6))
        self.combo_report_student = ttk.Combobox(inner, state="readonly", width=35)
        self.combo_report_student.pack(side=tk.LEFT, padx=(0, 15))
        self.combo_report_student.bind("<<ComboboxSelected>>", lambda e: self.generate_transcript_view())

        btn_gen = tk.Button(inner, text="📜 Generate Transcript", bg="#2563eb", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9, "bold"), padx=10, pady=3, command=self.generate_transcript_view)
        btn_gen.pack(side=tk.LEFT, padx=(0, 8))

        btn_save_txt = tk.Button(inner, text="💾 Save as Text File", bg="#16a34a", fg="#ffffff", relief=tk.FLAT, font=("Segoe UI", 9), padx=10, pady=3, command=self._save_transcript_text)
        btn_save_txt.pack(side=tk.RIGHT, padx=4)

        # Text View for Official Transcript
        view_frame = tk.Frame(frame, bg="#ffffff", bd=1, relief=tk.SOLID, highlightbackground="#cbd5e1")
        view_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.txt_transcript = tk.Text(
            view_frame,
            font=("Consolas", 10),
            wrap=tk.WORD,
            bg="#f8fafc",
            fg="#0f172a",
            padx=16,
            pady=16,
            relief=tk.FLAT,
        )
        scroll = ttk.Scrollbar(view_frame, orient=tk.VERTICAL, command=self.txt_transcript.yview)
        self.txt_transcript.configure(yscrollcommand=scroll.set)
        self.txt_transcript.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def refresh_reports_dropdown(self):
        students = self.student_mgr.list_students()
        self.report_student_lookup = {f"{s['student_id']} - {s['first_name']} {s['last_name']}": s["id"] for s in students}
        names = list(self.report_student_lookup.keys())
        self.combo_report_student["values"] = names
        if names and not self.combo_report_student.get():
            self.combo_report_student.current(0)
            self.generate_transcript_view()

    def generate_transcript_view(self):
        txt = self.combo_report_student.get()
        student_id = self.report_student_lookup.get(txt)
        if not student_id:
            return
        report_text = self.report_svc.generate_student_report_card_text(student_id)
        self.txt_transcript.delete("1.0", tk.END)
        self.txt_transcript.insert(tk.END, report_text)

    def _save_transcript_text(self):
        txt = self.combo_report_student.get()
        student_id = self.report_student_lookup.get(txt)
        if not student_id:
            return
        fname = os.path.join(os.path.dirname(__file__), f"transcript_student_{student_id}.txt")
        content = self.txt_transcript.get("1.0", tk.END)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Saved", f"Transcript successfully saved to:\n{os.path.abspath(fname)}")

    def _confirm_reseed(self):
        if messagebox.askyesno("Confirm Reset", "Reset database and restore demo data for all students, courses, attendance, and grades?"):
            self.db.init_database(seed=True)
            self.refresh_dashboard()
            self.refresh_students_list()
            self.refresh_courses_list()
            messagebox.showinfo("Reset Complete", "Database restored with initial seed data.")


def run_gui():
    root = tk.Tk()
    app = ClassroomGUI(root)
    root.mainloop()


if __name__ == "__main__":
    run_gui()
