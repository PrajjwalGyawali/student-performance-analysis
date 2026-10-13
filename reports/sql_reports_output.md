# Deliverable 5: SQL Analytical Reports Output

**Project:** End-to-End ETL & Academic Performance Pipeline  
**Database Engine:** SQLite / ANSI SQL Compliant  
**Total Queries Executed:** 10  

---

## Query 1: Academic Department Performance Benchmark

**Demonstrated SQL Concepts:** `JOIN, GROUP BY, Aggregate functions (COUNT, AVG, ROUND)`

```sql
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
```

### Query Execution Result:

| department           | course_name                         |   total_enrolled |   avg_midterm_score |   avg_final_score |   avg_composite_score |   avg_attendance_pct |
|:---------------------|:------------------------------------|-----------------:|--------------------:|------------------:|----------------------:|---------------------:|
| Computer Science     | Introduction to Computer Science    |              100 |               20.29 |             38.07 |                 71.13 |                50.44 |
| Software Engineering | Software Engineering Principles     |              100 |               20.33 |             36.56 |                 69.15 |                49.28 |
| Data Science         | Data Science & Statistical Learning |              100 |               19.29 |             37.49 |                 68.93 |                52.33 |


---

## Query 2: Performance & Risk Breakdown by Attendance Tier

**Demonstrated SQL Concepts:** `JOIN, GROUP BY, CASE statements, Conditional Aggregation`

```sql
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
```

### Query Execution Result:

| attendance_tier   |   total_students |   avg_attendance_rate |   avg_composite_score |   high_achievers_count |   high_risk_count |   high_risk_percentage |
|:------------------|-----------------:|----------------------:|----------------------:|-----------------------:|------------------:|-----------------------:|
| Irregular         |               65 |                 49.83 |                 71.64 |                     29 |                 7 |                  10.77 |
| Excellent         |               37 |                 87.99 |                 71.34 |                     16 |                 8 |                  21.62 |
| Critical          |              119 |                 27.17 |                 69.25 |                     46 |               119 |                 100    |
| Satisfactory      |               79 |                 69.34 |                 68.15 |                     30 |                15 |                  18.99 |


---

## Query 3: Dean's Honor List Recognition

**Demonstrated SQL Concepts:** `Multi-table JOIN, WHERE clause, Multi-column Ordering`

```sql
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
```

### Query Execution Result:

|   student_id | full_name          | gender   | course_code   |   previous_gpa |   overall_attendance_pct |   composite_score | letter_grade   | academic_standing   |
|-------------:|:-------------------|:---------|:--------------|---------------:|-------------------------:|------------------:|:---------------|:--------------------|
|          250 | Angela Rodriguez   | Female   | DS201         |           3.19 |                    88.89 |            100    | A              | Dean's Honor List   |
|          280 | Karen Frost        | Female   | DS201         |           2.43 |                    94.44 |             96.27 | A              | Dean's Honor List   |
|           71 | Dr. Susan James    | Male     | SE301         |           3.78 |                    83.33 |             95.93 | A              | Dean's Honor List   |
|          148 | Amy George         | Female   | DS201         |           2.48 |                    88.89 |             93.53 | A              | Dean's Honor List   |
|          149 | Jamie Kim          | Female   | SE301         |           3.63 |                    83.33 |             91.77 | A              | Dean's Honor List   |
|          239 | Megan Brewer       | Female   | SE301         |           2.31 |                   100    |             90.4  | A              | Dean's Honor List   |
|          212 | Cheryl Garcia      | Female   | SE301         |           3.21 |                    88.89 |             89.2  | A              | Dean's Honor List   |
|           73 | Richard Davis      | Male     | DS201         |           1.71 |                    88.89 |             86.9  | A              | Dean's Honor List   |
|          168 | Dr. David Hall Jr. | Male     | CS101         |           3.23 |                    83.33 |             86.63 | A              | Dean's Honor List   |
|          102 | Sandra Barr        | Male     | CS101         |           2.71 |                    88.89 |             85.53 | A              | Dean's Honor List   |
|          216 | Kerry Church       | Female   | CS101         |           2.68 |                   100    |             85.13 | A              | Dean's Honor List   |


---

## Query 4: Dropout Risk Demographics (Gender & Age Groups)

**Demonstrated SQL Concepts:** `GROUP BY, HAVING, CASE WHEN, Filtering on Cohort Thresholds`

```sql
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
```

### Query Execution Result:

| gender   | age_group   |   total_students |   avg_incoming_gpa |   high_risk_count |   high_risk_pct |   cohort_avg_score |
|:---------|:------------|-----------------:|-------------------:|------------------:|----------------:|-------------------:|
| Male     | 23-25       |               58 |               2.86 |                34 |           58.62 |              67.32 |
| Male     | 18-19       |               37 |               2.64 |                21 |           56.76 |              71.11 |
| Female   | 20-22       |               63 |               2.86 |                32 |           50.79 |              69.82 |
| Male     | 20-22       |               50 |               2.64 |                25 |           50    |              67.32 |
| Female   | 18-19       |               35 |               3.05 |                15 |           42.86 |              71.72 |
| Female   | 23-25       |               57 |               2.8  |                22 |           38.6  |              72.12 |


---

## Query 5: Students Performing Above Department Average

**Demonstrated SQL Concepts:** `Correlated Scalar Subquery, Mathematical Column Expressions, LIMIT`

```sql
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
```

### Query Execution Result:

|   student_id | student_name     | course_code   |   final_marks |   course_avg_final |   score_margin |
|-------------:|:-----------------|:--------------|--------------:|-------------------:|---------------:|
|           11 | Lawrence Powers  | SE301         |            50 |              36.56 |          13.44 |
|           14 | Rita Olson       | SE301         |            50 |              36.56 |          13.44 |
|           20 | Mark Allen       | SE301         |            50 |              36.56 |          13.44 |
|           50 | Tracy Myers      | SE301         |            50 |              36.56 |          13.44 |
|           53 | Jonathan Francis | SE301         |            50 |              36.56 |          13.44 |
|           56 | Jacob Ramirez    | SE301         |            50 |              36.56 |          13.44 |
|           59 | Lisa Ingram      | SE301         |            50 |              36.56 |          13.44 |
|           65 | Brad Anderson    | SE301         |            50 |              36.56 |          13.44 |
|           77 | Patrick Norton   | SE301         |            50 |              36.56 |          13.44 |
|           80 | John Ballard     | SE301         |            50 |              36.56 |          13.44 |


---

## Query 6: Continuous Assessment (Quiz Tiers) vs Examination Performance

**Demonstrated SQL Concepts:** `CASE WHEN, GROUP BY, Aggregate metric comparison across continuous assessment tiers`

```sql
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
```

### Query Execution Result:

| quiz_performance_tier          |   student_count |   avg_quiz_grade |   avg_midterm_marks |   avg_final_marks |   avg_composite_score |
|:-------------------------------|----------------:|-----------------:|--------------------:|------------------:|----------------------:|
| High Quiz Tier (>=8.0)         |              24 |             8.49 |               19.55 |             41.91 |                 78.43 |
| Mid Quiz Tier (6.0-7.9)        |             146 |             6.85 |               20.23 |             37.77 |                 71.7  |
| Developing Quiz Tier (4.0-5.9) |             117 |             5.22 |               19.19 |             36.65 |                 66.28 |
| Low Quiz Tier (<4.0)           |              13 |             3.43 |               24.85 |             31.08 |                 62.8  |


---

## Query 7: Top 3 Ranked Students per Department

**Demonstrated SQL Concepts:** `Common Table Expression (CTE), Window Function (DENSE_RANK() OVER PARTITION BY)`

```sql
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
```

### Query Execution Result:

| department           |   dept_rank |   student_id | student_name      |   composite_score | letter_grade   |
|:---------------------|------------:|-------------:|:------------------|------------------:|:---------------|
| Computer Science     |           1 |          195 | Douglas Cruz      |             93.63 | A              |
| Computer Science     |           2 |          138 | Amber Terry       |             92.87 | A              |
| Computer Science     |           3 |          219 | Jacqueline Gordon |             92.73 | A              |
| Data Science         |           1 |          250 | Angela Rodriguez  |            100    | A              |
| Data Science         |           2 |          280 | Karen Frost       |             96.27 | A              |
| Data Science         |           3 |          187 | Paul Smith        |             94.67 | A              |
| Software Engineering |           1 |           71 | Dr. Susan James   |             95.93 | A              |
| Software Engineering |           2 |           65 | Brad Anderson     |             92.27 | A              |
| Software Engineering |           3 |          149 | Jamie Kim         |             91.77 | A              |


---

## Query 8: Lab Participation Gap Impact Analysis

**Demonstrated SQL Concepts:** `Complex CASE expressions, Multi-table JOIN, Statistical Grouping`

```sql
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
```

### Query Execution Result:

| participation_profile   |   student_count |   avg_final_marks |   avg_composite_score |   avg_previous_gpa |
|:------------------------|----------------:|------------------:|----------------------:|-------------------:|
| High Lecture & High Lab |              20 |             40.96 |                 70.73 |               2.75 |
| Low Lecture & High Lab  |              46 |             36.65 |                 70.19 |               2.65 |
| Balanced / Moderate     |             202 |             37.57 |                 69.67 |               2.86 |
| High Lecture & Low Lab  |              32 |             34.94 |                 68.9  |               2.75 |


---

## Query 9: Early Intervention & Academic Warning Roster

**Demonstrated SQL Concepts:** `Complex boolean filtering, Multi-table JOIN, Risk mitigation reporting`

```sql
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
```

### Query Execution Result:

|   student_id | student_name       | course_name                         | attendance_tier   |   overall_attendance_pct |   composite_score | letter_grade   | dropout_risk   |
|-------------:|:-------------------|:------------------------------------|:------------------|-------------------------:|------------------:|:---------------|:---------------|
|          108 | Darrell Atkinson   | Introduction to Computer Science    | Satisfactory      |                    66.67 |             26.3  | F              | High Risk      |
|           79 | Robert Coffey      | Data Science & Statistical Learning | Critical          |                    11.11 |             27.43 | F              | High Risk      |
|           88 | Mr. Gabriel Harper | Data Science & Statistical Learning | Satisfactory      |                    61.11 |             28.47 | F              | High Risk      |
|           95 | Kevin Jones        | Software Engineering Principles     | Satisfactory      |                    77.78 |             31.4  | F              | High Risk      |
|           44 | Carol Walls        | Software Engineering Principles     | Critical          |                    38.89 |             31.73 | F              | High Risk      |
|           64 | Amy Goodman        | Data Science & Statistical Learning | Critical          |                    38.89 |             33.43 | F              | High Risk      |
|           72 | Bryan Cook         | Introduction to Computer Science    | Irregular         |                    55.56 |             39.03 | F              | High Risk      |
|           74 | Brian Murphy       | Software Engineering Principles     | Critical          |                     0    |             39.5  | F              | High Risk      |
|          178 | Kimberly Davidson  | Data Science & Statistical Learning | Critical          |                    22.22 |             39.67 | F              | High Risk      |
|           69 | David Browning     | Introduction to Computer Science    | Satisfactory      |                    72.22 |             40.53 | F              | High Risk      |


---

## Query 10: Grade Distribution Share per Course (Window Analytic Query)

**Demonstrated SQL Concepts:** `CTE, Window Aggregate SUM() OVER (PARTITION BY), Percentage Distribution`

```sql
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
```

### Query Execution Result:

| course_code   | letter_grade   |   grade_count |   course_total |   grade_percentage |
|:--------------|:---------------|--------------:|---------------:|-------------------:|
| CS101         | A              |            17 |            100 |                 17 |
| CS101         | B              |            28 |            100 |                 28 |
| CS101         | C              |            21 |            100 |                 21 |
| CS101         | D              |            28 |            100 |                 28 |
| CS101         | F              |             6 |            100 |                  6 |
| DS201         | A              |            19 |            100 |                 19 |
| DS201         | B              |            20 |            100 |                 20 |
| DS201         | C              |            23 |            100 |                 23 |
| DS201         | D              |            26 |            100 |                 26 |
| DS201         | F              |            12 |            100 |                 12 |
| SE301         | A              |            17 |            100 |                 17 |
| SE301         | B              |            20 |            100 |                 20 |
| SE301         | C              |            25 |            100 |                 25 |
| SE301         | D              |            27 |            100 |                 27 |
| SE301         | F              |            11 |            100 |                 11 |


---
