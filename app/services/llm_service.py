from langchain_cohere import ChatCohere
from app.core.config import settings
from app.constants import (
    get_mql_generation_prompt,
    get_query_fix_prompt,
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

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text response using Cohere API for general purposes
        
        Args:
            prompt (str): The prompt to send to the LLM
            
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
                max_tokens=500,
                temperature=0.1  # Low temperature for precise responses
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
                code_block_pattern = r'```(?:javascript|js|mongodb|python)?\s*([\s\S]*?)```'
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
            check_prompt = f"""
            Analyze the following MongoDB query and determine if it has ACTUAL ISSUES that need fixing.

            User Query: "{user_query}"
            Generated MongoDB Query: {query}
            Schema Context: {schema_context}

            ONLY respond "YES" if you detect ACTUAL PROBLEMS like:
            1. **SYNTAX ERRORS**: Invalid MongoDB syntax, wrong operators, malformed JSON
            2. **FIELD MISMATCHES**: Field names in query don't exist in schema
            3. **DATA TYPE ERRORS**: Using string values for Number fields or vice versa
            4. **CRITICAL LOGIC ERRORS**: Query logic completely wrong for the user's request
            5. **MONGODB RULE VIOLATIONS**: $lookup with $ prefixed localField/foreignField, etc.

            DO NOT flag for checking if:
            - Query is syntactically correct
            - Field names match schema
            - Data types are appropriate
            - Query logic makes sense for the user request
            - It's just a complex query with multiple stages

            Respond with "YES" ONLY if there are ACTUAL ISSUES that need fixing, otherwise "NO".
            Give only YES or NO as the answer.
            """

            self._initialize_cohere()
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=check_prompt,
                max_tokens=10,
                temperature=0.1
            )
            
            result = response.generations[0].text.strip().upper()
            return result == "YES"
            
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
            analysis_prompt = f"""
            Analyze the following MongoDB query for potential issues and suggest improvements:

            User Query: "{user_query}"
            MongoDB Query: {query}
            Schema Context: {schema_context}

            Check for:
            1. Syntax errors
            2. Field name mismatches with schema
            3. Incorrect operators usage
            4. Missing required stages
            5. Performance issues
            6. Logic errors
            7. **DATA TYPE MISMATCHES**:
               - If schema shows field as Number but query uses string value
               - If schema shows field as String but query uses numeric value
               - Convert natural language terms to appropriate data types based on schema
               - For level/grade fields: check if they should be numeric vs string based on schema

            IMPORTANT MONGODB SYNTAX RULES:
            - In $lookup stage, localField and foreignField should NOT have $ prefix
            - Use "localField": "_id" NOT "localField": "$_id"
            - Use "foreignField": "field_name" NOT "foreignField": "$field_name"
            - Field references in $project, $group, etc. should use $ prefix
            - Boolean values should be true/false, not True/False

            Respond in this exact JSON format:
            {{
                "has_issues": true/false,
                "issues": "description of issues found",
                "fixed_query": "corrected query if issues found, or null"
            }}

            Only provide the JSON response, nothing else.
            """

            self._initialize_cohere()
            response = self.cohere_client.generate(
                model='command-r-plus',
                prompt=analysis_prompt,
                max_tokens=800,
                temperature=0.1
            )
            
            result = response.generations[0].text.strip()
            
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
