import time
from langchain_community.document_loaders import PyPDFLoader
from typing import Dict, Any
from config import ExtractedContent, ContentType, ProcessingModel, DocumentMetadata

class PDFProcessor:
    """Process PDF files and extract content"""
    
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        """Extract text content from PDF using LangChain PyPDF loader"""
        start_time = time.time()
        
        # Load PDF using LangChain
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Extract text from all pages
        raw_text = ""
        page_contents = []
        
        for doc in documents:
            page_text = doc.page_content.strip()
            if page_text:
                raw_text += page_text + "\n\n"
                page_contents.append({
                    "page_number": len(page_contents) + 1,
                    "content": page_text,
                    "metadata": doc.metadata
                })
        
        # Structure the extracted data
        structured_data = {
            "total_pages": len(documents),
            "pages": page_contents,
            "document_metadata": documents[0].metadata if documents else {}
        }
        
        # Additional metadata
        metadata = {
            "total_pages": len(documents),
            "total_characters": len(raw_text),
            "word_count": len(raw_text.split()),
            "source": documents[0].metadata.get("source", file_path) if documents else file_path
        }
        
        processing_time = time.time() - start_time
        
        return ExtractedContent(
            content_type=ContentType.PDF,
            file_path=file_path,
            raw_text=raw_text.strip(),
            structured_data=structured_data,
            metadata=metadata,
            processing_model=ProcessingModel.GROQ_LLAMA_70B,
            processing_time=processing_time
        )
    
    @staticmethod
    def update_document_metadata(metadata: DocumentMetadata, extracted: ExtractedContent) -> DocumentMetadata:
        """Update document metadata with PDF-specific information"""
        metadata.page_count = extracted.metadata.get("total_pages", 0)
        metadata.word_count = extracted.metadata.get("word_count", 0)
        
        return metadata