# Ingestion Subsystem Documentation

## 🎯 Overview

The ingestion subsystem is responsible for extracting, processing, and analyzing content from multiple file formats. It provides a unified interface for handling PDFs, Word documents, PowerPoint presentations, code files, images, and text files.

## 🏗️ Architecture

```
┌─────────────────┐
│ UnifiedProcessor│ ◄── Main Entry Point
└─────┬───────────┘
      │
      ├── FileDetector (validation)
      ├── Format-specific processors
      └── AIAnalyzer (content analysis)

Format Processors:
├── PDFProcessor      (LangChain PyPDFLoader)
├── WordProcessor     (LangChain Docx2txtLoader)
├── PPTProcessor      (python-pptx + vision)
├── CodeProcessor     (AST + pattern analysis)
├── ImageProcessor    (binary + metadata)
└── TextProcessor     (LangChain TextLoader)
```

## 📁 File Structure

```
ingestion/
├── unified_processor.py     # Main orchestrator
├── file_detection.py       # File validation & type detection
├── ai_analyzer.py          # AI-powered content analysis
├── prompt_templates.py     # Centralized AI prompts
├── config.py              # Data models & configuration
├── pdf_processor.py       # PDF text extraction
├── word_processor.py      # Word document processing
├── ppt_processor.py       # PowerPoint processing
├── code_processor.py      # Code structure analysis
├── image_processor.py     # Image processing
├── text_processor.py      # Text file processing
├── batch_processor.py     # Batch operations
├── multi_file_processor.py # Multi-file aggregation
└── README.md             # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from ingestion.unified_processor import UnifiedProcessor

processor = UnifiedProcessor()
result = processor.process_file("document.pdf")

if result.success:
    print(f"Content: {result.extracted_content.raw_text}")
    print(f"AI Analysis: {result.ai_analysis}")
    print(f"Key Insights: {result.key_insights}")
```

### Batch Processing

```python
from ingestion.batch_processor import BatchProcessor

batch = BatchProcessor(max_workers=4)
results = batch.process_multiple_files([
    "doc1.pdf", "presentation.pptx", "code.py"
])

summary = batch.generate_batch_summary(results)
print(f"Processed {summary['successful']}/{summary['total_files']} files")
```

### Multi-File Aggregation

```python
from ingestion.multi_file_processor import MultiFileProcessor
from blog_generation.config import AggregationStrategy

processor = MultiFileProcessor()
result = await processor.process_multiple_files(
    ["file1.pdf", "file2.py", "file3.pptx"],
    AggregationStrategy.SYNTHESIS
)
```

## 📊 Data Models

### ProcessedContent (Main Output)

```python
class ProcessedContent(BaseModel):
    source_file: str                           # Original file path
    content_type: ContentType                  # Detected file type
    extracted_content: Optional[ExtractedContent]  # Raw extraction results
    ai_analysis: str                          # AI-generated analysis
    key_insights: List[str]                   # Top 5 insights
    metadata: Optional[DocumentMetadata]       # File metadata
    success: bool                             # Processing status
    error_message: Optional[str]              # Error details if failed
```

### ExtractedContent (Raw Extraction)

```python
class ExtractedContent(BaseModel):
    content_type: ContentType         # File type
    file_path: str                   # Source path
    raw_text: str                    # Extracted text content
    structured_data: Dict[str, Any]  # Format-specific data
    metadata: Dict[str, Any]         # Processing metadata
    processing_model: ProcessingModel # AI model used
    processing_time: float           # Time taken (seconds)
```

## 🔧 Configuration

### Supported File Types

```python
SUPPORTED_EXTENSIONS = {
    # Documents
    ".pdf": ContentType.PDF,
    ".docx": ContentType.WORD,
    ".doc": ContentType.WORD,
    ".pptx": ContentType.POWERPOINT,
    ".ppt": ContentType.POWERPOINT,
    
    # Text
    ".txt": ContentType.TEXT,
    ".md": ContentType.TEXT,
    
    # Code (20+ languages)
    ".py": ContentType.CODE,
    ".js": ContentType.CODE,
    ".java": ContentType.CODE,
    ".cpp": ContentType.CODE,
    # ... and more
    
    # Images
    ".jpg": ContentType.IMAGE,
    ".png": ContentType.IMAGE,
    ".gif": ContentType.IMAGE,
    # ... and more
}
```

### Model Selection

```python
MODEL_MAPPING = {
    ContentType.PDF: ProcessingModel.GROQ_LLAMA_70B,
    ContentType.WORD: ProcessingModel.GROQ_LLAMA_8B,
    ContentType.POWERPOINT: ProcessingModel.GROQ_LLAMA_70B,
    ContentType.CODE: ProcessingModel.GROQ_GPT_OSS_20B,
    ContentType.TEXT: ProcessingModel.GROQ_GEMMA,
    ContentType.IMAGE: ProcessingModel.GEMINI_FLASH
}
```

## 📋 Detailed Processor Guide

### 1. PDF Processing

**Features:**
- Text extraction from all pages
- Metadata preservation
- Page-by-page content organization

**Usage:**
```python
from ingestion.pdf_processor import PDFProcessor

extracted = PDFProcessor.extract_content("document.pdf")
print(f"Pages: {extracted.structured_data['total_pages']}")
```

**Output Structure:**
```python
structured_data = {
    "total_pages": 15,
    "pages": [
        {"page_number": 1, "content": "...", "metadata": {...}},
        # ... more pages
    ],
    "document_metadata": {...}
}
```

### 2. PowerPoint Processing

**Features:**
- Text extraction from slides
- Image extraction with bytes
- Speaker notes processing
- Visual analysis with Gemini

**Usage:**
```python
from ingestion.ppt_processor import PPTProcessor

extracted = PPTProcessor.extract_content("presentation.pptx")
slides = extracted.structured_data['slides']
```

**Output Structure:**
```python
structured_data = {
    "total_slides": 20,
    "slides": [
        {
            "slide_number": 1,
            "title": "Introduction",
            "content": ["Bullet point 1", "Bullet point 2"],
            "notes": "Speaker notes...",
            "has_images": True,
            "images": [
                {
                    "mime_type": "image/png",
                    "bytes_len": 15234,
                    "image_bytes": b"..." # Raw image data
                }
            ]
        }
    ],
    "image_captions": [  # Generated by Gemini
        {"slide": 1, "caption": "Chart showing growth trends"}
    ]
}
```

### 3. Code Processing

**Features:**
- Language detection
- Structure analysis (functions, classes, imports)
- Syntax error detection
- Cross-language pattern matching

**Usage:**
```python
from ingestion.code_processor import CodeProcessor

extracted = CodeProcessor.extract_content("script.py")
analysis = extracted.structured_data['analysis']
```

**Output Structure:**
```python
structured_data = {
    "language": "python",
    "file_extension": ".py",
    "analysis": {
        "functions": ["main", "process_data", "calculate_stats"],
        "classes": ["DataProcessor", "ResultAnalyzer"],
        "imports": ["import pandas", "from sklearn import..."],
        "summary": "Python code with 3 functions, 2 classes...",
        "has_syntax_errors": False
    },
    "line_count": 150,
    "chunks": ["chunk1", "chunk2", ...]  # For LangChain processing
}
```

### 4. Image Processing

**Features:**
- Binary data extraction
- MIME type detection
- Metadata preservation
- Gemini vision analysis

**Usage:**
```python
from ingestion.image_processor import ImageProcessor

extracted = ImageProcessor.extract_content("chart.png")
```

**Output Structure:**
```python
structured_data = {
    "image_bytes": b"...",  # Raw image data
    "image_url": None       # Alternative: URL reference
}
metadata = {
    "mime_type": "image/png",
    "file_extension": ".png",
    "has_bytes": True
}
```

## 🤖 AI Analysis

### Vision Analysis (Images & PPT)

**Gemini 2.0 Flash** processes visual content:

```python
# For images
prompt = "Describe the image, extract text, identify charts/diagrams, propose LinkedIn angles"

# For PowerPoint images  
prompt = "Provide brief professional caption and detected text"
```

### Text Analysis (All Other Formats)

**Groq Models** analyze textual content:

```python
# Example for code
system_prompt = "Expert software engineer analyzing code for professional audience"
user_prompt = "Analyze this code: purpose, architecture, key components..."

# Example for PDF
system_prompt = "Professional content analyst for LinkedIn optimization"
user_prompt = "Analyze this document: main topics, insights, blog angles..."
```

### Model Fallbacks

The system includes robust fallback mechanisms:

```python
# Primary model fails → Try fallback models
candidates = [
    "llama-3.3-70b-versatile",  # Primary
    "llama-3.1-8b-instant",     # Fallback 1
    "gemma2-9b-it"              # Fallback 2
]
```

## 🔄 Multi-File Processing

### Aggregation Strategies

```python
class AggregationStrategy(str, Enum):
    SYNTHESIS = "synthesis"      # Blend insights together
    COMPARISON = "comparison"    # Compare/contrast sources
    SEQUENCE = "sequence"        # Sequential narrative
    TIMELINE = "timeline"        # Chronological story
```

### Usage Example

```python
from ingestion.multi_file_processor import MultiFileProcessor

processor = MultiFileProcessor()

# Process multiple files with synthesis strategy
result = await processor.process_multiple_files(
    ["research.pdf", "code.py", "presentation.pptx"],
    AggregationStrategy.SYNTHESIS
)

print(f"Unified insights: {result.unified_insights}")
print(f"Cross-references: {result.cross_references}")
```

## 🧪 Testing

### Unit Tests

```bash
# Test individual processors
python -m pytest ingestion/tests/test_pdf_processor.py
python -m pytest ingestion/tests/test_code_processor.py

# Test unified processor
python -m pytest ingestion/tests/test_unified_processor.py
```

### Integration Tests

```bash
# Test with real files
python ingestion/tests/test_integration.py

# Test AI analysis
python ingestion/tests/test_ai_analyzer.py
```

### Performance Tests

```bash
# Benchmark processing speed
python ingestion/tests/benchmark.py
```

## 🔧 Customization

### Adding New File Types

1. **Create Processor:**
```python
class NewProcessor:
    @staticmethod
    def extract_content(file_path: str) -> ExtractedContent:
        # Your extraction logic
        return ExtractedContent(...)
```

2. **Register Processor:**
```python
# In unified_processor.py
self.processors[ContentType.NEW_TYPE] = NewProcessor
```

3. **Update Configuration:**
```python
# In config.py
SUPPORTED_EXTENSIONS[".new"] = ContentType.NEW_TYPE
```

### Custom AI Analysis

1. **Add Prompt Template:**
```python
# In prompt_templates.py
NEW_SYSTEM_PROMPT = "Your specialized system prompt"

def build_new_prompt(content, metadata):
    return f"Analyze this {content_type}: {content}"
```

2. **Update AI Analyzer:**
```python
# In ai_analyzer.py
if content_type == ContentType.NEW_TYPE:
    return self._analyze_with_custom_prompt(extracted_content)
```

## 📊 Performance Optimization

### Processing Speed

- **PDF**: ~1-3 seconds (depends on pages)
- **PowerPoint**: ~2-5 seconds (depends on images)
- **Code**: ~0.5-1 second
- **Images**: ~1-2 seconds (vision analysis)
- **Text**: ~0.3-0.8 seconds

### Memory Usage

- **Base**: ~50MB per processor
- **Per File**: ~5-20MB (depends on size)
- **Batch**: Linear scaling with worker count

### Optimization Tips

```python
# Use batch processing for multiple files
batch_processor = BatchProcessor(max_workers=4)

# Enable caching for repeated analysis
# (Consider implementing Redis caching)

# Use streaming for large files
# (Consider chunked processing)
```

## 🛠️ Environment Setup

### Required Dependencies

```bash
# Core processing
langchain
langchain-community
python-pptx
pypdf

# AI models
groq
google-generativeai

# Utilities
pydantic
pathlib
```

### Environment Variables

```bash
# AI Models
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key

# Optional: Model fallbacks
GROQ_FALLBACK_MODELS=llama-3.1-8b-instant,gemma2-9b-it

# File processing limits
MAX_FILE_SIZE_MB=50
PROCESSING_TIMEOUT=300
```

## 🐛 Troubleshooting

### Common Issues

**1. File Processing Fails**
```python
# Check file type support
supported = FileDetector.detect_file_type("file.xyz")
if not supported:
    print("Unsupported file type")

# Check file size
valid, message = FileDetector.validate_file("large_file.pdf")
```

**2. AI Analysis Errors**
```python
# Model fallback triggered
result = processor.process_file("file.pdf")
if "fallback" in result.ai_analysis:
    print("Primary model failed, used fallback")
```

**3. Memory Issues**
```python
# Process files in batches
batch_processor = BatchProcessor(max_workers=2)  # Reduce workers
```

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed tracing
os.environ["LANGSMITH_TRACING"] = "true"
```

## 📈 Metrics & Monitoring

### Processing Metrics

```python
# Available in ProcessedContent
result.extracted_content.processing_time  # Processing duration
result.metadata.file_size                # File size
len(result.key_insights)                 # Insights extracted
```

### Quality Metrics

```python
# Success rate tracking
total_files = len(results)
successful = len([r for r in results if r.success])
success_rate = successful / total_files
```

### LangSmith Integration

All processors include LangSmith tracing:

```python
@trace_step("file_processing", "workflow")
def process_file(self, file_path: str) -> ProcessedContent:
    # Automatic tracing of processing steps
```

## 🔗 Integration Examples

### With Blog Generation

```python
# Direct integration
result = processor.process_file("document.pdf")
if result.success:
    blog_state = BlogGenerationState(
        source_content=result.extracted_content.raw_text,
        content_insights=result.key_insights,
        ai_analysis=result.ai_analysis
    )
```

### With API

```python
# FastAPI endpoint
@app.post("/api/ingest")
async def ingest_file(file: UploadFile):
    result = processor.process_file(file.filename)
    return result.dict()
```

### With Chatbot

```python
# Conversational interface
extracted = processor.process_file(file_path)
chatbot.update_context(extracted.ai_analysis, extracted.key_insights)
```

---

**Next Steps:**
- See [Blog Generation README](../blog_generation/README.md) for content generation
- See [Chatbot README](../chatbot/README.md) for conversational interface
- See [API Documentation](../api.md) for REST endpoints