# Milestone 2 Documentation: Data Cleaning, Entity Normalization & Analytical Insights

**Capstone Project:** End-to-End ETL & Academic Performance Pipeline  
**Milestone:** Phase 3 & Phase 4 Engineering Documentation  
**Status:** Completed.  
**Phases Covered:**  
- **Phase 3:** Data Cleaning, Transformation & Relational Entity Normalization  
- **Phase 4:** Data Analysis, Analytical Questions & Insights  

---

## 1. Summary of Milestone 2 Objectives

In this phase, we addressed the data quality problems identified in the Exploratory Data Analysis, performed feature engineering, and split the flat raw dataset into 3 normalized relational tables. In addition, we conducted comprehensive data analysis in Python/Pandas to answer 5 core academic questions, supported by publication-quality visualizations.

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
* **Standardized Composite Score (100-Point Scale):**
  * Quizzes (weighted 20%): $(\text{quiz\_total} / 30) \times 20$
  * Midterm Exam (weighted 30%): `midterm_marks` (out of 30)
  * Final Exam (weighted 50%): `final_marks` (out of 50)
  * $\text{composite\_score} = \text{quiz\_weight\_20} + \text{midterm\_marks} + \text{final\_marks}$
* **Letter Grades:** Standard collegiate scale: A ($\ge 85$), B ($\ge 75$), C ($\ge 65$), D ($\ge 50$), F ($< 50$).
* **Academic Standing:** "Dean's Honor List" ($\ge 85$ composite score and $\ge 80\%$ attendance), "Good Standing" ($\ge 60$), "Academic Warning" ($\ge 50$), "Academic Probation" ($< 50$).
* **Dropout Risk Classification (Explicit Rule-Based Definition):** `High Risk` is explicitly defined by a deterministic business rule: student exhibits $\text{overall\_attendance\_pct} < 40\%$ OR $\text{composite\_score} < 45$ OR $\text{previous\_gpa} < 1.8$. *Note: This is a rule-based intervention label, not observed dropout outcome data.*

### 2.3 Relational Entity Normalization (3 Clean Tables)
Saved in `data/processed/`:
1. **`students.csv`** (300 rows, 7 cols): `student_id`, `first_name`, `last_name`, `age`, `age_group`, `gender`, `previous_gpa`
2. **`attendance_records.csv`** (300 rows, 10 cols): `attendance_id`, `student_id`, attendance counts, percentages, and tiers
3. **`academic_assessments.csv`** (300 rows, 12 cols): `assessment_id`, `student_id`, quizzes, exams, composite score, letter grade, and risk tiers

---

## 3. Phase 4: Core Analytical Questions & Insights

### 3.1 Five Core Analytical Questions Answered
1. **Attendance Impact on Grades:** Students in the `Excellent` attendance tier averaged a composite score of **71.34** vs **69.25** for `Critical` attendance.
2. **Demographic Risk Distribution:** Male students exhibited a 55.17% high-risk rate compared to 44.52% for female students, with elevated risk highest in the 23–25 age tier (58.62%).
3. **Dean's Honor List Achievement:** Exactly 11 students (3.7% of cohort) met the honors criteria of $\ge 80\%$ attendance and $\ge 85.0$ composite score.
4. **Continuous Assessment Predictability:** Average quiz scores strongly associated with final exam performance: students in the High Quiz Tier ($\ge 8.0$) averaged **41.91/50** vs **31.08/50** for Low Quiz Tier ($< 4.0$).
5. **Lab vs Lecture Attendance:** Students attending $\ge 80\%$ of lab sessions scored an average of **37.79** on final exams vs **34.86** for $< 40\%$ lab attendance (**2.9-point** margin). For lectures, high vs low attendance showed **37.58** vs **37.50** (**0.1-point** margin).

### 3.2 Five Key Data-Driven Insights
1. **Attendance Tiers Differ Modestly:** Attendance-tier composite scores differ only slightly: 'Excellent' tier averaged **71.3** vs **69.3** for 'Critical' tier (a **2.0-point** gap). The Pearson correlation between overall attendance percentage and final marks is **r = 0.03**, indicating a very weak linear relationship in this cohort.
2. **Rule-Based High-Risk Classification:** Exactly **149 students (49.7% of cohort)** carry the 'High Risk' label. This is a rule-based classification defined in `transform.py`—a student is flagged High Risk when meeting ANY of: overall attendance $< 40\%$, composite score $< 45$, or previous GPA $< 1.8$. It does not represent observed dropout outcomes.
3. **Dean's Honor Cohort:** Exactly **11 students (3.7% of cohort)** achieved Dean's Honor List standing ($\ge 80\%$ attendance AND $\ge 85.0$ composite score).
4. **Lab vs Lecture Attendance:** Students with $\ge 80\%$ lab attendance averaged **37.8** on final exams vs **34.9** for $< 40\%$ lab attendance (**2.9-point** difference). For lectures, the same comparison gives **37.6** vs **37.5** (**0.1-point** difference). Both effects are modest and non-causal.
5. **Historical GPA Linear Association:** Previous GPA vs final marks yielded Pearson **r = 0.10**, indicating that a student's prior GPA has very little linear association with their final exam score in this dataset. Similarly, previous GPA vs midterm yielded Pearson **r = 0.01**.

---

## 4. Visualizations Added
* **`visualizations/04_grade_by_attendance_tier.png`**: Boxplot illustrating composite score distributions across Attendance Tiers.
* **`visualizations/05_dropout_risk_breakdown.png`**: Categorical bar chart quantifying student counts and proportions across Dropout Risk Tiers.
