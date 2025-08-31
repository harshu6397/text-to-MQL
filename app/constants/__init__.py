"""
Constants package for the application
Contains all prompts, messages, and application constants
"""

from .prompts import *
from .app_constants import *
from .success_messages import *
from .error_messages import *
from .schema_instructions import *

__all__ = [
    # Prompts
    'get_mql_generation_prompt',
    'get_collection_identification_prompt',
    'check_query_permissions',
    'FORMAT_ANSWER_PROMPT',
    'get_query_check_prompt',
    'get_query_analysis_prompt',
    
    # Schema Instructions
    'get_schema_aware_instructions',
    'get_data_type_mapping_guide',
    'get_relationship_mapping_guide',
    'check_for_write_operations',
    'get_active_records_filter',
    'enhance_query_with_active_filter',
    'SCHEMA_INTERPRETATION_INSTRUCTIONS',
    'MONGODB_SYNTAX_INSTRUCTIONS',
    'QUERY_OPTIMIZATION_INSTRUCTIONS',
    'DATA_VALIDATION_INSTRUCTIONS',
    
    # App Constants
    'MAX_RETRIES',
    'MAX_COLLECTIONS_TO_ANALYZE',
    'COUNT_KEYWORDS',
    'FIRST_KEYWORDS', 
    'LAST_KEYWORDS',
    'DATE_FIELD_PATTERNS',
    'SYSTEM_COLLECTIONS',
    'QUERY_TIMEOUT',
    'MAX_RESULT_DISPLAY_LENGTH',
    'MAX_TOKEN_LIMIT',
    'DEFAULT_TEMPERATURE',
    'RECURSION_LIMIT',
    
    # Success Messages
    'SUCCESS_MESSAGES',
    
    # Error Messages
    'ERROR_MESSAGES'
]
