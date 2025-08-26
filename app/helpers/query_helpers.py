import logging
from app.constants import (
    DEFAULT_TARGET_COLLECTION,
    COUNT_KEYWORDS,
    FIRST_KEYWORDS,
    LAST_KEYWORDS,
    DATE_FIELDS
)

logger = logging.getLogger(__name__)


def fix_query_syntax(query: str) -> str:
    """
    Fix common syntax issues in MongoDB queries
    
    Args:
        query: MongoDB query string to fix
        
    Returns:
        str: Fixed query string
    """
    if not query:
        return query
        
    # Remove extra whitespace
    query = query.strip()
    
    # Fix common JSON formatting issues
    query = query.replace("'", '"')  # Replace single quotes with double quotes
    
    # Fix JSON boolean values that should be Python boolean values
    query = query.replace(': false', ': False')
    query = query.replace(': true', ': True')
    query = query.replace(': null', ': None')
    
    # Fix incomplete queries
    if query.startswith('db.') and query.count('[') > query.count(']'):
        # Try to close missing brackets
        missing_brackets = query.count('[') - query.count(']')
        query += ']' * missing_brackets
        
    # Fix incomplete parentheses
    if query.count('(') > query.count(')'):
        missing_parens = query.count('(') - query.count(')')
        query += ')' * missing_parens
        
    # Ensure proper aggregation syntax
    if 'db.' in query and 'aggregate(' in query and not query.endswith(')'):
        if not query.endswith(')]'):
            query += ')'
            
    return query


def regenerate_query(user_query: str, schema_context: str, target_collection: str) -> str:
    """
    Regenerate a simpler query when the original fails
    
    Args:
        user_query: Original user query
        schema_context: Schema information 
        target_collection: Target collection name
        
    Returns:
        str: Regenerated simple query
    """
    if not target_collection:
        target_collection = DEFAULT_TARGET_COLLECTION
        
    query_lower = user_query.lower()
    
    # Generate appropriate fallback based on query type using constants
    if any(word in query_lower for word in COUNT_KEYWORDS):
        return f'db.{target_collection}.aggregate([{{"$count": "total"}}])'
    elif any(word in query_lower for word in FIRST_KEYWORDS):
        # Try to determine the date field
        for field in DATE_FIELDS:
            if field in schema_context:
                return f'db.{target_collection}.aggregate([{{"$sort": {{"{field}": 1}}}}, {{"$limit": 1}}])'
        # Default sort by _id
        return f'db.{target_collection}.aggregate([{{"$sort": {{"_id": 1}}}}, {{"$limit": 1}}])'
    elif any(word in query_lower for word in LAST_KEYWORDS):
        # Similar logic for latest
        for field in DATE_FIELDS:
            if field in schema_context:
                return f'db.{target_collection}.aggregate([{{"$sort": {{"{field}": -1}}}}, {{"$limit": 1}}])'
        return f'db.{target_collection}.aggregate([{{"$sort": {{"_id": -1}}}}, {{"$limit": 1}}])'
    else:
        # Default to listing documents
        return f'db.{target_collection}.aggregate([{{"$limit": 5}}])'
