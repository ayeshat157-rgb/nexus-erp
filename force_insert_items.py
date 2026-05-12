from sqlalchemy import text
from database import engine

def force_insert():
    items = [
        ('INV-009','Solar Inverters (5kW)','Generation','units',20,4,15,0.5,30,'11111111-0000-0000-0000-000000000005','OK'),
        ('INV-010','Wind Turbine Blades','Generation','units',10,2,8,0.1,5,'11111111-0000-0000-0000-000000000002','OK')
    ]
    with engine.connect() as conn:
        for item in items:
            print(f"Inserting {item[0]}...")
            conn.execute(text("""
                INSERT INTO inventory_items (item_id, name, category, unit, min_threshold, critical_threshold, current_stock, daily_consumption, reorder_quantity, vendor_id, status)
                VALUES (:id, :name, :cat, :unit, :min, :crit, :stock, :dc, :rq, :vid, :status)
                ON CONFLICT (item_id) DO UPDATE SET category = EXCLUDED.category
            """), {
                "id": item[0], "name": item[1], "cat": item[2], "unit": item[3],
                "min": item[4], "crit": item[5], "stock": item[6], "dc": item[7],
                "rq": item[8], "vid": item[9], "status": item[10]
            })
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    force_insert()
