from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.core.database import db_manager
from app.routes import structured_routes, database_routes

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting up Text-to-MQL application...")
    
    try:
        await db_manager.connect_to_mongo()
        await db_manager.create_indexes()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        # Don't raise in production, just log the error
        logger.warning("Continuing without database connection...")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Text-to-MQL application...")
    try:
        await db_manager.close_mongo_connection()
    except:
        pass


# Create FastAPI app
app = FastAPI(
    title="Text-to-MQL API",
    description="""
    A comprehensive Text-to-MQL (MongoDB Query Language) API that converts natural language queries into MongoDB operations using AI agents.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ENV") == "development" and ["*"] or ["https://text-to-mql-frontend.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(structured_routes.router)
app.include_router(database_routes.router)


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Text-to-MQL API",
        "version": "1.0.0",
        "description": "Convert natural language to MongoDB queries using AI agents",
        "endpoints": {
            "structured_agent": "/api/structured/query", 
            "collections": "/api/database/collections",
            "search": "/api/database/search",
            "docs": "/docs"
        },
        "agent_types": {
            "structured": "Predictable, deterministic workflow"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        collections = await db_manager.database.list_collection_names()
        
        return {
            "status": "healthy",
            "database": "connected",
            "collections_count": len(collections),
            "available_services": [
                "Structured Agent", 
                "Database Operations"
            ]
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/demo-queries")
async def get_demo_queries():
    """Get example queries for testing"""
    return {
        "basic_queries": [
            "Find all students in Computer Science department",
            "List all teachers with their departments",
            "Show me courses offered this semester",
            "What departments do we have?",
            "Find students with GPA above 3.5"
        ],
        "analytical_queries": [
            "What's the average GPA of students in each department?",
            "Which courses have the highest enrollment?", 
            "List teachers with highest salaries",
            "Find students enrolled in Machine Learning courses",
            "Show departments with most students"
        ],
        "complex_queries": [
            "Find the top 3 students by GPA in Computer Science who are enrolled in at least 2 courses",
            "List teachers teaching more than 3 courses this semester",
            "What's the average salary of teachers in each department?",
            "Find courses with enrollment less than 10 students",
            "Show students who haven't enrolled in any courses"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
