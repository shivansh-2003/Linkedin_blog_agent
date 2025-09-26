import time
from pathlib import Path
from typing import Dict, Any
from config import ExtractedContent, ContentType, ProcessingModel, DocumentMetadata

class TextProcessor:
    """Process text files and extract content"""
    
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        """Extract content from text files"""
        start_time = time.time()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            raw_text = file.read()
        
        # Analyze text structure
        lines = raw_text.splitlines()
        paragraphs = [p.strip() for p in raw_text.split('\n\n') if p.strip()]
        
        # Detect if it's markdown
        is_markdown = Path(file_path).suffix.lower() == '.md'
        
        # Structure the extracted data
        structured_data = {
            "file_type": "markdown" if is_markdown else "plain_text",
            "line_count": len(lines),
            "paragraph_count": len(paragraphs),
            "empty_lines": len([line for line in lines if not line.strip()]),
            "paragraphs": paragraphs[:10] if len(paragraphs) > 10 else paragraphs,  # First 10 paragraphs
            "has_headers": is_markdown and any(line.strip().startswith('#') for line in lines)
        }
        
        # Additional metadata
        metadata = {
            "file_type": "markdown" if is_markdown else "text",
            "total_characters": len(raw_text),
            "word_count": len(raw_text.split()),
            "line_count": len(lines),
            "paragraph_count": len(paragraphs),
            "average_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
        processing_time = time.time() - start_time
        
        return ExtractedContent(
            content_type=ContentType.TEXT,
            file_path=file_path,
            raw_text=raw_text,
            structured_data=structured_data,
            metadata=metadata,
            processing_model=ProcessingModel.GROQ_GEMMA,
            processing_time=processing_time
        )
    
    @staticmethod
    def update_document_metadata(metadata: DocumentMetadata, extracted: ExtractedContent) -> DocumentMetadata:
        """Update document metadata with text-specific information"""
        metadata.word_count = extracted.metadata.get("word_count", 0)
        
        return metadata