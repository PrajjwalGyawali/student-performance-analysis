"""
Phase 3: Data Cleaning & Transformation Module
Cleans raw data, imputes missing telemetry, engineers academic features,
and normalizes the flat dataset into 4 relational entities:
1. students
2. courses
3. attendance_records
4. academic_assessments
"""

import os
import pandas as pd
import numpy as np

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "processed")

def clean_and_transform_data(df_raw: pd.DataFrame) -> dict:
    """
    Cleans raw student dataset and transforms it into 4 normalized relational DataFrames.
    """
    print("=" * 80)
    print("PHASE 3: DATA CLEANING & TRANSFORMATION")
    print("=" * 80)
    
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = df_raw.copy()
    
    # --- 3.1 Cleaning & Standardizing Strings ---
    df["name"] = df["name"].astype(str).str.strip().str.title()
    df["gender"] = df["gender"].astype(str).str.strip().str.capitalize()
    
    # Split full name into first and last name
    name_split = df["name"].str.split(" ", n=1, expand=True)
    df["first_name"] = name_split[0]
    df["last_name"] = name_split[1].fillna("")
    
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
    
    # Course assignment for multi-table modeling
    # 3 core curriculum courses distributed systematically across student cohort
    df["course_id"] = (df["student_id"] % 3) + 101

    # --- 3.4 Relational Entity Normalization ---
    # 1. Students Table
    df_students = df[[
        "student_id", "first_name", "last_name", "age", "age_group", "gender", "previous_gpa"
    ]].drop_duplicates(subset=["student_id"]).sort_values("student_id").reset_index(drop=True)
    
    # 2. Courses Table
    courses_data = [
        {
            "course_id": 101,
            "course_code": "CS101",
            "course_name": "Introduction to Computer Science",
            "department": "Computer Science",
            "credits": 4,
            "instructor_name": "Dr. Alan Turing"
        },
        {
            "course_id": 102,
            "course_code": "DS201",
            "course_name": "Data Science & Statistical Learning",
            "department": "Data Science",
            "credits": 3,
            "instructor_name": "Dr. Grace Hopper"
        },
        {
            "course_id": 103,
            "course_code": "SE301",
            "course_name": "Software Engineering Principles",
            "department": "Software Engineering",
            "credits": 4,
            "instructor_name": "Dr. Margaret Hamilton"
        }
    ]
    df_courses = pd.DataFrame(courses_data)
    
    # 3. Attendance Records Table
    df_attendance = df[[
        "student_id", "course_id", "total_lectures", "lectures_attended",
        "lecture_attendance_pct", "total_lab_sessions", "labs_attended",
        "lab_attendance_pct", "overall_attendance_pct", "attendance_tier"
    ]].copy().reset_index(drop=True)
    df_attendance.insert(0, "attendance_id", range(1, len(df_attendance) + 1))
    
    # 4. Academic Assessments Table
    df_assessments = df[[
        "student_id", "course_id", "quiz1_marks", "quiz2_marks", "quiz3_marks",
        "avg_quiz_score", "midterm_marks", "final_marks",
        "composite_score", "letter_grade", "academic_standing", "dropout_risk"
    ]].copy().reset_index(drop=True)
    df_assessments.insert(0, "assessment_id", range(1, len(df_assessments) + 1))
    
    # --- 3.5 Save Processed Files ---
    df_students.to_csv(os.path.join(PROCESSED_DIR, "students.csv"), index=False)
    df_courses.to_csv(os.path.join(PROCESSED_DIR, "courses.csv"), index=False)
    df_attendance.to_csv(os.path.join(PROCESSED_DIR, "attendance_records.csv"), index=False)
    df_assessments.to_csv(os.path.join(PROCESSED_DIR, "academic_assessments.csv"), index=False)
    
    print("\nSuccessfully transformed and saved 4 normalized relational tables:")
    print(f"  1. students.csv ({df_students.shape[0]} rows, {df_students.shape[1]} cols)")
    print(f"  2. courses.csv ({df_courses.shape[0]} rows, {df_courses.shape[1]} cols)")
    print(f"  3. attendance_records.csv ({df_attendance.shape[0]} rows, {df_attendance.shape[1]} cols)")
    print(f"  4. academic_assessments.csv ({df_assessments.shape[0]} rows, {df_assessments.shape[1]} cols)")
    
    return {
        "students": df_students,
        "courses": df_courses,
        "attendance": df_attendance,
        "assessments": df_assessments,
        "full_transformed": df
    }

if __name__ == "__main__":
    from extract import extract_raw_data
    df_raw = extract_raw_data()
    tables = clean_and_transform_data(df_raw)
