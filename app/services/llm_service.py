from langchain_cohere import ChatCohere
from app.core.config import settings
from app.constants import (
    get_mql_generation_prompt,
    get_query_check_prompt,
    get_query_analysis_prompt,
    DEFAULT_TEMPERATURE,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)
import logging
import cohere

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        self.llm = None
        self.cohere_client = None

    def _initialize_cohere(self):
        """Initialize Cohere client for MQL generation"""
        if not self.cohere_client:
            try:
                self.cohere_client = cohere.Client(settings.COHERE_API_KEY)
                logger.info(SUCCESS_MESSAGES['COHERE_CLIENT_INITIALIZED'])
            except Exception as e:
                logger.error(ERROR_MESSAGES['COHERE_CLIENT_INIT_FAILED'].format(error=str(e)))
                raise

    def initialize_llm(self):
        """Initialize the main LLM for general tasks"""
        try:
            self.llm = ChatCohere(
                model=settings.DEFAULT_LLM_MODEL,
                temperature=0,
                cohere_api_key=settings.COHERE_API_KEY,
                streaming=False
            )
            logger.info("LLM initialized successfully")
            return self.llm
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise

    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.1) -> str:
        """
        Generate text response using Cohere API for general purposes
        
        Args:
            prompt (str): The prompt to send to the LLM
            max_tokens (int): Maximum tokens for response
            temperature (float): Temperature for response generation
            
        Returns:
            str: Generated text response
        """
        try:
            # Initialize Cohere client if not already done
            self._initialize_cohere()
            
            # Generate response using Cohere
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            raw_response = response.generations[0].text.strip()
            logger.info(f"Generated text response: {raw_response}")
            
            return raw_response
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def generate_mql_query(self, natural_language_query: str, schema_context: str = "", target_collection: str = "collection") -> str:
        """
        Generate MongoDB Query Language (MQL) from natural language using Cohere API
        
        Args:
            natural_language_query (str): Natural language description of the query
            schema_context (str): Schema information for context
            target_collection (str): Target collection name
            
        Returns:
            str: Generated MQL query
        """
        
        # Get the MQL generation prompt from constants
        prompt = get_mql_generation_prompt(target_collection, schema_context, natural_language_query)

        try:
            # Use the generate_text method with appropriate parameters for MQL generation
            raw_response = self.generate_text(prompt, max_tokens=1000, temperature=DEFAULT_TEMPERATURE)

            print("Raw response from Cohere:", raw_response)  # Debug print
            
            return raw_response
            
        except Exception as e:
            logger.error(ERROR_MESSAGES['MQL_GENERATION_ERROR'].format(error=str(e)))
            # Fallback to a simple count query
            return f'db.{target_collection}.aggregate([{{"$count": "total"}}])'

    def should_check_query(self, query: str, user_query: str, schema_context: str) -> bool:
        """
        Determine if a generated MongoDB query needs to be checked for issues
        
        Args:
            query: The generated MongoDB query
            user_query: Original user query
            schema_context: Schema information
            
        Returns:
            bool: True if query needs checking, False otherwise
        """
        try:
            # Use the new query check prompt from constants
            check_prompt = get_query_check_prompt(query, user_query, schema_context)

            result = self.generate_text(check_prompt, max_tokens=10, temperature=0.1)
            return result.upper() == "YES"
            
        except Exception as e:
            logger.warning(f"Error checking if query needs validation: {e}")
            # Default to not checking if there's an error (fail safe)
            return False

    def analyze_query_issues(self, query: str, user_query: str, schema_context: str) -> dict:
        """
        Analyze a MongoDB query for potential issues and suggest fixes
        
        Args:
            query: The MongoDB query to analyze
            user_query: Original user query
            schema_context: Schema information
            
        Returns:
            dict: Analysis result with issues and potential fixes
        """
        try:
            # Use the new query analysis prompt from constants
            analysis_prompt = get_query_analysis_prompt(query, user_query, schema_context)

            result = self.generate_text(analysis_prompt, max_tokens=800, temperature=0.1)
            
            # Try to parse JSON response
            import json
            try:
                # Clean up the response to extract JSON
                if '```' in result:
                    start = result.find('{')
                    end = result.rfind('}') + 1
                    if start != -1 and end != 0:
                        result = result[start:end]
                
                analysis = json.loads(result)
                return analysis
                
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse JSON response: {result}")
                return {
                    "has_issues": False,
                    "issues": "Could not analyze query",
                    "fixed_query": None
                }
            
        except Exception as e:
            logger.warning(f"Error analyzing query issues: {e}")
            return {
                "has_issues": False,
                "issues": f"Analysis failed: {str(e)}",
                "fixed_query": None
            }


# Global instance
llm_service = LLMService()
