import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "school_db")
    
    # Cohere API settings
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_BASE_URL: str = os.getenv("COHERE_BASE_URL", "https://api.cohere.com/v1")
    print("Cohere Key:", COHERE_API_KEY)
    
    # FastAPI settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Agent settings
    DEFAULT_LLM_MODEL: str = os.getenv("DEFAULT_LLM_MODEL", "command-r-plus")
    MAX_QUERY_RESULTS: int = int(os.getenv("MAX_QUERY_RESULTS", "100"))
    
    # Collections
    COLLECTIONS = {
        "departments": "departments",
        "teachers": "teachers",
        "courses": "courses", 
        "students": "students",
        "enrollments": "enrollments"
    }


settings = Settings()
