-- ====================================================================
-- Classroom Management System (CMS) Seed Data
-- ====================================================================

-- 1. Insert Sample Students
INSERT OR IGNORE INTO students (id, student_id, first_name, last_name, email, gender, date_of_birth, phone, enrollment_date, status) VALUES
(1, 'STU-1001', 'Alice', 'Johnson', 'alice.johnson@school.edu', 'Female', '2005-04-12', '+1-555-0101', '2026-09-01', 'Active'),
(2, 'STU-1002', 'Brian', 'Smith', 'brian.smith@school.edu', 'Male', '2004-11-23', '+1-555-0102', '2026-09-01', 'Active'),
(3, 'STU-1003', 'Chloe', 'Davis', 'chloe.davis@school.edu', 'Female', '2005-02-18', '+1-555-0103', '2026-09-01', 'Active'),
(4, 'STU-1004', 'David', 'Miller', 'david.miller@school.edu', 'Male', '2005-07-30', '+1-555-0104', '2026-09-01', 'Active'),
(5, 'STU-1005', 'Emma', 'Wilson', 'emma.wilson@school.edu', 'Female', '2004-09-15', '+1-555-0105', '2026-09-01', 'Active'),
(6, 'STU-1006', 'Felix', 'Brown', 'felix.brown@school.edu', 'Male', '2005-01-20', '+1-555-0106', '2026-09-01', 'Active'),
(7, 'STU-1007', 'Grace', 'Taylor', 'grace.taylor@school.edu', 'Female', '2005-08-08', '+1-555-0107', '2026-09-01', 'Active'),
(8, 'STU-1008', 'Henry', 'Anderson', 'henry.anderson@school.edu', 'Male', '2004-12-05', '+1-555-0108', '2026-09-01', 'Active');

-- 2. Insert Sample Courses
INSERT OR IGNORE INTO courses (id, course_code, course_name, instructor, credit_hours, semester) VALUES
(1, 'CS-101', 'Intro to Computer Science', 'Dr. Alan Turing', 4, 'Fall 2026'),
(2, 'MATH-201', 'Calculus & Linear Algebra', 'Prof. Katherine Johnson', 4, 'Fall 2026'),
(3, 'ENG-102', 'Technical Writing & Communication', 'Dr. Maya Angelou', 3, 'Fall 2026'),
(4, 'PHY-101', 'Classical Mechanics & Physics', 'Prof. Richard Feynman', 4, 'Fall 2026');

-- 3. Enroll Students into Courses
-- All students enrolled in CS-101 and MATH-201
INSERT OR IGNORE INTO enrollments (student_id, course_id, enrolled_at) VALUES
(1, 1, '2026-09-01'), (2, 1, '2026-09-01'), (3, 1, '2026-09-01'), (4, 1, '2026-09-01'),
(5, 1, '2026-09-01'), (6, 1, '2026-09-01'), (7, 1, '2026-09-01'), (8, 1, '2026-09-01'),
(1, 2, '2026-09-01'), (2, 2, '2026-09-01'), (3, 2, '2026-09-01'), (4, 2, '2026-09-01'),
(5, 2, '2026-09-01'), (6, 2, '2026-09-01'), (7, 2, '2026-09-01'), (8, 2, '2026-09-01'),
-- Subset in ENG-102
(1, 3, '2026-09-01'), (3, 3, '2026-09-01'), (5, 3, '2026-09-01'), (7, 3, '2026-09-01'),
-- Subset in PHY-101
(2, 4, '2026-09-01'), (4, 4, '2026-09-01'), (6, 4, '2026-09-01'), (8, 4, '2026-09-01');

-- 4. Sample Attendance Records for CS-101 across several dates
INSERT OR IGNORE INTO attendance (student_id, course_id, attendance_date, status, remarks) VALUES
-- Day 1: 2026-11-03
(1, 1, '2026-11-03', 'Present', 'On time'),
(2, 1, '2026-11-03', 'Present', 'On time'),
(3, 1, '2026-11-03', 'Present', 'On time'),
(4, 1, '2026-11-03', 'Late', 'Arrived 10 mins late'),
(5, 1, '2026-11-03', 'Present', 'On time'),
(6, 1, '2026-11-03', 'Absent', 'Unexcused absence'),
(7, 1, '2026-11-03', 'Present', 'On time'),
(8, 1, '2026-11-03', 'Present', 'On time'),

-- Day 2: 2026-11-05
(1, 1, '2026-11-05', 'Present', 'Active participant'),
(2, 1, '2026-11-05', 'Present', 'On time'),
(3, 1, '2026-11-05', 'Present', 'On time'),
(4, 1, '2026-11-05', 'Present', 'On time'),
(5, 1, '2026-11-05', 'Late', 'Traffic delay'),
(6, 1, '2026-11-05', 'Absent', 'No note'),
(7, 1, '2026-11-05', 'Present', 'On time'),
(8, 1, '2026-11-05', 'Present', 'On time'),

-- Day 3: 2026-11-10
(1, 1, '2026-11-10', 'Present', 'On time'),
(2, 1, '2026-11-10', 'Late', 'Bus delay'),
(3, 1, '2026-11-10', 'Present', 'On time'),
(4, 1, '2026-11-10', 'Present', 'On time'),
(5, 1, '2026-11-10', 'Present', 'On time'),
(6, 1, '2026-11-10', 'Excused', 'Doctor appointment'),
(7, 1, '2026-11-10', 'Present', 'On time'),
(8, 1, '2026-11-10', 'Present', 'On time'),

-- Day 4: 2026-11-12
(1, 1, '2026-11-12', 'Present', 'On time'),
(2, 1, '2026-11-12', 'Present', 'On time'),
(3, 1, '2026-11-12', 'Present', 'On time'),
(4, 1, '2026-11-12', 'Present', 'On time'),
(5, 1, '2026-11-12', 'Present', 'On time'),
(6, 1, '2026-11-12', 'Absent', 'Repeated absence'),
(7, 1, '2026-11-12', 'Present', 'On time'),
(8, 1, '2026-11-12', 'Late', '5 mins late');

-- Attendance records for MATH-201
INSERT OR IGNORE INTO attendance (student_id, course_id, attendance_date, status, remarks) VALUES
(1, 2, '2026-11-04', 'Present', 'On time'),
(2, 2, '2026-11-04', 'Present', 'On time'),
(3, 2, '2026-11-04', 'Present', 'On time'),
(4, 2, '2026-11-04', 'Present', 'On time'),
(5, 2, '2026-11-04', 'Present', 'On time'),
(6, 2, '2026-11-04', 'Late', 'Late'),
(7, 2, '2026-11-04', 'Present', 'On time'),
(8, 2, '2026-11-04', 'Present', 'On time'),

(1, 2, '2026-11-11', 'Present', 'On time'),
(2, 2, '2026-11-11', 'Absent', 'Sick'),
(3, 2, '2026-11-11', 'Present', 'On time'),
(4, 2, '2026-11-11', 'Present', 'On time'),
(5, 2, '2026-11-11', 'Present', 'On time'),
(6, 2, '2026-11-11', 'Present', 'On time'),
(7, 2, '2026-11-11', 'Present', 'On time'),
(8, 2, '2026-11-11', 'Present', 'On time');

-- 5. Insert Sample Assessments
INSERT OR IGNORE INTO assessments (id, course_id, title, assessment_type, max_marks, weight_percentage, due_date) VALUES
-- CS-101 Assessments (Total 100%)
(1, 1, 'Assignment 1: Python Basics', 'Assignment', 50.0, 15.0, '2026-09-20'),
(2, 1, 'Quiz 1: Data Structures', 'Quiz', 30.0, 10.0, '2026-10-10'),
(3, 1, 'Midterm Exam: Algorithms', 'Midterm', 100.0, 30.0, '2026-10-25'),
(4, 1, 'Term Project: Software System', 'Project', 100.0, 25.0, '2026-11-15'),
(5, 1, 'Final Exam: Comprehensive', 'Final Exam', 100.0, 20.0, '2026-12-10'),

-- MATH-201 Assessments
(6, 2, 'Problem Set 1: Derivatives', 'Assignment', 50.0, 20.0, '2026-09-25'),
(7, 2, 'Midterm Exam: Linear Systems', 'Midterm', 100.0, 40.0, '2026-10-28'),
(8, 2, 'Final Exam: Calculus', 'Final Exam', 100.0, 40.0, '2026-12-12'),

-- ENG-102 Assessments
(9, 3, 'Essay: Scientific Ethics', 'Assignment', 100.0, 40.0, '2026-10-15'),
(10, 3, 'Oral Presentation', 'Project', 100.0, 60.0, '2026-11-20');

-- 6. Insert Grades for CS-101
INSERT OR IGNORE INTO grades (assessment_id, student_id, marks_obtained, feedback) VALUES
-- Assignment 1 (max 50)
(1, 1, 48.5, 'Excellent code structure and comments.'),
(1, 2, 42.0, 'Good effort, minor bug in test case 3.'),
(1, 3, 50.0, 'Flawless execution.'),
(1, 4, 38.0, 'Needs improvement in variable naming.'),
(1, 5, 46.0, 'Very good implementation.'),
(1, 6, 29.0, 'Late submission, missing functions.'),
(1, 7, 49.0, 'Outstanding solution.'),
(1, 8, 44.5, 'Well done.'),

-- Quiz 1 (max 30)
(2, 1, 28.0, 'Great theoretical understanding.'),
(2, 2, 24.0, 'Solid performance.'),
(2, 3, 30.0, 'Perfect score!'),
(2, 4, 21.0, 'Review tree traversal concepts.'),
(2, 5, 27.5, 'Very good.'),
(2, 6, 18.0, 'Struggled with Big-O notation.'),
(2, 7, 29.0, 'Near perfect.'),
(2, 8, 26.0, 'Good grasp of fundamentals.'),

-- Midterm Exam (max 100)
(3, 1, 94.0, 'Top 5% score in class!'),
(3, 2, 81.5, 'Good analytical reasoning.'),
(3, 3, 98.0, 'Highest score in the cohort.'),
(3, 4, 73.0, 'Adequate, practice sorting algorithms.'),
(3, 5, 88.0, 'Strong problem-solving.'),
(3, 6, 58.0, 'Below passing threshold, attend tutoring.'),
(3, 7, 92.5, 'Excellent work.'),
(3, 8, 85.0, 'Solid understanding of all concepts.'),

-- Term Project (max 100)
(4, 1, 95.0, 'Impressive UI and SQL integration.'),
(4, 2, 84.0, 'Good architecture and testing.'),
(4, 3, 97.0, 'Production ready submission.'),
(4, 4, 76.0, 'Meets core requirements.'),
(4, 5, 90.0, 'Clean database design.'),
(4, 6, 62.0, 'Incomplete documentation.'),
(4, 7, 94.0, 'Great presentation.'),
(4, 8, 87.0, 'Well designed schema.');

-- Grades for MATH-201
INSERT OR IGNORE INTO grades (assessment_id, student_id, marks_obtained, feedback) VALUES
(6, 1, 47.0, 'Clear mathematical steps.'),
(6, 2, 39.0, 'Check arithmetic in section 2.'),
(6, 3, 49.0, 'Superb proofs.'),
(6, 4, 35.0, 'Review matrix operations.'),
(6, 5, 45.0, 'Strong calculus principles.'),
(6, 6, 28.0, 'Incomplete calculations.'),
(6, 7, 48.0, 'Exemplary work.'),
(6, 8, 42.0, 'Good work overall.'),

(7, 1, 91.0, 'High distinction performance.'),
(7, 2, 78.0, 'Good, minor errors on eigenvalues.'),
(7, 3, 96.0, 'Exceptional mastery.'),
(7, 4, 71.0, 'Passed comfortably.'),
(7, 5, 86.0, 'Very good analytical proofs.'),
(7, 6, 55.0, 'Needs remedial assistance.'),
(7, 7, 93.0, 'Top tier paper.'),
(7, 8, 80.0, 'Solid result.');
