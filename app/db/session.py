import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from ..core.config import settings

logger = logging.getLogger(__name__)

class DataBase:
    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

db = DataBase()

async def connect_to_mongo() -> AsyncIOMotorDatabase:
    """Connect to MongoDB and return the database instance."""
    try:
        # Initialize the client and database
        db.client = AsyncIOMotorClient(settings.MONGODB_URL)
        db.database = db.client[settings.MONGODB_DB_NAME]
        
        # Test the connection
        await db.database.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        return db.database
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        # Ensure resources are cleaned up on failure
        if db.client:
            db.client.close()
            db.client = None
            db.database = None
        raise

async def close_mongo_connection() -> None:
    """Close MongoDB connection."""
    if db.client is not None:
        try:
            db.client.close()
            logger.info("Closed MongoDB connection")
        except Exception as e:
            logger.error(f"Error closing MongoDB connection: {e}")
        finally:
            db.client = None
            db.database = None

def get_database() -> AsyncIOMotorDatabase:
    """Get the database instance.
    
    Raises:
        RuntimeError: If the database is not initialized.
    """
    if db.database is None:
        raise RuntimeError("Database is not initialized. Call connect_to_mongo() first.")
    return db.database
