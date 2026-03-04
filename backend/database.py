from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base
from config import settings
import logging

logger = logging.getLogger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Enable pgvector extension
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
            logger.info("[DB] pgvector extension enabled")
    except Exception as e:
        logger.warning(f"[DB] Could not enable pgvector: {e}")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("[DB] Database initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
