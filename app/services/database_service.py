from app.core.database import db_manager
from app.core.config import settings
from typing import Dict, Any, List
from app.utils.logger import logger


class DatabaseService:
    def __init__(self):
        pass

    async def get_collections(self) -> List[str]:
        """Get list of all collections"""
        try:
            collections = await db_manager.database.list_collection_names()
            return collections
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return []

    async def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema information for a collection"""
        try:
            collection = db_manager.get_collection(collection_name)
            
            # Get sample documents to infer schema
            sample_docs = []
            async for doc in collection.find().limit(5):
                # Remove _id and vector_embedding for cleaner schema
                if '_id' in doc:
                    del doc['_id']
                if 'vector_embedding' in doc:
                    del doc['vector_embedding']
                sample_docs.append(doc)
            
            # Get document count
            count = await collection.count_documents({})
            
            # Get indexes
            indexes = await collection.list_indexes().to_list(length=None)
            index_info = [
                {
                    "name": idx.get("name", ""),
                    "keys": list(idx.get("key", {}).keys())
                }
                for idx in indexes
            ]
            
            return {
                "collection": collection_name,
                "document_count": count,
                "sample_documents": sample_docs,
                "indexes": index_info,
                "fields": self._extract_fields_from_samples(sample_docs)
            }
            
        except Exception as e:
            logger.error(f"Error getting schema for {collection_name}: {e}")
            return {}

    def _extract_fields_from_samples(self, sample_docs: List[Dict]) -> Dict[str, str]:
        """Extract field types from sample documents"""
        fields = {}
        
        for doc in sample_docs:
            for key, value in doc.items():
                if key not in fields:
                    fields[key] = type(value).__name__
                    
        return fields

    async def execute_raw_query(self, collection_name: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute a raw MongoDB query"""
        try:
            collection = db_manager.get_collection(collection_name)
            
            # Limit results for safety
            limit = min(query.get('limit', settings.MAX_QUERY_RESULTS), settings.MAX_QUERY_RESULTS)
            
            if 'aggregate' in query:
                # Handle aggregation pipeline
                pipeline = query['aggregate']
                if not any('$limit' in stage for stage in pipeline):
                    pipeline.append({'$limit': limit})
                
                results = []
                async for doc in collection.aggregate(pipeline):
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    if 'vector_embedding' in doc:
                        del doc['vector_embedding']
                    results.append(doc)
                
                return results
                
            else:
                # Handle find query
                filter_query = query.get('filter', {})
                projection = query.get('projection', {})
                sort = query.get('sort', {})
                
                # Add projection to exclude vector embeddings
                if not projection:
                    projection = {'vector_embedding': 0}
                else:
                    projection['vector_embedding'] = 0
                
                cursor = collection.find(filter_query, projection)
                
                if sort:
                    cursor = cursor.sort(list(sort.items()))
                
                cursor = cursor.limit(limit)
                
                results = []
                async for doc in cursor:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
                    results.append(doc)
                
                return results
                
        except Exception as e:
            logger.error(f"Error executing query on {collection_name}: {e}")
            raise

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics for all collections"""
        try:
            stats = {}
            collections = await self.get_collections()
            
            for collection_name in collections:
                if collection_name.startswith('system.'):
                    continue
                    
                collection = db_manager.get_collection(collection_name)
                count = await collection.count_documents({})
                
                stats[collection_name] = {
                    "document_count": count,
                    "collection_name": collection_name
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}

    async def search_collections(self, search_term: str) -> List[Dict[str, Any]]:
        """Search across all collections using text search"""
        try:
            results = []
            collections = await self.get_collections()
            
            for collection_name in collections:
                if collection_name.startswith('system.'):
                    continue
                    
                collection = db_manager.get_collection(collection_name)
                
                # Text search
                try:
                    async for doc in collection.find(
                        {"$text": {"$search": search_term}},
                        {"vector_embedding": 0}
                    ).limit(10):
                        if '_id' in doc:
                            doc['_id'] = str(doc['_id'])
                        doc['_collection'] = collection_name
                        results.append(doc)
                except Exception:
                    # If text search fails, try regex search on string fields
                    try:
                        async for doc in collection.find(
                            {"$or": [
                                {"name": {"$regex": search_term, "$options": "i"}},
                                {"description": {"$regex": search_term, "$options": "i"}},
                                {"course_name": {"$regex": search_term, "$options": "i"}},
                                {"specialization": {"$regex": search_term, "$options": "i"}}
                            ]},
                            {"vector_embedding": 0}
                        ).limit(5):
                            if '_id' in doc:
                                doc['_id'] = str(doc['_id'])
                            doc['_collection'] = collection_name
                            results.append(doc)
                    except Exception:
                        pass
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching collections: {e}")
            return []


# Global instance
database_service = DatabaseService()
