"""
Phase 7: SQL Analysis & Reporting Module
Executes 10 analytical SQL queries against the relational SQLite database
and exports formatted tabular reports to reports/sql_reports_output.md.

Tables used: students, attendance_records, academic_assessments (3 tables only).
No courses table — the raw dataset contains no real course/department data.
"""

import os
import sqlite3
import pandas as pd

DB_PATH     = os.path.join(os.path.dirname(__file__), "..", "database", "student_performance.db")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
REPORT_MD_PATH = os.path.join(REPORTS_DIR, "sql_reports_output.md")

QUERIES = [
    {
        "id": 1,
        "title": "Performance & Risk Breakdown by Attendance Tier",
        "concepts": "JOIN, GROUP BY, CASE, Conditional Aggregation",
        "sql": """
        SELECT
            att.attendance_tier,
            COUNT(s.student_id)                                                               AS total_students,
            ROUND(AVG(att.overall_attendance_pct), 2)                                         AS avg_attendance_pct,
            ROUND(AVG(a.composite_score), 2)                                                  AS avg_composite_score,
            ROUND(AVG(a.final_marks), 2)                                                      AS avg_final_marks,
            SUM(CASE WHEN a.letter_grade IN ('A', 'B') THEN 1 ELSE 0 END)                    AS high_achievers,
            SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)                    AS high_risk_count,
            ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)
                  / COUNT(s.student_id), 2)                                                   AS high_risk_pct
        FROM attendance_records att
        JOIN students s             ON att.student_id = s.student_id
        JOIN academic_assessments a ON att.student_id = a.student_id
        GROUP BY att.attendance_tier
        ORDER BY avg_composite_score DESC;
        """
    },
    {
        "id": 2,
        "title": "Dropout Risk Label Distribution by Gender & Age Group",
        "concepts": "GROUP BY, HAVING, Conditional Aggregation",
        "sql": """
        SELECT
            s.gender,
            s.age_group,
            COUNT(s.student_id)                                                               AS total_students,
            ROUND(AVG(s.previous_gpa), 2)                                                     AS avg_gpa,
            SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)                    AS high_risk_count,
            ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END)
                  / COUNT(s.student_id), 2)                                                   AS high_risk_pct,
            ROUND(AVG(a.composite_score), 2)                                                  AS avg_composite
        FROM students s
        JOIN academic_assessments a ON s.student_id = a.student_id
        GROUP BY s.gender, s.age_group
        HAVING COUNT(s.student_id) >= 10
        ORDER BY high_risk_pct DESC;
        """
    },
    {
        "id": 3,
        "title": "Dean's Honor List Recognition",
        "concepts": "Multi-table JOIN, WHERE clause, ORDER BY",
        "sql": """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name   AS full_name,
            s.gender,
            s.age,
            s.previous_gpa,
            att.overall_attendance_pct,
            a.composite_score,
            a.letter_grade,
            a.academic_standing
        FROM students s
        JOIN academic_assessments a  ON s.student_id = a.student_id
        JOIN attendance_records att  ON s.student_id = att.student_id
        WHERE a.academic_standing = "Dean's Honor List"
        ORDER BY a.composite_score DESC, att.overall_attendance_pct DESC;
        """
    },
    {
        "id": 4,
        "title": "Quiz Performance Tier vs Examination Outcomes",
        "concepts": "CASE WHEN, GROUP BY, Aggregate comparison",
        "sql": """
        SELECT
            CASE
                WHEN a.avg_quiz_score >= 8.0 THEN 'High Quiz Tier (>=8.0)'
                WHEN a.avg_quiz_score >= 6.0 THEN 'Mid Quiz Tier (6.0-7.9)'
                WHEN a.avg_quiz_score >= 4.0 THEN 'Developing Quiz Tier (4.0-5.9)'
                ELSE 'Low Quiz Tier (<4.0)'
            END                                     AS quiz_tier,
            COUNT(a.student_id)                     AS student_count,
            ROUND(AVG(a.avg_quiz_score),  2)        AS avg_quiz_score,
            ROUND(AVG(a.midterm_marks),   2)        AS avg_midterm,
            ROUND(AVG(a.final_marks),     2)        AS avg_final,
            ROUND(AVG(a.composite_score), 2)        AS avg_composite
        FROM academic_assessments a
        GROUP BY quiz_tier
        ORDER BY avg_composite DESC;
        """
    },
    {
        "id": 5,
        "title": "Students Scoring Above Cohort Average Final Mark",
        "concepts": "Scalar Subquery, JOIN, Mathematical Expressions, LIMIT",
        "sql": """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name           AS student_name,
            s.gender,
            s.age_group,
            a.final_marks,
            ROUND((SELECT AVG(final_marks) FROM academic_assessments), 2) AS cohort_avg_final,
            ROUND(a.final_marks - (SELECT AVG(final_marks) FROM academic_assessments), 2) AS margin_above_avg
        FROM academic_assessments a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.final_marks > (SELECT AVG(final_marks) FROM academic_assessments)
        ORDER BY margin_above_avg DESC
        LIMIT 15;
        """
    },
    {
        "id": 6,
        "title": "Lab vs Lecture Participation Profile Analysis",
        "concepts": "Complex CASE expressions, Multi-table JOIN, Statistical Grouping",
        "sql": """
        SELECT
            CASE
                WHEN att.lab_attendance_pct >= 80.0 AND att.lecture_attendance_pct >= 80.0 THEN 'High Lecture & High Lab'
                WHEN att.lab_attendance_pct <  50.0 AND att.lecture_attendance_pct >= 70.0 THEN 'High Lecture & Low Lab'
                WHEN att.lab_attendance_pct >= 70.0 AND att.lecture_attendance_pct <  50.0 THEN 'Low Lecture & High Lab'
                ELSE 'Balanced / Moderate'
            END                                       AS participation_profile,
            COUNT(s.student_id)                       AS student_count,
            ROUND(AVG(a.final_marks),     2)          AS avg_final_marks,
            ROUND(AVG(a.composite_score), 2)          AS avg_composite,
            ROUND(AVG(s.previous_gpa),    2)          AS avg_gpa
        FROM attendance_records att
        JOIN academic_assessments a ON att.student_id = a.student_id
        JOIN students s              ON att.student_id = s.student_id
        GROUP BY participation_profile
        ORDER BY avg_composite DESC;
        """
    },
    {
        "id": 7,
        "title": "Early Intervention Roster — High-Risk Students",
        "concepts": "Multi-condition WHERE filtering, Multi-table JOIN",
        "sql": """
        SELECT
            s.student_id,
            s.first_name || ' ' || s.last_name   AS student_name,
            s.gender,
            att.attendance_tier,
            att.overall_attendance_pct,
            a.composite_score,
            a.letter_grade,
            a.dropout_risk
        FROM academic_assessments a
        JOIN students s             ON a.student_id = s.student_id
        JOIN attendance_records att ON a.student_id = att.student_id
        WHERE a.dropout_risk = 'High Risk'
          AND (att.overall_attendance_pct < 40.0 OR a.composite_score < 50.0)
        ORDER BY a.composite_score ASC, att.overall_attendance_pct ASC
        LIMIT 10;
        """
    },
    {
        "id": 8,
        "title": "Overall Top-10 Students by Composite Score",
        "concepts": "CTE, Window Function DENSE_RANK() OVER (ORDER BY)",
        "sql": """
        WITH RankedStudents AS (
            SELECT
                s.student_id,
                s.first_name || ' ' || s.last_name  AS student_name,
                s.gender,
                s.age_group,
                a.composite_score,
                a.letter_grade,
                DENSE_RANK() OVER (ORDER BY a.composite_score DESC) AS overall_rank
            FROM academic_assessments a
            JOIN students s ON a.student_id = s.student_id
        )
        SELECT
            overall_rank,
            student_id,
            student_name,
            gender,
            age_group,
            composite_score,
            letter_grade
        FROM RankedStudents
        WHERE overall_rank <= 10
        ORDER BY overall_rank;
        """
    },
    {
        "id": 9,
        "title": "Grade Distribution Percentage Across Full Cohort",
        "concepts": "CTE, Window SUM() OVER (), Percentage Calculation",
        "sql": """
        WITH GradeBreakdown AS (
            SELECT
                a.letter_grade,
                COUNT(a.student_id)              AS grade_count,
                SUM(COUNT(a.student_id)) OVER () AS cohort_total
            FROM academic_assessments a
            GROUP BY a.letter_grade
        )
        SELECT
            letter_grade,
            grade_count,
            cohort_total,
            ROUND(100.0 * grade_count / cohort_total, 2) AS grade_pct
        FROM GradeBreakdown
        ORDER BY letter_grade;
        """
    },
    {
        "id": 10,
        "title": "Incoming GPA Band vs Current Composite Score",
        "concepts": "CASE WHEN, GROUP BY, HAVING, Aggregate comparison",
        "sql": """
        SELECT
            CASE
                WHEN s.previous_gpa >= 3.5 THEN 'High GPA (>=3.5)'
                WHEN s.previous_gpa >= 2.5 THEN 'Mid GPA (2.5-3.4)'
                WHEN s.previous_gpa >= 1.5 THEN 'Low GPA (1.5-2.4)'
                ELSE 'Very Low GPA (<1.5)'
            END                                       AS gpa_band,
            COUNT(s.student_id)                       AS student_count,
            ROUND(AVG(s.previous_gpa),    2)          AS avg_incoming_gpa,
            ROUND(AVG(a.composite_score), 2)          AS avg_composite,
            ROUND(AVG(a.final_marks),     2)          AS avg_final,
            SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count
        FROM students s
        JOIN academic_assessments a ON s.student_id = a.student_id
        GROUP BY gpa_band
        HAVING COUNT(s.student_id) >= 5
        ORDER BY avg_incoming_gpa DESC;
        """
    }
]


def generate_sql_reports(db_path: str = DB_PATH) -> list:
    """
    Runs all 10 SQL reporting queries against SQLite and generates markdown report.
    """
    print("=" * 80)
    print("PHASE 7: SQL ANALYSIS & REPORTING (10 COMPREHENSIVE REPORTS)")
    print("=" * 80)

    os.makedirs(REPORTS_DIR, exist_ok=True)
    conn = sqlite3.connect(db_path)

    md_lines = [
        "# SQL Analytical Reports Output\n",
        "**Project:** End-to-End ETL & Academic Performance Pipeline  ",
        "**Database Engine:** SQLite / ANSI SQL Compliant  ",
        "**Tables:** students, attendance_records, academic_assessments  ",
        "**Total Queries Executed:** 10  \n",
        "> **Note:** `dropout_risk` is a rule-based label defined in `transform.py`, "
        "not observed dropout outcome data.  \n",
        "---\n"
    ]

    results = []

    for q in QUERIES:
        qid      = q["id"]
        title    = q["title"]
        concepts = q["concepts"]
        sql      = q["sql"].strip()

        print(f"\n--- Running Query {qid}: {title} ---")
        print(f"SQL Concepts: {concepts}")

        df_result = pd.read_sql_query(sql, conn)
        print(df_result.to_string(index=False))

        md_lines.append(f"## Query {qid}: {title}\n")
        md_lines.append(f"**Demonstrated SQL Concepts:** `{concepts}`\n")
        md_lines.append("```sql\n" + sql + "\n```\n")
        md_lines.append("### Query Execution Result:\n")
        md_lines.append(df_result.to_markdown(index=False))
        md_lines.append("\n\n---\n")

        results.append({"id": qid, "title": title, "data": df_result})

    conn.close()

    with open(REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print(f"\n[+] Full SQL reporting output saved to: {os.path.abspath(REPORT_MD_PATH)}")
    return results


if __name__ == "__main__":
    generate_sql_reports()
