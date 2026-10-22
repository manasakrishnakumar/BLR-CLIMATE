"""
===========================================================
Bangalore Climate Analytics System
===========================================================

USER INPUT BASED TESTING SCRIPT

Features:
1. User manual input
2. Forecast future climate
3. Compute anomalies
4. Compute CES
5. Climate condition analysis
6. Generate plots
7. Save outputs
8. Professional interpretation

Run:
python test_model.py
"""

# =========================================================
# IMPORTS
# =========================================================

import os
import warnings
import numpy as np
import pandas as pd
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

# =========================================================
# CREATE DIRECTORIES
# =========================================================

os.makedirs('outputs', exist_ok=True)
os.makedirs('plots', exist_ok=True)

# =========================================================
# LOAD TRAINED MODEL
# =========================================================

def load_model(variable):

    model_path = os.path.join(
        'saved_models',
        f'sarima_{variable.lower()}.pkl'
    )

    if not os.path.exists(model_path):

        raise FileNotFoundError(
            f'Model not found: {model_path}'
        )

    return joblib.load(model_path)

# =========================================================
# DATA PREPROCESSING
# =========================================================

def preprocess_data(csv_path):

    print("\nLoading dataset...")

    df = pd.read_csv(csv_path)

    # Rename columns
    df.columns = [
        'Date',
        'Rainfall',
        'Temp_Max',
        'Temp_Min',
        'Humidity'
    ]

    # Convert date
    df['Date'] = pd.to_datetime(
        df['Date'],
        errors='coerce',
        dayfirst=True
    )

    # Replace invalid values
    df['Rainfall'] = df[
        'Rainfall'
    ].replace('Tr', 0)

    # Numeric conversion
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

    # Drop invalid rows
    df = df.dropna()

    # Mean temperature
    df['Temp_mean'] = (
        df['Temp_Max'] +
        df['Temp_Min']
    ) / 2

    # Extract year and month
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Monthly aggregation
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

    print("\nDataset Processed Successfully")

    return monthly

# =========================================================
# BASELINE STATISTICS
# =========================================================

def compute_baseline(monthly):

    baseline = {

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

    return baseline

# =========================================================
# ANOMALY LABEL
# =========================================================

def anomaly_label(z):

    az = abs(z)

    if az >= CES_EXTREME:
        return 'Strong Anomaly'

    elif az >= CES_MODERATE:
        return 'Moderate Anomaly'

    else:
        return 'Normal'

# =========================================================
# CES LABEL
# =========================================================

def ces_label(ces):

    ac = abs(ces)

    if ac >= CES_EXTREME:
        return 'Extreme'

    elif ac >= CES_MODERATE:
        return 'Moderate'

    else:
        return 'Normal'

# =========================================================
# COMPUTE CES
# =========================================================

def compute_ces(
    rainfall,
    temperature,
    humidity,
    baseline
):

    # -----------------------------
    # Z Scores
    # -----------------------------

    z_rain = (
        (
            rainfall -
            baseline['rain_mean']
        ) /
        (
            baseline['rain_std'] + 1e-8
        )
    )

    z_temp = (
        (
            temperature -
            baseline['temp_mean']
        ) /
        (
            baseline['temp_std'] + 1e-8
        )
    )

    # -----------------------------
    # Weighted CES (0.6 rain + 0.4 temp, no humidity)
    # Humidity removed due to multicollinearity
    # Rainfall weight 0.6 — Bangalore is monsoon-dominated (IMD SOP 2021)
    # Temperature weight 0.4 — secondary driver (IMD heatwave criteria)
    # -----------------------------

    ces = (
        0.6 * z_rain +
        0.4 * z_temp
    )

    result = {

        'Z_Rainfall':
            round(z_rain, 3),

        'Rainfall_Condition':
            anomaly_label(z_rain),

        'Z_Temperature':
            round(z_temp, 3),

        'Temperature_Condition':
            anomaly_label(z_temp),

        'CES':
            round(ces, 3),

        'Climate_Condition':
            ces_label(ces)
    }

    return result

# =========================================================
# FORECAST FUNCTION
# =========================================================

def generate_forecast(model, steps):

    forecast = model.get_forecast(
        steps=steps
    )

    return forecast.predicted_mean

# =========================================================
# VISUALIZATION
# =========================================================

def plot_forecast(
    forecast_df,
    ces_df
):

    fig, axes = plt.subplots(
        4,
        1,
        figsize=(12, 15)
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

    # --------------------------------
    # Forecast Plots
    # --------------------------------

    for ax, var, color in zip(
        axes[:3],
        variables,
        colors
    ):

        ax.plot(
            forecast_df[var],
            marker='o',
            color=color
        )

        ax.set_title(
            f'{var} Forecast'
        )

        ax.grid(True)

    # --------------------------------
    # CES Plot
    # --------------------------------

    axes[3].plot(
        ces_df['Month'],
        ces_df['CES'],
        marker='o',
        linewidth=2
    )

    axes[3].axhline(
        CES_MODERATE,
        linestyle='--',
        color='orange',
        label=f'Moderate \u2265{CES_MODERATE}'
    )

    axes[3].axhline(
        CES_EXTREME,
        linestyle='--',
        color='red',
        label=f'Extreme \u2265{CES_EXTREME}'
    )

    axes[3].set_title(
        'Climate Extreme Score'
    )

    axes[3].legend()

    axes[3].grid(True)

    plt.tight_layout()

    save_path = os.path.join(
        'plots',
        'forecast_analysis.png'
    )

    plt.savefig(save_path)

    plt.close()

    print(
        f'\nForecast plot saved: {save_path}'
    )

# =========================================================
# MAIN PROGRAM
# =========================================================

def main():

    print("\n================================================")
    print("BANGALORE CLIMATE ANALYTICS SYSTEM")
    print("================================================")

    # --------------------------------
    # USER INPUTS
    # --------------------------------

    csv_path = input(
        "\nEnter Dataset CSV Path: "
    )

    forecast_steps = int(
        input(
            "Enter Forecast Months: "
        )
    )

    # --------------------------------
    # LOAD DATA
    # --------------------------------

    monthly = preprocess_data(
        csv_path
    )

    # --------------------------------
    # BASELINE
    # --------------------------------

    baseline = compute_baseline(
        monthly
    )

    print("\nBaseline Statistics:")

    for k, v in baseline.items():

        print(
            f'{k}: {round(v, 2)}'
        )

    # --------------------------------
    # USER MANUAL CLIMATE INPUT
    # --------------------------------

    print("\n================================================")
    print("ENTER CURRENT CLIMATE VALUES")
    print("================================================")

    rainfall = float(
        input("Enter Rainfall (mm): ")
    )

    temperature = float(
        input(
            "Enter Mean Temperature (°C): "
        )
    )

    humidity = float(
        input("Enter Humidity (%): ")
    )

    # --------------------------------
    # COMPUTE CES
    # --------------------------------

    result = compute_ces(
        rainfall,
        temperature,
        humidity,
        baseline
    )

    print("\n================================================")
    print("CURRENT CLIMATE ANALYSIS")
    print("================================================")

    for k, v in result.items():

        print(f'{k}: {v}')

    # --------------------------------
    # LOAD MODELS
    # --------------------------------

    print("\nLoading Forecast Models...")

    rainfall_model = load_model(
        'Rainfall'
    )

    temp_model = load_model(
        'Temp_mean'
    )

    humidity_model = load_model(
        'Humidity'
    )

    print("Models Loaded Successfully")

    # --------------------------------
    # FORECASTING
    # --------------------------------

    print("\nGenerating Future Forecasts...")

    rainfall_forecast = generate_forecast(
        rainfall_model,
        forecast_steps
    )

    temp_forecast = generate_forecast(
        temp_model,
        forecast_steps
    )

    humidity_forecast = generate_forecast(
        humidity_model,
        forecast_steps
    )

    # --------------------------------
    # FORECAST DATAFRAME
    # --------------------------------

    forecast_df = pd.DataFrame({

        'Rainfall':
            rainfall_forecast.values,

        'Temp_mean':
            temp_forecast.values,

        'Humidity':
            humidity_forecast.values
    })

    print("\n================================================")
    print("FUTURE CLIMATE FORECAST")
    print("================================================")

    print(
        forecast_df.round(2).to_string()
    )

    # --------------------------------
    # FUTURE CES ANALYSIS
    # --------------------------------

    ces_results = []

    for idx, row in enumerate(
        forecast_df.itertuples(),
        start=1
    ):

        analysis = compute_ces(

            row.Rainfall,
            row.Temp_mean,
            row.Humidity,
            baseline
        )

        analysis['Month'] = idx

        ces_results.append(
            analysis
        )

    ces_df = pd.DataFrame(
        ces_results
    )

    print("\n================================================")
    print("FUTURE CLIMATE EXTREME ANALYSIS")
    print("================================================")

    print(
        ces_df[
            [
                'Month',
                'Z_Rainfall',
                'Z_Temperature',
                'Z_Humidity',
                'CES',
                'Climate_Condition'
            ]
        ].to_string(index=False)
    )

    # --------------------------------
    # SAVE OUTPUTS
    # --------------------------------

    forecast_df.to_csv(

        'outputs/future_forecast.csv',
        index=False
    )

    ces_df.to_csv(

        'outputs/future_ces_analysis.csv',
        index=False
    )

    print(
        "\nOutputs saved in outputs/ folder"
    )

    # --------------------------------
    # VISUALIZATION
    # --------------------------------

    plot_forecast(
        forecast_df,
        ces_df
    )

    # --------------------------------
    # FINAL INTERPRETATION
    # --------------------------------

    print("\n================================================")
    print("FINAL INTERPRETATION")
    print("================================================")

    extreme_count = ces_df[
        ces_df['Climate_Condition']
        == 'Extreme'
    ].shape[0]

    moderate_count = ces_df[
        ces_df['Climate_Condition']
        == 'Moderate'
    ].shape[0]

    print(
        f'Extreme Climate Months: {extreme_count}'
    )

    print(
        f'Moderate Climate Months: {moderate_count}'
    )

    print(
        "\nClimate variability trends "
        "are forecasted for Bangalore."
    )

    print(
        "Rainfall and humidity anomalies "
        "contribute strongly to CES."
    )

    print(
        "Temperature trends indicate "
        "future warming variability."
    )

    print("\n================================================")
    print("SYSTEM EXECUTION COMPLETE")
    print("================================================")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == '__main__':

    main()