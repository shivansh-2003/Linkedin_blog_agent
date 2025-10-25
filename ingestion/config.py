"""Configuration, data models, and constants for content processing"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from shared.models import AggregationStrategy


class ContentType(str, Enum):
    """Supported content types"""
    PDF = "pdf"
    WORD = "word"
    POWERPOINT = "powerpoint"
    CODE = "code"
    TEXT = "text"
    IMAGE = "image"
    MARKDOWN = "markdown"


class ProcessingModel(str, Enum):
    """AI models for content analysis"""
    PRIMARY = "llama-3.3-70b-versatile"
    FAST = "llama-3.1-8b-instant"
    FALLBACK = "gemma2-9b-it"
    VISION = "gemini-2.0-flash-exp"


class ExtractedContent(BaseModel):
    """Raw extracted content from a file"""
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    image_data: Optional[bytes] = None
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class AIInsights(BaseModel):
    """AI-generated insights from content"""
    main_topics: List[str] = Field(default_factory=list)
    key_insights: List[str] = Field(default_factory=list)
    target_audience: str = ""
    professional_context: str = ""
    linkedin_angles: List[str] = Field(default_factory=list)
    technical_depth: str = "intermediate"
    tone_suggestions: List[str] = Field(default_factory=list)


class ProcessedContent(BaseModel):
    """Complete processed content with AI analysis"""
    source_file: str
    content_type: ContentType
    raw_content: str
    insights: AIInsights
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time: float = 0.0
    model_used: str = ""
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class AggregatedContent(BaseModel):
    """Multiple files combined with unified insights"""
    sources: List[ProcessedContent]
    unified_insights: str
    cross_references: List[str]
    aggregation_strategy: AggregationStrategy
    combined_topics: List[str]
    narrative_flow: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Configuration:
    """Central configuration for the ingestion system"""
    
    # File size limits
    MAX_FILE_SIZE_MB = 50
    MAX_FILES_BATCH = 10
    
    # Supported extensions mapped to content types
    EXTENSION_MAP = {
        # Documents
        ".pdf": ContentType.PDF,
        ".docx": ContentType.WORD,
        ".doc": ContentType.WORD,
        ".pptx": ContentType.POWERPOINT,
        ".ppt": ContentType.POWERPOINT,
        
        # Text formats
        ".txt": ContentType.TEXT,
        ".md": ContentType.MARKDOWN,
        ".markdown": ContentType.MARKDOWN,
        
        # Code files
        ".py": ContentType.CODE,
        ".js": ContentType.CODE,
        ".ts": ContentType.CODE,
        ".jsx": ContentType.CODE,
        ".tsx": ContentType.CODE,
        ".java": ContentType.CODE,
        ".cpp": ContentType.CODE,
        ".c": ContentType.CODE,
        ".cs": ContentType.CODE,
        ".go": ContentType.CODE,
        ".rs": ContentType.CODE,
        ".php": ContentType.CODE,
        ".rb": ContentType.CODE,
        ".swift": ContentType.CODE,
        ".kt": ContentType.CODE,
        ".sql": ContentType.CODE,
        ".html": ContentType.CODE,
        ".css": ContentType.CODE,
        ".scss": ContentType.CODE,
        ".json": ContentType.CODE,
        ".xml": ContentType.CODE,
        ".yaml": ContentType.CODE,
        ".yml": ContentType.CODE,
        
        # Images
        ".jpg": ContentType.IMAGE,
        ".jpeg": ContentType.IMAGE,
        ".png": ContentType.IMAGE,
        ".gif": ContentType.IMAGE,
        ".bmp": ContentType.IMAGE,
        ".webp": ContentType.IMAGE,
    }
    
    # Model selection by content type
    MODEL_MAP = {
        ContentType.PDF: ProcessingModel.PRIMARY,
        ContentType.WORD: ProcessingModel.FAST,
        ContentType.POWERPOINT: ProcessingModel.PRIMARY,
        ContentType.CODE: ProcessingModel.PRIMARY,
        ContentType.TEXT: ProcessingModel.FAST,
        ContentType.MARKDOWN: ProcessingModel.FAST,
        ContentType.IMAGE: ProcessingModel.VISION,
    }
    
    # Processing timeouts (seconds)
    TIMEOUTS = {
        ContentType.PDF: 120,
        ContentType.WORD: 60,
        ContentType.POWERPOINT: 180,
        ContentType.CODE: 90,
        ContentType.TEXT: 30,
        ContentType.IMAGE: 60,
    }
    
    @classmethod
    def get_content_type(cls, file_path: str) -> ContentType:
        """Determine content type from file extension"""
        from pathlib import Path
        ext = Path(file_path).suffix.lower()
        content_type = cls.EXTENSION_MAP.get(ext)
        if not content_type:
            raise ValueError(f"Unsupported file extension: {ext}")
        return content_type
    
    @classmethod
    def get_model_for_type(cls, content_type: ContentType) -> str:
        """Get appropriate AI model for content type"""
        return cls.MODEL_MAP.get(content_type, ProcessingModel.FAST).value


# Export commonly used classes
__all__ = [
    'ContentType',
    'ProcessingModel',
    'ExtractedContent',
    'AIInsights',
    'ProcessedContent',
    'AggregatedContent',
    'Configuration',
]
