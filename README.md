# Nexus ERP - AI Module

This module handles data collection, machine learning model training, and the REST API for the Nexus ERP system.

## 🛠️ Backend Implementation

- **Framework**: FastAPI
- **Database ORM**: SQLAlchemy
- **Data Science**: Pandas, NumPy, Scikit-learn, XGBoost
- **Data Collection**: Integration with weather APIs for real-time forecasting.

## 🚀 Quick Start

### Installation
```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Running the API
```bash
cd api
uvicorn main:app --reload
```

## 📂 Module Structure

- `api/`: FastAPI server and route definitions.
- `data/`: Scripts for weather collection and dataset generation.
- `models/`: ML model definitions and training logic.
- `requirements.txt`: Python package dependencies.
