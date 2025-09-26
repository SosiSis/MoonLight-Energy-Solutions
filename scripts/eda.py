# src/eda.py (snippet)
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def plot_time_series(df, metric='GHI', freq='D', ax=None):
    s = df.set_index('Timestamp')[metric].resample(freq).mean()
    ax = ax or plt.gca()
    s.plot(ax=ax)
    ax.set_title(f'{metric} time series ({freq})')
    ax.set_ylabel(metric)
    ax.grid(True)
    return ax

def correlation_matrix(df, cols=None):
    cols = cols or ['GHI','DNI','DHI','Tamb','RH','WS','ModA','ModB']
    corr = df[cols].corr()
    plt.figure(figsize=(8,6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
    plt.title('Correlation matrix')
    plt.tight_layout()
    return corr

def wind_rose(df, speed_col='WS', dir_col='WD', bins=None):
    # basic wind-rose without external lib
    df = df.dropna(subset=[speed_col, dir_col])
    directions = np.deg2rad(df[dir_col].values)
    speeds = df[speed_col].values
    if bins is None:
        bins = [0,1,3,5,8,12,20]
    # categorize speeds into bins
    labels = range(len(bins)-1)
    speed_cat = np.digitize(speeds, bins) - 1
    n_dir = 16
    dir_bins = np.linspace(0, 2*np.pi, n_dir+1)
    counts = np.zeros((len(bins)-1, n_dir))
    for i in range(n_dir):
        mask = (directions >= dir_bins[i]) & (directions < dir_bins[i+1])
        for j in labels:
            counts[j,i] = ((speed_cat==j) & mask).sum()
    # stacked polar bar
    fig = plt.figure(figsize=(8,6))
    ax = fig.add_subplot(111, polar=True)
    width = (2*np.pi)/n_dir
    bottom = np.zeros(n_dir)
    for j in range(len(bins)-1):
        vals = counts[j]
        ax.bar(dir_bins[:-1], vals, width=width, bottom=bottom, edgecolor='k', align='edge')
        bottom += vals
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_title('Wind rose (counts by speed bins)')
    plt.show()
