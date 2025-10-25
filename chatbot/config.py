"""
Chatbot configuration and data models.
Pure Pydantic models with no business logic.
"""

import os
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ===== ENUMS =====

class ChatStage(str, Enum):
    """Simplified 4-stage conversation model"""
    CONVERSING = "conversing"              # General conversation, questions
    AWAITING_CONTENT = "awaiting_content"  # Waiting for file or text input
    REVIEWING_DRAFT = "reviewing_draft"    # User reviewing generated blog
    COMPLETED = "completed"                 # Session completed


class MessageType(str, Enum):
    """Message types in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ===== MESSAGE MODELS =====

class ChatMessage(BaseModel):
    """Single message in conversation"""
    message_id: str = Field(default_factory=lambda: f"msg_{datetime.now().timestamp()}")
    message_type: MessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_1234567890.123",
                "message_type": "user",
                "content": "Can you make this more technical?",
                "timestamp": "2025-01-15T10:30:00",
                "metadata": {"intent": "refine", "focus": "technical"}
            }
        }


# ===== BLOG CONTEXT =====

class BlogContext(BaseModel):
    """Context about the current blog being worked on"""
    
    # Source information
    source_type: str = ""  # "file" or "text"
    source_path: Optional[str] = None
    source_content: str = ""
    
    # AI Analysis from ingestion
    content_insights: List[str] = Field(default_factory=list)
    ai_analysis: str = ""
    
    # Current blog state
    current_blog: Optional[Dict[str, Any]] = None  # Current BlogPost as dict
    current_critique: Optional[Dict[str, Any]] = None  # Current CritiqueResult as dict
    
    # History
    blog_versions: List[Dict[str, Any]] = Field(default_factory=list)
    quality_scores: List[int] = Field(default_factory=list)
    
    # User interaction
    user_requirements: str = ""
    feedback_history: List[str] = Field(default_factory=list)
    
    # Workflow metadata
    workflow_iterations: int = 0
    last_updated: datetime = Field(default_factory=datetime.now)


# ===== CONVERSATION STATE =====

class ConversationState(BaseModel):
    """Complete conversation state for persistence"""
    
    session_id: str
    current_stage: ChatStage = ChatStage.CONVERSING
    
    # Messages
    messages: List[ChatMessage] = Field(default_factory=list)
    
    # Blog context (optional, only when working on a blog)
    blog_context: Optional[BlogContext] = None
    
    # User preferences
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    
    # Session metadata
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    blogs_completed: int = 0
    
    class Config:
        arbitrary_types_allowed = True


# ===== CONFIGURATION =====

class ChatbotConfig:
    """Chatbot configuration constants"""
    
    # Identity
    CHATBOT_NAME = "LinkedIn Blog Assistant"
    CHATBOT_VERSION = "2.0"
    
    # Memory Configuration
    MEMORY_BUFFER_SIZE = 20  # Number of messages in active memory
    SESSION_TIMEOUT_HOURS = 24
    MEMORY_DIR = "chatbot_sessions"
    
    # File Processing
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_EXTENSIONS = [
        '.pdf', '.docx', '.pptx', '.txt', '.md', 
        '.py', '.js', '.java', '.cpp', '.html'
    ]
    
    # Response Configuration
    MAX_RESPONSE_LENGTH = 2000
    
    # Blog Generation Defaults
    DEFAULT_MAX_ITERATIONS = 3
    DEFAULT_TARGET_AUDIENCE = "Professional network"
    DEFAULT_TONE = "Professional and engaging"


# ===== RESPONSE TEMPLATES =====

class ResponseTemplates:
    """Pre-defined response templates for consistency"""
    
    WELCOME = """
👋 Hi! I'm your LinkedIn Blog Assistant.

I can help you create engaging LinkedIn posts from:
📄 Documents (PDF, Word, PowerPoint)
💻 Code files  
📝 Text content

**To get started:**
- Upload a file or paste your content
- I'll automatically generate a professional LinkedIn post
- You can refine it with feedback until it's perfect

What would you like to create a post about?
"""
    
    FILE_RECEIVED = """
✅ File received: {filename}

Processing your {file_type} file...
This will take about {estimated_time} seconds.
"""
    
    BLOG_GENERATED = """
🎉 Your LinkedIn post is ready!

**Quality Score:** {quality_score}/10
**Status:** {quality_level}

{blog_preview}

**What would you like to do?**
- Refine it: "Make it more technical" or "Add more examples"
- Approve it: "Looks good!" or "Perfect!"
- Start over: "Let's try something else"
"""
    
    REFINEMENT_COMPLETE = """
✨ Updated version ready!

**Previous Score:** {old_score}/10 → **New Score:** {new_score}/10

{blog_preview}

Happy with this version?
"""
    
    COMPLETION = """
🎊 Great! Your LinkedIn post is ready to publish.

**Final Quality Score:** {quality_score}/10

You can copy this and post it directly to LinkedIn, or I can help you create another post.
"""
    
    ERROR = """
❌ Oops! Something went wrong: {error}

Let's try again. What would you like to do?
"""


# Export all
__all__ = [
    # Enums
    'ChatStage',
    'MessageType',
    
    # Models
    'ChatMessage',
    'BlogContext',
    'ConversationState',
    
    # Config
    'ChatbotConfig',
    'ResponseTemplates',
]
