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
    cat_list = []
    for cat in ["Generation", "Infrastructure", "Operational"]:
        cat_items = [i for i in items if i["category"] == cat]
        stats = {
            "name":     cat,
            "items":    len(cat_items),
            "total_items": len(cat_items),
            "ok":       sum(1 for x in cat_items if x["status"] == "OK"),
            "low":      sum(1 for x in cat_items if x["status"] == "Low"),
            "critical": sum(1 for x in cat_items if x["status"] == "Critical"),
            "OK":       sum(1 for x in cat_items if x["status"] == "OK"),
            "LOW":      sum(1 for x in cat_items if x["status"] == "Low"),
            "CRITICAL": sum(1 for x in cat_items if x["status"] == "Critical"),
        }
        cat_breakdown[cat] = stats
        cat_breakdown[cat.lower()] = stats
        cat_list.append(stats)
        if cat == "Operational":
            cat_breakdown["operation"] = stats

    inv_summary = {
        **inv_data["summary"],
        **cat_breakdown,
        "categories": cat_breakdown,
        "category_stats": cat_list
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
        "system_status": "Operational" if inv_summary["critical"] == 0 else "Action Required",
        # Accuracy metrics from screenshot
        "outage_accuracy": 89.8,
        "inventory_accuracy": 94.9,
    }
