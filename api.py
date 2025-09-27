"""
FastAPI app with ingestion and blog generation endpoints.
- /api/ingest: Process files through ingestion pipeline
- /api/generate-blog: Generate LinkedIn blogs from files or text
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import os
import tempfile
from pathlib import Path
import shutil
import sys

# Ensure ingestion and blog_generation modules are importable when running API from project root
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INGESTION_DIR = os.path.join(BASE_DIR, "ingestion")
BLOG_GEN_DIR = os.path.join(BASE_DIR, "blog_generation")

# Add ingestion first to avoid config conflicts
if INGESTION_DIR not in sys.path:
    sys.path.insert(0, INGESTION_DIR)

# Import ingestion modules first
from ingestion.unified_processor import UnifiedProcessor

# Then add blog_generation and import its modules
if BLOG_GEN_DIR not in sys.path:
    sys.path.insert(0, BLOG_GEN_DIR)

from blog_generation.workflow import BlogGenerationWorkflow
from blog_generation.config import BlogGenerationState, ProcessingStatus

# Helper to make nested structures JSON-safe (e.g., remove bytes)
def _sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items() if k != "image_bytes"}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, (bytes, bytearray)):
        return {"bytes_len": len(obj)}
    return obj

# Pydantic models for request/response
class TextBlogRequest(BaseModel):
    text: str
    target_audience: Optional[str] = "General professional audience"
    tone: Optional[str] = "Professional and engaging"
    max_iterations: Optional[int] = 3

class BlogResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    blog_post: Optional[dict] = None
    workflow_status: Optional[str] = None
    iterations: Optional[int] = None
    quality_score: Optional[float] = None

app = FastAPI(title="LinkedIn Blog AI Assistant", version="2.0.0")

# Initialize processors
ingestion_processor = UnifiedProcessor()
blog_workflow = BlogGenerationWorkflow()

@app.post("/api/ingest")
async def ingest_any_file(file: UploadFile = File(...)):
    """Process any supported document through the ingestion pipeline and return a JSON payload."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            result = ingestion_processor.process_file(tmp_path)
            structured_data_safe = None
            if result.extracted_content and result.extracted_content.structured_data is not None:
                structured_data_safe = _sanitize_for_json(result.extracted_content.structured_data)

            payload = {
                "success": result.success,
                "error": result.error_message,
                "source_file": result.source_file,
                "content_type": result.content_type.value,
                "ai_analysis": result.ai_analysis,
                "key_insights": result.key_insights,
                "metadata": result.metadata.dict() if result.metadata else None,
                "extracted_content": {
                    "content_type": result.extracted_content.content_type.value if result.extracted_content else None,
                    "file_path": result.extracted_content.file_path if result.extracted_content else None,
                    "raw_text": result.extracted_content.raw_text[:2000] + ("..." if result.extracted_content and len(result.extracted_content.raw_text) > 2000 else "") if result.extracted_content else None,
                    "structured_data": structured_data_safe,
                    "metadata": result.extracted_content.metadata if result.extracted_content else None,
                    "processing_model": result.extracted_content.processing_model.value if result.extracted_content else None,
                    "processing_time": result.extracted_content.processing_time if result.extracted_content else None,
                } if result.extracted_content else None,
            }
            return JSONResponse(content=payload)
        finally:
            os.unlink(tmp_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/generate-blog", response_model=BlogResponse)
async def generate_blog_from_text(request: TextBlogRequest):
    """Generate a LinkedIn blog post from text input using the LangGraph workflow."""
    try:
        # Create initial state for blog generation
        initial_state = BlogGenerationState(
            source_content=request.text,
            user_requirements=f"Target audience: {request.target_audience}, Tone: {request.tone}",
            max_iterations=request.max_iterations,
            current_status=ProcessingStatus.GENERATING
        )
        
        # Run the blog generation workflow
        result_state = blog_workflow.run_workflow(initial_state)
        
        # Prepare response
        quality_score = None
        if result_state.latest_critique:
            quality_score = result_state.latest_critique.quality_score
        elif result_state.critique_history:
            quality_score = result_state.critique_history[-1].quality_score
        
        response = BlogResponse(
            success=result_state.current_status == ProcessingStatus.COMPLETED,
            workflow_status=result_state.current_status.value,
            iterations=result_state.iteration_count,
            quality_score=quality_score
        )
        
        if result_state.final_blog:
            response.blog_post = {
                "title": result_state.final_blog.title,
                "hook": result_state.final_blog.hook,
                "content": result_state.final_blog.content,
                "call_to_action": result_state.final_blog.call_to_action,
                "hashtags": result_state.final_blog.hashtags,
                "target_audience": result_state.final_blog.target_audience,
                "engagement_score": result_state.final_blog.estimated_engagement_score
            }
        
        if result_state.last_error:
            response.error = result_state.last_error
            
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)}")

@app.post("/api/generate-blog-from-file", response_model=BlogResponse)
async def generate_blog_from_file(
    file: UploadFile = File(...),
    target_audience: str = Form("General professional audience"),
    tone: str = Form("Professional and engaging"),
    max_iterations: int = Form(3)
):
    """Generate a LinkedIn blog post from an uploaded file using ingestion + blog generation."""
    try:
        # First, process the file through ingestion
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Process file through ingestion pipeline
            ingestion_result = ingestion_processor.process_file(tmp_path)
            
            if not ingestion_result.success:
                raise HTTPException(status_code=400, detail=f"Ingestion failed: {ingestion_result.error_message}")
            
            # Extract text content for blog generation
            if ingestion_result.extracted_content and ingestion_result.extracted_content.raw_text:
                input_text = ingestion_result.extracted_content.raw_text
            elif ingestion_result.ai_analysis:
                input_text = ingestion_result.ai_analysis
            else:
                raise HTTPException(status_code=400, detail="No text content extracted from file")
            
            # Create initial state for blog generation
            initial_state = BlogGenerationState(
                source_content=input_text,
                source_file_path=file.filename,
                user_requirements=f"Target audience: {target_audience}, Tone: {tone}",
                max_iterations=max_iterations,
                current_status=ProcessingStatus.GENERATING
            )
            
            # Run the blog generation workflow
            result_state = blog_workflow.run_workflow(initial_state)
            
            # Prepare response
            quality_score = None
            if result_state.latest_critique:
                quality_score = result_state.latest_critique.quality_score
            elif result_state.critique_history:
                quality_score = result_state.critique_history[-1].quality_score
            
            response = BlogResponse(
                success=result_state.current_status == ProcessingStatus.COMPLETED,
                workflow_status=result_state.current_status.value,
                iterations=result_state.iteration_count,
                quality_score=quality_score
            )
            
            if result_state.final_blog:
                response.blog_post = {
                    "title": result_state.final_blog.title,
                    "hook": result_state.final_blog.hook,
                    "content": result_state.final_blog.content,
                    "call_to_action": result_state.final_blog.call_to_action,
                    "hashtags": result_state.final_blog.hashtags,
                    "target_audience": result_state.final_blog.target_audience,
                    "engagement_score": result_state.final_blog.estimated_engagement_score,
                    "source_file": file.filename,
                    "ingestion_analysis": ingestion_result.ai_analysis
                }
            
            if result_state.last_error:
                response.error = result_state.last_error
                
            return response
            
        finally:
            os.unlink(tmp_path)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation from file failed: {str(e)}")

@app.get("/")
async def root():
    """API information and available endpoints."""
    return {
        "message": "LinkedIn Blog AI Assistant API",
        "version": "2.0.0",
        "description": "AI-powered LinkedIn blog generation with LangGraph workflow",
        "endpoints": {
            "ingest": "/api/ingest - Process files through ingestion pipeline",
            "generate_blog_text": "/api/generate-blog - Generate blog from text input",
            "generate_blog_file": "/api/generate-blog-from-file - Generate blog from uploaded file",
            "health": "/health - API health check",
            "docs": "/docs - Interactive API documentation"
        },
        "features": {
            "file_processing": "PDF, Word, PPT, Code, Text, Image",
            "blog_generation": "LangGraph-powered Generate → Critique → Refine workflow",
            "quality_scoring": "Automated quality assessment and improvement",
            "reload_support": "Force regeneration with reload parameter"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "ingestion_ready": True,
        "blog_generation_ready": True,
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 