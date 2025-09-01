import logging
from typing import List
from app.constants import (
    COUNT_KEYWORDS,
    FIRST_KEYWORDS,
    LAST_KEYWORDS,
    DATE_FIELD_PATTERNS
)

logger = logging.getLogger()


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
    query = query.replace('true', 'True')
    query = query.replace('false', 'False')
    query = query.replace('null', 'None')
    
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


def find_date_fields_in_schema(schema_context: str) -> List[str]:
    """
    Dynamically find date fields in the schema context
    
    Args:
        schema_context: Schema information string
        
    Returns:
        List[str]: List of potential date field names
    """
    date_fields = []
    
    # Look for common date field patterns
    for pattern in DATE_FIELD_PATTERNS:
        # Find field names that contain the pattern
        lines = schema_context.split('\n')
        for line in lines:
            if pattern in line.lower() and ':' in line:
                # Extract field name (everything before the colon)
                field_part = line.split(':')[0].strip()
                # Remove quotes and clean up
                field_name = field_part.replace('"', '').replace("'", '').strip()
                if field_name and field_name not in date_fields:
                    date_fields.append(field_name)
    
    return date_fields


def convert_python_to_mongodb_query(query: str) -> str:
    """
    Convert Python-formatted MongoDB query back to MongoDB console format
    
    Args:
        query: Python-formatted MongoDB query string
        
    Returns:
        str: MongoDB console formatted query string
    """
    if not query:
        return query
        
    # Remove extra whitespace
    mongo_query = query.strip()
    
    # Convert Python boolean values back to MongoDB JSON boolean values
    mongo_query = mongo_query.replace('True', 'true')
    mongo_query = mongo_query.replace('False', 'false')
    mongo_query = mongo_query.replace('None', 'null')
    
    # Ensure proper JSON formatting (double quotes instead of single quotes)
    # This should already be done, but ensure consistency
    mongo_query = mongo_query.replace("'", '"')
    
    return mongo_query


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
        # If no target collection provided, use a generic name
        target_collection = "collection"
        
    query_lower = user_query.lower()
    
    # Generate appropriate fallback based on query type using constants
    if any(word in query_lower for word in COUNT_KEYWORDS):
        return f'db.{target_collection}.aggregate([{{"$count": "total"}}])'
    elif any(word in query_lower for word in FIRST_KEYWORDS):
        # Try to find date fields dynamically
        date_fields = find_date_fields_in_schema(schema_context)
        if date_fields:
            return f'db.{target_collection}.aggregate([{{"$sort": {{"{date_fields[0]}": 1}}}}, {{"$limit": 1}}])'
        # Default sort by _id
        return f'db.{target_collection}.aggregate([{{"$sort": {{"_id": 1}}}}, {{"$limit": 1}}])'
    elif any(word in query_lower for word in LAST_KEYWORDS):
        # Similar logic for latest
        date_fields = find_date_fields_in_schema(schema_context)
        if date_fields:
            return f'db.{target_collection}.aggregate([{{"$sort": {{"{date_fields[0]}": -1}}}}, {{"$limit": 1}}])'
        return f'db.{target_collection}.aggregate([{{"$sort": {{"_id": -1}}}}, {{"$limit": 1}}])'
    else:
        # Default to listing documents
        return f'db.{target_collection}.aggregate([{{"$limit": 5}}])'
