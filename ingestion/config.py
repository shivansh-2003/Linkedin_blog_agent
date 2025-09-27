import os
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum

class ContentType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    POWERPOINT = "powerpoint"
    CODE = "code"
    IMAGE = "image"
    TEXT = "text"

class ProcessingModel(str, Enum):
    GROQ_LLAMA_70B = "llama-3.3-70b-versatile"
    GROQ_LLAMA_8B = "llama-3.1-8b-instant"
    GROQ_GEMMA = "gemma2-9b-it"
    GROQ_GPT_OSS_20B = "openai/gpt-oss-20b"
    GEMINI_FLASH = "gemini-1.5-flash"

class ExtractedContent(BaseModel):
    content_type: ContentType
    file_path: str
    raw_text: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_model: ProcessingModel
    processing_time: float

class CodeAnalysis(BaseModel):
    language: str
    file_extension: str
    functions: List[str] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    imports: List[str] = Field(default_factory=list)
    summary: str
    complexity_score: Optional[int] = None
    has_syntax_errors: bool = False

class VisualAnalysis(BaseModel):
    image_type: str
    description: str
    text_content: str = ""
    chart_data: Optional[Dict[str, Any]] = None
    objects_detected: List[str] = Field(default_factory=list)

class DocumentMetadata(BaseModel):
    file_size: int
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    creation_date: Optional[str] = None
    author: Optional[str] = None

class ProcessedContent(BaseModel):
    source_file: str
    content_type: ContentType
    extracted_content: Optional[ExtractedContent] = None
    ai_analysis: str
    key_insights: List[str] = Field(default_factory=list)
    metadata: Optional[DocumentMetadata] = None
    success: bool = True
    error_message: Optional[str] = None

class Config:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # File size limits (in MB)
    MAX_FILE_SIZE = 50
    
    # Processing timeouts (in seconds)
    PROCESSING_TIMEOUT = 300
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        ".pdf": ContentType.PDF,
        ".docx": ContentType.WORD,
        ".doc": ContentType.WORD,
        ".pptx": ContentType.POWERPOINT,
        ".ppt": ContentType.POWERPOINT,
        ".txt": ContentType.TEXT,
        ".md": ContentType.TEXT,
        ".py": ContentType.CODE,
        ".js": ContentType.CODE,
        ".jsx": ContentType.CODE,
        ".ts": ContentType.CODE,
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
        ".jpg": ContentType.IMAGE,
        ".jpeg": ContentType.IMAGE,
        ".png": ContentType.IMAGE,
        ".gif": ContentType.IMAGE,
        ".bmp": ContentType.IMAGE,
        ".webp": ContentType.IMAGE
    }
    
    # Model selection based on file type
    MODEL_MAPPING = {
        ContentType.PDF: ProcessingModel.GROQ_LLAMA_70B,
        ContentType.WORD: ProcessingModel.GROQ_LLAMA_8B,
        ContentType.POWERPOINT: ProcessingModel.GROQ_LLAMA_70B,
        ContentType.CODE: ProcessingModel.GROQ_GPT_OSS_20B,
        ContentType.TEXT: ProcessingModel.GROQ_GEMMA,
        ContentType.IMAGE: ProcessingModel.GEMINI_FLASH
    }