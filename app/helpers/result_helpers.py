from typing import Any, List, Dict
import json
import logging

logger = logging.getLogger(__name__)


def is_empty_result(result: Any) -> bool:
    """
    Check if the query result is empty
    
    Args:
        result: Query result to check
        
    Returns:
        bool: True if result is empty, False otherwise
    """
    if result is None:
        return True
    
    # Handle different result formats
    if isinstance(result, list):
        return len(result) == 0
    elif isinstance(result, dict):
        if 'result' in result:
            return len(result['result']) == 0 if isinstance(result['result'], list) else result['result'] is None
    elif isinstance(result, str):
        # Check for empty result strings
        result_lower = result.lower()
        return '[]' in result_lower or 'empty' in result_lower or result.strip() == ''
    
    return False


def parse_results(results: Any) -> List[Dict[str, Any]]:
    """
    Parse results into consistent format
    
    Args:
        results: Raw results from database query
        
    Returns:
        List[Dict[str, Any]]: Parsed results in consistent format
    """
    try:
        if isinstance(results, str):
            # Try to parse as JSON
            try:
                parsed = json.loads(results)
                if isinstance(parsed, list):
                    return parsed
                else:
                    return [{"result": parsed}]
            except:
                return [{"content": results}]
        elif isinstance(results, list):
            return results
        elif isinstance(results, dict):
            return [results]
        else:
            return [{"result": str(results)}]
    except Exception:
        return []
