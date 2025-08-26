"""
Collection Analysis Helper Functions - Fully Dynamic
"""
from typing import List, Dict, Any
import logging
import json
from app.constants import (
    MAX_COLLECTIONS_TO_ANALYZE,
    SYSTEM_COLLECTIONS
)
from app.constants.prompts import get_collection_identification_prompt
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


def sync_ai_identify_relevant_collections(user_query: str, collections: List[str]) -> List[str]:
    """
    Synchronous version of AI collection identification for use in sync contexts
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: AI-identified relevant collections
    """
    try:
        return ai_identify_relevant_collections(user_query, collections)
    except Exception as e:
        logger.warning(f"Sync AI collection identification failed: {e}")
        return get_fallback_collections(user_query, collections)


def analyze_collections_for_query_sync(user_query: str, collections: List[str]) -> List[str]:
    """
    Synchronous version of collection analysis pipeline for use in workflow nodes
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: Final list of relevant collections to analyze
    """
    try:
        # Step 1: Try AI-powered identification first
        relevant_collections = sync_ai_identify_relevant_collections(user_query, collections)
        
        # If AI didn't find any collections, fall back to simple method
        if not relevant_collections:
            logger.info("AI didn't find relevant collections, using fallback method")
            relevant_collections = get_fallback_collections(user_query, collections)
        
    except Exception as e:
        logger.warning(f"AI collection identification failed: {e}, using fallback method")
        # Step 1 fallback: Use simple identification
        relevant_collections = get_fallback_collections(user_query, collections)
    
    # Step 2: Apply limits
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    logger.info(f"Final relevant collections identified: {relevant_collections}")
    return relevant_collections


def get_fallback_collections(user_query: str, collections: List[str]) -> List[str]:
    """
    Simple fallback method to identify collections when AI fails
    Just looks for collection names mentioned in the query
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: Collections found in the query
    """
    query_lower = user_query.lower()
    relevant_collections = []
    
    # Check if any collection name is mentioned in the query
    for collection in collections:
        if collection.lower() in query_lower:
            relevant_collections.append(collection)
    
    # If no collections found, return all collections (let AI in later steps decide)
    if not relevant_collections:
        # Filter out system collections and return up to max limit
        non_system_collections = [c for c in collections if not any(c.startswith(sys) for sys in SYSTEM_COLLECTIONS)]
        relevant_collections = non_system_collections[:MAX_COLLECTIONS_TO_ANALYZE]
        logger.info(f"No specific collections mentioned, using first {len(relevant_collections)} non-system collections")
    
    return relevant_collections


def ai_identify_relevant_collections(user_query: str, collections: List[str]) -> List[str]:
    """
    Use AI to identify relevant collections for a user query
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: AI-identified relevant collections
    """
    try:
        llm_service = LLMService()
        
        # Get the AI prompt for collection identification
        prompt = get_collection_identification_prompt(user_query, collections)
        
        # Get AI response
        ai_response = llm_service.generate_text(prompt)
        logger.info(f"AI collection identification response: {ai_response}")
        
        # Parse the JSON response
        try:
            # Clean the response in case there's extra text
            response_clean = ai_response.strip()
            
            # Remove markdown code blocks if present
            if response_clean.startswith('```json'):
                response_clean = response_clean.replace('```json', '').replace('```', '').strip()
            elif response_clean.startswith('```'):
                response_clean = response_clean.replace('```', '').strip()
            
            # Find JSON array in the response
            start_idx = response_clean.find('[')
            end_idx = response_clean.rfind(']') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_part = response_clean[start_idx:end_idx]
                relevant_collections = json.loads(json_part)
            else:
                # Try parsing the entire response as JSON
                relevant_collections = json.loads(response_clean)
            
            # Ensure we have a list
            if not isinstance(relevant_collections, list):
                logger.warning(f"AI response is not a list: {relevant_collections}")
                return []
            
            # Validate that all returned collections exist
            valid_collections = [col for col in relevant_collections if col in collections]
            
            if valid_collections:
                logger.info(f"AI identified relevant collections: {valid_collections}")
                return valid_collections
            else:
                logger.warning("AI didn't identify any valid collections")
                return []
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}. Response: {ai_response}")
            
            # Try to extract collection names mentioned in the response
            mentioned_collections = []
            response_lower = ai_response.lower()
            for collection in collections:
                if collection.lower() in response_lower:
                    mentioned_collections.append(collection)
            
            if mentioned_collections:
                logger.info(f"Extracted collections from AI response: {mentioned_collections}")
                return mentioned_collections
            
            return []
            
    except Exception as e:
        logger.warning(f"AI collection identification failed: {e}")
        return []


def determine_target_collection_ai(user_query: str, collections: List[str], schema_info: Dict[str, str]) -> str:
    """
    Use AI to determine the primary target collection for the query
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        schema_info: Schema information for collections
        
    Returns:
        str: Target collection name
    """
    # If we have schema info, return the first one (most relevant from AI identification)
    if schema_info:
        return list(schema_info.keys())[0]
    
    # If we have collections, return the first one
    if collections:
        return collections[0]
    
    # This should rarely happen, but return None if no collections available
    return None


def apply_collection_limits(relevant_collections: List[str], user_query: str, collections: List[str]) -> List[str]:
    """
    Apply limits to collection analysis to avoid token limits
    
    Args:
        relevant_collections: List of relevant collections
        user_query: User's query for context
        collections: All available collections
        
    Returns:
        List[str]: Limited list of collections
    """
    # If no specific collections found, use fallback method
    if not relevant_collections:
        relevant_collections = get_fallback_collections(user_query, collections)
        logger.info("No specific collections detected, using fallback collections")
    
    # Limit to avoid token limits but be more generous for complex queries
    max_collections = MAX_COLLECTIONS_TO_ANALYZE
    query_lower = user_query.lower()
    
    # For complex relationship queries, allow more collections
    relationship_keywords = ['enroll', 'department', 'course', 'join', 'with', 'in', 'by', 'from']
    if any(keyword in query_lower for keyword in relationship_keywords):
        max_collections = min(5, len(collections))  # Allow up to 5 for complex queries
        
    if len(relevant_collections) > max_collections:
        relevant_collections = relevant_collections[:max_collections]
    
    return relevant_collections


def analyze_collections_for_query(user_query: str, collections: List[str]) -> List[str]:
    """
    Complete collection analysis pipeline for a user query using AI with fallback
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: Final list of relevant collections to analyze
    """
    try:
        # Step 1: Try AI-powered identification first
        relevant_collections = ai_identify_relevant_collections(user_query, collections)
        
        # If AI didn't find any collections, fall back to simple method
        if not relevant_collections:
            logger.info("AI didn't find relevant collections, using fallback method")
            relevant_collections = get_fallback_collections(user_query, collections)
        
    except Exception as e:
        logger.warning(f"AI collection identification failed: {e}, using fallback method")
        # Step 1 fallback: Use simple identification
        relevant_collections = get_fallback_collections(user_query, collections)
    
    # Step 2: Apply limits
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    logger.info(f"Final relevant collections identified: {relevant_collections}")
    return relevant_collections
