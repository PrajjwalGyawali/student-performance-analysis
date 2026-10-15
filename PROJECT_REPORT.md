# Capstone Project Report: End-to-End ETL & Academic Performance Pipeline

**Project:** Capstone Project — End-to-End ETL & Academic Performance Pipeline  
**Author:** Prajjwal Gyawali  
**GitHub Repository:** [https://github.com/PrajjwalGyawali/student-performance-analysis.git](https://github.com/PrajjwalGyawali/student-performance-analysis.git)  
**Database Engine:** SQLite (ANSI SQL Compliant, relational engine via SQLAlchemy)  

---

## 1. Executive Summary & Objective

Higher education institutions face substantial challenges in identifying at-risk students before final examination failure and academic withdrawal occur. The objective of this capstone project is to architect an **End-to-End ETL (Extract, Transform, Load) and Analytical Pipeline** that ingests real-world raw academic data, performs exploratory data analysis and data quality auditing, transforms and normalizes the schema into multiple relational entities, loads the data into a relational database with strict referential integrity constraints, and generates multi-table SQL reports to derive actionable business and academic interventions.

The completed pipeline implements the full end-to-end data lifecycle:
$$\text{Raw Data} \longrightarrow \text{Extract} \longrightarrow \text{Explore (EDA)} \longrightarrow \text{Clean \& Transform} \longrightarrow \text{Normalize (3 Entities)} \longrightarrow \text{Relational Database} \longrightarrow \text{SQL Reporting} \longrightarrow \text{Academic Insights}$$

---

## 2. Dataset Overview & Data Acquisition (Phase 1)

* **Source Domain:** Education & Academic Learning Analytics
* **Origin:** Kaggle Dataset Repository (`muhammadkhubaibahmad/student-performance-and-clustering-dataset`)
* **Preservation Strategy:** The original dataset was preserved unmodified in [`data/raw/student_dropout_behavior_raw.csv`](data/raw/student_dropout_behavior_raw.csv).
* **Dataset Scale:** 300 records across 16 raw features.
* **Feature Schema:**
  * Identifiers & Demographics: `student_id`, `name`, `age`, `gender`, `previous_gpa`
  * Examination Marks: `quiz1_marks`, `quiz2_marks`, `quiz3_marks`, `midterm_marks`, `final_marks`
  * Assignment Telemetry: `total_assignments`, `assignments_submitted`
  * Attendance Tracking: `total_lectures`, `lectures_attended`, `total_lab_sessions`, `labs_attended`

The extraction logic was implemented in [`src/extract.py`](src/extract.py), verifying schema headers and data integrity prior to downstream ingestion.

---

## 3. Exploratory Data Analysis & Data Quality Audit (Phase 2)

EDA was executed through [`src/eda.py`](src/eda.py) to audit distributions and data quality issues:

### 3.1 Data Quality Findings
1. **Pervasive Missing Values:** `assignments_submitted` contained 300 missing (NaN) values (100% missing data in the raw extraction), representing a classic real-world incomplete sensor/telemetry collection failure.
2. **Duplicate Records:** 0 duplicate rows and 0 duplicate `student_id` entries were observed.
3. **Outlier Boundaries:** Using the Interquartile Range (IQR) method ($Q_1 - 1.5 \times \text{IQR}$ to $Q_3 + 1.5 \times \text{IQR}$), 3 lower-bound outliers were flagged in `final_marks` (students with 0 exam marks) and 2 lower-bound outliers in `previous_gpa` ($< 0.84$). These represent genuine academic failure cases rather than data collection errors.
4. **Demographic Balance:** Balanced cohort comprising 155 Female (51.7%) and 145 Male (48.3%) students aged 18 to 25 (mean age 21.55).

### 3.2 Visual Explorations
* [`visualizations/01_grade_distributions.png`](visualizations/01_grade_distributions.png): Visualized distributions for midterm (mean 19.97/30) and final marks (mean 37.38/50).
* [`visualizations/02_attendance_vs_performance.png`](visualizations/02_attendance_vs_performance.png): Examined attendance compliance versus exam achievement.
* [`visualizations/03_correlation_matrix.png`](visualizations/03_correlation_matrix.png): Inter-feature correlation analysis.

---

## 4. Data Cleaning, Transformation & Normalization (Phase 3)

Implemented in [`src/transform.py`](src/transform.py):

### 4.1 Cleaning Operations & Rationales
1. **String Standardization:** Standardized `name` (Title Case) and `gender` (Capitalized, whitespace stripped).
2. **Entity Attribute Decomposition:** Split `name` into `first_name` and `last_name` for granular attribute decomposition, structured sorting, indexing, and standardized reporting.
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
* **Dropout Risk Classification (Explicit Rule-Based Definition):** `High Risk` is explicitly defined by a deterministic business rule: student exhibits $\text{overall\_attendance\_pct} < 40\%$ OR $\text{composite\_score} < 45$ OR $\text{previous\_gpa} < 1.8$. *Note: This is a rule-based intervention label, not observed dropout outcome data.*

### 4.3 Relational Entity Splitting
To ensure analytical integrity, the raw flat dataset was normalized into **3 genuine relational tables** (avoiding any fabricated courses or departments):
1. `students.csv` (300 rows, 7 columns)
2. `attendance_records.csv` (300 rows, 10 columns)
3. `academic_assessments.csv` (300 rows, 12 columns)

---

## 5. Database Design & Relational Modeling (Phase 5)

* **RDBMS Engine:** SQLite / ANSI SQL Compliant (`database/student_performance.db`).
* **Design Strategy:** Normalized 3-table relational architecture linked by `student_id`.
* **ERD Specification:** Documented in [`database/ERD_DIAGRAM.md`](database/ERD_DIAGRAM.md) and [`database/erd_diagram.png`](database/erd_diagram.png).

```
[ students ] (1) ──────────< (1:1) [ attendance_records ]
      │
      └──────────────────< (1:1) [ academic_assessments ]
```

* **Constraints Enforced:**
  * Primary Keys on all tables (`student_id`, `attendance_id`, `assessment_id`).
  * Foreign Keys with `ON DELETE CASCADE` linking child tables to `students(student_id)`.
  * `CHECK` constraints on GPA ($0.0 \le \text{gpa} \le 4.0$), ages ($\ge 16$), score rubrics, and valid categorical enums.
  * Indexes on `gender`, `age_group`, `attendance_tier`, `dropout_risk`, and `letter_grade` for query performance.

---

## 6. ETL Loading Pipeline (Phase 6)

Implemented in [`src/load.py`](src/load.py):
* Uses `SQLAlchemy` to maintain database-agnostic connectivity.
* Automatically creates database tables directly from DDL in [`database/schema_and_queries.sql`](database/schema_and_queries.sql).
* Loads normalized Pandas DataFrames in strict dependency order (`students` parent table loaded prior to child tables).
* Validates post-load row counts:
  * `students`: 300 rows
  * `attendance_records`: 300 rows
  * `academic_assessments`: 300 rows

The master execution script [`main_pipeline.py`](main_pipeline.py) runs the entire extraction, cleaning, transformation, loading, and reporting lifecycle in **under 4.0 seconds**.

---

## 7. Data Analysis & Insights (Phase 4 & 7)

### 7.1 Five Core Analytical Questions
1. **How does attendance tier influence composite score?** Attendance tiers exhibit only slight variance: students in the `Excellent` tier averaged 71.34 vs 69.25 in `Critical` (a modest 2.1-point difference).
2. **What is the demographic distribution of dropout risk?** High-risk classification is elevated in male students (55.17%, 80 of 145) compared to female students (44.52%, 69 of 155), a 10.65 percentage point difference. Across age cohorts for all students, risk rates are relatively uniform: 50.00% (18–19), 50.44% (20–22), and 48.70% (23–25), with the 23–25 cohort exhibiting the lowest overall risk rate.
3. **What proportion achieves Dean's Honor List standing?** Exactly 11 students (3.67%) met the rigorous criteria of $\ge 80\%$ attendance and $\ge 85.0$ composite score.
4. **How predictive is continuous assessment (quizzes) for final examination success?** Students in the High Quiz Tier ($\ge 8.0$) achieved an average final exam mark of **41.91/50**, compared to **31.08/50** for the Low Quiz Tier ($< 4.0$).
5. **Does lab practical attendance impact final exams differently than lectures?** High lab attendance ($\ge 80\%$) averaged **37.79** on finals vs **34.86** for low lab attendance ($< 40\%$) (a **2.93-point** difference). In contrast, high lecture attendance ($\ge 80\%$) averaged **37.87** on finals vs **38.23** for low lecture attendance ($< 40\%$) (a **-0.36-point** difference).

### 7.2 Five Key Data-Driven Insights
1. **Attendance Tiers Differ Modestly:** Attendance-tier composite scores differ only slightly: 'Excellent' tier averaged **71.3** vs **69.2** for 'Critical' tier (a **2.1-point** gap). The Pearson correlation between overall attendance percentage and final marks is **r = 0.03**, indicating a very weak linear relationship in this cohort.
2. **Rule-Based High-Risk Classification:** Exactly **149 students (49.7% of cohort)** carry the 'High Risk' label. This is a rule-based classification defined in `transform.py`—a student is flagged High Risk when meeting ANY of: overall attendance $< 40\%$, composite score $< 45$, or previous GPA $< 1.8$. It does not represent observed dropout outcomes.
3. **Dean's Honor Cohort:** Exactly **11 students (3.7% of cohort)** achieved Dean's Honor List standing ($\ge 80\%$ attendance AND $\ge 85.0$ composite score).
4. **Lab vs Lecture Attendance:** Students with $\ge 80\%$ lab attendance averaged **37.8** on final exams vs **34.9** for $< 40\%$ lab attendance (**2.9-point** difference). For lectures, the same comparison gives **37.9** vs **38.2** (**-0.4-point** difference). Both effects are modest and should not be interpreted as causal.
5. **Historical GPA Linear Association:** Previous GPA vs final marks yielded Pearson **r = 0.10**, indicating that a student's prior GPA has very little linear association with their final exam score in this dataset. Similarly, previous GPA vs midterm yielded Pearson **r = 0.01**.

---

## 8. SQL Analysis & Reporting (Phase 7)

Documented in [`reports/sql_reports_output.md`](reports/sql_reports_output.md) and [`src/sql_reporting.py`](src/sql_reporting.py):
* **Query 1 (JOIN, GROUP BY, CASE):** Performance & risk breakdown by attendance tier.
* **Query 2 (GROUP BY, HAVING):** Dropout risk distribution by gender and age group.
* **Query 3 (Multi-table JOIN, WHERE, ORDER BY):** Dean's Honor List recognition roster.
* **Query 4 (CASE WHEN, GROUP BY, Aggregates):** Quiz performance tier vs examination outcomes.
* **Query 5 (Scalar Subquery, JOIN, LIMIT):** Students scoring above cohort average final mark.
* **Query 6 (Complex CASE expressions, Multi-table JOIN):** Lab vs lecture participation profile analysis.
* **Query 7 (Multi-condition Filtering, Multi-table JOIN):** Early intervention roster for high-risk students.
* **Query 8 (CTE, Window Function `DENSE_RANK()`):** Overall top-10 students by composite score.
* **Query 9 (CTE, Window `SUM() OVER ()`):** Grade distribution percentage across full cohort.
* **Query 10 (CASE WHEN, GROUP BY, HAVING):** Incoming GPA band vs current composite score.

---

## 9. Challenges Encountered & Solutions

1. **Missing Assignment Telemetry:** The raw dataset had 100% missing values for `assignments_submitted` (all 300 entries were null). We evaluated whether to impute or drop. Imputing unobserved values would hallucinate artificial student behaviors and compromise downstream reporting. We made the disciplined decision to drop the column and its associated constant `total_assignments`, preserving genuine empirical integrity across all analytical queries.
2. **Preserving Schema Authenticity (Removing Fabricated Tables):** Initial drafts considered adding synthetic course codes or department assignments. Because the underlying Kaggle dataset contains no real curriculum metadata, fabricating course entities violated analytical honesty. We redesigned the relational model into a clean, authentic 3-table schema (`students`, `attendance_records`, `academic_assessments`) linked by `student_id`.
3. **Pipeline Reproducibility:** Ensuring any user or evaluator could execute the entire project from scratch with zero configuration. Handled via automated SQLite DDL generation and SQLAlchemy connectors.

---

## 10. Conclusion

This project successfully demonstrates an end-to-end data pipeline adhering to enterprise data engineering and analytics best practices. Raw academic telemetry was extracted, systematically cleaned and transformed, normalized into an authentic 3-table relational database, and analyzed through advanced multi-table SQL queries to provide actionable insights into student retention and academic performance.
