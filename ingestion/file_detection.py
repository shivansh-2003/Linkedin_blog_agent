import os
from pathlib import Path
from typing import Optional, Tuple
from ingestion.config import Config, ContentType, DocumentMetadata

class FileDetector:
    """Detects file types and extracts basic metadata"""
    
    @staticmethod
    def detect_file_type(file_path: str) -> Optional[ContentType]:
        """Detect content type based on file extension"""
        extension = Path(file_path).suffix.lower()
        return Config.SUPPORTED_EXTENSIONS.get(extension)
    
    @staticmethod
    def get_file_metadata(file_path: str) -> DocumentMetadata:
        """Extract basic file metadata"""
        file_stats = os.stat(file_path)
        
        return DocumentMetadata(
            file_size=file_stats.st_size,
            creation_date=str(file_stats.st_ctime)
        )
    
    @staticmethod
    def validate_file(file_path: str) -> Tuple[bool, str]:
        """Validate file exists and is supported"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        if not FileDetector.detect_file_type(file_path):
            return False, f"Unsupported file type: {Path(file_path).suffix}"
        
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > Config.MAX_FILE_SIZE:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {Config.MAX_FILE_SIZE}MB)"
        
        return True, "File is valid"
    
    @staticmethod
    def get_language_from_extension(file_path: str) -> str:
        """Get programming language from file extension"""
        extension = Path(file_path).suffix.lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".cs": "csharp",
            ".go": "go",
            ".rs": "rust",
            ".php": "php",
            ".rb": "ruby",
            ".swift": "swift",
            ".kt": "kotlin",
            ".sql": "sql",
            ".html": "html",
            ".css": "css",
            ".scss": "scss",
            ".json": "json",
            ".xml": "xml",
            ".yaml": "yaml",
            ".yml": "yaml"
        }
        
        return language_map.get(extension, "text")