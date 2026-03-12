import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

os.makedirs("data/processed", exist_ok=True)
np.random.seed(42)

days       = 2000
start_date = datetime(2021, 1, 1)
data       = []

for i in range(days):
    date    = start_date + timedelta(days=i)
    month   = date.month
    dow     = date.weekday()
    season  = (0 if month in [12,1,2] else
               1 if month in [3,4,5] else
               2 if month in [6,7,8] else 3)

    # Weather by season
    if month in [6,7,8]:
        temp     = np.random.normal(38, 2)
        humidity = np.random.normal(65, 8)
        wind     = np.random.normal(4.5, 1.5)
        rainfall = max(0, np.random.normal(5, 8))
    elif month in [12,1,2]:
        temp     = np.random.normal(10, 3)
        humidity = np.random.normal(72, 6)
        wind     = np.random.normal(3.0, 1.2)
        rainfall = max(0, np.random.normal(1, 2))
    else:
        temp     = np.random.normal(26, 4)
        humidity = np.random.normal(55, 8)
        wind     = np.random.normal(3.5, 1.3)
        rainfall = max(0, np.random.normal(2, 4))

    grid_load   = np.random.uniform(55, 98)
    maintenance = 1 if np.random.random() < 0.08 else 0
    prev_outage = 1 if (len(data) > 0 and
                        data[-1]["outage_label"] == 1 and
                        np.random.random() < 0.25) else 0

    demand_kwh  = (15000 + (temp - 20) * 220 +
                   (-900 if dow >= 5 else 0) +
                   np.random.normal(0, 400))

    # DETERMINISTIC outage rules — clear signal for model
    outage = 0
    if temp > 42:                           outage = 1
    elif temp > 38 and grid_load > 92:      outage = 1
    elif wind > 7 and rainfall > 15:        outage = 1
    elif rainfall > 20:                     outage = 1
    elif grid_load > 96:                    outage = 1
    elif maintenance == 1 and grid_load>85: outage = 1
    elif prev_outage==1 and temp>35:        outage = 1
    else:
        # Small random chance for borderline cases
        risk = 0.0
        if temp > 35:      risk += 0.12
        if grid_load > 88: risk += 0.10
        if wind > 5:       risk += 0.08
        if rainfall > 8:   risk += 0.10
        if prev_outage==1: risk += 0.08
        outage = 1 if np.random.random() < risk else 0

    data.append({
        "date":          date.strftime("%Y-%m-%d"),
        "temperature":   round(temp, 1),
        "humidity":      round(humidity, 1),
        "wind_speed":    round(wind, 2),
        "rainfall":      round(rainfall, 2),
        "grid_load":     round(grid_load, 1),
        "demand_kwh":    round(demand_kwh, 2),
        "prev_outage":   prev_outage,
        "maintenance":   maintenance,
        "outage_label":  outage,
        "day_of_week":   dow,
        "month":         month,
        "season":        season,
    })

df = pd.DataFrame(data)
df.to_csv("data/processed/nexus_training_data.csv", index=False)
print(f"Generated {len(df)} rows")
print(f"Outage rate: {df['outage_label'].mean()*100:.1f}%")
print(df["outage_label"].value_counts())
