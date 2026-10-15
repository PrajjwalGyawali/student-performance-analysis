"""
Phase 4: Data Analysis & Academic Insights Module
Answers 5 core analytical questions and formulates data-driven insights with supporting charts.

NOTE: The dropout_risk column ('High Risk', 'Medium Risk', 'Low Risk') is a rule-based label
defined in transform.py. It is NOT real dropout outcome data. High Risk is assigned when a
student meets ANY of: overall_attendance_pct < 40, composite_score < 45, or previous_gpa < 1.8.
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
    Uses only students, attendance_records, and academic_assessments.
    """
    os.makedirs(VIS_DIR, exist_ok=True)

    print("=" * 80)
    print("PHASE 4: DATA ANALYSIS & INSIGHTS GENERATION")
    print("=" * 80)

    df_students    = tables["students"]
    df_attendance  = tables["attendance"]
    df_assessments = tables["assessments"]

    # Merge three real tables (no fabricated courses table)
    df_merged = df_assessments.merge(df_students, on="student_id") \
                              .merge(df_attendance, on="student_id")

    # -------------------------------------------------------------------------
    # Q1: How does attendance tier relate to composite scores?
    # -------------------------------------------------------------------------
    print("\n[Q1] Average Composite Score by Attendance Tier:")
    q1_summary = df_merged.groupby("attendance_tier").agg(
        student_count=("student_id", "count"),
        avg_composite_score=("composite_score", "mean"),
        avg_midterm=("midterm_marks", "mean"),
        avg_final=("final_marks", "mean"),
        avg_quiz_score=("avg_quiz_score", "mean")
    ).round(2).sort_values("avg_composite_score", ascending=False)
    print(q1_summary.to_string())

    # Correlation: overall attendance vs final marks
    corr_att_final = df_merged["overall_attendance_pct"].corr(df_merged["final_marks"])

    # -------------------------------------------------------------------------
    # Q2: Dropout Risk Distribution by Gender & Age Group
    # NOTE: dropout_risk is a rule-based label, not real dropout data.
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
    # Q3: Academic Standing and Dropout Risk by Age Group
    # -------------------------------------------------------------------------
    print("\n[Q3] Dropout Risk Proportions by Gender:")
    q3_risk_gender = pd.crosstab(df_merged["gender"], df_merged["dropout_risk"], normalize="index") * 100
    print(q3_risk_gender.round(2).to_string())

    print("\n[Q3b] Letter Grade Proportions by Age Group:")
    q3_grade_age = pd.crosstab(df_merged["age_group"], df_merged["letter_grade"], normalize="index") * 100
    print(q3_grade_age.round(2).to_string())

    # -------------------------------------------------------------------------
    # Q4: Correlation between Previous GPA and Current Performance
    # -------------------------------------------------------------------------
    corr_gpa_midterm = df_merged["previous_gpa"].corr(df_merged["midterm_marks"])
    corr_gpa_final   = df_merged["previous_gpa"].corr(df_merged["final_marks"])
    corr_att_final2  = df_merged["overall_attendance_pct"].corr(df_merged["final_marks"])
    print(f"\n[Q4] Key Correlation Coefficients:")
    print(f"  - Previous GPA vs Midterm Marks:         {corr_gpa_midterm:.3f}")
    print(f"  - Previous GPA vs Final Exam Marks:      {corr_gpa_final:.3f}")
    print(f"  - Overall Attendance vs Final Exam Marks: {corr_att_final2:.3f}")

    # -------------------------------------------------------------------------
    # Q5: Lab Attendance vs Lecture Attendance impact on Finals
    # -------------------------------------------------------------------------
    high_lab = df_merged[df_merged["lab_attendance_pct"] >= 80]["final_marks"].mean()
    low_lab  = df_merged[df_merged["lab_attendance_pct"] <  40]["final_marks"].mean()
    high_lec = df_merged[df_merged["lecture_attendance_pct"] >= 80]["final_marks"].mean()
    low_lec  = df_merged[df_merged["lecture_attendance_pct"] <  40]["final_marks"].mean()
    print("\n[Q5] Lab vs Lecture Attendance Impact on Final Score:")
    print(f"  - High Lab (>=80%) Avg Final: {high_lab:.2f}  |  Low Lab (<40%) Avg Final: {low_lab:.2f}  (Diff: {high_lab - low_lab:.2f})")
    print(f"  - High Lec (>=80%) Avg Final: {high_lec:.2f}  |  Low Lec (<40%) Avg Final: {low_lec:.2f}  (Diff: {high_lec - low_lec:.2f})")

    # -------------------------------------------------------------------------
    # Insights (all values computed from data, no hardcoded numbers)
    # -------------------------------------------------------------------------
    total_students   = len(df_merged)
    high_risk_total  = (df_merged["dropout_risk"] == "High Risk").sum()
    high_risk_pct    = (high_risk_total / total_students) * 100
    deans_list_total = (df_merged["academic_standing"] == "Dean's Honor List").sum()
    deans_list_pct   = (deans_list_total / total_students) * 100

    excellent_avg = q1_summary.loc["Excellent", "avg_composite_score"] if "Excellent" in q1_summary.index else float("nan")
    critical_avg  = q1_summary.loc["Critical",  "avg_composite_score"] if "Critical"  in q1_summary.index else float("nan")
    score_diff    = excellent_avg - critical_avg

    insights = [
        (f"1. Attendance-tier composite scores differ only slightly: 'Excellent' tier averaged "
         f"{excellent_avg:.1f} vs {critical_avg:.1f} for 'Critical' tier "
         f"(a {score_diff:.1f}-point gap). The Pearson correlation between overall attendance "
         f"percentage and final marks is {corr_att_final:.2f}, indicating a very weak linear "
         f"relationship in this cohort."),

        (f"2. {high_risk_total} students ({high_risk_pct:.1f}% of cohort) carry the 'High Risk' "
         f"label. This is a rule-based classification defined in transform.py — a student is "
         f"flagged High Risk when they meet ANY of: overall attendance < 40%, composite score "
         f"< 45, or previous GPA < 1.8. It does not represent observed dropout outcomes."),

        (f"3. {deans_list_total} students ({deans_list_pct:.1f}% of cohort) achieved Dean's "
         f"Honor List standing (>=80% attendance AND >=85.0 composite score)."),

        (f"4. Lab vs Lecture attendance: students with >=80% lab attendance averaged "
         f"{high_lab:.1f} on the final exam vs {low_lab:.1f} for <40% lab attendance "
         f"({high_lab - low_lab:.1f}-point difference). For lectures, the same comparison "
         f"gives {high_lec:.1f} vs {low_lec:.1f} ({high_lec - low_lec:.1f}-point difference). "
         f"Both effects are modest and should not be interpreted as causal."),

        (f"5. Previous GPA vs final marks: Pearson r = {corr_gpa_final:.2f}, indicating that "
         f"a student's historical GPA has very little linear association with their final exam "
         f"score in this dataset. Similarly, previous GPA vs midterm r = {corr_gpa_midterm:.2f}.")
    ]

    print("\n" + "=" * 80)
    print("KEY DATA-DRIVEN INSIGHTS (dropout_risk is a rule-based label, not real outcome data):")
    print("=" * 80)
    for ins in insights:
        print(f"- {ins}\n")

    # -------------------------------------------------------------------------
    # Visualizations
    # -------------------------------------------------------------------------
    if save_plots:
        sns.set_theme(style="whitegrid", palette="muted")

        # Figure 4: Attendance Tier vs Composite Score
        plt.figure(figsize=(9, 5))
        tier_order = [t for t in ["Critical", "Irregular", "Satisfactory", "Excellent"]
                      if t in df_merged["attendance_tier"].unique()]
        sns.boxplot(
            data=df_merged, x="attendance_tier", y="composite_score",
            hue="attendance_tier", order=tier_order,
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
        risk_order = [r for r in ["Low Risk", "Medium Risk", "High Risk"]
                      if r in df_merged["dropout_risk"].unique()]
        risk_counts = df_merged["dropout_risk"].value_counts().reindex(risk_order, fill_value=0)
        bars = plt.bar(risk_counts.index, risk_counts.values,
                       color=["#2ca02c", "#ff7f0e", "#d62728"][:len(risk_order)], width=0.55)
        plt.title("Distribution of Student Dropout Risk Labels (Rule-Based)", fontsize=13, weight="bold")
        plt.ylabel("Student Count", fontsize=11)
        for bar in bars:
            yval = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2.0, yval + 2,
                     f"{int(yval)} ({yval / total_students * 100:.1f}%)",
                     ha="center", va="bottom", weight="bold")
        plt.tight_layout()
        plt.savefig(os.path.join(VIS_DIR, "05_dropout_risk_breakdown.png"), dpi=300)
        plt.close()

        # NOTE: 06_department_performance.png removed. The raw dataset has no real
        # department or course metadata. A department plot from fabricated course_ids
        # would misrepresent the data.

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
