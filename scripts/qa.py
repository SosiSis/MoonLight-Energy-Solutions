# src/qa.py
import pandas as pd
import numpy as np

def basic_quality_report(df: pd.DataFrame) -> dict:
    report = {}
    report['n_rows'] = len(df)
    report['n_cols'] = df.shape[1]
    report['missing_per_col'] = df.isnull().sum().to_dict()
    report['dtypes'] = df.dtypes.astype(str).to_dict()
    # negative checks for sensors that must be >= 0
    non_negative_cols = ['GHI','DNI','DHI','ModA','ModB','Precipitation','WS','WSgust']
    neg_counts = {c: int((df[c] < 0).sum()) if c in df.columns else None for c in non_negative_cols}
    report['negative_counts'] = neg_counts
    # duplicates (full row)
    report['duplicate_rows'] = int(df.duplicated().sum())
    return report

def drop_bad_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    if "Timestamp" in df.columns:
        return df[df["Timestamp"].notna()].copy()
    return df
