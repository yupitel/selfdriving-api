"""
Database initialization module
Handles schema and table creation based on environment
"""

import logging
import os
from sqlalchemy import text, inspect
from sqlmodel import SQLModel

from app.cores.config import SCHEMA
from app.cores.database import engine

# Import all models to register them with SQLModel
from app.models.measurement import MeasurementModel
from app.models.datastream import DataStreamModel

logger = logging.getLogger(__name__)


def create_schema_if_not_exists():
    """Create schema if it doesn't exist"""
    try:
        with engine.connect() as connection:
            # Check if schema exists
            result = connection.execute(
                text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{SCHEMA}'")
            )
            
            if not result.fetchone():
                # Create schema
                connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}"))
                connection.commit()
                logger.info(f"Schema '{SCHEMA}' created successfully")
            else:
                logger.info(f"Schema '{SCHEMA}' already exists")
                
    except Exception as e:
        logger.error(f"Error creating schema: {e}")
        raise


def create_tables():
    """Create all tables defined in models"""
    try:
        # This will create all tables that don't exist
        SQLModel.metadata.create_all(engine)
        logger.info("Tables created successfully")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    try:
        SQLModel.metadata.drop_all(engine)
        logger.info("All tables dropped")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        raise


def check_tables_exist():
    """Check if tables exist in the database"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names(schema=SCHEMA)
    
    expected_tables = [
        "measurement",
        "datastream"
    ]
    
    missing_tables = [table for table in expected_tables if table not in existing_tables]
    
    if missing_tables:
        logger.warning(f"Missing tables: {missing_tables}")
        return False
    
    logger.info("All expected tables exist")
    return True


def initialize_database(mode: str = "test"):
    """
    Initialize database based on mode
    
    Args:
        mode: "test" - Create schema and tables (for testing)
              "development" - Create schema and tables if not exists
              "production" - Only check if schema and tables exist
    """
    logger.info(f"Initializing database in {mode} mode")
    
    if mode in ["test", "development"]:
        # Create schema if not exists
        create_schema_if_not_exists()
        
        if mode == "test":
            # For test mode, recreate tables
            logger.info("Test mode: Recreating tables")
            try:
                drop_all_tables()
            except Exception:
                pass  # Tables might not exist yet
            create_tables()
        else:
            # For development, create tables if not exists
            if not check_tables_exist():
                create_tables()
    
    elif mode == "production":
        # In production, just verify schema and tables exist
        logger.info("Production mode: Verifying database structure")
        
        # Check schema exists
        with engine.connect() as connection:
            result = connection.execute(
                text(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{SCHEMA}'")
            )
            if not result.fetchone():
                raise RuntimeError(f"Schema '{SCHEMA}' does not exist in production mode")
        
        # Check tables exist
        if not check_tables_exist():
            raise RuntimeError("Required tables do not exist in production mode")
        
        logger.info("Database structure verified successfully")
    
    else:
        raise ValueError(f"Invalid mode: {mode}. Must be 'test', 'development', or 'production'")


def get_db_mode():
    """Get database mode from environment variable"""
    return os.getenv("DB_MODE", "development").lower()