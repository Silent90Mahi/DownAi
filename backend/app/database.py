from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import ProgrammingError, IntegrityError
import os
import time
import logging
import threading

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ooumph.db")

if "postgresql" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={"connect_timeout": 30},
        isolation_level="AUTOCOMMIT"
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

_db_init_lock = threading.Lock()
_db_initialized = False

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables with thread-safe logic for multi-worker setup"""
    global _db_initialized
    
    if _db_initialized:
        logger.info("Database already initialized, skipping")
        return
    
    with _db_init_lock:
        if _db_initialized:
            logger.info("Database already initialized, skipping")
            return
        
        from . import models
        max_retries = 5
        
        for attempt in range(max_retries):
            try:
                Base.metadata.create_all(bind=engine, checkfirst=True)
                _db_initialized = True
                logger.info("Database tables initialized successfully")
                return
            except (ProgrammingError, IntegrityError) as e:
                if "already exists" in str(e).lower():
                    _db_initialized = True
                    logger.info(f"Tables already exist (attempt {attempt + 1})")
                    return
                elif attempt < max_retries - 1:
                    logger.warning(f"Database init attempt {attempt + 1} failed, retrying: {e}")
                    time.sleep(1)
                else:
                    logger.error(f"Database initialization failed after {max_retries} attempts: {e}")
                    raise
