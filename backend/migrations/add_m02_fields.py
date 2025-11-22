import os
import sys
from sqlalchemy import create_engine, text, inspect

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database import DATABASE_URL

def migrate():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        inspector = inspect(engine)
        columns = [c['name'] for c in inspector.get_columns('articles')]
        
        # Add script column
        if 'script' not in columns:
            print("Adding 'script' column to articles table...")
            conn.execute(text("ALTER TABLE articles ADD COLUMN script TEXT"))
        else:
            print("'script' column already exists.")
            
        # Add voice_url column
        if 'voice_url' not in columns:
            print("Adding 'voice_url' column to articles table...")
            conn.execute(text("ALTER TABLE articles ADD COLUMN voice_url TEXT"))
        else:
            print("'voice_url' column already exists.")
            
        # Add broll_video_url column
        if 'broll_video_url' not in columns:
            print("Adding 'broll_video_url' column to articles table...")
            conn.execute(text("ALTER TABLE articles ADD COLUMN broll_video_url TEXT"))
        else:
            print("'broll_video_url' column already exists.")
            
        conn.commit()
        print("Migration complete.")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)
