"""
Phase 1: Data Acquisition & Extraction Module
Dataset Domain: Education / Student Academic Performance Analytics
Source: Kaggle (muhammadkhubaibahmad/student-performance-and-clustering-dataset)
"""

import os
import pandas as pd

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "student_dropout_behavior_raw.csv")

def extract_raw_data(filepath: str = RAW_DATA_PATH) -> pd.DataFrame:
    """
    Extracts raw dataset from the preserved CSV file.
    Validates file existence, non-emptiness, and preserves raw state.
    """
    print("=" * 80)
    print("PHASE 1: DATA EXTRACTION")
    print("=" * 80)
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Raw data file not found at: {filepath}")
        
    df_raw = pd.read_csv(filepath)
    print(f"Successfully extracted raw data from: {filepath}")
    print(f"Raw Dataset Dimensions: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")
    print("\nInitial Column Schema:")
    for col in df_raw.columns:
        print(f"  - {col} ({df_raw[col].dtype})")
        
    print("\nSample Raw Records (First 3):")
    print(df_raw.head(3).to_string(index=False))
    return df_raw

if __name__ == "__main__":
    df = extract_raw_data()
