from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import get_db
from api.routes.forecast import get_forecast
from inventory_v2 import inventory_overview

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("")
@router.get("/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # 1. Get Forecast Summary
    forecast_data = get_forecast()
    forecast_summary = {
        "avg_outage_prob": sum(d["outage_probability"] for d in forecast_data["forecast"]) / 7,
        "max_risk": max(d["outage_probability"] for d in forecast_data["forecast"]),
        "high_risk_days": sum(1 for d in forecast_data["forecast"] if d["risk_level"] == "High")
    }

    # 2. Get Inventory Summary
    inv_data = inventory_overview(None, db)
    inv_summary = inv_data["summary"]

    # 3. Recent Notifications
    notifications = db.execute(
        text("SELECT * FROM notifications ORDER BY created_at DESC LIMIT 5")
    ).mappings().all()

    # 4. Active Orders
    active_orders = db.execute(
        text("SELECT COUNT(*) FROM procurement_orders WHERE stage NOT IN ('Delivered', 'Cancelled')")
    ).scalar()

    return {
        "forecast": forecast_summary,
        "inventory": inv_summary,
        "active_orders": active_orders,
        "recent_notifications": [dict(n) for n in notifications],
        "system_status": "Operational" if inv_summary["critical"] == 0 else "Action Required"
    }
