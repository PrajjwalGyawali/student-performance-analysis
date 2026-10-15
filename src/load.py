"""
Phase 6: Database Load Module (ETL Pipeline)
Connects to SQLite relational database using SQLAlchemy, initializes table schemas
with relational constraints (PK, FK, CHECK), and loads transformed DataFrames.

Tables: students, attendance_records, academic_assessments (3 tables only).
The courses table was removed because the raw dataset contains no real course,
department, or instructor data.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "student_performance.db")
SQL_SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "schema_and_queries.sql")

def get_engine(db_path: str = DB_PATH):
    """Creates an SQLAlchemy engine pointing to the SQLite database."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = create_engine(f"sqlite:///{os.path.abspath(db_path)}", echo=False)
    return engine

def init_database_schema(engine, schema_path: str = SQL_SCHEMA_PATH):
    """
    Executes DDL statements from the SQL file to initialize the 3 normalized tables.
    """
    with open(schema_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    # Extract only DDL statements (everything before the PHASE 7 marker)
    ddl_part = sql_content.split("-- PHASE 7:")[0]

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
    Loads 3 tables: students (parent), attendance_records and academic_assessments (children).
    """
    print("=" * 80)
    print("PHASE 6: DATABASE LOADING (ETL PIPELINE)")
    print("=" * 80)

    engine = get_engine(db_path)
    init_database_schema(engine)

    df_students    = tables["students"]
    df_attendance  = tables["attendance"]
    df_assessments = tables["assessments"]

    print("Loading data into normalized tables...")

    # 1. Parent table first (no FK dependencies)
    df_students.to_sql("students", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_students)} records into 'students'")

    # 2. Child tables (FK to students via student_id)
    df_attendance.to_sql("attendance_records", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_attendance)} records into 'attendance_records'")

    df_assessments.to_sql("academic_assessments", con=engine, if_exists="append", index=False)
    print(f"  [+] Loaded {len(df_assessments)} records into 'academic_assessments'")

    # Verification
    with engine.connect() as conn:
        counts = {}
        for tbl in ["students", "attendance_records", "academic_assessments"]:
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
