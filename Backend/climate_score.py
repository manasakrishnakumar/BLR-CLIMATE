"""
climate_score.py
Climate Extreme Score (CES) analysis utilities
"""

import pandas as pd
import numpy as np


def ces_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Yearly average CES."""
    return df.groupby('Year')['CES'].mean().reset_index()


def ces_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    """Decade average CES."""
    return df.groupby('Decade')['CES'].mean().reset_index()


def ces_by_season(df: pd.DataFrame) -> pd.DataFrame:
    """Seasonal average CES."""
    return df.groupby('Season')['CES'].mean().reset_index()


def ces_extreme_events(df: pd.DataFrame) -> pd.DataFrame:
    """Filter only Extreme CES events."""
    return df[df['CES_label'] == 'Extreme'].copy()


def period_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compare mean Rainfall, Temp_mean, Humidity, CES
    across three historical periods.
    """
    bins = [1950, 1980, 2000, 2025]
    labels = ['1951-1980', '1981-2000', '2001-2024']
    df = df.copy()
    df['Period'] = pd.cut(df['Year'], bins=bins, labels=labels, right=True)
    summary = df.groupby('Period', observed=True).agg(
        Rainfall=('Rainfall', 'mean'),
        Temp_mean=('Temp_mean', 'mean'),
        Humidity=('Humidity', 'mean'),
        CES=('CES', 'mean'),
        Anomaly_count=('Rain_label', lambda x: (x != 'Normal').sum())
    ).reset_index()
    return summary


if __name__ == '__main__':
    from preprocessing import load_data, preprocess, aggregate_monthly, add_season, add_decade
    from anomaly_detection import compute_climatology, compute_anomalies
    raw = load_data('data.csv')
    daily = preprocess(raw)
    monthly = aggregate_monthly(daily)
    monthly = add_season(monthly)
    monthly = add_decade(monthly)
    baseline = compute_climatology(monthly)
    df = compute_anomalies(monthly, baseline)
    print(period_comparison(df))
