"""
FastAPI Web API for LinkedIn Blog AI Assistant
Provides REST endpoints for all content processing pipelines and blog generation
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import os
import tempfile
import uuid
from pathlib import Path
import shutil
from dotenv import load_dotenv

# Import our pipelines
from pdf_text_pipeline import PDFTextPipeline
from image_pipeline import ImagePipeline
from code_pipeline import CodePipeline
from presentation_pipeline import PresentationPipeline
from blogger_agent import LinkedInBloggerAgent

load_dotenv()

app = FastAPI(
    title="LinkedIn Blog AI Assistant API",
    description="Transform various content types into engaging LinkedIn blog posts",
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

# Initialize pipelines globally
pdf_pipeline = None
image_pipeline = None
code_pipeline = None
presentation_pipeline = None
blogger_agent = None

def initialize_pipelines():
    """Initialize all pipelines with API keys"""
    global pdf_pipeline, image_pipeline, code_pipeline, presentation_pipeline, blogger_agent
    
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not all([openai_key, anthropic_key, google_key]):
        raise RuntimeError("Missing required API keys. Check your .env file.")
    
    pdf_pipeline = PDFTextPipeline(api_key=openai_key)
    image_pipeline = ImagePipeline(api_key=google_key)
    code_pipeline = CodePipeline(api_key=anthropic_key)
    presentation_pipeline = PresentationPipeline(api_key=openai_key, google_api_key=google_key)
    blogger_agent = LinkedInBloggerAgent(anthropic_api_key=anthropic_key)

# Pydantic models for request/response
class TextInput(BaseModel):
    text: str = Field(..., description="Text content to process")
    
class BlogGenerationRequest(BaseModel):
    extracted_info: str = Field(..., description="Extracted information from content")
    source_type: str = Field(..., description="Type of source content")
    
class BlogRefinementRequest(BaseModel):
    current_post: str = Field(..., description="Current blog post content")
    feedback: str = Field(..., description="User feedback for refinement")
    extracted_info: str = Field(..., description="Original extracted information")
    source_type: str = Field(..., description="Type of source content")

class ExtractionResponse(BaseModel):
    status: str
    source_type: str
    extracted_info: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BlogResponse(BaseModel):
    status: str
    blog_post: Optional[str] = None
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize pipelines on startup"""
    try:
        initialize_pipelines()
        print("✅ LinkedIn Blog AI Assistant API initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize API: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "LinkedIn Blog AI Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "text_processing": "/process/text",
            "file_upload": "/process/file",
            "image_upload": "/process/image", 
            "presentation_upload": "/process/presentation",
            "code_upload": "/process/code",
            "blog_generation": "/generate/blog",
            "blog_refinement": "/refine/blog",
            "documentation": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "pipelines_initialized": all([
            pdf_pipeline is not None,
            image_pipeline is not None, 
            code_pipeline is not None,
            presentation_pipeline is not None,
            blogger_agent is not None
        ])
    }

@app.post("/process/text", response_model=ExtractionResponse)
async def process_text(text_input: TextInput):
    """Process text input and extract information for blog generation"""
    try:
        result = pdf_pipeline.extract_from_text(text_input.text)
        return ExtractionResponse(
            status=result["status"],
            source_type=result["source_type"],
            extracted_info=result.get("extracted_info"),
            error=result.get("error")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

@app.post("/process/file", response_model=ExtractionResponse)
async def process_file_upload(file: UploadFile = File(...)):
    """Process uploaded file (PDF, text, etc.) and extract information"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            file_ext = Path(file.filename).suffix.lower()
            
            if file_ext == '.pdf':
                result = pdf_pipeline.extract_from_pdf(tmp_path)
            elif file_ext == '.txt':
                result = pdf_pipeline.extract_from_text_file(tmp_path)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")
            
            return ExtractionResponse(
                status=result["status"],
                source_type=result["source_type"],
                extracted_info=result.get("extracted_info"),
                error=result.get("error"),
                metadata={"filename": file.filename, "file_size": file.size}
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.post("/process/image", response_model=ExtractionResponse)
async def process_image_upload(file: UploadFile = File(...)):
    """Process uploaded image and extract information using vision AI"""
    try:
        # Validate image file
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            result = image_pipeline.extract_from_image(tmp_path)
            
            return ExtractionResponse(
                status=result["status"],
                source_type=result["source_type"],
                extracted_info=result.get("extracted_info"),
                error=result.get("error"),
                metadata={"filename": file.filename, "file_size": file.size}
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.post("/process/presentation", response_model=ExtractionResponse)
async def process_presentation_upload(
    file: UploadFile = File(...),
    analyze_images: bool = Form(True),
    specific_slides: Optional[str] = Form(None)
):
    """Process uploaded presentation (PowerPoint, PDF) and extract information"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in ['.pptx', '.ppt', '.pdf']:
            raise HTTPException(status_code=400, detail=f"Unsupported presentation format: {file_ext}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        try:
            # Handle specific slides if provided
            if specific_slides:
                try:
                    slide_numbers = [int(x.strip()) for x in specific_slides.split(',')]
                    result = presentation_pipeline.extract_key_slides(tmp_path, slide_numbers)
                    result["source_type"] = "presentation_excerpt"
                except ValueError:
                    # If parsing fails, process all slides
                    result = presentation_pipeline.extract_from_presentation(tmp_path, analyze_images)
            else:
                result = presentation_pipeline.extract_from_presentation(tmp_path, analyze_images)
            
            return ExtractionResponse(
                status=result["status"],
                source_type=result["source_type"],
                extracted_info=result.get("extracted_info"),
                error=result.get("error"),
                metadata={
                    "filename": file.filename,
                    "file_size": file.size,
                    "total_slides": result.get("total_slides"),
                    "images_analyzed": result.get("images_analyzed"),
                    "analyze_images": analyze_images,
                    "specific_slides": specific_slides
                }
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Presentation processing failed: {str(e)}")

@app.post("/process/code", response_model=ExtractionResponse)
async def process_code_upload(file: UploadFile = File(...)):
    """Process uploaded code file and extract information"""
    try:
        file_ext = Path(file.filename).suffix.lower()
        
        # Check if it's a supported code file type
        if not code_pipeline.is_supported_format(file.filename):
            raise HTTPException(status_code=400, detail=f"Unsupported code file type: {file_ext}")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, mode='w+') as tmp_file:
            content = await file.read()
            tmp_file.write(content.decode('utf-8'))
            tmp_path = tmp_file.name
        
        try:
            result = code_pipeline.extract_from_code(tmp_path)
            
            return ExtractionResponse(
                status=result["status"],
                source_type=result["source_type"],
                extracted_info=result.get("extracted_info"),
                error=result.get("error"),
                metadata={"filename": file.filename, "file_size": file.size, "language": result.get("language")}
            )
            
        finally:
            # Clean up temporary file
            os.unlink(tmp_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Code processing failed: {str(e)}")

@app.post("/generate/blog", response_model=BlogResponse)
async def generate_blog_post(request: BlogGenerationRequest):
    """Generate initial LinkedIn blog post from extracted information"""
    try:
        # Use the fallback generation method for API (no human-in-the-loop)
        blog_post = blogger_agent._fallback_generation(
            extracted_info=request.extracted_info,
            source_type=request.source_type
        )
        
        return BlogResponse(
            status="success",
            blog_post=blog_post
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog generation failed: {str(e)}")

@app.post("/refine/blog", response_model=BlogResponse)
async def refine_blog_post(request: BlogRefinementRequest):
    """Refine existing blog post based on user feedback"""
    try:
        # Create a refined prompt
        prompt = f"""
Refine the LinkedIn blog post based on the human feedback.

Previous Post:
{request.current_post}

Human Feedback:
{request.feedback}

Original Information:
{request.extracted_info}

Please incorporate the feedback while maintaining:
- Viral potential and engagement
- Professional tone
- Clear value proposition
- Proper LinkedIn formatting

Generate the improved version of the post.
"""
        
        # Use the blogger agent's LLM directly for refinement
        from langchain_core.messages import SystemMessage, HumanMessage
        
        response = blogger_agent.llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content strategist who creates viral, engaging posts."),
            HumanMessage(content=prompt)
        ])
        
        return BlogResponse(
            status="success",
            blog_post=response.content
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blog refinement failed: {str(e)}")

@app.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported file formats for each pipeline"""
    return {
        "presentations": [".pptx", ".ppt", ".pdf"],
        "documents": [".pdf", ".txt"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
        "code": [
            ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".cpp", ".c", 
            ".cs", ".rb", ".php", ".swift", ".kt", ".rs", ".r", ".css", ".scss", 
            ".html", ".sql", ".sh", ".yaml", ".yml", ".json", ".xml"
        ]
    }

@app.get("/examples")
async def get_usage_examples():
    """Get API usage examples"""
    return {
        "text_processing": {
            "endpoint": "/process/text",
            "method": "POST",
            "example": {
                "text": "Your text content here..."
            }
        },
        "file_upload": {
            "endpoint": "/process/file",
            "method": "POST",
            "content_type": "multipart/form-data",
            "description": "Upload PDF or text file"
        },
        "presentation_upload": {
            "endpoint": "/process/presentation",
            "method": "POST", 
            "content_type": "multipart/form-data",
            "parameters": {
                "file": "presentation file (.pptx, .ppt, .pdf)",
                "analyze_images": "boolean (default: true)",
                "specific_slides": "string (optional, e.g., '1,3,5')"
            }
        },
        "blog_generation": {
            "endpoint": "/generate/blog",
            "method": "POST",
            "example": {
                "extracted_info": "Key insights from your content...",
                "source_type": "presentation"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 