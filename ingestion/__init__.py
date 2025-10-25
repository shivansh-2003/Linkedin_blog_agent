"""
Simplified Content Ingestion Pipeline

A unified system for processing multiple file formats with AI-powered analysis.
Supports PDF, Word, PowerPoint, Code, Text, Markdown, and Images.
"""

from .config import (
    ContentType,
    ProcessingModel,
    ExtractedContent,
    AIInsights,
    ProcessedContent,
    AggregatedContent,
    Configuration
)

# Import AggregationStrategy from shared models (not config)
from shared.models import AggregationStrategy

from .unified_processor import UnifiedProcessor
from .multi_processor import MultiProcessor
from .format_handlers import FormatHandler
from .ai_analyzer import ContentAnalyzer

__version__ = "2.0.0"

__all__ = [
    # Main processors
    'UnifiedProcessor',
    'MultiProcessor',
    
    # Components
    'FormatHandler',
    'ContentAnalyzer',
    
    # Enums
    'ContentType',
    'ProcessingModel',
    'AggregationStrategy',
    
    # Data models
    'ExtractedContent',
    'AIInsights',
    'ProcessedContent',
    'AggregatedContent',
    'Configuration',
]

