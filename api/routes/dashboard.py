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

    # 2. Get Inventory Summary with category breakdown
    inv_data = inventory_overview(None, db)
    items = inv_data["items"]
    
    cat_breakdown = {}
    # Provide both Title Case and lowercase/aliases for maximum frontend compatibility
    for cat in ["Generation", "Infrastructure", "Operational"]:
        cat_items = [i for i in items if i["category"] == cat]
        stats = {
            "ok":       sum(1 for x in cat_items if x["status"] == "OK"),
            "low":      sum(1 for x in cat_items if x["status"] == "Low"),
            "critical": sum(1 for x in cat_items if x["status"] == "Critical"),
            "total":    len(cat_items)
        }
        cat_breakdown[cat] = stats
        cat_breakdown[cat.lower()] = stats
        if cat == "Operational":
            cat_breakdown["operation"] = stats
            cat_breakdown["Operation"] = stats

    inv_summary = {
        **inv_data["summary"],
        "categories": cat_breakdown
    }

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
