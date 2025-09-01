"""
Schema Analysis Helper Functions
"""
from typing import Dict, List, Any
from app.utils.logger import logger 


def prepare_schema_context(schema_info: Dict[str, str]) -> str:
    """
    Prepare schema context string for MQL generation with enhanced data type information
    
    Args:
        schema_info: Dictionary of collection names to schema information
        
    Returns:
        str: Formatted schema context string with data type guidance
    """
    if not schema_info:
        return "No schema information available"
    
    schema_parts = []
    for collection, schema in schema_info.items():
        # Enhance schema with data type guidance
        enhanced_schema = f"Collection '{collection}':\n{schema}"
        
        # Add data type mapping guidance from schema instructions
        try:
            from app.constants.schema_instructions import get_data_type_mapping_guide
            data_type_guide = get_data_type_mapping_guide()
            enhanced_schema += f"\n\n{data_type_guide}"
        except ImportError:
            # Fallback to basic guidance if schema instructions not available
            enhanced_schema += "\n\nDATA TYPE MAPPING GUIDANCE:"
            enhanced_schema += "\n- If field type is 'Number': Use integer values (e.g., level: 4, age: 22)"
            enhanced_schema += "\n- If field type is 'String': Use string values (e.g., name: \"John Doe\")"
            enhanced_schema += "\n- If field type is 'Date': Use ISODate format"
            enhanced_schema += "\n- If field type is 'ObjectId': Use ObjectId format"
        
        schema_parts.append(enhanced_schema)
    
    return "\n\n".join(schema_parts)


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
