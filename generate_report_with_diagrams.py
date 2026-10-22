"""
generate_report_with_diagrams.py
Creates all architecture/flow diagrams and embeds them into the Word document.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patches as FancyBboxPatch
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, ArrowStyle
import numpy as np
import os, datetime, io

from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

DIAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_diagrams")
os.makedirs(DIAG_DIR, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  DIAGRAM GENERATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

C_BLUE   = "#1A5376"
C_LBLUE  = "#2E74B5"
C_TEAL   = "#148F77"
C_GREEN  = "#1E8449"
C_ORANGE = "#D68910"
C_RED    = "#C0392B"
C_GREY   = "#5D6D7E"
C_LIGHT  = "#EBF5FB"
C_WHITE  = "#FFFFFF"

def save_fig(fig, name):
    path = os.path.join(DIAG_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {name}")
    return path

def draw_box(ax, x, y, w, h, text, color=C_BLUE, fontsize=9, text_color='white', radius=0.04, bold=False):
    box = FancyBboxPatch((x - w/2, y - h/2), w, h,
                          boxstyle=f"round,pad={radius}", linewidth=1.2,
                          edgecolor='white', facecolor=color, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=fontsize,
            color=text_color, fontweight='bold' if bold else 'normal',
            zorder=4, wrap=True, multialignment='center')

def arrow(ax, x1, y1, x2, y2, color=C_GREY, lw=1.5, label=''):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.02, my, label, fontsize=7, color=color, ha='left', va='center')

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 1: System Architecture Overview
# ───────────────────────────────────────────────────────────────────────────────
def make_system_architecture():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 14); ax.set_ylim(0, 9)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')
    ax.set_facecolor('#F8FBFF')

    ax.text(7, 8.6, 'Bangalore Climate Analytics System — Architecture Overview',
            ha='center', va='center', fontsize=14, fontweight='bold', color=C_BLUE)

    # Layers
    layers = [
        (7, 7.7, 12, 0.55, 'PRESENTATION LAYER  —  HTML5 / CSS3 / Jinja2 Templates', '#D6EAF8', C_BLUE),
        (7, 6.9, 12, 0.55, 'WEB FRAMEWORK LAYER  —  Flask 2.3 | Flask-Login | REST API', '#D5F5E3', C_TEAL),
        (7, 6.1, 12, 0.55, 'BUSINESS LOGIC LAYER  —  app.py (Routes, CES, Forecast Pipeline)', '#FDEBD0', '#784212'),
        (7, 5.3, 12, 0.55, 'SCIENTIFIC UTILITIES  —  preprocessing | anomaly_detection | climate_score | forecasting', '#EBF5FB', C_LBLUE),
        (7, 4.5, 12, 0.55, 'ML / STATISTICS LAYER  —  SARIMA Models | Z-Score | ADF Test | Scipy Stats', '#F4ECF7', '#6C3483'),
        (7, 3.7, 12, 0.55, 'DATA LAYER  —  SQLite (users, predictions) | data.csv (1951–2024, 882 months)', '#FDEDEC', C_RED),
    ]
    for x, y, w, h, label, fc, tc in layers:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.05",
                              linewidth=1.5, edgecolor=tc, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=9.5,
                color=tc, fontweight='bold', zorder=3)

    # Components below
    comp_y = 2.5
    components = [
        (1.8, comp_y, 2.2, 0.8, 'User Browser\n(HTML / JS)', '#D6EAF8', C_BLUE),
        (4.5, comp_y, 2.2, 0.8, 'Flask Routes\n/predict /result\n/analysis /xai', '#D5F5E3', C_TEAL),
        (7,   comp_y, 2.2, 0.8, 'SARIMA\nModels (.pkl)\nRainfall/Temp/Hum', '#F4ECF7', '#6C3483'),
        (9.5, comp_y, 2.2, 0.8, 'SQLite DB\nusers table\npredictions table', '#FDEDEC', C_RED),
        (12.2,comp_y, 2.2, 0.8, 'data.csv\n~27,000 rows\n1951–2024', '#FDEBD0', '#784212'),
    ]
    for x, y, w, h, txt, fc, ec in components:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.05",
                              linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    # Arrows between components
    for x in [4.5, 7, 9.5, 12.2]:
        ax.annotate('', xy=(x, comp_y+0.4), xytext=(x, 3.42),
                    arrowprops=dict(arrowstyle='<->', color=C_GREY, lw=1.2))

    ax.annotate('', xy=(4.5-1.1, comp_y), xytext=(1.8+1.1, comp_y),
                arrowprops=dict(arrowstyle='<->', color=C_GREY, lw=1.2))
    ax.annotate('', xy=(7-1.1, comp_y), xytext=(4.5+1.1, comp_y),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.2))
    ax.annotate('', xy=(9.5-1.1, comp_y), xytext=(7+1.1, comp_y),
                arrowprops=dict(arrowstyle='<->', color=C_GREY, lw=1.2))
    ax.annotate('', xy=(12.2-1.1, comp_y), xytext=(9.5+1.1, comp_y),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.2))

    # User icon / label
    ax.text(1.8, 1.7, 'User', ha='center', fontsize=9, color=C_BLUE, fontweight='bold')
    ax.text(7, 1.7, 'Saved Models', ha='center', fontsize=8, color='#6C3483')
    ax.text(9.5, 1.7, 'Persistence', ha='center', fontsize=8, color=C_RED)
    ax.text(12.2, 1.7, 'Raw Dataset', ha='center', fontsize=8, color='#784212')

    ax.text(7, 0.6, 'Technology: Python 3.10  |  Flask 2.3  |  SARIMA (statsmodels 0.14)  |  Pandas  |  NumPy  |  SQLite  |  Matplotlib',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "01_system_architecture.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 2: Data Pipeline Flowchart
# ───────────────────────────────────────────────────────────────────────────────
def make_data_pipeline():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')
    ax.set_facecolor('#F8FBFF')

    ax.text(7, 6.6, 'Data Pipeline — From Raw CSV to Analysis', ha='center',
            fontsize=13, fontweight='bold', color=C_BLUE)

    # Pipeline steps (x, y, label, sublabel, color)
    steps = [
        (1.2, 3.5, 'RAW DATA\n(data.csv)', '~27,000 daily rows\n1951–2024', '#D6EAF8', C_BLUE),
        (3.3, 3.5, 'PREPROCESSING\n(preprocessing.py)', 'Parse dates\nHandle Tr values\nInterpolate NaN\nCompute Temp_mean', '#D5F5E3', C_TEAL),
        (5.7, 3.5, 'MONTHLY\nAGGREGATION', 'Rain: SUM\nTemp: MEAN\nHum: MEAN\n→ 882 records', '#FDEBD0', '#784212'),
        (8.1, 3.5, 'BASELINE\nCOMPUTATION', 'rain_mean=66.17mm\nrain_std=77.93mm\ntemp_mean=24.77°C\ntemp_std=2.18°C', '#F4ECF7', '#6C3483'),
        (10.5, 3.5, 'ANOMALY\nDETECTION', 'Z_rain, Z_temp\nZ_hum computed\nLabels: Normal/\nModerate/Strong', '#FDEDEC', C_RED),
        (12.8, 3.5, 'CES\nCOMPUTATION', '0.6×Z_rain\n+0.4×Z_temp\nClassify:\nNormal/Mod/Ext', '#FEF9E7', C_ORANGE),
    ]
    for x, y, main, sub, fc, ec in steps:
        # Main box
        box = FancyBboxPatch((x-1.0, y+0.05), 2.0, 1.0, boxstyle="round,pad=0.06",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y+0.6, main, ha='center', va='center', fontsize=8.5,
                color=ec, fontweight='bold', zorder=3, multialignment='center')
        # Sub label below
        ax.text(x, y-0.6, sub, ha='center', va='top', fontsize=7.5,
                color=C_GREY, zorder=3, multialignment='center', style='italic')

    # Arrows
    for xi in [2.2, 4.6, 7.0, 9.4, 11.8]:
        ax.annotate('', xy=(xi+0.1, 3.5+0.55), xytext=(xi-0.1, 3.5+0.55),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=2.0))

    # Output boxes at bottom
    outputs = [
        (3.5, 1.3, 'Monthly DataFrame\n(882 rows)', '#D5F5E3', C_TEAL),
        (7.0, 1.3, 'Baseline Dict\n{rain_mean, std, ...}', '#F4ECF7', '#6C3483'),
        (10.5, 1.3, 'Anomaly Labels\n(Z-scores per month)', '#FDEDEC', C_RED),
        (13.0, 1.3, 'CES Score\n+ Classification', '#FEF9E7', C_ORANGE),
    ]
    for x, y, txt, fc, ec in outputs:
        box = FancyBboxPatch((x-1.1, y-0.3), 2.2, 0.75, boxstyle="round,pad=0.05",
                              linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y+0.07, txt, ha='center', va='center', fontsize=8,
                color=ec, fontweight='bold', zorder=3, multialignment='center')

    # Down arrows to outputs
    for sx, oy in [(3.3, 1.65), (8.1, 1.65), (10.5, 1.65), (12.8, 1.65)]:
        ax.annotate('', xy=(sx, oy), xytext=(sx, 3.55),
                    arrowprops=dict(arrowstyle='->', color='#AAB7B8', lw=1.2, linestyle='dashed'))

    ax.text(7, 0.25, 'All steps are performed in-memory using Pandas DataFrames. No external database used for processing.',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "02_data_pipeline.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 3: CES Computation Flow
# ───────────────────────────────────────────────────────────────────────────────
def make_ces_flow():
    fig, ax = plt.subplots(figsize=(13, 8))
    ax.set_xlim(0, 13); ax.set_ylim(0, 8)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(6.5, 7.6, 'Climate Extreme Score (CES) — Computation Flow', ha='center',
            fontsize=13, fontweight='bold', color=C_BLUE)

    # Inputs
    inputs = [
        (1.5, 6.0, 'RAINFALL INPUT\n(mm)', C_LBLUE, '#D6EAF8'),
        (1.5, 4.0, 'TEMPERATURE INPUT\n(°C)', C_RED, '#FDEDEC'),
        (1.5, 2.0, 'HUMIDITY INPUT\n(%)', C_GREY, '#EAECEE'),
    ]
    for x, y, txt, ec, fc in inputs:
        box = FancyBboxPatch((x-1.2, y-0.45), 2.4, 0.9, boxstyle="round,pad=0.07",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=9, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    # Z-score boxes
    zboxes = [
        (4.5, 6.0, 'Z-SCORE\nRAINFALL\n(rain−66.17)/77.93', C_LBLUE, '#D6EAF8'),
        (4.5, 4.0, 'Z-SCORE\nTEMPERATURE\n(temp−24.77)/2.18', C_RED, '#FDEDEC'),
        (4.5, 2.0, 'NOT USED\nIN CES\n(multicollinearity)', C_GREY, '#EAECEE'),
    ]
    for x, y, txt, ec, fc in zboxes:
        box = FancyBboxPatch((x-1.2, y-0.55), 2.4, 1.1, boxstyle="round,pad=0.07",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    # Arrows from inputs to z-scores
    for y in [6.0, 4.0, 2.0]:
        ax.annotate('', xy=(3.3, y), xytext=(2.7, y),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=2))

    # Weight boxes
    ax.text(6.2, 6.0, '× 0.60\n(60% weight)', ha='center', va='center',
            fontsize=9, color=C_LBLUE, fontweight='bold')
    ax.text(6.2, 4.0, '× 0.40\n(40% weight)', ha='center', va='center',
            fontsize=9, color=C_RED, fontweight='bold')
    ax.text(6.2, 2.0, '× 0.00\n(excluded)', ha='center', va='center',
            fontsize=9, color=C_GREY)

    for y in [6.0, 4.0, 2.0]:
        ax.annotate('', xy=(5.8, y), xytext=(5.7, y),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.5))

    # Summation box
    sum_box = FancyBboxPatch((7.2, 4.6), 2.0, 1.8, boxstyle="round,pad=0.1",
                              linewidth=2.5, edgecolor=C_BLUE, facecolor='#D6EAF8', zorder=2)
    ax.add_patch(sum_box)
    ax.text(8.2, 5.5, 'WEIGHTED\nSUM\n0.6×Z_r + 0.4×Z_t', ha='center', va='center',
            fontsize=9, color=C_BLUE, fontweight='bold', zorder=3, multialignment='center')

    # Lines from weights to sum
    ax.plot([6.7, 7.2], [6.0, 5.8], color=C_LBLUE, lw=2)
    ax.plot([6.7, 7.2], [4.0, 5.2], color=C_RED, lw=2)

    # Arrow to sum
    ax.annotate('', xy=(7.2, 5.5), xytext=(6.95, 5.5),
                arrowprops=dict(arrowstyle='->', color=C_BLUE, lw=2))

    # Abs value
    ax.text(9.9, 5.5, '|CES|', ha='center', va='center', fontsize=11,
            color=C_BLUE, fontweight='bold')
    ax.annotate('', xy=(9.6, 5.5), xytext=(9.2, 5.5),
                arrowprops=dict(arrowstyle='->', color=C_BLUE, lw=2))

    # Classification
    classes = [
        (11.5, 6.5, '|CES| ≥ 1.300', 'EXTREME', C_RED, '#FDEDEC'),
        (11.5, 5.5, '1.051 ≤ |CES| < 1.300', 'MODERATE', C_ORANGE, '#FEF9E7'),
        (11.5, 4.5, '|CES| < 1.051', 'NORMAL', C_GREEN, '#D5F5E3'),
    ]
    for x, y, thresh, label, ec, fc in classes:
        box = FancyBboxPatch((x-1.6, y-0.4), 3.2, 0.8, boxstyle="round,pad=0.06",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y+0.1, thresh, ha='center', va='center', fontsize=8,
                color=ec, zorder=3)
        ax.text(x, y-0.15, label, ha='center', va='center', fontsize=9,
                color=ec, fontweight='bold', zorder=3)
        ax.annotate('', xy=(x-1.6, y), xytext=(10.2, y),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=1.5))

    ax.annotate('', xy=(10.2, 6.5), xytext=(10.0, 5.5),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1, linestyle='dashed'))
    ax.annotate('', xy=(10.2, 5.5), xytext=(10.0, 5.5),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1))
    ax.annotate('', xy=(10.2, 4.5), xytext=(10.0, 5.5),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1, linestyle='dashed'))

    # Direction note
    ax.text(6.5, 0.9, 'DIRECTION:  Positive CES → Flood / Heat Risk     |     Negative CES → Drought / Cold Risk',
            ha='center', fontsize=9.5, color=C_BLUE, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#D6EAF8', edgecolor=C_BLUE, linewidth=1.5))

    ax.text(6.5, 0.25, 'Source: WMO-No. 1090 (2012) SPI Methodology  |  Thresholds: 84th percentile = 1.051, 95th percentile = 1.300',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "03_ces_computation_flow.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 4: SARIMA Forecasting Pipeline
# ───────────────────────────────────────────────────────────────────────────────
def make_sarima_pipeline():
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(7, 6.6, 'SARIMA Forecasting Pipeline', ha='center',
            fontsize=13, fontweight='bold', color=C_BLUE)

    # Top row: training pipeline
    top_steps = [
        (1.3, 5.2, 'MONTHLY DATA\n882 records\n1951–2024', C_TEAL, '#D5F5E3'),
        (3.5, 5.2, 'TRAIN / TEST\nSPLIT\n1951–2018 / 2019–2023', '#784212', '#FDEBD0'),
        (5.9, 5.2, 'ADF\nSTATIONARITY\nTEST', '#6C3483', '#F4ECF7'),
        (8.2, 5.2, 'SARIMA FIT\n(1,1,1)(1,1,1,12)\n3 models', C_BLUE, '#D6EAF8'),
        (10.6, 5.2, 'MODEL\nEVALUATION\nMAE/RMSE/R²', C_ORANGE, '#FEF9E7'),
        (12.8, 5.2, 'SAVE\nMODELS\n.pkl files', C_RED, '#FDEDEC'),
    ]
    for x, y, txt, ec, fc in top_steps:
        box = FancyBboxPatch((x-1.1, y-0.55), 2.2, 1.1, boxstyle="round,pad=0.07",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    for xi in [2.4, 4.8, 7.1, 9.3, 11.7]:
        ax.annotate('', xy=(xi+0.1, 5.2), xytext=(xi-0.1, 5.2),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=2))

    ax.text(7, 4.3, '▼  INFERENCE (FORECASTING) PIPELINE  ▼', ha='center',
            fontsize=9, color=C_BLUE, fontweight='bold')

    # Bottom row: inference pipeline
    bot_steps = [
        (1.5, 3.1, 'LOAD SAVED\nMODELS\n(joblib)', C_RED, '#FDEDEC'),
        (3.9, 3.1, 'GET FORECAST\n12 steps ahead\n(get_forecast)', C_BLUE, '#D6EAF8'),
        (6.3, 3.1, 'APPLY\nRAINFALL CAPS\n(physical limits)', '#784212', '#FDEBD0'),
        (8.7, 3.1, 'USER-INPUT\nCES BLENDING\n(decay weight)', '#6C3483', '#F4ECF7'),
        (11.1, 3.1, 'CES LABELS\n+RISK TYPES\n+EVENT DESC', C_TEAL, '#D5F5E3'),
        (13.0, 3.1, 'RESULT\nPAGE\n(Flask)', C_GREEN, '#D5F5E3'),
    ]
    for x, y, txt, ec, fc in bot_steps:
        box = FancyBboxPatch((x-1.1, y-0.55), 2.2, 1.1, boxstyle="round,pad=0.07",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    for xi in [2.6, 5.1, 7.5, 9.9, 12.1]:
        ax.annotate('', xy=(xi+0.1, 3.1), xytext=(xi-0.1, 3.1),
                    arrowprops=dict(arrowstyle='->', color=C_GREY, lw=2))

    # Models box (3 separate)
    ax.text(7, 2.0, 'Three separate SARIMA models:', ha='center', fontsize=9, color=C_BLUE, fontweight='bold')
    model_info = [
        (3.0, 1.3, 'sarima_rainfall.pkl', C_LBLUE, '#D6EAF8'),
        (7.0, 1.3, 'sarima_temp_mean.pkl', C_RED, '#FDEDEC'),
        (11.0, 1.3, 'sarima_humidity.pkl', C_TEAL, '#D5F5E3'),
    ]
    for x, y, txt, ec, fc in model_info:
        box = FancyBboxPatch((x-1.6, y-0.3), 3.2, 0.6, boxstyle="round,pad=0.05",
                              linewidth=1.5, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5, color=ec,
                fontweight='bold', zorder=3)

    ax.text(7, 0.35, 'SARIMA(1,1,1)(1,1,1,12) — Captures trend + 12-month seasonality  |  ADF test for stationarity  |  joblib for model persistence',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "04_sarima_pipeline.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 5: Web Application User Flow
# ───────────────────────────────────────────────────────────────────────────────
def make_web_flow():
    fig, ax = plt.subplots(figsize=(13, 10))
    ax.set_xlim(0, 13); ax.set_ylim(0, 10)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(6.5, 9.6, 'Web Application — User Journey & Page Flow', ha='center',
            fontsize=13, fontweight='bold', color=C_BLUE)

    pages = [
        (6.5, 8.7, '🌐  HOME PAGE  ( / )', 3.5, 0.6, C_BLUE, '#D6EAF8'),
        (3.0, 7.4, '📝  REGISTER\n( /register )', 2.2, 0.8, C_TEAL, '#D5F5E3'),
        (10.0, 7.4, '🔑  LOGIN\n( /login )', 2.2, 0.8, C_TEAL, '#D5F5E3'),
        (6.5, 6.0, '📊  DASHBOARD\n( /dashboard )', 2.8, 0.8, C_BLUE, '#EBF5FB'),
        (2.0, 4.4, '📈  HISTORICAL\nANALYSIS\n( /analysis )', 2.2, 1.0, '#784212', '#FDEBD0'),
        (6.5, 4.4, '🔮  PREDICT\n( /predict )', 2.2, 0.8, '#6C3483', '#F4ECF7'),
        (11.0, 4.4, '🧠  EXPLAINABLE AI\n( /xai )', 2.2, 0.8, C_RED, '#FDEDEC'),
        (6.5, 2.8, '📋  RESULT PAGE\n( /result )', 2.8, 0.8, C_GREEN, '#D5F5E3'),
        (6.5, 1.2, '💾  REST API\n( /api/forecast )', 2.5, 0.6, C_GREY, '#EAECEE'),
    ]
    for x, y, txt, w, h, ec, fc in pages:
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.07",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=2)
        ax.add_patch(box)
        ax.text(x, y, txt, ha='center', va='center', fontsize=8.5, color=ec,
                fontweight='bold', zorder=3, multialignment='center')

    # Arrows
    def arr(x1, y1, x2, y2, label='', color=C_GREY):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color=color, lw=1.8))
        if label:
            ax.text((x1+x2)/2+0.1, (y1+y2)/2, label, fontsize=7.5, color=color)

    arr(6.5, 8.4, 3.0, 7.8, 'New user')
    arr(6.5, 8.4, 10.0, 7.8, 'Existing user')
    arr(3.0, 7.0, 10.0, 7.8, 'After register →')
    arr(10.0, 7.0, 6.5, 6.4)
    arr(6.5, 5.6, 2.0, 4.9)
    arr(6.5, 5.6, 6.5, 4.8)
    arr(6.5, 5.6, 11.0, 4.8)
    arr(6.5, 4.0, 6.5, 3.2, 'Submit values')
    arr(6.5, 2.4, 6.5, 1.5, 'API call')

    # Labels on result page
    result_items = [
        'Current CES Score', '12-Month Forecast', 'Anomaly Labels',
        'Risk Classification', 'Visualization Charts'
    ]
    for i, item in enumerate(result_items):
        bx = 1.2 + i*2.2
        by = 0.45
        box = FancyBboxPatch((bx-0.9, by-0.2), 1.8, 0.4, boxstyle="round,pad=0.04",
                              linewidth=1, edgecolor=C_GREEN, facecolor='#D5F5E3', zorder=2)
        ax.add_patch(box)
        ax.text(bx, by, item, ha='center', va='center', fontsize=7,
                color=C_GREEN, fontweight='bold', zorder=3)
        ax.plot([bx, 6.5], [by+0.2, 2.4], color='#AAB7B8', lw=0.8, linestyle='dotted', zorder=1)

    ax.text(6.5, 0.05, '* All routes except /  and /api/forecast require Login (Flask-Login @login_required)',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "05_web_app_flow.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 6: CES Scale / Band Visualization
# ───────────────────────────────────────────────────────────────────────────────
def make_ces_scale():
    fig, ax = plt.subplots(figsize=(13, 5))
    ax.set_xlim(-3, 3); ax.set_ylim(0, 5)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(0, 4.7, 'CES Scale — Normal / Moderate / Extreme Bands (WMO SPI Methodology)',
            ha='center', fontsize=12, fontweight='bold', color=C_BLUE)

    # Draw gradient band
    bar_y = 2.6; bar_h = 0.7
    # Regions
    regions = [
        (-3.0, -1.300, '#8E44AD', 'Extreme\nDrought/Cold'),
        (-1.300, -1.051, '#E67E22', 'Moderate\nDrought/Cold'),
        (-1.051, 1.051, '#27AE60', 'Normal'),
        (1.051, 1.300, '#E67E22', 'Moderate\nFlood/Heat'),
        (1.300, 3.0, '#C0392B', 'Extreme\nFlood/Heat'),
    ]
    for x0, x1, fc, lbl in regions:
        rect = plt.Rectangle((x0, bar_y), x1-x0, bar_h, facecolor=fc, alpha=0.85, zorder=2)
        ax.add_patch(rect)
        mid = (x0+x1)/2
        ax.text(mid, bar_y+bar_h/2, lbl, ha='center', va='center',
                fontsize=8.5, color='white', fontweight='bold', multialignment='center', zorder=3)

    # Threshold lines
    for xv, lbl in [(-1.300, '-1.300\n(95th pct)'), (-1.051, '-1.051\n(84th pct)'),
                     (1.051, '1.051\n(84th pct)'), (1.300, '1.300\n(95th pct)')]:
        ax.plot([xv, xv], [bar_y-0.1, bar_y+bar_h+0.1], color='white', lw=2, zorder=4)
        ax.text(xv, bar_y-0.35, lbl, ha='center', va='top', fontsize=8,
                color=C_BLUE, fontweight='bold', multialignment='center')

    # Axis line below bar
    ax.plot([-3, 3], [bar_y-0.02, bar_y-0.02], color=C_GREY, lw=0.8)
    ax.annotate('', xy=(3.0, bar_y-0.02), xytext=(-3.0, bar_y-0.02),
                arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1.5))
    ax.text(0, bar_y-0.08, '0', ha='center', va='top', fontsize=9, color=C_GREY)
    ax.text(-3.05, bar_y-0.08, 'CES', ha='right', va='top', fontsize=9,
            color=C_BLUE, fontweight='bold')

    # Current examples
    examples = [
        (-1.75, '2015 Drought\nCES=−1.75', '#8E44AD'),
        (0.1,   'Normal Month\nCES=0.10', '#27AE60'),
        (1.22,  '2019 Monsoon\nCES=1.22', '#E67E22'),
        (1.76,  '2022 Floods\nCES=1.76', '#C0392B'),
    ]
    for xv, lbl, ec in examples:
        ax.annotate('', xy=(xv, bar_y+bar_h), xytext=(xv, bar_y+bar_h+0.55),
                    arrowprops=dict(arrowstyle='->', color=ec, lw=1.5))
        ax.text(xv, bar_y+bar_h+0.65, lbl, ha='center', va='bottom',
                fontsize=7.5, color=ec, fontweight='bold', multialignment='center')

    ax.text(0, 1.0,
            'Positive CES → Above-normal rainfall/temperature (Flood/Heat Risk)     '
            '|     Negative CES → Below-normal rainfall/temperature (Drought/Cold Risk)',
            ha='center', fontsize=9, color=C_BLUE,
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#D6EAF8', edgecolor=C_BLUE, lw=1.5))

    ax.text(0, 0.25,
            'Thresholds derived from 882-month Bangalore dataset (1951–2024) — 84th percentile = Moderate, 95th percentile = Extreme',
            ha='center', fontsize=8, color=C_GREY, style='italic')

    return save_fig(fig, "06_ces_scale.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 7: Module Dependency Map
# ───────────────────────────────────────────────────────────────────────────────
def make_module_map():
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(0, 12); ax.set_ylim(0, 7)
    ax.axis('off')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(6, 6.6, 'Module Dependency Map', ha='center',
            fontsize=13, fontweight='bold', color=C_BLUE)

    mods = {
        'app.py':              (6.0, 5.5, C_BLUE,    '#D6EAF8',  2.4, 0.7),
        'preprocessing.py':    (1.5, 3.8, C_TEAL,    '#D5F5E3',  2.2, 0.65),
        'anomaly_detection.py':(4.5, 3.8, C_ORANGE,  '#FEF9E7',  2.2, 0.65),
        'climate_score.py':    (7.5, 3.8, '#6C3483',  '#F4ECF7', 2.2, 0.65),
        'forecasting.py':      (10.5,3.8, C_RED,      '#FDEDEC', 2.2, 0.65),
        'database.py':         (3.0, 2.0, C_GREY,     '#EAECEE', 2.2, 0.65),
        'data.csv':            (1.5, 0.8, '#784212',  '#FDEBD0', 2.0, 0.55),
        'saved_models/':       (10.5,0.8, C_RED,      '#FDEDEC', 2.2, 0.55),
        'database.db':         (5.0, 0.8, C_GREY,     '#EAECEE', 2.0, 0.55),
        'templates/':          (6.0, 7.0, '#2471A3',  '#D6EAF8', 2.2, 0.55),
    }
    pos = {}
    for name, (x, y, ec, fc, w, h) in mods.items():
        pos[name] = (x, y)
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.06",
                              linewidth=2, edgecolor=ec, facecolor=fc, zorder=3)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', fontsize=8.5, color=ec,
                fontweight='bold', zorder=4)

    # Dependencies
    deps = [
        ('app.py', 'preprocessing.py'),
        ('app.py', 'anomaly_detection.py'),
        ('app.py', 'climate_score.py'),
        ('app.py', 'forecasting.py'),
        ('app.py', 'database.py'),
        ('app.py', 'templates/'),
        ('preprocessing.py', 'data.csv'),
        ('anomaly_detection.py', 'data.csv'),
        ('forecasting.py', 'saved_models/'),
        ('database.py', 'database.db'),
    ]
    for src, dst in deps:
        x1, y1 = pos[src]
        x2, y2 = pos[dst]
        ax.annotate('', xy=(x2, y2+0.3 if y2 < y1 else y2-0.3),
                    xytext=(x1, y1-0.35 if y2 < y1 else y1+0.35),
                    arrowprops=dict(arrowstyle='->', color='#808B96', lw=1.4,
                                    connectionstyle='arc3,rad=0.0'))

    legend_items = [
        (C_BLUE, 'Flask Application'), (C_TEAL, 'Data Processing'),
        (C_ORANGE, 'Anomaly Detection'), ('#6C3483', 'CES / Scoring'),
        (C_RED, 'Forecasting / Models'), (C_GREY, 'Database'),
    ]
    for i, (color, label) in enumerate(legend_items):
        bx = 0.8 + i*2.0
        box = FancyBboxPatch((bx-0.1, 0.05), 0.25, 0.25, boxstyle="round,pad=0.03",
                              linewidth=1, edgecolor=color, facecolor=color, zorder=2)
        ax.add_patch(box)
        ax.text(bx+0.25, 0.17, label, va='center', fontsize=7.5, color=C_GREY)

    return save_fig(fig, "07_module_dependency.png")

# ───────────────────────────────────────────────────────────────────────────────
# DIAGRAM 8: 12-Month CES Blending illustration
# ───────────────────────────────────────────────────────────────────────────────
def make_ces_blending():
    fig, ax = plt.subplots(figsize=(12, 5))
    months = np.arange(1, 13)

    sarima_ces = np.array([-0.78, -0.47, 0.01, 0.58, 0.96, 0.61, 0.65, 0.73, 1.04, 0.99, -0.09, -0.73])

    # Extreme user offset (CES ~1.84)
    user_offset = 1.84
    decay = 0.8 * np.maximum(0, 1 - (months-1)/11)
    extreme_blended = sarima_ces + decay * user_offset

    # Normal user offset (~0.10)
    normal_offset = 0.10
    normal_blended = sarima_ces + decay * normal_offset

    ax.fill_between(months, -1.30, -1.051, alpha=0.12, color='#8E44AD', label='_nolegend_')
    ax.fill_between(months, -1.051, 1.051, alpha=0.10, color='#27AE60', label='_nolegend_')
    ax.fill_between(months, 1.051, 1.30, alpha=0.12, color='#E67E22', label='_nolegend_')
    ax.fill_between(months, 1.30, 3.0, alpha=0.12, color='#C0392B', label='_nolegend_')

    ax.axhline(1.300, color=C_RED,    lw=1.5, ls='--', label='Extreme threshold (1.300)')
    ax.axhline(1.051, color=C_ORANGE, lw=1.5, ls='--', label='Moderate threshold (1.051)')
    ax.axhline(0,     color=C_GREY,   lw=0.8, ls='-')

    ax.plot(months, sarima_ces,      'o-', color=C_GREY,   lw=2, ms=6, label='Pure SARIMA forecast (Normal input)')
    ax.plot(months, extreme_blended, 's-', color=C_RED,    lw=2.5, ms=8, label='Blended CES — Extreme input (Rain=200, Temp=29°C)')
    ax.plot(months, normal_blended,  '^-', color=C_GREEN,  lw=2, ms=6, label='Blended CES — Normal input (Rain=50, Temp=25°C)', ls='dotted')

    ax.set_xlabel('Forecast Month', fontsize=11)
    ax.set_ylabel('CES Value', fontsize=11)
    ax.set_title('12-Month CES Forecast — User-Input-Driven Blending', fontsize=12, fontweight='bold', color=C_BLUE)
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], fontsize=9)
    ax.set_ylim(-1.5, 3.0)
    ax.legend(fontsize=9, loc='upper right')
    ax.grid(True, alpha=0.3)
    ax.set_facecolor('#F8FBFF')
    fig.patch.set_facecolor('#F8FBFF')

    ax.text(6, -1.35,
            'Blending formula: CES_blended(t) = CES_SARIMA(t) + 0.8×max(0, 1−(t−1)/11) × user_CES_offset',
            ha='center', fontsize=8, color=C_BLUE, style='italic')

    fig.tight_layout()
    return save_fig(fig, "08_ces_blending.png")

# ═══════════════════════════════════════════════════════════════════════════════
#  GENERATE ALL DIAGRAMS
# ═══════════════════════════════════════════════════════════════════════════════
print("Generating diagrams...")
d1 = make_system_architecture()
d2 = make_data_pipeline()
d3 = make_ces_flow()
d4 = make_sarima_pipeline()
d5 = make_web_flow()
d6 = make_ces_scale()
d7 = make_module_map()
d8 = make_ces_blending()
print("All diagrams generated.\n")

diagram_paths = [d1, d2, d3, d4, d5, d6, d7, d8]
diagram_titles = [
    "Figure 1: System Architecture Overview",
    "Figure 2: Data Pipeline Flowchart",
    "Figure 3: CES Computation Flow",
    "Figure 4: SARIMA Forecasting Pipeline",
    "Figure 5: Web Application — User Journey & Page Flow",
    "Figure 6: CES Scale — Normal / Moderate / Extreme Bands",
    "Figure 7: Module Dependency Map",
    "Figure 8: 12-Month CES Forecast — User-Input Blending",
]
diagram_descs = [
    "High-level layered architecture showing all six tiers of the application from the browser presentation layer down to the raw data and database layer.",
    "Step-by-step data transformation pipeline from the raw 27,000-row daily CSV file through preprocessing, monthly aggregation, baseline computation, anomaly detection, and final CES calculation.",
    "Detailed computation graph showing how rainfall and temperature inputs are converted to Z-scores, weighted, summed, and classified into Normal / Moderate / Extreme CES bands.",
    "Complete SARIMA modeling pipeline including training (ADF test → model fit → evaluation → save) and inference (load models → forecast → caps → user blending → result page).",
    "Full user journey through the web application showing all pages, navigation flows, authentication gates, and how the result page outputs map back to underlying computations.",
    "Visual representation of the CES scale from −3 to +3 showing the Normal (green), Moderate (orange), and Extreme (red) bands with historical event markers.",
    "Module dependency graph showing how app.py imports from all utility modules and how each module connects to data sources, databases, and saved models.",
    "Comparison of forecast CES trajectories for three input scenarios: pure SARIMA, extreme user input (Rain=200mm, Temp=29°C), and normal user input — demonstrating the user-driven blending.",
]

# ═══════════════════════════════════════════════════════════════════════════════
#  BUILD WORD DOCUMENT
# ═══════════════════════════════════════════════════════════════════════════════
print("Building Word document...")

doc = Document()
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Inches(1.0)
section.right_margin  = Inches(1.0)
section.top_margin    = Inches(1.0)
section.bottom_margin = Inches(1.0)

def h1(text):
    p = doc.add_heading(text, level=1)
    for run in p.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x53, 0x76)
        run.font.size = Pt(15)
    return p

def h2(text):
    p = doc.add_heading(text, level=2)
    for run in p.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x53, 0x76)
        run.font.size = Pt(12)
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
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(6)
    return p

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    return p

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

def add_table(headers, rows, col_widths=None):
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.size = Pt(9.5)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
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
            cell.paragraphs[0].runs[0].font.size = Pt(9.5)
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

def insert_image(path, width=Inches(6.2), caption='', desc=''):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(path, width=width)
    if caption:
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = cap.add_run(caption)
        cr.font.size = Pt(9)
        cr.font.color.rgb = RGBColor(0x5D, 0x6D, 0x7E)
        cr.italic = True
    if desc:
        dp = doc.add_paragraph()
        dr = dp.add_run(desc)
        dr.font.size = Pt(10)
        dp.paragraph_format.space_after = Pt(10)

# ────────────────────────────────────────────────────────────────────────────
# COVER PAGE
# ────────────────────────────────────────────────────────────────────────────
for _ in range(3): doc.add_paragraph()

tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tr_ = tp.add_run("BANGALORE CLIMATE ANALYTICS SYSTEM")
tr_.bold = True; tr_.font.size = Pt(22)
tr_.font.color.rgb = RGBColor(0x1A, 0x53, 0x76)

sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
sr_ = sp.add_run("Complete Technical Analysis & Project Documentation")
sr_.font.size = Pt(14); sr_.italic = True
sr_.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)

doc.add_paragraph()
tag = doc.add_paragraph()
tag.alignment = WD_ALIGN_PARAGRAPH.CENTER
tag.add_run("Advanced Climate Analysis  |  Anomaly Detection  |  SARIMA Forecasting  |  Flask Web Application").font.size = Pt(10)

for _ in range(3): doc.add_paragraph()

info = doc.add_table(rows=5, cols=2)
info.alignment = WD_TABLE_ALIGNMENT.CENTER
for i, (k, v) in enumerate([
    ("Project", "Bangalore Climate Analytics System"),
    ("Data Coverage", "1951 – 2024  |  73 Years  |  882 Monthly Records"),
    ("Technology", "Python 3.10  |  Flask  |  SARIMA  |  SQLite"),
    ("Methodology", "WMO SPI (WMO-No. 1090, 2012)"),
    ("Report Date", datetime.date.today().strftime("%d %B %Y")),
]):
    info.rows[i].cells[0].text = k
    info.rows[i].cells[0].paragraphs[0].runs[0].bold = True
    info.rows[i].cells[0].paragraphs[0].runs[0].font.size = Pt(10)
    info.rows[i].cells[1].text = v
    info.rows[i].cells[1].paragraphs[0].runs[0].font.size = Pt(10)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 1: EXECUTIVE SUMMARY
# ────────────────────────────────────────────────────────────────────────────
h1("1. Executive Summary")
divider()
body("The Bangalore Climate Analytics System is a full-stack scientific web application that provides "
     "historical climate analysis, Z-score based anomaly detection, composite Climate Extreme Score (CES) "
     "computation, and 12-month SARIMA-based forecasting for Bangalore, India. It covers 73 years of "
     "daily meteorological data (1951–2024) with 882 monthly aggregated records, following the "
     "WMO Standardized Precipitation Index (WMO-No. 1090, 2012) methodology.")
doc.add_paragraph()
h2("Key Highlights")
for f in [
    "73-year historical dataset — 882 monthly records from IMD (1951–2024)",
    "Z-score anomaly detection for Rainfall, Temperature, and Humidity",
    "CES = 0.6×Z_rain + 0.4×Z_temp with WMO-calibrated thresholds (1.051 Moderate, 1.300 Extreme)",
    "Three SARIMA(1,1,1)(1,1,1,12) models for Rainfall, Temperature, Humidity forecasting",
    "User-input-driven 12-month CES forecast: extreme input → risk alerts in early months",
    "User authentication (Flask-Login + SQLite), prediction history, dashboard, REST API",
    "15+ auto-generated analytical charts covering trends, anomalies, seasonal analysis",
]:
    bullet(f)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 2: ARCHITECTURE DIAGRAMS
# ────────────────────────────────────────────────────────────────────────────
h1("2. Architecture & System Diagrams")
divider()

for i, (path, title, desc) in enumerate(zip(diagram_paths, diagram_titles, diagram_descs)):
    h2(title)
    body(desc)
    insert_image(path, width=Inches(6.3), caption=title)
    doc.add_paragraph()
    if i < len(diagram_paths) - 1:
        doc.add_page_break()

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 3: TECHNOLOGY STACK
# ────────────────────────────────────────────────────────────────────────────
h1("3. Technology Stack")
divider()
add_table(
    ["Layer", "Technology", "Version", "Purpose"],
    [
        ["Backend Framework", "Flask", "2.3.3", "Web server, routing, session management"],
        ["Authentication", "Flask-Login", "0.6.2", "User sessions, @login_required protection"],
        ["Data Processing", "Pandas", "2.0.3", "DataFrames, aggregation, groupby"],
        ["Numerical Computing", "NumPy", "1.24.3", "Z-scores, array operations, decay weights"],
        ["Time Series", "Statsmodels", "0.14.0", "SARIMA fitting, ADF test, forecasting"],
        ["Auto ARIMA", "pmdarima", "2.0.4", "Automatic order selection support"],
        ["Statistical Tests", "SciPy", "1.11.1", "Linear regression for trend analysis"],
        ["ML Metrics", "Scikit-Learn", "1.3.0", "MAE, RMSE, R² model evaluation"],
        ["Visualization", "Matplotlib", "3.7.2", "All 15+ charts and diagrams"],
        ["Model Persistence", "Joblib", "1.3.2", "Save/load SARIMA .pkl files"],
        ["Database", "SQLite", "Built-in", "User accounts, prediction history"],
        ["Frontend", "HTML5+CSS3+JS", "—", "Jinja2 templates, responsive UI"],
    ],
    [1.5, 1.3, 0.8, 2.7]
)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 4: DATA PIPELINE
# ────────────────────────────────────────────────────────────────────────────
h1("4. Data Pipeline")
divider()
h2("4.1 Raw Dataset")
add_table(
    ["Column", "Description", "Unit", "Notes"],
    [
        ["Date", "Observation date", "YYYY-MM-DD", "Parsed as datetime"],
        ["Rainfall", "Daily rainfall", "mm", "'Tr'/'Trace' → 0.0"],
        ["Temp_Max", "Daily maximum temperature", "°C", "Used in Temp_mean"],
        ["Temp_Min", "Daily minimum temperature", "°C", "Used in Temp_mean"],
        ["Humidity", "Relative humidity", "%", "Daily average"],
    ]
)
doc.add_paragraph()
h2("4.2 Baseline Statistics (1951–2024)")
add_table(
    ["Variable", "Mean", "Std Dev", "Used In"],
    [
        ["Rainfall", "66.17 mm", "77.93 mm", "Z-score, CES"],
        ["Temperature", "24.77 °C", "2.18 °C", "Z-score, CES"],
        ["Humidity", "78.5 %", "~5.8 %", "Z-score (reference only)"],
    ]
)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 5: CES METHODOLOGY
# ────────────────────────────────────────────────────────────────────────────
h1("5. Climate Extreme Score (CES) Methodology")
divider()
h2("5.1 Formula")
p = doc.add_paragraph()
p.add_run("    CES  =  (0.6 × Z_rainfall)  +  (0.4 × Z_temperature)").font.size = Pt(13)
p.runs[0].bold = True; p.runs[0].font.color.rgb = RGBColor(0x1A, 0x53, 0x76)
p.runs[0].font.name = "Courier New"

doc.add_paragraph()
h2("5.2 WMO Thresholds & Historical Validation")
add_table(
    ["|CES| Range", "Classification", "Percentile", "Historical Example"],
    [
        ["< 1.051", "Normal", "Below 84th", "Typical months (~84% of dataset)"],
        ["1.051 – 1.300", "Moderate", "84th – 95th", "2019 Above-Normal Monsoon (CES=1.216)"],
        ["≥ 1.300", "Extreme", "Above 95th", "2022 Bangalore Floods (CES=1.756)"],
    ]
)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 6: FORECASTING
# ────────────────────────────────────────────────────────────────────────────
h1("6. Forecasting System")
divider()
h2("6.1 SARIMA Configuration")
add_table(
    ["Parameter", "Value", "Meaning"],
    [
        ["Order (p,d,q)", "(1,1,1)", "AR(1), first differencing, MA(1)"],
        ["Seasonal Order (P,D,Q,m)", "(1,1,1,12)", "Seasonal AR, differencing, MA — 12-month period"],
        ["Training Period", "1951–2018", "816 monthly observations"],
        ["Test Period", "2019–2023", "60 months held out for evaluation"],
        ["Models", "3 separate", "Rainfall.pkl, Temp_mean.pkl, Humidity.pkl"],
    ]
)
doc.add_paragraph()
h2("6.2 User-Input-Driven CES Blending Formula")
p = doc.add_paragraph()
p.add_run("    CES_blended(t)  =  CES_SARIMA(t)  +  decay(t) × user_CES_offset").font.size = Pt(11)
p.runs[0].font.name = "Courier New"; p.runs[0].bold = True
p2 = doc.add_paragraph()
p2.add_run("    decay(t)  =  0.8 × max(0,  1 − (t−1)/(T−1))    where T = 12").font.size = Pt(11)
p2.runs[0].font.name = "Courier New"

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 7: WEB APP ROUTES
# ────────────────────────────────────────────────────────────────────────────
h1("7. Web Application Routes")
divider()
add_table(
    ["Route", "Page", "Auth Required", "Description"],
    [
        ["/", "Home", "No", "Landing page with feature overview"],
        ["/register", "Register", "No", "New user account creation"],
        ["/login", "Login", "No", "User authentication"],
        ["/dashboard", "Dashboard", "Yes", "Overview, history, 6-month forecast preview"],
        ["/predict", "Predict", "Yes", "Input form for climate values"],
        ["/result", "Result", "Yes", "Full CES analysis and 12-month forecast"],
        ["/analysis", "Analysis", "Yes", "Period, decade, seasonal historical analysis"],
        ["/xai", "Explainable AI", "Yes", "Scientific methodology transparency"],
        ["/api/forecast", "REST API", "No", "JSON: forecast + CES data"],
    ],
    [1.1, 0.9, 1.0, 3.0]
)

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 8: HOW TO USE
# ────────────────────────────────────────────────────────────────────────────
h1("8. How to Use — Demo Values")
divider()
add_table(
    ["Scenario", "Rainfall (mm)", "Temp (°C)", "Humidity (%)", "Expected CES", "Classification"],
    [
        ["Extreme Flood/Heat", "200", "29", "88", "~+1.84", "EXTREME"],
        ["Moderate Risk", "150", "28", "82", "~+1.24", "MODERATE"],
        ["Normal Conditions", "50", "25", "75", "~+0.10", "NORMAL"],
        ["Extreme Drought/Cold", "0", "18", "45", "~−1.75", "EXTREME"],
    ],
    [1.6, 1.2, 1.0, 1.2, 1.2, 1.2]
)

doc.add_paragraph()
h2("Server Startup Command")
p = doc.add_paragraph()
run = p.add_run("    python app.py      →    http://127.0.0.1:5000")
run.font.name = "Courier New"; run.font.size = Pt(11); run.bold = True

doc.add_page_break()

# ────────────────────────────────────────────────────────────────────────────
# SECTION 9: SCIENTIFIC REFERENCES
# ────────────────────────────────────────────────────────────────────────────
h1("9. Scientific References")
divider()
for ref, desc in [
    ("WMO-No. 1090 (2012)", "World Meteorological Organization. Standardized Precipitation Index User Guide."),
    ("IMD SOP 2021", "India Meteorological Department. Standard Operating Procedure for Monsoon Monitoring."),
    ("IMD Climate Change Trends (2020)", "India Meteorological Department. Climate Change Trends over India."),
    ("Box, Jenkins (2015)", "Time Series Analysis: Forecasting and Control. 5th Ed. Wiley."),
    ("Dickey & Fuller (1979)", "Distribution of the Estimators for Autoregressive Time Series with Unit Root. JASA."),
]:
    p = doc.add_paragraph()
    p.add_run(f"[{ref}]  ").bold = True
    p.add_run(desc).font.size = Pt(10)
    p.paragraph_format.space_after = Pt(6)

# ────────────────────────────────────────────────────────────────────────────
# Footer
# ────────────────────────────────────────────────────────────────────────────
doc.add_paragraph()
foot = doc.add_paragraph()
foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
fr = foot.add_run(f"Bangalore Climate Analytics System  |  {datetime.date.today().strftime('%d %B %Y')}  |  Python + Flask + SARIMA + WMO SPI")
fr.font.size = Pt(9); fr.italic = True
fr.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)

# ────────────────────────────────────────────────────────────────────────────
out_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Bangalore_Climate_Analytics_Full_Report_WITH_DIAGRAMS.docx"
)
doc.save(out_path)
print(f"\nDocument saved to:\n{out_path}")
