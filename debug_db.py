from sqlalchemy import text
from database import engine

def debug():
    with engine.connect() as conn:
        print("--- All items ---")
        rows = conn.execute(text("SELECT item_id, category FROM inventory_items")).fetchall()
        for r in rows:
            print(r)
        
        print("\n--- Generation only ---")
        rows = conn.execute(text("SELECT item_id, category FROM inventory_items WHERE category = 'Generation'")).fetchall()
        for r in rows:
            print(r)

if __name__ == "__main__":
    debug()
