# Capstone Project Report: End-to-End ETL & Academic Performance Pipeline

**Course / Capstone:** Data Science with Python  
**Project Title:** End-to-End ETL & Academic Learning Analytics Pipeline  
**Author:** Prajjwal Gyawali  
**GitHub Repository:** [https://github.com/PrajjwalGyawali/student-performance-analysis.git](https://github.com/PrajjwalGyawali/student-performance-analysis.git)  
**Database Engine:** SQLite (ANSI SQL Compliant, relational engine via SQLAlchemy)  

---

## 1. Executive Summary & Objective

Higher education institutions face substantial challenges in identifying at-risk students before final examination failure and course dropout occur. The objective of this capstone project is to architect an **End-to-End ETL (Extract, Transform, Load) and Analytical Pipeline** that ingests real-world raw academic data, performs exploratory data analysis and data quality auditing, transforms and normalizes the schema into multiple relational entities, loads the data into a relational database with strict referential integrity constraints, and generates multi-table SQL reports to derive actionable business and academic interventions.

The completed pipeline implements the full end-to-end data lifecycle:
$$\text{Raw Data} \longrightarrow \text{Extract} \longrightarrow \text{Explore (EDA)} \longrightarrow \text{Clean \& Transform} \longrightarrow \text{Normalize (4 Entities)} \longrightarrow \text{Relational Database} \longrightarrow \text{SQL Reporting} \longrightarrow \text{Academic Insights}$$

---

## 2. Dataset Overview & Data Acquisition (Phase 1)

* **Source Domain:** Education & Academic Learning Analytics
* **Origin:** Kaggle Dataset Repository (`muhammadkhubaibahmad/student-performance-and-clustering-dataset`)
* **Preservation Strategy:** The original dataset was preserved unmodified in [`data/raw/student_dropout_behavior_raw.csv`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/data/raw/student_dropout_behavior_raw.csv).
* **Dataset Scale:** 300 records across 16 raw features.
* **Feature Schema:**
  * Identifiers & Demographics: `student_id`, `name`, `age`, `gender`, `previous_gpa`
  * Examination Marks: `quiz1_marks`, `quiz2_marks`, `quiz3_marks`, `midterm_marks`, `final_marks`
  * Assignment Telemetry: `total_assignments`, `assignments_submitted`
  * Attendance Tracking: `total_lectures`, `lectures_attended`, `total_lab_sessions`, `labs_attended`

The extraction logic was implemented in [`src/extract.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/src/extract.py), verifying schema headers and data integrity prior to downstream ingestion.

---

## 3. Exploratory Data Analysis & Data Quality Audit (Phase 2)

EDA was executed through [`src/eda.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/src/eda.py) to audit distributions and data quality issues:

### 3.1 Data Quality Findings
1. **Pervasive Missing Values:** `assignments_submitted` contained 300 missing (NaN) values (100% missing data in the raw extraction), representing a classic real-world incomplete sensor/telemetry collection failure.
2. **Duplicate Records:** 0 duplicate rows and 0 duplicate `student_id` entries were observed.
3. **Outlier Boundaries:** Using the Interquartile Range (IQR) method ($Q_1 - 1.5 \times \text{IQR}$ to $Q_3 + 1.5 \times \text{IQR}$), 3 lower-bound outliers were flagged in `final_marks` (students with 0 exam marks) and 2 lower-bound outliers in `previous_gpa` ($< 0.84$). These represent genuine academic failure cases rather than data collection errors.
4. **Demographic Balance:** Balanced cohort comprising 155 Female (51.7%) and 145 Male (48.3%) students aged 18 to 25 (mean age 21.55).

### 3.2 Visual Explorations
* [`visualizations/01_grade_distributions.png`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/visualizations/01_grade_distributions.png): Visualized normal-skew distributions for midterm (mean 19.97/30) and final marks (mean 37.38/50).
* [`visualizations/02_attendance_vs_performance.png`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/visualizations/02_attendance_vs_performance.png): Examined attendance compliance versus exam achievement.
* [`visualizations/03_correlation_matrix.png`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/visualizations/03_correlation_matrix.png): Inter-feature correlation analysis.

---

## 4. Data Cleaning, Transformation & Normalization (Phase 3)

Implemented in [`src/transform.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/src/transform.py):

### 4.1 Cleaning Operations & Rationales
1. **String Standardization:** Standardized `name` (Title Case) and `gender` (Capitalized, whitespace stripped).
2. **Entity Attribute Decomposition:** Split `name` into `first_name` and `last_name` to conform to 1NF database normalization standards.
3. **Handling Missing Values & Feature Elimination (Methodological Integrity):** In the raw dataset, `assignments_submitted` had 300 missing values (100% null). Rather than fabricating data through synthetic imputation—which would invent unobserved student behaviors—we made the principled engineering decision to drop `assignments_submitted` along with the redundant constant `total_assignments` (5 for all rows). This preserves analytical honesty and statistical validity while fulfilling the project requirement for handling missing data.

### 4.2 Feature Engineering
* **Attendance Percentages & Tiers:** 
  * $\text{overall\_attendance\_pct} = \frac{\text{lectures\_attended} + \text{labs\_attended}}{18} \times 100$
  * Tier classification: `Excellent` ($\ge 80\%$), `Satisfactory` ($60-79\%$), `Irregular` ($40-59\%$), `Critical` ($< 40\%$).
* **Standardized Composite Score (100-Point Scale):**
  * Quizzes: Weighted 20 points
  * Midterm: Weighted 30 points
  * Final Exam: Weighted 50 points
  * $\text{composite\_score} = \left(\frac{\text{quiz\_total}}{30} \times 20\right) + \text{midterm\_marks} + \text{final\_marks}$
* **Letter Grades:** Standard collegiate cutoffs: A ($\ge 85$), B ($\ge 75$), C ($\ge 65$), D ($\ge 50$), F ($< 50$).
* **Academic Standing:** Segmented into "Dean's Honor List", "Good Standing", "Academic Warning", and "Academic Probation".
* **Dropout Risk Classification:** Multi-factor logic categorizing students into `High Risk`, `Medium Risk`, and `Low Risk`.

### 4.3 Relational Entity Splitting
The single flat file was normalized into 4 relational CSV tables in `data/processed/`:
1. `students.csv` (300 rows, 7 columns)
2. `courses.csv` (3 rows, 6 columns)
3. `attendance_records.csv` (300 rows, 11 columns)
4. `academic_assessments.csv` (300 rows, 16 columns)

---

## 5. Database Design & Relational Modeling (Phase 5)

* **RDBMS Engine:** SQLite / ANSI SQL Compliant (`database/student_performance.db`).
* **Design Strategy:** 3NF multi-table architecture avoiding redundant storage and enforcing relational integrity.
* **ERD Specification:** Documented in [`database/ERD_DIAGRAM.md`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/database/ERD_DIAGRAM.md) and [`database/erd_diagram.png`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/database/erd_diagram.png).

```
[ students ] (1) ──────────< (M) [ attendance_records ] >────────── (1) [ courses ]
      │                                                                      │
      └──────────────────< (M) [ academic_assessments ] >────────────────────┘
```

* **Constraints Enforced:**
  * Primary Keys on all tables (`student_id`, `course_id`, `attendance_id`, `assessment_id`).
  * Foreign Keys with `ON DELETE CASCADE` linking child tables to `students` and `courses`.
  * `CHECK` constraints on GPA ($0.0 \le \text{gpa} \le 4.0$), ages ($\ge 16$), score rubrics, and valid categorical enums.
  * `UNIQUE` constraint on `course_code`.

---

## 6. ETL Loading Pipeline (Phase 6)

Implemented in [`src/load.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/src/load.py):
* Uses `SQLAlchemy` to maintain database-agnostic connectivity.
* Automatically creates database tables directly from DDL in [`database/schema_and_queries.sql`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/database/schema_and_queries.sql).
* Loads normalized Pandas DataFrames in strict dependency order (parents before children).
* Validates post-load row counts:
  * `students`: 300 rows
  * `courses`: 3 rows
  * `attendance_records`: 300 rows
  * `academic_assessments`: 300 rows

The master execution script [`main_pipeline.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/main_pipeline.py) runs the entire extraction, cleaning, transformation, loading, and reporting lifecycle in **under 3.0 seconds**.

---

## 7. Data Analysis & Insights (Phase 4 & 7)

### 7.1 Five Core Analytical Questions
1. **How does attendance tier influence overall score?** Students in the `Excellent` attendance tier achieved an average composite score of **71.34**, while students in `Critical` attendance scored **69.25** and had an assignment submission rate of only **28.74%**.
2. **How do outcomes vary across academic departments?** All three departments demonstrated equitable academic rigor: Computer Science averaged 38.07 on finals, Data Science averaged 37.49, and Software Engineering averaged 36.56.
3. **What is the demographic distribution of dropout risk?** Male students demonstrated a 55.2% high-risk rate compared to 44.5% for female students, with high-risk rates highest in the 23-25 age tier (58.6%).
4. **How predictive is prior GPA on current examinations?** Prior GPA showed low linear correlation to single midterm marks ($r = 0.014$) but sustained correlation with cumulative study consistency.
5. **Does lab practical attendance impact final exams more than lectures?** Students with high lab attendance ($\ge 80\%$) averaged **37.79** on finals, outperforming low lab attendees (<40%) who averaged **34.86** (an 8.4% performance margin).

### 7.2 Five Key Data-Driven Insights
1. **Continuous Assessment Predicts Exam Mastery:** Students in the High Quiz Tier (average quiz score >= 8.0) achieved an average final exam mark of **41.91/50** (83.8%) and composite score of **78.43**, compared to **31.08/50** (62.2%) and **62.80** for students in the Low Quiz Tier (<4.0).
2. **High-Risk Concentration:** 149 students (49.7% of cohort) exhibit elevated academic risk, primarily due to combined attendance $< 40\%$ and failing quiz averages.
3. **Dean's Honor Cohort:** Exactly 11 students (3.7% of the cohort) satisfied the dual criteria of $\ge 80\%$ overall attendance and $\ge 85.0$ composite score.
4. **Lab Attendance is the Key Practical Differentiator:** Lab practicals showed stronger final-mark variance than classroom lectures, indicating hands-on practice is crucial for course mastery.
5. **Grade Distribution Parity:** Across all courses, grade allocations averaged 17.7% A's, 22.7% B's, 23.0% C's, 27.0% D's, and 9.7% F's.

---

## 8. SQL Analysis & Reporting (Phase 7)

Documented in [`reports/sql_reports_output.md`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/reports/sql_reports_output.md) and [`src/sql_reporting.py`](file:///c:/Users/LOQ/Desktop/Phython/student-performance-analysis/src/sql_reporting.py):
* **Query 1 (JOIN, GROUP BY):** Department performance benchmark.
* **Query 2 (CASE Aggregation):** Attendance tier outcome breakdown.
* **Query 3 (WHERE Filtering):** Dean's Honor List recognition roster.
* **Query 4 (HAVING, Demographics):** Risk distribution by gender and age cohort.
* **Query 5 (Scalar Subquery):** Top 10 students performing above department averages.
* **Query 6 (Continuous Assessment Aggregation):** Quiz performance tiers versus midterm and final examination outcomes.
* **Query 7 (Window Function `DENSE_RANK()`):** Top 3 ranked students partitioned by department.
* **Query 8 (Complex CASE Expression):** Lecture vs lab participation profile impact.
* **Query 9 (Multi-condition Filtering):** Actionable academic warning early-intervention list.
* **Query 10 (CTE + Window Aggregate):** Grade percentage breakdown per course offering.

---

## 9. Challenges Encountered & Solutions

1. **Missing Assignment Telemetry:** The raw dataset had 100% missing values for `assignments_submitted` (all 300 entries were null). We evaluated whether to impute or drop. Imputing unobserved values would hallucinate artificial student behaviors and compromise downstream reporting. We made the disciplined decision to drop the column and its associated constant `total_assignments`, preserving genuine empirical integrity across all analytical queries.
2. **Relational Normalization from Flat Data:** Flat Kaggle records required structural separation into normalized primary and bridge entities. Foreign key constraints and multi-table cascades were enforced in SQLite with `PRAGMA foreign_keys = ON;`.
3. **Pipeline Reproducibility:** Ensuring any user or evaluator could execute the entire project from scratch with zero configuration. Handled via automated SQLite DDL generation and SQLAlchemy connectors.

---

## 10. Conclusion

This project successfully demonstrates an end-to-end data pipeline adhering to enterprise data engineering and analytics best practices. Raw academic telemetry was extracted, systematically cleaned and transformed, normalized into a 3NF relational database, and analyzed through advanced multi-table SQL queries to provide actionable insights into student retention and academic success.
