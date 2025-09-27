import time
from langchain_community.document_loaders import Docx2txtLoader
from typing import Dict, Any
from ingestion.config import ExtractedContent, ContentType, ProcessingModel, DocumentMetadata

class WordProcessor:
    """Process Word documents and extract content"""
    
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        """Extract text content from Word document using LangChain"""
        start_time = time.time()
        
        # Load Word document using LangChain
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        
        # Extract text content
        raw_text = ""
        for doc in documents:
            raw_text += doc.page_content + "\n"
        
        # Structure the extracted data
        structured_data = {
            "document_sections": [doc.page_content for doc in documents],
            "metadata": documents[0].metadata if documents else {}
        }
        
        # Additional metadata
        metadata = {
            "total_characters": len(raw_text),
            "word_count": len(raw_text.split()),
            "paragraph_count": len([p for p in raw_text.split('\n') if p.strip()]),
            "source": documents[0].metadata.get("source", file_path) if documents else file_path
        }
        
        processing_time = time.time() - start_time
        
        return ExtractedContent(
            content_type=ContentType.WORD,
            file_path=file_path,
            raw_text=raw_text.strip(),
            structured_data=structured_data,
            metadata=metadata,
            processing_model=ProcessingModel.GROQ_LLAMA_8B,
            processing_time=processing_time
        )
    
    @staticmethod
    def update_document_metadata(metadata: DocumentMetadata, extracted: ExtractedContent) -> DocumentMetadata:
        """Update document metadata with Word-specific information"""
        metadata.word_count = extracted.metadata.get("word_count", 0)
        
        return metadata