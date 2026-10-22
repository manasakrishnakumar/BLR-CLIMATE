# Bangalore Climate Analytics System

Flask web application for multi-variable climate analysis and forecasting of Bangalore (1951-2024): rainfall, mean temperature and humidity, SARIMA forecasts, anomaly detection with z-scores, the Climate Extreme Score (CES = 0.6 x z_rain + 0.4 x z_temp; thresholds 1.051 and 1.300), explainable-AI pages and a prediction history stored in SQLite.

This is the standalone application (configuration A) of the DevOps study in https://github.com/manasakrishnakumar/DEVOPS (silent failures of ML services on Kubernetes), which deploys the same models as a monolith, with Docker Compose and on Kubernetes.

## Run
```bash
pip install -r requirements.txt        # Python 3.10
python run_app.py                      # http://127.0.0.1:5000  (creates database.db on first start)
```
The SARIMA models (`*.pkl`, about 1 GB in total) are stored with **Git LFS**: install git-lfs before cloning (`git lfs install`), otherwise the files are small pointer files and the forecasts will not load.

## Layout
| Path | Content |
|---|---|
| `app.py`, `run_app.py` | Flask application and launcher |
| `models/`, `saved_models/`, `Backend/saved_models/` | trained SARIMA models (LFS) |
| `DATASET/`, `data.csv` | data (1951-2024) |
| `templates/`, `static/` | pages, CSS, JS, plots |
| `training_notebooks/`, `train_models.py` | training |
| `docs/` | literature survey and project analysis |
| `Bangalore_Climate_Analytics_System_Full_Report.*` | full report |

The Flask `secret_key` in `app.py` is a placeholder; change it before any real deployment.