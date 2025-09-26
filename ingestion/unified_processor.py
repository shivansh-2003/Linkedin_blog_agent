from typing import Optional
from config import ProcessedContent, ContentType
from file_detection import FileDetector
from pdf_processor import PDFProcessor
from word_processor import WordProcessor
from ppt_processor import PPTProcessor
from code_processor import CodeProcessor
from image_processor import ImageProcessor
from text_processor import TextProcessor
from ai_analyzer import AIAnalyzer

class UnifiedProcessor:
    """Main orchestrator for processing different file types"""
    
    def __init__(self):
        self.ai_analyzer = AIAnalyzer()
        
        # Processor mapping
        self.processors = {
            ContentType.PDF: PDFProcessor,
            ContentType.WORD: WordProcessor,
            ContentType.POWERPOINT: PPTProcessor,
            ContentType.CODE: CodeProcessor,
            ContentType.TEXT: TextProcessor,
            ContentType.IMAGE: ImageProcessor
        }
    
    def process_file(self, file_path: str) -> ProcessedContent:
        """Process a single file and return structured result"""
        
        # Validate file
        is_valid, message = FileDetector.validate_file(file_path)
        if not is_valid:
            return ProcessedContent(
                source_file=file_path,
                content_type=ContentType.TEXT,  # Default
                extracted_content=None,
                ai_analysis=f"File validation failed: {message}",
                key_insights=[],
                metadata=None,
                success=False,
                error_message=message
            )
        
        # Detect content type
        content_type = FileDetector.detect_file_type(file_path)
        if not content_type:
            return ProcessedContent(
                source_file=file_path,
                content_type=ContentType.TEXT,
                extracted_content=None,
                ai_analysis="Unsupported file type",
                key_insights=[],
                metadata=None,
                success=False,
                error_message="Unsupported file type"
            )
        
        try:
            # Get basic metadata
            metadata = FileDetector.get_file_metadata(file_path)
            
            # Extract content using appropriate processor
            processor = self.processors.get(content_type)
            if processor is None:
                return ProcessedContent(
                    source_file=file_path,
                    content_type=content_type,
                    extracted_content=None,
                    ai_analysis="No processor available for detected content type",
                    key_insights=[],
                    metadata=metadata,
                    success=False,
                    error_message="Processor not implemented for content type"
                )
            extracted_content = processor.extract_content(file_path)
            
            # Update metadata with content-specific information
            if hasattr(processor, 'update_document_metadata'):
                metadata = processor.update_document_metadata(metadata, extracted_content)
            
            # Analyze content with AI
            ai_analysis, insights = self.ai_analyzer.analyze_content(extracted_content)
            
            return ProcessedContent(
                source_file=file_path,
                content_type=content_type,
                extracted_content=extracted_content,
                ai_analysis=ai_analysis,
                key_insights=insights,
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            return ProcessedContent(
                source_file=file_path,
                content_type=content_type,
                extracted_content=None,
                ai_analysis=f"Processing failed: {str(e)}",
                key_insights=[],
                metadata=None,
                success=False,
                error_message=str(e)
            )
    
    def get_processing_summary(self, result: ProcessedContent) -> str:
        """Get a formatted summary of processing results"""
        if not result.success:
            return f"❌ Processing failed: {result.error_message}"
        
        summary_parts = [
            f"✅ Successfully processed {result.content_type.value} file",
            f"📄 File: {result.source_file}",
        ]
        
        if result.extracted_content:
            summary_parts.extend([
                f"⏱️  Processing time: {result.extracted_content.processing_time:.2f}s",
                f"📝 Content length: {len(result.extracted_content.raw_text)} characters",
                f"🔍 Insights found: {len(result.key_insights)}",
            ])
            
            # Add content-specific details
            if result.content_type == ContentType.PDF:
                pages = result.extracted_content.metadata.get('total_pages', 0)
                summary_parts.append(f"📖 Pages: {pages}")
            
            elif result.content_type == ContentType.CODE:
                lang = result.extracted_content.metadata.get('language', 'unknown')
                funcs = result.extracted_content.metadata.get('functions_count', 0)
                summary_parts.extend([
                    f"💻 Language: {lang}",
                    f"🔧 Functions: {funcs}"
                ])
            
            elif result.content_type == ContentType.POWERPOINT:
                slides = result.extracted_content.metadata.get('total_slides', 0)
                summary_parts.append(f"🎯 Slides: {slides}")
        
        return "\n".join(summary_parts)