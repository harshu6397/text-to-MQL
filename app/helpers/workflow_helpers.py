"""
Workflow Management Helper Functions
"""
from typing import Dict, List, Any
from langgraph.graph import StateGraph, START, END
import logging

logger = logging.getLogger(__name__)


def build_workflow_graph(workflow_nodes: Dict[str, Any]) -> StateGraph:
    """
    Build the structured workflow graph with given nodes
    
    Args:
        workflow_nodes: Dictionary of node names to node functions
        
    Returns:
        StateGraph: Configured workflow graph
    """
    from app.services.structured_agent_service import MessagesState
    
    # Create state graph
    workflow = StateGraph(MessagesState)

    # Add nodes
    for node_name, node_function in workflow_nodes.items():
        workflow.add_node(node_name, node_function)

    # Define the workflow edges with conditional routing
    workflow.add_edge(START, "list_collections")
    workflow.add_edge("list_collections", "get_schema")
    
    # Conditional edge from generate_query
    def decide_after_generate_query(state: MessagesState):
        """Decide whether query was denied or should proceed to need_checker"""
        if state.get("step_status", {}).get("generate_query") == "denied":
            return END
        else:
            return "need_checker"
    
    workflow.add_conditional_edges(
        "generate_query",
        decide_after_generate_query,
        {
            "need_checker": "need_checker",
            END: END
        }
    )
    
    workflow.add_edge("get_schema", "generate_query")
    
    # Conditional edge from need_checker
    def decide_next_step(state: MessagesState):
        """Decide whether to check query or run it directly"""
        if state.get("needs_check", False):
            return "check_query"
        else:
            return "run_query"
    
    workflow.add_conditional_edges(
        "need_checker",
        decide_next_step,
        {
            "check_query": "check_query",
            "run_query": "run_query"
        }
    )
    
    # Both check_query and run_query lead to format_answer
    workflow.add_edge("check_query", "run_query")
    workflow.add_edge("run_query", END)
    # workflow.add_edge("format_answer", END)

    return workflow


def extract_workflow_steps(final_state: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Extract workflow steps for debugging and monitoring
    
    Args:
        final_state: Final state from workflow execution
        
    Returns:
        List[Dict[str, str]]: List of workflow steps with their status
    """
    steps = [
        {"step": "List Collections", "status": final_state.get("step_status", {}).get("list_collections", "pending")},
        {"step": "Get Schema", "status": final_state.get("step_status", {}).get("get_schema", "pending")},
        {"step": "Generate Query", "status": final_state.get("step_status", {}).get("generate_query", "pending")},
        {"step": "Need Checker", "status": final_state.get("step_status", {}).get("need_checker", "pending")},
        {"step": "Check Query", "status": final_state.get("step_status", {}).get("check_query", "skipped" if not final_state.get("needs_check", False) else "pending")},
        {"step": "Run Query", "status": final_state.get("step_status", {}).get("run_query", "pending")},
        # {"step": "Format Answer", "status": final_state.get("step_status", {}).get("format_answer", "pending")}
    ]
    return steps


def check_workflow_success(final_state: Dict[str, Any]) -> bool:
    """
    Check if workflow completed successfully
    
    Args:
        final_state: Final state from workflow execution
        
    Returns:
        bool: True if all steps completed successfully
    """
    step_status = final_state.get("step_status", {})
    return all(
        status == "success" 
        for status in step_status.values()
    )


def create_initial_workflow_state(user_query: str) -> Dict[str, Any]:
    """
    Create initial state for workflow execution
    
    Args:
        user_query: User's natural language query
        
    Returns:
        Dict[str, Any]: Initial workflow state
    """
    from langchain_core.messages import HumanMessage
    
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "user_query": user_query,
        "collections": [],
        "schema_info": {},
        "mql_query": "",
        "query_result": None,
        "formatted_answer": "",
        "step_status": {},
        "error_info": None,
        "needs_check": False,
        "query_issues": None
    }
    
    return initial_state


def create_workflow_config(thread_id: str, recursion_limit: int) -> Dict[str, Any]:
    """
    Create configuration for workflow execution
    
    Args:
        thread_id: Thread ID for the workflow
        recursion_limit: Maximum recursion limit
        
    Returns:
        Dict[str, Any]: Workflow configuration
    """
    config = {
        "configurable": {"thread_id": thread_id},
        "recursion_limit": recursion_limit
    }
    
    return config
