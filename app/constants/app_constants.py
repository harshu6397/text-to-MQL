"""
Application constants for the MongoDB MQL generation service
"""

# Default values
MAX_RETRIES = 3
MAX_COLLECTIONS_TO_ANALYZE = 3

# Query type keywords (these are universal and not collection-specific)
COUNT_KEYWORDS = ['count', 'how many', 'total', 'number']
FIRST_KEYWORDS = ['first', 'earliest', 'oldest']
LAST_KEYWORDS = ['last', 'latest', 'newest']

# Common date field patterns (these are universal field name patterns)
DATE_FIELD_PATTERNS = ['date', 'created', 'established', 'year', 'time', 'updated']

# System collections to filter out (these are MongoDB system collections)
SYSTEM_COLLECTIONS = ['checkpoint', 'system']

# Query limits and timeouts
QUERY_TIMEOUT = 30  # seconds
MAX_RESULT_DISPLAY_LENGTH = 200
MAX_TOKEN_LIMIT = 1000

# Model configuration
DEFAULT_TEMPERATURE = 0.1
RECURSION_LIMIT = 50
