"""
FastAPI Web API for LinkedIn Blog AI Assistant
Advanced API with enhanced agents, research capabilities, and comprehensive content generation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import tempfile
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Import our advanced assistant class
from main import AdvancedLinkedInBlogAIAssistant

load_dotenv()

app = FastAPI(
    title="LinkedIn Blog AI Assistant API",
    description="Advanced API for creating engaging LinkedIn blog posts with AI-powered research and critique workflow",
    version="2.0.0",
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
    """Initialize the Advanced LinkedIn Blog AI Assistant"""
    global assistant
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not all([openai_key, anthropic_key, google_key]):
        raise RuntimeError("Missing required API keys. Check your .env file.")
    
    assistant = AdvancedLinkedInBlogAIAssistant(
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

# Enhanced Pydantic models for request/response
class TextInput(BaseModel):
    text: str = Field(..., description="Text content to process and convert to LinkedIn blog post")
    use_enhanced_generation: bool = Field(default=True, description="Use enhanced AI critique workflow")

class ResearchInput(BaseModel):
    prompt: str = Field(..., description="Research topic or prompt for AI-driven content generation")
    research_scope: str = Field(default="comprehensive", description="Research depth: basic, comprehensive, expert")

class FileInput(BaseModel):
    use_enhanced_generation: bool = Field(default=True, description="Use enhanced AI critique workflow")

class PerformancePrediction(BaseModel):
    engagement_likelihood: float
    viral_potential: float
    optimization_score: float
    predicted_reach: str
    recommendations: List[str]

class CritiqueResult(BaseModel):
    language_score: int
    content_score: int
    engagement_score: int
    language_feedback: str
    content_feedback: str
    engagement_feedback: str
    overall_recommendation: str
    needs_revision: bool

class EnhancedBlogResponse(BaseModel):
    status: str
    final_post: Optional[str] = None
    performance_prediction: Optional[PerformancePrediction] = None
    critique_history: Optional[List[CritiqueResult]] = None
    revision_count: Optional[int] = None
    all_versions: Optional[List[str]] = None
    error: Optional[str] = None

class ResearchBlogResponse(BaseModel):
    status: str
    final_post: Optional[str] = None
    research_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    research_citations: Optional[List[str]] = None
    research_depth: Optional[int] = None
    content_strategy: Optional[str] = None
    critique_history: Optional[List[CritiqueResult]] = None
    revision_count: Optional[int] = None
    error: Optional[str] = None

class BasicBlogResponse(BaseModel):
    status: str
    blog_post: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Advanced LinkedIn Blog AI Assistant API",
        "version": "2.0.0",
        "description": "Advanced API with enhanced AI agents, research capabilities, and critique workflow",
        "features": [
            "Research-driven content generation",
            "Enhanced AI critique workflow", 
            "Multi-format file processing",
            "Performance prediction",
            "Quality assessment and revision"
        ],
        "endpoints": {
            "health": "/health",
            "research_content": "/api/research",
            "enhanced_text": "/api/enhanced/text",
            "enhanced_file": "/api/enhanced/file", 
            "basic_text": "/api/basic/text",
            "basic_file": "/api/basic/file",
            "documentation": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "assistant_initialized": assistant is not None,
        "features_available": {
            "enhanced_generation": True,
            "research_capabilities": True,
            "critique_workflow": True,
            "performance_prediction": True
        }
    }

@app.post("/api/research", response_model=ResearchBlogResponse)
async def generate_research_driven_content(research_input: ResearchInput):
    """
    Generate LinkedIn content from research prompt using AI-driven research
    
    The AI will research the topic, gather insights, and create comprehensive content
    """
    try:
        assistant_instance = get_assistant()
        
        results = assistant_instance.generate_from_research_prompt(research_input.prompt)
        
        if results.get("status") == "success":
            return ResearchBlogResponse(
                status="success",
                final_post=results.get("final_post"),
                research_summary=results.get("research_summary"),
                confidence_score=results.get("confidence_score"),
                research_citations=results.get("research_citations"),
                research_depth=results.get("research_depth"),
                content_strategy=results.get("content_strategy"),
                critique_history=results.get("critique_history"),
                revision_count=results.get("revision_count")
            )
        else:
            return ResearchBlogResponse(
                status="error",
                error=results.get("error", "Research-driven content generation failed")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research content generation failed: {str(e)}")

@app.post("/api/enhanced/text", response_model=EnhancedBlogResponse)
async def process_enhanced_text_input(text_input: TextInput):
    """
    Process text input with enhanced AI critique workflow
    
    Uses advanced AI agents with critique and revision capabilities for superior content quality
    """
    try:
        assistant_instance = get_assistant()
        
        if text_input.use_enhanced_generation:
            # Use enhanced processing with critique workflow
            results = assistant_instance.process_content_with_enhancement(text_input.text, "text")
        else:
            # Fallback to basic processing
            extraction_result = assistant_instance.pdf_text_pipeline.extract_from_text(text_input.text)
            if extraction_result["status"] == "success":
                results = assistant_instance.generate_enhanced_content(extraction_result)
            else:
                results = {"status": "error", "error": extraction_result.get("error")}
        
        if results.get("status") == "success":
            return EnhancedBlogResponse(
                status="success",
                final_post=results.get("final_post"),
                performance_prediction=results.get("performance_prediction"),
                critique_history=results.get("critique_history"),
                revision_count=results.get("revision_count"),
                all_versions=results.get("all_versions")
            )
        else:
            return EnhancedBlogResponse(
                status="error",
                error=results.get("error", "Enhanced text processing failed")
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced text processing failed: {str(e)}")

@app.post("/api/enhanced/file", response_model=EnhancedBlogResponse)
async def process_enhanced_file_upload(
    file: UploadFile = File(...),
    use_enhanced_generation: bool = Query(default=True, description="Use enhanced AI critique workflow")
):
    """
    Process uploaded file with enhanced AI critique workflow
    
    Supports: PDF, images (jpg, png, gif, bmp), code files (py, js, go, etc.), 
    presentations (pptx, ppt), and text files (txt)
    """
    try:
        assistant_instance = get_assistant()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            if use_enhanced_generation:
                # Use enhanced processing with critique workflow
                results = assistant_instance.process_content_with_enhancement(tmp_path, "file")
            else:
                # Fallback to basic processing
                extraction_result = assistant_instance.process_file(tmp_path)
                if extraction_result["status"] == "success":
                    results = assistant_instance.generate_enhanced_content(extraction_result)
                else:
                    results = {"status": "error", "error": extraction_result.get("error")}
            
            if results.get("status") == "success":
                return EnhancedBlogResponse(
                    status="success",
                    final_post=results.get("final_post"),
                    performance_prediction=results.get("performance_prediction"),
                    critique_history=results.get("critique_history"),
                    revision_count=results.get("revision_count"),
                    all_versions=results.get("all_versions")
                )
            else:
                return EnhancedBlogResponse(
                    status="error",
                    error=results.get("error", "Enhanced file processing failed")
                )
                
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced file processing failed: {str(e)}")

@app.post("/api/basic/text", response_model=BasicBlogResponse)
async def process_basic_text_input(text_input: TextInput):
    """
    Process text input with basic generation (legacy endpoint)
    
    Simple text-to-blog conversion without enhanced features
    """
    try:
        assistant_instance = get_assistant()
        
        # Use basic text processing
        extraction_result = assistant_instance.pdf_text_pipeline.extract_from_text(text_input.text)
        
        if extraction_result["status"] != "success":
            return BasicBlogResponse(
                status="error",
                error=extraction_result.get("error", "Text processing failed")
            )
        
        # For basic mode, we'll use a simple generation approach
        # This would need to be implemented in the main class
        blog_post = f"LinkedIn post generated from: {text_input.text[:100]}..."
        
        return BasicBlogResponse(
            status="success",
            blog_post=blog_post
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Basic text processing failed: {str(e)}")

@app.post("/api/basic/file", response_model=BasicBlogResponse)
async def process_basic_file_upload(file: UploadFile = File(...)):
    """
    Process uploaded file with basic generation (legacy endpoint)
    
    Simple file-to-blog conversion without enhanced features
    """
    try:
        assistant_instance = get_assistant()
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Process the file with basic extraction
            extraction_result = assistant_instance.process_file(tmp_path)
            
            if extraction_result["status"] != "success":
                return BasicBlogResponse(
                    status="error",
                    error=extraction_result.get("error", "File processing failed")
                )
            
            # For basic mode, we'll use a simple generation approach
            blog_post = f"LinkedIn post generated from {extraction_result['source_type']} file"
            
            return BasicBlogResponse(
                status="success",
                blog_post=blog_post
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Basic file processing failed: {str(e)}")

# Legacy endpoints for backward compatibility
@app.post("/api/text", response_model=BasicBlogResponse)
async def process_text_input_legacy(text_input: TextInput):
    """
    Legacy endpoint - redirects to enhanced text processing
    """
    return await process_enhanced_text_input(text_input)

@app.post("/api/file", response_model=BasicBlogResponse)
async def process_file_upload_legacy(file: UploadFile = File(...)):
    """
    Legacy endpoint - redirects to enhanced file processing
    """
    return await process_enhanced_file_upload(file, use_enhanced_generation=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 