"""
FastAPI Web API for Advanced LinkedIn Blog AI Assistant
Enhanced API with research-driven content generation and AI critique workflow
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
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
    title="Advanced LinkedIn Blog AI Assistant API",
    description="Transform text, files, or research prompts into engaging LinkedIn blog posts with AI critique and performance prediction",
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
    research_scope: str = Field(default="comprehensive", description="Research depth: basic, comprehensive, or expert")

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
    blog_post: Optional[str] = None
    performance_prediction: Optional[PerformancePrediction] = None
    critique_results: Optional[List[CritiqueResult]] = None
    revision_count: Optional[int] = None
    research_summary: Optional[str] = None
    confidence_score: Optional[float] = None
    research_citations: Optional[List[str]] = None
    error: Optional[str] = None

class BlogResponse(BaseModel):
    status: str
    blog_post: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Advanced LinkedIn Blog AI Assistant API",
        "version": "2.0.0",
        "description": "Enhanced API with research-driven content generation, AI critique workflow, and performance prediction",
        "features": [
            "Research-driven content generation",
            "Enhanced AI critique workflow", 
            "Performance prediction and optimization",
            "Multi-format file processing",
            "Quality assessment and revision"
        ],
        "endpoints": {
            "health": "/health",
            "text_input": "/api/text",
            "file_upload": "/api/file",
            "research_generation": "/api/research",
            "enhanced_text": "/api/enhanced/text",
            "enhanced_file": "/api/enhanced/file",
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

@app.post("/api/research", response_model=EnhancedBlogResponse)
async def generate_research_driven_content(research_input: ResearchInput):
    """
    Generate LinkedIn content from research prompt using AI research capabilities
    
    The AI will research the topic, synthesize findings, and create engaging content
    """
    try:
        # Get initialized assistant
        assistant_instance = get_assistant()
        
        # Generate research-driven content
        results = assistant_instance.generate_from_research_prompt(research_input.prompt)
        
        if results.get("status") != "success":
            return EnhancedBlogResponse(
                status="error",
                error=results.get("error", "Research-driven content generation failed")
            )
        
        # Convert critique results to Pydantic models
        critique_results = []
        if results.get("critique_history"):
            for critique in results["critique_history"]:
                critique_results.append(CritiqueResult(
                    language_score=critique.language_score,
                    content_score=critique.content_score,
                    engagement_score=critique.engagement_score,
                    language_feedback=critique.language_feedback,
                    content_feedback=critique.content_feedback,
                    engagement_feedback=critique.engagement_feedback,
                    overall_recommendation=critique.overall_recommendation,
                    needs_revision=critique.needs_revision
                ))
        
        return EnhancedBlogResponse(
            status="success",
            blog_post=results.get("final_post"),
            research_summary=results.get("research_summary"),
            confidence_score=results.get("confidence_score"),
            research_citations=results.get("research_citations"),
            critique_results=critique_results,
            revision_count=results.get("revision_count")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Research-driven content generation failed: {str(e)}")

@app.post("/api/enhanced/text", response_model=EnhancedBlogResponse)
async def process_enhanced_text_input(text_input: TextInput):
    """
    Process text input with enhanced AI critique workflow
    
    Uses advanced AI agents with critique, revision, and performance prediction
    """
    try:
        # Get initialized assistant
        assistant_instance = get_assistant()
        
        # Process content with enhancement
        results = assistant_instance.process_content_with_enhancement(text_input.text, "text")
        
        if results.get("status") != "success":
            return EnhancedBlogResponse(
                status="error",
                error=results.get("error", "Enhanced text processing failed")
            )
        
        # Convert performance prediction to Pydantic model
        performance_prediction = None
        if results.get("performance_prediction"):
            perf = results["performance_prediction"]
            performance_prediction = PerformancePrediction(
                engagement_likelihood=perf.get("engagement_likelihood", 0),
                viral_potential=perf.get("viral_potential", 0),
                optimization_score=perf.get("optimization_score", 0),
                predicted_reach=perf.get("predicted_reach", "Unknown"),
                recommendations=perf.get("recommendations", [])
            )
        
        # Convert critique results to Pydantic models
        critique_results = []
        if results.get("critique_history"):
            for critique in results["critique_history"]:
                critique_results.append(CritiqueResult(
                    language_score=critique.language_score,
                    content_score=critique.content_score,
                    engagement_score=critique.engagement_score,
                    language_feedback=critique.language_feedback,
                    content_feedback=critique.content_feedback,
                    engagement_feedback=critique.engagement_feedback,
                    overall_recommendation=critique.overall_recommendation,
                    needs_revision=critique.needs_revision
                ))
        
        return EnhancedBlogResponse(
            status="success",
            blog_post=results.get("final_post"),
            performance_prediction=performance_prediction,
            critique_results=critique_results,
            revision_count=results.get("revision_count")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced text processing failed: {str(e)}")

@app.post("/api/enhanced/file", response_model=EnhancedBlogResponse)
async def process_enhanced_file_upload(file: UploadFile = File(...)):
    """
    Process uploaded file with enhanced AI critique workflow
    
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
            # Process the file with enhancement
            results = assistant_instance.process_content_with_enhancement(tmp_path, "file")
            
            if results.get("status") != "success":
                return EnhancedBlogResponse(
                    status="error",
                    error=results.get("error", "Enhanced file processing failed")
                )
            
            # Convert performance prediction to Pydantic model
            performance_prediction = None
            if results.get("performance_prediction"):
                perf = results["performance_prediction"]
                performance_prediction = PerformancePrediction(
                    engagement_likelihood=perf.get("engagement_likelihood", 0),
                    viral_potential=perf.get("viral_potential", 0),
                    optimization_score=perf.get("optimization_score", 0),
                    predicted_reach=perf.get("predicted_reach", "Unknown"),
                    recommendations=perf.get("recommendations", [])
                )
            
            # Convert critique results to Pydantic models
            critique_results = []
            if results.get("critique_history"):
                for critique in results["critique_history"]:
                    critique_results.append(CritiqueResult(
                        language_score=critique.language_score,
                        content_score=critique.content_score,
                        engagement_score=critique.engagement_score,
                        language_feedback=critique.language_feedback,
                        content_feedback=critique.content_feedback,
                        engagement_feedback=critique.engagement_feedback,
                        overall_recommendation=critique.overall_recommendation,
                        needs_revision=critique.needs_revision
                    ))
            
            return EnhancedBlogResponse(
                status="success",
                blog_post=results.get("final_post"),
                performance_prediction=performance_prediction,
                critique_results=critique_results,
                revision_count=results.get("revision_count")
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced file processing failed: {str(e)}")

@app.post("/api/text", response_model=BlogResponse)
async def process_text_input(text_input: TextInput):
    """
    Process text input and generate LinkedIn blog post (Legacy endpoint)
    
    Takes raw text and converts it into an engaging LinkedIn blog post using AI
    """
    try:
        # Get initialized assistant
        assistant_instance = get_assistant()
        
        # Use enhanced processing by default
        results = assistant_instance.process_content_with_enhancement(text_input.text, "text")
        
        if results.get("status") != "success":
            return BlogResponse(
                status="error",
                error=results.get("error", "Text processing failed")
            )
        
        return BlogResponse(
            status="success",
            blog_post=results.get("final_post")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

@app.post("/api/file", response_model=BlogResponse)
async def process_file_upload(file: UploadFile = File(...)):
    """
    Process uploaded file and generate LinkedIn blog post (Legacy endpoint)
    
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
            # Use enhanced processing by default
            results = assistant_instance.process_content_with_enhancement(tmp_path, "file")
            
            if results.get("status") != "success":
                return BlogResponse(
                    status="error",
                    error=results.get("error", "File processing failed")
                )
            
            return BlogResponse(
                status="success",
                blog_post=results.get("final_post")
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 