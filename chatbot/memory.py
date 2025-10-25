"""
Conversation memory management with LangChain integration.
Handles persistent storage and conversation history.
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage

from .config import (
    ConversationState,
    ChatMessage,
    MessageType,
    BlogContext,
    ChatStage,
    ChatbotConfig
)


class ConversationMemory:
    """
    Manages conversation state with LangChain memory and persistent storage.
    """
    
    def __init__(self, session_id: str = None):
        """
        Initialize conversation memory.
        
        Args:
            session_id: Optional session ID. If not provided, creates new session.
        """
        self.session_id = session_id or self._generate_session_id()
        self.memory_dir = Path(ChatbotConfig.MEMORY_DIR)
        self.memory_dir.mkdir(exist_ok=True)
        
        # LangChain conversation buffer memory
        self.langchain_memory = ConversationBufferWindowMemory(
            k=ChatbotConfig.MEMORY_BUFFER_SIZE,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Load or create conversation state
        self.state = self._load_or_create_state()
        
        # Sync LangChain memory with existing messages
        self._sync_langchain_memory()
    
    # ===== SESSION MANAGEMENT =====
    
    @staticmethod
    def _generate_session_id() -> str:
        """Generate unique session ID"""
        return f"session_{uuid.uuid4().hex[:12]}"
    
    def _get_state_file(self) -> Path:
        """Get file path for session state"""
        return self.memory_dir / f"{self.session_id}.json"
    
    def _load_or_create_state(self) -> ConversationState:
        """Load existing state or create new one"""
        state_file = self._get_state_file()
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state = ConversationState(**data)
                    
                    # Check expiration
                    if self._is_expired(state):
                        print(f"⚠️  Session {self.session_id} expired, creating new")
                        return self._create_new_state()
                    
                    print(f"✅ Loaded session: {self.session_id}")
                    return state
                    
            except Exception as e:
                print(f"⚠️  Error loading state: {e}, creating new")
                return self._create_new_state()
        
        return self._create_new_state()
    
    def _create_new_state(self) -> ConversationState:
        """Create new conversation state"""
        return ConversationState(
            session_id=self.session_id,
            current_stage=ChatStage.CONVERSING
        )
    
    def _is_expired(self, state: ConversationState) -> bool:
        """Check if session has expired"""
        expiry_time = state.last_updated + timedelta(
            hours=ChatbotConfig.SESSION_TIMEOUT_HOURS
        )
        return datetime.now() > expiry_time
    
    def _save_state(self):
        """Persist conversation state to disk"""
        state_file = self._get_state_file()
        
        # Update last_updated timestamp
        self.state.last_updated = datetime.now()
        
        # Convert to dict with datetime serialization
        state_dict = self.state.model_dump()
        
        # Custom datetime serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state_dict, f, indent=2, ensure_ascii=False, default=serialize_datetime)
    
    # ===== MESSAGE MANAGEMENT =====
    
    def add_message(
        self,
        message_type: MessageType,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> ChatMessage:
        """
        Add message to conversation.
        
        Args:
            message_type: Type of message (user/assistant/system)
            content: Message content
            metadata: Optional metadata
            
        Returns:
            Created ChatMessage
        """
        message = ChatMessage(
            message_type=message_type,
            content=content,
            metadata=metadata or {}
        )
        
        # Add to state
        self.state.messages.append(message)
        
        # Add to LangChain memory
        if message_type == MessageType.USER:
            self.langchain_memory.chat_memory.add_user_message(content)
        elif message_type == MessageType.ASSISTANT:
            self.langchain_memory.chat_memory.add_ai_message(content)
        
        # Save state
        self._save_state()
        
        return message
    
    def add_user_message(self, content: str, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Convenience method for user messages"""
        return self.add_message(MessageType.USER, content, metadata)
    
    def add_assistant_message(self, content: str, metadata: Dict[str, Any] = None) -> ChatMessage:
        """Convenience method for assistant messages"""
        return self.add_message(MessageType.ASSISTANT, content, metadata)
    
    def get_recent_messages(self, count: int = 10) -> List[ChatMessage]:
        """Get recent messages"""
        return self.state.messages[-count:]
    
    def get_conversation_summary(self) -> str:
        """Get text summary of recent conversation"""
        recent = self.get_recent_messages(5)
        summary_lines = []
        
        for msg in recent:
            prefix = "User" if msg.message_type == MessageType.USER else "Assistant"
            summary_lines.append(f"{prefix}: {msg.content[:100]}...")
        
        return "\n".join(summary_lines)
    
    # ===== STAGE MANAGEMENT =====
    
    def update_stage(self, new_stage: ChatStage):
        """Update conversation stage"""
        old_stage = self.state.current_stage
        self.state.current_stage = new_stage
        self.state.last_updated = datetime.now()
        self._save_state()
        
        print(f"📍 Stage: {old_stage.value} → {new_stage.value}")
    
    def get_current_stage(self) -> ChatStage:
        """Get current conversation stage"""
        return self.state.current_stage
    
    # ===== BLOG CONTEXT MANAGEMENT =====
    
    def create_blog_context(
        self,
        source_content: str,
        source_type: str = "text",
        source_path: Optional[str] = None,
        content_insights: List[str] = None,
        user_requirements: str = ""
    ) -> BlogContext:
        """
        Create new blog context.
        
        Args:
            source_content: Raw content to generate blog from
            source_type: "file" or "text"
            source_path: File path if source is file
            content_insights: Insights from ingestion system
            user_requirements: User's specific requirements
            
        Returns:
            Created BlogContext
        """
        blog_context = BlogContext(
            source_type=source_type,
            source_path=source_path,
            source_content=source_content,
            content_insights=content_insights or [],
            user_requirements=user_requirements
        )
        
        self.state.blog_context = blog_context
        self._save_state()
        
        return blog_context
    
    def update_blog_context(self, **updates):
        """Update blog context fields"""
        if not self.state.blog_context:
            self.state.blog_context = BlogContext()
        
        for key, value in updates.items():
            if hasattr(self.state.blog_context, key):
                setattr(self.state.blog_context, key, value)
        
        self.state.blog_context.last_updated = datetime.now()
        self._save_state()
    
    def add_blog_version(
        self,
        blog_post: Dict[str, Any],
        critique: Dict[str, Any] = None,
        quality_score: int = None
    ):
        """Add a new blog version to history"""
        if not self.state.blog_context:
            self.state.blog_context = BlogContext()
        
        # Update current blog
        self.state.blog_context.current_blog = blog_post
        self.state.blog_context.current_critique = critique
        
        # Add to history
        version = {
            "blog": blog_post,
            "critique": critique,
            "quality_score": quality_score,
            "timestamp": datetime.now().isoformat()
        }
        self.state.blog_context.blog_versions.append(version)
        
        # Track quality scores
        if quality_score:
            self.state.blog_context.quality_scores.append(quality_score)
        
        # Increment iterations
        self.state.blog_context.workflow_iterations += 1
        
        self._save_state()
    
    def add_feedback(self, feedback: str):
        """Add user feedback to blog context"""
        if not self.state.blog_context:
            return
        
        self.state.blog_context.feedback_history.append(feedback)
        self._save_state()
    
    def get_blog_context(self) -> Optional[BlogContext]:
        """Get current blog context"""
        return self.state.blog_context
    
    def clear_blog_context(self):
        """Clear blog context (start fresh)"""
        self.state.blog_context = None
        self._save_state()
    
    # ===== LANGCHAIN MEMORY SYNC =====
    
    def _sync_langchain_memory(self):
        """Sync conversation state with LangChain memory"""
        # Clear existing
        self.langchain_memory.clear()
        
        # Add recent messages
        recent = self.state.messages[-ChatbotConfig.MEMORY_BUFFER_SIZE:]
        
        for msg in recent:
            if msg.message_type == MessageType.USER:
                self.langchain_memory.chat_memory.add_user_message(msg.content)
            elif msg.message_type == MessageType.ASSISTANT:
                self.langchain_memory.chat_memory.add_ai_message(msg.content)
    
    def get_langchain_memory(self) -> ConversationBufferWindowMemory:
        """Get LangChain memory for use in chains"""
        return self.langchain_memory
    
    # ===== SESSION UTILITIES =====
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        return {
            "session_id": self.session_id,
            "current_stage": self.state.current_stage.value,
            "message_count": len(self.state.messages),
            "blogs_completed": self.state.blogs_completed,
            "has_active_blog": self.state.blog_context is not None,
            "created_at": self.state.created_at.isoformat(),
            "last_updated": self.state.last_updated.isoformat()
        }
    
    def complete_blog(self):
        """Mark current blog as completed"""
        self.state.blogs_completed += 1
        self.clear_blog_context()
        self.update_stage(ChatStage.COMPLETED)
    
    @staticmethod
    def list_sessions(memory_dir: str = None) -> List[str]:
        """List all session IDs"""
        dir_path = Path(memory_dir or ChatbotConfig.MEMORY_DIR)
        if not dir_path.exists():
            return []
        
        return [f.stem for f in dir_path.glob("session_*.json")]
    
    @staticmethod
    def delete_session(session_id: str, memory_dir: str = None):
        """Delete a session"""
        dir_path = Path(memory_dir or ChatbotConfig.MEMORY_DIR)
        state_file = dir_path / f"{session_id}.json"
        
        if state_file.exists():
            state_file.unlink()
            print(f"🗑️  Deleted session: {session_id}")


# Export
__all__ = ['ConversationMemory']

