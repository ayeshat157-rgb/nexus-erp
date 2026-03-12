import pandas as pd
import json, os
from datetime import datetime, timedelta
import uuid

DATA_PATH = "D:/fyp/nexus-erp/ai-module/data/inventory/inventory_items.json"
ORDERS_PATH = "D:/fyp/nexus-erp/ai-module/data/inventory/current_orders.json"

def load_inventory():
    with open(DATA_PATH) as f:
        return json.load(f)

def save_orders(orders):
    with open(ORDERS_PATH, "w") as f:
        json.dump(orders, f, indent=2)

def load_orders():
    if not os.path.exists(ORDERS_PATH):
        return []
    with open(ORDERS_PATH) as f:
        return json.load(f)

def get_status(current, minimum):
    critical_threshold = minimum * 0.20
    if current <= critical_threshold: return "Critical"
    elif current < minimum:           return "Low"
    else:                             return "OK"

def check_and_generate_orders():
    inventory = load_inventory()
    orders    = load_orders()
    existing  = {o["item_id"] for o in orders
                 if o["stage"] != "Delivered"}
    new_orders = []

    for item in inventory:
        status = get_status(
            item["current_stock"],
            item["min_threshold"])

        if item["item_id"] in existing:
            continue

        if status in ["Low", "Critical"]:
            trigger = "VEMA-Triggered" if status == "Critical" \
                      else "Auto-Generated"
            order = {
                "order_id":       f"ORD-{uuid.uuid4().hex[:6].upper()}",
                "item_id":        item["item_id"],
                "item_name":      item["name"],
                "quantity":       item["reorder_quantity"],
                "unit":           item["unit"],
                "vendor":         item["vendor"],
                "vendor_email":   item["vendor_email"],
                "trigger_type":   trigger,
                "stage":          "Pending Verification",
                "contract_status":"Pending",
                "created_at":     datetime.now().isoformat(),
                "expected_delivery": (
                    datetime.now() + timedelta(days=14)
                ).strftime("%Y-%m-%d"),
            }
            new_orders.append(order)
            print(f"[{trigger}] Order created for "
                  f"{item['name']} — Qty: {item['reorder_quantity']}")

    all_orders = orders + new_orders
    save_orders(all_orders)
    return new_orders

def get_inventory_overview():
    inventory = load_inventory()
    result = []
    for item in inventory:
        status = get_status(
            item["current_stock"],
            item["min_threshold"])
        result.append({
            **item,
            "status":       status,
            "last_updated": datetime.now().isoformat(),
        })
    return result

def get_current_orders():
    orders = load_orders()
    return [o for o in orders if o["stage"] != "Delivered"]

def get_past_orders():
    orders = load_orders()
    return [o for o in orders if o["stage"] == "Delivered"]

if __name__ == "__main__":
    print("Running inventory check...")
    new_orders = check_and_generate_orders()
    print(f"\nGenerated {len(new_orders)} new orders")
    print("\nCurrent Orders:")
    for o in get_current_orders():
        print(f"  {o['order_id']} | {o['item_name']:35} | "
              f"{o['stage']:25} | {o['trigger_type']}")
