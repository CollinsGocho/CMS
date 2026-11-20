-- ====================================================================
-- Classroom Management System (CMS) Database Schema
-- SQL Engine: SQLite 3 (Standard Relational SQL)
-- ====================================================================

PRAGMA foreign_keys = ON;

-- --------------------------------------------------------------------
-- 1. Table: students
-- Stores personal and enrollment details of all registered students.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT UNIQUE NOT NULL,            -- e.g. 'STU-1001'
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    gender TEXT CHECK(gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),
    date_of_birth TEXT,                         -- Format: YYYY-MM-DD
    phone TEXT,
    enrollment_date TEXT NOT NULL,              -- Format: YYYY-MM-DD
    status TEXT DEFAULT 'Active' CHECK(status IN ('Active', 'Inactive', 'Suspended', 'Graduated')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------------------
-- 2. Table: courses
-- Represents academic classes/subjects offered in the classroom.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT UNIQUE NOT NULL,          -- e.g. 'CS-101'
    course_name TEXT NOT NULL,                  -- e.g. 'Intro to Computer Science'
    instructor TEXT NOT NULL,                   -- e.g. 'Dr. Alan Turing'
    credit_hours INTEGER DEFAULT 3 CHECK(credit_hours > 0),
    semester TEXT NOT NULL,                     -- e.g. 'Fall 2026'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------------------
-- 3. Table: enrollments
-- Many-to-Many junction table linking students to courses.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrollments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TEXT DEFAULT CURRENT_DATE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id)
);

-- --------------------------------------------------------------------
-- 4. Table: attendance
-- Records daily attendance per student per course.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,             -- Format: YYYY-MM-DD
    status TEXT NOT NULL CHECK(status IN ('Present', 'Absent', 'Late', 'Excused')),
    remarks TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id, attendance_date)
);

-- --------------------------------------------------------------------
-- 5. Table: assessments
-- Academic evaluations (Exams, Quizzes, Assignments, Projects).
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_id INTEGER NOT NULL,
    title TEXT NOT NULL,                        -- e.g. 'Midterm Exam'
    assessment_type TEXT NOT NULL CHECK(assessment_type IN ('Quiz', 'Assignment', 'Midterm', 'Final Exam', 'Project', 'Lab')),
    max_marks REAL NOT NULL CHECK(max_marks > 0),
    weight_percentage REAL NOT NULL DEFAULT 20.0 CHECK(weight_percentage >= 0 AND weight_percentage <= 100),
    due_date TEXT,                              -- Format: YYYY-MM-DD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- --------------------------------------------------------------------
-- 6. Table: grades
-- Academic performance results scored by students on assessments.
-- --------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS grades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    marks_obtained REAL NOT NULL CHECK(marks_obtained >= 0),
    feedback TEXT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE(assessment_id, student_id)
);

-- ====================================================================
-- INDEXES for Query Optimization
-- ====================================================================
CREATE INDEX IF NOT EXISTS idx_students_student_id ON students(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_student ON enrollments(student_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course ON enrollments(course_id);
CREATE INDEX IF NOT EXISTS idx_attendance_lookup ON attendance(student_id, course_id, attendance_date);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(attendance_date);
CREATE INDEX IF NOT EXISTS idx_grades_assessment ON grades(assessment_id);
CREATE INDEX IF NOT EXISTS idx_grades_student ON grades(student_id);

-- ====================================================================
-- VIEWS for Reporting & Analytics
-- ====================================================================

-- View 1: Student Attendance Summary per Course
CREATE VIEW IF NOT EXISTS v_attendance_summary AS
SELECT 
    s.id AS student_pk,
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.id AS course_pk,
    c.course_code,
    c.course_name,
    COUNT(a.id) AS total_sessions,
    SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count,
    SUM(CASE WHEN a.status = 'Late' THEN 1 ELSE 0 END) AS late_count,
    SUM(CASE WHEN a.status = 'Absent' THEN 1 ELSE 0 END) AS absent_count,
    SUM(CASE WHEN a.status = 'Excused' THEN 1 ELSE 0 END) AS excused_count,
    ROUND(
        CASE 
            WHEN COUNT(a.id) = 0 THEN 0.0
            ELSE (
                (SUM(CASE WHEN a.status = 'Present' THEN 1.0 ELSE 0.0 END) + 
                 SUM(CASE WHEN a.status = 'Late' THEN 0.75 ELSE 0.0 END)) 
                / COUNT(a.id) * 100.0
            )
        END, 2
    ) AS attendance_percentage
FROM enrollments e
JOIN students s ON e.student_id = s.id
JOIN courses c ON e.course_id = c.id
LEFT JOIN attendance a ON a.student_id = s.id AND a.course_id = c.id
GROUP BY s.id, c.id;

-- View 2: Student Academic Performance per Assessment
CREATE VIEW IF NOT EXISTS v_assessment_grades AS
SELECT 
    g.id AS grade_id,
    s.id AS student_pk,
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.id AS course_pk,
    c.course_code,
    c.course_name,
    asm.id AS assessment_id,
    asm.title AS assessment_title,
    asm.assessment_type,
    asm.max_marks,
    asm.weight_percentage,
    g.marks_obtained,
    ROUND((g.marks_obtained / asm.max_marks) * 100.0, 2) AS percentage,
    g.feedback,
    g.recorded_at
FROM grades g
JOIN assessments asm ON g.assessment_id = asm.id
JOIN courses c ON asm.course_id = c.id
JOIN students s ON g.student_id = s.id;

-- View 3: Course Academic Aggregates
CREATE VIEW IF NOT EXISTS v_course_stats AS
SELECT 
    asm.course_id,
    c.course_code,
    c.course_name,
    asm.id AS assessment_id,
    asm.title AS assessment_title,
    COUNT(g.id) AS total_submissions,
    ROUND(AVG(g.marks_obtained), 2) AS avg_marks,
    MAX(g.marks_obtained) AS highest_marks,
    MIN(g.marks_obtained) AS lowest_marks,
    ROUND(AVG(g.marks_obtained / asm.max_marks * 100.0), 2) AS avg_percentage
FROM assessments asm
JOIN courses c ON asm.course_id = c.id
LEFT JOIN grades g ON asm.id = g.assessment_id
GROUP BY asm.id;
