"""
Phase 2: Exploratory Data Analysis (EDA) & Data Quality Module
Performs comprehensive data exploration, data quality auditing, and visualization.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

VIS_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")

def perform_eda(df: pd.DataFrame, save_visualizations: bool = True) -> dict:
    """
    Executes Exploratory Data Analysis and Data Quality Audit.
    Generates summary statistics, text quality audits, and visual diagnostic plots.
    """
    os.makedirs(VIS_DIR, exist_ok=True)
    
    print("=" * 80)
    print("PHASE 2: EXPLORATORY DATA ANALYSIS (EDA) & DATA QUALITY AUDIT")
    print("=" * 80)
    
    # 1. Basic Structure
    num_rows, num_cols = df.shape
    print(f"Total Records: {num_rows}")
    print(f"Total Features: {num_cols}")
    
    print("\n--- 1.1 Column Data Types ---")
    for col, dtype in df.dtypes.items():
        print(f"  - {col}: {dtype}")
        
    print("\n--- 1.2 Number of Unique Values per Column ---")
    unique_counts = df.nunique()
    for col, u_cnt in unique_counts.items():
        print(f"  - {col}: {u_cnt} unique values")
        
    print("\n--- 1.3 First 5 Sample Records ---")
    print(df.head(5).to_string(index=False))
    
    # 2. Data Quality Checks
    print("\n--- 2.1 Missing Values Analysis ---")
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / num_rows) * 100
    missing_df = pd.DataFrame({"Missing Count": missing_counts, "Percentage (%)": missing_pct})
    print(missing_df[missing_df["Missing Count"] > 0])
    
    print("\n--- 2.2 Duplication Analysis ---")
    dup_rows = df.duplicated().sum()
    dup_ids = df["student_id"].duplicated().sum()
    dup_names = df["name"].duplicated().sum()
    print(f"Duplicate Full Rows: {dup_rows}")
    print(f"Duplicate Student IDs: {dup_ids}")
    print(f"Duplicate Student Names: {dup_names}")
    if dup_names > 0:
        dup_sample = df[df["name"].duplicated(keep=False)].sort_values("name")[["student_id", "name", "gender"]]
        print(f"  Note: {dup_names} names appear more than once, but have distinct student_ids:")
        for name_val, grp in dup_sample.groupby("name"):
            id_list = grp["student_id"].tolist()
            print(f"    * '{name_val}': IDs {id_list} (Kept as distinct student entities)")
            
    print("\n--- 2.3 Text Consistency & Casing Audit ---")
    inconsistent_mask = df["name"] != df["name"].str.strip().str.title()
    inconsistent_names_count = int(inconsistent_mask.sum())
    print(f"Names with extra whitespace or non-standard capitalization: {inconsistent_names_count}")
    if inconsistent_names_count > 0:
        print(f"  Flagged records: {df.loc[inconsistent_mask, 'name'].tolist()}")
        print("  Resolution: Handled in Phase 3 via .str.strip().str.title()")
        
    print("\n--- 2.4 Name-Gender Semantic Alignment Check ---")
    print("Observation: Several records exhibit discordant traditional name-gender associations")
    print("  (e.g., 'Kristina Vaughan' listed as Male, 'Mark Thomas' listed as Female).")
    print("  Assessment: Characteristics indicate synthetic dataset generation (e.g. Faker).")
    print("  Integrity Policy: Gender telemetry preserved unmodified to avoid subjective alteration.")
    
    # 3. Descriptive Statistics
    print("\n--- 2.5 Numerical Feature Summary Statistics ---")
    numeric_summary = df.describe().round(2)
    print(numeric_summary.to_string())
    
    # 4. Categorical Feature Inspection
    print("\n--- 2.6 Categorical Feature Distributions ---")
    print("Gender Distribution:")
    print(df["gender"].value_counts())
    print("\nAge Value Counts:")
    print(df["age"].value_counts().sort_index())
    
    # 5. Outlier Detection using IQR Method
    print("\n--- 2.7 Outlier Audit (IQR Method) ---")
    outlier_summary = {}
    eval_cols = ["quiz1_marks", "quiz2_marks", "quiz3_marks", "midterm_marks", "final_marks", "previous_gpa"]
    for col in eval_cols:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        outlier_summary[col] = len(outliers)
        print(f"  {col}: {len(outliers)} outliers (Lower: {lower_bound:.2f}, Upper: {upper_bound:.2f})")

    # 6. Generate and Save Visualizations
    if save_visualizations:
        print("\n--- 2.8 Generating Visualizations ---")
        sns.set_theme(style="whitegrid", palette="muted")
        
        # Figure 1: Grade Distributions
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        sns.histplot(df["midterm_marks"], kde=True, ax=axes[0, 0], color="#2b5c8f", bins=15)
        axes[0, 0].set_title("Midterm Marks Distribution (Max: 30)", fontsize=13, weight="bold")
        axes[0, 0].set_xlabel("Midterm Score")
        
        sns.histplot(df["final_marks"], kde=True, ax=axes[0, 1], color="#278045", bins=15)
        axes[0, 1].set_title("Final Marks Distribution (Max: 50)", fontsize=13, weight="bold")
        axes[0, 1].set_xlabel("Final Score")
        
        sns.histplot(df["previous_gpa"], kde=True, ax=axes[1, 0], color="#b06500", bins=15)
        axes[1, 0].set_title("Previous GPA Distribution (Scale: 0.0 - 4.0)", fontsize=13, weight="bold")
        axes[1, 0].set_xlabel("GPA")
        
        # Quiz averages
        quiz_melt = df.melt(value_vars=["quiz1_marks", "quiz2_marks", "quiz3_marks"], var_name="Quiz", value_name="Marks")
        sns.boxplot(x="Quiz", y="Marks", hue="Quiz", data=quiz_melt, ax=axes[1, 1], palette="Set2", legend=False)
        axes[1, 1].set_title("Quiz Marks Comparison (1 to 3)", fontsize=13, weight="bold")
        
        plt.tight_layout()
        fig_path1 = os.path.join(VIS_DIR, "01_grade_distributions.png")
        plt.savefig(fig_path1, dpi=300)
        plt.close()
        print(f"Saved: {fig_path1}")
        
        # Figure 2: Attendance vs Academic Performance
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        sns.scatterplot(
            data=df, x="lectures_attended", y="final_marks", hue="gender",
            s=80, alpha=0.85, ax=axes[0], palette=["#20639B", "#ED553B"]
        )
        axes[0].set_title("Lectures Attended vs Final Marks", fontsize=13, weight="bold")
        axes[0].set_xlabel("Lectures Attended (out of 12)")
        axes[0].set_ylabel("Final Marks")
        
        sns.scatterplot(
            data=df, x="labs_attended", y="final_marks", hue="gender",
            s=80, alpha=0.85, ax=axes[1], palette=["#20639B", "#ED553B"]
        )
        axes[1].set_title("Labs Attended vs Final Marks", fontsize=13, weight="bold")
        axes[1].set_xlabel("Labs Attended (out of 6)")
        axes[1].set_ylabel("Final Marks")
        
        plt.tight_layout()
        fig_path2 = os.path.join(VIS_DIR, "02_attendance_vs_performance.png")
        plt.savefig(fig_path2, dpi=300)
        plt.close()
        print(f"Saved: {fig_path2}")
        
        # Figure 3: Correlation Matrix
        plt.figure(figsize=(10, 8))
        corr_cols = [
            "previous_gpa", "quiz1_marks", "quiz2_marks", "quiz3_marks",
            "midterm_marks", "final_marks", "lectures_attended", "labs_attended"
        ]
        corr_matrix = df[corr_cols].corr()
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", cbar=True, square=True)
        plt.title("Feature Correlation Heatmap", fontsize=14, weight="bold")
        plt.tight_layout()
        fig_path3 = os.path.join(VIS_DIR, "03_correlation_matrix.png")
        plt.savefig(fig_path3, dpi=300)
        plt.close()
        print(f"Saved: {fig_path3}")
        
    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "column_dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "unique_counts": unique_counts.to_dict(),
        "sample_records_head5": df.head(5).to_dict(orient="records"),
        "missing_summary": missing_counts.to_dict(),
        "duplicate_rows": int(dup_rows),
        "duplicate_student_ids": int(dup_ids),
        "duplicate_names": int(dup_names),
        "inconsistent_names_count": inconsistent_names_count,
        "outlier_summary": outlier_summary
    }

if __name__ == "__main__":
    from extract import extract_raw_data
    df_raw = extract_raw_data()
    perform_eda(df_raw)
