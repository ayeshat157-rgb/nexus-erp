from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        print("Checking for 'category' column...")
        # Check if column exists
        res = conn.execute(text("""
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='inventory_items' AND column_name='category'
        """)).fetchone()
        
        if not res:
            print("Adding 'category' column...")
            conn.execute(text("ALTER TABLE inventory_items ADD COLUMN category VARCHAR(50) NOT NULL DEFAULT 'Operational'"))
            conn.commit()
            print("✅ Column added.")
        else:
            print("✅ Column already exists.")

if __name__ == "__main__":
    migrate()
