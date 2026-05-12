from fastapi import APIRouter
import joblib, numpy as np, sys
from datetime import datetime, timedelta

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)
router = APIRouter()

demand_model = joblib.load(os.path.join(BASE_DIR, "models", "saved", "demand_model.pkl"))
outage_model = joblib.load(os.path.join(BASE_DIR, "models", "saved", "outage_model.pkl"))

def get_risk_level(probability: float) -> str:
    if probability < 40:   return "Low"
    elif probability < 70: return "Medium"
    else:                  return "High"

def get_zones(risk: str):
    if risk == "High":     return ["G-9", "F-7", "I-8", "E-11"]
    elif risk == "Medium": return ["G-11", "F-6"]
    else:                  return []

def get_weather_factors(temp: float, wind: float,
                        rainfall: float, grid_load: float):
    factors = []
    if temp > 35:        factors.append("Heatwave alert")
    if temp < 5:         factors.append("Cold wave alert")
    if wind > 6:         factors.append("High wind speed")
    if rainfall > 10:    factors.append("Heavy rainfall")
    if grid_load > 90:   factors.append("Grid overload risk")
    if not factors:      factors.append("Normal conditions")
    return factors

def get_actions(risk: str):
    if risk == "High":
        return ["Load shedding preparation",
                "Deploy field engineers",
                "Activate demand response",
                "Public advisory"]
    elif risk == "Medium":
        return ["Pre-position repair crews",
                "Alert field engineers"]
    else:
        return ["Routine monitoring"]

@router.get("/forecast")
def get_forecast():
    forecast   = []
    today      = datetime.today()
    prev_outage = 0

    # Try to load real weather data
    weather_df = None
    weather_path = os.path.join(BASE_DIR, "data", "raw", "weather.csv")
    if os.path.exists(weather_path):
        try:
            weather_df = pd.read_csv(weather_path)
            weather_df['date_only'] = pd.to_datetime(weather_df['date']).dt.date
        except:
            pass

    for i in range(7):
        date  = today + timedelta(days=i)
        month = date.month
        
        # Default values (simulated)
        if month in [6, 7, 8]:
            temp, humidity, wind = 37.0, 62.0, 3.8
            rainfall, grid_load  = 8.0, 88.0
        elif month in [12, 1, 2]:
            temp, humidity, wind = 9.0, 72.0, 2.5
            rainfall, grid_load  = 1.0, 70.0
        else:
            temp, humidity, wind = 26.0, 55.0, 3.2
            rainfall, grid_load  = 3.0, 75.0

        # Override with real data if available (using Islamabad as primary city for forecast)
        if weather_df is not None:
            day_data = weather_df[(weather_df['date_only'] == date.date()) & (weather_df['city'] == 'Islamabad')]
            if not day_data.empty:
                # Average for the day
                temp      = float(day_data['temperature'].mean())
                humidity  = float(day_data['humidity'].mean())
                wind      = float(day_data['wind_speed'].mean())
                rainfall  = float(day_data['rainfall'].mean())
                # Recalculate grid load based on temp
                grid_load = min(98.0, 70.0 + (temp - 20) * 1.5) if temp > 20 else 70.0

        season = (0 if month in [12,1,2] else
                  1 if month in [3,4,5] else
                  2 if month in [6,7,8] else 3)

        features = np.array([[
            temp, humidity, wind, rainfall,
            grid_load, 15000.0, prev_outage, 0,
            date.weekday(), month, season]])

        demand      = float(demand_model.predict(features)[0])
        outage_prob = float(
            outage_model.predict_proba(features)[0][1] * 100)
        risk        = get_risk_level(outage_prob)
        prev_outage = 1 if outage_prob > 50 else 0

        forecast.append({
            "date":                date.strftime("%Y-%m-%d"),
            "day":                 date.strftime("%A"),
            "demand_kwh":          round(demand, 2),
            "outage_probability":  round(outage_prob, 1),
            "risk_level":          risk,
            "affected_zones":      get_zones(risk),
            "weather_factors":     get_weather_factors(
                temp, wind, rainfall, grid_load),
            "recommended_actions": get_actions(risk)
        })

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "forecast":     forecast
    }

@router.get("/forecast/{date}")
def get_forecast_detail(date: str):
    forecasts = get_forecast()["forecast"]
    for day in forecasts:
        if day["date"] == date:
            return day
    return {"error": "Date not found in forecast range"}
