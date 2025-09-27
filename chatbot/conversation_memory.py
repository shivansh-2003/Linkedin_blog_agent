import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage, SystemMessage
from pathlib import Path

from chatbot.config import (
    ConversationState, ChatMessage, MessageType, BlogContext,
    ChatStage, ChatbotConfig
)

class ConversationMemoryManager:
    """Enhanced conversation memory with persistent storage and context awareness"""
    
    def __init__(self, session_id: str, memory_dir: str = "chatbot_sessions"):
        self.session_id = session_id
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        
        # LangChain conversation buffer memory
        self.langchain_memory = ConversationBufferWindowMemory(
            k=ChatbotConfig.MEMORY_BUFFER_SIZE,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Load or create conversation state
        self.conversation_state = self._load_or_create_state()
        
        # Initialize LangChain memory with existing messages
        self._sync_langchain_memory()
    
    def _load_or_create_state(self) -> ConversationState:
        """Load existing conversation state or create new one"""
        state_file = self.memory_dir / f"{self.session_id}.json"
        
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    state = ConversationState(**data)
                    
                    # Check if session has expired
                    if self._is_session_expired(state):
                        print(f"Session {self.session_id} expired, creating new state")
                        return self._create_new_state()
                    
                    return state
            except Exception as e:
                print(f"Error loading state: {e}, creating new state")
                return self._create_new_state()
        
        return self._create_new_state()
    
    def _create_new_state(self) -> ConversationState:
        """Create a new conversation state"""
        return ConversationState(
            session_id=self.session_id,
            current_stage=ChatStage.INITIAL
        )
    
    def _is_session_expired(self, state: ConversationState) -> bool:
        """Check if session has expired"""
        expiry_time = state.last_updated + timedelta(hours=ChatbotConfig.SESSION_TIMEOUT_HOURS)
        return datetime.now() > expiry_time
    
    def _sync_langchain_memory(self):
        """Sync conversation state with LangChain memory"""
        # Clear existing memory
        self.langchain_memory.clear()
        
        # Add recent messages to LangChain memory
        recent_messages = self.conversation_state.messages[-ChatbotConfig.MEMORY_BUFFER_SIZE:]
        
        for msg in recent_messages:
            if msg.message_type == MessageType.USER:
                self.langchain_memory.chat_memory.add_user_message(msg.content)
            elif msg.message_type == MessageType.ASSISTANT:
                self.langchain_memory.chat_memory.add_ai_message(msg.content)
    
    def add_message(self, message_type: MessageType, content: str, 
                   metadata: Dict[str, Any] = None, file_path: str = None,
                   blog_data: Dict[str, Any] = None) -> ChatMessage:
        """Add a new message to conversation memory"""
        
        message = ChatMessage(
            message_type=message_type,
            content=content,
            metadata=metadata or {},
            file_path=file_path,
            blog_data=blog_data
        )
        
        # Add to conversation state
        self.conversation_state.messages.append(message)
        self.conversation_state.last_updated = datetime.now()
        
        # Add to LangChain memory
        if message_type == MessageType.USER:
            self.langchain_memory.chat_memory.add_user_message(content)
        elif message_type == MessageType.ASSISTANT:
            self.langchain_memory.chat_memory.add_ai_message(content)
        
        # Save state
        self._save_state()
        
        return message
    
    def update_stage(self, new_stage: ChatStage):
        """Update current conversation stage"""
        self.conversation_state.current_stage = new_stage
        self.conversation_state.last_updated = datetime.now()
        self._save_state()
    
    def update_blog_context(self, blog_context: BlogContext):
        """Update blog context information"""
        self.conversation_state.blog_context = blog_context
        self.conversation_state.last_updated = datetime.now()
        self._save_state()
    
    def add_blog_draft(self, draft_data: Dict[str, Any], quality_score: int = None):
        """Add a new blog draft to context"""
        if not self.conversation_state.blog_context:
            self.conversation_state.blog_context = BlogContext()
        
        # Store current draft
        self.conversation_state.blog_context.current_draft = draft_data
        
        # Add to history
        self.conversation_state.blog_context.draft_history.append({
            **draft_data,
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score
        })
        
        # Update quality scores
        if quality_score is not None:
            self.conversation_state.blog_context.quality_scores.append(quality_score)
        
        self._save_state()
    
    def add_feedback(self, feedback: str):
        """Add user feedback to blog context"""
        if not self.conversation_state.blog_context:
            self.conversation_state.blog_context = BlogContext()
        
        self.conversation_state.blog_context.feedback_history.append(feedback)
        self._save_state()
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation"""
        state = self.conversation_state
        
        summary_parts = [
            f"Session: {state.session_id}",
            f"Stage: {state.current_stage}",
            f"Messages: {len(state.messages)}",
            f"Blogs Generated: {state.total_blogs_generated}"
        ]
        
        if state.blog_context:
            blog_info = [
                f"Current Blog: {'Yes' if state.blog_context.current_draft else 'No'}",
                f"Draft Iterations: {len(state.blog_context.draft_history)}",
                f"Feedback Items: {len(state.blog_context.feedback_history)}"
            ]
            summary_parts.extend(blog_info)
        
        return " | ".join(summary_parts)
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Get context information for LLM processing"""
        context = {
            "session_id": self.session_id,
            "current_stage": self.conversation_state.current_stage,
            "message_count": len(self.conversation_state.messages),
            "blogs_generated": self.conversation_state.total_blogs_generated
        }
        
        # Add blog context if available
        if self.conversation_state.blog_context:
            blog_ctx = self.conversation_state.blog_context
            context.update({
                "has_source_content": bool(blog_ctx.source_content),
                "has_current_draft": bool(blog_ctx.current_draft),
                "draft_iterations": len(blog_ctx.draft_history),
                "feedback_count": len(blog_ctx.feedback_history),
                "latest_quality_score": blog_ctx.quality_scores[-1] if blog_ctx.quality_scores else None
            })
        
        return context
    
    def get_recent_messages(self, count: int = 5) -> List[ChatMessage]:
        """Get recent messages from conversation"""
        return self.conversation_state.messages[-count:] if self.conversation_state.messages else []
    
    def get_blog_context(self) -> Optional[BlogContext]:
        """Get current blog context"""
        return self.conversation_state.blog_context
    
    def clear_blog_context(self):
        """Clear current blog context for new blog creation"""
        self.conversation_state.blog_context = None
        self.conversation_state.total_blogs_generated += 1
        self._save_state()
    
    def get_langchain_memory(self) -> ConversationBufferWindowMemory:
        """Get LangChain memory for use in chains"""
        return self.langchain_memory
    
    def _save_state(self):
        """Save conversation state to disk"""
        state_file = self.memory_dir / f"{self.session_id}.json"
        
        try:
            # Convert to dict and handle datetime serialization
            state_dict = self.conversation_state.dict()
            
            # Convert datetime objects to ISO format strings
            state_dict['created_at'] = self.conversation_state.created_at.isoformat()
            state_dict['last_updated'] = self.conversation_state.last_updated.isoformat()
            
            # Convert message timestamps
            for msg in state_dict['messages']:
                if isinstance(msg['timestamp'], datetime):
                    msg['timestamp'] = msg['timestamp'].isoformat()
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state_dict, f, indent=2, ensure_ascii=False)
        
        except Exception as e:
            print(f"Error saving conversation state: {e}")
    
    def export_conversation(self) -> Dict[str, Any]:
        """Export complete conversation for analysis"""
        return {
            "session_id": self.session_id,
            "created_at": self.conversation_state.created_at.isoformat(),
            "last_updated": self.conversation_state.last_updated.isoformat(),
            "total_messages": len(self.conversation_state.messages),
            "current_stage": self.conversation_state.current_stage,
            "blogs_generated": self.conversation_state.total_blogs_generated,
            "messages": [
                {
                    "type": msg.message_type,
                    "content": msg.content[:200] + "..." if len(msg.content) > 200 else msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "has_file": bool(msg.file_path),
                    "has_blog_data": bool(msg.blog_data)
                }
                for msg in self.conversation_state.messages
            ],
            "blog_context": self.get_blog_context().dict() if self.get_blog_context() else None
        }
    
    def cleanup_old_sessions(self, days_old: int = 7):
        """Clean up old session files"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        for session_file in self.memory_dir.glob("*.json"):
            try:
                if session_file.stat().st_mtime < cutoff_date.timestamp():
                    session_file.unlink()
                    print(f"Cleaned up old session: {session_file.name}")
            except Exception as e:
                print(f"Error cleaning up {session_file.name}: {e}")

class MemoryUtils:
    """Utility functions for memory management"""
    
    @staticmethod
    def create_session_id() -> str:
        """Create a unique session ID"""
        from uuid import uuid4
        return str(uuid4())[:8]
    
    @staticmethod
    def format_messages_for_display(messages: List[ChatMessage]) -> str:
        """Format messages for display"""
        formatted = []
        
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M")
            if msg.message_type == MessageType.USER:
                formatted.append(f"[{timestamp}] You: {msg.content}")
            elif msg.message_type == MessageType.ASSISTANT:
                formatted.append(f"[{timestamp}] BlogBot: {msg.content}")
            elif msg.message_type == MessageType.FILE_UPLOAD:
                formatted.append(f"[{timestamp}] File: {msg.file_path}")
        
        return "\n".join(formatted)
    
    @staticmethod
    def extract_key_points(messages: List[ChatMessage]) -> List[str]:
        """Extract key points from conversation"""
        key_points = []
        
        for msg in messages:
            if msg.message_type == MessageType.USER and len(msg.content) > 50:
                # Extract first sentence as key point
                first_sentence = msg.content.split('.')[0].strip()
                if len(first_sentence) > 20:
                    key_points.append(first_sentence)
        
        return key_points[-5:]  # Return last 5 key points