import time
import re
from pathlib import Path
from typing import Dict, Any, List
from config import ExtractedContent, ContentType, ProcessingModel, CodeAnalysis
from file_detection import FileDetector

class CodeProcessor:
    """Process code files and extract structural information"""
    
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        """Extract code content and analyze structure"""
        start_time = time.time()
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            raw_text = file.read()
        
        # Get language
        language = FileDetector.get_language_from_extension(file_path)
        file_extension = Path(file_path).suffix.lower()
        
        # Analyze code structure
        code_analysis = CodeProcessor._analyze_code_structure(raw_text, language)
        
        # Structure the extracted data
        structured_data = {
            "language": language,
            "file_extension": file_extension,
            "analysis": code_analysis.dict(),
            "line_count": len(raw_text.splitlines()),
            "has_syntax_errors": False  # Basic assumption, could be enhanced
        }
        
        # Additional metadata
        metadata = {
            "language": language,
            "total_characters": len(raw_text),
            "line_count": len(raw_text.splitlines()),
            "word_count": len(raw_text.split()),
            "functions_count": len(code_analysis.functions),
            "classes_count": len(code_analysis.classes),
            "imports_count": len(code_analysis.imports)
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
    def _analyze_code_structure(code: str, language: str) -> CodeAnalysis:
        """Analyze code structure based on language"""
        functions = []
        classes = []
        imports = []
        
        lines = code.split('\n')
        
        if language == "python":
            functions = CodeProcessor._extract_python_functions(lines)
            classes = CodeProcessor._extract_python_classes(lines)
            imports = CodeProcessor._extract_python_imports(lines)
        elif language in ["javascript", "typescript"]:
            functions = CodeProcessor._extract_js_functions(lines)
            classes = CodeProcessor._extract_js_classes(lines)
            imports = CodeProcessor._extract_js_imports(lines)
        elif language == "java":
            functions = CodeProcessor._extract_java_methods(lines)
            classes = CodeProcessor._extract_java_classes(lines)
            imports = CodeProcessor._extract_java_imports(lines)
        
        # Generate summary
        summary = f"{language.title()} code with {len(functions)} functions, {len(classes)} classes, and {len(imports)} imports"
        
        return CodeAnalysis(
            language=language,
            file_extension=f".{language}" if language != "text" else ".txt",
            functions=functions,
            classes=classes,
            imports=imports,
            summary=summary
        )
    
    @staticmethod
    def _extract_python_functions(lines: List[str]) -> List[str]:
        """Extract Python function names"""
        functions = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('def '):
                match = re.match(r'def\s+(\w+)', stripped)
                if match:
                    functions.append(match.group(1))
        return functions
    
    @staticmethod
    def _extract_python_classes(lines: List[str]) -> List[str]:
        """Extract Python class names"""
        classes = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class '):
                match = re.match(r'class\s+(\w+)', stripped)
                if match:
                    classes.append(match.group(1))
        return classes
    
    @staticmethod
    def _extract_python_imports(lines: List[str]) -> List[str]:
        """Extract Python import statements"""
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')):
                imports.append(stripped)
        return imports
    
    @staticmethod
    def _extract_js_functions(lines: List[str]) -> List[str]:
        """Extract JavaScript/TypeScript function names"""
        functions = []
        for line in lines:
            stripped = line.strip()
            # Function declarations
            if 'function ' in stripped:
                match = re.search(r'function\s+(\w+)', stripped)
                if match:
                    functions.append(match.group(1))
            # Arrow functions
            elif '=>' in stripped and '=' in stripped:
                match = re.search(r'(\w+)\s*=.*=>', stripped)
                if match:
                    functions.append(match.group(1))
        return functions
    
    @staticmethod
    def _extract_js_classes(lines: List[str]) -> List[str]:
        """Extract JavaScript/TypeScript class names"""
        classes = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('class '):
                match = re.match(r'class\s+(\w+)', stripped)
                if match:
                    classes.append(match.group(1))
        return classes
    
    @staticmethod
    def _extract_js_imports(lines: List[str]) -> List[str]:
        """Extract JavaScript/TypeScript import statements"""
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(('import ', 'const ')) and ('require(' in stripped or 'from ' in stripped):
                imports.append(stripped)
        return imports
    
    @staticmethod
    def _extract_java_methods(lines: List[str]) -> List[str]:
        """Extract Java method names"""
        methods = []
        for line in lines:
            stripped = line.strip()
            # Look for method signatures
            if any(modifier in stripped for modifier in ['public', 'private', 'protected']) and '(' in stripped and ')' in stripped:
                match = re.search(r'\w+\s+(\w+)\s*\(', stripped)
                if match and match.group(1) not in ['class', 'interface']:
                    methods.append(match.group(1))
        return methods
    
    @staticmethod
    def _extract_java_classes(lines: List[str]) -> List[str]:
        """Extract Java class names"""
        classes = []
        for line in lines:
            stripped = line.strip()
            if 'class ' in stripped:
                match = re.search(r'class\s+(\w+)', stripped)
                if match:
                    classes.append(match.group(1))
        return classes
    
    @staticmethod
    def _extract_java_imports(lines: List[str]) -> List[str]:
        """Extract Java import statements"""
        imports = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('import '):
                imports.append(stripped)
        return imports