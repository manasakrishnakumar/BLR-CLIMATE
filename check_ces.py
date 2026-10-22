import sys, os, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')
from utils import get_baseline_for_flask, load_all_models, forecast_with_loaded_models

baseline = get_baseline_for_flask()
models   = load_all_models('saved_models')

def show_forecast(label, user_rain, user_temp):
    _, ces_df = forecast_with_loaded_models(models, 12, baseline,
                                             user_rainfall=user_rain, user_temp=user_temp)
    print(f"\n{'='*60}")
    print(f"  INPUT: {label}  (Rainfall={user_rain}mm, Temp={user_temp}C)")
    print(f"{'='*60}")
    for _, row in ces_df.iterrows():
        bar = '🔴 EXTREME' if row['Climate_Condition'] == 'Extreme' else \
              '🟡 MODERATE' if row['Climate_Condition'] == 'Moderate' else '✅ Normal'
        print(f"  Month {int(row['Month']):2d}: CES={row['CES']:+.3f}  {bar}")

show_forecast("EXTREME FLOOD INPUT",   user_rain=200, user_temp=29)
show_forecast("MODERATE INPUT",        user_rain=150, user_temp=28)
show_forecast("NORMAL INPUT",          user_rain=50,  user_temp=25)
show_forecast("EXTREME DROUGHT INPUT", user_rain=0,   user_temp=18)
