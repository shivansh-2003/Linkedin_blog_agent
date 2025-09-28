# FastAPI REST API Documentation

## 🎯 Overview

The LinkedIn Blog AI Assistant provides a comprehensive REST API built with FastAPI that exposes all system capabilities including file ingestion, blog generation, multi-file aggregation, and conversational chat interface.

## 🏗️ API Architecture

```
┌─────────────────┐
│   FastAPI App   │ ◄── api.py (Main Application)
└─────┬───────────┘
      │
      ├── /api/ingest            # File processing endpoint
      ├── /api/generate-blog     # Text-to-blog generation  
      ├── /api/generate-blog-from-file  # File-to-blog generation
      ├── /api/aggregate         # Multi-file aggregation
      ├── /api/chat/*           # Chatbot endpoints
      ├── /health               # Health check
      ├── /docs                 # Interactive documentation
      └── /                     # API information
```

## 🚀 Quick Start

### Start the Server

```bash
# Development mode
python api.py

# Production mode with Uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4

# Server runs on: http://localhost:8000
```

### Interactive Documentation

Visit the automatically generated API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

## 📋 Core Endpoints

### 1. Health & Info Endpoints

#### GET `/health`
Check API health and status.

**Response:**
```json
{
  "status": "healthy",
  "ingestion_ready": true,
  "blog_generation_ready": true,
  "chatbot_ready": true,
  "multi_file_processing_ready": true,
  "active_sessions": 3,
  "version": "2.0.0"
}
```

#### GET `/`
Get API information and available endpoints.

**Response:**
```json
{
  "message": "LinkedIn Blog AI Assistant API",
  "version": "2.0.0",
  "description": "AI-powered LinkedIn blog generation with LangGraph workflow",
  "endpoints": {
    "ingest": "/api/ingest - Process files through ingestion pipeline",
    "generate_blog_text": "/api/generate-blog - Generate blog from text",
    // ... more endpoints
  },
  "features": {
    "file_processing": "PDF, Word, PPT, Code, Text, Image",
    "blog_generation": "LangGraph-powered workflow",
    // ... more features
  }
}
```

### 2. File Ingestion

#### POST `/api/ingest`
Process any supported file through the ingestion pipeline.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "success": true,
  "error": null,
  "source_file": "document.pdf",
  "content_type": "pdf",
  "ai_analysis": "Comprehensive analysis of the document...",
  "key_insights": [
    "Key insight 1",
    "Key insight 2",
    "Key insight 3"
  ],
  "metadata": {
    "total_pages": 15,
    "word_count": 3500,
    "processing_time": 2.34
  },
  "extracted_content": {
    "content_type": "pdf",
    "file_path": "document.pdf",
    "raw_text": "Extracted text content...",
    "structured_data": {
      "total_pages": 15,
      "pages": [...]
    },
    "processing_model": "llama-3.3-70b-versatile",
    "processing_time": 2.34
  }
}
```

**Supported File Types:**
- **Documents**: PDF, Word (.docx, .doc), PowerPoint (.pptx, .ppt)
- **Code**: Python, JavaScript, Java, C++, Go, Rust, PHP, and 15+ more
- **Text**: Plain text (.txt), Markdown (.md)
- **Images**: JPG, PNG, GIF, BMP, WebP

### 3. Blog Generation

#### POST `/api/generate-blog`
Generate LinkedIn blog post from text input.

**Request:**
```json
{
  "text": "Artificial Intelligence is transforming healthcare through predictive analytics and diagnostic assistance...",
  "target_audience": "Healthcare professionals and technology leaders",
  "tone": "Professional and informative",
  "max_iterations": 3
}
```

**Response:**
```json
{
  "success": true,
  "error": null,
  "blog_post": {
    "title": "AI Revolution in Healthcare: From Prediction to Practice",
    "hook": "What if AI could predict health issues before symptoms appear?",
    "content": "Artificial Intelligence is revolutionizing healthcare in ways we never imagined...",
    "call_to_action": "What's your experience with AI in healthcare? Share your thoughts below!",
    "hashtags": ["#HealthcareAI", "#MedicalTechnology", "#PredictiveAnalytics", "#DigitalHealth", "#Innovation"],
    "target_audience": "Healthcare professionals and technology leaders",
    "engagement_score": 8
  },
  "workflow_status": "completed",
  "iterations": 2,
  "quality_score": 8.5
}
```

#### POST `/api/generate-blog-from-file`
Generate LinkedIn blog post from uploaded file.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/generate-blog-from-file" \
  -F "file=@research_paper.pdf" \
  -F "target_audience=Data scientists and researchers" \
  -F "tone=Technical but accessible" \
  -F "max_iterations=3"
```

**Response:**
```json
{
  "success": true,
  "blog_post": {
    // Same structure as generate-blog
    "source_file": "research_paper.pdf",
    "ingestion_analysis": "Research paper analysis results..."
  },
  "workflow_status": "completed",
  "iterations": 3,
  "quality_score": 9.2
}
```

### 4. Multi-File Aggregation

#### POST `/api/aggregate`
Aggregate multiple files into a single cohesive LinkedIn post.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/aggregate" \
  -F "files=@document1.pdf" \
  -F "files=@code_example.py" \
  -F "files=@presentation.pptx" \
  -F "aggregation_strategy=synthesis" \
  -F "target_audience=Technology professionals" \
  -F "tone=Professional and engaging"
```

**Aggregation Strategies:**
- **synthesis**: Blend insights from all files into unified narrative
- **comparison**: Compare/contrast findings across files
- **sequence**: Create sequential story from multiple sources
- **timeline**: Chronological narrative from multiple sources

**Response:**
```json
{
  "success": true,
  "blog_post": {
    "title": "Comprehensive Technology Overview: Code to Insights",
    "content": "Synthesized content from multiple sources...",
    "aggregation_strategy": "synthesis",
    "source_count": 3,
    "source_types": ["pdf", "code", "powerpoint"],
    "unified_insights": [
      "Cross-source insight 1",
      "Cross-source insight 2"
    ],
    "cross_references": {
      "source_0": ["source_1", "source_2"],
      "source_1": ["source_0"]
    }
  },
  "quality_score": 8.8
}
```

## 🗨️ Chatbot API Endpoints

### Session Management

#### POST `/api/chat/start`
Start a new chat session.

**Response:**
```json
{
  "session_id": "session_1703123456",
  "current_stage": "initial",
  "message_count": 0,
  "blog_context": null,
  "created_at": "2024-12-21 10:30:45"
}
```

#### GET `/api/chat/sessions`
List all active chat sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session_1703123456",
      "created_at": "2024-12-21 10:30:45",
      "current_stage": "presenting_draft",
      "message_count": 8,
      "has_blog_context": true
    }
  ],
  "total_sessions": 1
}
```

#### DELETE `/api/chat/session/{session_id}`
Delete a specific chat session.

**Response:**
```json
{
  "success": true,
  "message": "Session session_1703123456 deleted successfully"
}
```

### Conversation

#### POST `/api/chat/message`
Send a message to the chatbot.

**Request:**
```json
{
  "message": "I want to create a LinkedIn post about machine learning best practices",
  "session_id": "session_1703123456"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Great! I'd be happy to help you create a LinkedIn post about machine learning best practices. Do you have any specific content, files, or examples you'd like me to analyze?",
  "session_id": "session_1703123456",
  "current_stage": "awaiting_input",
  "blog_context": null
}
```

#### GET `/api/chat/history/{session_id}`
Get conversation history for a session.

**Response:**
```json
{
  "session_id": "session_1703123456",
  "messages": [
    {
      "message_id": "1703123456.001",
      "message_type": "user",
      "content": "I want to create a LinkedIn post about machine learning",
      "timestamp": "2024-12-21T10:30:45",
      "metadata": {}
    },
    {
      "message_id": "1703123456.002", 
      "message_type": "assistant",
      "content": "Great! I'd be happy to help you...",
      "timestamp": "2024-12-21T10:30:46",
      "metadata": {}
    }
  ],
  "current_stage": "awaiting_input",
  "blog_context": null
}
```

### Feedback & Approval

#### POST `/api/chat/feedback`
Submit feedback on current blog draft.

**Request:**
```json
{
  "session_id": "session_1703123456",
  "feedback": "Make the post more engaging and add some statistics about ML adoption",
  "feedback_type": "content"
}
```

**Response:**
```json
{
  "success": true,
  "response": "Thanks for the feedback! I'll make the post more engaging and add statistics about ML adoption. Let me refine it for you...",
  "session_id": "session_1703123456",
  "current_stage": "refining_blog",
  "blog_context": {
    "current_draft": {...},
    "feedback_history": ["Make it more engaging..."]
  }
}
```

#### POST `/api/chat/approve`
Approve or reject current blog draft.

**Request:**
```json
{
  "session_id": "session_1703123456",
  "approved": true,
  "final_notes": "Looks perfect! Ready to publish."
}
```

**Response:**
```json
{
  "success": true,
  "response": "✅ Blog approved and finalized! Your LinkedIn post has been saved and is ready to publish. Would you like to create another post?",
  "session_id": "session_1703123456",
  "current_stage": "completed"
}
```

## 📊 Request/Response Models

### BlogRequest

```python
class BlogRequest(BaseModel):
    text: str
    target_audience: Optional[str] = "General professional audience"
    tone: Optional[str] = "Professional and engaging"
    max_iterations: Optional[int] = 3
```

### BlogResponse

```python
class BlogResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    blog_post: Optional[dict] = None
    workflow_status: Optional[str] = None
    iterations: Optional[int] = None
    quality_score: Optional[float] = None
```

### ChatMessageRequest

```python
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
```

### FeedbackRequest

```python
class FeedbackRequest(BaseModel):
    session_id: str
    feedback: str
    feedback_type: str = "general"  # general, specific, approval, rejection
```

## 🔧 Configuration

### Environment Variables

```bash
# Core API Keys (Required)
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# LangSmith Monitoring (Optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=linkedin-blog-agent

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
MAX_FILE_SIZE_MB=50
```

### CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting (Production)

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate-blog")
@limiter.limit("10/minute")  # 10 requests per minute
async def generate_blog(request: Request, blog_request: BlogRequest):
    # Implementation
```

## 🧪 Testing

### Automated Testing

```bash
# Run comprehensive API tests
python test.py

# Run with pytest
pytest test.py -v

# Test specific endpoints
pytest test.py::TestAPIEndpoints::test_generate_blog_from_text -v
```

### Manual Testing with cURL

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test blog generation
curl -X POST "http://localhost:8000/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AI is transforming business operations",
    "target_audience": "Business professionals",
    "tone": "Professional"
  }'

# Test file upload
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@document.pdf"

# Test chat session
curl -X POST "http://localhost:8000/api/chat/start"
```

### Load Testing

```python
# Using locust for load testing
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def test_health(self):
        self.client.get("/health")
    
    @task(3)
    def test_blog_generation(self):
        self.client.post("/api/generate-blog", json={
            "text": "Sample content for load testing",
            "target_audience": "Professionals"
        })

# Run: locust -f load_test.py --host=http://localhost:8000
```

## 🔒 Security

### Authentication (Production)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verify JWT token
    if not verify_jwt_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return token

@app.post("/api/generate-blog")
async def generate_blog(request: BlogRequest, token: str = Depends(verify_token)):
    # Protected endpoint
```

### Input Validation

```python
from pydantic import validator
from fastapi import File, UploadFile, HTTPException

class BlogRequest(BaseModel):
    text: str
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v) < 10:
            raise ValueError('Text must be at least 10 characters long')
        if len(v) > 50000:
            raise ValueError('Text must be less than 50,000 characters')
        return v

async def validate_file(file: UploadFile = File(...)):
    # File size validation
    if file.size > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=413, detail="File too large")
    
    # File type validation
    allowed_types = ['.pdf', '.docx', '.pptx', '.txt', '.py', '.js']
    if not any(file.filename.endswith(ext) for ext in allowed_types):
        raise HTTPException(status_code=415, detail="Unsupported file type")
    
    return file
```

### Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

## 📈 Performance Optimization

### Async Processing

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

# For CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

@app.post("/api/process-heavy-file")
async def process_heavy_file(file: UploadFile):
    # Run in thread pool
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor, 
        heavy_processing_function, 
        file
    )
    return result
```

### Caching

```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=128)
def expensive_computation(input_hash: str):
    # Expensive operation
    return result

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

async def cached_analysis(content: str):
    cache_key = f"analysis:{hash(content)}"
    cached_result = redis_client.get(cache_key)
    
    if cached_result:
        return json.loads(cached_result)
    
    result = await perform_analysis(content)
    redis_client.setex(cache_key, 3600, json.dumps(result))  # 1 hour cache
    return result
```

### Background Tasks

```python
from fastapi import BackgroundTasks

def save_analytics(session_id: str, operation: str, duration: float):
    # Save analytics to database
    pass

@app.post("/api/generate-blog")
async def generate_blog(request: BlogRequest, background_tasks: BackgroundTasks):
    start_time = time.time()
    
    # Main processing
    result = await process_blog_generation(request)
    
    # Add background task
    background_tasks.add_task(
        save_analytics, 
        "anonymous", 
        "blog_generation", 
        time.time() - start_time
    )
    
    return result
```

## 🔄 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    volumes:
      - ./logs:/app/logs
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
```

### Production Configuration

```python
# production_settings.py
import os

class ProductionConfig:
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
    
    # API Limits
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    
    # Workers
    WORKER_COUNT = int(os.getenv("WORKER_COUNT", "4"))
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: linkedin-blog-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: linkedin-blog-api
  template:
    metadata:
      labels:
        app: linkedin-blog-api
    spec:
      containers:
      - name: api
        image: linkedin-blog-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: GROQ_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: groq-api-key
        resources:
          limits:
            memory: "1Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## 📊 Monitoring & Observability

### LangSmith Integration

The API includes comprehensive LangSmith tracing for all operations:

```python
from langsmith_config import trace_step

@trace_step("api_blog_generation", "workflow")
async def generate_blog_from_text(request: BlogRequest):
    # Automatic tracing shows:
    # - Request parameters
    # - Processing time
    # - Success/failure status
    # - Error details
    # - Quality scores
```

### Custom Metrics

```python
import time
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    process_time = time.time() - start_time
    REQUEST_DURATION.observe(process_time)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/metrics")
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Logging

```python
import logging
from pythonjsonlogger import jsonlogger

# Configure structured logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    logger.info(
        "API Request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": time.time() - start_time,
            "user_agent": request.headers.get("user-agent"),
            "ip": request.client.host
        }
    )
    
    return response
```

---

**Next Steps:**
- Explore interactive documentation at `/docs`
- Test endpoints with provided examples
- See [Testing Guide](../test_guide.md) for comprehensive testing
- Check [Monitoring Guide](../monitoring.md) for observability setup