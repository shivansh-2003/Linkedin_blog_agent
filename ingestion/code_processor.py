import time
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ingestion.config import ExtractedContent, ContentType, ProcessingModel, CodeAnalysis
from ingestion.file_detection import FileDetector

class CodeProcessor:
    """Generic code processor using LangChain and configurable language analyzers"""
    
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        """Extract code content using LangChain and analyze structure with AST"""
        start_time = time.time()
        
        # Use LangChain TextLoader for consistent document handling
        loader = TextLoader(file_path, encoding='utf-8')
        documents = loader.load()
        raw_text = documents[0].page_content if documents else ""
        
        # Get language and file info
        language = FileDetector.get_language_from_extension(file_path)
        file_extension = Path(file_path).suffix.lower()
        
        # Use LangChain text splitter for code
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_text(raw_text)
        
        # Analyze code structure using generic language-agnostic approach
        code_analysis = CodeProcessor._analyze_code_structure(raw_text, language, file_path)
        
        # Structure the extracted data
        structured_data = {
            "language": language,
            "file_extension": file_extension,
            "analysis": code_analysis.dict(),
            "chunks": chunks[:5],  # First 5 chunks for context
            "total_chunks": len(chunks),
            "line_count": len(raw_text.splitlines()),
            "has_syntax_errors": code_analysis.has_syntax_errors
        }
        
        # Additional metadata
        metadata = {
            "language": language,
            "total_characters": len(raw_text),
            "line_count": len(raw_text.splitlines()),
            "word_count": len(raw_text.split()),
            "functions_count": len(code_analysis.functions),
            "classes_count": len(code_analysis.classes),
            "imports_count": len(code_analysis.imports),
            "chunks_count": len(chunks),
            "source": documents[0].metadata.get("source", file_path) if documents else file_path
        }
        
        processing_time = time.time() - start_time
        
        return ExtractedContent(
            content_type=ContentType.CODE,
            file_path=file_path,
            raw_text=raw_text,
            structured_data=structured_data,
            metadata=metadata,
            processing_model=ProcessingModel.GROQ_GPT_OSS_20B,
            processing_time=processing_time
        )
    
    
    @staticmethod
    def _analyze_code_structure(code: str, language: str, file_path: str) -> CodeAnalysis:
        """Generic code structure analysis - language detection handled elsewhere"""
        functions = []
        classes = []
        imports = []
        has_syntax_errors = False
        
        try:
            # Try AST parsing if available for the language
            tree = ast.parse(code)
            functions, classes, imports = CodeProcessor._extract_with_ast(tree)
        except (SyntaxError, Exception) as e:
            has_syntax_errors = True
            # Fallback to generic pattern matching for any language
            functions, classes, imports = CodeProcessor._extract_generic_patterns(code)
        
        # Generate summary
        summary = f"{language.title()} code with {len(functions)} functions, {len(classes)} classes, and {len(imports)} imports"
        if has_syntax_errors:
            summary += " (syntax errors detected)"
        
        return CodeAnalysis(
            language=language,
            file_extension=f".{language}" if language != "text" else ".txt",
            functions=functions,
            classes=classes,
            imports=imports,
            summary=summary,
            has_syntax_errors=has_syntax_errors
        )
    
    @staticmethod
    def _extract_with_ast(tree: ast.AST) -> Tuple[List[str], List[str], List[str]]:
        """Generic AST extraction for supported languages"""
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(f"import {alias.name}")
                else:  # ImportFrom
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"from {module} import {alias.name}")
        
        return functions, classes, imports
    
    @staticmethod
    def _extract_generic_patterns(code: str) -> Tuple[List[str], List[str], List[str]]:
        """Generic pattern-based extraction for any programming language"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        
        # Generic patterns that work across most languages
        generic_patterns = {
            'functions': [
                r'function\s+(\w+)',           # function name()
                r'def\s+(\w+)',                # def name()
                r'(\w+)\s*\([^)]*\)\s*{',      # name() {
                r'func\s+(\w+)',               # func name()
                r'fn\s+(\w+)',                 # fn name()
                r'(\w+)\s*=\s*.*=>',           # name = () =>
            ],
            'classes': [
                r'class\s+(\w+)',              # class Name
                r'struct\s+(\w+)',             # struct Name
                r'interface\s+(\w+)',          # interface Name
                r'type\s+(\w+)\s+struct',      # type Name struct
                r'trait\s+(\w+)',              # trait Name
            ],
            'imports': [
                r'import\s+([^;]+)',           # import something
                r'from\s+([^\s]+)\s+import',   # from module import
                r'#include\s*[<"]([^>"]+)[>"]', # #include <file>
                r'using\s+([^;]+);',           # using namespace;
                r'use\s+([^;]+);',             # use module;
                r'require\([\'"]([^\'"]+)[\'"]', # require('module')
            ]
        }
        
        # Extract functions
        for pattern in generic_patterns['functions']:
            for line in lines:
                matches = re.findall(pattern, line, re.IGNORECASE)
                functions.extend(matches)
        
        # Extract classes/structs/interfaces
        for pattern in generic_patterns['classes']:
            for line in lines:
                matches = re.findall(pattern, line, re.IGNORECASE)
                classes.extend(matches)
        
        # Extract imports/includes
        for pattern in generic_patterns['imports']:
            for line in lines:
                matches = re.findall(pattern, line, re.IGNORECASE)
                imports.extend(matches)
        
        # Remove duplicates and filter out empty strings
        functions = list(dict.fromkeys([f for f in functions if f.strip()]))
        classes = list(dict.fromkeys([c for c in classes if c.strip()]))
        imports = list(dict.fromkeys([i for i in imports if i.strip()]))
        
        return functions, classes, imports