# Milestone 1 Documentation: Data Extraction, Exploratory Data Analysis & Data Quality Audit

**Capstone Project:** End-to-End ETL & Academic Performance Pipeline  
**Milestone:** Phase 1 & Phase 2 Engineering Documentation  
**Phases Completed:**  
- **Phase 1:** Data Acquisition & Extraction  
- **Phase 2:** Exploratory Data Analysis (EDA) & Data Quality Checks  

---

## 1. Summary of Milestone 1 Objectives

In this phase, we established the project repository, ingested the raw dataset, preserved the original source data without modification, and performed a comprehensive Exploratory Data Analysis (EDA) and Data Quality Audit using Python, Pandas, Matplotlib, and Seaborn.

---

## 2. Dataset Overview

* **Source Domain:** Education / Student Academic Analytics
* **Source:** Kaggle (`muhammadkhubaibahmad/student-performance-and-clustering-dataset`)
* **Raw File Path:** `data/raw/student_dropout_behavior_raw.csv`
* **Dataset Scale:** 300 rows x 16 columns
* **Features:**
  1. `student_id` (int64) - Unique identifier (1 to 300)
  2. `name` (str) - Student full name
  3. `age` (int64) - Student age (18 to 25)
  4. `gender` (str) - Gender (155 Female, 145 Male)
  5. `quiz1_marks` (float64) - Quiz 1 score (out of 10.0)
  6. `quiz2_marks` (float64) - Quiz 2 score (out of 10.0)
  7. `quiz3_marks` (float64) - Quiz 3 score (out of 10.0)
  8. `total_assignments` (int64) - Number of homework assignments assigned (5 for all students)
  9. `assignments_submitted` (float64) - **Critical Data Quality Issue:** 100% missing (300 nulls in raw data)
  10. `midterm_marks` (float64) - Midterm examination score (out of 30.0)
  11. `final_marks` (float64) - Final examination score (out of 50.0)
  12. `previous_gpa` (float64) - Prior cumulative GPA (scale: 0.0 to 4.0)
  13. `total_lectures` (int64) - Total scheduled lectures (12)
  14. `lectures_attended` (int64) - Lectures attended (0 to 12)
  15. `total_lab_sessions` (int64) - Total scheduled lab sessions (6)
  16. `labs_attended` (int64) - Lab sessions attended (0 to 6)

---

## 3. Key Findings & Data Quality Audit

### 3.1 Missing Value Discovery
* **`assignments_submitted`**: Contained **300 missing values (100% null)**.
* **Significance:** Represents a real-world data collection telemetry failure. In Phase 3 (Day 2), we implement an academic engagement ratio imputation based on lecture and lab attendance logs rather than simply dropping the column.

### 3.2 Duplication Audit
* Duplicate full rows: `0`
* Duplicate `student_id` records: `0`
* **Conclusion:** Primary identifier integrity is clean and valid.

### 3.3 Outlier Detection (Interquartile Range - IQR Method)
Using $Q_1 - 1.5 \times \text{IQR}$ and $Q_3 + 1.5 \times \text{IQR}$:
* `midterm_marks`: 0 outliers (Range: 0.0 to 30.0, Mean: 19.97)
* `final_marks`: 3 lower-bound outliers (Scores of 0.0; genuine student exam absences)
* `previous_gpa`: 2 lower-bound outliers (GPAs < 0.84; severe academic probation cases)

### 3.4 Summary Statistics Table
| Feature | Count | Mean | Std Dev | Min | 25% | 50% (Median) | 75% | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `age` | 300 | 21.55 | 2.24 | 18.0 | 20.0 | 22.0 | 23.0 | 25.0 |
| `quiz1_marks` | 300 | 7.25 | 1.61 | 2.80 | 6.07 | 7.30 | 8.40 | 10.0 |
| `quiz2_marks` | 300 | 5.87 | 2.41 | 0.00 | 4.00 | 5.80 | 7.70 | 10.0 |
| `quiz3_marks` | 300 | 5.47 | 2.71 | 0.00 | 3.60 | 5.60 | 7.20 | 10.0 |
| `midterm_marks` | 300 | 19.97 | 8.27 | 0.00 | 14.23 | 21.35 | 27.42 | 30.0 |
| `final_marks` | 300 | 37.38 | 11.80 | 0.00 | 29.88 | 39.60 | 49.55 | 50.0 |
| `previous_gpa` | 300 | 2.81 | 0.73 | 0.61 | 2.33 | 2.80 | 3.32 | 4.0 |
| `lectures_attended` | 300 | 6.01 | 3.73 | 0.00 | 3.00 | 6.00 | 9.00 | 12.0 |
| `labs_attended` | 300 | 3.11 | 1.98 | 0.00 | 1.00 | 3.00 | 5.00 | 6.0 |

---

## 4. Visualizations Generated (Phase 2)

1. **`visualizations/01_grade_distributions.png`**:
   Histograms with Kernel Density Estimation (KDE) for Midterm Marks, Final Marks, Previous GPA, and a comparative Boxplot of Quizzes 1 through 3.
2. **`visualizations/02_attendance_vs_performance.png`**:
   Scatter plots colored by gender demonstrating the distribution of final marks against lecture attendance (out of 12) and lab attendance (out of 6).
3. **`visualizations/03_correlation_matrix.png`**:
   Statistical correlation heatmap measuring inter-feature linear relationships across examinations, attendance rates, and GPA.

---

## 5. Day 1 Source Code

### File 1: `src/extract.py` (Phase 1 Extraction Module)
```python
import os
import pandas as pd

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "student_dropout_behavior_raw.csv")

def extract_raw_data(filepath: str = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Extracts raw dataset from the preserved CSV file.
    Validates file existence, non-emptiness, and preserves raw state.
    """
    print("=" * 80)
    print("PHASE 1: DATA EXTRACTION")
    print("=" * 80)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found at: {filepath}")
        
    df_raw = pd.read_csv(filepath)
    print(f"Successfully extracted raw data from: {filepath}")
    print(f"Raw Dataset Dimensions: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print("\nInitial Column Schema:")
    for col in df_raw.columns:
        print(f"  - {col} ({df_raw[col].dtype})")
        
    print("\nSample Raw Records (First 3):")
    print(df_raw.head(3).to_string(index=False))
    return df_raw

if __name__ == "__main__":
    df = extract_raw_data()
```

---

### File 2: `src/eda.py` (Phase 2 Exploratory Data Analysis Module)
```python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

VIS_DIR = os.path.join(os.path.dirname(__file__), "..", "visualizations")

def perform_eda(df: pd.DataFrame, save_visualizations: bool = True) -> dict:
    """
    Executes Exploratory Data Analysis and Data Quality Audit.
    Generates summary statistics and visual diagnostic plots.
    """
    os.makedirs(VIS_DIR, exist_ok=True)
    
    print("=" * 80)
    print("PHASE 2: EXPLORATORY DATA ANALYSIS (EDA) & DATA QUALITY AUDIT")
    print("=" * 80)
    
    # 1. Basic Structure
    num_rows, num_cols = df.shape
    print(f"Total Records: {num_rows}")
    print(f"Total Features: {num_cols}")
    
    # 2. Data Quality Checks
    print("\n--- 2.1 Missing Values Analysis ---")
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / num_rows) * 100
    missing_df = pd.DataFrame({"Missing Count": missing_counts, "Percentage (%)": missing_pct})
    print(missing_df[missing_df["Missing Count"] > 0])
    
    print("\n--- 2.2 Duplication Analysis ---")
    dup_rows = df.duplicated().sum()
    dup_ids = df["student_id"].duplicated().sum()
    print(f"Duplicate Full Rows: {dup_rows}")
    print(f"Duplicate Student IDs: {dup_ids}")
    
    # 3. Descriptive Statistics
    print("\n--- 2.3 Numerical Feature Summary Statistics ---")
    numeric_summary = df.describe().round(2)
    print(numeric_summary.to_string())
    
    # 4. Categorical Feature Inspection
    print("\n--- 2.4 Categorical Features ---")
    print("Gender Distribution:")
    print(df["gender"].value_counts())
    print("\nAge Value Counts:")
    print(df["age"].value_counts().sort_index())
    
    # 5. Outlier Detection using IQR Method
    print("\n--- 2.5 Outlier Audit (IQR Method) ---")
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
        print("\n--- 2.6 Generating Visualizations ---")
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
        "missing_summary": missing_counts.to_dict(),
        "duplicate_rows": int(dup_rows),
        "outlier_summary": outlier_summary
    }

if __name__ == "__main__":
    from extract import extract_raw_data
    df_raw = extract_raw_data()
    perform_eda(df_raw)
```
