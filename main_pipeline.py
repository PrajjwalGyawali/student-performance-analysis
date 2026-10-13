"""
End-to-End ETL & Data Analysis Pipeline Master Execution Script
Author: Prajjwal Gyawali
Capstone Project: Student Performance & Academic Analytics Pipeline
Domain: Education / Academic Learning Analytics

This script runs all 7 phases sequentially and reproducibly:
  Phase 1: Raw Data Ingestion & Extraction
  Phase 2: Exploratory Data Analysis & Data Quality Audit
  Phase 3: Data Cleaning, Imputation, Transformation & Normalization
  Phase 4: Python Analytical Questions & Visualizations
  Phase 5 & 6: Database Relational Schema Creation & SQLAlchemy Loading
  Phase 7: SQL Reporting & Business Insights
"""

import sys
import os
import time

# Ensure src directory is in sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from extract import extract_raw_data
from eda import perform_eda
from transform import clean_and_transform_data
from analysis import perform_data_analysis
from load import load_data_to_database
from sql_reporting import generate_sql_reports

def run_pipeline():
    start_time = time.time()
    print("=" * 80)
    print("STARTING END-TO-END ETL & DATA ANALYSIS PIPELINE")
    print("Repository: https://github.com/PrajjwalGyawali/student-performance-analysis.git")
    print("=" * 80)
    
    # Phase 1: Extraction
    df_raw = extract_raw_data()
    
    # Phase 2: Exploratory Data Analysis & Quality Audit
    eda_results = perform_eda(df_raw, save_visualizations=True)
    
    # Phase 3: Data Cleaning, Transformation & Normalization
    tables = clean_and_transform_data(df_raw)
    
    # Phase 4: Data Analysis & Insights
    analysis_results = perform_data_analysis(tables, save_plots=True)
    
    # Phase 5 & 6: Database Loading
    db_counts = load_data_to_database(tables)
    
    # Phase 7: SQL Reporting
    sql_results = generate_sql_reports()
    
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("ETL PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"Total Execution Time: {elapsed:.2f} seconds")
    print("Database Tables Loaded:")
    for tbl, cnt in db_counts.items():
        print(f"  - {tbl}: {cnt} rows")
    print(f"Total SQL Queries Executed: {len(sql_results)}")
    print("Visualizations Generated in: ./visualizations/")
    print("SQL Report Output Saved to: ./reports/sql_reports_output.md")
    print("=" * 80)

if __name__ == "__main__":
    run_pipeline()
