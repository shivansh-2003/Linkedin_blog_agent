# pdf_text_pipeline.py

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from typing import Dict, Any

class PDFTextPipeline:
    def __init__(self, api_key: str = None):
        """Initialize the PDF/Text extraction pipeline with OpenAI"""
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=api_key or os.getenv("OPENAI_API_KEY")
        )
        
        self.extraction_prompt = PromptTemplate(
            input_variables=["content", "source_type"],
            template="""
You are an expert content analyzer. Extract key information from the following {source_type} content 
that would be valuable for creating a LinkedIn blog post.

Content:
{content}

Please extract and organize:
1. Main Topic/Theme
2. Key Points and Insights (bullet points)
3. Interesting Statistics or Facts
4. Potential Hook or Attention Grabber
5. Relevant Examples or Case Studies
6. Actionable Takeaways
7. Technical Details (if applicable)

Format the output in a structured way that can be easily used to generate a LinkedIn blog post.
Focus on extracting information that would resonate with a professional audience.
"""
        )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
    
    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract information from PDF file"""
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Combine chunks (limiting to first 5 for efficiency)
            combined_content = "\n\n".join([chunk.page_content for chunk in chunks[:5]])
            
            # Extract information using LLM
            response = self.llm.invoke(
                self.extraction_prompt.format(
                    content=combined_content,
                    source_type="PDF document"
                )
            )
            
            return {
                "source_type": "pdf",
                "file_path": pdf_path,
                "extracted_info": response.content,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "pdf",
                "file_path": pdf_path,
                "error": str(e),
                "status": "error"
            }
    
    def extract_from_text(self, text_content: str) -> Dict[str, Any]:
        """Extract information from text input"""
        try:
            # Direct text processing
            response = self.llm.invoke(
                self.extraction_prompt.format(
                    content=text_content,
                    source_type="text input"
                )
            )
            
            return {
                "source_type": "text",
                "extracted_info": response.content,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "text",
                "error": str(e),
                "status": "error"
            }
    
    def extract_from_text_file(self, file_path: str) -> Dict[str, Any]:
        """Extract information from text file"""
        try:
            # Load text file
            loader = TextLoader(file_path)
            documents = loader.load()
            
            # Combine content
            content = "\n".join([doc.page_content for doc in documents])
            
            # Extract using the text method
            return self.extract_from_text(content)
            
        except Exception as e:
            return {
                "source_type": "text_file",
                "file_path": file_path,
                "error": str(e),
                "status": "error"
            }