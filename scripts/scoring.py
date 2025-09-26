# src/scoring.py
import pandas as pd
import numpy as np

def country_score(df_daily: pd.DataFrame, weights=None):
    """
    df_daily - daily aggregated metrics with columns GHI, DNI, DHI, Tamb
    weights dict - weights for scoring
    Score = w1*avg_GHI + w2*avg_DNI - w3*avg_DHI - w4*temp_penalty
    temperature penalty = normalized temperature (higher is worse)
    """
    if weights is None:
        weights = {'GHI':0.4, 'DNI':0.35, 'DHI':0.15, 'Tamb':0.10}
    agg = {}
    agg['avg_GHI'] = df_daily['GHI'].mean()
    agg['avg_DNI'] = df_daily['DNI'].mean()
    agg['avg_DHI'] = df_daily['DHI'].mean()
    agg['avg_Tamb'] = df_daily['Tamb'].mean()
    # normalize temperature to [0,1] using a soft scale (example: 0-40C)
    temp_norm = (agg['avg_Tamb'] - 0) / 40.0
    score = (weights['GHI']*agg['avg_GHI'] + weights['DNI']*agg['avg_DNI'] -
             weights['DHI']*agg['avg_DHI'] - weights['Tamb']*temp_norm*1000)  # scale multiplier
    return {'agg':agg, 'score':score}
