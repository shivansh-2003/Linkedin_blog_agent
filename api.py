"""
FastAPI app with ingestion and blog generation endpoints.
- /api/ingest: Process files through ingestion pipeline
- /api/generate-blog: Generate LinkedIn blogs from files or text
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import tempfile
from pathlib import Path
import shutil
import sys
import uuid
import time

# Import LangSmith configuration
from langsmith_config import trace_step, verify_langsmith_setup

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

# Import chatbot modules
from chatbot.chatbot_orchastrator import ChatbotOrchestrator
from chatbot.config import ChatStage, MessageType, ChatMessage
from chatbot.conversation_memory import ConversationMemoryManager

# Import multi-file processing modules
from ingestion.multi_file_processor import MultiFileProcessor
from blog_generation.config import AggregationStrategy, AggregatedBlogGenerationState

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

# Chatbot-specific Pydantic models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    success: bool
    response: str
    session_id: str
    current_stage: str
    blog_context: Optional[dict] = None
    error: Optional[str] = None

class ChatSessionResponse(BaseModel):
    session_id: str
    current_stage: str
    message_count: int
    blog_context: Optional[dict] = None
    created_at: str

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    current_stage: str
    blog_context: Optional[dict] = None

class FeedbackRequest(BaseModel):
    session_id: str
    feedback: str
    feedback_type: str = "general"  # general, specific, approval, rejection

class ApprovalRequest(BaseModel):
    session_id: str
    approved: bool
    final_notes: Optional[str] = None

app = FastAPI(title="LinkedIn Blog AI Assistant", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize processors (these will now be traced)
ingestion_processor = UnifiedProcessor()
blog_workflow = BlogGenerationWorkflow()

# Note: ChatbotOrchestrator and ConversationMemoryManager will be created per session, not globally

# Initialize multi-file processor
multi_file_processor = MultiFileProcessor()

# Simple session storage for single-user focus
active_sessions: Dict[str, Dict[str, Any]] = {}

# Verify LangSmith setup on startup
@app.on_event("startup")
async def startup_event():
    """Verify LangSmith configuration on API startup"""
    if verify_langsmith_setup():
        print("🔍 LangSmith monitoring enabled for API endpoints")
    else:
        print("⚠️ LangSmith setup verification failed")

@app.post("/api/ingest")
@trace_step("api_ingest", "tool")
async def ingest_any_file(file: UploadFile = File(...)):
    """
    Process file through ingestion pipeline with API-level tracing
    
    This will show you:
    - API endpoint performance
    - File processing success rates
    - Response times for different file types
    - Error patterns from API usage
    """
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
@trace_step("api_blog_generation", "workflow")
async def generate_blog_from_text(request: TextBlogRequest):
    """
    Generate blog with complete workflow tracing
    
    This shows the full blog generation pipeline from API perspective
    """
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

@app.post("/api/aggregate", response_model=BlogResponse)
@trace_step("api_multi_file_aggregation", "workflow")
async def aggregate_multiple_files(
    files: List[UploadFile] = File(...),
    aggregation_strategy: str = Form("synthesis"),
    target_audience: str = Form("General professional audience"),
    tone: str = Form("Professional and engaging"),
    max_iterations: int = Form(3)
):
    """
    Aggregate multiple files into a single cohesive LinkedIn post
    
    Strategies:
    - synthesis: Blend insights from all files into unified narrative
    - comparison: Compare/contrast findings across files  
    - sequence: Create sequential story from multiple sources
    - timeline: Chronological narrative from multiple sources
    """
    try:
        if len(files) < 2:
            raise HTTPException(status_code=400, detail="At least 2 files are required for aggregation")
        
        if len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum 10 files allowed for aggregation")
        
        # Validate aggregation strategy
        try:
            strategy = AggregationStrategy(aggregation_strategy)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid aggregation strategy. Must be one of: {[s.value for s in AggregationStrategy]}"
            )
        
        # Save uploaded files temporarily
        temp_files = []
        try:
            for file in files:
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                    shutil.copyfileobj(file.file, tmp_file)
                    temp_files.append(tmp_file.name)
            
            # Process multiple files through multi-file processor
            multi_source_content = await multi_file_processor.process_multiple_files(
                temp_files, 
                strategy
            )
            
            # Create aggregated blog generation state
            initial_state = AggregatedBlogGenerationState(
                source_content="",  # Will be populated from multi_source_content
                user_requirements=f"Target audience: {target_audience}, Tone: {tone}",
                max_iterations=max_iterations,
                current_status=ProcessingStatus.GENERATING,
                multi_source_content=multi_source_content,
                aggregation_strategy=strategy
            )
            
            # Run the blog generation workflow with multi-source content
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
                    "aggregation_strategy": strategy.value,
                    "source_count": len(multi_source_content.sources),
                    "source_types": list(set(s.content_type.value for s in multi_source_content.sources)),
                    "unified_insights": multi_source_content.unified_insights[:5],  # Top 5 insights
                    "cross_references": multi_source_content.cross_references
                }
            
            if result_state.last_error:
                response.error = result_state.last_error
                
            return response
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except:
                    pass  # Ignore cleanup errors
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Multi-file aggregation failed: {str(e)}")

# ============================================================================
# CHATBOT API ENDPOINTS - Single User Session Management
# ============================================================================

@app.post("/api/chat/start", response_model=ChatSessionResponse)
@trace_step("api_chat_start", "tool")
async def start_chat_session():
    """
    Start a new chat session for LinkedIn post improvement
    
    Returns a new session ID and initializes the conversation state
    """
    try:
        # Generate simple session ID (timestamp-based for single user)
        session_id = f"session_{int(time.time())}"
        
        # Initialize session state
        session_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "current_stage": ChatStage.INITIAL.value,
            "message_count": 0,
            "blog_context": None,
            "conversation_state": None
        }
        
        # Store in active sessions
        active_sessions[session_id] = session_data
        
        return ChatSessionResponse(
            session_id=session_id,
            current_stage=ChatStage.INITIAL.value,
            message_count=0,
            blog_context=None,
            created_at=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start chat session: {str(e)}")

@app.post("/api/chat/message", response_model=ChatMessageResponse)
@trace_step("api_chat_message", "workflow")
async def send_chat_message(request: ChatMessageRequest):
    """
    Send a message to the chatbot and get a response
    
    This handles the core conversation flow for LinkedIn post improvement
    """
    try:
        session_id = request.session_id
        
        # If no session_id provided, create a new session
        if not session_id:
            session_id = f"session_{int(time.time())}"
            active_sessions[session_id] = {
                "session_id": session_id,
                "created_at": time.time(),
                "current_stage": ChatStage.INITIAL.value,
                "message_count": 0,
                "blog_context": None,
                "conversation_state": None
            }
        
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        
        # Process message through chatbot orchestrator (create per session)
        chatbot_orchestrator = ChatbotOrchestrator(session_id)
        response = await chatbot_orchestrator.process_user_input(request.message)
        
        # Update session data
        session_data["message_count"] += 1
        session_data["current_stage"] = chatbot_orchestrator.current_stage.value
        
        # Get blog context if available
        blog_context = None
        memory_blog_context = chatbot_orchestrator.memory.get_blog_context()
        if memory_blog_context:
            blog_context = {
                "source_content": memory_blog_context.source_content,
                "ai_analysis": memory_blog_context.ai_analysis,
                "key_insights": memory_blog_context.key_insights,
                "current_draft": memory_blog_context.current_draft,
                "user_requirements": memory_blog_context.user_requirements,
                "feedback_history": memory_blog_context.feedback_history
            }
            session_data["blog_context"] = blog_context
        
        return ChatMessageResponse(
            success=True,
            response=response,
            session_id=session_id,
            current_stage=chatbot_orchestrator.current_stage.value,
            blog_context=blog_context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat message processing failed: {str(e)}")

@app.get("/api/chat/history/{session_id}", response_model=ChatHistoryResponse)
@trace_step("api_chat_history", "tool")
async def get_chat_history(session_id: str):
    """
    Get the conversation history for a specific session
    """
    try:
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        
        # Get conversation history from memory manager (create per session)
        memory_manager = ConversationMemoryManager(session_id)
        conversation_state = memory_manager.get_conversation_state(session_id)
        
        messages = []
        if conversation_state and conversation_state.messages:
            for msg in conversation_state.messages:
                messages.append({
                    "message_id": msg.message_id,
                    "message_type": msg.message_type.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "metadata": msg.metadata
                })
        
        return ChatHistoryResponse(
            session_id=session_id,
            messages=messages,
            current_stage=session_data["current_stage"],
            blog_context=session_data.get("blog_context")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")

@app.post("/api/chat/feedback", response_model=ChatMessageResponse)
@trace_step("api_chat_feedback", "workflow")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on the current blog draft for improvement
    """
    try:
        session_id = request.session_id
        
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        
        # Process feedback through chatbot (create per session)
        chatbot_orchestrator = ChatbotOrchestrator(session_id)
        feedback_message = f"User feedback ({request.feedback_type}): {request.feedback}"
        response = await chatbot_orchestrator.process_user_input(feedback_message)
        
        # Update session data
        session_data["message_count"] += 1
        session_data["current_stage"] = chatbot_orchestrator.current_stage.value
        
        # Update blog context
        blog_context = None
        memory_blog_context = chatbot_orchestrator.memory.get_blog_context()
        if memory_blog_context:
            blog_context = {
                "source_content": memory_blog_context.source_content,
                "ai_analysis": memory_blog_context.ai_analysis,
                "key_insights": memory_blog_context.key_insights,
                "current_draft": memory_blog_context.current_draft,
                "user_requirements": memory_blog_context.user_requirements,
                "feedback_history": memory_blog_context.feedback_history
            }
            session_data["blog_context"] = blog_context
        
        return ChatMessageResponse(
            success=True,
            response=response,
            session_id=session_id,
            current_stage=chatbot_orchestrator.current_stage.value,
            blog_context=blog_context
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback processing failed: {str(e)}")

@app.post("/api/chat/approve", response_model=ChatMessageResponse)
@trace_step("api_chat_approve", "workflow")
async def approve_blog_draft(request: ApprovalRequest):
    """
    Approve or reject the current blog draft
    """
    try:
        session_id = request.session_id
        
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data = active_sessions[session_id]
        
        # Process approval/rejection (create per session)
        chatbot_orchestrator = ChatbotOrchestrator(session_id)
        if request.approved:
            approval_message = f"APPROVE: {request.final_notes or 'Blog draft approved'}"
        else:
            approval_message = f"REJECT: {request.final_notes or 'Blog draft needs more work'}"
        
        response = await chatbot_orchestrator.process_user_input(approval_message)
        
        # Update session data
        session_data["message_count"] += 1
        session_data["current_stage"] = chatbot_orchestrator.current_stage.value
        
        # Update blog context
        blog_context = None
        memory_blog_context = chatbot_orchestrator.memory.get_blog_context()
        if memory_blog_context:
            blog_context = {
                "source_content": memory_blog_context.source_content,
                "ai_analysis": memory_blog_context.ai_analysis,
                "key_insights": memory_blog_context.key_insights,
                "current_draft": memory_blog_context.current_draft,
                "user_requirements": memory_blog_context.user_requirements,
                "feedback_history": memory_blog_context.feedback_history
            }
            session_data["blog_context"] = blog_context
        
        return ChatMessageResponse(
            success=True,
            response=response,
            session_id=session_id,
            current_stage=chatbot_orchestrator.current_stage.value,
            blog_context=blog_context
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Approval processing failed: {str(e)}")

@app.delete("/api/chat/session/{session_id}")
@trace_step("api_chat_delete", "tool")
async def delete_chat_session(session_id: str):
    """
    Delete a chat session and clean up resources
    """
    try:
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove from active sessions
        del active_sessions[session_id]
        
        # Clean up memory manager session
        try:
            memory_manager = ConversationMemoryManager(session_id)
            memory_manager.cleanup_session(session_id)
        except:
            pass  # Ignore cleanup errors
        
        return {"success": True, "message": f"Session {session_id} deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@app.get("/api/chat/sessions")
@trace_step("api_chat_sessions", "tool")
async def list_chat_sessions():
    """
    List all active chat sessions (for single-user management)
    """
    try:
        sessions = []
        for session_id, session_data in active_sessions.items():
            sessions.append({
                "session_id": session_id,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session_data["created_at"])),
                "current_stage": session_data["current_stage"],
                "message_count": session_data["message_count"],
                "has_blog_context": session_data["blog_context"] is not None
            })
        
        return {
            "sessions": sessions,
            "total_sessions": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

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
            "aggregate_files": "/api/aggregate - Aggregate multiple files into cohesive LinkedIn post",
            "chat_start": "/api/chat/start - Start new chat session",
            "chat_message": "/api/chat/message - Send message to chatbot",
            "chat_history": "/api/chat/history/{session_id} - Get conversation history",
            "chat_feedback": "/api/chat/feedback - Submit feedback on blog draft",
            "chat_approve": "/api/chat/approve - Approve/reject blog draft",
            "chat_sessions": "/api/chat/sessions - List active sessions",
            "chat_delete": "/api/chat/session/{session_id} - Delete session",
            "health": "/health - API health check",
            "docs": "/docs - Interactive API documentation"
        },
        "features": {
            "file_processing": "PDF, Word, PPT, Code, Text, Image",
            "blog_generation": "LangGraph-powered Generate → Critique → Refine workflow",
            "multi_file_aggregation": "Synthesize insights from multiple sources (synthesis, comparison, sequence, timeline)",
            "quality_scoring": "Automated quality assessment and improvement",
            "chatbot": "Single-user conversational interface for LinkedIn post improvement",
            "session_management": "Simple session-based conversation history",
            "human_in_loop": "Interactive feedback and approval workflow",
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
        "chatbot_ready": True,
        "multi_file_processing_ready": True,
        "active_sessions": len(active_sessions),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True) 