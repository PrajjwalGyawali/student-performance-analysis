"""
Phase 4: Data Analysis & Business/Academic Insights Module
Answers 5 core analytical questions and formulates 5 data-driven insights with supporting charts.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

VIS_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")

def perform_data_analysis(tables: dict, save_plots: bool = True) -> dict:
    """
    Performs in-depth analytical evaluations across the normalized tables.
    """
    os.makedirs(VIS_DIR, exist_ok=True)
    
    print("=" * 80)
    print("PHASE 4: DATA ANALYSIS & INSIGHTS GENERATION")
    print("=" * 80)
    
    df_students = tables["students"]
    df_courses = tables["courses"]
    df_attendance = tables["attendance"]
    df_assessments = tables["assessments"]
    
    # Merge for integrated multi-table analytical slicing (students + attendance + assessments only)
    df_merged = df_assessments.merge(df_students, on="student_id") \
                              .merge(df_attendance, on="student_id")
    
    # -------------------------------------------------------------------------
    # Analytical Question 1: How does attendance tier impact composite scores & grades?
    # -------------------------------------------------------------------------
    print("\n[Q1] Average Composite Score and Grade Distribution by Attendance Tier:")
    q1_summary = df_merged.groupby("attendance_tier").agg(
        student_count=("student_id", "count"),
        avg_composite_score=("composite_score", "mean"),
        avg_midterm=("midterm_marks", "mean"),
        avg_final=("final_marks", "mean"),
        avg_quiz_score=("avg_quiz_score", "mean")
    ).round(2).sort_values("avg_composite_score", ascending=False)
    print(q1_summary.to_string())
    
    # -------------------------------------------------------------------------
    # Analytical Question 2: Dropout Risk Distribution by Gender & Age Group?
    # (Department analysis removed: dataset has no real department/course metadata)
    # -------------------------------------------------------------------------
    print("\n[Q2] Dropout Risk and Performance by Gender:")
    q2_summary = df_merged.groupby("gender").agg(
        student_count=("student_id", "count"),
        avg_final_marks=("final_marks", "mean"),
        avg_composite=("composite_score", "mean"),
        high_risk_count=("dropout_risk", lambda x: (x == "High Risk").sum()),
        deans_list_count=("academic_standing", lambda x: (x == "Dean's Honor List").sum())
    ).round(2)
    print(q2_summary.to_string())
    
    # -------------------------------------------------------------------------
    # Analytical Question 3: Academic Standing and Dropout Risk by Gender & Age Group?
    # -------------------------------------------------------------------------
    print("\n[Q3] Dropout Risk Proportions by Gender:")
    q3_risk_gender = pd.crosstab(df_merged["gender"], df_merged["dropout_risk"], normalize="index") * 100
    print(q3_risk_gender.round(2).to_string())
    
    print("\n[Q3b] Letter Grade Proportions by Age Group:")
    q3_grade_age = pd.crosstab(df_merged["age_group"], df_merged["letter_grade"], normalize="index") * 100
    print(q3_grade_age.round(2).to_string())
    
    # -------------------------------------------------------------------------
    # Analytical Question 4: Correlation between Previous GPA and Current Performance?
    # -------------------------------------------------------------------------
    corr_gpa_midterm = df_merged["previous_gpa"].corr(df_merged["midterm_marks"])
    corr_gpa_final = df_merged["previous_gpa"].corr(df_merged["final_marks"])
    corr_att_final = df_merged["overall_attendance_pct"].corr(df_merged["final_marks"])
    print(f"\n[Q4] Key Correlation Coefficients:")
    print(f"  - Previous GPA vs Midterm Marks: {corr_gpa_midterm:.3f}")
    print(f"  - Previous GPA vs Final Exam Marks: {corr_gpa_final:.3f}")
    print(f"  - Overall Attendance Rate vs Final Exam Marks: {corr_att_final:.3f}")
    
    # -------------------------------------------------------------------------
    # Analytical Question 5: Impact of Lab Attendance vs Lecture Attendance on Finals?
    # -------------------------------------------------------------------------
    high_lab = df_merged[df_merged["lab_attendance_pct"] >= 80]["final_marks"].mean()
    low_lab = df_merged[df_merged["lab_attendance_pct"] < 40]["final_marks"].mean()
    high_lec = df_merged[df_merged["lecture_attendance_pct"] >= 80]["final_marks"].mean()
    low_lec = df_merged[df_merged["lecture_attendance_pct"] < 40]["final_marks"].mean()
    print("\n[Q5] Lab Attendance vs Lecture Attendance Impact on Final Score:")
    print(f"  - High Lab (>=80%) Avg Final: {high_lab:.2f} vs Low Lab (<40%) Avg Final: {low_lab:.2f} (Diff: {high_lab - low_lab:.2f})")
    print(f"  - High Lecture (>=80%) Avg Final: {high_lec:.2f} vs Low Lecture (<40%) Avg Final: {low_lec:.2f} (Diff: {high_lec - low_lec:.2f})")
    
    # -------------------------------------------------------------------------
    # Insights Formulation
    # -------------------------------------------------------------------------
    total_students = len(df_merged)
    high_risk_total = (df_merged["dropout_risk"] == "High Risk").sum()
    high_risk_pct = (high_risk_total / total_students) * 100
    deans_list_total = (df_merged["academic_standing"] == "Dean's Honor List").sum()
    deans_list_pct = (deans_list_total / total_students) * 100
    
    insights = [
        f"1. Students in the 'Excellent' attendance tier averaged a composite score of {q1_summary.loc['Excellent', 'avg_composite_score']:.1f}, compared to {q1_summary.loc['Critical', 'avg_composite_score']:.1f} for the 'Critical' tier. The data shows a clear difference in outcomes, though attendance alone cannot be identified as the sole cause.",
        f"2. {high_risk_total} students ({high_risk_pct:.1f}% of cohort) are classified as 'High Risk'. This group is defined by overall attendance under 40% and final exam scores under 25 combined — both conditions must hold.",
        f"3. High-Achieving Cohort: {deans_list_total} students ({deans_list_pct:.1f}% of cohort) qualified for the Dean's Honor List, demonstrating both >=80% attendance and >=85.0 composite marks.",
        f"4. Lab Session Impact: Students attending >=80% of lab sessions scored an average of {high_lab:.1f} on the final exam, compared to {low_lab:.1f} for students with <40% lab attendance — a {high_lab - low_lab:.1f}-point observed difference.",
        f"5. Lab vs Lecture: High lab attenders scored {high_lab:.1f} avg vs {low_lab:.1f} for low lab attenders ({((high_lab - low_lab)/low_lab)*100:.1f}% higher). High lecture attenders scored {high_lec:.1f} vs {low_lec:.1f} for low lecture attenders."
    ]
    
    print("\n" + "=" * 80)
    print("KEY DATA-DRIVEN INSIGHTS:")
    print("=" * 80)
    for ins in insights:
        print(f"- {ins}")

    # Generate analytical visualizations
    if save_plots:
        sns.set_theme(style="whitegrid", palette="muted")
        
        # Figure 4: Attendance Tier vs Composite Score
        plt.figure(figsize=(9, 5))
        sns.boxplot(
            data=df_merged, x="attendance_tier", y="composite_score", hue="attendance_tier",
            order=["Critical", "Irregular", "Satisfactory", "Excellent"],
            palette="Blues_r", legend=False
        )
        plt.title("Student Composite Score by Attendance Tier", fontsize=13, weight="bold")
        plt.xlabel("Attendance Tier", fontsize=11)
        plt.ylabel("Composite Score (out of 100)", fontsize=11)
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, "04_grade_by_attendance_tier.png"), dpi=300)
        plt.close()
        
        # Figure 5: Dropout Risk Distribution
        plt.figure(figsize=(8, 5))
        risk_counts = df_merged["dropout_risk"].value_counts()[["Low Risk", "Medium Risk", "High Risk"]]
        bars = plt.bar(risk_counts.index, risk_counts.values, color=["#2ca02c", "#ff7f0e", "#d62728"], width=0.55)
        plt.title("Distribution of Student Dropout Risk Tiers", fontsize=13, weight="bold")
        plt.ylabel("Student Count", fontsize=11)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, yval + 2, f"{int(yval)} ({yval/total_students*100:.1f}%)", ha="center", va="bottom", weight="bold")
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, "05_dropout_risk_breakdown.png"), dpi=300)
        plt.close()
        
        # NOTE: 06_department_performance.png removed. The raw dataset has no real
        # department/course metadata. Generating a department plot from fabricated
        # course_id assignments would misrepresent the data.

    return {
        "insights": insights,
        "q1_summary": q1_summary,
        "q2_summary": q2_summary
    }

if __name__ == "__main__":
    from extract import extract_raw_data
    from transform import clean_and_transform_data
    df_raw = extract_raw_data()
    tables = clean_and_transform_data(df_raw)
    perform_data_analysis(tables)
