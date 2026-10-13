"""
Phase 7: SQL Analysis & Reporting Module
Executes 10 analytical SQL queries against the relational SQLite database
and exports formatted tabular reports to reports/sql_reports_output.md.
"""

import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "student_performance.db")
REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "reports")
REPORT_MD_PATH = os.path.join(REPORTS_DIR, "sql_reports_output.md")

QUERIES = [
    {
        "id": 1,
        "title": "Academic Department Performance Benchmark",
        "concepts": "JOIN, GROUP BY, Aggregate functions (COUNT, AVG, ROUND)",
        "sql": """
        SELECT 
            c.department,
            c.course_name,
            COUNT(a.student_id) AS total_enrolled,
            ROUND(AVG(a.midterm_marks), 2) AS avg_midterm_score,
            ROUND(AVG(a.final_marks), 2) AS avg_final_score,
            ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
            ROUND(AVG(att.overall_attendance_pct), 2) AS avg_attendance_pct
        FROM courses c
        JOIN academic_assessments a ON c.course_id = a.course_id
        JOIN attendance_records att ON a.student_id = att.student_id AND a.course_id = att.course_id
        GROUP BY c.department, c.course_name
        ORDER BY avg_composite_score DESC;
        """
    },
    {
        "id": 2,
        "title": "Performance & Risk Breakdown by Attendance Tier",
        "concepts": "JOIN, GROUP BY, CASE statements, Conditional Aggregation",
        "sql": """
        SELECT 
            att.attendance_tier,
            COUNT(s.student_id) AS total_students,
            ROUND(AVG(att.overall_attendance_pct), 2) AS avg_attendance_rate,
            ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
            SUM(CASE WHEN a.letter_grade IN ('A', 'B') THEN 1 ELSE 0 END) AS high_achievers_count,
            SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count,
            ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) / COUNT(s.student_id), 2) AS high_risk_percentage
        FROM attendance_records att
        JOIN students s ON att.student_id = s.student_id
        JOIN academic_assessments a ON s.student_id = a.student_id
        GROUP BY att.attendance_tier
        ORDER BY avg_composite_score DESC;
        """
    },
    {
        "id": 3,
        "title": "Dean's Honor List Recognition",
        "concepts": "Multi-table JOIN, WHERE clause, Multi-column Ordering",
        "sql": """
        SELECT 
            s.student_id,
            s.first_name || ' ' || s.last_name AS full_name,
            s.gender,
            c.course_code,
            s.previous_gpa,
            att.overall_attendance_pct,
            a.composite_score,
            a.letter_grade,
            a.academic_standing
        FROM students s
        JOIN academic_assessments a ON s.student_id = a.student_id
        JOIN attendance_records att ON s.student_id = att.student_id
        JOIN courses c ON a.course_id = c.course_id
        WHERE a.academic_standing = "Dean's Honor List"
        ORDER BY a.composite_score DESC, att.overall_attendance_pct DESC;
        """
    },
    {
        "id": 4,
        "title": "Dropout Risk Demographics (Gender & Age Groups)",
        "concepts": "GROUP BY, HAVING, CASE WHEN, Filtering on Cohort Thresholds",
        "sql": """
        SELECT 
            s.gender,
            s.age_group,
            COUNT(s.student_id) AS total_students,
            ROUND(AVG(s.previous_gpa), 2) AS avg_incoming_gpa,
            SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) AS high_risk_count,
            ROUND(100.0 * SUM(CASE WHEN a.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) / COUNT(s.student_id), 2) AS high_risk_pct,
            ROUND(AVG(a.composite_score), 2) AS cohort_avg_score
        FROM students s
        JOIN academic_assessments a ON s.student_id = a.student_id
        GROUP BY s.gender, s.age_group
        HAVING COUNT(s.student_id) >= 10
        ORDER BY high_risk_pct DESC;
        """
    },
    {
        "id": 5,
        "title": "Students Performing Above Department Average",
        "concepts": "Correlated Scalar Subquery, Mathematical Column Expressions, LIMIT",
        "sql": """
        SELECT 
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            c.course_code,
            a.final_marks,
            ROUND((SELECT AVG(final_marks) FROM academic_assessments WHERE course_id = a.course_id), 2) AS course_avg_final,
            ROUND(a.final_marks - (SELECT AVG(final_marks) FROM academic_assessments WHERE course_id = a.course_id), 2) AS score_margin
        FROM academic_assessments a
        JOIN students s ON a.student_id = s.student_id
        JOIN courses c ON a.course_id = c.course_id
        WHERE a.final_marks > (
            SELECT AVG(sub.final_marks)
            FROM academic_assessments sub
            WHERE sub.course_id = a.course_id
        )
        ORDER BY score_margin DESC
        LIMIT 10;
        """
    },
    {
        "id": 6,
        "title": "Continuous Assessment (Quiz Tiers) vs Examination Performance",
        "concepts": "CASE WHEN, GROUP BY, Aggregate metric comparison across continuous assessment tiers",
        "sql": """
        SELECT 
            CASE 
                WHEN a.avg_quiz_score >= 8.0 THEN 'High Quiz Tier (>=8.0)'
                WHEN a.avg_quiz_score >= 6.0 THEN 'Mid Quiz Tier (6.0-7.9)'
                WHEN a.avg_quiz_score >= 4.0 THEN 'Developing Quiz Tier (4.0-5.9)'
                ELSE 'Low Quiz Tier (<4.0)'
            END AS quiz_performance_tier,
            COUNT(a.student_id) AS student_count,
            ROUND(AVG(a.avg_quiz_score), 2) AS avg_quiz_grade,
            ROUND(AVG(a.midterm_marks), 2) AS avg_midterm_marks,
            ROUND(AVG(a.final_marks), 2) AS avg_final_marks,
            ROUND(AVG(a.composite_score), 2) AS avg_composite_score
        FROM academic_assessments a
        GROUP BY quiz_performance_tier
        ORDER BY avg_composite_score DESC;
        """
    },
    {
        "id": 7,
        "title": "Top 3 Ranked Students per Department",
        "concepts": "Common Table Expression (CTE), Window Function (DENSE_RANK() OVER PARTITION BY)",
        "sql": """
        WITH RankedStudents AS (
            SELECT 
                c.department,
                s.student_id,
                s.first_name || ' ' || s.last_name AS student_name,
                a.composite_score,
                a.letter_grade,
                DENSE_RANK() OVER (PARTITION BY c.department ORDER BY a.composite_score DESC) AS dept_rank
            FROM academic_assessments a
            JOIN students s ON a.student_id = s.student_id
            JOIN courses c ON a.course_id = c.course_id
        )
        SELECT 
            department,
            dept_rank,
            student_id,
            student_name,
            composite_score,
            letter_grade
        FROM RankedStudents
        WHERE dept_rank <= 3
        ORDER BY department, dept_rank;
        """
    },
    {
        "id": 8,
        "title": "Lab Participation Gap Impact Analysis",
        "concepts": "Complex CASE expressions, Multi-table JOIN, Statistical Grouping",
        "sql": """
        SELECT 
            CASE 
                WHEN att.lab_attendance_pct >= 80.0 AND att.lecture_attendance_pct >= 80.0 THEN 'High Lecture & High Lab'
                WHEN att.lab_attendance_pct < 50.0 AND att.lecture_attendance_pct >= 70.0 THEN 'High Lecture & Low Lab'
                WHEN att.lab_attendance_pct >= 70.0 AND att.lecture_attendance_pct < 50.0 THEN 'Low Lecture & High Lab'
                ELSE 'Balanced / Moderate'
            END AS participation_profile,
            COUNT(s.student_id) AS student_count,
            ROUND(AVG(a.final_marks), 2) AS avg_final_marks,
            ROUND(AVG(a.composite_score), 2) AS avg_composite_score,
            ROUND(AVG(s.previous_gpa), 2) AS avg_previous_gpa
        FROM attendance_records att
        JOIN academic_assessments a ON att.student_id = a.student_id
        JOIN students s ON att.student_id = s.student_id
        GROUP BY participation_profile
        ORDER BY avg_composite_score DESC;
        """
    },
    {
        "id": 9,
        "title": "Early Intervention & Academic Warning Roster",
        "concepts": "Complex boolean filtering, Multi-table JOIN, Risk mitigation reporting",
        "sql": """
        SELECT 
            s.student_id,
            s.first_name || ' ' || s.last_name AS student_name,
            c.course_name,
            att.attendance_tier,
            att.overall_attendance_pct,
            a.composite_score,
            a.letter_grade,
            a.dropout_risk
        FROM academic_assessments a
        JOIN students s ON a.student_id = s.student_id
        JOIN courses c ON a.course_id = c.course_id
        JOIN attendance_records att ON a.student_id = att.student_id
        WHERE a.dropout_risk = 'High Risk'
          AND (att.overall_attendance_pct < 40.0 OR a.composite_score < 50.0)
        ORDER BY a.composite_score ASC, att.overall_attendance_pct ASC
        LIMIT 10;
        """
    },
    {
        "id": 10,
        "title": "Grade Distribution Share per Course (Window Analytic Query)",
        "concepts": "CTE, Window Aggregate SUM() OVER (PARTITION BY), Percentage Distribution",
        "sql": """
        WITH GradeBreakdown AS (
            SELECT 
                c.course_code,
                a.letter_grade,
                COUNT(a.student_id) AS grade_count,
                SUM(COUNT(a.student_id)) OVER (PARTITION BY c.course_code) AS course_total
            FROM academic_assessments a
            JOIN courses c ON a.course_id = c.course_id
            GROUP BY c.course_code, a.letter_grade
        )
        SELECT 
            course_code,
            letter_grade,
            grade_count,
            course_total,
            ROUND(100.0 * grade_count / course_total, 2) AS grade_percentage
        FROM GradeBreakdown
        ORDER BY course_code, letter_grade;
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
        "# Deliverable 5: SQL Analytical Reports Output\n",
        "**Project:** End-to-End ETL & Academic Performance Pipeline  ",
        "**Database Engine:** SQLite / ANSI SQL Compliant  ",
        "**Total Queries Executed:** 10  \n",
        "---\n"
    ]
    
    results = []
    
    for q in QUERIES:
        qid = q["id"]
        title = q["title"]
        concepts = q["concepts"]
        sql = q["sql"].strip()
        
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
