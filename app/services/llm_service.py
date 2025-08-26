from langchain_cohere import ChatCohere
from app.core.config import settings
from app.constants import (
    get_mql_generation_prompt,
    get_query_fix_prompt,
    DEFAULT_TARGET_COLLECTION,
    DEFAULT_TEMPERATURE,
    SUCCESS_MESSAGES,
    ERROR_MESSAGES
)
import logging
import re
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
        
        # Initialize Cohere client if not already done
        self._initialize_cohere()
        
        # Get the MQL generation prompt from constants
        prompt = get_mql_generation_prompt(target_collection, schema_context, natural_language_query)

        try:
            # Generate response using Cohere
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=prompt,
                max_tokens=1000,
                temperature=DEFAULT_TEMPERATURE
            )

            print("Response received from Cohere", response)  # Debug print
            
            raw_response = response.generations[0].text.strip()

            print("Raw response from Cohere:", raw_response)  # Debug print
            
            # Extract and clean the MongoDB command
            # mql_query = self._extract_and_clean_mql(raw_response, target_collection)
            
            return raw_response
            
        except Exception as e:
            logger.error(ERROR_MESSAGES['MQL_GENERATION_ERROR'].format(error=str(e)))
            # Fallback to a simple count query
            return f'db.{target_collection}.aggregate([{{"$count": "total"}}])'

    def _extract_and_clean_mql(self, raw_response: str, target_collection: str) -> str:
        """Extract and clean MongoDB command from response"""
        
        # Remove code blocks if present
        if '```' in raw_response:
            code_block_pattern = r'```(?:javascript|js|mongodb)?\s*([\s\S]*?)```'
            match = re.search(code_block_pattern, raw_response)
            if match:
                raw_response = match.group(1).strip()
        
        # Look for db.collection.aggregate() commands
        lines = raw_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('db.') and 'aggregate' in line:
                # Clean up the line
                line = line.replace("'", '"')  # Ensure double quotes
                return line
        
        # If no proper command found, try to extract JSON part and construct command
        if '[' in raw_response and ']' in raw_response:
            # Extract the aggregation pipeline
            start = raw_response.find('[')
            end = raw_response.rfind(']') + 1
            pipeline = raw_response[start:end]
            
            # Clean up JSON
            pipeline = pipeline.replace("'", '"')
            
            return f'db.{target_collection}.aggregate({pipeline})'
        
        # Final fallback
        return f'db.{target_collection}.aggregate([{{"$count": "total"}}])'

    def ask_llm_to_fix_query(self, query: str, user_query: str, schema_context: str) -> str:
        """
        Ask the LLM to check and fix a MongoDB query that returned empty results
        """
        try:
            # Use the query fix prompt from constants
            fix_prompt = get_query_fix_prompt(query, user_query, schema_context)

            # Use Cohere to fix the query
            self._initialize_cohere()
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=fix_prompt,
                max_tokens=500,
                temperature=0.1  # Low temperature for precise fixes
            )
            
            fixed_query = response.generations[0].text.strip()
            
            # Clean the response
            if '```' in fixed_query:
                code_block_pattern = r'```(?:javascript|js|mongodb)?\s*([\s\S]*?)```'
                match = re.search(code_block_pattern, fixed_query)
                if match:
                    fixed_query = match.group(1).strip()
            
            # Basic validation
            if fixed_query.startswith('db.') and 'aggregate' in fixed_query:
                return fixed_query
            else:
                logger.warning(f"LLM returned invalid query format: {fixed_query}")
                return query  # Return original if fix doesn't look valid
                
        except Exception as e:
            logger.warning(f"Error asking LLM to fix query: {e}")
            return query  # Return original query if fixing fails


# Global instance
llm_service = LLMService()
