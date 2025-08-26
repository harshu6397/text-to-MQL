"""
Schema Analysis Helper Functions
"""
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def prepare_schema_context(schema_info: Dict[str, str]) -> str:
    """
    Prepare schema context string for MQL generation
    
    Args:
        schema_info: Dictionary of collection names to schema information
        
    Returns:
        str: Formatted schema context string
    """
    if not schema_info:
        return "No schema information available"
    
    schema_context = "\n\n".join([
        f"Collection '{collection}':\n{schema}" 
        for collection, schema in schema_info.items()
    ])
    
    return schema_context


def get_schema_for_collections(schema_tool: Any, relevant_collections: List[str]) -> Dict[str, str]:
    """
    Retrieve schema information for relevant collections
    
    Args:
        schema_tool: MongoDB schema tool instance
        relevant_collections: List of collection names to get schema for
        
    Returns:
        Dict[str, str]: Dictionary mapping collection names to schema information
    """
    schema_info = {}
    
    if schema_tool and relevant_collections:
        try:
            # mongodb_schema expects collection_names as comma-separated string
            collections_string = ", ".join(relevant_collections)
            logger.info(f"Getting schema for collections: {collections_string}")
            
            schema_result = schema_tool.invoke({"collection_names": collections_string})
            
            # Store the schema for all relevant collections
            for collection in relevant_collections:
                schema_info[collection] = schema_result
            
            logger.info(f"Got schema for {len(relevant_collections)} collections")
                    
        except Exception as e:
            logger.warning(f"Could not get schema: {e}")
            # Provide basic schema info for relevant collections
            for collection in relevant_collections:
                schema_info[collection] = f"Collection '{collection}' exists but detailed schema unavailable: {e}"
    else:
        logger.warning("No schema tool available or no relevant collections found")
        # Provide basic schema info for relevant collections
        for collection in relevant_collections:
            schema_info[collection] = f"Collection '{collection}' exists but detailed schema unavailable"
    
    return schema_info
