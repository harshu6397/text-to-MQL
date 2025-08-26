"""
Constants package for the application
Contains all prompts, messages, and application constants
"""

from .prompts import *
from .app_constants import *
from .success_messages import *
from .error_messages import *

__all__ = [
    # Prompts
    'get_mql_generation_prompt',
    'get_collection_identification_prompt',
    'FORMAT_ANSWER_PROMPT',
    'get_query_fix_prompt',
    
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
