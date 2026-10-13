"""
Phase 6: Database Load Module (ETL Pipeline)
Connects to SQLite relational database using SQLAlchemy, initializes table schemas
with relational constraints (PK, FK, CHECK), and loads transformed DataFrames.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "student_performance.db")
SQL_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema_and_queries.sql")

def get_engine(db_path: str = DB_PATH):
    """Creates an SQLAlchemy engine with foreign key support enabled."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{os.path.abspath(db_path)}", echo=False)
    return engine

def init_database_schema(engine, schema_path: str = SQL_SCHEMA_PATH):
    """
    Executes DDL statements from the SQL file to initialize normalized tables.
    """
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Extract only DDL statements up to the first query
    ddl_part = sql_content.split("-- PHASE 7:")[0]
    
    # Execute DDL statements using sqlite3 direct connection for multi-statement execution
    raw_conn = sqlite3.connect(engine.url.database)
    try:
        raw_conn.execute("PRAGMA foreign_keys = ON;")
        raw_conn.executescript(ddl_part)
        raw_conn.commit()
    finally:
        raw_conn.close()
        
    print("Database schema successfully initialized with constraints (PK, FK, CHECK).")

def load_data_to_database(tables: dict, db_path: str = DB_PATH) -> dict:
    """
    Loads transformed relational DataFrames into their respective database tables.
    """
    print("=" * 80)
    print("PHASE 6: DATABASE LOADING (ETL PIPELINE)")
    print("=" * 80)
    
    engine = get_engine(db_path)
    init_database_schema(engine)
    
    df_students = tables["students"]
    df_courses = tables["courses"]
    df_attendance = tables["attendance"]
    df_assessments = tables["assessments"]
    
    # Load each DataFrame in correct foreign key order
    print("Loading data into normalized tables...")
    
    # 1. Primary entity tables (No foreign keys)
    df_students.to_sql("students", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_students)} records into 'students'")
    
    df_courses.to_sql("courses", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_courses)} records into 'courses'")
    
    # 2. Child tables (Foreign keys to students and courses)
    df_attendance.to_sql("attendance_records", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_attendance)} records into 'attendance_records'")
    
    df_assessments.to_sql("academic_assessments", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_assessments)} records into 'academic_assessments'")
    
    # Verification query
    with engine.connect() as conn:
        counts = {}
        for tbl in ["students", "courses", "attendance_records", "academic_assessments"]:
            res = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            counts[tbl] = res
            
    print("\nVerification Count in Relational Database:")
    for tbl, count in counts.items():
        print(f"  Table '{tbl}': {count} rows")
        
    print(f"\nDatabase successfully loaded at: {os.path.abspath(db_path)}")
    return counts

if __name__ == "__main__":
    from extract import extract_raw_data
    from transform import clean_and_transform_data
    df_raw = extract_raw_data()
    tables = clean_and_transform_data(df_raw)
    load_data_to_database(tables)
