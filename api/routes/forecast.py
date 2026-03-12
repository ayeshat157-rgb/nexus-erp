from fastapi import APIRouter
import joblib, numpy as np, os, sys
from datetime import datetime, timedelta

sys.path.insert(0, "D:/fyp/nexus-erp/ai-module")

router = APIRouter()

BASE_DIR = "D:/fyp/nexus-erp/ai-module"
demand_model = joblib.load(f"{BASE_DIR}/models/saved/demand_model.pkl")
outage_model = joblib.load(f"{BASE_DIR}/models/saved/outage_model.pkl")

def get_risk_level(probability: float) -> str:
    if probability < 40:   return "Low"
    elif probability < 70: return "Medium"
    else:                  return "High"

def get_zones(risk: str):
    if risk == "High":     return ["G-9", "F-7", "I-8", "E-11"]
    elif risk == "Medium": return ["G-11", "F-6"]
    else:                  return []

def get_weather_factors(temp: float, wind: float):
    factors = []
    if temp > 35:   factors.append("Heatwave alert")
    if temp < 5:    factors.append("Cold wave alert")
    if wind > 5:    factors.append("High wind speed")
    if not factors: factors.append("Normal conditions")
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
    forecast = []
    today = datetime.today()

    for i in range(7):
        date = today + timedelta(days=i)
        month = date.month

        if month in [6, 7, 8]:
            temp, humidity, wind = 37.0, 62.0, 3.8
        elif month in [12, 1, 2]:
            temp, humidity, wind = 9.0, 72.0, 2.5
        else:
            temp, humidity, wind = 26.0, 55.0, 3.2

        season = (0 if month in [12,1,2] else
                  1 if month in [3,4,5] else
                  2 if month in [6,7,8] else 3)

        features = np.array([[temp, humidity, wind,
                               date.weekday(), month, season]])

        demand = float(demand_model.predict(features)[0])
        outage_prob = float(
            outage_model.predict_proba(features)[0][1] * 100)
        risk = get_risk_level(outage_prob)

        forecast.append({
            "date":                date.strftime("%Y-%m-%d"),
            "day":                 date.strftime("%A"),
            "demand_kwh":          round(demand, 2),
            "outage_probability":  round(outage_prob, 1),
            "risk_level":          risk,
            "affected_zones":      get_zones(risk),
            "weather_factors":     get_weather_factors(temp, wind),
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
