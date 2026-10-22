"""
visualization.py
All plotting functions for Bangalore Climate Analytics
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

PLOTS_DIR = 'plots'
os.makedirs(PLOTS_DIR, exist_ok=True)


def _save(name):
    path = os.path.join(PLOTS_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=100)
    plt.close()
    print(f"Saved plot: {path}")


def plot_trend(df, col, ylabel, title, filename, color='steelblue', rolling=60):
    """Generic trend plot with rolling average."""
    yearly = df.groupby('Year')[col].mean()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(yearly.index, yearly.values, color=color, alpha=0.5, label='Annual Mean')
    roll = yearly.rolling(5, center=True).mean()
    ax.plot(yearly.index, roll.values, color='red', linewidth=2, label='5-yr Rolling Avg')
    ax.set_title(title)
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel)
    ax.legend()
    ax.grid(True, alpha=0.3)
    _save(filename)


def plot_rainfall_trend(df):
    plot_trend(df, 'Rainfall', 'Rainfall (mm/month)', 'Bangalore Monthly Rainfall Trend (1951–2024)',
               '01_rainfall_trend.png', color='royalblue')


def plot_temperature_trend(df):
    plot_trend(df, 'Temp_mean', 'Temperature (°C)', 'Bangalore Mean Temperature Trend (1951–2024)',
               '02_temperature_trend.png', color='tomato')


def plot_humidity_trend(df):
    plot_trend(df, 'Humidity', 'Humidity (%)', 'Bangalore Humidity Trend (1951–2024)',
               '03_humidity_trend.png', color='seagreen')


def plot_correlation_heatmap(df):
    """Correlation heatmap of climate variables."""
    cols = ['Rainfall', 'Temp_mean', 'Humidity', 'CES']
    cols = [c for c in cols if c in df.columns]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=45, ha='right')
    ax.set_yticklabels(cols)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', fontsize=9)
    ax.set_title('Correlation Heatmap')
    _save('04_correlation_heatmap.png')


def plot_anomalies(df):
    """Anomaly scatter plots for Z-scores."""
    fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    pairs = [('Z_rain', 'Rainfall Z-score', 'royalblue'),
             ('Z_temp', 'Temperature Z-score', 'tomato'),
             ('Z_hum', 'Humidity Z-score', 'seagreen')]

    for ax, (col, label, color) in zip(axes, pairs):
        ax.bar(df['Date'], df[col], color=color, alpha=0.5, width=20)
        ax.axhline(2, color='red', linestyle='--', linewidth=0.8, label='±2σ')
        ax.axhline(-2, color='red', linestyle='--', linewidth=0.8)
        ax.axhline(1.5, color='orange', linestyle=':', linewidth=0.8, label='±1.5σ')
        ax.axhline(-1.5, color='orange', linestyle=':', linewidth=0.8)
        ax.set_ylabel(label)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.2)

    axes[0].set_title('Climate Variable Anomalies (Z-scores) 1951–2024')
    axes[-1].set_xlabel('Date')
    _save('05_anomaly_plots.png')


def plot_ces(df):
    """CES over time."""
    fig, ax = plt.subplots(figsize=(12, 4))
    colors = df['CES_label'].map({'Normal': 'steelblue', 'Moderate': 'orange', 'Extreme': 'red'})
    ax.bar(df['Date'], df['CES'], color=colors, width=20, alpha=0.7)
    ax.axhline(3, color='red', linestyle='--', linewidth=0.8, label='Extreme threshold')
    ax.axhline(-3, color='red', linestyle='--', linewidth=0.8)
    ax.axhline(1, color='orange', linestyle=':', linewidth=0.8, label='Moderate threshold')
    ax.axhline(-1, color='orange', linestyle=':', linewidth=0.8)
    ax.set_title('Climate Extreme Score (CES) Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('CES')
    ax.legend()
    ax.grid(True, alpha=0.2)
    _save('06_ces_timeseries.png')


def plot_ces_distribution(df):
    """CES distribution histogram."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(df['CES'], bins=50, color='purple', alpha=0.7, edgecolor='white')
    ax.axvline(3, color='red', linestyle='--', label='Extreme')
    ax.axvline(-3, color='red', linestyle='--')
    ax.axvline(1, color='orange', linestyle=':', label='Moderate')
    ax.axvline(-1, color='orange', linestyle=':')
    ax.set_title('CES Distribution')
    ax.set_xlabel('CES')
    ax.set_ylabel('Frequency')
    ax.legend()
    _save('07_ces_distribution.png')


def plot_seasonal_analysis(df):
    """Seasonal bar charts for climate variables."""
    season_order = ['Winter', 'Summer', 'Monsoon', 'Post-Monsoon']
    season_df = df.groupby('Season').agg(
        Rainfall=('Rainfall', 'mean'),
        Temp_mean=('Temp_mean', 'mean'),
        Humidity=('Humidity', 'mean'),
        CES=('CES', 'mean')
    ).reindex(season_order)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    cols = ['Rainfall', 'Temp_mean', 'Humidity', 'CES']
    titles = ['Mean Rainfall (mm)', 'Mean Temperature (°C)', 'Mean Humidity (%)', 'Mean CES']
    colors = ['royalblue', 'tomato', 'seagreen', 'purple']

    for ax, col, title, color in zip(axes.flatten(), cols, titles, colors):
        ax.bar(season_df.index, season_df[col], color=color, alpha=0.8)
        ax.set_title(title)
        ax.set_xlabel('Season')
        ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Seasonal Climate Analysis — Bangalore', fontsize=14)
    _save('08_seasonal_analysis.png')


def plot_decade_comparison(df):
    """Decade-wise comparison of climate variables."""
    decade_df = df.groupby('Decade').agg(
        Rainfall=('Rainfall', 'mean'),
        Temp_mean=('Temp_mean', 'mean'),
        Humidity=('Humidity', 'mean'),
        CES=('CES', 'mean')
    ).reset_index()

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    pairs = [('Rainfall', 'royalblue'), ('Temp_mean', 'tomato'),
             ('Humidity', 'seagreen'), ('CES', 'purple')]

    for ax, (col, color) in zip(axes.flatten(), pairs):
        ax.bar(decade_df['Decade'].astype(str), decade_df[col], color=color, alpha=0.8)
        ax.set_title(f'{col} by Decade')
        ax.set_xlabel('Decade')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Decade-wise Climate Comparison — Bangalore', fontsize=14)
    _save('09_decade_comparison.png')


def plot_period_comparison(period_df):
    """Period comparison bar chart."""
    fig, axes = plt.subplots(1, 4, figsize=(14, 5))
    cols = ['Rainfall', 'Temp_mean', 'Humidity', 'CES']
    colors = ['royalblue', 'tomato', 'seagreen', 'purple']

    for ax, col, color in zip(axes, cols, colors):
        ax.bar(period_df['Period'].astype(str), period_df[col], color=color, alpha=0.8)
        ax.set_title(col)
        ax.tick_params(axis='x', rotation=30)
        ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Climate Shift Across Periods — Bangalore', fontsize=13)
    _save('10_period_comparison.png')


def plot_forecast(results, variable):
    """Actual vs predicted and future forecast."""
    res = results[variable]
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.plot(res['train'].index, res['train'].values, color='steelblue', alpha=0.6, label='Train')
    ax.plot(res['test'].index, res['test'].values, color='green', label='Actual (Test)')
    ax.plot(res['pred_test'].index, res['pred_test'].values, color='red', linestyle='--', label='Predicted (Test)')

    if 'future' in res:
        ax.plot(res['future'].index, res['future'].values, color='orange', linestyle='-.', label='Future Forecast')

    ax.set_title(f'{variable} — Actual vs Predicted + Future Forecast')
    ax.set_xlabel('Date')
    ax.set_ylabel(variable)
    ax.legend()
    ax.grid(True, alpha=0.2)
    fname = f'11_forecast_{variable.lower()}.png'
    _save(fname)


def plot_future_ces(future_df, baseline):
    """Future CES from forecasted values."""
    # Compute Z-scores using overall baseline
    future = future_df.copy()
    for var, bcol_mean, bcol_std in [
        ('Rainfall', 'Rain_mean', 'Rain_std'),
        ('Temp_mean', 'Temp_mean_mean', 'Temp_mean_std'),
        ('Humidity', 'Hum_mean', 'Hum_std')
    ]:
        if var not in future.columns:
            continue
        # Use overall mean/std from baseline
        m = baseline[bcol_mean].mean()
        s = baseline[bcol_std].mean()
        future[f'Z_{var}'] = (future[var] - m) / (s + 1e-8)

    z_cols = [c for c in ['Z_Rainfall', 'Z_Temp_mean', 'Z_Humidity'] if c in future.columns]
    if z_cols:
        future['CES'] = future[z_cols].sum(axis=1)
    else:
        future['CES'] = 0

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(future['Date'], future['CES'], color='purple', marker='o', markersize=3)
    ax.axhline(3, color='red', linestyle='--', label='Extreme')
    ax.axhline(-3, color='red', linestyle='--')
    ax.set_title('Future Climate Extreme Score (CES) — Forecast Period')
    ax.set_xlabel('Date')
    ax.set_ylabel('CES')
    ax.legend()
    ax.grid(True, alpha=0.2)
    _save('12_future_ces.png')


def plot_anomaly_evolution(df):
    """Yearly anomaly count evolution."""
    df = df.copy()
    df['any_anomaly'] = ((df['Rain_label'] != 'Normal') |
                         (df['Temp_label'] != 'Normal') |
                         (df['Hum_label'] != 'Normal')).astype(int)
    yearly = df.groupby('Year')['any_anomaly'].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(yearly['Year'], yearly['any_anomaly'], color='coral', alpha=0.8)
    roll = yearly.set_index('Year')['any_anomaly'].rolling(5, center=True).mean()
    ax.plot(roll.index, roll.values, color='darkred', linewidth=2, label='5-yr trend')
    ax.set_title('Annual Anomaly Count Evolution (1951–2024)')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Anomalous Months')
    ax.legend()
    ax.grid(True, alpha=0.2)
    _save('13_anomaly_evolution.png')


def generate_all_plots(df, results, future_df, period_df, baseline):
    """Run all visualization functions."""
    print("\nGenerating plots...")
    plot_rainfall_trend(df)
    plot_temperature_trend(df)
    plot_humidity_trend(df)
    plot_correlation_heatmap(df)
    plot_anomalies(df)
    plot_ces(df)
    plot_ces_distribution(df)
    plot_seasonal_analysis(df)
    plot_decade_comparison(df)
    plot_period_comparison(period_df)
    for var in ['Rainfall', 'Temp_mean', 'Humidity']:
        if var in results:
            plot_forecast(results, var)
    plot_future_ces(future_df, baseline)
    plot_anomaly_evolution(df)
    print("All plots saved to plots/")
