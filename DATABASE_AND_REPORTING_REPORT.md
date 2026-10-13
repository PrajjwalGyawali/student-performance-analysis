# Milestone 3 Documentation: Database Design, ETL Loading & SQL Reporting

**Capstone Project:** End-to-End ETL & Academic Performance Pipeline
**Milestone:** Phase 5, 6 & 7 Engineering Documentation
**Status:** Milestone 3 (Day 3) - Completed and pushed to main branch.
**Phases Completed:**
- **Phase 5:** Relational Database Schema Design (DDL + Constraints)
- **Phase 6:** Automated ETL Loading via SQLAlchemy into SQLite
- **Phase 7:** SQL Analytical Reporting (10 Multi-Table Queries)

---

## 1. Summary of Milestone 3 Objectives

This milestone concludes the capstone pipeline by persisting all four normalized DataFrames into a production-grade SQLite relational database, enforcing referential integrity through PK/FK/CHECK constraints, and executing 10 advanced multi-table SQL analytical queries that surface academic insights suitable for dashboards or reporting tools.

---

## 2. Phase 5: Relational Database Schema Design

### 2.1 Database Technology
- **Engine:** SQLite (via SQLAlchemy ORM)
- **File:** `database/student_performance.db`
- **Schema File:** `database/schema_and_queries.sql`

### 2.2 Four-Table Relational Model

| Table | Rows | Primary Key | Foreign Keys |
|-------|------|-------------|--------------|
| `students` | 300 | `student_id` | - |
| `courses` | 3 | `course_id` | - |
| `attendance_records` | 300 | `attendance_id` | `student_id`, `course_id` |
| `academic_assessments` | 300 | `assessment_id` | `student_id`, `course_id` |

### 2.3 Integrity Constraints Applied

| Table | Constraint | Rule |
|-------|-----------|------|
| `students` | CHECK | `age BETWEEN 16 AND 80` |
| `students` | CHECK | `gender IN ('Male','Female','Other')` |
| `students` | CHECK | `previous_gpa BETWEEN 0.0 AND 4.0` |
| `courses` | UNIQUE | `course_code` |
| `attendance_records` | FK + CASCADE | `student_id`, `course_id` |
| `academic_assessments` | CHECK | `quiz1_marks BETWEEN 0.0 AND 10.0` |
| `academic_assessments` | CHECK | `composite_score BETWEEN 0.0 AND 100.0` |
| `academic_assessments` | FK + CASCADE | `student_id`, `course_id` |

### 2.4 ERD (Entity Relationship Diagram)
- Mermaid ERD: `database/ERD_DIAGRAM.md`
- Visual PNG: `database/erd_diagram.png`

Relationships:
- `STUDENTS` 1-to-Many `ATTENDANCE_RECORDS`
- `STUDENTS` 1-to-Many `ACADEMIC_ASSESSMENTS`
- `COURSES` 1-to-Many `ATTENDANCE_RECORDS`
- `COURSES` 1-to-Many `ACADEMIC_ASSESSMENTS`

---

## 3. Phase 6: Automated ETL Database Loading (src/load.py)

### 3.1 Loading Process
1. SQLAlchemy engine created pointing to `database/student_performance.db`.
2. `PRAGMA foreign_keys = ON` activated for FK enforcement.
3. DDL schema executed via `sqlite3.executescript()` to handle multi-statement SQL.
4. DataFrames loaded in FK-safe insertion order:
   - First: `students` and `courses` (parent tables, no FK dependencies)
   - Then: `attendance_records` and `academic_assessments` (child tables)
5. Post-load verification: `SELECT COUNT(*)` executed for all 4 tables.

### 3.2 Verification Output

| Table | Rows Loaded |
|-------|------------|
| `students` | 300 |
| `courses` | 3 |
| `attendance_records` | 300 |
| `academic_assessments` | 300 |

---

## 4. Phase 7: SQL Analytical Reporting (src/sql_reporting.py)

10 analytical SQL queries executed; output saved to `reports/sql_reports_output.md`.

### 4.1 Summary of All 10 SQL Queries

| # | Query Title | SQL Techniques Used |
|---|-------------|-------------------|
| 1 | Average Final Marks by Department | JOIN, GROUP BY, AVG |
| 2 | Student Count per Dropout Risk Tier | JOIN, GROUP BY, COUNT |
| 3 | Top 10 Students by Composite Score | JOIN, ORDER BY DESC, LIMIT |
| 4 | High-Risk Rate per Attendance Tier | JOIN, CASE, GROUP BY, HAVING |
| 5 | Dean's Honor List (Elite Students) | JOIN, WHERE, multiple conditions |
| 6 | Risk Rate by Age Group and Gender | JOIN, GROUP BY on two dimensions |
| 7 | Students Scoring Above Course Average | Scalar subquery, JOIN |
| 8 | Intra-Department Class Rank | `DENSE_RANK() OVER PARTITION` window function |
| 9 | Grade Distribution Percentage | CTE, COUNT, percentage calculation |
| 10 | Lab Attendance vs Final Exam Tier | CASE, GROUP BY, AVG |

### 4.2 Key SQL Insights
- Department performance is evenly distributed (CS: 38.07, DS: 37.49, SE: 36.56 avg final marks).
- 149 students (49.7%) are classified as High Risk - highest intervention priority.
- 11 students (3.7%) qualify for the Dean's Honor List (>=85 composite + >=80% attendance).
- Students scoring above their course average identified via scalar subquery for targeted support.
- Window functions used for per-department academic ranking without collapsing rows.
- CTE approach ensures grade distribution percentages are computed cleanly in a single pass.

---

## 5. One-Click Pipeline: main_pipeline.py

All 7 phases orchestrated via a single master script:

```bash
python main_pipeline.py
```

Execution sequence:
1. `extract.py` - loads raw CSV, preserves source data
2. `eda.py` - generates EDA statistics and 3 diagnostic plots
3. `transform.py` - cleans data, engineers features, normalizes into 4 tables
4. `analysis.py` - answers 5 core research questions with 3 plots
5. `load.py` - creates SQLite schema and loads all 4 tables
6. `sql_reporting.py` - executes 10 SQL queries, saves markdown report

---

## 6. Deliverables Summary (All 3 Milestones)

| Deliverable | File | Milestone |
|------------|------|----------|
| Raw Dataset | `data/raw/student_dropout_behavior_raw.csv` | Milestone 1 |
| EDA Report | `EXTRACTION_AND_EDA_REPORT.md` | Milestone 1 |
| EDA Visualizations | `visualizations/01-03_*.png` | Milestone 1 |
| Cleaned + Normalized CSVs | `data/processed/` | Milestone 2 |
| Analysis Report | `TRANSFORMATION_AND_ANALYSIS_REPORT.md` | Milestone 2 |
| Analysis Visualizations | `visualizations/04-06_*.png` | Milestone 2 |
| SQLite Database | `database/student_performance.db` | Milestone 3 |
| DDL Schema | `database/schema_and_queries.sql` | Milestone 3 |
| ERD Diagram | `database/ERD_DIAGRAM.md` + `.png` | Milestone 3 |
| SQL Reports | `reports/sql_reports_output.md` | Milestone 3 |
| Master Pipeline | `main_pipeline.py` | Milestone 3 |
| Jupyter Notebook | `notebooks/student_performance_etl_pipeline.ipynb` | Milestone 3 |
| Final Project Report | `PROJECT_REPORT.md` | Milestone 3 |

---

*All Milestone 3 (Day 3) work has been committed and pushed to the `main` branch.*
