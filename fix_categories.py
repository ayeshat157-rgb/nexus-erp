from sqlalchemy import text
from database import engine

def update_categories():
    mapping = {
        'Generation': ['INV-009', 'INV-010'],
        'Infrastructure': ['INV-001', 'INV-002', 'INV-003', 'INV-005', 'INV-006', 'INV-008'],
        'Operational': ['INV-004', 'INV-007']
    }
    with engine.connect() as conn:
        for cat, ids in mapping.items():
            print(f"Updating {cat}...")
            conn.execute(text("UPDATE inventory_items SET category = :cat WHERE item_id = ANY(:ids)"), {"cat": cat, "ids": ids})
        conn.commit()
        print("Done.")

if __name__ == "__main__":
    update_categories()
