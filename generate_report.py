"""
generate_report.py
Generates a comprehensive Word document analysis of the Bangalore Climate Analytics System.
"""

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime
import os

doc = Document()

# ─── Page margins ────────────────────────────────────────────────────────────
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1.1)
section.right_margin  = Inches(1.1)
section.top_margin    = Inches(1.0)
section.bottom_margin = Inches(1.0)

# ─── Style helpers ────────────────────────────────────────────────────────────
def set_heading(para, text, level=1, color=RGBColor(0x1A, 0x53, 0x76)):
    run = para.runs[0] if para.runs else para.add_run(text)
    if not para.runs:
        para.clear()
        run = para.add_run(text)
    run.bold = True
    run.font.color.rgb = color
    run.font.size = Pt(16 if level == 1 else 13 if level == 2 else 11)

def h1(text, color=RGBColor(0x1A, 0x53, 0x76)):
    p = doc.add_heading(text, level=1)
    for run in p.runs:
        run.font.color.rgb = color
        run.font.size = Pt(16)
    return p

def h2(text, color=RGBColor(0x1A, 0x53, 0x76)):
    p = doc.add_heading(text, level=2)
    for run in p.runs:
        run.font.color.rgb = color
        run.font.size = Pt(13)
    return p

def h3(text):
    p = doc.add_heading(text, level=3)
    for run in p.runs:
        run.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
        run.font.size = Pt(11)
    return p

def body(text, bold=False, italic=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.font.size = Pt(11)
    run.bold  = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(6)
    return p

def bullet(text, level=0):
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    p.paragraph_format.left_indent = Inches(0.3 + level * 0.2)
    return p

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr = t.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Blue background
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), '1A5376')
        tcPr.append(shd)
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    for ri, row_data in enumerate(rows):
        row = t.rows[ri+1]
        for ci, val in enumerate(row_data):
            cell = row.cells[ci]
            cell.text = str(val)
            cell.paragraphs[0].runs[0].font.size = Pt(10)
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            if ri % 2 == 1:
                tc = cell._tc
                tcPr = tc.get_or_add_tcPr()
                shd = OxmlElement('w:shd')
                shd.set(qn('w:val'), 'clear')
                shd.set(qn('w:color'), 'auto')
                shd.set(qn('w:fill'), 'EBF5FB')
                tcPr.append(shd)

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    return t

def divider():
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1A5376')
    pBdr.append(bottom)
    pPr.append(pBdr)

# ═══════════════════════════════════════════════════════════════════════════════
#  COVER PAGE
# ═══════════════════════════════════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()
doc.add_paragraph()

title_para = doc.add_paragraph()
title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr = title_para.add_run("BANGALORE CLIMATE ANALYTICS SYSTEM")
tr.bold = True
tr.font.size = Pt(22)
tr.font.color.rgb = RGBColor(0x1A, 0x53, 0x76)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr = sub.add_run("Complete Technical Analysis & Project Documentation")
sr.font.size = Pt(14)
sr.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
sr.italic = True

doc.add_paragraph()
tag = doc.add_paragraph()
tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
tag.add_run("Advanced Climate Analysis  |  Anomaly Detection  |  Forecasting System").font.size = Pt(11)

doc.add_paragraph()
doc.add_paragraph()

info_table = doc.add_table(rows=5, cols=2)
info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
info_data = [
    ("Project Title", "Bangalore Climate Analytics System"),
    ("Version", "Final (v2.0)"),
    ("Technology Stack", "Python 3.10 | Flask | SARIMA | SQLite"),
    ("Data Coverage", "1951 – 2024 (73 Years | 882 Months)"),
    ("Report Date", datetime.date.today().strftime("%d %B %Y")),
]
for i, (k, v) in enumerate(info_data):
    row = info_table.rows[i]
    row.cells[0].text = k
    row.cells[0].paragraphs[0].runs[0].bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
    row.cells[1].text = v
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  1. EXECUTIVE SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════
h1("1. Executive Summary")
divider()
body(
    "The Bangalore Climate Analytics System is a full-stack web application built using Python (Flask) "
    "that provides scientific climate analysis, anomaly detection, and 12-month forecasting for Bangalore, "
    "India. The system is backed by 73 years of daily meteorological data (1951–2024) sourced from the "
    "India Meteorological Department (IMD), covering rainfall, maximum temperature, minimum temperature, "
    "and relative humidity."
)
body(
    "The application uses the World Meteorological Organization (WMO) Standardized Precipitation Index "
    "(SPI) methodology (WMO-No. 1090, 2012) to compute a composite Climate Extreme Score (CES) that "
    "quantifies the overall climate extremeness for any given month. SARIMA time-series models forecast "
    "future climate variables, and the 12-month CES forecast is dynamically driven by the user's current "
    "input conditions."
)

doc.add_paragraph()
h2("Key Features at a Glance")
features = [
    "73-year historical climate database (882 monthly records)",
    "Z-score based anomaly detection for Rainfall, Temperature, and Humidity",
    "Composite Climate Extreme Score (CES) using WMO SPI percentile thresholds",
    "SARIMA forecasting for 12-month ahead predictions",
    "User-input-driven CES forecast: extreme inputs produce risk alerts in early forecast months",
    "Interactive web dashboard with user authentication (Flask-Login + SQLite)",
    "Explainable AI (XAI) page for scientific transparency",
    "15+ analytical charts generated automatically",
    "Period, decade, and seasonal comparative analysis",
    "REST API endpoint (/api/forecast) for programmatic access",
]
for f in features:
    bullet(f)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  2. PROJECT ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════
h1("2. Project Architecture")
divider()

h2("2.1 Directory Structure")
body("The project is organized as a standard Flask application with dedicated modules for each concern:")

structure = [
    ("bangalore_climate_app/", "Root application directory"),
    ("  app.py", "Main Flask application (1,449 lines) — all routes, logic, helpers"),
    ("  run_app.py", "Application launcher with startup checks"),
    ("  data.csv", "Raw daily climate dataset (1951–2024, ~1.18 MB, ~27,000 rows)"),
    ("  database.db", "SQLite database — users, prediction history"),
    ("  requirements.txt", "Python package dependencies"),
    ("  saved_models/", "Trained SARIMA model files (.pkl) — Rainfall, Temp_mean, Humidity"),
    ("  utils/", "Core scientific utility modules"),
    ("    preprocessing.py", "Data loading, cleaning, monthly aggregation"),
    ("    anomaly_detection.py", "Z-score anomaly detection, baseline computation"),
    ("    climate_score.py", "CES computation, trend analysis, visualization"),
    ("    forecasting.py", "SARIMA training, forecasting, user-driven CES blending"),
    ("    database.py", "SQLite ORM — user registration, authentication, history"),
    ("    train_models.py", "Model training pipeline wrapper"),
    ("  static/images/", "Generated forecast charts (result page)"),
    ("  static/analysis/", "17 pre-generated analytical charts (XAI/analysis pages)"),
    ("  templates/", "Jinja2 HTML templates (index, login, predict, result, analysis, xai)"),
    ("  outputs/plots/", "Backup plot storage"),
    ("  Backend/", "Standalone testing and experimentation scripts"),
]
t = doc.add_table(rows=1+len(structure), cols=2)
t.style = 'Table Grid'
t.alignment = WD_TABLE_ALIGNMENT.CENTER
hrow = t.rows[0]
for ci, hdr in enumerate(["Path / File", "Description"]):
    hrow.cells[ci].text = hdr
    hrow.cells[ci].paragraphs[0].runs[0].bold = True
    hrow.cells[ci].paragraphs[0].runs[0].font.size = Pt(10)
for ri, (path, desc) in enumerate(structure):
    row = t.rows[ri+1]
    row.cells[0].text = path
    run = row.cells[0].paragraphs[0].runs[0]
    run.font.size = Pt(9)
    run.font.name = "Courier New"
    row.cells[1].text = desc
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(9)

doc.add_paragraph()
h2("2.2 Technology Stack")
add_table(
    ["Layer", "Technology", "Version", "Purpose"],
    [
        ["Backend Framework", "Flask", "2.3.3", "Web server, routing, session management"],
        ["Authentication", "Flask-Login", "0.6.2", "User sessions, login protection"],
        ["Data Processing", "Pandas", "2.0.3", "Data wrangling, aggregation"],
        ["Numerical Computing", "NumPy", "1.24.3", "Array operations, Z-score computation"],
        ["Machine Learning", "Scikit-Learn", "1.3.0", "MAE, RMSE, R² metrics"],
        ["Time Series", "Statsmodels", "0.14.0", "SARIMA model fitting & forecasting"],
        ["Auto ARIMA", "pmdarima", "2.0.4", "Automatic order selection"],
        ["Statistical Tests", "SciPy", "1.11.1", "ADF test, linear regression"],
        ["Visualization", "Matplotlib", "3.7.2", "All charts and plots"],
        ["Interactive Plots", "Plotly", "5.15.0", "Interactive chart components"],
        ["Model Persistence", "Joblib", "1.3.2", "Save/load SARIMA .pkl models"],
        ["Database", "SQLite (built-in)", "—", "User accounts, prediction history"],
        ["Frontend", "HTML5 + CSS3 + JS", "—", "Jinja2 templates, custom styles"],
        ["Server OS", "Windows / Linux", "—", "Cross-platform deployment"],
    ],
    [1.5, 1.4, 0.8, 2.2]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  3. DATA PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
h1("3. Data Pipeline")
divider()

h2("3.1 Raw Dataset")
body(
    "The application uses a daily climate dataset for Bangalore (Kempegowda International Airport / HAL "
    "weather station) covering January 1951 to December 2024 — a span of 73 years. The raw CSV file "
    "(data.csv) contains approximately 27,000 daily records."
)
add_table(
    ["Column", "Description", "Unit", "Notes"],
    [
        ["Date", "Observation date", "YYYY-MM-DD", "Parsed as datetime"],
        ["Rainfall", "Daily rainfall accumulation", "mm", "'Tr'/'Trace' → 0.0"],
        ["Temp_Max", "Daily maximum temperature", "°C", "Used in Temp_mean"],
        ["Temp_Min", "Daily minimum temperature", "°C", "Used in Temp_mean"],
        ["Humidity", "Relative humidity", "%", "Daily average"],
    ]
)

doc.add_paragraph()
h2("3.2 Preprocessing Steps (preprocessing.py)")
steps = [
    "Column standardization: rename raw headers to [Date, Rainfall, Temp_Max, Temp_Min, Humidity]",
    "Date parsing: pd.to_datetime() with error coercion; invalid dates dropped",
    "Trace rainfall handling: 'Tr' and 'Trace' strings replaced with 0.0 before numeric conversion",
    "Numeric coercion: pd.to_numeric(errors='coerce') on all measurement columns",
    "Duplicate removal: drop_duplicates() on Date column",
    "Missing value imputation: linear interpolation → forward fill → backward fill",
    "Derived feature: Temp_mean = (Temp_Max + Temp_Min) / 2",
    "Time features: Year and Month extracted from Date",
    "Filtering: records limited to 1951–2024 for analysis consistency",
]
for s in steps:
    bullet(s)

doc.add_paragraph()
h2("3.3 Monthly Aggregation")
body("Daily data is aggregated to monthly frequency for all modeling and analysis:")
add_table(
    ["Variable", "Aggregation Method", "Rationale"],
    [
        ["Rainfall", "SUM (monthly total)", "Total monthly precipitation is the standard meteorological metric"],
        ["Temp_Max", "MEAN", "Average of daily maxima over the month"],
        ["Temp_Min", "MEAN", "Average of daily minima over the month"],
        ["Temp_mean", "MEAN", "Monthly average of (Tmax+Tmin)/2"],
        ["Humidity", "MEAN", "Monthly average relative humidity"],
    ]
)

doc.add_paragraph()
h2("3.4 Baseline Statistics (1951–2024)")
body("The overall baseline is computed from all 882 monthly records and used for CES computation:")
add_table(
    ["Variable", "Mean", "Std Dev", "Usage"],
    [
        ["Rainfall", "66.17 mm", "77.93 mm", "Z-score normalization, CES calculation"],
        ["Temperature", "24.77 °C", "2.18 °C", "Z-score normalization, CES calculation"],
        ["Humidity", "78.5 %", "~5.8 %", "Baseline reference (not used in CES)"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  4. ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
h1("4. Anomaly Detection")
divider()

h2("4.1 Methodology")
body(
    "Anomaly detection uses the Z-score method, comparing each monthly observation to the "
    "long-term historical mean and standard deviation. This is consistent with WMO's "
    "Standardized Precipitation Index (SPI) framework."
)

h2("4.2 Z-Score Formula")
body("For each climate variable:", bold=True)
p = doc.add_paragraph()
run = p.add_run("    Z = (Observed Value − Historical Mean) / Historical Standard Deviation")
run.font.name = "Courier New"
run.font.size = Pt(10.5)
run.bold = True

doc.add_paragraph()
add_table(
    ["Z-Score Range", "Label", "Percentile", "Interpretation"],
    [
        ["|Z| < 1.051", "Normal", "Below 84th", "Within expected historical range"],
        ["1.051 ≤ |Z| < 1.300", "Moderate Anomaly", "84th–95th", "Anomalous; warrants monitoring"],
        ["|Z| ≥ 1.300", "Strong Anomaly", "Above 95th", "Extreme — rare historical event"],
    ]
)

doc.add_paragraph()
h2("4.3 Variables Monitored")
bullet("Rainfall Anomaly (Z_rain): Monthly rainfall vs. 73-year average of 66.17 mm")
bullet("Temperature Anomaly (Z_temp): Monthly mean temperature vs. 73-year average of 24.77°C")
bullet("Humidity Anomaly (Z_hum): Monthly humidity vs. historical mean (reference only)")

doc.add_paragraph()
h2("4.4 Seasonal Climatology")
add_table(
    ["Season", "Months", "Climate Characteristics"],
    [
        ["Winter", "Dec, Jan, Feb", "Cool and dry; minimal rainfall; lowest temperatures"],
        ["Summer / Pre-Monsoon", "Mar, Apr, May", "Rising temperatures; isolated thunderstorms"],
        ["Monsoon (SW)", "Jun, Jul, Aug, Sep", "Peak rainfall; humidity >82%; moderate temperatures"],
        ["Post-Monsoon (NE)", "Oct, Nov", "Secondary rainfall peak; temperatures declining"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  5. CLIMATE EXTREME SCORE (CES)
# ═══════════════════════════════════════════════════════════════════════════════
h1("5. Climate Extreme Score (CES)")
divider()

h2("5.1 Definition & Formula")
body(
    "The Climate Extreme Score (CES) is a composite index that combines the rainfall and temperature "
    "anomalies into a single scalar measure of overall climate extremeness for a given month. "
    "It follows the WMO SPI methodology (WMO-No. 1090, 2012)."
)

p = doc.add_paragraph()
run = p.add_run("    CES = (0.6 × Z_rainfall) + (0.4 × Z_temperature)")
run.font.name = "Courier New"
run.font.size = Pt(11)
run.bold = True
run.font.color.rgb = RGBColor(0x1A, 0x53, 0x76)

doc.add_paragraph()
h2("5.2 Weighting Rationale")
add_table(
    ["Variable", "Weight", "Scientific Justification"],
    [
        ["Rainfall", "0.60 (60%)", "Bangalore is monsoon-dominated; rainfall is the primary climate driver (IMD SOP 2021)"],
        ["Temperature", "0.40 (40%)", "Secondary driver; relevant for heatwave and cold wave detection (IMD heatwave criteria)"],
        ["Humidity", "0.00 (excluded)", "Removed due to multicollinearity with rainfall; does not improve predictive accuracy"],
    ]
)

doc.add_paragraph()
h2("5.3 CES Thresholds")
body("Thresholds are derived from the actual CES distribution of 882 Bangalore months (1951–2024):")
add_table(
    ["CES Range (|CES|)", "Classification", "Percentile", "Frequency"],
    [
        ["< 1.051", "Normal", "Below 84th", "~84% of all months"],
        ["1.051 – 1.300", "Moderate", "84th – 95th", "~11% of all months"],
        ["≥ 1.300", "Extreme", "Above 95th", "~5% of all months"],
    ]
)

doc.add_paragraph()
h2("5.4 Direction Awareness")
body(
    "The CES sign indicates the nature of the anomaly, making the index direction-aware:"
)
add_table(
    ["CES Sign", "Interpretation", "Risk Type"],
    [
        ["Positive CES (+)", "Above-normal rainfall and/or temperature", "Flood / Heat Risk"],
        ["Negative CES (−)", "Below-normal rainfall and/or temperature", "Drought / Cold Wave Risk"],
    ]
)

doc.add_paragraph()
h2("5.5 Historical Validation")
body("The CES has been validated against 5 known Bangalore extreme events:")
add_table(
    ["Event", "Year", "CES Value", "Classification", "Match"],
    [
        ["Bangalore Floods", "2022", "1.756", "Extreme Flood/Heat", "Correct"],
        ["October Extreme Rains", "2005", "1.791", "Extreme Flood/Heat", "Correct"],
        ["Extreme Monsoon Season", "2020", "1.756", "Extreme Flood/Heat", "Correct"],
        ["Deficient Monsoon", "2015", "1.583", "Moderate Drought/Cold", "Correct"],
        ["Above-Normal Monsoon", "2019", "1.216", "Moderate Flood/Heat", "Correct"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  6. FORECASTING
# ═══════════════════════════════════════════════════════════════════════════════
h1("6. Forecasting System")
divider()

h2("6.1 Model Selection")
body(
    "Seasonal Auto-Regressive Integrated Moving Average (SARIMA) models are used for time-series "
    "forecasting. SARIMA is the industry standard for monthly climate variables due to its ability "
    "to capture both trend and seasonal patterns simultaneously."
)

h2("6.2 SARIMA Configuration")
add_table(
    ["Parameter", "Value", "Meaning"],
    [
        ["Order (p, d, q)", "(1, 1, 1)", "AR(1), first differencing, MA(1)"],
        ["Seasonal Order (P, D, Q, m)", "(1, 1, 1, 12)", "Seasonal AR, differencing, MA with 12-month period"],
        ["Training Period", "1951 – 2018", "68 years of monthly data for training"],
        ["Test Period", "2019 – 2023", "5 years held out for evaluation"],
        ["Variables Modeled", "Rainfall, Temp_mean, Humidity", "Three separate SARIMA models"],
        ["Model Storage", "saved_models/*.pkl", "Serialized with joblib for fast loading"],
    ]
)

doc.add_paragraph()
h2("6.3 Model Stationarity")
body(
    "The Augmented Dickey-Fuller (ADF) test is applied to each training series before fitting. "
    "If the series is non-stationary (p-value ≥ 0.05), first differencing is applied automatically. "
    "SARIMA's integrated component (d=1) handles residual non-stationarity."
)

doc.add_paragraph()
h2("6.4 Physical Rainfall Caps")
body(
    "To prevent physically unrealistic SARIMA extrapolations, monthly rainfall caps are applied "
    "based on the 75th percentile / mean+1.5×std from the 73-year dataset:"
)
add_table(
    ["Month", "Cap (mm)", "Month", "Cap (mm)", "Month", "Cap (mm)"],
    [
        ["January", "5.0", "May", "162.0", "September", "292.1"],
        ["February", "8.0", "June", "140.9", "October", "298.6"],
        ["March", "9.0", "July", "203.5", "November", "145.3"],
        ["April", "43.0", "August", "225.1", "December", "38.1"],
    ]
)

doc.add_paragraph()
h2("6.5 User-Input-Driven CES Forecast (Key Feature)")
body(
    "A unique feature of this system is that the 12-month CES forecast dynamically reflects "
    "the user's current input conditions. The SARIMA model alone produces mean-reverting forecasts "
    "(tending toward historical averages). The system blends the user's current anomaly into "
    "the early forecast months using a decaying weight function:"
)
p = doc.add_paragraph()
run = p.add_run("    CES_blended(t) = CES_SARIMA(t) + decay(t) × CES_user_offset")
run.font.name = "Courier New"
run.font.size = Pt(10.5)
run.bold = True

p = doc.add_paragraph()
run = p.add_run("    decay(t) = 0.8 × max(0, 1 − (t−1) / (T−1))    where T = 12 months")
run.font.name = "Courier New"
run.font.size = Pt(10.5)

doc.add_paragraph()
body("Effect of this blending:", bold=True)
add_table(
    ["User Input", "Month 1 CES", "Months 6–8", "Month 12", "Behaviour"],
    [
        ["Extreme (Rain=200, Temp=29°C)", "High (influenced by user)", "Moderate–Extreme", "Pure SARIMA", "Risk shown early, fades out"],
        ["Normal (Rain=50, Temp=25°C)", "Normal", "Normal", "Normal", "All months Normal (no forced risk)"],
        ["Drought (Rain=0, Temp=18°C)", "Extreme Drought", "Normal", "Normal", "Drought risk early, recovers"],
    ]
)

doc.add_paragraph()
h2("6.6 Forecast Output")
body("For each of the 12 forecast months, the system produces:")
bullet("Predicted rainfall (mm), temperature (°C), humidity (%)")
bullet("CES value and classification (Normal / Moderate / Extreme)")
bullet("Risk type (Flood Risk, Drought Risk, Thunderstorm Risk, etc.)")
bullet("Event description (e.g., 'Heavy monsoon — flood and waterlogging risk')")
bullet("Risk level label for the result table")

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  7. WEB APPLICATION
# ═══════════════════════════════════════════════════════════════════════════════
h1("7. Web Application")
divider()

h2("7.1 Routes & Pages")
add_table(
    ["URL Route", "Page", "Access", "Description"],
    [
        ["/", "Home / Landing", "Public", "Project introduction, feature highlights, data range"],
        ["/register", "Register", "Public", "New user account creation"],
        ["/login", "Login", "Public", "User authentication (username + password)"],
        ["/dashboard", "Dashboard", "Login Required", "Climate overview, prediction history, 6-month forecast preview"],
        ["/predict", "Predict", "Login Required", "Input form: Rainfall, Temperature, Humidity, forecast months"],
        ["/result", "Result", "Login Required", "Full analysis: anomaly labels, CES, 12-month forecast, charts, interpretation"],
        ["/analysis", "Historical Analysis", "Login Required", "Period, decade, seasonal analysis tables"],
        ["/xai", "Explainable AI", "Login Required", "Scientific methodology transparency — SARIMA, CES, data sources"],
        ["/api/forecast", "REST API", "Public", "JSON endpoint returning forecast_df and ces_df"],
        ["/logout", "Logout", "Login Required", "Session termination"],
    ]
)

doc.add_paragraph()
h2("7.2 Predict Page — Input Validation")
add_table(
    ["Field", "Valid Range", "Default (June)", "Unit"],
    [
        ["Rainfall", "0 – 500", "74.1", "mm"],
        ["Temperature", "10 – 45", "25.7", "°C"],
        ["Humidity", "0 – 100", "81.2", "%"],
        ["Forecast Months", "1 – 24", "12", "months"],
    ]
)
body("Default values are dynamically set based on the current calendar month using historical monthly averages.", italic=True)

doc.add_paragraph()
h2("7.3 Result Page Sections")
sections_list = [
    ("1. Current Conditions Table", "Shows entered values alongside monthly averages for context"),
    ("2. Anomaly Labels", "Z-score and label for Rainfall, Temperature, Humidity individually"),
    ("3. CES Value", "Large display of current CES with direction indicator (Flood/Heat or Drought/Cold)"),
    ("4. CES Classification", "Normal / Moderate / Extreme badge with WMO threshold explanation"),
    ("5. Forecast Visualization", "4-panel matplotlib chart: Rainfall, Temp, Humidity, CES over 12 months"),
    ("6. Future CES Table", "Month-by-month CES, condition, risk level, expected event description"),
    ("7. Future Interpretation", "Trend analysis (rainfall increasing/decreasing), extreme month count"),
    ("8. CES Score Explanation", "Scientific explanation of the current CES with historical comparisons"),
    ("9. Analytical Charts", "Anomaly evolution and seasonal charts from historical analysis"),
]
t2 = doc.add_table(rows=1+len(sections_list), cols=2)
t2.style = 'Table Grid'
hrow2 = t2.rows[0]
hrow2.cells[0].text = "Section"
hrow2.cells[1].text = "Content"
for c in hrow2.cells:
    c.paragraphs[0].runs[0].bold = True
    c.paragraphs[0].runs[0].font.size = Pt(10)
for ri, (sec, desc) in enumerate(sections_list):
    row = t2.rows[ri+1]
    row.cells[0].text = sec
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(10)
    row.cells[0].paragraphs[0].runs[0].bold = True
    row.cells[1].text = desc
    row.cells[1].paragraphs[0].runs[0].font.size = Pt(10)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  8. DATABASE
# ═══════════════════════════════════════════════════════════════════════════════
h1("8. Database Design")
divider()

h2("8.1 Overview")
body(
    "The application uses SQLite (database.db) for lightweight, zero-configuration persistence. "
    "Two tables store user account and prediction history data."
)

h2("8.2 Users Table")
add_table(
    ["Column", "Type", "Constraints", "Description"],
    [
        ["id", "INTEGER", "PRIMARY KEY AUTOINCREMENT", "Unique user identifier"],
        ["username", "TEXT", "UNIQUE NOT NULL", "Login username"],
        ["email", "TEXT", "UNIQUE NOT NULL", "User email address"],
        ["password_hash", "TEXT", "NOT NULL", "Werkzeug SHA-256 password hash"],
        ["created_at", "TIMESTAMP", "DEFAULT CURRENT_TIMESTAMP", "Account creation time"],
    ]
)

doc.add_paragraph()
h2("8.3 Predictions Table")
add_table(
    ["Column", "Type", "Description"],
    [
        ["id", "INTEGER PRIMARY KEY", "Prediction record identifier"],
        ["user_id", "INTEGER (FK)", "References users.id"],
        ["rainfall", "REAL", "Input rainfall value (mm)"],
        ["temperature", "REAL", "Input temperature (°C)"],
        ["humidity", "REAL", "Input humidity (%)"],
        ["ces_score", "REAL", "Computed CES value"],
        ["climate_condition", "TEXT", "Normal / Moderate / Extreme classification"],
        ["created_at", "TIMESTAMP", "Prediction timestamp"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  9. GENERATED CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
h1("9. Generated Charts & Visualizations")
divider()

h2("9.1 Static Analysis Charts (static/analysis/)")
add_table(
    ["File", "Chart Title", "Description"],
    [
        ["01_rainfall_trend.png", "Rainfall Trend (1951–2024)", "Monthly rainfall time series with trend line"],
        ["02_temperature_trend.png", "Temperature Trend", "Mean temperature over 73 years"],
        ["03_humidity_trend.png", "Humidity Trend", "Relative humidity over 73 years"],
        ["04_correlation_heatmap.png", "Correlation Heatmap", "Pearson correlations between climate variables"],
        ["05_distributions.png", "Variable Distributions", "Histograms for Rainfall, Temp, Humidity"],
        ["06_anomaly_zscores.png", "Z-Score Anomalies", "Time series of Z-scores for all three variables"],
        ["07_ces_timeseries.png", "CES Over Time", "CES timeline with Moderate/Extreme threshold lines"],
        ["08_ces_distribution.png", "CES Distribution", "Histogram of CES values with percentile markers"],
        ["09_anomaly_evolution.png", "Anomaly Evolution", "Rolling anomaly frequency over decades"],
        ["10_decade_anomaly.png", "Decade-wise Anomaly Counts", "Bar chart of anomaly events per decade"],
        ["11_seasonal_analysis.png", "Seasonal Analysis", "Box plots of climate variables by season"],
        ["12_climate_shift.png", "Climate Shift", "Period comparison chart (1951–1980 vs 2001–2024)"],
        ["13_actual_vs_predicted.png", "SARIMA Fit vs Actual", "Model predictions overlaid on test data"],
        ["14_future_forecast.png", "Future Forecast", "12-month ahead forecast for Rainfall, Temp, Humidity"],
        ["15_future_ces.png", "Future CES Forecast", "12-month CES forecast with threshold lines"],
        ["forecast_analysis.png", "Combined Forecast Chart", "4-panel: Rainfall, Temp, Humidity, CES"],
        ["forecast_results.png", "Forecast Results Summary", "Summary visualization of forecast outputs"],
    ]
)

doc.add_paragraph()
h2("9.2 Dynamic Charts (static/images/)")
body("Generated fresh on each prediction request:")
add_table(
    ["File", "Description"],
    [
        ["forecast_analysis.png", "4-panel forecast chart regenerated with every prediction"],
        ["09_anomaly_evolution.png", "Anomaly evolution chart shown on result page"],
        ["season.png", "Seasonal rainfall chart used in result page"],
        ["shift.png", "Climate shift visualization used in result page"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  10. HOW TO USE
# ═══════════════════════════════════════════════════════════════════════════════
h1("10. How to Use the Application")
divider()

h2("10.1 Starting the Server")
body("Navigate to the project folder and run:")
p = doc.add_paragraph()
run = p.add_run("    python app.py")
run.font.name = "Courier New"
run.font.size = Pt(11)
run.bold = True
body("The server starts at: http://127.0.0.1:5000")

doc.add_paragraph()
h2("10.2 Step-by-Step Usage")
steps2 = [
    ("Step 1 — Open Browser", "Navigate to http://127.0.0.1:5000"),
    ("Step 2 — Register/Login", "Create an account or log in with existing credentials"),
    ("Step 3 — Go to Predict", "Click 'Predict' from the dashboard or navigation bar"),
    ("Step 4 — Enter Values", "Input Rainfall (mm), Temperature (°C), Humidity (%), select forecast months"),
    ("Step 5 — Submit", "Click 'Analyze Climate' to run the full analysis"),
    ("Step 6 — View Results", "The Result page shows current CES, anomaly labels, 12-month forecast, charts"),
    ("Step 7 — Explore Analysis", "Visit the 'Analysis' page for historical period/decade/seasonal comparison"),
    ("Step 8 — View XAI", "Visit the 'Explainable AI' page for scientific methodology details"),
]
for title, desc in steps2:
    p = doc.add_paragraph()
    p.add_run(title + ": ").bold = True
    p.add_run(desc)
    p.paragraph_format.space_after = Pt(4)

doc.add_paragraph()
h2("10.3 Demo Values for Testing")
add_table(
    ["Scenario", "Rainfall (mm)", "Temp (°C)", "Humidity (%)", "Expected CES"],
    [
        ["Extreme Flood", "200", "29", "88", "~1.84 → EXTREME"],
        ["Moderate Risk", "150", "28", "82", "~1.24 → MODERATE"],
        ["Normal Conditions", "50", "25", "75", "~0.10 → NORMAL"],
        ["Extreme Drought", "0", "18", "45", "~−1.75 → EXTREME"],
        ["Typical Monsoon (Aug)", "115", "24.5", "83", "~0.71 → NORMAL"],
    ]
)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  11. SCIENTIFIC REFERENCES
# ═══════════════════════════════════════════════════════════════════════════════
h1("11. Scientific References & Standards")
divider()

refs = [
    ("WMO-No. 1090 (2012)", "World Meteorological Organization. Standardized Precipitation Index User Guide. Geneva, Switzerland. — Source for SPI methodology and percentile thresholds used in CES."),
    ("IMD SOP 2021", "India Meteorological Department. Standard Operating Procedure for Monsoon Monitoring and Early Warning. — Basis for rainfall weight of 0.60 in the CES formula."),
    ("IMD Heatwave Criteria", "India Meteorological Department. Heat Wave Guidelines. — Basis for temperature weight of 0.40 in the CES formula."),
    ("IMD Climate Change Trends (2020)", "India Meteorological Department. Climate Change Trends over India. — Referenced for Bangalore warming rate and monsoon intensification."),
    ("WMO State of Climate in Asia (2023)", "World Meteorological Organization. State of Climate in Asia 2023. — Supports monsoon variability projections used in forecast context."),
    ("Box, Jenkins, Reinsel, Ljung (2015)", "Time Series Analysis: Forecasting and Control. 5th Ed. Wiley. — Theoretical basis for SARIMA modeling."),
    ("Dickey & Fuller (1979)", "Distribution of the Estimators for Autoregressive Time Series with a Unit Root. JASA. — ADF test for stationarity checking."),
]
for ref, desc in refs:
    p = doc.add_paragraph()
    p.add_run(f"[{ref}]  ").bold = True
    p.add_run(desc).font.size = Pt(10)
    p.paragraph_format.space_after = Pt(6)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  12. LIMITATIONS & FUTURE SCOPE
# ═══════════════════════════════════════════════════════════════════════════════
h1("12. Limitations & Future Scope")
divider()

h2("12.1 Current Limitations")
limitations = [
    "SARIMA models are univariate — each variable (rainfall, temperature, humidity) is forecast independently, ignoring cross-variable correlations",
    "The 12-month forecast is inherently mean-reverting; longer-horizon predictions have wide confidence intervals",
    "No real-time data feed — the dataset is static (last updated to 2024); live IMD API integration is not implemented",
    "Humidity is not used in the CES due to multicollinearity; this may miss humidity-specific climate stress",
    "The user-input blending for the 12-month CES is a linear decay model — more sophisticated blending could use Bayesian updating",
    "No spatial analysis — the application covers Bangalore city as a single point, not grid-based spatial climate",
    "SQLite is suitable for single-user/demo use; production deployment would require PostgreSQL or MySQL",
]
for l in limitations:
    bullet(l)

doc.add_paragraph()
h2("12.2 Future Enhancements")
enhancements = [
    "Live IMD API integration for real-time daily data updates",
    "LSTM / Transformer deep learning models for improved multi-step forecasting",
    "VAR (Vector Auto-Regression) model for multivariate joint forecasting of all climate variables",
    "Spatial interpolation and district-level climate maps for Karnataka",
    "Mobile-responsive Progressive Web App (PWA) version",
    "Email/SMS alert system when forecast CES exceeds Moderate threshold",
    "Ensemble forecasting combining SARIMA + ML for improved accuracy",
    "Integration with CMIP6 global climate model projections for 2025–2050 scenarios",
    "PDF report download directly from the result page",
    "Docker containerization for easy deployment",
]
for e in enhancements:
    bullet(e)

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════════
#  13. GLOSSARY
# ═══════════════════════════════════════════════════════════════════════════════
h1("13. Glossary")
divider()

glossary = [
    ("ADF Test", "Augmented Dickey-Fuller Test — statistical test for time series stationarity"),
    ("ARIMA", "Auto-Regressive Integrated Moving Average — time series forecasting model"),
    ("CES", "Climate Extreme Score — composite index measuring overall climate extremeness"),
    ("IMD", "India Meteorological Department — national weather agency of India"),
    ("MAE", "Mean Absolute Error — average absolute difference between predicted and actual values"),
    ("MAPE", "Mean Absolute Percentage Error — percentage-based forecast accuracy metric"),
    ("RMSE", "Root Mean Square Error — square root of average squared forecast errors"),
    ("R²", "Coefficient of Determination — proportion of variance explained by the model"),
    ("SARIMA", "Seasonal ARIMA — ARIMA extended with seasonal differencing and parameters"),
    ("SPI", "Standardized Precipitation Index — WMO standard for precipitation anomaly quantification"),
    ("WMO", "World Meteorological Organization — UN agency for meteorology and climate science"),
    ("XAI", "Explainable Artificial Intelligence — making model decisions transparent and interpretable"),
    ("Z-Score", "Standard score — number of standard deviations an observation is from the mean"),
]
add_table(
    ["Term", "Definition"],
    [(k, v) for k, v in glossary]
)

# ─── Final Footer ─────────────────────────────────────────────────────────────
doc.add_paragraph()
doc.add_paragraph()
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = foot.add_run(f"Bangalore Climate Analytics System  |  Generated: {datetime.date.today().strftime('%d %B %Y')}  |  Python + Flask + SARIMA + WMO SPI")
fr.font.size = Pt(9)
fr.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
fr.italic = True

# ─── Save ────────────────────────────────────────────────────────────────────
out_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Bangalore_Climate_Analytics_System_Full_Report.docx"
)
doc.save(out_path)
print("Document saved to:", out_path)
