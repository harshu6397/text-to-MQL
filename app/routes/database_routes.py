from fastapi import APIRouter, HTTPException, Query
from app.controllers.query_controller import query_controller
from typing import Dict, Any

router = APIRouter(prefix="/api/database", tags=["Database Operations"])


@router.get("/collections")
async def get_collections():
    """Get list of all collections with statistics"""
    try:
        result = await query_controller.get_collections()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/schema/{collection_name}")
async def get_collection_schema(collection_name: str):
    """Get schema information for a specific collection"""
    try:
        result = await query_controller.get_collection_schema(collection_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_collections(
    q: str = Query(..., description="Search term to look for across collections")
):
    """Search across all collections using text search"""
    try:
        result = await query_controller.search_collections(q)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/raw-query/{collection_name}")
async def execute_raw_query(collection_name: str, query: Dict[str, Any]):
    """Execute a raw MongoDB query on a specific collection"""
    try:
        result = await query_controller.execute_raw_query(collection_name, query)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def database_health():
    """Health check for database operations"""
    return {
        "status": "healthy",
        "service": "Database Operations",
        "description": "Direct database access and schema information"
    }
