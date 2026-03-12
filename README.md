# Nexus ERP - AI-Driven Enterprise Resource Planning

Nexus ERP is a modern enterprise solution designed for the Pakistan electricity sector, featuring AI-powered 7-day outage predictions and inventory management.

## 🚀 Project Overview

This project integrates a robust AI module for forecasting and a database-backed backend to manage enterprise resources efficiently.

- **AI Forecasting**: Predicts electricity outages using weather and historical data.
- **Inventory Management**: AI-driven engine for optimizing inventory levels.
- **REST API**: Built with FastAPI for high performance and scalability.
- **Database**: PostgreSQL integration for reliable data storage.

---

## 📂 Project Structure

```text
nexus-erp/
├── ai-module/               # Core AI & Backend Logic
│   ├── api/                 # FastAPI Application
│   │   ├── routes/          # API Endpoints (Forecast, Inventory)
│   │   └── database.py      # SQLAlchemy Configuration
│   ├── data/                # Data Collection & Generation Scripts
│   ├── models/              # ML Models & Training Engines
│   ├── .env                 # Environment Variables
│   └── requirements.txt     # Python Dependencies
├── frontend/                # Frontend Application (Work in Progress)
├── docker-compose.yml       # Infrastructure (PostgreSQL)
└── README.md                # Project Documentation
```

---

## 🛠️ Setup Instructions

### 1. Database Setup
Ensure you have [Docker](https://www.docker.com/) installed. Start the PostgreSQL database using:

```bash
docker-compose up -d
```

### 2. AI Module Setup
Navigate to the `ai-module` directory and set up a virtual environment:

```bash
cd ai-module
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
Create a `.env` file in the `ai-module` directory (if not already present) with correctly configured database credentials:

```env
DATABASE_URL=postgresql://nexus_user:nexus_pass@localhost:5432/nexus_erp
```

### 4. Running the API
Start the FastAPI server:

```bash
cd api
uvicorn main:app --reload
```
The API documentation will be available at `http://localhost:8000/docs`.

---

## 📊 Core Components

### AI Forecasting & Data
- `collect_weather.py`: Fetches real-time weather data.
- `generate_sample.py`: Generates synthetic data for model training.
- `train.py`: Logic for training the outage prediction models.

### API Endpoints
- `GET /api/forecast`: Retrieve 7-day weather and outage predictions.
- `GET /api/inventory`: Access inventory optimization data.
- `GET /health`: Check service status.

---

## 📝 License
This project is part of a Final Year Project (FYP). All rights reserved.
