import pandas as pd
import numpy as np
from xgboost import XGBClassifier, XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, classification_report
import joblib, os

os.makedirs("models/saved", exist_ok=True)

df = pd.read_csv("data/processed/nexus_training_data.csv")
print(f"Loaded {len(df)} rows")

FEATURES = ["temperature", "humidity", "wind_speed", "day_of_week", "month", "season"]
X = df[FEATURES]

# Demand Model
print("\nTraining demand prediction model...")
y_demand = df["demand_kwh"]
X_train, X_test, y_train, y_test = train_test_split(X, y_demand, test_size=0.2, random_state=42)
demand_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.05, random_state=42)
demand_model.fit(X_train, y_train)
mae = mean_absolute_error(y_test, demand_model.predict(X_test))
print(f"Demand Model MAE: {mae:.0f} KWh")
joblib.dump(demand_model, "models/saved/demand_model.pkl")
print("Saved demand_model.pkl")

# Outage Model
print("\nTraining outage prediction model...")
y_outage = df["outage_label"]
X_train, X_test, y_train, y_test = train_test_split(X, y_outage, test_size=0.2, random_state=42)
outage_model = XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.05, scale_pos_weight=3, random_state=42)
outage_model.fit(X_train, y_train)
acc = accuracy_score(y_test, outage_model.predict(X_test))
print(f"Outage Model Accuracy: {acc*100:.1f}%")
print("\nClassification Report:")
print(classification_report(y_test, outage_model.predict(X_test)))
joblib.dump(outage_model, "models/saved/outage_model.pkl")
print("Saved outage_model.pkl")

print("\nBoth models trained and saved successfully!")
