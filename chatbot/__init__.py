"""
Simplified Chatbot System

Autonomous chatbot with:
- Conversation memory with LangChain integration
- Simple intent detection
- Integration with autonomous blog workflow
- LangSmith tracing
"""

from .config import (
    ChatStage,
    MessageType,
    ChatMessage,
    BlogContext,
    ConversationState,
    ChatbotConfig,
    ResponseTemplates
)

from .memory import ConversationMemory
from .orchestrator import ChatbotOrchestrator

__version__ = "2.0.0"

__all__ = [
    # Main orchestrator
    'ChatbotOrchestrator',
    
    # Memory
    'ConversationMemory',
    
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

