"""
Simplified Blog Generation System

Autonomous blog generation workflow with:
- LangChain structured outputs
- LangGraph circular workflow
- LangSmith comprehensive tracing
"""

from .config import (
    BlogPost,
    CritiqueResult,
    BlogGenerationState,
    AggregatedBlogGenerationState,
    HumanFeedback,
    BlogQuality,
    ProcessingStatus,
    AggregationStrategy,
    Config
)

from .workflow import BlogWorkflow
from .prompts import LinkedInPrompts

__version__ = "2.0.0"

__all__ = [
    # Main workflow
    'BlogWorkflow',
    
    # Prompts
    'LinkedInPrompts',
    
    # Models
    'BlogPost',
    'CritiqueResult',
    'BlogGenerationState',
    'AggregatedBlogGenerationState',
    'HumanFeedback',
    
    # Enums
    'BlogQuality',
    'ProcessingStatus',
    'AggregationStrategy',
    
    # Config
    'Config',
]
