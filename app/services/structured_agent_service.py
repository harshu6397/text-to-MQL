from langchain_mongodb.agent_toolkit import MongoDBDatabase, MongoDBDatabaseToolkit
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.checkpoint.mongodb import MongoDBSaver
from app.core.database import db_manager
from app.core.config import settings
from app.services.llm_service import llm_service
from app.helpers.result_helpers import is_empty_result, parse_results
from app.helpers.query_helpers import fix_query_syntax, regenerate_query
from app.helpers.collection_helpers import determine_target_collection, analyze_collections_for_query
from app.helpers.schema_helpers import prepare_schema_context, get_schema_for_collections
from app.helpers.workflow_helpers import (
    build_workflow_graph, extract_workflow_steps, create_initial_workflow_state, 
    create_workflow_config, check_workflow_success
)
from app.constants import (
    FORMAT_ANSWER_PROMPT,
    DEFAULT_TARGET_COLLECTION,
    MAX_RETRIES,
    SYSTEM_COLLECTIONS,
    MAX_RESULT_DISPLAY_LENGTH,
    RECURSION_LIMIT,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)
from typing import Dict, Any, List, TypedDict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class MessagesState(TypedDict):
    """State object for the structured workflow"""
    messages: List[Any] 
    user_query: str     
    collections: List[str] 
    schema_info: Dict[str, str] 
    mql_query: str      
    query_result: Any   
    formatted_answer: str 
    step_status: Dict[str, str] 
    error_info: Optional[str]   


class StructuredAgentService:
    def __init__(self):
        self.llm = None
        self.toolkit = None
        self.agent = None
        self.checkpointer = None
        self.tool_map = {}

    async def initialize(self):
        """Initialize the Structured workflow agent"""
        try:
            # Initialize LLM with Cohere using LLM service
            self.llm = llm_service.initialize_llm()

            # Initialize MongoDB database for LangChain
            db = MongoDBDatabase.from_connection_string(
                connection_string=settings.MONGODB_URI,
                database=settings.DATABASE_NAME
            )

            # Create toolkit
            self.toolkit = MongoDBDatabaseToolkit(db=db, llm=self.llm)
            tools = self.toolkit.get_tools()
            
            # Create a mapping of tool names to tool objects for easy access
            self.tool_map = {tool.name: tool for tool in tools}

            # Create checkpointer for conversation memory
            self.checkpointer = MongoDBSaver(
                client=db_manager.sync_client,
                db_name=settings.DATABASE_NAME
            )

            # Build structured workflow
            self._build_workflow()

            logger.info(SUCCESS_MESSAGES['STRUCTURED_AGENT_INITIALIZED'].format(tools=list(self.tool_map.keys())))

        except Exception as e:
            logger.error(ERROR_MESSAGES['STRUCTURED_AGENT_INIT_FAILED'].format(error=str(e)))
            raise

    def _build_workflow(self):
        """Build the structured workflow graph"""
        # Create workflow nodes
        workflow_nodes = {
            "list_collections": self._list_collections_node,
            "get_schema": self._get_schema_node,
            "generate_query": self._generate_query_node,
            "run_query": self._run_query_node,
            "format_answer": self._format_answer_node
        }
        
        # Build workflow using helper
        workflow = build_workflow_graph(workflow_nodes)
        
        # Compile the workflow with checkpointer
        self.agent = workflow.compile(checkpointer=self.checkpointer)

    def _list_collections_node(self, state: MessagesState) -> MessagesState:
        """
        Node 1: Discover available collections in the database
        This is the first step in our deterministic workflow.
        """
        logger.info("Step 1: Discovering database collections...")
        
        try:
            # Use the mongodb_list_collections tool
            list_tool = self.tool_map.get("mongodb_list_collections")
            if not list_tool:
                raise Exception(ERROR_MESSAGES['COLLECTIONS_TOOL_NOT_AVAILABLE'])
            
            result = list_tool.invoke({})
            logger.info(f"Raw result from list_collections tool: {result}")
            
            # Parse the result to extract collection names
            if isinstance(result, str):
                # Handle both comma-separated and newline-separated results
                if ',' in result and '\n' not in result.strip():
                    # Comma-separated format
                    collections = [
                        c.strip() for c in result.split(',') 
                        if c.strip() and not any(c.strip().startswith(sys_col) for sys_col in SYSTEM_COLLECTIONS)
                    ]
                else:
                    # Newline-separated format
                    collections = [
                        c.strip() for c in result.split('\n') 
                        if c.strip() and not any(c.startswith(sys_col) for sys_col in SYSTEM_COLLECTIONS)
                    ]
            else:
                collections = []
            
            # Update state
            state["collections"] = collections
            state["step_status"]["list_collections"] = "success"
            
            # Add to conversation history
            tool_message = ToolMessage(
                content=SUCCESS_MESSAGES['COLLECTIONS_DISCOVERED'].format(count=len(collections), collections=', '.join(collections)),
                tool_call_id="list_collections_call"
            )
            state["messages"].append(tool_message)
            
            logger.info(SUCCESS_MESSAGES['COLLECTIONS_DISCOVERED'].format(count=len(collections), collections=collections))
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['COLLECTIONS_LIST_FAILED'].format(error=str(e))
            logger.error(error_msg)
            
            state["collections"] = []
            state["step_status"]["list_collections"] = "failed"
            state["error_info"] = error_msg
            
            error_message = ToolMessage(
                content=error_msg,
                tool_call_id="list_collections_call"
            )
            state["messages"].append(error_message)
        
        return state

    def _get_schema_node(self, state: MessagesState) -> MessagesState:
        """
        Node 2: Get schema information for relevant collections
        This step analyzes the user query to determine which collections are relevant
        and retrieves their schemas for context.
        """
        logger.info("Step 2: Analyzing schemas for relevant collections...")
        
        try:
            # Use collection helper to analyze relevant collections
            relevant_collections = analyze_collections_for_query(state["user_query"], state["collections"])
            
            logger.info(SUCCESS_MESSAGES['RELEVANT_COLLECTIONS_IDENTIFIED'].format(collections=relevant_collections))
            
            # Get schema for relevant collections using helper
            schema_tool = self.tool_map.get("mongodb_schema")
            schema_info = get_schema_for_collections(schema_tool, relevant_collections)
            
            # Update state
            state["schema_info"] = schema_info
            state["step_status"]["get_schema"] = "success"
            
            # Add to conversation history
            schema_summary = SUCCESS_MESSAGES['SCHEMA_RETRIEVED'].format(count=len(schema_info), collections=', '.join(schema_info.keys()))
            tool_message = ToolMessage(
                content=schema_summary,
                tool_call_id="get_schema_call"
            )
            state["messages"].append(tool_message)
            
            logger.info(SUCCESS_MESSAGES['SCHEMA_RETRIEVED'].format(count=len(schema_info), collections=list(schema_info.keys())))
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['SCHEMA_RETRIEVAL_FAILED'].format(error=str(e))
            logger.error(error_msg)
            
            state["schema_info"] = {}
            state["step_status"]["get_schema"] = "failed"
            state["error_info"] = error_msg
            
            error_message = ToolMessage(
                content=error_msg,
                tool_call_id="get_schema_call"
            )
            state["messages"].append(error_message)
        
        return state

    def _generate_query_node(self, state: MessagesState) -> MessagesState:
        """
        Node 3: Generate MongoDB query based on natural language input
        This step uses Cohere API with comprehensive MQL generation prompt
        to convert the user's natural language query into a proper MongoDB aggregation pipeline.
        """
        logger.info("Step 3: Generating MongoDB aggregation pipeline using Cohere MQL generator...")
        
        try:
            # Prepare schema context for the MQL generator using helper
            schema_context = prepare_schema_context(state["schema_info"])
            
            # Determine target collection
            target_collection = determine_target_collection(state["user_query"], state["collections"], state["schema_info"])
            if not target_collection:
                target_collection = DEFAULT_TARGET_COLLECTION  # fallback
            
            logger.info(SUCCESS_MESSAGES['TARGET_COLLECTION_DETERMINED'].format(collection=target_collection))
            logger.info("Using enhanced MQL generator with schema context")
            
            # Generate MQL using the comprehensive prompt
            mql_query = llm_service.generate_mql_query(
                natural_language_query=state['user_query'],
                schema_context=schema_context,
                target_collection=target_collection
            )
            
            
            logger.info(SUCCESS_MESSAGES['MQL_QUERY_GENERATED'].format(query=mql_query))
            
            # Update state
            state["mql_query"] = mql_query
            state["step_status"]["generate_query"] = "success"
            
            # Add to conversation history
            ai_message = AIMessage(
                content=SUCCESS_MESSAGES['MQL_QUERY_GENERATED'].format(query=mql_query)
            )
            state["messages"].append(ai_message)
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['QUERY_GENERATION_FAILED'].format(error=str(e))
            logger.error(error_msg)
            
            # Fallback to simple count query
            target_collection = determine_target_collection(state["user_query"], state["collections"], state["schema_info"])
            if not target_collection:
                target_collection = DEFAULT_TARGET_COLLECTION
            
            fallback_query = f'db.{target_collection}.aggregate([{{"$count": "total"}}])'
            
            state["mql_query"] = fallback_query
            state["step_status"]["generate_query"] = "failed"
            state["error_info"] = error_msg
            
            error_message = AIMessage(content=f"{error_msg}. Using fallback query: {fallback_query}")
            state["messages"].append(error_message)
        
        return state

    def _run_query_node(self, state: MessagesState) -> MessagesState:
        """
        Node 4: Execute the generated MongoDB query
        This step runs the MongoDB command against the database and captures the results.
        """
        logger.info("Step 4: Executing MongoDB query...")
        
        try:
            if not state["mql_query"]:
                raise Exception(ERROR_MESSAGES['NO_QUERY_TO_EXECUTE'])
            
            logger.info(f"Executing command: {state['mql_query']}")
            
            # Use mongodb_query tool
            query_tool = self.tool_map.get("mongodb_query")
            
            if not query_tool:
                logger.error(f"mongodb_query tool not found. Available tools: {list(self.tool_map.keys())}")
                raise Exception(ERROR_MESSAGES['MONGODB_TOOL_NOT_FOUND'])
            
            logger.info(SUCCESS_MESSAGES['MONGODB_TOOL_READY'])
            
            # Execute the MongoDB command with retry logic
            max_retries = MAX_RETRIES
            retry_count = 0
            result = None
            
            while retry_count < max_retries and result is None:
                try:
                    current_query = state["mql_query"]
                    
                    # Fix common query issues
                    current_query = fix_query_syntax(current_query)
                    
                    logger.info(f"Attempt {retry_count + 1}: Executing query: {current_query}")
                    result = query_tool.invoke({"query": current_query})
                    logger.info(SUCCESS_MESSAGES['QUERY_EXECUTED_SUCCESS'].format(attempt=retry_count + 1))
                    
                    print("Raw query result:", result, type(result))  # Debug print
                    # Check if result is empty and this is the first attempt
                    if is_empty_result(result):
                        logger.warning("Query returned empty result on first attempt. Asking LLM to check and fix the query...")
                        
                        # Ask LLM to check and fix the query
                        fixed_query = self._ask_llm_to_fix_query(current_query, state)
                        if fixed_query and fixed_query != current_query:
                            logger.info(f"LLM provided fixed query: {fixed_query}")
                            # Try the fixed query
                            try:
                                result = query_tool.invoke({"query": fixed_query})
                                if not is_empty_result(result):
                                    logger.info("Fixed query returned results!")
                                    state["mql_query"] = fixed_query
                                    break
                                else:
                                    logger.warning("Fixed query also returned empty results")
                            except Exception as fix_error:
                                logger.warning(f"Fixed query failed: {fix_error}")
                        
                        # If still empty after fix attempt, continue with normal retry logic
                        result = None
                        retry_count += 1
                        continue
                    
                    # Update state with working query
                    state["mql_query"] = current_query
                    
                except Exception as e:
                    retry_count += 1
                    logger.warning(f"Attempt {retry_count} failed: {e}")
                    
                    if retry_count < max_retries:
                        # Try to generate a new query or fix the current one
                        if retry_count == 1:
                            # First retry: try to fix syntax issues
                            state["mql_query"] = fix_query_syntax(state["mql_query"])
                        elif retry_count == 2:
                            # Second retry: try to regenerate the query
                            state["mql_query"] = regenerate_query(state["user_query"], str(state.get("schema_info", {})), determine_target_collection(state["user_query"], state["collections"], state["schema_info"]))
                    else:
                        # Final fallback to simple count query
                        target_collection = determine_target_collection(state["user_query"], state["collections"], state["schema_info"])
                        if not target_collection:
                            target_collection = DEFAULT_TARGET_COLLECTION
                        
                        fallback_query = f'db.{target_collection}.aggregate([{{"$count": "total"}}])'
                        logger.info(f"Final fallback: {fallback_query}")
                        
                        try:
                            result = query_tool.invoke({"query": fallback_query})
                            state["mql_query"] = fallback_query
                            logger.info(SUCCESS_MESSAGES['FALLBACK_QUERY_SUCCESS'])
                        except Exception as fallback_error:
                            logger.error(ERROR_MESSAGES['FALLBACK_QUERY_FAILED'].format(error=fallback_error))
                            raise Exception(ERROR_MESSAGES['ALL_RETRIES_FAILED'].format(error=e))
            
            if result is None:
                raise Exception("Failed to execute query after all retry attempts")
            
            # Update state
            state["query_result"] = result
            state["step_status"]["run_query"] = "success"
            
            # Add to conversation history
            tool_message = ToolMessage(
                content=f"Query executed successfully. Result: {str(result)[:MAX_RESULT_DISPLAY_LENGTH]}{'...' if len(str(result)) > MAX_RESULT_DISPLAY_LENGTH else ''}",
                tool_call_id="run_query_call"
            )
            state["messages"].append(tool_message)
            
            logger.info(SUCCESS_MESSAGES['QUERY_EXECUTION_COMPLETE'].format(result=str(result)))
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['QUERY_EXECUTION_FAILED'].format(error=str(e))
            logger.error(error_msg)
            
            state["query_result"] = None
            state["step_status"]["run_query"] = "failed"
            state["error_info"] = error_msg
            
            error_message = ToolMessage(
                content=error_msg,
                tool_call_id="run_query_call"
            )
            state["messages"].append(error_message)
        
        return state

    def _format_answer_node(self, state: MessagesState) -> MessagesState:
        """
        Node 5: Format the query result into a human-readable answer
        This is the final step that converts raw MongoDB results into 
        a natural language response for the user.
        """
        logger.info("Step 5: Formatting final answer...")
        
        try:
            # Check if we have a query result
            if state["query_result"] is None:
                # Handle case where query execution failed
                if state["error_info"]:
                    formatted_answer = ERROR_MESSAGES['QUERY_PROCESSING_ERROR'].format(error=state['error_info'])
                else:
                    formatted_answer = ERROR_MESSAGES['UNABLE_TO_RETRIEVE_INFO']
            else:
                # Create a prompt to format the result naturally using constants
                format_prompt = FORMAT_ANSWER_PROMPT.format(
                    user_query=state["user_query"],
                    query_result=state["query_result"]
                )
                
                # Generate formatted response
                response = self.llm.invoke([HumanMessage(content=format_prompt)])
                formatted_answer = response.content.strip()
            
            # Update state
            state["formatted_answer"] = formatted_answer
            state["step_status"]["format_answer"] = "success"
            
            # Add final answer to conversation history
            final_message = AIMessage(content=formatted_answer)
            state["messages"].append(final_message)
            
            logger.info(SUCCESS_MESSAGES['ANSWER_FORMATTED'].format(answer=formatted_answer[:100]))
            
        except Exception as e:
            error_msg = ERROR_MESSAGES['ANSWER_FORMATTING_FAILED'].format(error=str(e))
            logger.error(error_msg)
            
            # Provide a fallback answer
            fallback_answer = ERROR_MESSAGES['FORMATTING_ERROR_FALLBACK'].format(result=state.get('query_result', 'No result available'))
            
            state["formatted_answer"] = fallback_answer
            state["step_status"]["format_answer"] = "failed"
            state["error_info"] = error_msg
            
            error_message = AIMessage(content=fallback_answer)
            state["messages"].append(error_message)
        
        return state
    
    def _ask_llm_to_fix_query(self, query: str, state: MessagesState) -> str:
        """
        Ask the LLM to check and fix a MongoDB query that returned empty results
        """
        # Prepare schema context using helper
        schema_context = prepare_schema_context(state["schema_info"])

        # Use LLM service to fix the query
        return llm_service.ask_llm_to_fix_query(query, state['user_query'], schema_context)

    async def query(self, query: str, thread_id: str = "default") -> Dict[str, Any]:
        """Process natural language query using structured workflow"""
        start_time = time.time()
        
        try:
            if not self.agent:
                await self.initialize()

            # Create initial state for the workflow using helper
            initial_state = create_initial_workflow_state(query)

            # Create config using helper
            config = create_workflow_config(thread_id, RECURSION_LIMIT)
            
            # Execute query with structured workflow
            final_state = self.agent.invoke(initial_state, config)

            execution_time = time.time() - start_time
            
            # Check if workflow completed successfully using helper
            workflow_success = check_workflow_success(final_state)
            
            return {
                "success": workflow_success,
                "query": query,
                "generated_mql": final_state.get("mql_query", ""),
                "results": parse_results(final_state.get("query_result", [])),
                "formatted_answer": final_state.get("formatted_answer", ""),
                "error": final_state.get("error_info"),
                "execution_time": execution_time,
                "workflow_steps": extract_workflow_steps(final_state),
                "collections_found": len(final_state.get("collections", [])),
                "schema_retrieved": len(final_state.get("schema_info", {}))
            }

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(ERROR_MESSAGES['WORKFLOW_EXECUTION_FAILED'].format(error=e))
            
            return {
                "success": False,
                "query": query,
                "generated_mql": None,
                "results": [],
                "formatted_answer": ERROR_MESSAGES['UNEXPECTED_ERROR'].format(error=str(e)),
                "error": str(e),
                "execution_time": execution_time,
                "workflow_steps": [],
                "collections_found": 0,
                "schema_retrieved": 0
            }


# Global instance
structured_agent_service = StructuredAgentService()
