-- ============================================================================
-- End-to-End ETL & Data Analysis Pipeline: Database Schema & Reporting Queries
-- Domain: Education & Student Academic Performance Analytics
-- Database Engine: SQLite / ANSI SQL Compliant
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- DDL: TABLE CREATION STATEMENTS
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS academic_assessments;
DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS students;

-- 1. Students Entity
CREATE TABLE students (
    student_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 16 AND age <= 80),
    age_group TEXT NOT NULL CHECK (age_group IN ('18-19', '20-22', '23-25')),
    gender TEXT NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    previous_gpa REAL NOT NULL CHECK (previous_gpa >= 0.0 AND previous_gpa <= 4.0)
);

-- 2. Courses Entity
CREATE TABLE courses (
    course_id INTEGER PRIMARY KEY,
    course_code TEXT NOT NULL UNIQUE,
    course_name TEXT NOT NULL,
    department TEXT NOT NULL,
    credits INTEGER NOT NULL CHECK (credits > 0),
    instructor_name TEXT NOT NULL
);

-- 3. Attendance Records Entity (Relational Bridge & Engagement Metrics)
CREATE TABLE attendance_records (
    attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    total_lectures INTEGER NOT NULL DEFAULT 12,
    lectures_attended INTEGER NOT NULL CHECK (lectures_attended >= 0 AND lectures_attended <= total_lectures),
    lecture_attendance_pct REAL NOT NULL,
    total_lab_sessions INTEGER NOT NULL DEFAULT 6,
    labs_attended INTEGER NOT NULL CHECK (labs_attended >= 0 AND labs_attended <= total_lab_sessions),
    lab_attendance_pct REAL NOT NULL,
    overall_attendance_pct REAL NOT NULL,
    attendance_tier TEXT NOT NULL CHECK (attendance_tier IN ('Excellent', 'Satisfactory', 'Irregular', 'Critical')),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- 4. Academic Assessments Entity (Examinations, Quizzes, Grading & Risk)
CREATE TABLE academic_assessments (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    quiz1_marks REAL NOT NULL CHECK (quiz1_marks >= 0.0 AND quiz1_marks <= 10.0),
    quiz2_marks REAL NOT NULL CHECK (quiz2_marks >= 0.0 AND quiz2_marks <= 10.0),
    quiz3_marks REAL NOT NULL CHECK (quiz3_marks >= 0.0 AND quiz3_marks <= 10.0),
    avg_quiz_score REAL NOT NULL,
    midterm_marks REAL NOT NULL CHECK (midterm_marks >= 0.0 AND midterm_marks <= 30.0),
    final_marks REAL NOT NULL CHECK (final_marks >= 0.0 AND final_marks <= 50.0),
    composite_score REAL NOT NULL CHECK (composite_score >= 0.0 AND composite_score <= 100.0),
    letter_grade TEXT NOT NULL CHECK (letter_grade IN ('A', 'B', 'C', 'D', 'F')),
    academic_standing TEXT NOT NULL,
    dropout_risk TEXT NOT NULL CHECK (dropout_risk IN ('Low Risk', 'Medium Risk', 'High Risk')),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
);

-- Optimization Indexes
CREATE INDEX idx_students_gender ON students(gender);
CREATE INDEX idx_students_age_group ON students(age_group);
CREATE INDEX idx_attendance_tier ON attendance_records(attendance_tier);
CREATE INDEX idx_assessments_risk ON academic_assessments(dropout_risk);
CREATE INDEX idx_assessments_grade ON academic_assessments(letter_grade);


-- ============================================================================
-- PHASE 7: SQL ANALYSIS & REPORTING QUERIES (10 COMPREHENSIVE REPORTS)
-- ============================================================================

-- Query 1: Academic Department Performance Benchmark (JOIN, GROUP BY, Aggregate)
-- Purpose: Evaluates average student scores, pass rates, and attendance by academic department.
SELECT 
    c.department,
    c.course_name,
    COUNT(a.student_id) AS total_enrolled,
    ROUND(AVG(a.midterm_marks), 2) AS avg_midterm_score,
    ROUND(AVG(a.final_marks), 2) AS avg_final_score,
    ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
    ROUND(AVG(att.overall_attendance_pct), 2) AS avg_attendance_pct
FROM courses c
JOIN academic_assessments a ON c.course_id = a.course_id
JOIN attendance_records att ON a.student_id = att.student_id AND a.course_id = att.course_id
GROUP BY c.department, c.course_name
ORDER BY avg_composite_score DESC;

-- Query 2: Performance & Academic Standing Breakdown by Attendance Tier (JOIN, GROUP BY)
-- Purpose: Demonstrates the relationship between attendance tiers and final course outcomes.
SELECT 
    att.attendance_tier,
    COUNT(s.student_id) AS total_students,
    ROUND(AVG(att.overall_attendance_pct), 2) AS avg_attendance_rate,
    ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
    SUM(CASE WHEN a.letter_grade IN ('A', 'B') THEN 1 ELSE 0 END) AS high_achievers_count,
    SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count,
    ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) / COUNT(s.student_id), 2) AS high_risk_percentage
FROM attendance_records att
JOIN students s ON att.student_id = s.student_id
JOIN academic_assessments a ON s.student_id = a.student_id
GROUP BY att.attendance_tier
ORDER BY avg_composite_score DESC;

-- Query 3: Dean's Honor List Recognition (JOIN, WHERE, Complex Filtering)
-- Purpose: Identifies top-performing students qualifying for academic honors.
SELECT 
    s.student_id,
    s.first_name || ' ' || s.last_name AS full_name,
    s.gender,
    c.course_code,
    s.previous_gpa,
    att.overall_attendance_pct,
    a.composite_score,
    a.letter_grade,
    a.academic_standing
FROM students s
JOIN academic_assessments a ON s.student_id = a.student_id
JOIN attendance_records att ON s.student_id = att.student_id
JOIN courses c ON a.course_id = c.course_id
WHERE a.academic_standing = "Dean's Honor List"
ORDER BY a.composite_score DESC, att.overall_attendance_pct DESC;

-- Query 4: Dropout Risk Analysis by Demographics (GROUP BY, CASE Statement)
-- Purpose: Identifies which demographic groups are at elevated risk of course failure.
SELECT 
    s.gender,
    s.age_group,
    COUNT(s.student_id) AS total_students,
    ROUND(AVG(s.previous_gpa), 2) AS avg_incoming_gpa,
    SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count,
    ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) / COUNT(s.student_id), 2) AS high_risk_pct,
    ROUND(AVG(a.composite_score), 2) AS cohort_avg_score
FROM students s
JOIN academic_assessments a ON s.student_id = a.student_id
GROUP BY s.gender, s.age_group
HAVING COUNT(s.student_id) >= 10
ORDER BY high_risk_pct DESC;

-- Query 5: Students Performing Above Department Average (Subquery / Scalar Subquery)
-- Purpose: Finds students whose final exam score exceeds the cohort average in their respective course.
SELECT 
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_code,
    a.final_marks,
    ROUND((SELECT AVG(final_marks) FROM academic_assessments WHERE course_id = a.course_id), 2) AS course_avg_final,
    ROUND(a.final_marks - (SELECT AVG(final_marks) FROM academic_assessments WHERE course_id = a.course_id), 2) AS score_margin
FROM academic_assessments a
JOIN students s ON a.student_id = s.student_id
JOIN courses c ON a.course_id = c.course_id
WHERE a.final_marks > (
    SELECT AVG(sub.final_marks)
    FROM academic_assessments sub
    WHERE sub.course_id = a.course_id
)
ORDER BY score_margin DESC
LIMIT 15;

-- Query 6: Continuous Assessment (Quiz Tiers) vs Examination Performance (CASE, Aggregates)
-- Purpose: Evaluates how continuous quiz mastery correlates with midterm and final examination outcomes.
SELECT 
    CASE 
        WHEN a.avg_quiz_score >= 8.0 THEN 'High Quiz Tier (>=8.0)'
        WHEN a.avg_quiz_score >= 6.0 THEN 'Mid Quiz Tier (6.0-7.9)'
        WHEN a.avg_quiz_score >= 4.0 THEN 'Developing Quiz Tier (4.0-5.9)'
        ELSE 'Low Quiz Tier (<4.0)'
    END AS quiz_performance_tier,
    COUNT(a.student_id) AS student_count,
    ROUND(AVG(a.avg_quiz_score), 2) AS avg_quiz_grade,
    ROUND(AVG(a.midterm_marks), 2) AS avg_midterm_marks,
    ROUND(AVG(a.final_marks), 2) AS avg_final_marks,
    ROUND(AVG(a.composite_score), 2) AS avg_composite_score
FROM academic_assessments a
GROUP BY quiz_performance_tier
ORDER BY avg_composite_score DESC;

-- Query 7: Student Cohort Ranking within Department (Window Function: DENSE_RANK)
-- Purpose: Computes intra-department class rank based on composite academic score.
WITH RankedStudents AS (
    SELECT 
        c.department,
        s.student_id,
        s.first_name || ' ' || s.last_name AS student_name,
        a.composite_score,
        a.letter_grade,
        DENSE_RANK() OVER (PARTITION BY c.department ORDER BY a.composite_score DESC) AS dept_rank
    FROM academic_assessments a
    JOIN students s ON a.student_id = s.student_id
    JOIN courses c ON a.course_id = c.course_id
)
SELECT 
    department,
    dept_rank,
    student_id,
    student_name,
    composite_score,
    letter_grade
FROM RankedStudents
WHERE dept_rank <= 3
ORDER BY department, dept_rank;

-- Query 8: Lab Attendance Gap Impact Analysis (CASE & Aggregate Functions)
-- Purpose: Isolates students with high lecture attendance but poor lab attendance vs vice-versa.
SELECT 
    CASE 
        WHEN att.lab_attendance_pct >= 80.0 AND att.lecture_attendance_pct >= 80.0 THEN 'High Lecture & High Lab'
        WHEN att.lab_attendance_pct < 50.0 AND att.lecture_attendance_pct >= 70.0 THEN 'High Lecture & Low Lab'
        WHEN att.lab_attendance_pct >= 70.0 AND att.lecture_attendance_pct < 50.0 THEN 'Low Lecture & High Lab'
        ELSE 'Balanced / Moderate'
    END AS participation_profile,
    COUNT(s.student_id) AS student_count,
    ROUND(AVG(a.final_marks), 2) AS avg_final_marks,
    ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
    ROUND(AVG(s.previous_gpa), 2) AS avg_previous_gpa
FROM attendance_records att
JOIN academic_assessments a ON att.student_id = a.student_id
JOIN students s ON att.student_id = s.student_id
GROUP BY participation_profile
ORDER BY avg_composite_score DESC;

-- Query 9: Academic Warning List - Interventions Required (Multi-condition Filtering)
-- Purpose: Generates an action report for academic advisors listing students requiring immediate intervention.
SELECT 
    s.student_id,
    s.first_name || ' ' || s.last_name AS student_name,
    c.course_name,
    att.attendance_tier,
    att.overall_attendance_pct,
    a.composite_score,
    a.letter_grade,
    a.dropout_risk
FROM academic_assessments a
JOIN students s ON a.student_id = s.student_id
JOIN courses c ON a.course_id = c.course_id
JOIN attendance_records att ON a.student_id = att.student_id
WHERE a.dropout_risk = 'High Risk'
  AND (att.overall_attendance_pct < 40.0 OR a.composite_score < 50.0)
ORDER BY a.composite_score ASC, att.overall_attendance_pct ASC
LIMIT 10;

-- Query 10: Cumulative Grade Distribution Percentage by Course (Common Table Expression - CTE)
-- Purpose: Evaluates grading equity and percentage share of letter grades per course offering.
WITH GradeBreakdown AS (
    SELECT 
        c.course_code,
        a.letter_grade,
        COUNT(a.student_id) AS grade_count,
        SUM(COUNT(a.student_id)) OVER (PARTITION BY c.course_code) AS course_total
    FROM academic_assessments a
    JOIN courses c ON a.course_id = c.course_id
    GROUP BY c.course_code, a.letter_grade
)
SELECT 
    course_code,
    letter_grade,
    grade_count,
    course_total,
    ROUND(100.0 * grade_count / course_total, 2) AS grade_percentage
FROM GradeBreakdown
ORDER BY course_code, letter_grade;
