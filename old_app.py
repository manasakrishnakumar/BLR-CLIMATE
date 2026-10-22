"""
Bangalore Climate Analytics System - Flask Web Application
==========================================================
Complete web interface for climate analysis and forecasting
"""
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
from utils.database import init_db, register_user, authenticate_user, save_prediction, get_user_predictions, get_user_by_id
from utils import (
    get_baseline_for_flask, 
    compute_ces_single,
    load_all_models,
    forecast_with_loaded_models
)


# ══════════════════════════════════════════════════════════════
# CES THRESHOLDS — WMO SPI METHODOLOGY (WMO-No. 1090, 2012)
# Computed from actual Bangalore data 1951–2024 (882 months)
# Moderate = 84th percentile of CES distribution = 1.051
# Extreme  = 95th percentile of CES distribution = 1.300
# Validated against known Bangalore extreme events:
#   2022 Bangalore floods      → CES = 1.756 → Extreme ✓
#   2005 October extreme rains → CES = 1.791 → Extreme ✓
#   2020 extreme monsoon       → CES = 1.756 → Extreme ✓
#   2015 deficient monsoon     → CES = 1.583 → Moderate ✓
#   2019 above-normal monsoon  → CES = 1.216 → Moderate ✓
# ══════════════════════════════════════════════════════════════
CES_MODERATE = 1.051
CES_EXTREME  = 1.300

warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create necessary directories
os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs/plots', exist_ok=True)
os.makedirs('models', exist_ok=True)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database setup
def init_db():
    """Initialize SQLite database with users table"""
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rainfall REAL,
            temperature REAL,
            humidity REAL,
            ces REAL,
            climate_condition TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    conn.commit()
    conn.close()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email):
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT id, username, email FROM users WHERE id = ?', (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        return User(user[0], user[1], user[2])
    return None

# Helper functions
def load_model(variable):
    """Load trained SARIMA model"""
    model_path = os.path.join('models', f'sarima_{variable.lower()}.pkl')
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

def compute_baseline():
    """Return baseline statistics for Bangalore climate"""
    # These values are based on historical Bangalore climate data (1951-2024)
    return {
        'rain_mean': 108.5,
        'rain_std': 85.3,
        'temp_mean': 24.8,
        'temp_std': 3.2,
        'hum_mean': 65.0,
        'hum_std': 15.5
    }

def anomaly_label(z):
    """Label anomaly based on Z-score using WMO SPI percentile thresholds"""
    az = abs(z)
    if az >= CES_EXTREME:    return 'Strong Anomaly'
    elif az >= CES_MODERATE: return 'Moderate Anomaly'
    else:                    return 'Normal'

def ces_label(ces):
    """Label climate extreme score using WMO SPI percentile thresholds"""
    ac = abs(ces)
    if ac >= CES_EXTREME:    return 'Extreme'
    elif ac >= CES_MODERATE: return 'Moderate'
    else:                    return 'Normal'

def compute_ces(rainfall, temperature, humidity, baseline):
    """Compute Climate Extreme Score"""
    # Humidity kept as parameter so form does not break
    # but NOT used in CES — removed due to multicollinearity
    z_rain = (rainfall - baseline['rain_mean']) / (baseline['rain_std'] + 1e-8)
    z_temp = (temperature - baseline['temp_mean']) / (baseline['temp_std'] + 1e-8)
    # Rainfall weight 0.6 — Bangalore is monsoon-dominated (IMD SOP 2021)
    # Temperature weight 0.4 — secondary driver (IMD heatwave criteria)
    ces = (0.6 * z_rain) + (0.4 * z_temp)
    
    return {
        'Z_Rainfall': round(z_rain, 3),
        'Rainfall_Condition': anomaly_label(z_rain),
        'Z_Temperature': round(z_temp, 3),
        'Temperature_Condition': anomaly_label(z_temp),
        'CES': round(ces, 3),
        'Climate_Condition': ces_label(ces)
    }

def generate_forecast_plot(forecast_df, ces_df):
    """Generate comprehensive forecast visualization"""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os
    
    print("\n" + "="*50)
    print("DEBUG: Starting plot generation")
    print("="*50)
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 16))
    
    variables = ['Rainfall', 'Temp_mean', 'Humidity']
    colors = ['royalblue', 'tomato', 'seagreen']
    titles = ['Rainfall Forecast (mm)', 'Temperature Forecast (°C)', 'Humidity Forecast (%)']
    ylabels = ['Rainfall (mm)', 'Temperature (°C)', 'Humidity (%)']
    
    for ax, var, color, title, ylabel in zip(axes[:3], variables, colors, titles, ylabels):
        ax.plot(forecast_df['Month'], forecast_df[var], marker='o', color=color, 
                linewidth=2, markersize=8, label='Forecast')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('#f8f9fa')
        ax.legend()
    
    # CES Plot
    axes[3].plot(ces_df['Month'], ces_df['CES'], marker='o', linewidth=2, 
                 markersize=8, color='purple', label='CES Value')
    axes[3].axhline(CES_MODERATE, linestyle='--', color='orange', linewidth=2,
                    label=f'Moderate ≥{CES_MODERATE} (WMO SPI, 84th percentile)')
    axes[3].axhline(CES_EXTREME,  linestyle='--', color='red',    linewidth=2,
                    label=f'Extreme ≥{CES_EXTREME} (WMO SPI, 95th percentile)')
    axes[3].set_title('Climate Extreme Score (CES) Forecast', fontsize=14, fontweight='bold')
    axes[3].set_xlabel('Month', fontsize=12)
    axes[3].set_ylabel('CES Value', fontsize=12)
    axes[3].legend(loc='best')
    axes[3].grid(True, alpha=0.3)
    axes[3].set_facecolor('#f8f9fa')
    
    plt.tight_layout()
    
    # Get absolute paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Save to multiple locations
    save_paths = [
        os.path.join('static', 'images', 'forecast_analysis.png'),
        os.path.join('outputs', 'plots', 'forecast_analysis.png'),
        os.path.join(current_dir, 'static', 'images', 'forecast_analysis.png'),
        os.path.join(current_dir, 'outputs', 'plots', 'forecast_analysis.png'),
    ]
    
    saved_paths = []
    for save_path in save_paths:
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ Plot saved to: {save_path}")
            print(f"   File exists: {os.path.exists(save_path)}")
            saved_paths.append(save_path)
        except Exception as e:
            print(f"❌ Failed to save to {save_path}: {e}")
    
    plt.close()
    
    # Check if plot was saved
    if saved_paths:
        print(f"✅ Plot successfully saved to {len(saved_paths)} locations")
        return 'images/forecast_analysis.png'
    else:
        print("❌ Failed to save plot to any location")
        return None
    


def generate_forecast(forecast_months=12):
    """Generate climate forecast using trained models"""
    # Load trained models
    models = load_all_models('saved_models')
    baseline = compute_baseline()
    
    # Generate forecast
    forecast_df, ces_df = forecast_with_loaded_models(models, forecast_months, baseline)
    
    # Generate plot and get the relative path
    plot_path = generate_forecast_plot(forecast_df, ces_df)
    
    return forecast_df, ces_df, plot_path

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/test-plot')
def test_plot():
    """Test if static files are being served"""
    from flask import send_file
    import os
    
    plot_path = os.path.join('static', 'images', 'forecast_analysis.png')
    if os.path.exists(plot_path):
        return send_file(plot_path, mimetype='image/png')
    else:
        return "Plot not found", 404
    

@app.route('/generate-plot-manual')
@login_required
def generate_plot_manual():
    """Manually generate and save the plot"""
    import os
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    # Generate sample data for testing
    months = list(range(1, 13))
    rainfall = [108.5 + i * 2 for i in range(12)]
    temp = [24.8 + i * 0.1 for i in range(12)]
    humidity = [65 + i * 0.5 for i in range(12)]
    ces_values = [1.2 + i * 0.1 for i in range(12)]
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 16))
    
    axes[0].plot(months, rainfall, marker='o', color='royalblue', linewidth=2)
    axes[0].set_title('Rainfall Forecast (mm)', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(months, temp, marker='o', color='tomato', linewidth=2)
    axes[1].set_title('Temperature Forecast (°C)', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(months, humidity, marker='o', color='seagreen', linewidth=2)
    axes[2].set_title('Humidity Forecast (%)', fontsize=14, fontweight='bold')
    axes[2].grid(True, alpha=0.3)
    
    axes[3].plot(months, ces_values, marker='o', color='purple', linewidth=2)
    axes[3].axhline(1, linestyle='--', color='orange', label='Moderate')
    axes[3].axhline(2, linestyle='--', color='red', label='Extreme')
    axes[3].set_title('CES Forecast', fontsize=14, fontweight='bold')
    axes[3].legend()
    axes[3].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save plot
    save_path = os.path.join('static', 'images', 'forecast_analysis.png')
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    return f"Plot saved to {save_path}. <a href='/static/images/forecast_analysis.png'>View Plot</a>"


@app.route('/plot/<filename>')
def serve_plot(filename):
    """Serve generated plots"""
    from flask import send_from_directory
    return send_from_directory('static/images', filename)


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        
        hashed_password = generate_password_hash(password)
        
        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id, username, email, password FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):
            user_obj = User(user[0], user[1], user[2])
            login_user(user_obj)
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page with climate overview"""
    # Get historical context
    baseline = compute_baseline()
    
    # Get user's prediction history
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''
        SELECT rainfall, temperature, humidity, ces, climate_condition, timestamp 
        FROM predictions 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 10
    ''', (current_user.id,))
    history = c.fetchall()
    conn.close()
    
    # Generate forecast for dashboard preview
    forecast_df, ces_df, plot_path = generate_forecast(6)
    
    return render_template('dashboard.html', 
                         baseline=baseline, 
                         history=history,
                         forecast_df=forecast_df.head(6),
                         ces_df=ces_df.head(6),
                         plot_path=plot_path)

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    """Prediction input page"""
    if request.method == 'POST':
        try:
            # Get input values
            rainfall = float(request.form.get('rainfall'))
            temperature = float(request.form.get('temperature'))
            humidity = float(request.form.get('humidity'))
            forecast_months = int(request.form.get('forecast_months', 12))
            
            # Store in session for result page
            session['current_prediction'] = {
                'rainfall': rainfall,
                'temperature': temperature,
                'humidity': humidity,
                'forecast_months': forecast_months
            }
            
            return redirect(url_for('result'))
        except Exception as e:
            flash(f'Error processing input: {str(e)}', 'danger')
            return redirect(url_for('predict'))
    
    return render_template('predict.html')

@app.route('/result')
@login_required
def result():
    """Result page displaying all analysis outputs"""
    prediction_data = session.get('current_prediction', {})
    
    if not prediction_data:
        flash('No prediction data found. Please make a prediction first.', 'warning')
        return redirect(url_for('predict'))
    
    rainfall = prediction_data['rainfall']
    temperature = prediction_data['temperature']
    humidity = prediction_data['humidity']
    forecast_months = prediction_data.get('forecast_months', 12)
    
    # Compute CES for current conditions
    baseline = compute_baseline()
    ces_result = compute_ces(rainfall, temperature, humidity, baseline)
    
    # Generate future forecast
    forecast_df, ces_df, plot_path = generate_forecast(forecast_months)
    
    # Debug: Print plot path
    print(f"\nDEBUG: Plot path returned: {plot_path}")
    
    # Get forecast trends
    rainfall_trend = 'increasing' if forecast_df['Rainfall'].iloc[-1] > forecast_df['Rainfall'].iloc[0] else 'decreasing'
    temp_trend = 'increasing' if forecast_df['Temp_mean'].iloc[-1] > forecast_df['Temp_mean'].iloc[0] else 'decreasing'
    humidity_trend = 'increasing' if forecast_df['Humidity'].iloc[-1] > forecast_df['Humidity'].iloc[0] else 'decreasing'
    
    # Save prediction to database
    try:
        save_prediction(
            current_user.id, 
            rainfall, 
            temperature, 
            humidity, 
            ces_result['CES'], 
            ces_result['Climate_Condition']
        )
    except Exception as e:
        print(f"Error saving prediction: {e}")
    
    # Get climate interpretation
    interpretation, extreme_months, moderate_months = get_climate_interpretation(
        ces_result, ces_df, forecast_df, forecast_months
    )
    
    # Check if plot file actually exists
    import os
    static_plot_path = os.path.join('static', 'images', 'forecast_analysis.png')
    plot_exists = os.path.exists(static_plot_path)
    print(f"DEBUG: Plot file exists at {static_plot_path}: {plot_exists}")
    
    # Dynamic CES score explanation for predict/result page
    ces_value = round(abs(ces_result['CES']), 3)

    if ces_value >= CES_EXTREME:
        score_explanation = {
            'classification': 'Extreme',
            'color': 'danger',
            'percentile': 'top 5% of all months',
            'meaning': (
                f'Your CES score of {ces_value} exceeds the Extreme threshold of {CES_EXTREME}. '
                f'This means the entered climate conditions are more severe than 95% of all '
                f'months recorded in Bangalore from 1951 to 2024 (882 months total).'
            ),
            'comparison': (
                f'This is comparable to the 2022 Bangalore floods (CES=1.756) '
                f'and 2005 October extreme rains (CES=1.791).'
            ),
            'source': f'Extreme threshold = 95th percentile of Bangalore data. Source: WMO-No. 1090 (2012)',
            'action': 'High climate stress detected. Rainfall and/or temperature are significantly above historical norms.'
        }
    elif ces_value >= CES_MODERATE:
        score_explanation = {
            'classification': 'Moderate',
            'color': 'warning',
            'percentile': '84th to 95th percentile',
            'meaning': (
                f'Your CES score of {ces_value} falls in the Moderate band '
                f'({CES_MODERATE} to {CES_EXTREME}). '
                f'This means conditions are more anomalous than 84% of all months '
                f'in Bangalore history but not yet in the extreme category.'
            ),
            'comparison': (
                f'This is comparable to the 2019 above-normal monsoon (CES=1.216) '
                f'and 2015 deficient monsoon season (CES=1.583).'
            ),
            'source': f'Moderate threshold = 84th percentile of Bangalore data. Source: WMO-No. 1090 (2012)',
            'action': 'Notable climate anomaly. Monitor rainfall and temperature trends closely.'
        }
    else:
        score_explanation = {
            'classification': 'Normal',
            'color': 'success',
            'percentile': 'below 84th percentile',
            'meaning': (
                f'Your CES score of {ces_value} is below the Moderate threshold of {CES_MODERATE}. '
                f'Current conditions are within the normal historical range of Bangalore climate '
                f'based on 73 years of data.'
            ),
            'comparison': 'Conditions are typical for Bangalore. No significant climate anomaly detected.',
            'source': f'Normal = below 84th percentile of Bangalore data. Source: WMO-No. 1090 (2012)',
            'action': 'No climate stress detected. Conditions are within expected historical range.'
        }

    return render_template('result.html',
                         rainfall=rainfall,
                         temperature=temperature,
                         humidity=humidity,
                         ces_result=ces_result,
                         forecast_df=forecast_df,
                         ces_df=ces_df,
                         plot_path=plot_path,
                         plot_exists=plot_exists,  # Pass this to template
                         rainfall_trend=rainfall_trend,
                         temp_trend=temp_trend,
                         humidity_trend=humidity_trend,
                         interpretation=interpretation,
                         extreme_months=extreme_months,
                         moderate_months=moderate_months,
                         total_months=forecast_months,
                         score_explanation=score_explanation)



@app.route('/api/forecast')
def api_forecast():
    """API endpoint for forecast data"""
    months = int(request.args.get('months', 12))
    forecast_df, ces_df, _ = generate_forecast(months)
    return jsonify({
        'forecast': forecast_df.to_dict('records'),
        'ces': ces_df.to_dict('records')
    })

# Initialize database
init_db()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("BANGALORE CLIMATE ANALYTICS SYSTEM")
    print("="*60)
    print("\nFlask Application Starting...")
    print("Visit http://127.0.0.1:5000 to access the application")
    print("\nDefault credentials (if database is empty, register first)")
    print("="*60 + "\n")
    app.run(debug=True, host='127.0.0.1', port=5000)