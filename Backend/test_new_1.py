"""
test_model.py
===========================================================
Bangalore Climate Analytics — Standalone Testing Script
===========================================================

Features:
1. Load trained SARIMA models
2. CSV testing
3. Manual input testing
4. Forecast future climate variables
5. Compute anomalies
6. Compute Climate Extreme Score (CES)
7. Generate plots
8. Save outputs
9. Climate interpretation
10. Professional formatted outputs

Usage:

1. CSV Input
python test_model.py --csv data.csv

2. Manual Input
python test_model.py --manual

3. Forecast Horizon
python test_model.py --csv data.csv --steps 24
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import argparse
import warnings
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use('Agg')

import matplotlib.pyplot as plt
import joblib

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

warnings.filterwarnings('ignore')


# =========================================================
# DIRECTORIES
# =========================================================

os.makedirs('outputs', exist_ok=True)
os.makedirs('plots', exist_ok=True)


# =========================================================
# LOAD MODEL
# =========================================================

def load_model(variable):

    path = os.path.join(
        'saved_models',
        f'sarima_{variable.lower()}.pkl'
    )

    if not os.path.exists(path):
        raise FileNotFoundError(
            f'Model not found: {path}'
        )

    return joblib.load(path)


# =========================================================
# LABEL FUNCTIONS
# =========================================================

def anomaly_label(z):

    z = abs(z)

    if z >= 2:
        return 'Strong'

    elif z >= 1:
        return 'Moderate'

    else:
        return 'Normal'


def ces_label(c):

    if c >= 2:
        return 'Extreme'

    elif c >= 1:
        return 'Moderate'

    else:
        return 'Normal'


# =========================================================
# CES COMPUTATION
# =========================================================

def compute_ces(
    rainfall,
    temp_mean,
    humidity,
    baseline_stats
):

    # -----------------------------
    # Z Scores
    # -----------------------------

    z_rain = abs(
        (
            rainfall -
            baseline_stats['rain_mean']
        ) /
        (
            baseline_stats['rain_std'] + 1e-8
        )
    )

    z_temp = abs(
        (
            temp_mean -
            baseline_stats['temp_mean']
        ) /
        (
            baseline_stats['temp_std'] + 1e-8
        )
    )

    z_humidity = abs(
        (
            humidity -
            baseline_stats['hum_mean']
        ) /
        (
            baseline_stats['hum_std'] + 1e-8
        )
    )

    # -----------------------------
    # Weighted CES
    # -----------------------------

    ces = (
        0.4 * z_rain +
        0.3 * z_temp +
        0.3 * z_humidity
    )

    return {
        'Z_Rainfall': round(z_rain, 3),
        'Rainfall_Label': anomaly_label(z_rain),

        'Z_Temp': round(z_temp, 3),
        'Temp_Label': anomaly_label(z_temp),

        'Z_Humidity': round(z_humidity, 3),
        'Humidity_Label': anomaly_label(z_humidity),

        'CES': round(ces, 3),
        'Climate_Condition': ces_label(ces)
    }


# =========================================================
# FORECAST
# =========================================================

def forecast_from_model(
    model,
    steps=12
):

    forecast = model.get_forecast(
        steps=steps
    )

    return forecast.predicted_mean


# =========================================================
# DATA PREPROCESSING
# =========================================================

def preprocess_dataset(df):

    # Rename columns
    df.columns = [
        'Date',
        'Rainfall',
        'Temp_Max',
        'Temp_Min',
        'Humidity'
    ]

    # Date conversion
    df['Date'] = pd.to_datetime(
        df['Date'],
        errors='coerce',
        dayfirst=True
    )

    # Replace invalid values
    df['Rainfall'] = df[
        'Rainfall'
    ].replace('Tr', 0)

    # Convert numeric
    numeric_cols = [
        'Rainfall',
        'Temp_Max',
        'Temp_Min',
        'Humidity'
    ]

    for col in numeric_cols:

        df[col] = pd.to_numeric(
            df[col],
            errors='coerce'
        )

    # Remove bad rows
    df = df.dropna(
        subset=numeric_cols
    )

    # Mean temperature
    df['Temp_mean'] = (
        df['Temp_Max'] +
        df['Temp_Min']
    ) / 2

    # Extract date info
    df['Year'] = df[
        'Date'
    ].dt.year

    df['Month'] = df[
        'Date'
    ].dt.month

    return df


# =========================================================
# BASELINE STATISTICS
# =========================================================

def compute_baseline(monthly):

    baseline_stats = {

        'rain_mean':
            monthly['Rainfall'].mean(),

        'rain_std':
            monthly['Rainfall'].std(),

        'temp_mean':
            monthly['Temp_mean'].mean(),

        'temp_std':
            monthly['Temp_mean'].std(),

        'hum_mean':
            monthly['Humidity'].mean(),

        'hum_std':
            monthly['Humidity'].std(),
    }

    return baseline_stats


# =========================================================
# PLOT FORECASTS
# =========================================================

def plot_forecasts(
    forecast_df,
    ces_df
):

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(12, 16)
    )

    variables = [
        'Rainfall',
        'Temp_mean',
        'Humidity'
    ]

    colors = [
        'royalblue',
        'tomato',
        'seagreen'
    ]

    # -----------------------------
    # Forecast Variables
    # -----------------------------

    for ax, var, color in zip(
        axes[:3],
        variables,
        colors
    ):

        if var in forecast_df.columns:

            ax.plot(
                range(
                    1,
                    len(forecast_df) + 1
                ),
                forecast_df[var].values,
                marker='o',
                color=color
            )

            ax.set_title(
                f'{var} Forecast'
            )

            ax.set_xlabel(
                'Future Month'
            )

            ax.set_ylabel(var)

            ax.grid(True)

    # -----------------------------
    # CES Plot
    # -----------------------------

    axes[3].plot(
        ces_df['Month'],
        ces_df['CES'],
        marker='o',
        linewidth=2
    )

    axes[3].axhline(
        1,
        linestyle='--',
        color='orange',
        label='Moderate'
    )

    axes[3].axhline(
        2,
        linestyle='--',
        color='red',
        label='Extreme'
    )

    axes[3].set_title(
        'Climate Extreme Score'
    )

    axes[3].set_xlabel(
        'Month'
    )

    axes[3].set_ylabel(
        'CES'
    )

    axes[3].legend()

    axes[3].grid(True)

    plt.tight_layout()

    save_path = os.path.join(
        'plots',
        'forecast_results.png'
    )

    plt.savefig(save_path)

    plt.close()

    print(
        f'\nForecast plots saved: {save_path}'
    )


# =========================================================
# CLIMATE INTERPRETATION
# =========================================================

def generate_interpretation(ces_df):

    extreme_count = (
        ces_df[
            ces_df['Climate_Condition']
            == 'Extreme'
        ].shape[0]
    )

    moderate_count = (
        ces_df[
            ces_df['Climate_Condition']
            == 'Moderate'
        ].shape[0]
    )

    print("\n================================================")
    print("CLIMATE INTERPRETATION")
    print("================================================")

    if extreme_count > 0:

        print(
            f'- {extreme_count} months show '
            'extreme climate conditions.'
        )

    if moderate_count > 0:

        print(
            f'- {moderate_count} months show '
            'moderate climate variability.'
        )

    print(
        '- Forecast suggests future '
        'climate fluctuations.'
    )

    print(
        '- Rainfall and humidity anomalies '
        'are key climate drivers.'
    )

    print(
        '- Temperature trend indicates '
        'possible warming signals.'
    )


# =========================================================
# MANUAL INPUT
# =========================================================

def manual_input_test(
    baseline_stats
):

    print("\n================================================")
    print("MANUAL CLIMATE INPUT")
    print("================================================")

    rainfall = float(
        input('Enter Rainfall (mm): ')
    )

    temperature = float(
        input('Enter Mean Temperature (°C): ')
    )

    humidity = float(
        input('Enter Humidity (%): ')
    )

    result = compute_ces(
        rainfall,
        temperature,
        humidity,
        baseline_stats
    )

    print("\n================================================")
    print("CLIMATE ANALYSIS RESULT")
    print("================================================")

    for k, v in result.items():
        print(f'{k}: {v}')


# =========================================================
# MAIN TEST FUNCTION
# =========================================================

def run_test(
    csv_path=None,
    steps=12,
    manual=False
):

    print("\n================================================")
    print("Bangalore Climate Analytics")
    print("================================================")

    # -----------------------------
    # LOAD DATASET
    # -----------------------------

    if csv_path:

        print(
            f'\nLoading dataset: {csv_path}'
        )

        df = pd.read_csv(csv_path)

    else:

        print(
            '\nLoading default dataset: data.csv'
        )

        df = pd.read_csv('data.csv')

    # -----------------------------
    # PREPROCESS
    # -----------------------------

    df = preprocess_dataset(df)

    # -----------------------------
    # MONTHLY AGGREGATION
    # -----------------------------

    monthly = df.groupby(
        ['Year', 'Month']
    ).agg(

        Rainfall=(
            'Rainfall',
            'sum'
        ),

        Temp_mean=(
            'Temp_mean',
            'mean'
        ),

        Humidity=(
            'Humidity',
            'mean'
        )

    ).reset_index()

    # -----------------------------
    # BASELINE
    # -----------------------------

    baseline_stats = compute_baseline(
        monthly
    )

    print("\nBaseline Statistics:")

    for k, v in baseline_stats.items():

        print(
            f'{k}: {round(v, 2)}'
        )

    # -----------------------------
    # MANUAL INPUT
    # -----------------------------

    if manual:

        manual_input_test(
            baseline_stats
        )

        return

    # -----------------------------
    # LOAD MODELS
    # -----------------------------

    print("\nLoading models...")

    models = {}

    variables = [
        'Rainfall',
        'Temp_mean',
        'Humidity'
    ]

    for var in variables:

        try:

            model = load_model(var)

            models[var] = model

            print(
                f'Loaded: {var}'
            )

        except Exception as e:

            print(
                f'ERROR loading {var}: {e}'
            )

    # -----------------------------
    # FORECASTING
    # -----------------------------

    forecasts = {}

    print(
        f'\nGenerating '
        f'{steps}-month forecasts...'
    )

    for var, model in models.items():

        forecasts[var] = forecast_from_model(
            model,
            steps
        )

    forecast_df = pd.DataFrame(
        forecasts
    )

    print("\n================================================")
    print("FORECAST RESULTS")
    print("================================================")

    print(
        forecast_df.round(2).to_string()
    )

    # -----------------------------
    # CES ANALYSIS
    # -----------------------------

    ces_results = []

    for idx, (
        timestamp,
        row
    ) in enumerate(
        forecast_df.iterrows(),
        start=1
    ):

        rain = row['Rainfall']
        temp = row['Temp_mean']
        hum = row['Humidity']

        result = compute_ces(
            rain,
            temp,
            hum,
            baseline_stats
        )

        result['Month'] = idx

        ces_results.append(result)

    ces_df = pd.DataFrame(
        ces_results
    )

    print("\n================================================")
    print("CLIMATE EXTREME ANALYSIS")
    print("================================================")

    print(
        ces_df[
            [
                'Month',
                'Z_Rainfall',
                'Z_Temp',
                'Z_Humidity',
                'CES',
                'Climate_Condition'
            ]
        ].to_string(index=False)
    )

    # -----------------------------
    # SAVE RESULTS
    # -----------------------------

    results_path = os.path.join(
        'outputs',
        'forecast_results.csv'
    )

    ces_df.to_csv(
        results_path,
        index=False
    )

    print(
        f'\nResults saved: {results_path}'
    )

    # -----------------------------
    # PLOTS
    # -----------------------------

    plot_forecasts(
        forecast_df,
        ces_df
    )

    # -----------------------------
    # INTERPRETATION
    # -----------------------------

    generate_interpretation(
        ces_df
    )

    print("\n================================================")
    print("TESTING COMPLETE")
    print("================================================")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description=
        'Bangalore Climate Analytics'
    )

    parser.add_argument(
        '--csv',
        type=str,
        default=None,
        help='CSV file path'
    )

    parser.add_argument(
        '--steps',
        type=int,
        default=12,
        help='Forecast horizon'
    )

    parser.add_argument(
        '--manual',
        action='store_true',
        help='Manual climate input'
    )

    args = parser.parse_args()

    run_test(
        csv_path=args.csv,
        steps=args.steps,
        manual=args.manual
    )