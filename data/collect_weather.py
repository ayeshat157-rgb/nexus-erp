import httpx
import pandas as pd
import os
from datetime import datetime

# Open-Meteo coordinates for major Pakistan cities
CITIES = {
    "Islamabad": {"lat": 33.6844, "lon": 73.0479},
    "Lahore":    {"lat": 31.5204, "lon": 74.3587},
    "Karachi":   {"lat": 24.8607, "lon": 67.0011}
}

def get_weather():
    all_data = []

    # Use httpx client for synchronous requests
    with httpx.Client() as client:
        for city, coords in CITIES.items():
            print(f"Fetching weekly weather for {city} from Open-Meteo...")
            
            # Open-Meteo Forecast API (Fetching 7 days)
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude":  coords["lat"],
                "longitude": coords["lon"],
                "hourly":    "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
                "timezone":  "auto",
                "forecast_days": 7  # Changed to 7 days
            }

            response = client.get(url, params=params)

            if response.status_code != 200:
                print(f"Error for {city}: {response.text}")
                continue

            data = response.json()
            hourly = data["hourly"]

            # Parse hourly data into rows
            for i in range(len(hourly["time"])):
                all_data.append({
                    "date":        hourly["time"][i].replace("T", " "),
                    "city":        city,
                    "temperature": hourly["temperature_2m"][i],
                    "humidity":    hourly["relative_humidity_2m"][i],
                    "wind_speed":  hourly["wind_speed_10m"][i],
                    "rainfall":    hourly["precipitation"][i],
                    "description": "Open-Meteo Data"
                })

    df = pd.DataFrame(all_data)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv("data/raw/weather.csv", index=False)
    
    print(f"\n✅ Success! Saved {len(df)} rows to data/raw/weather.csv (Weekly data)")
    print(df.head())

if __name__ == "__main__":
    get_weather()