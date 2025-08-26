# Text-to-MQL FastAPI Application

A comprehensive Text-to-MQL (MongoDB Query Language) application that converts natural language queries into MongoDB operations using AI agents.

## 🚀 Features

- **ReAct Agent**: Flexible, dynamic query processing with reasoning and acting capabilities
- **Structured Agent**: Predictable, deterministic workflow for consistent results
- **Vector Embeddings**: Semantic search capabilities for enhanced query understanding
- **RESTful API**: Complete FastAPI implementation with proper structure
- **Sample Data**: Generated school database with students, teachers, courses, etc.

## 📁 Project Structure

```
textToMql/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   └── database.py        # Database connection manager
│   ├── models/
│   │   └── schemas.py         # Pydantic models and schemas
│   ├── services/
│   │   ├── react_agent_service.py      # ReAct agent implementation
│   │   ├── structured_agent_service.py # Structured workflow agent
│   │   └── database_service.py         # Database operations
│   ├── controllers/
│   │   └── query_controller.py # Request/response handling
│   ├── routes/
│   │   ├── react_routes.py     # ReAct agent endpoints
│   │   ├── structured_routes.py # Structured agent endpoints
│   │   └── database_routes.py   # Database operation endpoints
│   └── utils/
│       └── data_generator.py   # Sample data generation
├── requirements.txt
├── .env
├── generate_data.py           # Data generation script
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

# Corcel API Configuration (Required for agents)
CORCEL_API_KEY=your_corcel_api_key_here
CORCEL_BASE_URL=https://api.corcel.io/v1

# Model Configuration  
DEFAULT_LLM_MODEL=corcel/llama-3.1-8b

# FastAPI Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Agent Settings
MAX_QUERY_RESULTS=100
```

**Getting a Corcel API Key:**
1. Visit [https://app.corcel.io](https://app.corcel.io)
2. Sign up for an account
3. Navigate to the API Keys section
4. Generate a new API key
5. Add the key to your `.env` file

**Available Corcel Models:**
- `corcel/llama-3.1-8b` (recommended for balanced performance)
- `corcel/llama-3.1-70b` (for complex reasoning tasks)
- `corcel/mixtral-8x7b` (for multilingual tasks)
- `corcel/gemma-7b` (for efficient processing)

### 3. Database Setup

Make sure MongoDB is running, then generate sample data:

```bash
# Generate sample data
python generate_data.py
```

### 4. Run the Application

```bash
# Start the FastAPI server
python -m app.main

# Or use uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **Application**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

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

## 🤖 Agent Types

### ReAct Agent (`/api/react/query`)
- **Best for**: Exploratory analytics, unpredictable queries, interactive dashboards
- **Characteristics**: Adapts dynamically, variable response times, maximum flexibility
- **Use Cases**: Data exploration, ad-hoc analysis, research queries

### Structured Agent (`/api/structured/query`)
- **Best for**: Production APIs, customer-facing apps, automated systems
- **Characteristics**: Fixed workflow, predictable performance, consistent results
- **Use Cases**: Production applications, automated reporting, customer interfaces

## 🔗 API Endpoints

### Agent Endpoints
```
POST /api/react/query          # ReAct agent query
POST /api/structured/query     # Structured agent query
GET  /api/react/health         # ReAct agent health check
GET  /api/structured/health    # Structured agent health check
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
GET  /                    # API information
GET  /health             # Application health check
GET  /demo-queries       # Example queries for testing
GET  /docs              # Interactive API documentation
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
# Test ReAct agent
curl -X POST "http://localhost:8000/api/react/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Find all students in Computer Science department"}'

# Test Structured agent
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
    "http://localhost:8000/api/react/query",
    json={"query": "Find students with GPA above 3.5"}
)
print(response.json())
```

## 🔧 Configuration

### Agent Selection Guidelines

**Use ReAct Agent when:**
- Building exploratory analytics tools
- Creating interactive dashboards
- Handling unpredictable query patterns
- Maximum flexibility is required

**Use Structured Agent when:**
- Building production APIs
- Creating customer-facing applications
- Needing consistent performance
- Debugging and monitoring are critical

### Performance Optimization

- **Query Caching**: Implement caching for frequently used queries
- **Result Limits**: Configure `MAX_QUERY_RESULTS` appropriately
- **Index Optimization**: Ensure proper MongoDB indexes are created
- **Connection Pooling**: Configure MongoDB connection pools for production

## 🛡️ Security Considerations

- **API Keys**: Secure your Corcel API key
- **Database Access**: Implement proper MongoDB authentication
- **Rate Limiting**: Add rate limiting for production use
- **Input Validation**: Validate all user inputs
- **CORS**: Configure CORS policies appropriately

## 🚀 Deployment

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use environment variables for all configuration
- Implement proper logging and monitoring
- Set up health checks and alerts
- Configure load balancing if needed
- Use a production ASGI server like Gunicorn with Uvicorn workers

## 📝 License

This project is for demonstration purposes. Please ensure you comply with Corcel's usage policies and any other relevant licenses.

## 🤝 Contributing

This is a demo application. For production use, consider:
- Adding comprehensive error handling
- Implementing authentication and authorization
- Adding request/response logging
- Setting up monitoring and metrics
- Adding comprehensive tests
- Optimizing for scalability

---

**Happy Querying! 🎉**
