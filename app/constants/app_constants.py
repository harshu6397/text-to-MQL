"""
Application constants for the MongoDB MQL generation service
"""

# Default values
MAX_RETRIES = 3
MAX_COLLECTIONS_TO_ANALYZE = 3

# Query type keywords (these are universal and not collection-specific)
COUNT_KEYWORDS = ['count', 'how many', 'total', 'number']
FIRST_KEYWORDS = ['first', 'earliest', 'oldest']
LAST_KEYWORDS = ['last', 'latest', 'newest']

# Common date field patterns (these are universal field name patterns)
DATE_FIELD_PATTERNS = ['date', 'created', 'established', 'year', 'time', 'updated']

# System collections to filter out (these are MongoDB system collections)
SYSTEM_COLLECTIONS = ['checkpoint', 'system']

# Query limits and timeouts
QUERY_TIMEOUT = 30  # seconds
MAX_RESULT_DISPLAY_LENGTH = 200
MAX_TOKEN_LIMIT = 1000

# Model configuration
DEFAULT_TEMPERATURE = 0.1
RECURSION_LIMIT = 50

# Database Collection Mapping and Business Context
DATABASE_COLLECTION_MAP = {
    # Core Organizational Collections
    "USERS": {
        "purpose": "Central user management - employees, trainers, administrators",
        "field_schema": {
            "firstName": "string - User's first name",
            "lastName": "string - User's last name",
            "email": "string - User's email address",
            "loginId": "string - Login identifier/username",
            "departments": "array - Department IDs user belongs to",
            "orgId": "ObjectId/string - Organization identifier",
            "roleId": "ObjectId/string - User role identifier",
            "accounts": "array - Account IDs associated with user",
            "deleted": "boolean - false=active user, true=deleted/deactivated",
            "lastLoginAttempt": "date - Last login timestamp",
            "createdOn": "date - Account creation timestamp",
            "modifiedOn": "date - Last modification timestamp",
            "_id": "ObjectId - Unique user identifier"
        },
        "relationships": ["departments", "organizations", "roles", "accounts", "courseassignments", "courseprogresses", "useractivities", "conversations"],
        "business_logic": "Primary entity for all system users. Links to departments and organizations for training purposes",
        "query_hints": "Use for employee searches, authentication, profile management. Use firstName/lastName for name searches"
    },
    "DEPARTMENTS": {
        "purpose": "Business departments that organize the company training structure", 
        "field_schema": {
            "name": "string - Department name (e.g., 'Service', 'Sales', 'Parts', 'Body Shop', 'BDC Service')",
            "createdOn": "date - Department creation timestamp",
            "createdBy": "ObjectId/string - User ID who created the department",
            "modifiedOn": "date - Last modification timestamp",
            "deleted": "boolean - false=active department, true=deleted/deactivated",
            "__v": "integer - Version key",
            "_id": "ObjectId - Unique department identifier"
        },
        "relationships": ["users", "courses", "organizations", "coursecontents"],
        "business_logic": "Organizational structure for business divisions and training groups",
        "query_hints": "Use for department-based queries, organizational hierarchy, employee grouping"
    },
    "COURSES": {
        "purpose": "Training courses offered by the organization",
        "field_schema": {
            "title": "string - Course title/name",
            "description": "string - Course description and content overview",
            "orgId": "ObjectId/string - Organization identifier",
            "isGlobal": "boolean - true=available globally, false=organization-specific",
            "createdBy": "ObjectId/string - User ID who created the course",
            "updatedBy": "ObjectId/string - User ID who last updated the course",
            "isDeleted": "boolean - false=active course, true=deleted/archived",
            "accounts": "array - Account IDs that have access to this course",
            "departments": "array - Department IDs assigned to this course",
            "interactionType": "string - Interaction type ('sequential', 'random')",
            "modules": "array - Module IDs included in this course",
            "isPublish": "boolean - true=published, false=not published",
            "isDraft": "boolean - true=draft state, false=finalized",
            "itemCount": "integer - Number of items/modules in the course",
            "awardCertificate": "boolean - true=awards certificate upon completion",
            "isProGlobal": "boolean - Professional global course flag",
            "isUniversityCourse": "boolean - University-level course flag",
            "createdOn": "date - Creation timestamp",
            "modifiedOn": "date - Last modification timestamp",
            "createdAt": "date - Alternative creation timestamp",
            "updatedAt": "date - Alternative update timestamp",
            "__v": "integer - Version key",
            "_id": "ObjectId - Unique course identifier"
        },
        "relationships": ["departments", "organizations", "accounts", "users", "courseassignments", "courseprogresses", "courseitems", "modules", "coursecontents"],
        "business_logic": "Training content management and employee skill development programs",
        "query_hints": "Use for training catalog queries, course content searches, employee development programs. Filter by status=false for available courses"
    },
    "COURSEASSIGNMENTS": {
        "purpose": "Links employees to training courses - enrollment management",
        "key_fields": ["courseId", "userId", "assignedAt", "isActive", "status"],
        "field_schema": {
            "courseId": "ObjectId/string - Reference to the assigned course",
            "userId": "ObjectId/string - Reference to the user assigned to the course",
            "assignedAt": "date - When the course was assigned",
            "isActive": "boolean - true=assignment active, false=assignment inactive",
            "status": "string - Assignment status (completed, not_started, in_progress, etc.)",
            "createdOn": "date - Record creation timestamp",
            "modifiedOn": "date - Record last modification timestamp",
            "createdAt": "date - Alternative creation timestamp",
            "updatedAt": "date - Alternative update timestamp",
            "dueDate": "date - When the course assignment is due",
            "isReassigned": "boolean - true=reassigned, false=original assignment",
            "assignmentType": "string - Type of assignment (Course, etc.)",
            "assignmentTypeId": "ObjectId/string - Reference to the specific assignment type entity",
            "assignedBy": "ObjectId/string - Reference to the user who made the assignment (optional)",
            "_id": "ObjectId - Unique assignment identifier"
        },
        "relationships": ["users", "courses", "courseprogresses", "useractivities"],
        "business_logic": "Junction table for employee-course relationships and training assignments",
        "query_hints": "Use for training enrollment queries, employee-course relationships, training assignments. Filter by isActive=true for active assignments"
    },
    "COURSEPROGRESSES": {
        "purpose": "Tracks employee progress through training courses",
        "key_fields": ["courseId", "userId", "status", "isActive", "createdOn"],
        "field_schema": {
            "courseId": "string - Reference to the course being tracked",
            "userId": "string - Reference to the user whose progress is tracked",
            "status": "string - Progress status (not_started, in_progress, completed, etc.)",
            "isActive": "boolean - true=progress tracking active, false=inactive",
            "createdOn": "date - When progress tracking started",
            "modifiedOn": "date - When progress was last updated",
            "__v": "number - Version key",
            "awardCertificate": "boolean - true=certificate awarded, false=no certificate",
            "completedItems": "array - List of completed course items/modules",
            "startedAt": "date - When the user started the course",
            "_id": "ObjectId - Unique progress tracking identifier"
        },
        "relationships": ["users", "courses", "courseassignments", "itemprogresses", "useractivities"],
        "business_logic": "Progress tracking for training completion and employee development",
        "query_hints": "Use for progress reports, completion status, training analytics, employee performance. Filter by isActive=true for current progress"
    },
    "ACCOUNTS": {
        "purpose": "User account management for organizational access",
        "key_fields": ["name", "orgId", "accountId", "createdOn", "createdBy"],
        "field_schema": {
            "name": "string - Account name or title",
            "orgId": "string - Reference to the parent organization",
            "accountId": "string - Unique account identifier/code",
            "createdOn": "date - When the account was created",
            "createdBy": "string - Reference to user who created the account",
            "modifiedOn": "date - When the account was last modified",
            "deleted": "boolean - true=account deleted, false=account active",
            "brands": "array - List of brands associated with the account",
            "__v": "number - Version key",
            "dealerType": "string - Type of dealer (e.g., Mass Market Automotive Dealership)",
            "_id": "ObjectId - Unique account identifier"
        },
        "relationships": ["organizations", "users", "courses", "documents", "coursecontents", "roles"],
        "business_logic": "User account structure for multi-organization access",
        "query_hints": "Use for user details, organizational access. Filter by deleted=false for active accounts"    },
    "ORGANIZATIONS": {
        "purpose": "Top-level business organizations and companies using the training platform",
        "key_fields": ["name", "createdBy", "deleted", "updatedBy", "modifiedOn"],
        "field_schema": {
            "name": "string - Organization name",
            "createdBy": "string - Reference to user who created the organization",
            "deleted": "boolean - true=organization deleted, false=organization active",
            "updatedBy": "string - Reference to user who last updated the organization",
            "modifiedOn": "date - When the organization was last modified",
            "createdOn": "date - When the organization was created",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique organization identifier"
        },
        "relationships": ["users", "accounts", "departments", "courses"],
        "business_logic": "Highest level organizational structure for multi-company training management",
        "query_hints": "Use for multi-tenant queries, company-wide data, organizational management. Filter by deleted=false for active organizations"    },
    
    # Training and Assessment Collections
    "CHALLENGES": {
        "purpose": "Training challenges and assessments for employee skills development",
        "key_fields": ["name", "description", "background_context", "persona_scenario", "objectives"],
        "field_schema": {
            "name": "string - Challenge title/name",
            "description": "string - Challenge description", 
            "moduleType": "string - Type of challenge (e.g., 'rolePlay', 'assessment')",
            "status": "boolean - false=active/available, true=inactive/disabled",
            "deleted": "boolean - false=not deleted, true=deleted/archived",
            "publishstatus": "boolean - true=published, false=draft",
            "background_context": "string - Background scenario context",
            "persona_scenario": "string - Role-play persona details",
            "objectives": "object - Challenge objectives and tasks",
            "assignaccountids": "array - Account IDs assigned to challenge",
            "orgId": "ObjectId/string - Organization identifier",
            "challengetcalltype": "string - Call type (Inbound/Outbound/InPerson)",
            "challengettype": "array - Challenge type categories",
            "createdOn": "date - Creation timestamp",
            "modifiedOn": "date - Last modification timestamp",
            "_id": "ObjectId - Unique challenge identifier"
        },
        "relationships": ["organizations", "accounts", "users", "conversations", "conversationanalyses", "courseitems", "useractivities"],
        "business_logic": "Core assessment and skill-building activities for employee training",
        "query_hints": "Use for training assessment queries, skill evaluations, employee development activities. Note: status=false for active challenges, status=true for inactive"
    },
    "CONVERSATIONS": {
        "purpose": "Employee-system training interactions and practice dialogue sessions",
        "key_fields": ["userId", "challengeId", "promptId", "customerVoice", "isRandomCall"],
        "field_schema": {
            "userId": "ObjectId/string - User identifier (foreign key to users collection)",
            "challengeId": "ObjectId/string - Challenge identifier (foreign key to challenges collection)",
            "promptId": "ObjectId/string - Prompt template identifier",
            "customerVoice": "string - Customer voice/persona used",
            "isRandomCall": "boolean - true=random call, false=scheduled",
            "status": "integer - Conversation status code",
            "deleted": "boolean - false=not deleted, true=deleted",
            "createdOn": "date - Creation timestamp",
            "modifiedOn": "date - Last modification timestamp",
            "_id": "ObjectId - Unique conversation identifier"
        },
        "relationships": ["users", "challenges", "conversationmessages", "conversationanalyses", "useractivities"],
        "business_logic": "Interactive training sessions and role-play communications for skill development",
        "query_hints": "Use for training interaction analysis, practice session logs, employee communication training. Links challenges to users via conversations"    },
    "CONVERSATIONMESSAGES": {
        "purpose": "Individual messages within training conversation sessions",
        "key_fields": ["conversationId", "sender", "content", "audioUrl", "timestamp"],
        "field_schema": {
            "conversationId": "string - Reference to the parent conversation",
            "sender": "string - Message sender (user, bot, system)",
            "content": "string - Message text content",
            "audioUrl": "string - URL to audio recording of message",
            "timestamp": "date - When the message was sent",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique message identifier"
        },
        "relationships": ["conversations"],
        "business_logic": "Detailed communication content for training analysis and feedback",
        "query_hints": "Use for message analysis, conversation details, training communication review. Filter by sender for bot vs user messages"    },
    "CONVERSATIONANALYSES": {
        "purpose": "AI analysis and scoring of employee training conversation sessions",
        "key_fields": ["conversationId", "criteria_evaluation", "marksObtained", "feedback", "needsImprovement"],
        "field_schema": {
            "conversationId": "string - Reference to the analyzed conversation",
            "criteria_evaluation": "array - List of evaluation criteria with marks and details",
            "marksObtained": "number - Total score obtained in the analysis",
            "feedback": "string - Positive feedback and strengths identified",
            "needsImprovement": "string - Areas needing improvement and suggestions",
            "performanceStrategy": "string - Strategic recommendations for performance improvement",
            "passed": "boolean - true=passed evaluation, false=failed evaluation",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique analysis identifier"
        },
        "relationships": ["conversations"],
        "business_logic": "Performance evaluation and feedback generation for employee development",
        "query_hints": "Use for performance analytics, training assessment scoring, employee feedback. Filter by passed=true for successful evaluations"    },
    
    # Content and Training Resource Collections
    "DOCUMENTS": {
        "purpose": "File storage and management for training content and materials",
        "key_fields": ["filename", "originalName", "fileType", "mimeType", "fileSize"],
        "field_schema": {
            "filename": "string - Stored filename in the system",
            "originalName": "string - Original filename when uploaded",
            "fileType": "string - File extension/type (pdf, docx, etc.)",
            "mimeType": "string - MIME type of the file",
            "fileSize": "number - File size in bytes",
            "openaiFileId": "string - OpenAI file identifier for AI processing",
            "vectorStoreId": "string - Vector store identifier for embeddings",
            "vectorStoreStatus": "string - Status of vector processing (completed, pending, etc.)",
            "metadata": "object - Additional file metadata and processing info",
            "accountIds": "array - Account IDs that have access to this document",
            "env": "string - Environment (uat, prod, etc.)",
            "userId": "string - Reference to user who uploaded the document",
            "departments": "array - Department IDs that have access to this document",
            "courseContentId": "array - Course content IDs associated with this document",
            "uploadedAt": "date - When the document was uploaded",
            "description": "string - Document description or summary",
            "processingStatus": "string - Document processing status",
            "pages": "array - Page processing information",
            "totalPages": "number - Total number of pages in document",
            "blobContainer": "string - Storage container name",
            "blobPath": "string - Storage path to the file",
            "blobUrl": "string - URL to access the document",
            "createdAt": "date - Document creation timestamp",
            "updatedAt": "date - Document last update timestamp",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique document identifier"
        },
        "relationships": ["users", "accounts", "departments", "coursecontents"],
        "business_logic": "Digital asset management for training materials and company resources",
        "query_hints": "Use for training content management, file searches, resource queries. Filter by processingStatus=completed for processed files"    },
    "COURSECONTENTS": {
        "purpose": "Training materials and resources linked to courses",
        "key_fields": ["userId", "accounts", "departments", "fileName", "mimeType"],
        "field_schema": {
            "userId": "string - Reference to user who created the content",
            "accounts": "array - Account IDs that have access to this content",
            "departments": "array - Department IDs that have access to this content",
            "fileName": "string - Stored filename of the content",
            "mimeType": "string - MIME type of the content file",
            "originalFileName": "string - Original filename when uploaded",
            "module": "string - Module type (course, etc.)",
            "fileUrl": "string - URL to access the content file",
            "title": "string - Content title or name",
            "description": "string - Content description or summary",
            "createdOn": "date - When the content was created",
            "createdBy": "string - Name/reference of content creator",
            "modifiedOn": "date - When the content was last modified",
            "deleted": "boolean - true=content deleted, false=content active",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique content identifier"
        },
        "relationships": ["courses", "documents", "users", "departments"],
        "business_logic": "Training content delivery and organization for employee development",
        "query_hints": "Use for training content catalogs, learning resource queries, employee materials. Filter by deleted=false for active content"    },
    "COURSEITEMS": {
        "purpose": "Individual items and modules within courses",
        "key_fields": ["itemType", "referenceId", "isPractice", "label", "order"],
        "field_schema": {
            "itemType": "string - Type of course item (challenge, module, content, etc.)",
            "referenceId": "string - Reference to the specific item object",
            "isPractice": "boolean - true=practice item, false=actual assessment",
            "label": "string - Display name/title of the course item",
            "order": "number - Sequence order within the course",
            "createdBy": "string - Reference to user who created the item",
            "updatedBy": "string - Reference to user who last updated the item",
            "isDeleted": "boolean - true=item deleted, false=item active",
            "createdOn": "date - When the item was created",
            "modifiedOn": "date - When the item was last modified",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique course item identifier"
        },
        "relationships": ["courses", "itemprogresses"],
        "business_logic": "Granular course structure and sequencing",
        "query_hints": "Use for detailed course structure, learning path queries. Filter by isDeleted=false for active items, order by 'order' field for sequence"    },
    "MODULES": {
        "purpose": "Reusable learning modules and components",
        "key_fields": ["title", "items", "order", "createdBy", "updatedBy"],
        "field_schema": {
            "title": "string - Module title or name",
            "items": "array - List of item IDs contained in this module",
            "order": "number - Sequence order of the module",
            "createdBy": "string - Reference to user who created the module",
            "updatedBy": "string - Reference to user who last updated the module",
            "isDeleted": "boolean - true=module deleted, false=module active",
            "createdOn": "date - When the module was created",
            "modifiedOn": "date - When the module was last modified",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique module identifier"
        },
        "relationships": ["courseitems", "itemprogresses"],
        "business_logic": "Modular learning content organization",
        "query_hints": "Use for modular content queries, component searches. Filter by isDeleted=false for active modules, order by 'order' field for sequence"    },
    
    # Employee Analytics and Tracking Collections  
    "USERACTIVITIES": {
        "purpose": "Comprehensive tracking of all employee interactions and training behaviors",
        "key_fields": ["userId", "referenceId", "referenceType", "childReferenceId", "childReferenceType"],
        "field_schema": {
            "userId": "string - Reference to the user performing the activity",
            "referenceId": "string - Reference to the main activity object (course progress, etc.)",
            "referenceType": "string - Type of the main reference (CourseProgress, Challenge, etc.)",
            "childReferenceId": "string - Reference to the child/related object",
            "childReferenceType": "string - Type of the child reference (Course, Module, etc.)",
            "assignmentId": "string/null - Reference to assignment if applicable",
            "isPractice": "boolean - true=practice activity, false=actual activity",
            "status": "string - Activity status (not_started, in_progress, completed, etc.)",
            "from": "string - Source of the activity (course, challenge, etc.)",
            "otherFlags": "object - Additional activity metadata and flags",
            "createdOn": "date - When the activity was created",
            "modifiedOn": "date - When the activity was last modified",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique activity identifier"
        },
        "relationships": ["users", "courses", "challenges", "conversations"],
        "business_logic": "Employee behavioral analytics and training engagement tracking",
        "query_hints": "Use for employee activity analysis, engagement metrics, training behavioral patterns. Filter by isPractice for practice vs real activities"    },
    "AGENTACTIVITIES": {
        "purpose": "AI agent performance and training task completion tracking",
        "key_fields": ["userName", "userId", "challengeAttemptNumber", "completedChallenges", "totalTask"],
        "field_schema": {
            "userName": "string - Name of the user/agent",
            "userId": "string - Reference to the user identifier",
            "challengeAttemptNumber": "number - Number of challenge attempts made",
            "completedChallenges": "number - Number of challenges successfully completed",
            "totalTask": "number - Total number of tasks assigned",
            "totalTaskCompleted": "number - Number of tasks successfully completed",
            "passRate": "number - Success rate percentage",
            "createdOn": "date - When the activity record was created",
            "modifiedOn": "date - When the activity record was last modified",
            "deleted": "boolean - true=record deleted, false=record active",
            "challengeProgress": "array - Challenge progress tracking data",
            "progress": "array - General progress tracking data",
            "lastLoginAttempt": "date - When the user last attempted to login",
            "hotStreak": "number - Current consecutive success streak",
            "_id": "ObjectId - Unique activity record identifier"
        },
        "relationships": ["users", "challenges"],
        "business_logic": "AI system performance monitoring for training delivery",
        "query_hints": "Use for AI agent analytics, system performance metrics. Filter by deleted=false for active records"    },
    "ITEMPROGRESSES": {
        "purpose": "Detailed progress tracking for individual course items",
        "key_fields": ["itemId", "courseProgressId", "status", "isActive", "startedAt"],
        "field_schema": {
            "itemId": "string - Reference to the specific course item",
            "courseProgressId": "string - Reference to the parent course progress",
            "status": "string - Progress status (not_started, in_progress, completed, etc.)",
            "isActive": "boolean - true=progress tracking active, false=inactive",
            "startedAt": "date - When the item was started",
            "attempts": "number - Number of attempts made on this item",
            "createdOn": "date - When progress tracking started",
            "modifiedOn": "date - When progress was last updated",
            "__v": "number - Version key",
            "completedAt": "date - When the item was completed (if applicable)",
            "_id": "ObjectId - Unique item progress identifier"
        },
        "relationships": ["courseitems", "courseprogresses", "useractivities"],
        "business_logic": "Granular progress monitoring within courses",
        "query_hints": "Use for detailed progress analytics, completion tracking. Filter by isActive=true for current progress, status for completion analysis"    },
    
    # Search and AI Collections
    "AISEARCHRESULTS": {
        "purpose": "AI-powered search results and query responses",
        "key_fields": ["accountId", "userId", "sessionId", "query", "answer"],
        "field_schema": {
            "accountId": "string - Reference to the account making the search",
            "userId": "string - Reference to the user making the search",
            "sessionId": "string - Search session identifier",
            "query": "string - User's search query text",
            "answer": "string - AI-generated response to the query",
            "sources": "array - Source documents and references used for the answer",
            "responseTime": "number - Time taken to generate response (in milliseconds)",
            "timestamp": "date - When the search was performed",
            "vectorStoreId": "string - Vector store used for search",
            "createdAt": "date - Record creation timestamp",
            "updatedAt": "date - Record last update timestamp",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique search result identifier"
        },
        "relationships": ["users", "accounts", "searchsessions", "documents"],
        "business_logic": "Intelligent search and knowledge retrieval",
        "query_hints": "Use for search analytics, AI interaction analysis. Filter by responseTime for performance analysis"
    },
    "SEARCHSESSIONS": {
        "purpose": "User search sessions and interaction tracking",
        "key_fields": ["userId", "sessionId", "threadId", "status", "assistanceId"],
        "field_schema": {
            "userId": "string - Reference to the user conducting the search session",
            "sessionId": "string - Unique session identifier",
            "threadId": "string - AI thread identifier for conversation continuity",
            "status": "string - Session status (active, completed, etc.)",
            "assistanceId": "string - AI assistance identifier",
            "tmpVectorStoreId": "string - Temporary vector store used for this session",
            "createdAt": "date - When the session was created",
            "lastActivity": "date - When the session was last active",
            "updatedAt": "date - When the session was last updated",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique session identifier"
        },
        "relationships": ["users", "aisearchresults"],
        "business_logic": "Search behavior and session management",
        "query_hints": "Use for search behavior analysis, session tracking. Filter by status for active sessions"    },
    
    # System Administration Collections
    "ROLES": {
        "purpose": "Role-based access control and permissions",
        "key_fields": ["name", "permissions", "accountId", "status", "createdOn"],
        "field_schema": {
            "name": "string - Role name (superadmin, agent, manager, candidate, etc.)",
            "permissions": "array - List of permissions assigned to this role",
            "accountId": "string - Reference to the account this role belongs to",
            "status": "boolean - true=role active, false=role inactive",
            "createdOn": "date - When the role was created",
            "createdBy": "string - Reference to user who created the role",
            "modifiedOn": "date - When the role was last modified",
            "deleted": "boolean - true=role deleted, false=role active",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique role identifier"
        },
        "relationships": ["users", "accounts"],
        "business_logic": "Security and access management",
        "query_hints": "Use for permission queries, role management. Filter by deleted=false and status=true for active roles"
    },
    "USERPREFERENCES": {
        "purpose": "Individual user settings and customization",
        "key_fields": ["userId", "preferences", "createdOn", "modifiedOn", "deleted"],
        "field_schema": {
            "userId": "string - Reference to the user these preferences belong to",
            "preferences": "object - User preference settings (rolePlayMode, language, etc.)",
            "createdOn": "date - When the preferences were created",
            "modifiedOn": "date - When the preferences were last modified",
            "deleted": "boolean - true=preferences deleted, false=preferences active",
            "__v": "number - Version key",
            "_id": "ObjectId - Unique preferences identifier"
        },
        "relationships": ["users"],
        "business_logic": "User experience personalization",
        "query_hints": "Use for user preference analysis, customization queries. Filter by deleted=false for active preferences"
    }
}

# Collections with NO DATA - Should be avoided in queries
EMPTY_COLLECTIONS = {
    "OTPS", "SOCRATESCONVERSATIONS", "VENDORPACKAGEITEMS", "ROLEAPLAY_ACTIVITIES",
    "RELAYLEADREFERENCESUMMARIES", "EMAILQUEUES", "LINKS", "TWILIOCALLCONVERSATIONS", 
    "SLACKUSERS", "UNANSWERDQUESTIONS", "URLSESSIONGENERALS", "GENERICPROMPTS",
    "ROLEPLAYINSTRUCTIONAUTOMOTIVES", "TEST", "TYPES", "DECKS", "EXCEPTIONROUTINGS",
    "LEADCONTACTS", "LEADFILES", "QUESTIONS", "MODULEPROGRESSES", "URLSESSIONS",
    "INSIGHTREPORTS", "VOICECLONES"  # Add common misspelling to avoid
}

# High-value collections for common academic queries
PRIORITY_COLLECTIONS = [
    "USERS", "COURSES", "COURSEASSIGNMENTS", "COURSEPROGRESSES", "DEPARTMENTS",
    "ORGANIZATIONS", "ACCOUNTS", "CHALLENGES", "CONVERSATIONS", "USERACTIVITIES"
]
