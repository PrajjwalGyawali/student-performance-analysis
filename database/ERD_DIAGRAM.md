# Entity Relationship Diagram: 3-Table Schema

**Project:** End-to-End ETL & Academic Performance Pipeline  
**Database:** `database/student_performance.db` (SQLite)  
**Tables:** `students`, `attendance_records`, `academic_assessments`  

> **Note:** The raw Kaggle dataset contains no course, department, or instructor data.
> The `courses` table was removed to preserve analytical honesty.

---

## 1. Visual ERD (Mermaid)

```mermaid
erDiagram
    STUDENTS ||--o{ ATTENDANCE_RECORDS  : "has (1:1 in this dataset)"
    STUDENTS ||--o{ ACADEMIC_ASSESSMENTS : "evaluated_by (1:1 in this dataset)"

    STUDENTS {
        INTEGER student_id    PK "Unique Student Identifier"
        TEXT    first_name       "Student First Name"
        TEXT    last_name        "Student Last Name"
        INTEGER age              "Student Age (16-80)"
        TEXT    age_group        "Tier: 18-19 / 20-22 / 23-25"
        TEXT    gender           "Male / Female / Other"
        REAL    previous_gpa     "Prior Cumulative GPA (0.0-4.0)"
    }

    ATTENDANCE_RECORDS {
        INTEGER attendance_id       PK "Auto-increment PK"
        INTEGER student_id          FK "References students(student_id)"
        INTEGER total_lectures         "Scheduled Lectures (12)"
        INTEGER lectures_attended      "Lectures Attended (0-12)"
        REAL    lecture_attendance_pct "Lecture Compliance %"
        INTEGER total_lab_sessions     "Scheduled Labs (6)"
        INTEGER labs_attended          "Labs Attended (0-6)"
        REAL    lab_attendance_pct     "Lab Compliance %"
        REAL    overall_attendance_pct "Combined Attendance %"
        TEXT    attendance_tier        "Excellent / Satisfactory / Irregular / Critical"
    }

    ACADEMIC_ASSESSMENTS {
        INTEGER assessment_id    PK "Auto-increment PK"
        INTEGER student_id       FK "References students(student_id)"
        REAL    quiz1_marks         "Quiz 1 (0.0-10.0)"
        REAL    quiz2_marks         "Quiz 2 (0.0-10.0)"
        REAL    quiz3_marks         "Quiz 3 (0.0-10.0)"
        REAL    avg_quiz_score      "Average of 3 Quizzes"
        REAL    midterm_marks       "Midterm (0.0-30.0)"
        REAL    final_marks         "Final Exam (0.0-50.0)"
        REAL    composite_score     "Standardized Score (0.0-100.0)"
        TEXT    letter_grade        "A / B / C / D / F"
        TEXT    academic_standing   "Honor List / Good Standing / Warning / Probation"
        TEXT    dropout_risk        "Rule-based label: Low / Medium / High Risk"
    }
```

---

## 2. Relational Integrity & Constraint Catalog

| Table | Constraint | Expression | Purpose |
|-------|-----------|------------|---------|
| `students` | Primary Key | `student_id` | Unique student identification |
| `students` | CHECK | `age BETWEEN 16 AND 80` | Realistic age bounds |
| `students` | CHECK | `gender IN ('Male','Female','Other')` | Categorical consistency |
| `students` | CHECK | `previous_gpa BETWEEN 0.0 AND 4.0` | Standard GPA scale |
| `attendance_records` | Primary Key | `attendance_id` (AUTOINCREMENT) | Unique attendance log |
| `attendance_records` | Foreign Key | `student_id → students(student_id) ON DELETE CASCADE` | Referential integrity |
| `attendance_records` | CHECK | `lectures_attended <= total_lectures` | Cannot exceed scheduled count |
| `attendance_records` | CHECK | `attendance_tier IN (...)` | Controlled vocabulary |
| `academic_assessments` | Primary Key | `assessment_id` (AUTOINCREMENT) | Unique assessment record |
| `academic_assessments` | Foreign Key | `student_id → students(student_id) ON DELETE CASCADE` | Referential integrity |
| `academic_assessments` | CHECK | `quiz*_marks BETWEEN 0.0 AND 10.0` | Valid quiz score range |
| `academic_assessments` | CHECK | `midterm_marks BETWEEN 0.0 AND 30.0` | Valid midterm range |
| `academic_assessments` | CHECK | `final_marks BETWEEN 0.0 AND 50.0` | Valid final range |
| `academic_assessments` | CHECK | `composite_score BETWEEN 0.0 AND 100.0` | Normalized score |
| `academic_assessments` | CHECK | `dropout_risk IN ('Low Risk','Medium Risk','High Risk')` | Controlled label set |

---

## 3. Dropout Risk Label Definition

`dropout_risk` is assigned in `src/transform.py` by this rule:

| Label | Condition (ANY of) |
|-------|-------------------|
| `High Risk` | `overall_attendance_pct < 40` OR `composite_score < 45` OR `previous_gpa < 1.8` |
| `Medium Risk` | `overall_attendance_pct < 65` OR `composite_score < 60` (and not High Risk) |
| `Low Risk` | All other students |

This is **not** observed dropout data. It is a pedagogical classification label.
