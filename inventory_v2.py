"""
NEXUS ERP — Inventory Router (Module 2 — DB-connected)
Replaces the JSON-file based inventory_engine with PostgreSQL.
"""
import uuid, json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from services.notification_service import notify_stock_critical, notify_stock_low

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


# ────────────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────────────

def _compute_status(stock: float, min_t: int, crit_t: int) -> str:
    if stock <= crit_t:  return "Critical"
    if stock < min_t:    return "Low"
    return "OK"


def _enrich_item(row: dict) -> dict:
    """Add computed fields to an inventory row."""
    s  = float(row.get("current_stock", 0))
    mn = int(row.get("min_threshold", 0))
    dc = float(row.get("daily_consumption", 1))
    cr = int(row.get("critical_threshold", 0))
    row["status"]               = _compute_status(s, mn, cr)
    row["days_until_reorder"]   = max(0, round((s - mn)  / dc)) if dc > 0 and s > mn else 0
    row["days_until_critical"]  = max(0, round((s - cr)  / dc)) if dc > 0 and s > cr else 0
    row["stock_pct"]            = round((s / mn) * 100, 1) if mn > 0 else 100
    return row


# ────────────────────────────────────────────────────────────────────────────
# GET /overview
# ────────────────────────────────────────────────────────────────────────────

@router.get("/overview")
def inventory_overview(db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT i.*, v.name AS vendor_name, v.email AS vendor_email
            FROM inventory_items i
            LEFT JOIN vendors v ON v.id = i.vendor_id
            ORDER BY i.item_id
        """)
    ).mappings().all()

    items = [_enrich_item(dict(r)) for r in rows]
    summary = {
        "total_items": len(items),
        "ok":       sum(1 for x in items if x["status"] == "OK"),
        "low":      sum(1 for x in items if x["status"] == "Low"),
        "critical": sum(1 for x in items if x["status"] == "Critical"),
    }
    return {"summary": summary, "items": items, "timestamp": datetime.utcnow().isoformat()}


# ────────────────────────────────────────────────────────────────────────────
# GET /item/{item_id}
# ────────────────────────────────────────────────────────────────────────────

@router.get("/item/{item_id}")
def get_item(item_id: str, db: Session = Depends(get_db)):
    row = db.execute(
        text("""
            SELECT i.*, v.name AS vendor_name, v.email AS vendor_email
            FROM inventory_items i
            LEFT JOIN vendors v ON v.id = i.vendor_id
            WHERE i.item_id = :id
        """),
        {"id": item_id},
    ).mappings().first()
    if not row:
        raise HTTPException(404, f"Item {item_id} not found")
    return _enrich_item(dict(row))


# ────────────────────────────────────────────────────────────────────────────
# POST /check — scan all items and auto-generate orders for Low/Critical
# ────────────────────────────────────────────────────────────────────────────

@router.post("/check")
def run_inventory_check(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Trigger inventory scan. For each Low/Critical item without an open order,
    create a procurement order automatically (calls procurement route logic directly).
    """
    from api.routes.procurement import create_order, CreateOrderRequest

    rows = db.execute(
        text("""
            SELECT i.*, v.name AS vendor_name, v.email AS vendor_email
            FROM inventory_items i
            LEFT JOIN vendors v ON v.id = i.vendor_id
        """)
    ).mappings().all()

    # Items already having open (non-Delivered) orders
    open_orders = db.execute(
        text("""
            SELECT item_id FROM procurement_orders
            WHERE stage NOT IN ('Delivered', 'Cancelled')
        """)
    ).scalars().all()
    open_set = set(open_orders)

    created = []
    for r in rows:
        item = _enrich_item(dict(r))
        if item["item_id"] in open_set:
            continue
        if item["status"] not in ("Low", "Critical"):
            continue

        trigger = "VEMA-Triggered" if item["status"] == "Critical" else "Auto-Generated"

        # Fire notification
        if item["status"] == "Critical":
            background_tasks.add_task(
                notify_stock_critical, db,
                item["name"], item["current_stock"], item["item_id"]
            )
        else:
            background_tasks.add_task(
                notify_stock_low, db,
                item["name"], item["current_stock"], item["item_id"]
            )

        result = create_order(
            CreateOrderRequest(
                item_id      = item["item_id"],
                quantity     = item["reorder_quantity"],
                trigger_type = trigger,
            ),
            db,
        )
        created.append(result)

    return {
        "message":    f"{len(created)} new orders generated",
        "new_orders": created,
        "timestamp":  datetime.utcnow().isoformat(),
    }


# ────────────────────────────────────────────────────────────────────────────
# PUT /item/{item_id}/stock — update stock level (e.g. after manual count)
# ────────────────────────────────────────────────────────────────────────────

class StockUpdateRequest(BaseModel):
    current_stock: float
    notes:         Optional[str] = None


@router.put("/item/{item_id}/stock")
def update_stock(item_id: str, req: StockUpdateRequest, db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT * FROM inventory_items WHERE item_id=:id"), {"id": item_id}
    ).mappings().first()
    if not row:
        raise HTTPException(404, f"Item {item_id} not found")

    item = dict(row)
    new_status = _compute_status(
        req.current_stock, item["min_threshold"], item["critical_threshold"]
    )
    db.execute(
        text("""
            UPDATE inventory_items
            SET current_stock=:s, status=:st, last_updated=NOW()
            WHERE item_id=:id
        """),
        {"s": req.current_stock, "st": new_status, "id": item_id},
    )
    db.commit()
    return {"item_id": item_id, "new_stock": req.current_stock, "status": new_status}
