# 3-Day Git Commit & Push Schedule

This repository is structured for a 3-day progressive development timeline matching the 7 ETL pipeline phases.

---

## 📅 Day 1 (Today): Ingestion, Extraction & Exploratory Data Analysis
**Phases Covered:** Phase 1 (Data Acquisition) & Phase 2 (EDA & Quality Audit)

**Committed Files:**
- `.gitignore` & `requirements.txt`
- `data/raw/student_dropout_behavior_raw.csv` (Preserved raw dataset)
- `src/extract.py` (Ingestion script)
- `src/eda.py` (EDA & Data Quality Audit script)
- `visualizations/01_grade_distributions.png`
- `visualizations/02_attendance_vs_performance.png`
- `visualizations/03_correlation_matrix.png`

**Status:** ✅ **Committed locally!**  
**To push Day 1 to GitHub, run:**
```powershell
cd c:\Users\LOQ\Desktop\Phython\student-performance-analysis
git push -u origin main
```

---

## 📅 Day 2 (Tomorrow): Cleaning, Transformation, Normalization & Insights
**Phases Covered:** Phase 3 (Data Cleaning & Normalization) & Phase 4 (Analytical Questions & Insights)

**Files to Commit:**
- `src/transform.py` (Cleaning, imputation & feature engineering)
- `data/processed/students.csv`
- `data/processed/courses.csv`
- `data/processed/attendance_records.csv`
- `data/processed/academic_assessments.csv`
- `src/analysis.py` (5 core analytical questions & business insights)
- `visualizations/04_grade_by_attendance_tier.png`
- `visualizations/05_dropout_risk_breakdown.png`
- `visualizations/06_department_performance.png`

**Commands to run on Day 2:**
```powershell
cd c:\Users\LOQ\Desktop\Phython\student-performance-analysis
git add src/transform.py data/processed/ src/analysis.py visualizations/04_grade_by_attendance_tier.png visualizations/05_dropout_risk_breakdown.png visualizations/06_department_performance.png
git commit -m "feat(day2): data cleaning, feature engineering, 4-table normalization and analytical insights"
git push origin main
```

---

## 📅 Day 3 (Day After Tomorrow): Database Architecture, Automated ETL Loading, SQL Reports & Deliverables
**Phases Covered:** Phase 5 (Database Design & ERD), Phase 6 (ETL Load), Phase 7 (SQL Reporting) & Final Documentation

**Files to Commit:**
- `database/schema_and_queries.sql` (DDL + 10 SQL queries)
- `database/student_performance.db` (SQLite relational database)
- `database/ERD_DIAGRAM.md` & `database/erd_diagram.png` (Entity Relationship Diagram)
- `src/load.py` (SQLAlchemy loader)
- `src/sql_reporting.py` (SQL query runner & exporter)
- `reports/sql_reports_output.md` (SQL results tables)
- `notebooks/student_performance_etl_pipeline.ipynb` (Jupyter Notebook)
- `main_pipeline.py` (Master pipeline execution runner)
- `PROJECT_REPORT.md` (Comprehensive Capstone Project Report)
- `README.md` (Repository documentation)

**Commands to run on Day 3:**
```powershell
cd c:\Users\LOQ\Desktop\Phython\student-performance-analysis
git add database/ src/load.py src/sql_reporting.py reports/ notebooks/ main_pipeline.py PROJECT_REPORT.md README.md
git commit -m "feat(day3): database schema, automated ETL loader, 10 SQL analytical reports, ERD and project report"
git push origin main
```
