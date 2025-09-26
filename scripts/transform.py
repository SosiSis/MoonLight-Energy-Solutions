# src/transform.py
import pandas as pd
import numpy as np

def fill_interpolate(df: pd.DataFrame, method='time') -> pd.DataFrame:
    df = df.set_index("Timestamp")
    numeric_cols = df.select_dtypes(include='number').columns
    # forward/backfill small gaps
    df[numeric_cols] = df[numeric_cols].interpolate(method=method).ffill().bfill()
    return df.reset_index()

def add_daily_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    df['date'] = df['Timestamp'].dt.date
    agg = df.groupby('date').agg({
        'GHI':'mean','DNI':'mean','DHI':'mean','ModA':'mean','ModB':'mean',
        'Tamb':'mean','RH':'mean','WS':'mean','BP':'mean'
    }).reset_index().rename(columns={'date':'Date'})
    return agg

def add_post_clean_flag(df: pd.DataFrame, days_after=1):
    # mark rows within days_after days after a cleaning event
    df = df.copy()
    if 'Cleaning' not in df.columns:
        df['Cleaning'] = 0
    df['Cleaning'] = df['Cleaning'].fillna(0).astype(int)
    df['clean_timestamp'] = pd.to_datetime(df['Timestamp'].where(df['Cleaning']==1))
    df['last_clean'] = df['clean_timestamp'].ffill()
    df['days_since_clean'] = (pd.to_datetime(df['Timestamp']) - df['last_clean']).dt.total_seconds()/(3600*24)
    df['post_clean'] = df['days_since_clean'].between(0, days_after)
    df = df.drop(columns=['clean_timestamp','last_clean','days_since_clean'])
    return df
