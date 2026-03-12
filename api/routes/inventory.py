from fastapi import APIRouter
import json, os, uuid, sys
from datetime import datetime, timedelta

sys.path.insert(0, "D:/fyp/nexus-erp/ai-module")
from models.inventory_engine import (
    get_inventory_overview,
    get_current_orders,
    get_past_orders,
    check_and_generate_orders,
    load_orders,
    save_orders
)

router = APIRouter()

@router.get("/inventory/overview")
def inventory_overview():
    items = get_inventory_overview()
    summary = {
        "total_items": len(items),
        "ok":          sum(1 for i in items if i["status"] == "OK"),
        "low":         sum(1 for i in items if i["status"] == "Low"),
        "critical":    sum(1 for i in items if i["status"] == "Critical"),
    }
    return {
        "summary":   summary,
        "items":     items,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/inventory/orders/current")
def current_orders():
    orders = get_current_orders()
    return {"count": len(orders), "orders": orders}

@router.get("/inventory/orders/history")
def past_orders():
    orders = get_past_orders()
    return {"count": len(orders), "orders": orders}

@router.post("/inventory/check")
def run_inventory_check():
    new_orders = check_and_generate_orders()
    return {
        "message":    f"{len(new_orders)} new orders generated",
        "new_orders": new_orders,
        "timestamp":  datetime.now().isoformat()
    }

@router.post("/inventory/reorder/{item_id}")
def manual_reorder(item_id: str, quantity: int = 100):
    orders = load_orders()
    order = {
        "order_id":        f"ORD-{uuid.uuid4().hex[:6].upper()}",
        "item_id":         item_id,
        "item_name":       item_id,
        "quantity":        quantity,
        "trigger_type":    "Manual",
        "stage":           "Pending Verification",
        "contract_status": "Pending",
        "created_at":      datetime.now().isoformat(),
        "expected_delivery": (
            datetime.now() + timedelta(days=14)
        ).strftime("%Y-%m-%d"),
    }
    orders.append(order)
    save_orders(orders)
    return {"message": "Manual reorder placed", "order": order}
