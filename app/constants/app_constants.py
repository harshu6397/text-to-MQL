"""
Application constants for the MongoDB MQL generation service
"""

# Default values
DEFAULT_TARGET_COLLECTION = "departments"
MAX_RETRIES = 3
MAX_COLLECTIONS_TO_ANALYZE = 3

# Collection keywords mapping for smart collection detection
COLLECTION_KEYWORDS = {
    'students': ['student', 'pupil', 'learner', 'enrollment'],
    'departments': ['department', 'dept', 'faculty', 'division'],
    'courses': ['course', 'class', 'subject', 'curriculum'],
    'teachers': ['teacher', 'instructor', 'professor', 'faculty'],
    'enrollments': ['enrollment', 'enroll', 'registration', 'signup']
}

# Common collections priority order
COMMON_COLLECTIONS = ['students', 'departments', 'courses']

# Date fields for sorting operations
DATE_FIELDS = ['established_year', 'created_at', 'date', 'year']

# Query type keywords
COUNT_KEYWORDS = ['count', 'how many', 'total', 'number']
FIRST_KEYWORDS = ['first', 'earliest', 'oldest']
LAST_KEYWORDS = ['last', 'latest', 'newest']

# Collection priority mapping for target collection determination
COLLECTION_PRIORITY = {
    'departments': ['department', 'dept', 'faculty', 'division'],
    'students': ['student', 'pupil', 'learner'],
    'courses': ['course', 'class', 'subject'],
    'teachers': ['teacher', 'instructor', 'professor'],
    'enrollments': ['enrollment', 'enroll', 'registration']
}

# System collections to filter out
SYSTEM_COLLECTIONS = ['checkpoint', 'system']

# Query limits and timeouts
QUERY_TIMEOUT = 30  # seconds
MAX_RESULT_DISPLAY_LENGTH = 200
MAX_TOKEN_LIMIT = 1000

# Model configuration
DEFAULT_TEMPERATURE = 0.1
RECURSION_LIMIT = 50
