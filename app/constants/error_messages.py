"""
Error messages for the application
"""

ERROR_MESSAGES = {
    # Initialization errors
    'STRUCTURED_AGENT_INIT_FAILED': "Error initializing Structured agent: {error}",
    'COHERE_CLIENT_INIT_FAILED': "Error initializing Cohere client: {error}",
    'MONGODB_CONNECTION_FAILED': "Failed to connect to MongoDB: {error}",
    
    # Collection discovery errors
    'COLLECTIONS_LIST_FAILED': "Error listing collections: {error}",
    'COLLECTIONS_TOOL_NOT_AVAILABLE': "mongodb_list_collections tool not available",
    'NO_COLLECTIONS_FOUND': "No collections found in the database",
    
    # Schema retrieval errors
    'SCHEMA_RETRIEVAL_FAILED': "Error getting schema information: {error}",
    'SCHEMA_TOOL_NOT_AVAILABLE': "Schema tool not available or no relevant collections found",
    'SCHEMA_UNAVAILABLE': "Collection '{collection}' exists but detailed schema unavailable: {error}",
    
    # Query generation errors
    'QUERY_GENERATION_FAILED': "Error generating query with MQL generator: {error}",
    'MQL_GENERATION_ERROR': "Error generating MQL query with Cohere: {error}",
    'TARGET_COLLECTION_NOT_FOUND': "Unable to determine target collection",
    
    # Query execution errors
    'QUERY_EXECUTION_FAILED': "Error executing query: {error}",
    'MONGODB_TOOL_NOT_FOUND': "MongoDB query tool not available",
    'NO_QUERY_TO_EXECUTE': "No query to execute",
    'ALL_RETRIES_FAILED': "All query attempts failed. Last error: {error}",
    'FALLBACK_QUERY_FAILED': "Even fallback query failed: {error}",
    'QUERY_PARSING_FAILED': "Failed to parse aggregation pipeline: {error}",
    
    # Answer formatting errors
    'ANSWER_FORMATTING_FAILED': "Error formatting answer: {error}",
    'RESULT_PROCESSING_FAILED': "Error processing query results: {error}",
    
    # Workflow errors
    'WORKFLOW_EXECUTION_FAILED': "Error in Structured agent query: {error}",
    'STEP_EXECUTION_FAILED': "Step {step} execution failed: {error}",
    'STATE_UPDATE_FAILED': "Failed to update state: {error}",
    
    # Data validation errors
    'INVALID_QUERY_SYNTAX': "Invalid MongoDB query syntax: {error}",
    'MISSING_REQUIRED_PARAMETER': "Missing required parameter: {parameter}",
    'INVALID_COLLECTION_NAME': "Invalid collection name: {collection}",
    
    # API errors
    'API_REQUEST_FAILED': "API request failed: {error}",
    'TIMEOUT_ERROR': "Request timeout after {timeout} seconds",
    'RATE_LIMIT_EXCEEDED': "Rate limit exceeded, please try again later",
    
    # Generic errors
    'UNEXPECTED_ERROR': "An unexpected error occurred: {error}",
    'OPERATION_FAILED': "Operation failed: {error}",
    'PROCESSING_ERROR': "Error processing request: {error}",
    
    # Fallback messages
    'UNABLE_TO_RETRIEVE_INFO': "I apologize, but I was unable to retrieve the requested information.",
    'QUERY_PROCESSING_ERROR': "I apologize, but I encountered an error while processing your query: {error}",
    'FORMATTING_ERROR_FALLBACK': "I apologize, but I encountered an error while formatting the response. Raw result: {result}"
}
