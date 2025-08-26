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
    return f"""# MongoDB Query Language (MQL) Generation Prompt

You are an expert MongoDB query generator. Your task is to convert natural language descriptions into accurate MongoDB Query Language (MQL) queries.

## Instructions

1. **Extract ALL the data from the user's question first** so you understand what they are looking for:
   - Identify specific IDs, codes, names mentioned (e.g., "CRS_023", "Machine Learning", specific student names)
   - Extract exact values that should be used in filters (preserve case and format)
   - Note any specific field values referenced in the query

2. **Analyze the natural language input** to understand:
   - The operation type (find, aggregate, update, delete, etc.)
   - Filter conditions and criteria
   - Projection requirements
   - Sorting, limiting, or grouping needs
   - Any aggregation pipeline operations

3. **Generate syntactically correct MQL** that:
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

4. **Important Rules:**
   - Don't add '$' before field names unless it's a MongoDB operator (e.g., $gt, $in), as this is a common mistake
   - Use ONLY aggregate() syntax, not find()
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

### Input: "Find all users who are older than 25 and live in New York"
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

### Input: "Get the total number of orders by status, sorted by count descending"
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

### Input: "Show me student names and ages who are enrolled in course CRS_023"
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

### Input: "Find all courses in Mathematics department"
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

### Input: "How many departments do we have?"
```python
db.departments.aggregate([{{"$count": "total"}}])
```

### What is the average GPA of all students?
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

Notes: you need to build the aggregation pipeline for python code blocks like above.

## Schema Context
Target Collection: {target_collection}
{schema_context if schema_context else "No schema information available"}

## Your Task

Convert the following natural language query into MQL:

**Input:** {natural_language_query}

Return ONLY the MongoDB aggregate command. Do not include any explanations, comments, or additional text. Just the command starting with db.{target_collection}.aggregate()"""


FORMAT_ANSWER_PROMPT = """You are a helpful assistant that converts database query results into natural language answers.

User's original question: "{user_query}"

Database query result: {query_result}

Instructions:
1. Provide a clear, concise answer to the user's question
2. If the result is a number, state it clearly with context
3. If the result is a list, format it nicely (use bullets if more than 3 items)
4. If the result is empty, explain that no data was found
5. Be conversational and helpful
6. Don't mention technical details about MongoDB or the query

Provide only the natural language answer:"""


def get_query_fix_prompt(query: str, user_query: str, schema_context: str) -> str:
    """
    Generate the query fix prompt for when a query returns empty results
    
    Args:
        query (str): The MongoDB query that returned empty results
        user_query (str): User's original natural language question
        schema_context (str): Schema information for context
        
    Returns:
        str: Complete query fix prompt
    """
    return f"""The following MongoDB query returned empty results:

Query: {query}

User's original question: {user_query}

Available collections and schemas:
{schema_context}

Extract all the data from the user's question first so you understand what they are looking for.

Please check the query and fix any issues. Common problems include:
- Wrong data extracted from the initial user question (e.g., wrong course ID, wrong names)
- As we are using python, so ensure that the query must use the python syntax for db.collection.aggregate([...]) and keywords like None, True, False etc
- Wrong localField in $lookup (should match the actual field name, not _id)
- Wrong collection names
- Wrong field names
- Incorrect matching conditions
- Logical errors in the aggregation pipeline (e.g., $match before $lookup)
- Missing or extra brackets/parentheses
- Wrong pipeline stage order

IMPORTANT: Pay attention to the aggregation pipeline order:
1. $lookup must come BEFORE you can reference the joined data in $match
2. $unwind should come after $lookup
3. $match on joined data should come after $unwind

Return ONLY the corrected MongoDB query, nothing else."""
