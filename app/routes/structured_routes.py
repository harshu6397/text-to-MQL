from fastapi import APIRouter, HTTPException, Query
from app.controllers.query_controller import query_controller
from app.models.schemas import QueryRequest, QueryResponse
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/structured", tags=["Structured Agent"])


@router.post("/query", response_model=QueryResponse)
async def process_structured_query(
    request: QueryRequest,
    thread_id: Optional[str] = Query(None, description="Conversation thread ID")
):
    """
    Process natural language query using Structured workflow agent
    
    The Structured agent provides predictable, deterministic processing 
    with a fixed workflow sequence for consistent results.
    """
    try:
        result = await query_controller.process_structured_query(request, thread_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def structured_agent_health():
    """Health check for Structured agent"""
    return {
        "status": "healthy",
        "agent_type": "Structured",
        "description": "Deterministic workflow agent for predictable query processing"
    }
