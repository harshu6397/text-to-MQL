"""
Success messages for the application
"""

SUCCESS_MESSAGES = {
    # Initialization messages
    'STRUCTURED_AGENT_INITIALIZED': "Structured agent initialized successfully with tools: {tools}",
    'COHERE_CLIENT_INITIALIZED': "Cohere client initialized successfully",
    
    # Collection discovery messages
    'COLLECTIONS_DISCOVERED': "Found {count} collections: {collections}",
    'COLLECTIONS_LISTED_SUCCESS': "Successfully discovered database collections",
    
    # Schema retrieval messages
    'SCHEMA_RETRIEVED': "Retrieved schema for {count} collections: {collections}",
    'SCHEMA_ANALYSIS_SUCCESS': "Successfully analyzed schemas for relevant collections",
    'RELEVANT_COLLECTIONS_IDENTIFIED': "Relevant collections identified: {collections}",
    
    # Query generation messages
    'MQL_QUERY_GENERATED': "Generated MongoDB command using enhanced MQL generator: {query}",
    'QUERY_GENERATION_SUCCESS': "Successfully generated MQL query",
    'TARGET_COLLECTION_DETERMINED': "Target collection for query generation: {collection}",
    
    # Query execution messages
    'QUERY_EXECUTED_SUCCESS': "Query executed successfully on attempt {attempt}",
    'QUERY_EXECUTION_COMPLETE': "Query executed successfully. Result: {result}",
    'FALLBACK_QUERY_SUCCESS': "Fallback query succeeded",
    
    # Answer formatting messages
    'ANSWER_FORMATTED': "Final answer generated: {answer}",
    'ANSWER_FORMATTING_SUCCESS': "Successfully formatted final answer",
    
    # Workflow completion messages
    'WORKFLOW_COMPLETED': "Workflow completed successfully",
    'STEP_COMPLETED': "Step {step} completed successfully",
    
    # Tool operation messages
    'TOOL_INVOKED_SUCCESS': "Tool {tool_name} invoked successfully",
    'MONGODB_TOOL_READY': "MongoDB query tool ready for execution",
    
    # Data processing messages
    'RESULTS_PARSED': "Results parsed successfully into consistent format",
    'STATE_UPDATED': "State updated successfully with {data_type} data"
}
