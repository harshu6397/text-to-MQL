"""
Collection Analysis Helper Functions - Enhanced with Database Knowledge
"""
from typing import List, Dict
import json
from app.constants import (
    MAX_COLLECTIONS_TO_ANALYZE,
    SYSTEM_COLLECTIONS
)
from app.constants.app_constants import (
    DATABASE_COLLECTION_MAP,
    EMPTY_COLLECTIONS,
    PRIORITY_COLLECTIONS
)
from app.constants.prompts import get_collection_identification_prompt
from app.services.llm_service import LLMService
from app.utils.logger import logger


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


def filter_collections_with_data(collections: List[str]) -> List[str]:
    """
    Filter out collections that have no data based on the EMPTY_COLLECTIONS set
    
    Args:
        collections: List of collection names to filter
        
    Returns:
        List[str]: Collections that have data (documents > 0)
    """
    filtered_collections = []
    for collection in collections:
        if collection not in EMPTY_COLLECTIONS:
            filtered_collections.append(collection)
        else:
            logger.info(f"Filtering out empty collection: {collection}")
    
    return filtered_collections


def get_collection_business_context(collection_name: str) -> Dict:
    """
    Get business context and relationship information for a collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dict: Business context including purpose, relationships, and query hints
    """
    return DATABASE_COLLECTION_MAP.get(collection_name, {
        "purpose": "Data storage collection",
        "business_logic": "Standard data collection",
        "query_hints": "General data queries",
        "relationships": [],
        "has_data": True
    })


def get_priority_collections_for_training_queries() -> List[str]:
    """
    Get the most important collections for training-related queries
    
    Returns:
        List[str]: Priority collections with high business value
    """
    return PRIORITY_COLLECTIONS


def get_collection_relationships(collection_name: str) -> List[str]:
    """
    Get related collections for a given collection based on business relationships
    
    Args:
        collection_name: Name of the primary collection
        
    Returns:
        List[str]: List of related collection names
    """
    collection_info = get_collection_business_context(collection_name)
    return collection_info.get("relationships", [])


def enhance_collection_selection_with_context(user_query: str, initial_collections: List[str]) -> List[str]:
    """
    Enhance collection selection by adding business context and relationships
    
    Args:
        user_query: User's natural language query
        initial_collections: Initially selected collections
        
    Returns:
        List[str]: Enhanced collection list with business context
    """
    enhanced_collections = initial_collections.copy()
    
    # Add related collections based on business logic
    for collection in initial_collections:
        context = get_collection_business_context(collection)
        related = context.get("relationships", [])
        
        # Add related collections that might be needed
        for related_collection in related:
            if related_collection.upper() not in enhanced_collections:
                enhanced_collections.append(related_collection.upper())
    
    # Filter out empty collections
    enhanced_collections = filter_collections_with_data(enhanced_collections)
    
    # Limit to reasonable number
    if len(enhanced_collections) > 4:
        # Prioritize based on business importance
        priority_collections = get_priority_collections_for_training_queries()
        enhanced_collections = [col for col in priority_collections if col in enhanced_collections][:4]
    
    return enhanced_collections


def get_collection_query_guidance(collection_name: str) -> str:
    """
    Get query guidance and best practices for a specific collection
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        str: Query guidance text
    """
    context = get_collection_business_context(collection_name)
    return context.get("query_hints", "Standard data queries")


def is_training_related_query(user_query: str) -> bool:
    """
    Determine if a query is related to training and employee development
    
    Args:
        user_query: User's natural language query
        
    Returns:
        bool: True if query is training-related
    """
    training_keywords = [
        "training", "course", "employee", "progress", "challenge", "conversation",
        "skill", "development", "learning", "assessment", "performance", "department",
        "organization", "user", "completion", "assignment", "analytics", "feedback"
    ]
    
    query_lower = user_query.lower()
    return any(keyword in query_lower for keyword in training_keywords)


def get_database_overview() -> Dict:
    """
    Get a high-level overview of the CallRevu training database
    
    Returns:
        Dict: Database overview with key statistics and information
    """
    return {
        "database_name": "callrevu-uat-lab",
        "environment": "Training Platform",
        "total_collections": 85,
        "total_documents": 1452982,
        "key_domains": [
            "Organizational Structure & Management",
            "Training Course Management & Content",
            "Employee Progress Tracking & Analytics", 
            "Skill Development & Assessment Challenges",
            "Conversation Practice & Role-play Training",
            "Performance Analysis & Feedback Systems"
        ],
        "primary_collections": get_priority_collections_for_training_queries(),
        "business_focus": "Employee training, skill development, and organizational learning management"
    }


def get_collection_schema_context(collection_name: str) -> str:
    """
    Get schema context for prompts to help AI understand collection structure
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        str: Schema context string for prompts
    """
    context = get_collection_business_context(collection_name)
    
    schema_context = f"""
Collection: {collection_name}
Purpose: {context.get('purpose', 'Data storage')}
Business Logic: {context.get('business_logic', 'Standard data operations')}
Key Fields: {', '.join(context.get('key_fields', []))}
Relationships: {', '.join(context.get('relationships', []))}
Query Guidance: {context.get('query_hints', 'Standard queries')}
"""
    
    return schema_context


def generate_collection_context_for_prompt(collections: List[str]) -> str:
    """
    Generate comprehensive context about collections for AI prompts
    
    Args:
        collections: List of collection names
        
    Returns:
        str: Formatted context for AI prompts
    """
    if not collections:
        return "No collections specified."
    
    context_parts = []
    context_parts.append("## Collection Context for CallRevu Training Platform\n")
    
    for collection in collections:
        collection_info = get_collection_business_context(collection)
        context_parts.append(f"### {collection}")
        context_parts.append(f"- **Purpose**: {collection_info.get('purpose', 'Data storage')}")
        context_parts.append(f"- **Business Logic**: {collection_info.get('business_logic', 'Standard operations')}")
        context_parts.append(f"- **Key Fields**: {', '.join(collection_info.get('key_fields', []))}")
        context_parts.append(f"- **Query Patterns**: {collection_info.get('query_hints', 'Standard queries')}")
        
        relationships = collection_info.get('relationships', [])
        if relationships:
            context_parts.append(f"- **Related Collections**: {', '.join(relationships)}")
        context_parts.append("")
    
    return "\n".join(context_parts)


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
    
    # Step 2: Apply limits and enhance with business context
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    # Step 3: Filter empty collections and enhance with business relationships
    relevant_collections = filter_collections_with_data(relevant_collections)
    relevant_collections = enhance_collection_selection_with_context(user_query, relevant_collections)
    
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
        if collection.lower() in query_lower and collection not in EMPTY_COLLECTIONS:
            if collection not in relevant_collections:
                relevant_collections.append(collection)
    
    # If no collections found, return priority collections (excluding empty ones)
    if not relevant_collections:
        # Filter out system collections and empty collections
        non_system_collections = [c for c in collections 
                                if not any(c.startswith(sys) for sys in SYSTEM_COLLECTIONS) 
                                and c not in EMPTY_COLLECTIONS]
        
        # Prioritize high-value collections
        priority_available = [c for c in get_priority_collections_for_training_queries() if c in non_system_collections]
        
        if priority_available:
            relevant_collections = priority_available[:MAX_COLLECTIONS_TO_ANALYZE]
        else:
            relevant_collections = non_system_collections[:MAX_COLLECTIONS_TO_ANALYZE]
            
        logger.info(f"No specific collections mentioned, using priority collections: {relevant_collections}")
    
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
            
            # Validate that all returned collections exist and have data
            # Create case-insensitive lookup for collections
            collections_lower = {col.lower(): col for col in collections}
            empty_collections_lower = {col.lower() for col in EMPTY_COLLECTIONS}
            
            valid_collections = []
            for col in relevant_collections:
                col_lower = col.lower()
                if col_lower in collections_lower and col_lower not in empty_collections_lower:
                    # Use the original case from the collections list
                    valid_collections.append(collections_lower[col_lower])
            
            if valid_collections:
                logger.info(f"AI identified relevant collections: {valid_collections}")
                return valid_collections
            else:
                logger.warning("AI didn't identify any valid collections with data")
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
    
    # Step 2: Apply limits and enhance with business context
    relevant_collections = apply_collection_limits(relevant_collections, user_query, collections)
    
    # Step 3: Filter empty collections and enhance with business relationships
    relevant_collections = filter_collections_with_data(relevant_collections)
    relevant_collections = enhance_collection_selection_with_context(user_query, relevant_collections)
    
    logger.info(f"Final relevant collections identified: {relevant_collections}")
    return relevant_collections
