"""
FastAPI Web API for LinkedIn Blog AI Assistant
Simple API with only two endpoints: text input and file upload
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import os
import tempfile
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Import our main assistant class
from main import LinkedInBlogAIAssistant

load_dotenv()

app = FastAPI(
    title="LinkedIn Blog AI Assistant API",
    description="Transform text or files into engaging LinkedIn blog posts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize assistant globally
assistant = None

def initialize_assistant():
    """Initialize the LinkedIn Blog AI Assistant"""
    global assistant
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not all([openai_key, anthropic_key, google_key]):
        raise RuntimeError("Missing required API keys. Check your .env file.")
    
    assistant = LinkedInBlogAIAssistant(
        openai_key=openai_key,
        anthropic_key=anthropic_key,
        google_key=google_key
    )

def get_assistant():
    """Get the assistant, initializing it if needed"""
    global assistant
    if assistant is None:
        initialize_assistant()
    return assistant

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str = Field(..., description="Text content to process and convert to LinkedIn blog post")

class BlogResponse(BaseModel):
    status: str
    blog_post: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LinkedIn Blog AI Assistant API",
        "version": "1.0.0",
        "description": "Simple API with two endpoints for creating LinkedIn blog posts",
        "endpoints": {
            "health": "/health",
            "text_input": "/api/text",
            "file_upload": "/api/file",
            "documentation": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "assistant_initialized": assistant is not None
    }

@app.post("/api/text", response_model=BlogResponse)
async def process_text_input(text_input: TextInput):
    """
    Process text input and generate LinkedIn blog post
    
    Takes raw text and converts it into an engaging LinkedIn blog post using AI
    """
    try:
        # Get initialized assistant
        assistant_instance = get_assistant()
        
        # Extract information from text
        extraction_result = assistant_instance.process_text_input(text_input.text)
        
        if extraction_result["status"] != "success":
            return BlogResponse(
                status="error",
                error=extraction_result.get("error", "Text processing failed")
            )
        
        # Generate blog post
        blog_post = assistant_instance.generate_blog(extraction_result)
        
        if not blog_post:
            return BlogResponse(
                status="error",
                error="Blog generation failed"
            )
        
        return BlogResponse(
            status="success",
            blog_post=blog_post
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

@app.post("/api/file", response_model=BlogResponse)
async def process_file_upload(file: UploadFile = File(...)):
    """
    Process uploaded file and generate LinkedIn blog post
    
    Supports: PDF, images (jpg, png, gif, bmp), code files (py, js, go, etc.), 
    presentations (pptx, ppt), and text files (txt)
    """
    try:
        # Get initialized assistant
        assistant_instance = get_assistant()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Process the file
            extraction_result = assistant_instance.process_file(tmp_path)
            
            if extraction_result["status"] != "success":
                return BlogResponse(
                    status="error",
                    error=extraction_result.get("error", "File processing failed")
                )
            
            # Generate blog post
            blog_post = assistant_instance.generate_blog(extraction_result)
            
            if not blog_post:
                return BlogResponse(
                    status="error",
                    error="Blog generation failed"
                )
            
            return BlogResponse(
                status="success",
                blog_post=blog_post
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 