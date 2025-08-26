from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.sync_client: MongoClient = None
        self.database = None
        self.sync_database = None

    async def connect_to_mongo(self):
        """Create database connection"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URI)
            self.database = self.client[settings.DATABASE_NAME]
            
            # Sync client for LangChain integration
            self.sync_client = MongoClient(settings.MONGODB_URI)
            self.sync_database = self.sync_client[settings.DATABASE_NAME]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {e}")
            raise

    async def close_mongo_connection(self):
        """Close database connection"""
        if self.client:
            self.client.close()
        if self.sync_client:
            self.sync_client.close()
        logger.info("Disconnected from MongoDB")

    def get_collection(self, collection_name: str):
        """Get async collection"""
        return self.database[collection_name]
    
    def get_sync_collection(self, collection_name: str):
        """Get sync collection for LangChain"""
        return self.sync_database[collection_name]

    async def create_indexes(self):
        """Create necessary indexes"""
        try:
            # Create text indexes for search
            collections_to_index = [
                "departments", "teachers", "courses", "students", "enrollments"
            ]
            
            for collection_name in collections_to_index:
                collection = self.get_collection(collection_name)
                
                # Create text index for full-text search
                await collection.create_index([("$**", "text")])
                
                # Create vector index if embeddings exist
                try:
                    await collection.create_index([("vector_embedding", "2dsphere")])
                except Exception:
                    pass  # Vector index creation might fail if field doesn't exist
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")


# Global database manager instance
db_manager = DatabaseManager()
