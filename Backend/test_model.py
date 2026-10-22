"""
test_model.py
Standalone testing script for Bangalore Climate Analytics models.

Usage:
    python test_model.py                    # uses default test CSV
    python test_model.py --csv mydata.csv  # specify CSV path
"""

import os
import sys
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import joblib

warnings.filterwarnings('ignore')

# ══════════════════════════════════════════════════════════════
# CES THRESHOLDS — WMO SPI METHODOLOGY (WMO-No. 1090, 2012)
# Computed from actual Bangalore data 1951–2024 (882 months)
# Moderate = 84th percentile of CES distribution = 1.051
# Extreme  = 95th percentile of CES distribution = 1.300
# ══════════════════════════════════════════════════════════════
CES_MODERATE = 1.051
CES_EXTREME  = 1.300


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def load_model(variable: str):
    path = os.path.join('saved_models', f'sarima_{variable.lower()}.pkl')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model not found: {path}. Run climate_training notebook first.")
    return joblib.load(path)


def compute_ces(rainfall, temp_mean, humidity, baseline_stats: dict) -> dict:
    """
    Compute Z-scores and CES for given values.
    Humidity kept as parameter but NOT used in CES (multicollinearity).
    baseline_stats keys: rain_mean, rain_std, temp_mean, temp_std, hum_mean, hum_std
    """
    z_rain = (rainfall - baseline_stats['rain_mean']) / (baseline_stats['rain_std'] + 1e-8)
    z_temp = (temp_mean - baseline_stats['temp_mean']) / (baseline_stats['temp_std'] + 1e-8)
    # Rainfall weight 0.6 — Bangalore is monsoon-dominated (IMD SOP 2021)
    # Temperature weight 0.4 — secondary driver (IMD heatwave criteria)
    ces = (0.6 * z_rain) + (0.4 * z_temp)

    def label_z(z):
        az = abs(z)
        if az >= CES_EXTREME:    return 'Strong Anomaly'
        elif az >= CES_MODERATE: return 'Moderate Anomaly'
        else:                    return 'Normal'

    def label_ces(c):
        a = abs(c)
        if a >= CES_EXTREME:    return 'Extreme'
        elif a >= CES_MODERATE: return 'Moderate'
        else:                   return 'Normal'

    return {
        'Z_Rainfall': round(z_rain, 3), 'Rain_Label': label_z(z_rain),
        'Z_Temp': round(z_temp, 3), 'Temp_Label': label_z(z_temp),
        'CES': round(ces, 3), 'Climate_Condition': label_ces(ces)
    }


def forecast_from_model(model, steps: int = 12) -> pd.Series:
    """Generate n-step forecast from a saved SARIMA model."""
    fc = model.get_forecast(steps=steps)
    return fc.predicted_mean


# ─────────────────────────────────────────────
# Main test routine
# ─────────────────────────────────────────────

def run_test(csv_path: str = None, steps: int = 12):
    print("\n" + "=" * 60)
    print("  Bangalore Climate Analytics — Model Testing")
    print("=" * 60)

    # Load data to compute baseline statistics
    data_path = csv_path if csv_path and os.path.exists(csv_path) else 'data.csv'
    print(f"\nLoading data from: {data_path}")

    df = pd.read_csv(data_path)
    df.columns = ['Date', 'Rainfall', 'Temp_Max', 'Temp_Min', 'Humidity']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Temp_mean'] = (df['Temp_Max'] + df['Temp_Min']) / 2
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    monthly = df.groupby(['Year', 'Month']).agg(
        Rainfall=('Rainfall', 'sum'),
        Temp_mean=('Temp_mean', 'mean'),
        Humidity=('Humidity', 'mean')
    ).reset_index()

    # Compute overall baseline
    baseline_stats = {
        'rain_mean': monthly['Rainfall'].mean(),
        'rain_std': monthly['Rainfall'].std(),
        'temp_mean': monthly['Temp_mean'].mean(),
        'temp_std': monthly['Temp_mean'].std(),
        'hum_mean': monthly['Humidity'].mean(),
        'hum_std': monthly['Humidity'].std(),
    }
    print("\nBaseline Statistics (overall):")
    for k, v in baseline_stats.items():
        print(f"  {k}: {round(v, 2)}")

    # Load models
    print("\nLoading trained models...")
    models = {}
    for var in ['Rainfall', 'Temp_mean', 'Humidity']:
        try:
            models[var] = load_model(var)
            print(f"  Loaded: {var}")
        except FileNotFoundError as e:
            print(f"  WARNING: {e}")

    if not models:
        print("\nNo models found. Please run the training notebook first.")
        return

    # Generate forecasts
    print(f"\nGenerating {steps}-month forecast...")
    forecasts = {}
    for var, model in models.items():
        forecasts[var] = forecast_from_model(model, steps=steps)

    # Build results table
    forecast_df = pd.DataFrame(forecasts)
    forecast_df.index.name = 'Future_Month'
    print("\nForecasted Values:")
    print(forecast_df.round(2).to_string())

    # Compute CES for each forecast step
    print("\nClimate Condition Analysis:")
    ces_results = []
    for i, row in forecast_df.iterrows():
        rain = row.get('Rainfall', baseline_stats['rain_mean'])
        temp = row.get('Temp_mean', baseline_stats['temp_mean'])
        hum = row.get('Humidity', baseline_stats['hum_mean'])
        ces_info = compute_ces(rain, temp, hum, baseline_stats)
        ces_info['Month'] = str(i)
        ces_results.append(ces_info)

    ces_df = pd.DataFrame(ces_results)
    print(ces_df[['Month', 'Z_Rainfall', 'Z_Temp', 'Z_Humidity', 'CES', 'Climate_Condition']].to_string(index=False))

    # Count conditions
    print("\nForecast Summary:")
    print(ces_df['Climate_Condition'].value_counts().to_string())

    # Plot
    os.makedirs('outputs', exist_ok=True)
    fig, axes = plt.subplots(4, 1, figsize=(12, 14))

    variables = ['Rainfall', 'Temp_mean', 'Humidity']
    colors = ['royalblue', 'tomato', 'seagreen']

    for ax, var, color in zip(axes[:3], variables, colors):
        if var in forecast_df.columns:
            ax.plot(range(len(forecast_df)), forecast_df[var].values, color=color, marker='o', markersize=4)
            ax.set_title(f'Forecast: {var}')
            ax.set_xlabel('Month Ahead')
            ax.set_ylabel(var)
            ax.grid(True, alpha=0.3)

    axes[3].bar(range(len(ces_df)), ces_df['CES'].values, color='purple', alpha=0.7)
    axes[3].axhline(CES_EXTREME,  color='red',    linestyle='--', label=f'Extreme ≥{CES_EXTREME}')
    axes[3].axhline(-CES_EXTREME, color='red',    linestyle='--')
    axes[3].axhline(CES_MODERATE, color='orange', linestyle=':', label=f'Moderate ≥{CES_MODERATE}')
    axes[3].axhline(-CES_MODERATE,color='orange', linestyle=':')
    axes[3].set_title('Forecasted Climate Extreme Score (CES)')
    axes[3].set_xlabel('Month Ahead')
    axes[3].set_ylabel('CES')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)

    plt.suptitle(f'Bangalore Climate Forecast — Next {steps} Months', fontsize=14)
    plt.tight_layout()
    out_path = 'outputs/test_forecast_output.png'
    plt.savefig(out_path, dpi=100)
    plt.close()
    print(f"\nForecast plot saved: {out_path}")

    # Save results CSV
    csv_out = 'outputs/test_forecast_results.csv'
    ces_df.to_csv(csv_out, index=False)
    print(f"Results CSV saved: {csv_out}")

    print("\n" + "=" * 60)
    print("  Testing Complete!")
    print("=" * 60)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Bangalore Climate Models')
    parser.add_argument('--csv', type=str, default=None, help='Path to CSV dataset')
    parser.add_argument('--steps', type=int, default=12, help='Forecast horizon (months)')
    args = parser.parse_args()
    run_test(csv_path=args.csv, steps=args.steps)
