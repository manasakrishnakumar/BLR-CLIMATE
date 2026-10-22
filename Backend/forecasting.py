"""
forecasting.py
Time-series forecasting using ARIMA/SARIMA for Bangalore climate variables
"""

import pandas as pd
import numpy as np
import warnings
import joblib
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

warnings.filterwarnings('ignore')

MODELS_DIR = 'saved_models'
os.makedirs(MODELS_DIR, exist_ok=True)


def adf_test(series: pd.Series, name: str = '') -> bool:
    """Augmented Dickey-Fuller test. Returns True if stationary."""
    result = adfuller(series.dropna())
    stationary = result[1] < 0.05
    print(f"ADF Test [{name}]: p-value={result[1]:.4f} → {'Stationary' if stationary else 'Non-Stationary'}")
    return stationary


def make_stationary(series: pd.Series) -> pd.Series:
    """Apply first differencing if non-stationary."""
    if not adf_test(series, series.name):
        series = series.diff().dropna()
    return series


def train_sarima(series: pd.Series, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)):
    """Fit SARIMA model."""
    model = SARIMAX(series, order=order, seasonal_order=seasonal_order,
                    enforce_stationarity=False, enforce_invertibility=False)
    fitted = model.fit(disp=False)
    return fitted


def evaluate_model(actual: np.ndarray, predicted: np.ndarray) -> dict:
    """Compute MAE, RMSE, MAPE, R2."""
    mae = mean_absolute_error(actual, predicted)
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mape = np.mean(np.abs((actual - predicted) / (actual + 1e-8))) * 100
    r2 = r2_score(actual, predicted)
    return {'MAE': round(mae, 3), 'RMSE': round(rmse, 3), 'MAPE': round(mape, 3), 'R2': round(r2, 3)}


def train_all_models(monthly: pd.DataFrame, train_cutoff_year: int = 2018):
    """
    Train SARIMA models for Rainfall, Temp_mean, Humidity.
    Save models to saved_models/.
    Returns dict of fitted models and evaluation metrics.
    """
    targets = {
        'Rainfall': (1, 1, 1),
        'Temp_mean': (1, 1, 1),
        'Humidity': (1, 1, 1),
    }

    train = monthly[monthly['Year'] <= train_cutoff_year].set_index('Date')
    test = monthly[monthly['Year'] > train_cutoff_year].set_index('Date')

    results = {}
    metrics = {}

    for var, order in targets.items():
        print(f"\n--- Training SARIMA for {var} ---")
        train_series = train[var]
        test_series = test[var]

        adf_test(train_series, var)

        fitted = train_sarima(train_series, order=order, seasonal_order=(1, 1, 1, 12))

        # In-sample + forecast for test period
        forecast_steps = len(test_series)
        forecast_obj = fitted.get_forecast(steps=forecast_steps)
        pred = forecast_obj.predicted_mean.values

        actual = test_series.values[:len(pred)]
        m = evaluate_model(actual, pred)
        metrics[var] = m
        print(f"  {var} → MAE={m['MAE']}, RMSE={m['RMSE']}, MAPE={m['MAPE']}%, R2={m['R2']}")

        # Save model
        model_path = os.path.join(MODELS_DIR, f'sarima_{var.lower()}.pkl')
        joblib.dump(fitted, model_path)
        print(f"  Model saved: {model_path}")

        results[var] = {
            'model': fitted,
            'train': train_series,
            'test': test_series,
            'pred_test': pd.Series(pred, index=test_series.index[:len(pred)]),
        }

    return results, metrics


def forecast_future(results: dict, steps: int = 24) -> pd.DataFrame:
    """
    Generate future forecasts for all variables.
    Returns a DataFrame with future dates and forecasted values.
    """
    future_dfs = []
    for var, res in results.items():
        fitted = res['model']
        fc = fitted.get_forecast(steps=steps)
        fc_mean = fc.predicted_mean
        fc_mean.name = var
        future_dfs.append(fc_mean)

    future_df = pd.concat(future_dfs, axis=1).reset_index()
    future_df.columns = ['Date'] + list(results.keys())
    return future_df


if __name__ == '__main__':
    from preprocessing import load_data, preprocess, aggregate_monthly, add_season, add_decade
    raw = load_data('data.csv')
    daily = preprocess(raw)
    monthly = aggregate_monthly(daily)
    monthly = add_season(monthly)
    monthly = add_decade(monthly)
    results, metrics = train_all_models(monthly)
    print("\nEvaluation Metrics:")
    print(pd.DataFrame(metrics).T)
    future = forecast_future(results, steps=24)
    print("\nFuture Forecast (first 6 rows):")
    print(future.head(6))
