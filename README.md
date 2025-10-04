# LinkedIn Blog AI Assistant 🚀
https://shivansh-2003-linkedin-blog-agent-app-s2y1sq.streamlit.app/


A comprehensive AI-powered assistant that transforms any content (files, text, images) into engaging LinkedIn blog posts through intelligent conversational interface with human-in-the-loop optimization.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-purple.svg)](https://langchain.readthedocs.io/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)

## 🎯 Overview

Transform any content into viral LinkedIn posts using:
- **Multi-format ingestion** (PDF, Word, PowerPoint, Code, Images, Text)
- **AI-powered analysis** with multiple models (Groq, Gemini)
- **Circular workflow** (Generate → Critique → Refine)
- **Conversational interface** with memory and intent recognition
- **Human-in-the-loop optimization** for perfect results
- **Quality scoring** and performance prediction

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Ingestion     │    │ Blog Generation  │    │    Chatbot      │
│   Pipeline      │───▶│    Workflow      │◄──▶│  Orchestrator   │
│                 │    │                  │    │                 │
│ • PDF/Word/PPT  │    │ • LangGraph      │    │ • Conversation  │
│ • Code/Images   │    │ • Multi-agent    │    │ • Memory        │
│ • Text/Markdown │    │ • Quality Gates  │    │ • Intent Recog  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌──────────────────┐
                    │   FastAPI        │
                    │   REST API       │
                    │                  │
                    │ • Endpoints      │
                    │ • File Upload    │
                    │ • Multi-file     │
                    └──────────────────┘
```

## 🌟 Key Features

### Multi-Format Input Support
- **📄 Documents**: PDF, Word (.docx), PowerPoint (.pptx)
- **💻 Code Files**: 20+ programming languages with structure analysis
- **🖼️ Images**: AI vision analysis with Gemini 2.0 Flash
- **📝 Text**: Direct input or file-based content
- **🔀 Multi-File**: Aggregate multiple sources into cohesive posts

### AI-Powered Processing
- **PDF/Word**: Text extraction and content analysis
- **PowerPoint**: Slide content + visual analysis with Gemini
- **Code**: Structure analysis, function extraction, and technical insights
- **Images**: Object detection, text extraction, and visual understanding
- **Text**: Content analysis and key insight extraction

### Advanced Blog Generation
- **LangGraph Workflow**: Generate → Critique → Refine cycle
- **Quality Scoring**: 1-10 assessment across multiple dimensions
- **LinkedIn Optimization**: Algorithm-friendly formatting and engagement
- **Human-in-the-Loop**: Interactive feedback and refinement
- **Multi-Source Aggregation**: Synthesize insights from multiple files

### Conversational Interface
- **Memory Management**: Persistent conversation history
- **Intent Recognition**: Understand user goals and context
- **Stage-Based Flow**: Guided conversation for optimal results
- **File Upload**: Process files directly in conversation
- **Feedback Integration**: Seamless human feedback incorporation

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python --version

# Required API Keys
export GROQ_API_KEY="your_groq_key"
export GOOGLE_API_KEY="your_google_key"
export LANGSMITH_API_KEY="your_langsmith_key"  # Optional for monitoring
```

### Installation

```bash
# Clone repository
git clone <repository-url>
cd linkedin-blog-ai-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env_template.txt .env
# Edit .env with your API keys
```

### Run the Application

```bash
# Start API server
python api.py
# Server runs on http://localhost:8000

# Interactive CLI mode
python main.py

# Test the system
python test.py
```

## 📁 Project Structure

```
linkedin-blog-ai-assistant/
├── 📂 ingestion/              # Multi-format content processing
│   ├── unified_processor.py   # Main orchestrator
│   ├── pdf_processor.py      # PDF extraction
│   ├── word_processor.py     # Word document processing
│   ├── ppt_processor.py      # PowerPoint processing
│   ├── code_processor.py     # Code analysis (language-agnostic)
│   ├── image_processor.py    # Image processing
│   ├── text_processor.py     # Text file processing
│   ├── multi_file_processor.py # Multi-file aggregation
│   ├── batch_processor.py    # Batch processing utilities
│   ├── ai_analyzer.py        # AI-powered content analysis
│   ├── prompt_templates.py   # Centralized prompt templates
│   └── README.md             # Detailed ingestion docs
├── 📂 blog_generation/        # AI blog generation workflow
│   ├── workflow.py           # LangGraph circular workflow
│   ├── blog_generator.py     # Content generation agent
│   ├── critique_agent.py     # Quality assessment agent
│   ├── refinement_agent.py   # Content improvement agent
│   ├── prompt_templates.py   # Blog generation prompts
│   ├── config.py             # Workflow configuration
│   └── README.md             # Detailed workflow docs
├── 📂 chatbot/               # Conversational interface
│   ├── chatbot_orchastrator.py  # Main conversation manager
│   ├── conversation_memory.py   # Persistent memory system
│   ├── intent_recognition.py    # Intent classification
│   ├── config.py             # Chatbot configuration
│   └── README.md             # Detailed chatbot docs
├── 📄 api.py                 # FastAPI REST API
├── 📄 main.py               # Interactive CLI interface
├── 📄 app.py                # Streamlit web interface
├── 📄 test.py               # Comprehensive test suite
├── 📄 langsmith_config.py   # LangSmith monitoring setup
├── 📄 requirements.txt      # Dependencies
└── 📄 README.md            # This file
```

## 🎮 Usage Examples

### 1. Interactive CLI Mode

```bash
python main.py
```

Choose from:
- 📚 Research-driven content generation
- 📄 Enhanced file processing
- 📝 Enhanced text processing
- 🔄 Basic mode

### 2. API Mode

```bash
# Start server
python api.py

# Upload file and generate blog
curl -X POST "http://localhost:8000/api/generate-blog-from-file" \
  -F "file=@document.pdf" \
  -F "target_audience=Tech professionals" \
  -F "tone=Professional and engaging"

# Generate from text
curl -X POST "http://localhost:8000/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "AI is transforming healthcare...",
    "target_audience": "Healthcare professionals",
    "tone": "Informative and inspiring"
  }'

# Multi-file aggregation
curl -X POST "http://localhost:8000/api/aggregate" \
  -F "files=@research1.pdf" \
  -F "files=@research2.docx" \
  -F "aggregation_strategy=synthesis" \
  -F "target_audience=Research professionals"
```

### 3. Chatbot Conversation

```bash
# Start chat session
curl -X POST "http://localhost:8000/api/chat/start"

# Send message
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to create a LinkedIn post about machine learning",
    "session_id": "your_session_id"
  }'
```

### 4. Streamlit Web Interface

```bash
# Start Streamlit app
streamlit run app.py
# Opens in browser at http://localhost:8501
```

## 🧪 Testing

### Run Test Suite

```bash
# Full comprehensive test (24 tests)
python test.py

# Test with pytest
pytest test.py -v

# Test LangSmith integration
python test_langsmith_simple.py
python test_langsmith_integration.py

# Test specific components
pytest test.py::TestAPIEndpoints::test_05_generate_blog_from_text -v
```

### Test Coverage

The test suite covers:
- ✅ **API Endpoints**: All REST endpoints with real file uploads
- ✅ **File Processing**: PDF, Word, PowerPoint, Code, Images, Text
- ✅ **Blog Generation**: Text and file-based generation
- ✅ **Chatbot**: Session management and conversation flow
- ✅ **Multi-File**: Aggregation strategies and validation
- ✅ **Error Handling**: Invalid inputs and edge cases
- ✅ **Performance**: Concurrent requests and response times

## 📊 Monitoring

The system includes comprehensive monitoring with LangSmith:

```bash
# Check monitoring setup
python test_langsmith_simple.py

# View traces at: https://smith.langchain.com
```

### LangSmith Integration

- **End-to-End Tracing**: All API calls, file processing, and blog generation
- **Performance Metrics**: Response times, success rates, error patterns
- **Quality Tracking**: Blog quality scores and improvement trends
- **Debugging**: Detailed execution traces for troubleshooting

## 🔧 Configuration

### Environment Variables

```bash
# Core API Keys (Required)
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

# LangSmith Monitoring (Optional)
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=linkedin-blog-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# Model Configuration (Optional)
GROQ_FALLBACK_MODELS=llama-3.1-8b-instant,gemma2-9b-it
```

### Model Selection

The system automatically selects optimal AI models per content type:
- **PDF/PowerPoint**: `llama-3.3-70b-versatile` (Groq)
- **Code**: `openai/gpt-oss-20b` (Groq)
- **Images**: `gemini-2.0-flash` (Google)
- **Text**: `gemma2-9b-it` (Groq)

## 🚀 Advanced Features

### Multi-File Aggregation Strategies

1. **Synthesis**: Blend insights from all files into unified narrative
2. **Comparison**: Compare and contrast findings across sources
3. **Sequence**: Create sequential story from multiple sources
4. **Timeline**: Chronological narrative from multiple sources

### Quality Assessment

The system evaluates blog posts across 5 dimensions:
- **Clarity**: How clear and understandable the content is
- **Engagement**: Potential for likes, comments, and shares
- **Professionalism**: Appropriate tone and language
- **LinkedIn Optimization**: Algorithm-friendly formatting
- **Value**: Practical insights and actionable content

### Human-in-the-Loop Workflow

1. **Generate**: AI creates initial blog post
2. **Critique**: AI evaluates quality and provides feedback
3. **Refine**: AI improves content based on critique
4. **Human Review**: User provides specific feedback
5. **Iterate**: Process continues until satisfaction (max 3 cycles)

## 📈 Performance

- **Processing Speed**: ~2-5 seconds per file
- **Quality Scores**: Typically 7-9/10
- **Supported Formats**: 25+ file types
- **Concurrent Users**: Scales with FastAPI
- **Memory Usage**: ~200MB base, +50MB per session
- **Success Rate**: >95% for supported file types

## 🔧 Supported File Types

### Documents
- **PDF**: `.pdf` (text extraction)
- **Word**: `.docx` (full document processing)
- **PowerPoint**: `.pptx`, `.ppt` (slides + visual analysis)

### Code Files
- **Languages**: Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, R, CSS, HTML, SQL, Shell, YAML, JSON, XML
- **Analysis**: Function extraction, structure analysis, technical insights

### Images
- **Formats**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`
- **Analysis**: Object detection, text extraction, visual understanding

### Text
- **Formats**: `.txt`, `.md`, direct text input
- **Processing**: Content analysis and key insight extraction

## 🛠️ Development

### Adding New File Types

1. Create processor in `ingestion/`
2. Register in `unified_processor.py`
3. Add to `config.SUPPORTED_EXTENSIONS`
4. Update tests

### Extending AI Models

1. Add model to `config.ProcessingModel`
2. Update `ai_analyzer.py`
3. Configure in `MODEL_MAPPING`
4. Test with fallbacks

### Custom Workflows

1. Extend `BlogGenerationWorkflow`
2. Add new nodes and edges
3. Update routing logic
4. Test with LangGraph

## 💡 Tips for Best Results

### For Presentations:
- **PowerPoint files** work best (.pptx, .ppt)
- Enable image analysis for slides with charts, graphs, or diagrams
- Use selective slide processing for long presentations
- Include speaker notes for additional context
- Visual-heavy presentations benefit most from Gemini analysis

### For Code Files:
- Include well-commented code
- Provide context about the problem being solved
- Multiple related files can be processed together
- Language-agnostic processing works for most languages

### For Images:
- Use high-quality images with clear content
- Diagrams, charts, and infographics work exceptionally well
- Screenshots of applications or UIs provide good material

### For PDFs/Text:
- Focus on content with clear insights or learnings
- Technical documents, research papers, and reports work great
- Personal experiences and case studies create engaging posts

### During Refinement:
- Be specific with feedback (e.g., "Make it more technical" or "Add a personal story")
- Use "regenerate" if you want a completely different angle
- Consider your target audience when providing feedback

## 🤝 Example Use Cases

1. **Conference Presentation**: Transform your slide deck into viral LinkedIn content
2. **Technical Tutorial**: Convert your code project into an educational post
3. **Research Summary**: Transform a PDF research paper into digestible insights
4. **Data Visualization**: Turn charts and graphs into compelling narratives
5. **Product Demo**: Combine presentation slides with code examples
6. **Learning Journey**: Share insights from conference talks or presentations
7. **Project Showcase**: Combine code, images, and presentation materials
8. **Multi-Source Analysis**: Synthesize insights from multiple research papers
9. **Code Review**: Transform technical code analysis into educational content
10. **Visual Storytelling**: Convert infographics and diagrams into engaging posts

## 🐛 Troubleshooting

### API Key Issues
- Ensure all API keys are correctly set in `.env`
- Check API quotas and limits
- Google API key needed for image and presentation analysis

### File Processing Errors
- Verify file paths are correct
- Ensure files are in supported formats
- Check file permissions
- For presentations: Ensure proper PowerPoint format

### Presentation-Specific Issues
- If image analysis fails, disable it and process text only
- Large presentations may take longer to process
- PDF presentations have limited visual analysis compared to .pptx

### Generation Issues
- Try providing more specific feedback
- Use "regenerate" for a fresh approach
- Ensure extracted information is relevant
- Check model availability and fallbacks

### Chatbot Issues
- Ensure session is properly created before sending messages
- Check conversation memory and context
- Verify intent recognition is working correctly

## 🚀 Recent Updates

- ✅ **Multi-File Processing**: Aggregate multiple sources into cohesive posts
- ✅ **Language-Agnostic Code Processing**: Generic code analysis for all languages
- ✅ **Enhanced PowerPoint Support**: Full slide and visual analysis
- ✅ **Gemini 2.0 Flash**: Advanced visual analysis for charts and diagrams
- ✅ **Streamlit Interface**: Web-based conversational interface
- ✅ **Comprehensive Testing**: 24-test suite with real file uploads
- ✅ **LangSmith Integration**: End-to-end monitoring and tracing
- ✅ **Quality Scoring**: Multi-dimensional blog assessment
- ✅ **Human-in-the-Loop**: Interactive refinement workflow

## 🔮 Future Enhancements

- [ ] Video content analysis
- [ ] LinkedIn analytics integration
- [ ] Scheduled posting capability
- [ ] Multi-language support
- [ ] Template library
- [ ] Advanced chart data extraction
- [ ] Real-time collaboration
- [ ] Custom model fine-tuning
- [ ] A/B testing for blog variants
- [ ] Performance analytics dashboard

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python test.py`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- **LangChain** for the powerful AI framework
- **LangGraph** for workflow orchestration
- **Groq** for fast inference and multiple model support
- **Google Gemini** for advanced vision capabilities
- **FastAPI** for the robust API framework
- **Streamlit** for the interactive web interface
- **LangSmith** for comprehensive monitoring

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 **Documentation**: See individual component READMEs
- 🐛 **Bug Reports**: Use issue templates
- 💡 **Feature Requests**: Open enhancement issues
- 💬 **Discussions**: GitHub Discussions for questions

---

**Built with ❤️ using modern AI and Python technologies**

*Transform any content into viral LinkedIn posts with the power of AI!*