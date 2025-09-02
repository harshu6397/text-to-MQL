"""
Prompts for the MongoDB Query Language (MQL) generation
"""

def get_collection_identification_prompt(user_query: str, available_collections: list) -> str:
    """
    Generate prompt for AI-powered collection identification
    
    Args:
        user_query (str): User's natural language query
        available_collections (list): List of available collection names
        
    Returns:
        str: Collection identification prompt
    """
    collections_str = ", ".join(available_collections)
    
    return f"""# Collection Identification for MongoDB Query

You are an expert MongoDB database analyst. Your task is to identify which collections are relevant for answering a user's natural language query.

## Available Collections
{collections_str}

## User Query
"{user_query}"

## Instructions
1. **Analyze the user's question** to understand what information they're seeking
2. **Identify primary collections** that directly contain the data needed to answer the question
3. **Identify related collections** that might be needed for joins or additional context
4. **Consider relationships** between collections (e.g., if asking about students in a course, you might need both students and enrollments collections)

## Rules
- Return only collection names that exist in the available collections list
- Prioritize collections that directly answer the question
- Include related collections only if they're necessary for the query
- Maximum of 4 collections to avoid complexity
- Return collections in order of importance (most relevant first)

## Output Format
Return only a JSON array of collection names, for example:
["students", "departments", "enrollments"]

Do not include any explanation or additional text - just the JSON array.

## Examples
These are generic examples - adapt them based on the actual collections and schema provided:

- Query: "How many records are there?" → Check the most relevant collection
- Query: "Show records from [collection_name]" → Use the specified collection
- Query: "Find records with [relationship]" → Use relevant collections based on schema
- Query: "List all records by [field]" → Use collection containing that field

## Your Response
Based on the user query above, identify the relevant collections:"""

def check_query_permissions(natural_language_query: str) -> tuple[bool, str]:
    """
    Check if the user query is allowed (read-only operations)
    
    Args:
        natural_language_query (str): User's natural language query
        
    Returns:
        tuple[bool, str]: (is_allowed, denial_message_if_not_allowed)
    """
    from .schema_instructions import check_for_write_operations
    
    is_write, denial_message = check_for_write_operations(natural_language_query)
    return not is_write, denial_message

def get_mql_generation_prompt(target_collection: str, schema_context: str, natural_language_query: str) -> str:
    """
    Generate the MQL generation prompt with dynamic values
    
    Args:
        target_collection (str): Target collection name
        schema_context (str): Schema information for context
        natural_language_query (str): User's natural language query
        
    Returns:
        str: Complete MQL generation prompt
    """
    # Import schema instructions to include in the prompt
    from .schema_instructions import get_schema_aware_instructions
    
    schema_instructions = get_schema_aware_instructions()
    
    return f"""# MongoDB Query Language (MQL) Generation Prompt

You are an expert MongoDB query generator. Your task is to convert natural language descriptions into accurate MongoDB Query Language (MQL) queries.

## CRITICAL REQUIREMENTS (ALWAYS ENFORCE)
1. **ACTIVE RECORDS ONLY**: Every query MUST include a filter for active records only. Add {{"status": "active"}} or {{"is_active": true}} to all $match stages.
2. **READ-ONLY OPERATIONS**: Only generate read operations (aggregate, find, count). If user requests write operations (insert, update, delete), respond with the denial message from schema instructions.
3. **EXCLUDE _ID FIELDS**: Never include "_id" fields in $project stages unless the user specifically asks for IDs. Use "_id": 0 to exclude _id from results when using $project.

## Important Notes
- You need to build the aggregation pipeline for python code blocks like above
- Never add ```python and ``` at the beginning and end of the code block

{schema_instructions}

## Instructions

### 1. Extract ALL Data from User's Question
Extract ALL the data from the user's question first so you understand what they are looking for:
- Identify specific IDs, codes, names mentioned (e.g., "CRS_023", "Machine Learning", specific student names)
- Extract exact values that should be used in filters (preserve case and format)
- Note any specific field values referenced in the query

### 2. Analyze Natural Language Input
Analyze the natural language input to understand:
- The operation type (find, aggregate, update, delete, etc.)
- Filter conditions and criteria
- Projection requirements
- Sorting, limiting, or grouping needs
- Any aggregation pipeline operations

### 3. Generate Syntactically Correct MQL
Generate syntactically correct MQL that:
- Uses proper MongoDB syntax and operators
- **HANDLES DATA TYPES CORRECTLY** based on schema:
  * Number fields: Use numeric values (e.g., level: 4, age: 22)
  * String fields: Use string values (e.g., name: "John Doe", status: "active")
  * Date fields: Use ISODate format
  * ObjectId fields: Use ObjectId format
- **MAPS NATURAL LANGUAGE TO CORRECT DATA TYPES**:
  * Check schema to determine if field is Number, String, Date, etc.
  * Convert text descriptions to appropriate data types based on schema
  * For level/year fields: map grade levels to numbers if schema shows Number type
  * Always check field type in schema before creating query conditions
- Includes proper field names and collection references
- Uses efficient query patterns
- **PRESERVES EXACT VALUES** from the user query (e.g., if user says "CRS_023", use "CRS_023" not "CRS_002")

### 4. Important Rules
- Don't add '$' before field names unless it's a MongoDB operator (e.g., $gt, $in), as this is a common mistake
- Use ONLY aggregate() syntax, not find()
- **USE CASE-INSENSITIVE MATCHING for names and descriptive text**: Use {{"field": {{"$regex": "value", "$options": "i"}}}} for better user experience
- **PRESERVE EXACT VALUES for IDs, codes, and enum values**: Use exact matching like {{"course_id": "CRS_023"}} for precise identifiers
- For queries with words like "first", "earliest", "oldest", use $sort with ascending order (1) and $limit: 1
- For queries with words like "last", "latest", "newest", use $sort with descending order (-1) and $limit: 1
- For queries asking "how many", "count", "total", use $count
- Always return just the aggregate command starting with db.{target_collection}.aggregate()
- Use double quotes for all string values and field names
- **PAY ATTENTION TO AGGREGATION PIPELINE ORDER**: $lookup must come before you can reference the joined data in $match
- Use JSON boolean values: true/false (not True/False)

## Common MQL Operators Reference

### Query Operators
- `$eq`: Equal to
- `$ne`: Not equal to
- `$gt`, `$gte`: Greater than, greater than or equal
- `$lt`, `$lte`: Less than, less than or equal
- `$in`: Matches any value in array
- `$nin`: Does not match any value in array
- `$exists`: Field exists
- `$regex`: Regular expression match
- `$and`, `$or`, `$not`: Logical operators

### Array Operators
- `$elemMatch`: Match array elements
- `$all`: Match all values in array
- `$size`: Array size

### Aggregation Pipeline Stages
- `$match`: Filter documents
- `$group`: Group documents
- `$sort`: Sort documents
- `$project`: Select/transform fields
- `$limit`, `$skip`: Pagination
- `$lookup`: Join collections
- `$unwind`: Deconstruct arrays

### localField and foreignField in $lookup
- `localField`: Field from the input documents (current collection)
- `foreignField`: Field from the documents of the "from" collection (joined collection)
- Use dot notation to access nested fields (e.g., "enrollments_info.course_id")
- Use proper field names as per the schema context provided (department_id, course_id, student_id, etc.)

## Examples

### Example 1: Basic Filtering
**Input:** "Find all users who are older than 25 and live in New York"
```python
db.users.aggregate([
  {{
    "$match": {{
      "age": {{ "$gt": 25 }},
      "city": "New York"
    }}
  }}
])
```

### Example 2: Grouping and Sorting
**Input:** "Get the total number of orders by status, sorted by count descending"
```python
db.orders.aggregate([
  {{
    "$group": {{
      "_id": "$status",
      "count": {{ "$sum": 1 }}
    }}
  }},
  {{
    "$sort": {{ "count": -1 }}
  }}
])
```

### Example 3: Joins with Lookup
**Input:** "Show me student names and ages who are enrolled in course CRS_023"
```python
db.students.aggregate([
  {{
    "$lookup": {{
      "from": "enrollments",
      "localField": "student_id",
      "foreignField": "student_id",
      "as": "enrollments_info"
    }}
  }},
  {{
    "$unwind": {{
      "path": "$enrollments_info",
      "preserveNullAndEmptyArrays": False
    }}
  }},
  {{
    "$match": {{
      "enrollments_info.course_id": "CRS_023"
    }}
  }},
  {{
    "$project": {{
      "name": 1,
      "age": 1
    }}
  }}
])
```

### Example 4: Complex Join with Department
**Input:** "Find all courses in Mathematics department"
```python
db.courses.aggregate([
  {{
    "$lookup": {{
      "from": "departments",
      "localField": "department_id",
      "foreignField": "dept_id", 
      "as": "department_info"
    }}
  }},
  {{
    "$unwind": {{
      "path": "$department_info",
      "preserveNullAndEmptyArrays": False
    }}
  }},
  {{
    "$match": {{
      "department_info.name": "Mathematics"
    }}
  }},
  {{
    "$project": {{
      "course_id": 1,
      "course_name": 1,
      "course_code": 1,
      "credits": 1,
      "semester": 1,
      "year": 1
    }}
  }}
])
```

### Example 5: Count Query
**Input:** "How many departments do we have?"
```python
db.departments.aggregate([{{"$count": "total"}}])
```

### Example 6: Average Calculation
**Input:** "What is the average GPA of all students?"
```python
db.students.aggregate([
    {{
        "$group": {{
        "_id": None,
        "averageGPA": {{ "$avg": "$gpa" }}
        }}
    }}
])
```

### Example 7: Case-Insensitive Name Search
**Input:** "Find information about user named Apollo"
```python
db.users.aggregate([
  {{{{
    "$match": {{{{
      "firstName": {{{{"$regex": "Apollo", "$options": "i"}}}},
      "status": "active"
    }}}}
  }}}}
])
```

### Example 8: Case-Insensitive Full Name Search  
**Input:** "Show me details for Apollo Otika"
```python
db.users.aggregate([
  {{{{
    "$match": {{{{
      "$and": [
        {{{{"firstName": {{{{"$regex": "Apollo", "$options": "i"}}}}}}}},
        {{{{"lastName": {{{{"$regex": "Otika", "$options": "i"}}}}}}}}
      ],
      "status": "active"
    }}}}
  }}}}
])
```

### Example 9: Case-Insensitive Department Search
**Input:** "List all courses in computer science department"
```python
db.courses.aggregate([
  {{{{
    "$match": {{{{
      "department_name": {{{{"$regex": "computer science", "$options": "i"}}}},
      "status": "active"
    }}}}
  }}}}
])
```

## Schema Context
Target Collection: {target_collection}
{schema_context if schema_context else "No schema information available"}

## Your Task

Convert the following natural language query into MQL:

**Input:** {natural_language_query}

Return ONLY the Single MongoDB aggregate command. Do not include any explanations, comments, or additional text. Just the command starting with db.{target_collection}.aggregate()"""


FORMAT_ANSWER_PROMPT = """# Format Database Query Results

You are a helpful assistant that converts database query results into natural language answers.

## User's Original Question
"{user_query}"

## Database Query Result
{query_result}

## Instructions
1. Provide a clear, concise answer to the user's question
2. If the result is a number, state it clearly with context
3. If the result is a list, format it nicely (use bullets if more than 3 items)
4. If the result is empty, explain that no data was found
5. Be conversational and helpful
6. Don't mention technical details about MongoDB or the query

## Your Response
Provide only the natural language answer:"""



def get_query_check_prompt(query: str, user_query: str, schema_context: str) -> str:
    """
    Generate the prompt for checking if a MongoDB query needs validation
    
    Args:
        query (str): The MongoDB query to check
        user_query (str): User's original natural language question
        schema_context (str): Schema information for context
        
    Returns:
        str: Complete query check prompt
    """
    return f"""# MongoDB Query Validation Check

## Task
Analyze the following MongoDB query and determine if it has ACTUAL ISSUES that need fixing.

## Query Information
**User Query:** "{user_query}"
**Generated MongoDB Query:** {query}
**Schema Context:** {schema_context}

## Check for ACTUAL PROBLEMS Only
ONLY respond "YES" if you detect ACTUAL PROBLEMS like:

### 1. Syntax Errors
- Invalid MongoDB syntax
- Wrong operators
- Malformed JSON

### 2. Field Mismatches
- Field names in query don't exist in schema

### 3. Data Type Errors
- Using string values for Number fields or vice versa

### 4. Critical Logic Errors
- Query logic completely wrong for the user's request

### 5. MongoDB Rule Violations
- $lookup with $ prefixed localField/foreignField, etc.

## DO NOT Flag These
DO NOT flag for checking if:
- Query is syntactically correct
- Field names match schema
- Data types are appropriate
- Query logic makes sense for the user request
- It's just a complex query with multiple stages

## Response Format
Respond with "YES" ONLY if there are ACTUAL ISSUES that need fixing, otherwise "NO".
Give only YES or NO as the answer."""


def get_query_analysis_prompt(query: str, user_query: str, schema_context: str) -> str:
    """
    Generate the prompt for analyzing MongoDB query issues and suggesting fixes
    
    Args:
        query (str): The MongoDB query to analyze
        user_query (str): User's original natural language question
        schema_context (str): Schema information for context
        
    Returns:
        str: Complete query analysis prompt
    """
    # Import schema instructions for analysis
    from .schema_instructions import get_data_type_mapping_guide, MONGODB_SYNTAX_INSTRUCTIONS
    
    data_type_guide = get_data_type_mapping_guide()
    
    return f"""# MongoDB Query Analysis and Fix

## Query Information
**User Query:** "{user_query}"
**MongoDB Query:** {query}
**Schema Context:** {schema_context}

{data_type_guide}

{MONGODB_SYNTAX_INSTRUCTIONS}

## Analysis Checklist
Check for:

### 1. Syntax Issues
- Syntax errors
- Field name mismatches with schema
- Incorrect operators usage

### 2. Structural Issues
- Missing required stages
- Performance issues
- Logic errors

### 3. Data Type Issues
**DATA TYPE MISMATCHES:**
- If schema shows field as Number but query uses string value
- If schema shows field as String but query uses numeric value
- Convert natural language terms to appropriate data types based on schema
- For level/grade fields: check if they should be numeric vs string based on schema

### 4. MongoDB Syntax Rules
**IMPORTANT MONGODB SYNTAX RULES:**
- In $lookup stage, localField and foreignField should NOT have $ prefix
- Use "localField": "_id" NOT "localField": "$_id"
- Use "foreignField": "field_name" NOT "foreignField": "$field_name"
- Field references in $project, $group, etc. should use $ prefix
- Boolean values should be true/false, not True/False

## Important Notes
- You need to build the aggregation pipeline for python code blocks like above
- Never add ```python and ``` at the beginning and end of the code block

## Response Requirements
Return ONLY the Single MongoDB aggregate command. Do not include any explanations, comments, or additional text. Just the command starting with db.target_collection.aggregate()

## Response Format
Respond in this exact JSON format:
```json
{{
    "has_issues": true/false,
    "issues": "description of issues found",
    "fixed_query": "corrected query if issues found, or null"
}}
```

Only provide the JSON response, nothing else."""
