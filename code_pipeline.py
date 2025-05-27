# code_pipeline.py

from langchain_anthropic import ChatAnthropic
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
import os
from typing import Dict, Any
from pathlib import Path

class CodePipeline:
    def __init__(self, api_key: str = None):
        """Initialize the code extraction pipeline with Anthropic"""
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.3,
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        
        self.extraction_prompt = PromptTemplate(
            input_variables=["code", "language", "filename"],
            template="""
You are an expert code analyst and technical writer. Analyze the following {language} code 
from file '{filename}' and extract insights suitable for a LinkedIn blog post.

Code:
```{language}
{code}
```

Please extract and provide:
1. **Purpose & Functionality**: What does this code do? What problem does it solve?
2. **Key Technical Concepts**: Important patterns, algorithms, or architectures used
3. **Best Practices Demonstrated**: Any notable coding practices or design patterns
4. **Innovation & Creativity**: Unique or clever solutions in the code
5. **Learning Points**: What can developers learn from this code?
6. **Business Value**: How does this code contribute to business goals?
7. **Technical Stack**: Technologies, libraries, and frameworks used
8. **Potential Improvements**: Areas for optimization or enhancement
9. **Real-world Applications**: How this code could be applied in different contexts

Format the output as a structured analysis that can be transformed into an engaging LinkedIn post.
Focus on insights that would interest and educate a professional developer audience.
"""
        )
        
        self.supported_extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.rb': 'ruby',
            '.php': 'php',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.rs': 'rust',
            '.r': 'r',
            '.css': 'css',
            '.scss': 'scss',
            '.html': 'html',
            '.sql': 'sql',
            '.sh': 'bash',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml'
        }
    
    def extract_from_code(self, file_path: str) -> Dict[str, Any]:
        """Extract information from code file"""
        try:
            # Get file extension and language
            file_ext = Path(file_path).suffix.lower()
            language = self.supported_extensions.get(file_ext, 'unknown')
            filename = Path(file_path).name
            
            # Load code file
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            # Limit code length for processing
            if len(code_content) > 10000:
                code_content = code_content[:10000] + "\n... (truncated for analysis)"
            
            # Extract information using LLM
            response = self.llm.invoke(
                self.extraction_prompt.format(
                    code=code_content,
                    language=language,
                    filename=filename
                )
            )
            
            return {
                "source_type": "code",
                "file_path": file_path,
                "language": language,
                "extracted_info": response.content,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "code",
                "file_path": file_path,
                "error": str(e),
                "status": "error"
            }
    
    def extract_from_multiple_files(self, file_paths: list) -> Dict[str, Any]:
        """Extract information from multiple code files (e.g., a project)"""
        try:
            all_extractions = []
            languages_used = set()
            
            for file_path in file_paths:
                if self.is_supported_format(file_path):
                    result = self.extract_from_code(file_path)
                    if result["status"] == "success":
                        all_extractions.append({
                            "file": Path(file_path).name,
                            "info": result["extracted_info"],
                            "language": result["language"]
                        })
                        languages_used.add(result["language"])
            
            # Synthesize information from all files
            newline = '\n'
            synthesis_prompt = f"""
Analyze the following code analysis from multiple files and create a cohesive summary 
for a LinkedIn blog post about this project:

Project Languages: {', '.join(languages_used)}

{newline.join([f"File: {ext['file']} ({ext['language']}){newline}{ext['info']}{newline}" for ext in all_extractions])}

Create a unified narrative that:
1. Describes the overall project architecture
2. Highlights the most impressive technical aspects
3. Explains the business value and use cases
4. Provides key learnings for developers
5. Suggests how readers can apply these concepts
"""
            
            response = self.llm.invoke(synthesis_prompt)
            
            return {
                "source_type": "code_project",
                "file_paths": file_paths,
                "languages": list(languages_used),
                "extracted_info": response.content,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "source_type": "code_project",
                "file_paths": file_paths,
                "error": str(e),
                "status": "error"
            }
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if the code file format is supported"""
        return Path(file_path).suffix.lower() in self.supported_extensions