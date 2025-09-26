# src/stats.py
import numpy as np
import pandas as pd
from scipy import stats

def compute_zscore(series: pd.Series) -> pd.Series:
    return (series - series.mean())/series.std(ddof=0)

def flag_outliers_z(df: pd.DataFrame, col: str, threshold=3.0) -> pd.DataFrame:
    s = df[col]
    z = compute_zscore(s)
    df[f'{col}_z'] = z
    df[f'{col}_outlier'] = z.abs() > threshold
    return df

def cleaning_impact_test(df: pd.DataFrame, metric='ModA', pre_window_hours=24, post_window_hours=24):
    """
    Compares average metric in pre-window vs post-window around cleaning events using paired t-test.
    We'll compute mean before and after for each cleaning event, then do t-test across events.
    """
    df = df.sort_values('Timestamp').reset_index(drop=True)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    events = df[df['Cleaning']==1]['Timestamp'].tolist()
    pre_vals, post_vals = [], []
    for t in events:
        pre_start = t - pd.Timedelta(hours=pre_window_hours)
        pre = df[(df['Timestamp'] >= pre_start) & (df['Timestamp'] < t)][metric].mean()
        post_end = t + pd.Timedelta(hours=post_window_hours)
        post = df[(df['Timestamp'] > t) & (df['Timestamp'] <= post_end)][metric].mean()
        if np.isfinite(pre) and np.isfinite(post):
            pre_vals.append(pre)
            post_vals.append(post)
    if len(pre_vals) < 2:
        return {"n_events": len(pre_vals), "message": "Not enough paired events for a t-test"}
    t_stat, p_val = stats.ttest_rel(post_vals, pre_vals, nan_policy='omit')
    return {"n_events": len(pre_vals), "t_stat": float(t_stat), "p_value": float(p_val),
            "mean_pre": float(np.mean(pre_vals)), "mean_post": float(np.mean(post_vals)),
            "mean_diff": float(np.mean(post_vals)-np.mean(pre_vals))}
