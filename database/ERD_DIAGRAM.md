# Deliverable 4: Entity Relationship Diagram (ERD) & Schema Specification

**Project:** End-to-End ETL & Academic Performance Pipeline  
**Database Technology:** SQLite / ANSI SQL Compliant  
**Database File:** `database/student_performance.db`  

---

## 1. Visual Entity Relationship Diagram (Mermaid)

```mermaid
erDiagram
    STUDENTS ||--o{ ATTENDANCE_RECORDS : "generates (1:M)"
    STUDENTS ||--o{ ACADEMIC_ASSESSMENTS : "evaluated_by (1:M)"
    COURSES ||--o{ ATTENDANCE_RECORDS : "tracks (1:M)"
    COURSES ||--o{ ACADEMIC_ASSESSMENTS : "grades (1:M)"

    STUDENTS {
        INTEGER student_id PK "Unique Student Identifier"
        TEXT first_name "Student First Name"
        TEXT last_name "Student Last Name"
        INTEGER age "Student Age (16-80)"
        TEXT age_group "Categorical Tier ('18-19', '20-22', '23-25')"
        TEXT gender "Gender ('Male', 'Female', 'Other')"
        REAL previous_gpa "Prior Academic Cumulative GPA (0.0-4.0)"
    }

    COURSES {
        INTEGER course_id PK "Unique Course Identifier"
        TEXT course_code UK "Unique Course Code (e.g. CS101, DS201)"
        TEXT course_name "Full Descriptive Title"
        TEXT department "Academic Faculty / Division"
        INTEGER credits "Credit Weighting (>0)"
        TEXT instructor_name "Lead Faculty Instructor"
    }

    ATTENDANCE_RECORDS {
        INTEGER attendance_id PK "Unique Attendance Log Identifier"
        INTEGER student_id FK "References students(student_id)"
        INTEGER course_id FK "References courses(course_id)"
        INTEGER total_lectures "Total Scheduled Lectures (12)"
        INTEGER lectures_attended "Lectures Attended (0-12)"
        REAL lecture_attendance_pct "Lecture Compliance Percentage"
        INTEGER total_lab_sessions "Total Lab Practicals (6)"
        INTEGER labs_attended "Labs Attended (0-6)"
        REAL lab_attendance_pct "Lab Compliance Percentage"
        REAL overall_attendance_pct "Weighted Overall Attendance %"
        TEXT attendance_tier "Tier ('Excellent', 'Satisfactory', 'Irregular', 'Critical')"
    }

    ACADEMIC_ASSESSMENTS {
        INTEGER assessment_id PK "Unique Assessment Evaluation Identifier"
        INTEGER student_id FK "References students(student_id)"
        INTEGER course_id FK "References courses(course_id)"
        REAL quiz1_marks "Quiz 1 Marks (0.0-10.0)"
        REAL quiz2_marks "Quiz 2 Marks (0.0-10.0)"
        REAL quiz3_marks "Quiz 3 Marks (0.0-10.0)"
        REAL avg_quiz_score "Average of 3 Quizzes (0.0-10.0)"
        REAL midterm_marks "Midterm Examination Marks (0.0-30.0)"
        REAL final_marks "Final Comprehensive Examination Marks (0.0-50.0)"
        REAL composite_score "Standardized Course Grade (0.0-100.0 scale)"
        TEXT letter_grade "Letter Grade ('A', 'B', 'C', 'D', 'F')"
        TEXT academic_standing "Honor tier / Good Standing / Warning / Probation"
        TEXT dropout_risk "Classified Risk ('Low Risk', 'Medium Risk', 'High Risk')"
    }
```

---

## 2. Relational Integrity & Constraint Catalog

| Table | Constraint Type | Constraint Expression / Foreign Target | Purpose |
| :--- | :--- | :--- | :--- |
| `students` | Primary Key | `student_id` | Ensures unique identification of every registered student. |
| `students` | Check | `age >= 16 AND age <= 80` | Enforces realistic collegiate demographic boundaries. |
| `students` | Check | `gender IN ('Male', 'Female', 'Other')` | Enforces categorical consistency. |
| `students` | Check | `previous_gpa >= 0.0 AND previous_gpa <= 4.0` | Restricts GPA to standard collegiate 4.0 scale. |
| `courses` | Primary Key | `course_id` | Guarantees unique primary identification for department courses. |
| `courses` | Unique Key | `course_code` | Eliminates duplicated course codes within the catalog. |
| `attendance_records` | Primary Key | `attendance_id` | Auto-incrementing unique key per attendance entry. |
| `attendance_records` | Foreign Key | `student_id REFERENCES students(student_id) ON DELETE CASCADE` | Prevents orphan attendance rows if a student is removed. |
| `attendance_records` | Foreign Key | `course_id REFERENCES courses(course_id) ON DELETE CASCADE` | Enforces course catalog referential integrity. |
| `academic_assessments` | Primary Key | `assessment_id` | Auto-incrementing unique key per assessment record. |
| `academic_assessments` | Foreign Key | `student_id REFERENCES students(student_id) ON DELETE CASCADE` | Links grades strictly to verified student profiles. |
| `academic_assessments` | Foreign Key | `course_id REFERENCES courses(course_id) ON DELETE CASCADE` | Links grades strictly to verified course offerings. |
| `academic_assessments` | Check | `quiz1_marks BETWEEN 0.0 AND 10.0` | Prevents invalid grading input outside rubric bounds. |
| `academic_assessments` | Check | `composite_score BETWEEN 0.0 AND 100.0` | Bounds normalized score to 100-point collegiate scale. |
