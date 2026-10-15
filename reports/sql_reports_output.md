# SQL Analytical Reports Output

**Project:** End-to-End ETL & Academic Performance Pipeline  
**Database Engine:** SQLite / ANSI SQL Compliant  
**Tables:** students, attendance_records, academic_assessments  
**Total Queries Executed:** 10  

> **Note:** `dropout_risk` is a rule-based label defined in `transform.py`, not observed dropout outcome data.  

---

## Query 1: Performance & Risk Breakdown by Attendance Tier

**Demonstrated SQL Concepts:** `JOIN, GROUP BY, CASE, Conditional Aggregation`

```sql
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
```

### Query Execution Result:

| attendance_tier   |   total_students |   avg_attendance_pct |   avg_composite_score |   avg_final_marks |   high_achievers |   high_risk_count |   high_risk_pct |
|:------------------|-----------------:|---------------------:|----------------------:|------------------:|-----------------:|------------------:|----------------:|
| Irregular         |               65 |                49.83 |                 71.64 |             37.12 |               29 |                 7 |           10.77 |
| Excellent         |               37 |                87.99 |                 71.34 |             40.55 |               16 |                 8 |           21.62 |
| Critical          |              119 |                27.17 |                 69.25 |             37.06 |               46 |               119 |          100    |
| Satisfactory      |               79 |                69.34 |                 68.15 |             36.58 |               30 |                15 |           18.99 |


---

## Query 2: Dropout Risk Label Distribution by Gender & Age Group

**Demonstrated SQL Concepts:** `GROUP BY, HAVING, Conditional Aggregation`

```sql
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
```

### Query Execution Result:

| gender   | age_group   |   total_students |   avg_gpa |   high_risk_count |   high_risk_pct |   avg_composite |
|:---------|:------------|-----------------:|----------:|------------------:|----------------:|----------------:|
| Male     | 23-25       |               58 |      2.86 |                34 |           58.62 |           67.32 |
| Male     | 18-19       |               37 |      2.64 |                21 |           56.76 |           71.11 |
| Female   | 20-22       |               63 |      2.86 |                32 |           50.79 |           69.82 |
| Male     | 20-22       |               50 |      2.64 |                25 |           50    |           67.32 |
| Female   | 18-19       |               35 |      3.05 |                15 |           42.86 |           71.72 |
| Female   | 23-25       |               57 |      2.8  |                22 |           38.6  |           72.12 |


---

## Query 3: Dean's Honor List Recognition

**Demonstrated SQL Concepts:** `Multi-table JOIN, WHERE clause, ORDER BY`

```sql
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
```

### Query Execution Result:

|   student_id | full_name        | gender   |   age |   previous_gpa |   overall_attendance_pct |   composite_score | letter_grade   | academic_standing   |
|-------------:|:-----------------|:---------|------:|---------------:|-------------------------:|------------------:|:---------------|:--------------------|
|          250 | Angela Rodriguez | Female   |    25 |           3.19 |                    88.89 |            100    | A              | Dean's Honor List   |
|          280 | Karen Frost      | Female   |    25 |           2.43 |                    94.44 |             96.27 | A              | Dean's Honor List   |
|           71 | Susan James      | Male     |    22 |           3.78 |                    83.33 |             95.93 | A              | Dean's Honor List   |
|          148 | Amy George       | Female   |    20 |           2.48 |                    88.89 |             93.53 | A              | Dean's Honor List   |
|          149 | Jamie Kim        | Female   |    25 |           3.63 |                    83.33 |             91.77 | A              | Dean's Honor List   |
|          239 | Megan Brewer     | Female   |    18 |           2.31 |                   100    |             90.4  | A              | Dean's Honor List   |
|          212 | Cheryl Garcia    | Female   |    23 |           3.21 |                    88.89 |             89.2  | A              | Dean's Honor List   |
|           73 | Richard Davis    | Male     |    23 |           1.71 |                    88.89 |             86.9  | A              | Dean's Honor List   |
|          168 | David Hall       | Male     |    22 |           3.23 |                    83.33 |             86.63 | A              | Dean's Honor List   |
|          102 | Sandra Barr      | Male     |    22 |           2.71 |                    88.89 |             85.53 | A              | Dean's Honor List   |
|          216 | Kerry Church     | Female   |    24 |           2.68 |                   100    |             85.13 | A              | Dean's Honor List   |


---

## Query 4: Quiz Performance Tier vs Examination Outcomes

**Demonstrated SQL Concepts:** `CASE WHEN, GROUP BY, Aggregate comparison`

```sql
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
```

### Query Execution Result:

| quiz_tier                      |   student_count |   avg_quiz_score |   avg_midterm |   avg_final |   avg_composite |
|:-------------------------------|----------------:|-----------------:|--------------:|------------:|----------------:|
| High Quiz Tier (>=8.0)         |              24 |             8.49 |         19.55 |       41.91 |           78.43 |
| Mid Quiz Tier (6.0-7.9)        |             146 |             6.85 |         20.23 |       37.77 |           71.7  |
| Developing Quiz Tier (4.0-5.9) |             117 |             5.22 |         19.19 |       36.65 |           66.28 |
| Low Quiz Tier (<4.0)           |              13 |             3.43 |         24.85 |       31.08 |           62.8  |


---

## Query 5: Students Scoring Above Cohort Average Final Mark

**Demonstrated SQL Concepts:** `Scalar Subquery, JOIN, Mathematical Expressions, LIMIT`

```sql
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
```

### Query Execution Result:

|   student_id | student_name         | gender   | age_group   |   final_marks |   cohort_avg_final |   margin_above_avg |
|-------------:|:---------------------|:---------|:------------|--------------:|-------------------:|-------------------:|
|            6 | Austin Griffin       | Male     | 20-22       |            50 |              37.38 |              12.63 |
|            7 | Crystal Jordan       | Female   | 23-25       |            50 |              37.38 |              12.63 |
|           11 | Lawrence Powers      | Female   | 18-19       |            50 |              37.38 |              12.63 |
|           14 | Rita Olson           | Female   | 18-19       |            50 |              37.38 |              12.63 |
|           18 | Gregg Gonzales       | Female   | 20-22       |            50 |              37.38 |              12.63 |
|           20 | Mark Allen           | Female   | 20-22       |            50 |              37.38 |              12.63 |
|           28 | Michael Williamson   | Female   | 20-22       |            50 |              37.38 |              12.63 |
|           34 | Christopher Buchanan | Male     | 20-22       |            50 |              37.38 |              12.63 |
|           37 | Patricia Macias      | Female   | 20-22       |            50 |              37.38 |              12.63 |
|           43 | Melanie Cox          | Male     | 23-25       |            50 |              37.38 |              12.63 |
|           50 | Tracy Myers          | Male     | 23-25       |            50 |              37.38 |              12.63 |
|           53 | Jonathan Francis     | Male     | 18-19       |            50 |              37.38 |              12.63 |
|           56 | Jacob Ramirez        | Female   | 23-25       |            50 |              37.38 |              12.63 |
|           59 | Lisa Ingram          | Female   | 18-19       |            50 |              37.38 |              12.63 |
|           61 | Brandon Parks        | Male     | 18-19       |            50 |              37.38 |              12.63 |


---

## Query 6: Lab vs Lecture Participation Profile Analysis

**Demonstrated SQL Concepts:** `Complex CASE expressions, Multi-table JOIN, Statistical Grouping`

```sql
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
```

### Query Execution Result:

| participation_profile   |   student_count |   avg_final_marks |   avg_composite |   avg_gpa |
|:------------------------|----------------:|------------------:|----------------:|----------:|
| High Lecture & High Lab |              20 |             40.96 |           70.73 |      2.75 |
| Low Lecture & High Lab  |              46 |             36.65 |           70.19 |      2.65 |
| Balanced / Moderate     |             202 |             37.57 |           69.67 |      2.86 |
| High Lecture & Low Lab  |              32 |             34.94 |           68.9  |      2.75 |


---

## Query 7: Early Intervention Roster — High-Risk Students

**Demonstrated SQL Concepts:** `Multi-condition WHERE filtering, Multi-table JOIN`

```sql
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
```

### Query Execution Result:

|   student_id | student_name      | gender   | attendance_tier   |   overall_attendance_pct |   composite_score | letter_grade   | dropout_risk   |
|-------------:|:------------------|:---------|:------------------|-------------------------:|------------------:|:---------------|:---------------|
|          108 | Darrell Atkinson  | Female   | Satisfactory      |                    66.67 |             26.3  | F              | High Risk      |
|           79 | Robert Coffey     | Female   | Critical          |                    11.11 |             27.43 | F              | High Risk      |
|           88 | Gabriel Harper    | Male     | Satisfactory      |                    61.11 |             28.47 | F              | High Risk      |
|           95 | Kevin Jones       | Female   | Satisfactory      |                    77.78 |             31.4  | F              | High Risk      |
|           44 | Carol Walls       | Male     | Critical          |                    38.89 |             31.73 | F              | High Risk      |
|           64 | Amy Goodman       | Male     | Critical          |                    38.89 |             33.43 | F              | High Risk      |
|           72 | Bryan Cook        | Female   | Irregular         |                    55.56 |             39.03 | F              | High Risk      |
|           74 | Brian Murphy      | Female   | Critical          |                     0    |             39.5  | F              | High Risk      |
|          178 | Kimberly Davidson | Male     | Critical          |                    22.22 |             39.67 | F              | High Risk      |
|           69 | David Browning    | Female   | Satisfactory      |                    72.22 |             40.53 | F              | High Risk      |


---

## Query 8: Overall Top-10 Students by Composite Score

**Demonstrated SQL Concepts:** `CTE, Window Function DENSE_RANK() OVER (ORDER BY)`

```sql
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
```

### Query Execution Result:

|   overall_rank |   student_id | student_name      | gender   | age_group   |   composite_score | letter_grade   |
|---------------:|-------------:|:------------------|:---------|:------------|------------------:|:---------------|
|              1 |          250 | Angela Rodriguez  | Female   | 23-25       |            100    | A              |
|              2 |          280 | Karen Frost       | Female   | 23-25       |             96.27 | A              |
|              3 |           71 | Susan James       | Male     | 20-22       |             95.93 | A              |
|              4 |          187 | Paul Smith        | Female   | 23-25       |             94.67 | A              |
|              5 |          195 | Douglas Cruz      | Female   | 20-22       |             93.63 | A              |
|              6 |          148 | Amy George        | Female   | 20-22       |             93.53 | A              |
|              7 |          138 | Amber Terry       | Male     | 18-19       |             92.87 | A              |
|              8 |           94 | Holly Gonzalez    | Female   | 18-19       |             92.73 | A              |
|              8 |          219 | Jacqueline Gordon | Male     | 23-25       |             92.73 | A              |
|              8 |          277 | Maria Booth       | Female   | 18-19       |             92.73 | A              |
|              9 |           65 | Brad Anderson     | Female   | 20-22       |             92.27 | A              |
|             10 |          147 | Kristi James      | Female   | 23-25       |             92.07 | A              |


---

## Query 9: Grade Distribution Percentage Across Full Cohort

**Demonstrated SQL Concepts:** `CTE, Window SUM() OVER (), Percentage Calculation`

```sql
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
```

### Query Execution Result:

| letter_grade   |   grade_count |   cohort_total |   grade_pct |
|:---------------|--------------:|---------------:|------------:|
| A              |            53 |            300 |       17.67 |
| B              |            68 |            300 |       22.67 |
| C              |            69 |            300 |       23    |
| D              |            81 |            300 |       27    |
| F              |            29 |            300 |        9.67 |


---

## Query 10: Incoming GPA Band vs Current Composite Score

**Demonstrated SQL Concepts:** `CASE WHEN, GROUP BY, HAVING, Aggregate comparison`

```sql
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
```

### Query Execution Result:

| gpa_band            |   student_count |   avg_incoming_gpa |   avg_composite |   avg_final |   high_risk_count |
|:--------------------|----------------:|-------------------:|----------------:|------------:|------------------:|
| High GPA (>=3.5)    |              57 |               3.82 |           70.59 |       39.28 |                28 |
| Mid GPA (2.5-3.4)   |             148 |               2.95 |           70.37 |       37.29 |                62 |
| Low GPA (1.5-2.4)   |              83 |               2.09 |           68.38 |       36.37 |                47 |
| Very Low GPA (<1.5) |              12 |               1.12 |           67.31 |       36.36 |                12 |


---
