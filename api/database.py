import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "nexus_erp")
DB_USER = os.getenv("DB_USER", "nexus_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nexus_pass")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS forecast_results (
                id SERIAL PRIMARY KEY,
                generated_at TIMESTAMP DEFAULT NOW(),
                forecast_date DATE,
                demand_kwh FLOAT,
                outage_probability FLOAT,
                risk_level VARCHAR(10),
                affected_zones TEXT,
                weather_factors TEXT,
                recommended_actions TEXT
            )
        """))
        conn.commit()
        print("Database tables ready.")

if __name__ == "__main__":
    init_db()
