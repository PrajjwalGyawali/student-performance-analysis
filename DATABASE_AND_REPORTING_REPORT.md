# Milestone 3 Documentation: Database Design, ETL Loading & SQL Reporting

**Capstone Project:** End-to-End ETL & Academic Performance Pipeline  
**Milestone:** Phase 5, 6 & 7 Engineering Documentation  
**Status:** Completed.  
**Phases Covered:**  
- **Phase 5:** Relational Database Schema Design (DDL + Constraints)  
- **Phase 6:** Automated ETL Loading via SQLAlchemy into SQLite  
- **Phase 7:** SQL Analytical Reporting (10 Multi-Table Queries)  

---

## 1. Summary of Milestone 3 Objectives

This milestone concludes the capstone pipeline by persisting all three normalized DataFrames into a production-grade SQLite relational database, enforcing referential integrity through PK/FK/CHECK constraints, and executing 10 advanced multi-table SQL analytical queries that surface academic insights suitable for dashboards or reporting tools.

---

## 2. Phase 5: Relational Database Schema Design

### 2.1 Database Technology
- **Engine:** SQLite (via SQLAlchemy ORM)
- **File:** `database/student_performance.db`
- **Schema File:** `database/schema_and_queries.sql`

### 2.2 Three-Table Relational Model

| Table | Rows | Primary Key | Foreign Keys |
|-------|------|-------------|--------------|
| `students` | 300 | `student_id` | - |
| `attendance_records` | 300 | `attendance_id` | `student_id` |
| `academic_assessments` | 300 | `assessment_id` | `student_id` |

*Note: The raw Kaggle dataset contains no curriculum, course, or department telemetry. The schema intentionally normalizes only genuine student entities to preserve analytical integrity.*

### 2.3 Integrity Constraints Applied

| Table | Constraint | Rule |
|-------|-----------|------|
| `students` | CHECK | `age BETWEEN 16 AND 80` |
| `students` | CHECK | `gender IN ('Male','Female','Other')` |
| `students` | CHECK | `previous_gpa BETWEEN 0.0 AND 4.0` |
| `attendance_records` | FK + CASCADE | `student_id REFERENCES students(student_id)` |
| `attendance_records` | CHECK | `lectures_attended <= total_lectures` |
| `attendance_records` | CHECK | `labs_attended <= total_lab_sessions` |
| `academic_assessments` | CHECK | `quiz1-3 BETWEEN 0.0 AND 10.0` |
| `academic_assessments` | CHECK | `midterm_marks BETWEEN 0.0 AND 30.0` |
| `academic_assessments` | CHECK | `final_marks BETWEEN 0.0 AND 50.0` |
| `academic_assessments` | CHECK | `composite_score BETWEEN 0.0 AND 100.0` |
| `academic_assessments` | FK + CASCADE | `student_id REFERENCES students(student_id)` |

### 2.4 ERD (Entity Relationship Diagram)
- Mermaid ERD: `database/ERD_DIAGRAM.md`
- Visual PNG: `database/erd_diagram.png`

Relationships:
- `STUDENTS` 1-to-1 `ATTENDANCE_RECORDS` (via `student_id`)
- `STUDENTS` 1-to-1 `ACADEMIC_ASSESSMENTS` (via `student_id`)

---

## 3. Phase 6: Automated ETL Database Loading (src/load.py)

### 3.1 Loading Process
1. SQLAlchemy engine created pointing to `database/student_performance.db`.
2. `PRAGMA foreign_keys = ON` activated for FK enforcement.
3. DDL schema executed via `sqlite3.executescript()` to handle multi-statement SQL.
4. DataFrames loaded in FK-safe insertion order:
   - First: `students` (parent table, no FK dependencies)
   - Then: `attendance_records` and `academic_assessments` (child tables referencing `students`)
5. Post-load verification: `SELECT COUNT(*)` executed for all 3 tables.

### 3.2 Verification Output

| Table | Rows Loaded |
|-------|------------|
| `students` | 300 |
| `attendance_records` | 300 |
| `academic_assessments` | 300 |

---

## 4. Phase 7: SQL Analytical Reporting (src/sql_reporting.py)

10 analytical SQL queries executed; output saved to `reports/sql_reports_output.md`.

### 4.1 Summary of All 10 SQL Queries

| # | Query Title | SQL Techniques Used |
|---|-------------|-------------------|
| 1 | Performance & Risk Breakdown by Attendance Tier | JOIN, GROUP BY, CASE, AVG |
| 2 | Dropout Risk Distribution by Gender & Age Group | JOIN, GROUP BY, HAVING, AVG |
| 3 | Dean's Honor List Recognition Roster | Multi-table JOIN, WHERE, ORDER BY |
| 4 | Quiz Performance Tier vs Examination Outcomes | CASE WHEN, GROUP BY, Aggregates |
| 5 | Students Scoring Above Cohort Average Final Mark | Scalar Subquery, JOIN, LIMIT |
| 6 | Lab vs Lecture Participation Profile Analysis | Complex CASE, Multi-table JOIN |
| 7 | Early Intervention Roster for High-Risk Students | Multi-condition WHERE, Multi-table JOIN |
| 8 | Overall Top-10 Students by Composite Score | CTE, `DENSE_RANK() OVER (ORDER BY)` |
| 9 | Grade Distribution Percentage Across Cohort | CTE, Window `SUM() OVER ()` |
| 10 | Incoming GPA Band vs Current Composite Score | CASE WHEN, GROUP BY, HAVING |

### 4.2 Key SQL Insights
- Attendance-tier composite scores differ only slightly: 'Excellent' tier averaged 71.34 vs 69.25 in 'Critical' tier.
- 149 students (49.7%) carry the rule-based High Risk label (triggered by low attendance, low composite, or low previous GPA).
- 11 students (3.7%) qualify for the Dean's Honor List ($\ge 85$ composite + $\ge 80\%$ attendance).
- Scalar subqueries and window functions enable cohort-relative benchmarks without table denormalization.
- CTE approach ensures grade distribution percentages are computed cleanly in a single pass.

---

## 5. One-Click Pipeline: main_pipeline.py

All 7 phases orchestrated via a single master script:

```bash
python main_pipeline.py
```

Execution sequence:
1. `extract.py` - loads raw CSV, preserves source data
2. `eda.py` - generates EDA statistics and diagnostic plots
3. `transform.py` - cleans data, engineers features, normalizes into 3 tables
4. `analysis.py` - answers 5 core research questions with plots
5. `load.py` - creates SQLite schema and loads all 3 tables
6. `sql_reporting.py` - executes 10 SQL queries, saves markdown report

---

## 6. Deliverables Summary

| Deliverable | File | Status |
|------------|------|--------|
| Raw Dataset | `data/raw/student_dropout_behavior_raw.csv` | Preserved (300 rows) |
| EDA Report | `EXTRACTION_AND_EDA_REPORT.md` | Complete |
| EDA Visualizations | `visualizations/01-03_*.png` | Complete |
| Cleaned + Normalized CSVs | `data/processed/` | 3 CSVs Complete |
| Analysis Report | `TRANSFORMATION_AND_ANALYSIS_REPORT.md` | Complete |
| Analysis Visualizations | `visualizations/04-05_*.png` | Complete |
| SQLite Database | `database/student_performance.db` | Complete |
| DDL Schema | `database/schema_and_queries.sql` | 3 Tables + 10 Queries |
| ERD Diagram | `database/ERD_DIAGRAM.md` + `.png` | Complete |
| SQL Reports | `reports/sql_reports_output.md` | 10 Reports Complete |
| Master Pipeline | `main_pipeline.py` | Complete |
| Jupyter Notebook | `notebooks/student_performance_etl_pipeline.ipynb` | Complete |
| Final Project Report | `PROJECT_REPORT.md` | Complete |
