from app.services.structured_agent_service import structured_agent_service
from app.services.database_service import database_service
from app.models.schemas import QueryRequest, QueryResponse
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class QueryController:
    def __init__(self):
        pass

    async def process_structured_query(self, request: QueryRequest, thread_id: str = None) -> QueryResponse:
        """Process query using Structured workflow agent"""
        try:
            if thread_id is None:
                thread_id = f"structured_{hash(request.query) % 10000}"
            
            result = await structured_agent_service.query(
                query=request.query,
                thread_id=thread_id
            )
            
            return QueryResponse(**result)
            
        except Exception as e:
            logger.error(f"Error in Structured query processing: {e}")
            return QueryResponse(
                success=False,
                query=request.query,
                results=[],
                error=str(e),
                execution_time=0.0
            )

    async def get_collections(self) -> Dict[str, Any]:
        """Get all collections"""
        try:
            collections = await database_service.get_collections()
            stats = await database_service.get_collection_stats()
            
            return {
                "success": True,
                "collections": collections,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting collections: {e}")
            return {
                "success": False,
                "error": str(e),
                "collections": [],
                "stats": {}
            }

    async def get_collection_schema(self, collection_name: str) -> Dict[str, Any]:
        """Get schema for specific collection"""
        try:
            schema = await database_service.get_collection_schema(collection_name)
            
            return {
                "success": True,
                "schema": schema
            }
            
        except Exception as e:
            logger.error(f"Error getting schema for {collection_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "schema": {}
            }

    async def search_collections(self, search_term: str) -> Dict[str, Any]:
        """Search across all collections"""
        try:
            results = await database_service.search_collections(search_term)
            
            return {
                "success": True,
                "search_term": search_term,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error searching collections: {e}")
            return {
                "success": False,
                "error": str(e),
                "search_term": search_term,
                "results": [],
                "count": 0
            }

    async def execute_raw_query(self, collection_name: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """Execute raw MongoDB query"""
        try:
            results = await database_service.execute_raw_query(collection_name, query)
            
            return {
                "success": True,
                "collection": collection_name,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error executing raw query: {e}")
            return {
                "success": False,
                "error": str(e),
                "collection": collection_name,
                "query": query,
                "results": [],
                "count": 0
            }


# Global instance
query_controller = QueryController()
