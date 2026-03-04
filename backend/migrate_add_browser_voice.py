"""Add browser_voice_name column to avatars table"""
import os
from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/voice_agent")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Add browser_voice_name column if it doesn't exist
    conn.execute(text("""
        ALTER TABLE avatars 
        ADD COLUMN IF NOT EXISTS browser_voice_name VARCHAR(100);
    """))
    conn.commit()
    print("✓ Migration completed: browser_voice_name column added")
