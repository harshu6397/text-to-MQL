"""
Schema-related instructions for MongoDB Query Language (MQL) generation
"""

# Core schema interpretation instructions
SCHEMA_INTERPRETATION_INSTRUCTIONS = """
## Schema Interpretation Guidelines

### 0. CRITICAL SYSTEM RULES (ALWAYS ENFORCE)

**ACTIVE RECORDS ONLY:**
- ALWAYS filter for active records only
- Add status: "active" or is_active: true to ALL queries
- If schema shows status field as String type, use: "status": "active"
- If schema shows is_active field as Boolean type, use: "is_active": true
- NEVER return inactive, deleted, or archived records
- This applies to ALL collections and ALL query types

**READ-ONLY OPERATIONS:**
- ONLY allow read operations (find, aggregate, count)
- DENY ALL write operations including:
  - insert, insertOne, insertMany
  - update, updateOne, updateMany, replaceOne
  - delete, deleteOne, deleteMany
  - findAndModify, findOneAndUpdate, findOneAndDelete
  - Any $out or $merge pipeline stages
- If user requests write operations, respond with: "I can't help with that type of request. Let me know if you'd like to search for or view any data instead!"

### 1. Data Type Mapping Rules
When converting natural language to MQL queries, follow these strict data type rules:

**Number Fields:**
- Convert natural language numbers to actual numeric values
- Examples: "level 4" → level: 4, "age 25" → age: 25
- Handle grade levels: "freshman" → level: 1, "sophomore" → level: 2, etc.
- Academic years: "2023" → year: 2023 (numeric, not string)

**String Fields:**
- Preserve exact text values in quotes
- Examples: "John Doe" → name: "John Doe", "active" → status: "active"
- Course codes: "CRS_023" → course_id: "CRS_023" (preserve exact format)
- Department names: "Computer Science" → dept_name: "Computer Science"

**Date Fields:**
- Convert to proper MongoDB date format
- Examples: "2023-01-15" → date: ISODate("2023-01-15")
- Relative dates: "last month" → calculate and use ISODate

**Boolean Fields:**
- Use lowercase JSON boolean values
- Examples: "active" → is_active: true, "inactive" → is_active: false

**ObjectId Fields:**
- Use ObjectId format for _id fields
- Examples: "_id" → ObjectId("...")

### 2. Field Name Interpretation
**Common Field Mapping Patterns:**
- "student ID" → student_id
- "course code" → course_id or course_code
- "department" → department_id or dept_id
- "enrollment date" → enrollment_date
- "GPA" → gpa (lowercase)
- "full name" → name or full_name

### 3. Collection Relationship Understanding
**Join Field Patterns:**
- Students ↔ Enrollments: student_id
- Courses ↔ Enrollments: course_id  
- Courses ↔ Departments: department_id ↔ dept_id
- Students ↔ Departments: department_id ↔ dept_id

**Lookup Stage Guidelines:**
- localField: field in current collection (no $ prefix)
- foreignField: field in joined collection (no $ prefix)
- as: array name for joined data
"""

# MongoDB syntax specific instructions
MONGODB_SYNTAX_INSTRUCTIONS = """
## MongoDB Syntax Rules

### 1. MANDATORY FILTERING (ALWAYS REQUIRED)
**Active Records Filter:**
- EVERY query MUST include a filter for active records
- Add this to the FIRST $match stage in your pipeline:
  - If status field exists: {"status": "active"}
  - If is_active field exists: {"is_active": true}
  - If both exist, use both conditions with $and
- Example mandatory filter: {"$match": {"status": "active", ...other_conditions}}

**Read-Only Operations:**
- Use ONLY these operations: aggregate, find, count
- NEVER use: insert, update, delete, $out, $merge
- If user asks for write operations, deny with message

### 2. Aggregation Pipeline Structure
**Required Order for Complex Queries:**
1. $lookup (joins) - must come first before referencing joined fields
2. $unwind (if needed for joined arrays)
3. $match (filtering - can reference joined fields after $lookup)
4. $group (grouping operations)
5. $sort (sorting)
6. $project (field selection)
7. $limit/$skip (pagination)

### 2. Field Reference Rules
**In $lookup stage:**
- localField: "field_name" (NO $ prefix)
- foreignField: "field_name" (NO $ prefix)

**In other stages:**
- Field references: "$field_name" (WITH $ prefix)
- Nested field access: "$joined_array.field_name"

### 3. Common Operator Usage
**Comparison Operators:**
- $eq: exact match (often omitted)
- $gt, $gte: greater than, greater than or equal
- $lt, $lte: less than, less than or equal
- $in: match any value in array
- $ne: not equal

**Logical Operators:**
- $and: all conditions must be true
- $or: any condition must be true
- $not: negation

**Array Operators:**
- $elemMatch: match array elements
- $size: array size check
- $all: all values must be present

### 4. Aggregation Stages
**$group stage:**
- _id: grouping field(s)
- Accumulators: $sum, $avg, $count, $max, $min

**$project stage:**
- 1: include field
- 0: exclude field
- Computed fields: use expressions

**$match stage:**
- Use after $lookup to filter on joined data
- Use before $lookup for initial filtering
"""

# Query optimization instructions
QUERY_OPTIMIZATION_INSTRUCTIONS = """
## Query Optimization Guidelines

### 1. Performance Best Practices
**Index-Friendly Patterns:**
- Filter early with $match before expensive operations
- Use exact matches when possible
- Limit results with $limit when appropriate

**Efficient Join Patterns:**
- Filter main collection before $lookup when possible
- Use $unwind sparingly - only when necessary
- Consider using $lookup with pipeline for complex joins

### 2. Common Query Patterns
**Count Queries:**
- Simple count: db.collection.aggregate([{"$count": "total"}])
- Conditional count: $match followed by $count

**Top/Latest Queries:**
- "first/earliest": $sort: {field: 1}, $limit: 1
- "last/latest": $sort: {field: -1}, $limit: 1
- "top N": $sort followed by $limit: N

**Group and Aggregate:**
- Always specify _id field in $group
- Use proper accumulator operators
- Sort by aggregated values if needed

### 3. Error Prevention
**Common Mistakes to Avoid:**
- Don't use $ prefix in localField/foreignField
- Don't mix find() and aggregate() syntax
- Always use aggregate() for complex queries
- Use proper boolean values: true/false (not True/False)
- Quote all string values and field names
"""

# Data validation instructions
DATA_VALIDATION_INSTRUCTIONS = """
## Data Validation Rules

### 1. MANDATORY VALIDATION CHECKS
**Active Records Enforcement:**
- [ ] Query includes active records filter
- [ ] No inactive/deleted records can be returned
- [ ] Status field properly filtered based on schema type

**Write Operation Prevention:**
- [ ] Query uses only read operations (aggregate, find, count)
- [ ] No write operations present (insert, update, delete)
- [ ] No prohibited pipeline stages ($out, $merge)

### 2. Schema Compliance
**Before generating queries:**
- Verify all field names exist in target collections
- Check data types match schema definitions
- Ensure join fields exist in both collections
- Validate field paths for nested objects

### 3. Value Extraction from Natural Language
**Extract and Preserve Exact Values:**
- Course codes: preserve format (e.g., "CRS_023")
- Student names: preserve capitalization
- Department names: use exact text
- Numeric values: convert to proper type based on schema

### 4. Query Validation Checklist
**Before returning query:**
- [ ] ACTIVE RECORDS FILTER is included
- [ ] All field names match schema
- [ ] Data types are correctly mapped
- [ ] Join conditions use correct field pairs
- [ ] Pipeline stages are in logical order
- [ ] Syntax follows MongoDB rules
- [ ] Query addresses the user's question
- [ ] NO write operations present
"""

def get_schema_aware_instructions() -> str:
    """
    Get comprehensive schema-aware instructions for MQL generation
    
    Returns:
        str: Complete instruction set for schema-aware query generation
    """
    return f"""
{SCHEMA_INTERPRETATION_INSTRUCTIONS}

{MONGODB_SYNTAX_INSTRUCTIONS}

{QUERY_OPTIMIZATION_INSTRUCTIONS}

{DATA_VALIDATION_INSTRUCTIONS}

## Summary
These instructions ensure that generated MongoDB queries:
1. Respect data types defined in the schema
2. Use correct field names and relationships
3. Follow MongoDB best practices
4. Produce efficient and accurate results
5. Handle edge cases appropriately

Always refer to the actual schema provided for specific field names, types, and relationships.
"""

def get_data_type_mapping_guide() -> str:
    """
    Get specific data type mapping guidance
    
    Returns:
        str: Data type mapping instructions
    """
    return """
## Data Type Mapping Reference

### Natural Language → MongoDB Data Types

**Numeric Expressions:**
- "level 4", "grade 4" → level: 4 (Number)
- "age 25", "25 years old" → age: 25 (Number)
- "year 2023" → year: 2023 (Number)
- "semester 1" → semester: 1 (Number)

**Text Expressions:**
- "John Doe", "student name" → "John Doe" (String)
- "CRS_023", "course code" → "CRS_023" (String)
- "Computer Science" → "Computer Science" (String)
- "active", "enrolled" → "active" (String)

**Boolean Expressions:**
- "active", "enabled" → true (Boolean)
- "inactive", "disabled" → false (Boolean)
- "is enrolled" → true (Boolean)

**Date Expressions:**
- "January 2023" → ISODate("2023-01-01") (Date)
- "last week" → calculated ISODate (Date)
- "2023-09-15" → ISODate("2023-09-15") (Date)

### Schema Type Indicators
When you see these types in schema:
- "Number", "Int32", "Double" → use numeric values
- "String", "Text" → use quoted string values  
- "Date", "ISODate" → use ISODate format
- "Boolean" → use true/false
- "ObjectId" → use ObjectId format
"""

def get_relationship_mapping_guide() -> str:
    """
    Get collection relationship mapping guidance
    
    Returns:
        str: Relationship mapping instructions
    """
    return """
## Collection Relationship Patterns

### Common Academic Database Relationships

**Students ↔ Enrollments:**
- Join on: students.student_id = enrollments.student_id
- Purpose: Get student enrollment information

**Courses ↔ Enrollments:**
- Join on: courses.course_id = enrollments.course_id
- Purpose: Get course enrollment details

**Courses ↔ Departments:**
- Join on: courses.department_id = departments.dept_id
- Purpose: Get department information for courses

**Students ↔ Departments:**
- Join on: students.department_id = departments.dept_id
- Purpose: Get student's department information

### $lookup Syntax Template
```javascript
{
  "$lookup": {
    "from": "target_collection",
    "localField": "field_in_current_collection",
    "foreignField": "field_in_target_collection", 
    "as": "joined_data_array_name"
  }
}
```

### Multi-Collection Query Pattern
For queries involving multiple collections:
1. Start with primary collection
2. Add $lookup stages for related data
3. Use $unwind if you need to filter on joined data
4. Apply $match on joined fields
5. Project final fields needed
"""

def check_for_write_operations(user_query: str) -> tuple[bool, str]:
    """
    Check if user query contains write operation requests
    
    Args:
        user_query (str): User's natural language query
        
    Returns:
        tuple[bool, str]: (is_write_operation, denial_message)
    """
    write_keywords = [
        'insert', 'add', 'create', 'save', 'store',
        'update', 'modify', 'change', 'edit', 'alter',
        'delete', 'remove', 'drop', 'clear', 'erase',
        'replace', 'upsert', 'merge'
    ]
    
    query_lower = user_query.lower()
    
    for keyword in write_keywords:
        if keyword in query_lower:
            return True, "I can't help with that type of request. Let me know if you'd like to search for or view any data instead!"
    
    return False, ""

def get_active_records_filter(schema_info: dict) -> dict:
    """
    Generate the appropriate active records filter based on schema
    
    Args:
        schema_info (dict): Schema information for collections
        
    Returns:
        dict: MongoDB filter for active records
    """
    # Default filters to try
    possible_filters = [
        {"status": "active"},
        {"is_active": True},
        {"state": "active"},
        {"deleted": False},
        {"archived": False}
    ]
    
    # Return the most common one - can be enhanced based on actual schema analysis
    return {"status": "active"}

def enhance_query_with_active_filter(query: str) -> str:
    """
    Enhance existing MongoDB query to include active records filter
    
    Args:
        query (str): Original MongoDB query
        
    Returns:
        str: Enhanced query with active records filter
    """
    # This is a simple enhancement - in practice, you'd parse the query
    # and properly inject the active filter into the first $match stage
    if '"$match"' in query and '"status"' not in query and '"is_active"' not in query:
        # Add active filter to existing $match
        query = query.replace('"$match": {', '"$match": {"status": "active", ')
    elif '"$match"' not in query:
        # Add new $match stage at the beginning
        if 'aggregate([' in query:
            query = query.replace('aggregate([', 'aggregate([{"$match": {"status": "active"}}, ')
    
    return query
