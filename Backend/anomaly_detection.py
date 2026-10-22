"""
anomaly_detection.py
Z-score based anomaly detection for climate variables
"""

import pandas as pd
import numpy as np

# ══════════════════════════════════════════════════════════════
# CES THRESHOLDS — WMO SPI METHODOLOGY (WMO-No. 1090, 2012)
# Computed from actual Bangalore data 1951–2024 (882 months)
# Moderate = 84th percentile of CES distribution = 1.051
# Extreme  = 95th percentile of CES distribution = 1.300
# ══════════════════════════════════════════════════════════════
CES_MODERATE = 1.051
CES_EXTREME  = 1.300


def compute_climatology(monthly: pd.DataFrame) -> pd.DataFrame:
    """
    Compute monthly climatology baseline:
    mean and std for Rainfall, Temp_mean, Humidity per calendar month.
    """
    baseline = monthly.groupby('Month').agg(
        Rain_mean=('Rainfall', 'mean'),
        Rain_std=('Rainfall', 'std'),
        Temp_mean_mean=('Temp_mean', 'mean'),
        Temp_mean_std=('Temp_mean', 'std'),
        Hum_mean=('Humidity', 'mean'),
        Hum_std=('Humidity', 'std'),
    ).reset_index()
    return baseline


def compute_anomalies(monthly: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    """
    Merge climatology with monthly data and compute:
    - Raw anomalies
    - Z-scores
    - Anomaly labels
    - CES
    """
    df = monthly.merge(baseline, on='Month', how='left')

    # Raw anomalies
    df['Rain_anomaly'] = df['Rainfall'] - df['Rain_mean']
    df['Temp_anomaly'] = df['Temp_mean'] - df['Temp_mean_mean']
    df['Hum_anomaly'] = df['Humidity'] - df['Hum_mean']

    # Z-scores
    df['Z_rain'] = df['Rain_anomaly'] / df['Rain_std'].replace(0, np.nan)
    df['Z_temp'] = df['Temp_anomaly'] / df['Temp_mean_std'].replace(0, np.nan)
    df['Z_hum'] = df['Hum_anomaly'] / df['Hum_std'].replace(0, np.nan)

    # Fill NaN Z-scores with 0
    for col in ['Z_rain', 'Z_temp', 'Z_hum']:
        df[col] = df[col].fillna(0)

    # Anomaly labels per variable
    def label_anomaly(z):
        az = abs(z)
        if az >= CES_EXTREME:
            return 'Strong'
        elif az >= CES_MODERATE:
            return 'Moderate'
        else:
            return 'Normal'

    df['Rain_label'] = df['Z_rain'].apply(label_anomaly)
    df['Temp_label'] = df['Z_temp'].apply(label_anomaly)
    df['Hum_label'] = df['Z_hum'].apply(label_anomaly)

    # Climate Extreme Score (humidity kept in pipeline but not in CES)
    df['CES'] = (0.6 * df['Z_rain']) + (0.4 * df['Z_temp'])

    # CES classification
    def label_ces(ces):
        a = abs(ces)
        if a >= CES_EXTREME:
            return 'Extreme'
        elif a >= CES_MODERATE:
            return 'Moderate'
        else:
            return 'Normal'

    df['CES_label'] = df['CES'].apply(label_ces)

    return df


def anomaly_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return count of each anomaly label per variable."""
    rain_counts = df['Rain_label'].value_counts().rename('Rainfall')
    temp_counts = df['Temp_label'].value_counts().rename('Temperature')
    hum_counts = df['Hum_label'].value_counts().rename('Humidity')
    summary = pd.DataFrame([rain_counts, temp_counts, hum_counts]).T.fillna(0).astype(int)
    return summary


if __name__ == '__main__':
    from preprocessing import load_data, preprocess, aggregate_monthly, add_season, add_decade
    raw = load_data('data.csv')
    daily = preprocess(raw)
    monthly = aggregate_monthly(daily)
    monthly = add_season(monthly)
    monthly = add_decade(monthly)
    baseline = compute_climatology(monthly)
    df_anom = compute_anomalies(monthly, baseline)
    print(df_anom[['Date', 'Z_rain', 'Z_temp', 'Z_hum', 'CES', 'CES_label']].head(10))
    print("\nAnomaly Summary:")
    print(anomaly_summary(df_anom))
