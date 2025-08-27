# Text-to-MQL FastAPI Application

A comprehensive Text-to-MQL (MongoDB Query Language) application that converts natural language queries into MongoDB operations using AI agents with support for multiple LLM providers.

## 🚀 Features

- **Structured Agent**: Predictable, deterministic workflow for consistent query generation
- **Multi-LLM Support**: Integrated support for Cohere and OpenAI models with proxy pattern
- **Smart Collection Detection**: AI-powered collection identification for query optimization
- **Query Validation**: Automatic query checking and error correction
- **RESTful API**: Complete FastAPI implementation with proper structure
- **Sample Data**: Generated school database with students, teachers, courses, etc.
- **Type Safety**: Full TypeScript-style type hints and Pydantic models

## 📁 Project Structure

```
textToMql/
├── app/
│   ├── __init__.py
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── app_constants.py    # Application constants and limits
│   │   ├── error_messages.py   # Centralized error messages
│   │   ├── prompts.py          # AI prompts for query generation
│   │   └── success_messages.py # Success message templates
│   ├── controllers/
│   │   └── query_controller.py # Request/response handling
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── database.py        # Database connection manager
│   ├── helpers/
│   │   ├── collection_helpers.py # Collection identification logic
│   │   ├── query_helpers.py      # Query processing utilities
│   │   ├── result_helpers.py     # Result formatting
│   │   ├── schema_helpers.py     # Schema analysis tools
│   │   └── workflow_helpers.py   # Workflow orchestration
│   ├── models/
│   │   └── schemas.py         # Pydantic models and schemas
│   ├── routes/
│   │   ├── database_routes.py   # Database operation endpoints
│   │   └── structured_routes.py # Structured agent endpoints
│   ├── services/
│   │   ├── database_service.py         # Database operations
│   │   ├── llm_service.py             # LLM provider abstraction
│   │   ├── structured_agent_service.py # Structured workflow agent
│   │   └── llm/
│   │       ├── __init__.py
│   │       ├── cohere_provider.py     # Cohere LLM integration
│   │       ├── openai_provider.py     # OpenAI LLM integration
│   │       └── proxy.py               # LLM provider proxy
│   └── utils/
│       └── data_generator.py   # Sample data generation
├── frontend/
│   ├── index.html             # Web interface
│   ├── script.js              # Frontend JavaScript
│   ├── style.css              # Styling
│   └── package.json           # Frontend dependencies
├── main.py                    # FastAPI application entry point
├── generate_data.py           # Data generation script
├── requirements.txt
├── .env
└── README.md
```

## 🛠️ Setup Instructions

### 1. Environment Setup

```bash
# Clone or create the project directory
cd textToMql

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Update the `.env` file with your settings:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=school_db

# LLM Provider Configuration
DEFAULT_LLM_PROVIDER=cohere  # Options: cohere, openai
DEFAULT_LLM_MODEL=command-r-plus

# Cohere Configuration (if using cohere provider)
COHERE_API_KEY=your_cohere_api_key_here

# OpenAI Configuration (if using openai provider)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# FastAPI Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Agent Settings
MAX_QUERY_RESULTS=100
DEFAULT_TEMPERATURE=0.1
```

**Getting API Keys:**

**For Cohere:**
1. Visit [https://cohere.ai](https://cohere.ai)
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Add the key to your `.env` file as `COHERE_API_KEY`

**For OpenAI:**
1. Visit [https://platform.openai.com](https://platform.openai.com)
2. Sign up for an account
3. Navigate to API Keys
4. Create a new secret key
5. Add the key to your `.env` file as `OPENAI_API_KEY`

**Available Models:**
- **Cohere**: `command-r-plus`, `command-r`, `command`
- **OpenAI**: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`

### 3. Database Setup

Make sure MongoDB is running, then generate sample data:

```bash
# Generate sample data
python generate_data.py
```

### 4. Run the Application

```bash
# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Web Interface**: http://localhost:8000 (Frontend included)

## 📊 Database Schema

The application uses a school database with the following collections:

### Collections Structure:
- **departments**: Academic departments
- **teachers**: Faculty members with specializations
- **courses**: Course offerings with descriptions
- **students**: Student records with GPAs
- **enrollments**: Student-course enrollments with grades

### Relationships:
- Students → Departments (department_id)
- Teachers → Departments (department_id)
- Courses → Departments (department_id)
- Courses → Teachers (teacher_id)
- Enrollments → Students (student_id)
- Enrollments → Courses (course_id)

## 🤖 Agent Architecture

### Structured Agent (`/api/structured/query`)
- **Best for**: Production APIs, customer-facing apps, automated systems
- **Characteristics**: Fixed workflow, predictable performance, consistent results
- **Use Cases**: Production applications, automated reporting, customer interfaces

### Key Components:
1. **Collection Identification**: AI-powered detection of relevant collections
2. **Schema Analysis**: Automatic schema inference and field mapping
3. **Query Generation**: Natural language to MQL conversion
4. **Query Validation**: Automatic syntax and logic checking
5. **Error Correction**: Self-healing query fixes
6. **Result Formatting**: Natural language response generation

### Workflow:
1. Parse user query
2. Identify relevant collections using AI
3. Retrieve schema information
4. Generate MongoDB aggregation pipeline
5. Validate and optionally fix query
6. Execute query and format results

## 🔗 API Endpoints

### Core Query Endpoint
```
POST /api/structured/query     # Main query processing endpoint
GET  /api/structured/health    # Service health check
```

### Database Endpoints
```
GET  /api/database/collections           # List all collections
GET  /api/database/schema/{collection}   # Get collection schema
GET  /api/database/search?q={term}      # Search across collections
POST /api/database/raw-query/{collection} # Execute raw MongoDB query
GET  /api/database/health               # Database health check
```

### Utility Endpoints
```
GET  /                    # API information and web interface
GET  /health             # Application health check
GET  /docs              # Interactive API documentation
GET  /redoc             # ReDoc API documentation
```

## 💬 Example Queries

### Basic Queries
```json
{
  "query": "Find all students in Computer Science department"
}
```

```json
{
  "query": "List all teachers with their specializations"
}
```

### Analytical Queries
```json
{
  "query": "What's the average GPA of students in each department?"
}
```

```json
{
  "query": "Which courses have the highest enrollment this semester?"
}
```

### Complex Queries
```json
{
  "query": "Find the top 3 students by GPA in Computer Science who are enrolled in at least 2 courses"
}
```

## 🧪 Testing the API

### Using curl:
```bash
# Test Structured agent
curl -X POST "http://localhost:8000/api/structured/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find all students in Computer Science department"}'

# Test with complex query
curl -X POST "http://localhost:8000/api/structured/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the average GPA of all students?"}'

# Get collections
curl "http://localhost:8000/api/database/collections"

# Search across collections
curl "http://localhost:8000/api/database/search?q=computer"
```

### Using Python requests:
```python
import requests

# Test query
response = requests.post(
    "http://localhost:8000/api/structured/query",
    json={"query": "Find students with GPA above 3.5"}
)
print(response.json())

# Test multiple provider configurations
# Set DEFAULT_LLM_PROVIDER=cohere in .env for Cohere
# Set DEFAULT_LLM_PROVIDER=openai in .env for OpenAI
```

### Using the Web Interface:
1. Open http://localhost:8000 in your browser
2. Enter natural language queries in the interface
3. View formatted results and generated MongoDB queries

## 🔧 Configuration

### LLM Provider Selection

The application supports multiple LLM providers through a unified proxy pattern:

**Switch between providers by setting in `.env`:**
```env
DEFAULT_LLM_PROVIDER=cohere  # or openai
```

**Provider-specific configuration:**
- **Cohere**: Set `COHERE_API_KEY` and optionally `DEFAULT_LLM_MODEL`
- **OpenAI**: Set `OPENAI_API_KEY` and optionally `OPENAI_MODEL`

### Performance Tuning

**Query Processing:**
- `DEFAULT_TEMPERATURE`: Controls randomness in LLM responses (0.0-1.0)
- `MAX_QUERY_RESULTS`: Limits result set size
- `MAX_COLLECTIONS_TO_ANALYZE`: Limits collection analysis scope

**Error Handling:**
- `MAX_RETRIES`: Number of retry attempts for failed queries
- `QUERY_TIMEOUT`: Timeout for database operations

### Advanced Features

**Smart Collection Detection:**
- Automatically identifies relevant collections from user queries
- Reduces query complexity and improves performance
- Falls back to keyword matching when AI detection fails

**Query Validation Pipeline:**
- Pre-execution syntax checking
- Automatic error detection and correction
- Post-execution result validation

## 🛡️ Security Considerations

- **API Keys**: Secure your LLM provider API keys (Cohere/OpenAI)
- **Database Access**: Implement proper MongoDB authentication
- **Rate Limiting**: Add rate limiting for production use
- **Input Validation**: All inputs are validated through Pydantic models
- **CORS**: Configure CORS policies appropriately
- **Environment Variables**: Use `.env` files and never commit API keys

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use environment variables for all configuration
- Implement proper logging and monitoring
- Set up health checks and alerts
- Configure load balancing if needed
- Use a production ASGI server like Gunicorn with Uvicorn workers
- Set up proper MongoDB indexes for performance
- Consider implementing query result caching
- Monitor LLM API usage and costs

## 📝 License

This project is for demonstration purposes. Please ensure you comply with your chosen LLM provider's usage policies (Cohere, OpenAI) and any other relevant licenses.

## 🤝 Contributing

This is a production-ready application with the following architecture principles:
- **Modular Design**: Clear separation of concerns with helpers, services, and controllers
- **Type Safety**: Full type hints and Pydantic validation
- **Error Handling**: Comprehensive error handling and recovery
- **Multi-Provider Support**: Flexible LLM provider integration
- **Extensibility**: Easy to add new providers and features

For enhancements, consider:
- Adding authentication and authorization
- Implementing query result caching
- Adding comprehensive test coverage
- Setting up monitoring and metrics
- Optimizing for higher scalability
- Adding support for additional LLM providers

---

**Happy Querying! 🎉**
