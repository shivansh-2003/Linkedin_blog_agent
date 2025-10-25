"""Main API for content processing with validation"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path for langsmith_config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langsmith_config import trace_step

from .config import (
    Configuration,
    ContentType,
    ExtractedContent,
    ProcessedContent,
    AIInsights
)
from .format_handlers import FormatHandler
from .ai_analyzer import ContentAnalyzer


class UnifiedProcessor:
    """Main entry point for all content processing"""
    
    def __init__(self):
        """Initialize processor with AI analyzer"""
        self.config = Configuration()
        self.analyzer = ContentAnalyzer()
        self.format_handler = FormatHandler()
    
    @trace_step("process_file", "workflow")
    async def process_file(
        self, 
        file_path: str,
        enable_ai: bool = True
    ) -> ProcessedContent:
        """
        Process a single file completely
        
        Args:
            file_path: Path to file to process
            enable_ai: Whether to run AI analysis (default: True)
        
        Returns:
            ProcessedContent with extraction and AI insights
        """
        
        start_time = time.time()
        
        try:
            # 1. Validate file
            self._validate_file(file_path)
            
            # 2. Detect content type
            content_type = self.config.get_content_type(file_path)
            
            # 3. Extract content
            extracted = self.format_handler.extract(file_path, content_type)
            
            # 4. Run AI analysis
            if enable_ai:
                insights = await self.analyzer.analyze(extracted, content_type)
            else:
                insights = AIInsights()
            
            # 5. Build result
            processing_time = time.time() - start_time
            
            result = ProcessedContent(
                source_file=file_path,
                content_type=content_type,
                raw_content=extracted.content,
                insights=insights,
                metadata=extracted.metadata,
                processing_time=processing_time,
                model_used=self.config.get_model_for_type(content_type),
                success=True,
                error_message=None
            )
            
            return result
            
        except Exception as e:
            # Return error result
            processing_time = time.time() - start_time
            
            return ProcessedContent(
                source_file=file_path,
                content_type=ContentType.TEXT,  # Default
                raw_content="",
                insights=AIInsights(),
                metadata={"error": str(e)},
                processing_time=processing_time,
                model_used="",
                success=False,
                error_message=str(e)
            )
    
    @trace_step("validate_file", "tool")
    def _validate_file(self, file_path: str) -> None:
        """Validate file exists, size, and format"""
        
        # Check file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check if it's a file (not directory)
        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > self.config.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File too large: {file_size_mb:.2f}MB "
                f"(max: {self.config.MAX_FILE_SIZE_MB}MB)"
            )
        
        # Check extension is supported
        ext = Path(file_path).suffix.lower()
        if ext not in self.config.EXTENSION_MAP:
            supported = ", ".join(sorted(set(self.config.EXTENSION_MAP.keys())))
            raise ValueError(
                f"Unsupported file extension: {ext}\n"
                f"Supported: {supported}"
            )
    
    def get_supported_formats(self) -> dict:
        """Get list of supported file formats by category"""
        
        formats = {}
        for ext, content_type in self.config.EXTENSION_MAP.items():
            type_name = content_type.value
            if type_name not in formats:
                formats[type_name] = []
            formats[type_name].append(ext)
        
        return formats
    
    @trace_step("validate_batch", "tool")
    def validate_batch(self, file_paths: list) -> dict:
        """Validate multiple files and return validation results"""
        
        results = {
            "valid": [],
            "invalid": [],
            "total_size_mb": 0
        }
        
        for file_path in file_paths:
            try:
                self._validate_file(file_path)
                results["valid"].append(file_path)
                results["total_size_mb"] += os.path.getsize(file_path) / (1024 * 1024)
            except Exception as e:
                results["invalid"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return results


# Export
__all__ = ['UnifiedProcessor']
