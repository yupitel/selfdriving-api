import logging
import os
from typing import Generator

from app.cores.config import AWS_REGION, SQL_CLUSTER_ENDPOINT, SSL_CERT_PATH, SCHEMA
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
from sqlmodel import Session, SQLModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/selfdriving"
)

# Get database mode
DB_MODE = os.getenv("DB_MODE", "development").lower()

# Create engine with schema-aware configuration
engine = create_engine(
    DATABASE_URL,
    echo=(DB_MODE != "production"),  # Disable echo in production
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args={
        "options": f"-csearch_path={SCHEMA},public"
    } if SCHEMA else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)


def init_db():
    """Initialize database tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session
