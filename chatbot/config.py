import os
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime

class ChatStage(str, Enum):
    INITIAL = "initial"
    AWAITING_INPUT = "awaiting_input"
    PROCESSING_FILE = "processing_file"
    ANALYZING_CONTENT = "analyzing_content"
    GENERATING_BLOG = "generating_blog"
    PRESENTING_DRAFT = "presenting_draft"
    AWAITING_FEEDBACK = "awaiting_feedback"
    REFINING_BLOG = "refining_blog"
    COMPLETED = "completed"
    ERROR = "error"

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FILE_UPLOAD = "file_upload"
    BLOG_DRAFT = "blog_draft"
    FEEDBACK = "feedback"

class ChatMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(datetime.now().timestamp()))
    message_type: MessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    file_path: Optional[str] = None
    blog_data: Optional[Dict[str, Any]] = None

class BlogContext(BaseModel):
    """Context about the current blog being worked on"""
    source_file_path: Optional[str] = None
    source_content: str = ""
    ai_analysis: str = ""
    key_insights: List[str] = Field(default_factory=list)
    current_draft: Optional[Dict[str, Any]] = None
    draft_history: List[Dict[str, Any]] = Field(default_factory=list)
    quality_scores: List[int] = Field(default_factory=list)
    user_requirements: str = ""
    feedback_history: List[str] = Field(default_factory=list)

class ConversationState(BaseModel):
    """Complete conversation state for the chatbot"""
    session_id: str
    current_stage: ChatStage = ChatStage.INITIAL
    messages: List[ChatMessage] = Field(default_factory=list)
    blog_context: Optional[BlogContext] = None
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    total_blogs_generated: int = 0

class UserIntent(BaseModel):
    """Detected user intent and extracted information"""
    intent_type: str
    confidence: float
    entities: Dict[str, str] = Field(default_factory=dict)
    file_path: Optional[str] = None
    feedback_type: Optional[str] = None
    specific_requests: List[str] = Field(default_factory=list)

class ChatbotConfig:
    # Memory Configuration
    MEMORY_BUFFER_SIZE = 20  # Number of messages to keep in active memory
    SESSION_TIMEOUT_HOURS = 24  # Hours before session expires
    
    # Processing Configuration
    MAX_FILE_SIZE_MB = 50
    SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.pptx', '.txt', '.md', '.py', '.js', '.jpg', '.png']
    
    # Response Configuration
    MAX_RESPONSE_LENGTH = 2000
    TYPING_DELAY = 0.5  # Simulate typing delay in seconds
    
    # Blog Generation Configuration
    MAX_REFINEMENT_ITERATIONS = 3
    AUTO_IMPROVE_THRESHOLD = 6  # Quality score below which auto-refinement triggers
    
    # Personality Configuration
    CHATBOT_NAME = "BlogBot"
    PERSONALITY_TRAITS = {
        "helpful": True,
        "professional": True,
        "encouraging": True,
        "detail_oriented": True
    }
    
    # Intent Recognition Patterns
    INTENT_PATTERNS = {
        "file_upload": [
            "process this file", "analyze this document", "here's my file",
            "upload", "file", "document", "pdf", "word"
        ],
        "start_blog": [
            "create", "write", "make", "generate", "post", "blog",
            "linkedin", "article", "content", "draft", "compose",
            "about", "regarding", "on", "topic"
        ],
        "provide_feedback": [
            "change", "improve", "modify", "different", "better",
            "more", "less", "add", "remove", "fix"
        ],
        "approve_draft": [
            "looks good", "approve", "accept", "perfect", "great",
            "publish", "done", "ready"
        ],
        "start_over": [
            "start over", "new blog", "different approach", "restart",
            "begin again", "fresh start"
        ],
        "ask_question": [
            "what", "how", "why", "when", "where", "can you", "help"
        ]
    }
    
    # Response Templates
    RESPONSE_TEMPLATES = {
        "welcome": [
            "Hello! I'm {name}, your LinkedIn blog creation assistant! 🚀",
            "I can help you transform any content into engaging LinkedIn posts.",
            "You can share text, upload files (PDF, Word, PowerPoint, code, images), or just tell me what you'd like to write about!"
        ],
        "file_received": [
            "Great! I've received your {file_type} file: {filename}",
            "Let me analyze this content for you... 🔍"
        ],
        "processing_complete": [
            "✅ Analysis complete! Here's what I found:",
            "📊 Content length: {length} characters",
            "💡 Key insights extracted: {insights_count}",
            "",
            "Now I'll generate an engaging LinkedIn post based on this content..."
        ],
        "draft_ready": [
            "🎉 Your LinkedIn blog post is ready! Here's the draft:",
            "",
            "📝 **Title:** {title}",
            "🎣 **Hook:** {hook}",
            "",
            "**Content:**",
            "{content}",
            "",
            "📢 **Call-to-Action:** {cta}",
            "🏷️ **Hashtags:** {hashtags}",
            "",
            "📈 **Quality Score:** {quality_score}/10",
            "",
            "What do you think? You can:",
            "• Ask me to make specific changes",
            "• Approve it as is",
            "• Request a completely different approach"
        ],
        "feedback_received": [
            "Got it! Let me refine the post based on your feedback...",
            "I'll focus on: {focus_areas}"
        ],
        "refinement_complete": [
            "✨ Here's your refined version:",
            "",
            "**Improvements made:**",
            "{improvements}",
            "",
            "📈 **New Quality Score:** {quality_score}/10 (was {old_score}/10)"
        ],
        "error": [
            "I encountered an issue: {error}",
            "Don't worry, let's try a different approach. You can:",
            "• Upload a different file",
            "• Provide text content directly", 
            "• Ask me for help with something specific"
        ]
    }
    
    # Conversation Flow Messages
    FLOW_MESSAGES = {
        "ask_for_input": "What would you like to create a LinkedIn post about? You can share text directly or upload a file (PDF, Word, PowerPoint, code, images).",
        "ask_for_requirements": "Any specific requirements for your LinkedIn post? (tone, audience, key points to emphasize, etc.)",
        "ask_for_feedback": "How would you like me to improve this draft? Be as specific as you'd like!",
        "session_complete": "Perfect! Your LinkedIn post is ready. Would you like to create another post or need help with anything else?",
        "clarify_intent": "I'm not sure I understand. Could you clarify what you'd like me to do? I can help with creating LinkedIn posts from files or text content."
    }