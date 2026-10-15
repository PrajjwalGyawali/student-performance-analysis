-- ============================================================================
-- End-to-End ETL & Data Analysis Pipeline: Database Schema & Reporting Queries
-- Domain: Education & Student Academic Performance Analytics
-- Database Engine: SQLite / ANSI SQL Compliant
-- Tables: students, attendance_records, academic_assessments (3 tables)
-- NOTE: The raw dataset contains no course, department, or instructor data.
--       The courses table has been removed to preserve analytical integrity.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ----------------------------------------------------------------------------
-- DDL: TABLE CREATION STATEMENTS
-- ----------------------------------------------------------------------------

DROP TABLE IF EXISTS academic_assessments;
DROP TABLE IF EXISTS attendance_records;
DROP TABLE IF EXISTS students;

-- 1. Students Entity
CREATE TABLE students (
    student_id   INTEGER PRIMARY KEY,
    first_name   TEXT    NOT NULL,
    last_name    TEXT    NOT NULL,
    age          INTEGER NOT NULL CHECK (age >= 16 AND age <= 80),
    age_group    TEXT    NOT NULL CHECK (age_group IN ('18-19', '20-22', '23-25')),
    gender       TEXT    NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    previous_gpa REAL    NOT NULL CHECK (previous_gpa >= 0.0 AND previous_gpa <= 4.0)
);

-- 2. Attendance Records Entity
CREATE TABLE attendance_records (
    attendance_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id            INTEGER NOT NULL,
    total_lectures        INTEGER NOT NULL DEFAULT 12,
    lectures_attended     INTEGER NOT NULL CHECK (lectures_attended >= 0 AND lectures_attended <= total_lectures),
    lecture_attendance_pct REAL   NOT NULL,
    total_lab_sessions    INTEGER NOT NULL DEFAULT 6,
    labs_attended         INTEGER NOT NULL CHECK (labs_attended >= 0 AND labs_attended <= total_lab_sessions),
    lab_attendance_pct    REAL    NOT NULL,
    overall_attendance_pct REAL   NOT NULL,
    attendance_tier       TEXT    NOT NULL CHECK (attendance_tier IN ('Excellent', 'Satisfactory', 'Irregular', 'Critical')),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- 3. Academic Assessments Entity
-- NOTE: dropout_risk is a rule-based label defined in transform.py.
--       High Risk = attendance < 40% OR composite < 45 OR previous_gpa < 1.8.
--       It is NOT observed dropout outcome data.
CREATE TABLE academic_assessments (
    assessment_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id       INTEGER NOT NULL,
    quiz1_marks      REAL    NOT NULL CHECK (quiz1_marks  >= 0.0 AND quiz1_marks  <= 10.0),
    quiz2_marks      REAL    NOT NULL CHECK (quiz2_marks  >= 0.0 AND quiz2_marks  <= 10.0),
    quiz3_marks      REAL    NOT NULL CHECK (quiz3_marks  >= 0.0 AND quiz3_marks  <= 10.0),
    avg_quiz_score   REAL    NOT NULL,
    midterm_marks    REAL    NOT NULL CHECK (midterm_marks >= 0.0 AND midterm_marks <= 30.0),
    final_marks      REAL    NOT NULL CHECK (final_marks  >= 0.0 AND final_marks  <= 50.0),
    composite_score  REAL    NOT NULL CHECK (composite_score >= 0.0 AND composite_score <= 100.0),
    letter_grade     TEXT    NOT NULL CHECK (letter_grade IN ('A', 'B', 'C', 'D', 'F')),
    academic_standing TEXT   NOT NULL,
    dropout_risk     TEXT    NOT NULL CHECK (dropout_risk IN ('Low Risk', 'Medium Risk', 'High Risk')),
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
);

-- Optimization Indexes
CREATE INDEX idx_students_gender    ON students(gender);
CREATE INDEX idx_students_age_group ON students(age_group);
CREATE INDEX idx_attendance_tier    ON attendance_records(attendance_tier);
CREATE INDEX idx_assessments_risk   ON academic_assessments(dropout_risk);
CREATE INDEX idx_assessments_grade  ON academic_assessments(letter_grade);


-- ============================================================================
-- PHASE 7: SQL ANALYSIS & REPORTING QUERIES (10 COMPREHENSIVE REPORTS)
-- ============================================================================

-- Query 1: Performance & Risk Breakdown by Attendance Tier (JOIN, GROUP BY, CASE)
-- Purpose: Shows how composite scores and High-Risk rates vary across attendance tiers.
SELECT
    att.attendance_tier,
    COUNT(s.student_id)                                                           AS total_students,
    ROUND(AVG(att.overall_attendance_pct), 2)                                     AS avg_attendance_pct,
    ROUND(AVG(a.composite_score), 2)                                              AS avg_composite_score,
    ROUND(AVG(a.final_marks), 2)                                                  AS avg_final_marks,
    SUM(CASE WHEN a.letter_grade IN ('A', 'B') THEN 1 ELSE 0 END)                AS high_achievers,
    SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)                AS high_risk_count,
    ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)
          / COUNT(s.student_id), 2)                                               AS high_risk_pct
FROM attendance_records att
JOIN students s            ON att.student_id = s.student_id
JOIN academic_assessments a ON att.student_id = a.student_id
GROUP BY att.attendance_tier
ORDER BY avg_composite_score DESC;

-- Query 2: Dropout Risk Distribution by Gender & Age Group (GROUP BY, HAVING)
-- Purpose: Identifies demographic groups with elevated rule-based risk labels.
SELECT
    s.gender,
    s.age_group,
    COUNT(s.student_id)                                                             AS total_students,
    ROUND(AVG(s.previous_gpa), 2)                                                   AS avg_gpa,
    SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)                  AS high_risk_count,
    ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)
          / COUNT(s.student_id), 2)                                                 AS high_risk_pct,
    ROUND(AVG(a.composite_score), 2)                                                AS avg_composite
FROM students s
JOIN academic_assessments a ON s.student_id = a.student_id
GROUP BY s.gender, s.age_group
HAVING COUNT(s.student_id) >= 10
ORDER BY high_risk_pct DESC;

-- Query 3: Dean's Honor List Recognition (Multi-table JOIN, WHERE, ORDER BY)
-- Purpose: Lists students who achieved both >=80% attendance and >=85 composite score.
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name  AS full_name,
    s.gender,
    s.age,
    s.previous_gpa,
    att.overall_attendance_pct,
    a.composite_score,
    a.letter_grade,
    a.academic_standing
FROM students s
JOIN academic_assessments a  ON s.student_id = a.student_id
JOIN attendance_records att  ON s.student_id = att.student_id
WHERE a.academic_standing = "Dean's Honor List"
ORDER BY a.composite_score DESC, att.overall_attendance_pct DESC;

-- Query 4: Quiz Performance Tier vs Examination Outcomes (CASE, GROUP BY, Aggregates)
-- Purpose: Evaluates how continuous quiz scores relate to midterm and final marks.
SELECT
    CASE
        WHEN a.avg_quiz_score >= 8.0 THEN 'High Quiz Tier (>=8.0)'
        WHEN a.avg_quiz_score >= 6.0 THEN 'Mid Quiz Tier (6.0-7.9)'
        WHEN a.avg_quiz_score >= 4.0 THEN 'Developing Quiz Tier (4.0-5.9)'
        ELSE 'Low Quiz Tier (<4.0)'
    END                                       AS quiz_tier,
    COUNT(a.student_id)                       AS student_count,
    ROUND(AVG(a.avg_quiz_score),  2)          AS avg_quiz_score,
    ROUND(AVG(a.midterm_marks),   2)          AS avg_midterm,
    ROUND(AVG(a.final_marks),     2)          AS avg_final,
    ROUND(AVG(a.composite_score), 2)          AS avg_composite
FROM academic_assessments a
GROUP BY quiz_tier
ORDER BY avg_composite DESC;

-- Query 5: Students Scoring Above the Cohort Average Final Mark (Scalar Subquery)
-- Purpose: Identifies students who outperformed the overall average final exam score.
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name          AS student_name,
    s.gender,
    s.age_group,
    a.final_marks,
    ROUND((SELECT AVG(final_marks) FROM academic_assessments), 2) AS cohort_avg_final,
    ROUND(a.final_marks - (SELECT AVG(final_marks) FROM academic_assessments), 2) AS margin_above_avg
FROM academic_assessments a
JOIN students s ON a.student_id = s.student_id
WHERE a.final_marks > (SELECT AVG(final_marks) FROM academic_assessments)
ORDER BY margin_above_avg DESC
LIMIT 15;

-- Query 6: Lab vs Lecture Participation Profile Analysis (CASE, GROUP BY, Aggregates)
-- Purpose: Compares final exam outcomes across four lab/lecture attendance combinations.
SELECT
    CASE
        WHEN att.lab_attendance_pct >= 80.0 AND att.lecture_attendance_pct >= 80.0 THEN 'High Lecture & High Lab'
        WHEN att.lab_attendance_pct <  50.0 AND att.lecture_attendance_pct >= 70.0 THEN 'High Lecture & Low Lab'
        WHEN att.lab_attendance_pct >= 70.0 AND att.lecture_attendance_pct <  50.0 THEN 'Low Lecture & High Lab'
        ELSE 'Balanced / Moderate'
    END                                       AS participation_profile,
    COUNT(s.student_id)                       AS student_count,
    ROUND(AVG(a.final_marks),     2)          AS avg_final_marks,
    ROUND(AVG(a.composite_score), 2)          AS avg_composite,
    ROUND(AVG(s.previous_gpa),    2)          AS avg_gpa
FROM attendance_records att
JOIN academic_assessments a ON att.student_id = a.student_id
JOIN students s              ON att.student_id = s.student_id
GROUP BY participation_profile
ORDER BY avg_composite DESC;

-- Query 7: Early Intervention Roster — High-Risk Students (Multi-condition Filtering)
-- Purpose: Generates an action list for advisors: High Risk students with worst metrics first.
SELECT
    s.student_id,
    s.first_name || ' ' || s.last_name  AS student_name,
    s.gender,
    att.attendance_tier,
    att.overall_attendance_pct,
    a.composite_score,
    a.letter_grade,
    a.dropout_risk
FROM academic_assessments a
JOIN students s             ON a.student_id = s.student_id
JOIN attendance_records att ON a.student_id = att.student_id
WHERE a.dropout_risk = 'High Risk'
  AND (att.overall_attendance_pct < 40.0 OR a.composite_score < 50.0)
ORDER BY a.composite_score ASC, att.overall_attendance_pct ASC
LIMIT 10;

-- Query 8: Top-Ranked Students by Composite Score (CTE, DENSE_RANK window function)
-- Purpose: Ranks all students by composite score and shows the top performers.
WITH RankedStudents AS (
    SELECT
        s.student_id,
        s.first_name || ' ' || s.last_name  AS student_name,
        s.gender,
        s.age_group,
        a.composite_score,
        a.letter_grade,
        DENSE_RANK() OVER (ORDER BY a.composite_score DESC) AS overall_rank
    FROM academic_assessments a
    JOIN students s ON a.student_id = s.student_id
)
SELECT
    overall_rank,
    student_id,
    student_name,
    gender,
    age_group,
    composite_score,
    letter_grade
FROM RankedStudents
WHERE overall_rank <= 10
ORDER BY overall_rank;

-- Query 9: Grade Distribution Percentage Across Cohort (CTE, Window SUM OVER)
-- Purpose: Shows the share of each letter grade across the full student cohort.
WITH GradeBreakdown AS (
    SELECT
        a.letter_grade,
        COUNT(a.student_id)                              AS grade_count,
        SUM(COUNT(a.student_id)) OVER ()                 AS cohort_total
    FROM academic_assessments a
    GROUP BY a.letter_grade
)
SELECT
    letter_grade,
    grade_count,
    cohort_total,
    ROUND(100.0 * grade_count / cohort_total, 2)  AS grade_pct
FROM GradeBreakdown
ORDER BY letter_grade;

-- Query 10: Previous GPA Band vs Current Composite Score (CASE, GROUP BY, HAVING)
-- Purpose: Checks whether incoming GPA bands predict current academic composite scores.
SELECT
    CASE
        WHEN s.previous_gpa >= 3.5 THEN 'High GPA (>=3.5)'
        WHEN s.previous_gpa >= 2.5 THEN 'Mid GPA (2.5-3.4)'
        WHEN s.previous_gpa >= 1.5 THEN 'Low GPA (1.5-2.4)'
        ELSE 'Very Low GPA (<1.5)'
    END                                       AS gpa_band,
    COUNT(s.student_id)                       AS student_count,
    ROUND(AVG(s.previous_gpa),    2)          AS avg_incoming_gpa,
    ROUND(AVG(a.composite_score), 2)          AS avg_composite,
    ROUND(AVG(a.final_marks),     2)          AS avg_final,
    SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count
FROM students s
JOIN academic_assessments a ON s.student_id = a.student_id
GROUP BY gpa_band
HAVING COUNT(s.student_id) >= 5
ORDER BY avg_incoming_gpa DESC;
