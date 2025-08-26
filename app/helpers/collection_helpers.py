"""
Collection Analysis Helper Functions
"""
from typing import List, Dict, Any
import logging
import json
from app.constants import (
    COLLECTION_KEYWORDS,
    COMMON_COLLECTIONS,
    COLLECTION_PRIORITY,
    MAX_COLLECTIONS_TO_ANALYZE
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
    import asyncio
    import concurrent.futures
    
    def run_async():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                ai_identify_relevant_collections(user_query, collections)
            )
        finally:
            loop.close()
    
    try:
        # Check if we're in an async context
        try:
            asyncio.get_running_loop()
            # If we're here, there's already a running loop
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                return future.result(timeout=30)  # 30 second timeout
        except RuntimeError:
            # No event loop running, we can create one
            return asyncio.run(ai_identify_relevant_collections(user_query, collections))
    except Exception as e:
        logger.warning(f"Sync AI collection identification failed: {e}")
        return []


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
        
        # If AI didn't find any collections, fall back to manual method
        if not relevant_collections:
            logger.info("AI didn't find relevant collections, using manual method")
            relevant_collections = get_relevant_collections(user_query, collections)
        
    except Exception as e:
        logger.warning(f"AI collection identification failed: {e}, using manual method")
        # Step 1 fallback: Use manual identification
        relevant_collections = get_relevant_collections(user_query, collections)
    
    # Step 2: Add related collections based on relationships
    relevant_collections = add_related_collections(relevant_collections, collections, user_query)
    
    # Step 3: Apply limits and fallbacks
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    logger.info(f"Final relevant collections identified: {relevant_collections}")
    return relevant_collections


async def ai_identify_relevant_collections(user_query: str, collections: List[str]) -> List[str]:
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
        ai_response = await llm_service.generate_text(prompt)
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


def determine_target_collection(user_query: str, collections: List[str], schema_info: Dict[str, str]) -> str:
    """
    Helper function to determine which collection to query based on the user's question
    and available schema information.
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        schema_info: Schema information for collections
        
    Returns:
        str: Target collection name or None if not found
    """
    query_lower = user_query.lower()
    
    # Check for keyword matches using constants
    for collection, keywords in COLLECTION_PRIORITY.items():
        if collection in collections and any(keyword in query_lower for keyword in keywords):
            return collection
    
    # Return the first available collection from schema info
    if schema_info:
        collection = list(schema_info.keys())[0]
        return collection
    
    # Fallback to first available collection
    if collections:
        collection = collections[0]
        return collection
    
    return None


def get_relevant_collections(user_query: str, collections: List[str]) -> List[str]:
    """
    Determine relevant collections based on user query
    
    Args:
        user_query: User's natural language query
        collections: List of available collections
        
    Returns:
        List[str]: List of relevant collection names
    """
    query_lower = user_query.lower()
    relevant_collections = []
    
    # Find relevant collections using constants - be more inclusive
    for collection in collections:
        is_relevant = False
        
        # Check if collection name appears in query
        if collection.lower() in query_lower:
            is_relevant = True
        
        # Check keywords for this collection
        if collection in COLLECTION_KEYWORDS:
            keywords = COLLECTION_KEYWORDS[collection]
            if any(keyword in query_lower for keyword in keywords):
                is_relevant = True
        
        if is_relevant and collection not in relevant_collections:
            relevant_collections.append(collection)
    
    return relevant_collections


def add_related_collections(relevant_collections: List[str], collections: List[str], user_query: str) -> List[str]:
    """
    Add related collections based on relationships and query context
    
    Args:
        relevant_collections: Current list of relevant collections
        collections: All available collections
        user_query: User's query for context
        
    Returns:
        List[str]: Updated list with related collections added
    """
    query_lower = user_query.lower()
    updated_collections = relevant_collections.copy()
    
    # For queries involving relationships, ensure we have all related collections
    # If we have enrollments, we likely need students and courses too
    if 'enrollments' in relevant_collections:
        for related_collection in ['students', 'courses']:
            if related_collection in collections and related_collection not in updated_collections:
                updated_collections.append(related_collection)
                logger.info(f"Added {related_collection} collection due to enrollment relationship")
    
    # If we have students and mention departments, include departments
    if 'students' in relevant_collections and ('department' in query_lower or 'dept' in query_lower):
        if 'departments' in collections and 'departments' not in updated_collections:
            updated_collections.append('departments')
            logger.info("Added departments collection due to student-department relationship")
    
    # If we have courses and mention departments, include departments
    if 'courses' in relevant_collections and ('department' in query_lower or 'dept' in query_lower):
        if 'departments' in collections and 'departments' not in updated_collections:
            updated_collections.append('departments')
            logger.info("Added departments collection due to course-department relationship")
    
    # If we have teachers and mention departments, include departments
    if 'teachers' in relevant_collections and ('department' in query_lower or 'dept' in query_lower):
        if 'departments' in collections and 'departments' not in updated_collections:
            updated_collections.append('departments')
            logger.info("Added departments collection due to teacher-department relationship")
    
    return updated_collections


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
    query_lower = user_query.lower()
    
    # If no specific collections found, use common ones
    if not relevant_collections:
        relevant_collections = [c for c in COMMON_COLLECTIONS if c in collections]
        logger.info("No specific collections detected, using common collections")
    
    # Limit to avoid token limits but be more generous for complex queries
    max_collections = MAX_COLLECTIONS_TO_ANALYZE
    if len(relevant_collections) > max_collections:
        # For relationship queries, allow more collections
        if any(keyword in query_lower for keyword in ['enroll', 'department', 'course']):
            max_collections = min(5, len(collections))  # Allow up to 5 for complex queries
        relevant_collections = relevant_collections[:max_collections]
    
    return relevant_collections


async def analyze_collections_for_query(user_query: str, collections: List[str]) -> List[str]:
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
        relevant_collections = await ai_identify_relevant_collections(user_query, collections)
        
        # If AI didn't find any collections, fall back to manual method
        if not relevant_collections:
            logger.info("AI didn't find relevant collections, using manual method")
            relevant_collections = get_relevant_collections(user_query, collections)
        
    except Exception as e:
        logger.warning(f"AI collection identification failed: {e}, using manual method")
        # Step 1 fallback: Use manual identification
        relevant_collections = get_relevant_collections(user_query, collections)
    
    # Step 2: Add related collections based on relationships (keep this as backup logic)
    relevant_collections = add_related_collections(relevant_collections, collections, user_query)
    
    # Step 3: Apply limits and fallbacks
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    logger.info(f"Final relevant collections identified: {relevant_collections}")
    return relevant_collections
