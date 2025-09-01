from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from app.core.config import settings
from app.utils.logger import logger

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
        """Create necessary indexes dynamically for all collections"""
        try:
            # Get all collections dynamically
            collection_names = await self.database.list_collection_names()
            
            # Filter out system collections
            user_collections = [
                name for name in collection_names 
                if not name.startswith('system.') and name not in ['checkpoint']
            ]
            
            for collection_name in user_collections:
                collection = self.get_collection(collection_name)
                
                try:
                    # Create text index for full-text search
                    await collection.create_index([("$**", "text")])
                    logger.info(f"Created text index for collection: {collection_name}")
                except Exception as e:
                    logger.warning(f"Could not create text index for {collection_name}: {e}")
                
                try:
                    # Create vector index if embeddings exist
                    await collection.create_index([("vector_embedding", "2dsphere")])
                    logger.info(f"Created vector index for collection: {collection_name}")
                except Exception:
                    # Vector index creation might fail if field doesn't exist, which is fine
                    pass
            
            logger.info(f"Database indexes created successfully for {len(user_collections)} collections")
            
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")


# Global database manager instance
db_manager = DatabaseManager()
