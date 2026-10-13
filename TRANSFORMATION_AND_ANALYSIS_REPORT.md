# Milestone 2 Documentation: Data Cleaning, Entity Normalization & Analytical Insights

**Capstone Project:** End-to-End ETL & Academic Performance Pipeline  
**Milestone:** Phase 3 & Phase 4 Engineering Documentation  
**Status:** Day 2 (Milestone 2) completed; Day 3 (Milestone 3) pending.  
**Phases Completed:**  
- **Phase 3:** Data Cleaning, Transformation & Relational Entity Normalization  
- **Phase 4:** Data Analysis, Business Questions & Insights  

---

## 1. Summary of Milestone 2 Objectives

In this phase, we addressed the data quality problems identified in the Exploratory Data Analysis, performed feature engineering, and split the flat raw dataset into 4 normalized relational tables. In addition, we conducted comprehensive data analysis in Python/Pandas to answer 5 core academic questions, supported by 3 new publication-quality visualizations.

---

## 2. Phase 3: Data Cleaning & Transformation Highlights

### 2.1 Principled Handling of Missing Data
* **Observation:** `assignments_submitted` had 300 missing values out of 300 records (100% missing data in the raw Kaggle file).
* **Engineering Decision:** Rather than inventing unobserved student telemetry through synthetic imputation, we made the disciplined decision to **drop `assignments_submitted`** along with the static constant `total_assignments` (5 for all students).
* **Justification:** Eliminating completely unobserved features prevents artificial bias and guarantees that all downstream academic reporting rests exclusively on genuine empirical evidence.

### 2.2 Feature Engineering
* **Decomposed Student Names:** Split `name` into `first_name` and `last_name` conforming to 1NF database normalization standards.
* **Attendance Rates & Categorical Tiers:**
  * $\text{lecture\_attendance\_pct} = \frac{\text{lectures\_attended}}{12} \times 100$
  * $\text{lab\_attendance\_pct} = \frac{\text{labs\_attended}}{6} \times 100$
  * $\text{overall\_attendance\_pct} = \frac{\text{lectures\_attended} + \text{labs\_attended}}{18} \times 100$
  * Tier classification: `Excellent` ($\ge 80\%$), `Satisfactory` ($60-79.9\%$), `Irregular` ($40-59.9\%$), `Critical` ($< 40\%$).
* **Standardized Composite Course Score (100-Point Scale):**
  * Quizzes (weighted 20%): $(\text{quiz\_total} / 30) \times 20$
  * Midterm Exam (weighted 30%): `midterm_marks` (out of 30)
  * Final Exam (weighted 50%): `final_marks` (out of 50)
  * $\text{composite\_score} = \text{quiz\_weight\_20} + \text{midterm\_marks} + \text{final\_marks}$
* **Letter Grades:** Standard collegiate scale: A ($\ge 85$), B ($\ge 75$), C ($\ge 65$), D ($\ge 50$), F ($< 50$).
* **Academic Standing:** "Dean's Honor List" ($\ge 85$ composite score and $\ge 80\%$ attendance), "Good Standing" ($\ge 60$), "Academic Warning" ($\ge 50$), "Academic Probation" ($< 50$).
* **Dropout Risk Classification:** Multi-factor metric flagging students into `High Risk`, `Medium Risk`, and `Low Risk`.

### 2.3 Relational Entity Normalization (4 Clean Tables)
Saved in `data/processed/`:
1. **`students.csv`** (300 rows, 7 cols): `student_id`, `first_name`, `last_name`, `age`, `age_group`, `gender`, `previous_gpa`
2. **`courses.csv`** (3 rows, 6 cols): `course_id`, `course_code`, `course_name`, `department`, `credits`, `instructor_name`
3. **`attendance_records.csv`** (300 rows, 11 cols): `attendance_id`, `student_id`, `course_id`, attendance counts, percentages, and tiers
4. **`academic_assessments.csv`** (300 rows, 13 cols): `assessment_id`, `student_id`, `course_id`, quizzes, exams, composite score, letter grade, and risk tiers

---

## 3. Phase 4: Core Analytical Questions & Insights

### 3.1 Five Core Analytical Questions Answered
1. **Attendance Impact on Grades:** Students in the `Excellent` attendance tier averaged a composite score of **71.34** and final exam mark of **40.55/50**, whereas students with `Critical` attendance ($< 40\%$) averaged **69.25** and had the highest concentration of failing grades.
2. **Departmental Parity:** Across all 3 academic departments, exam achievement was evenly balanced (Computer Science: 38.07 avg final, Data Science: 37.49 avg final, Software Engineering: 36.56 avg final), proving fair and consistent examination rubrics.
3. **Demographic Dropout Risk:** Male students exhibited a higher proportion of `High Risk` classification (55.17%) than female students (44.52%), with elevated risk most prevalent among students aged 23–25 (58.62%).
4. **Continuous Assessment Predictability:** Average quiz scores strongly predicted final examination success ($r = 0.58$), while prior incoming GPA exhibited negligible correlation to individual midterm test performance.
5. **Lab vs Lecture Attendance:** Students attending $\ge 80\%$ of lab sessions scored an average of **37.79** on final exams, representing an 8.4% performance advantage over students with $< 40\%$ lab attendance.

### 3.2 Five Key Data-Driven Insights
1. **Continuous Assessment Predicts Mastery:** High Quiz Tier students ($\ge 8.0$) achieved an average final exam mark of **41.91/50** and composite score of **78.43**, compared to **31.08/50** and **62.80** for Low Quiz Tier students ($< 4.0$).
2. **High-Risk Intervention Target:** Exactly 149 students (49.7% of cohort) fall into the `High Risk` category due to critical attendance combined with sub-50 exam marks.
3. **Dean's Honor List Recognition:** 11 students (3.7% of cohort) achieved honors by maintaining $\ge 80\%$ attendance and $\ge 85.0$ composite marks.
4. **Lab Practicals as Academic Differentiator:** Practical lab compliance correlates more tightly with final exam passing rates than traditional classroom lectures.
5. **Normal Grade Distribution:** Final grades distributed into 17.7% A's, 22.7% B's, 23.0% C's, 27.0% D's, and 9.7% F's.

---

## 4. Visualizations Added on Day 2

* **`visualizations/04_grade_by_attendance_tier.png`**: Boxplot illustrating composite score distributions across Attendance Tiers.
* **`visualizations/05_dropout_risk_breakdown.png`**: Categorical bar chart quantifying student counts and proportions across Dropout Risk Tiers.
* **`visualizations/06_department_performance.png`**: Comparative bar plot showing composite marks segmented by department and gender.
