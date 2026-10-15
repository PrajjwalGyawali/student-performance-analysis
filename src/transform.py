"""
Phase 3: Data Cleaning & Transformation Module
Cleans raw data, imputes missing telemetry, engineers academic features,
and normalizes the flat dataset into 3 relational entities:
1. students
2. attendance_records
3. academic_assessments
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def clean_and_transform_data(df_raw: pd.DataFrame) -> dict:
    """
    Cleans raw student dataset and transforms it into 3 normalized relational DataFrames.
    """
    print("=" * 80)
    print("PHASE 3: DATA CLEANING & TRANSFORMATION")
    print("=" * 80)
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = df_raw.copy()
    
    # --- 3.1 Cleaning & Standardizing Strings ---
    # Strip whitespace, collapse repeated spaces, and remove honorific prefixes and suffixes
    # (avoiding .str.title() which damages acronym suffixes like MD, DDS, and numeral II)
    PREFIXES = {"Dr.", "Mr.", "Mrs.", "Ms.", "Miss", "Prof."}
    SUFFIXES = {"II", "III", "IV", "MD", "DDS", "PhD", "DVM", "Jr.", "Sr."}

    def parse_clean_name(raw_name: str):
        clean_text = " ".join(str(raw_name).strip().split())
        tokens = clean_text.split(" ")
        while tokens and tokens[0] in PREFIXES:
            tokens.pop(0)
        while tokens and tokens[-1] in SUFFIXES:
            tokens.pop(-1)
        first = tokens[0] if tokens else ""
        last = " ".join(tokens[1:]) if len(tokens) > 1 else ""
        return first, last

    name_parsed = df["name"].apply(parse_clean_name).tolist()
    df["first_name"] = [p[0] for p in name_parsed]
    df["last_name"] = [p[1] for p in name_parsed]
    df["gender"] = df["gender"].astype(str).str.strip().str.capitalize()
    
    # --- 3.2 Handling Missing Values & Unnecessary Columns ---
    # Rationale: In the raw dataset, 'assignments_submitted' has 300 nulls (100% missing).
    # Rather than inventing data through synthetic imputation, dropping the unobserved column
    # along with the static constant 'total_assignments' ensures analytical integrity.
    df = df.drop(columns=["assignments_submitted", "total_assignments"], errors="ignore")
    print("Handled missing values: Dropped 'assignments_submitted' (100% missing) & 'total_assignments' to preserve data integrity.")
    
    # --- 3.3 Feature Engineering & Academic Calculations ---
    # Quiz scores
    df["avg_quiz_score"] = ((df["quiz1_marks"] + df["quiz2_marks"] + df["quiz3_marks"]) / 3.0).round(2)
    df["total_quiz_score"] = (df["quiz1_marks"] + df["quiz2_marks"] + df["quiz3_marks"]).round(2)
    
    # Attendance percentages
    df["lecture_attendance_pct"] = ((df["lectures_attended"] / df["total_lectures"]) * 100.0).round(2)
    df["lab_attendance_pct"] = ((df["labs_attended"] / df["total_lab_sessions"]) * 100.0).round(2)
    df["overall_attendance_pct"] = (
        ((df["lectures_attended"] + df["labs_attended"]) / 
         (df["total_lectures"] + df["total_lab_sessions"])) * 100.0
    ).round(2)
    
    # Attendance Tier
    def categorize_attendance(pct):
        if pct >= 80.0:
            return "Excellent"
        elif pct >= 60.0:
            return "Satisfactory"
        elif pct >= 40.0:
            return "Irregular"
        else:
            return "Critical"
    df["attendance_tier"] = df["overall_attendance_pct"].apply(categorize_attendance)
    
    # Composite Score (100-point scale: Quizzes=20%, Midterm=30%, Final=50%)
    quiz_weight_20 = (df["total_quiz_score"] / 30.0) * 20.0
    df["composite_score"] = (quiz_weight_20 + df["midterm_marks"] + df["final_marks"]).round(2)
    
    # Letter Grade
    def assign_letter_grade(score):
        if score >= 85.0:
            return "A"
        elif score >= 75.0:
            return "B"
        elif score >= 65.0:
            return "C"
        elif score >= 50.0:
            return "D"
        else:
            return "F"
    df["letter_grade"] = df["composite_score"].apply(assign_letter_grade)
    
    # Academic Standing
    def assign_standing(row):
        score = row["composite_score"]
        att = row["overall_attendance_pct"]
        if score >= 85.0 and att >= 80.0:
            return "Dean's Honor List"
        elif score >= 60.0:
            return "Good Standing"
        elif score >= 50.0:
            return "Academic Warning"
        else:
            return "Academic Probation"
    df["academic_standing"] = df.apply(assign_standing, axis=1)
    
    # Dropout Risk Tier
    def assign_dropout_risk(row):
        score = row["composite_score"]
        att = row["overall_attendance_pct"]
        gpa = row["previous_gpa"]
        if att < 40.0 or score < 45.0 or gpa < 1.80:
            return "High Risk"
        elif att < 65.0 or score < 60.0:
            return "Medium Risk"
        else:
            return "Low Risk"
    df["dropout_risk"] = df.apply(assign_dropout_risk, axis=1)
    
    # Age Group Categorization
    def assign_age_group(age):
        if age <= 19:
            return "18-19"
        elif age <= 22:
            return "20-22"
        else:
            return "23-25"
    df["age_group"] = df["age"].apply(assign_age_group)
    
    # NOTE: The raw dataset contains no course metadata (no course name, department, or
    # instructor columns). A course_id derived from student_id % 3 was previously used
    # but it invented a relationship that does not exist in the data. It has been removed.
    # All downstream tables work on the single-course flat structure of the raw dataset.

    # --- 3.4 Relational Entity Normalization ---
    # 1. Students Table
    df_students = df[[
        "student_id", "first_name", "last_name", "age", "age_group", "gender", "previous_gpa"
    ]].drop_duplicates(subset=["student_id"]).sort_values("student_id").reset_index(drop=True)
    
    # NOTE: Courses table removed. The raw dataset has no course name, department,
    # or instructor columns. The previous courses table was entirely invented data
    # and has been dropped to maintain analytical honesty.
    
    # 2. Attendance Records Table (no fabricated course_id)
    df_attendance = df[[
        "student_id", "total_lectures", "lectures_attended",
        "lecture_attendance_pct", "total_lab_sessions", "labs_attended",
        "lab_attendance_pct", "overall_attendance_pct", "attendance_tier"
    ]].copy().reset_index(drop=True)
    df_attendance.insert(0, "attendance_id", range(1, len(df_attendance) + 1))
    
    # 3. Academic Assessments Table (no fabricated course_id)
    df_assessments = df[[
        "student_id", "quiz1_marks", "quiz2_marks", "quiz3_marks",
        "avg_quiz_score", "midterm_marks", "final_marks",
        "composite_score", "letter_grade", "academic_standing", "dropout_risk"
    ]].copy().reset_index(drop=True)
    df_assessments.insert(0, "assessment_id", range(1, len(df_assessments) + 1))
    
    # --- 3.4 Save Processed Files ---
    df_students.to_csv(os.path.join(PROCESSED_DIR, "students.csv"), index=False)
    df_attendance.to_csv(os.path.join(PROCESSED_DIR, "attendance_records.csv"), index=False)
    df_assessments.to_csv(os.path.join(PROCESSED_DIR, "academic_assessments.csv"), index=False)
    
    print("\nSuccessfully transformed and saved 3 normalized relational tables:")
    print(f"  1. students.csv ({df_students.shape[0]} rows, {df_students.shape[1]} cols)")
    print(f"  2. attendance_records.csv ({df_attendance.shape[0]} rows, {df_attendance.shape[1]} cols)")
    print(f"  3. academic_assessments.csv ({df_assessments.shape[0]} rows, {df_assessments.shape[1]} cols)")
    
    return {
        "students": df_students,
        "attendance": df_attendance,
        "assessments": df_assessments,
        "full_transformed": df
    }

if __name__ == "__main__":
    from extract import extract_raw_data
    df_raw = extract_raw_data()
    tables = clean_and_transform_data(df_raw)
