# End-to-End ETL & Academic Performance Pipeline

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20SQLAlchemy-green.svg)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-orange.svg)](https://pandas.pydata.org/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

An enterprise-grade, reproducible **End-to-End ETL (Extract, Transform, Load) and Data Analysis Pipeline** built with Python, Pandas, SQLAlchemy, and SQLite on a real-world educational dataset.

```
       RAW DATA (Kaggle)
              │
              ▼
         EXTRACTION (Python)
              │
              ▼
    EXPLORATORY DATA ANALYSIS (EDA)
              │
              ▼
    CLEANING & TRANSFORMATION (Pandas)
              │
              ▼
    ENTITY NORMALIZATION (3 Relational Tables)
              │
              ▼
        LOAD (SQLAlchemy → SQLite DB)
              │
              ▼
    SQL REPORTING & ANALYTICAL INSIGHTS (10 Queries)
```

---

## Project Structure

```
student-performance-analysis/
│
├── data/
│   ├── raw/
│   │   └── student_dropout_behavior_raw.csv    # Preserved original Kaggle dataset (300 records)
│   └── processed/
│       ├── students.csv                        # Normalized students entity (300 rows)
│       ├── attendance_records.csv              # Normalized attendance logs (300 rows)
│       └── academic_assessments.csv            # Normalized exam & risk logs (300 rows)
│
├── database/
│   ├── student_performance.db                 # SQLite relational database file
│   ├── schema_and_queries.sql                  # DDL schemas (PK/FK/CHECK) + 10 SQL queries
│   ├── ERD_DIAGRAM.md                          # Mermaid ERD & constraint catalog
│   └── erd_diagram.png                         # Rendered ERD architecture diagram
│
├── notebooks/
│   └── student_performance_etl_pipeline.ipynb  # Interactive Jupyter Notebook walkthrough
│
├── reports/
│   └── sql_reports_output.md                   # Full outputs of 10 SQL reporting queries
│
├── src/
│   ├── extract.py                              # Phase 1: Ingestion & raw data preservation
│   ├── eda.py                                  # Phase 2: EDA, quality checks & distributions
│   ├── transform.py                            # Phase 3: Cleaning, imputation & normalization
│   ├── analysis.py                             # Phase 4: Core questions & business insights
│   ├── load.py                                 # Phase 5 & 6: SQLAlchemy automated database loader
│   └── sql_reporting.py                        # Phase 7: Automated SQL execution & reporting
│
├── visualizations/
│   ├── 01_grade_distributions.png              # Exam score distributions
│   ├── 02_attendance_vs_performance.png        # Lecture & lab scatter plots
│   ├── 03_correlation_matrix.png               # Correlation heatmap
│   ├── 04_grade_by_attendance_tier.png         # Attendance boxplot analysis
│   └── 05_dropout_risk_breakdown.png           # Risk category distribution
│
├── main_pipeline.py                            # Master one-click end-to-end execution runner
├── PROJECT_REPORT.md                           # Comprehensive final capstone project report
├── EXTRACTION_AND_EDA_REPORT.md                # Phase 1 & 2 detailed documentation
├── TRANSFORMATION_AND_ANALYSIS_REPORT.md       # Phase 3 & 4 detailed documentation
├── DATABASE_AND_REPORTING_REPORT.md            # Phase 5, 6 & 7 detailed documentation
└── README.md                                   # Project overview and navigation
```

---

## Multi-Stage Engineering & Implementation Roadmap

The project is built across three cohesive engineering milestones:

* **Milestone 1: Ingestion, Extraction & Exploratory Data Analysis (Phases 1 & 2)**
  * Raw dataset acquisition & preservation (`data/raw/`).
  * Ingestion logic (`src/extract.py`).
  * Exploratory Data Analysis & Data Quality Audit (`src/eda.py`).
  * Diagnostic visualizations (`visualizations/01_...`, `02_...`, `03_...`).
* **Milestone 2: Cleaning, Transformation, Normalization & Insights (Phases 3 & 4)**
  * Missing value handling & string formatting (`src/transform.py`).
  * Calculated metrics: composite score (100-pt scale), letter grades, rule-based dropout risk tiers.
  * Relational entity normalization into 3 CSV tables (`data/processed/`).
  * Analytical evaluations & research questions (`src/analysis.py`, `visualizations/04_...`, `05_...`).
* **Milestone 3: Database Design, Automated ETL Loading & SQL Reporting (Phases 5, 6 & 7)**
  * Relational database schema with PK, FK, and CHECK constraints (`database/schema_and_queries.sql`).
  * Entity Relationship Diagram (`database/ERD_DIAGRAM.md`, `erd_diagram.png`).
  * SQLAlchemy database loading pipeline (`src/load.py`).
  * 10 multi-table SQL analytical reports (`src/sql_reporting.py`, `reports/sql_reports_output.md`).
  * One-click master pipeline (`main_pipeline.py`) & Jupyter notebook (`notebooks/`).
  * Final Project Report (`PROJECT_REPORT.md`).

---

## Quickstart: Running the Pipeline

### 1. Prerequisites & Installation
Ensure Python 3.10+ is installed:
```bash
pip install -r requirements.txt
# or install directly:
pip install pandas numpy sqlalchemy matplotlib seaborn tabulate
```

### 2. Run the Entire Pipeline in One Click
```bash
python main_pipeline.py
```
This automatically extracts the raw data, executes EDA, cleans and normalizes tables, loads SQLite (`student_performance.db`), runs 10 SQL queries, and generates reports.

---

## SQL Reporting Capabilities (Phase 7 Highlights)

The pipeline executes 10 advanced SQL queries illustrating:
1. **Multi-Table JOINs & Aggregations:** Performance and risk breakdown by attendance tier.
2. **Demographic Grouping & HAVING:** Dropout risk distribution by gender and age cohort.
3. **Multi-table JOIN & WHERE Filtering:** Identifying Dean's Honor List recipients.
4. **Conditional CASE Statements:** Quiz performance tiers vs examination outcomes.
5. **Scalar Subqueries:** Pinpointing students scoring above cohort average final marks.
6. **Complex CASE Expressions & Multi-Table JOIN:** Lecture vs lab participation profile analysis.
7. **Multi-condition Filtering:** Actionable academic early-intervention roster for high-risk students.
8. **Window Functions (`DENSE_RANK()`):** Top 10 students by composite score.
9. **Common Table Expressions (CTEs) & Window Aggregates:** Grade distribution percentages across full cohort.
10. **Conditional CASE & GROUP BY:** Prior GPA bands vs current academic performance.

---

## Author
* **Prajjwal Gyawali**  
* GitHub: [@PrajjwalGyawali](https://github.com/PrajjwalGyawali)  
* Repository: [student-performance-analysis](https://github.com/PrajjwalGyawali/student-performance-analysis)
