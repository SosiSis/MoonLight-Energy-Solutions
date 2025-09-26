# app/utils.py - Enhanced utility functions for Streamlit dashboard
import os
import sys

# Ensure project root is on sys.path so `scripts` is importable when running this file directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import pandas as pd
import numpy as np
from scripts.data_load import load_csv
from scripts.transform import add_daily_aggregates, add_post_clean_flag
from scripts.stats import cleaning_impact_test, compute_zscore, flag_outliers_z

def load_all_countries():
    """Load all country data from CSV files in data/raw/"""
    import glob
    files = glob.glob("data/raw/*.csv")
    data = {}
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0].title()
        # Map to proper country names
        if "benin" in name.lower():
            country_name = "Benin"
        elif "sierraleone" in name.lower():
            country_name = "Sierra Leone"
        elif "togo" in name.lower():
            country_name = "Togo"
        else:
            country_name = name
        data[country_name] = load_csv(f)
    return data

def daily_agg_for_country(df):
    """Create daily aggregates for a country"""
    df2 = add_post_clean_flag(df)
    daily = add_daily_aggregates(df2)
    return daily

def plot_timeseries_streamlit(daily_df, cols):
    """Plot time series using Plotly for Streamlit"""
    import streamlit as st
    import plotly.express as px

    # Filter columns that exist
    available_cols = [col for col in cols if col in daily_df.columns]

    if available_cols:
        fig = px.line(daily_df, x='Date', y=available_cols,
                     title=f"Daily {', '.join(available_cols)}",
                     labels={'value': 'Value', 'Date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"None of the requested columns {cols} found in data")

def cleaning_impact_report(df, metric='ModA'):
    """Generate cleaning impact analysis report"""
    if 'Cleaning' not in df.columns or metric not in df.columns:
        return None
    return cleaning_impact_test(df, metric=metric)

def compute_correlations(df):
    """Compute correlation matrix for key variables"""
    key_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'Tamb', 'RH', 'WS', 'WD', 'BP']
    available_cols = [col for col in key_cols if col in df.columns]

    if len(available_cols) >= 2:
        return df[available_cols].corr()
    return None

def create_wind_analysis(df):
    """Create wind analysis statistics"""
    if 'WS' not in df.columns or 'WD' not in df.columns:
        return None

    return {
        'mean_ws': df['WS'].mean(),
        'max_ws': df['WS'].max(),
        'std_ws': df['WS'].std(),
        'std_wd': df['WD'].std(),
        'data_points': len(df)
    }

def generate_summary_stats(df, columns=None):
    """Generate summary statistics for specified columns"""
    if columns is None:
        columns = df.select_dtypes(include=[np.number]).columns.tolist()

    available_cols = [col for col in columns if col in df.columns]
    if not available_cols:
        return pd.DataFrame()

    stats = df[available_cols].describe().T
    stats['skewness'] = df[available_cols].skew()
    stats['kurtosis'] = df[available_cols].kurtosis()
    return stats

def create_zscore_analysis(df):
    """Create Z-score outlier analysis"""
    outlier_data = {}
    key_cols = ['GHI', 'DNI', 'DHI', 'ModA', 'ModB', 'WS', 'WSgust', 'Tamb']

    for col in key_cols:
        if col in df.columns:
            df_z = flag_outliers_z(df.copy(), col, threshold=3.0)
            outlier_count = df_z[f'{col}_outlier'].sum()
            outlier_pct = 100 * outlier_count / len(df_z)
            outlier_data[col] = {
                'outlier_count': int(outlier_count),
                'outlier_percentage': round(outlier_pct, 2),
                'total_records': len(df_z)
            }

    return outlier_data

def create_bubble_charts(df):
    """Prepare data for bubble chart visualizations"""
    required_cols = ['GHI', 'Tamb', 'WS', 'RH']
    if not all(col in df.columns for col in required_cols):
        return None

    # Sample data for performance
    sample = df.sample(min(1000, len(df)))
    return sample[required_cols]

def calculate_country_scores(data):
    """Calculate solar potential scores for all countries"""
    country_scores = {}

    for country, df in data.items():
        daily_agg = daily_agg_for_country(df)

        # Simple scoring algorithm
        ghi_score = daily_agg['GHI'].mean() / 100 if 'GHI' in daily_agg.columns else 0
        temp_penalty = 0

        if 'Tamb' in daily_agg.columns:
            avg_temp = daily_agg['Tamb'].mean()
            # Penalty for very high temperatures (above 30°C)
            temp_penalty = max(0, (avg_temp - 30) / 10)

        # Bonus for DNI (direct irradiance is better for concentrated solar)
        dni_bonus = daily_agg['DNI'].mean() / 200 if 'DNI' in daily_agg.columns else 0

        score = ghi_score + dni_bonus - temp_penalty
        country_scores[country] = score

    return country_scores
