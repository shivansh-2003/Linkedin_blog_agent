# LinkedIn Blog AI Assistant 🚀

An intelligent AI-powered assistant that transforms various content types (PDFs, images, code files, and text) into engaging LinkedIn blog posts using advanced language models and human-in-the-loop feedback.

## 🌟 Features

- **Multi-format Input Support**:
  - 📄 PDF documents
  - 📝 Text input (direct or from files)
  - 🖼️ Images (with AI vision analysis)
  - 💻 Code files (20+ programming languages)
  - 🔀 Mixed inputs (combine multiple sources)

- **Intelligent Information Extraction**:
  - PDF/Text: OpenAI GPT-4 for content analysis
  - Images: Google Gemini Vision for visual understanding
  - Code: Anthropic Claude for technical insights

- **Human-in-the-Loop Blog Generation**:
  - Interactive refinement process
  - Real-time feedback incorporation
  - Multiple iteration support
  - "Regenerate" option for fresh approaches

- **Professional LinkedIn Optimization**:
  - Viral hook creation
  - Optimal formatting for engagement
  - Strategic emoji usage
  - Relevant hashtag suggestions
  - Call-to-action questions

## 📋 Prerequisites

- Python 3.8+
- API Keys for:
  - OpenAI (for PDF/text processing)
  - Anthropic (for code analysis)
  - Google AI (for image processing)
  - Groq (for blog generation)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd linkedin-blog-ai-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
touch .env

# Add your API keys
echo "OPENAI_API_KEY=your_openai_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_key" >> .env
echo "GOOGLE_API_KEY=your_google_key" >> .env
echo "GROQ_API_KEY=your_groq_key" >> .env
```

## 🚀 Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

This launches an interactive menu where you can:
1. Choose your input type
2. Provide the content
3. Review and refine the generated post
4. Save the final result

### Command Line Mode

**Process a single file:**
```bash
# PDF file
python main.py --mode file --input document.pdf

# Image file
python main.py --mode file --input screenshot.png

# Code file
python main.py --mode file --input app.py
```

**Process text directly:**
```bash
python main.py --mode text --input "Your ideas about AI and the future..."
```

**With specific API keys:**
```bash
python main.py --openai-key YOUR_KEY --anthropic-key YOUR_KEY
```

## 📁 Project Structure

```
linkedin-blog-ai-assistant/
├── main.py                 # Main orchestrator
├── pdf_text_pipeline.py    # PDF/Text extraction pipeline
├── image_pipeline.py       # Image extraction pipeline
├── code_pipeline.py        # Code extraction pipeline
├── blogger_agent.py        # LangGraph blog generation agent
├── requirements.txt        # Python dependencies
├── .env                   # API keys (create this)
└── README.md              # This file
```

## 🔄 Workflow

1. **Input Processing**: The assistant analyzes your input using specialized pipelines
2. **Information Extraction**: Key insights, patterns, and valuable content are extracted
3. **Blog Generation**: Initial LinkedIn post is created based on extracted information
4. **Human Review**: You review the post and can:
   - Provide specific feedback for refinement
   - Request a complete regeneration
   - Approve the final version
5. **Iteration**: The process continues until you're satisfied
6. **Final Output**: Save your optimized LinkedIn post

## 💡 Tips for Best Results

### For Code Files:
- Include well-commented code
- Provide context about the problem being solved
- Multiple related files can be processed together

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

## 🔧 Supported File Types

**Code Files**: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go`, `.java`, `.cpp`, `.c`, `.cs`, `.rb`, `.php`, `.swift`, `.kt`, `.rs`, `.r`, `.css`, `.scss`, `.html`, `.sql`, `.sh`, `.yaml`, `.yml`, `.json`, `.xml`

**Image Files**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`

**Document Files**: `.pdf`, `.txt`

## 🤝 Example Use Cases

1. **Technical Tutorial**: Convert your code project into an educational LinkedIn post
2. **Research Summary**: Transform a PDF research paper into digestible insights
3. **Visual Explanation**: Turn diagrams or infographics into engaging narratives
4. **Project Showcase**: Combine code, images, and documentation for a comprehensive post
5. **Learning Journey**: Share your learning experience with code examples

## 📊 Best Posting Practices

The assistant provides LinkedIn posting tips with each generated post:
- Optimal posting times
- Engagement strategies
- Comment management
- Performance tracking

## 🐛 Troubleshooting

**API Key Issues**:
- Ensure all API keys are correctly set in `.env`
- Check API quotas and limits

**File Processing Errors**:
- Verify file paths are correct
- Ensure files are in supported formats
- Check file permissions

**Generation Issues**:
- Try providing more specific feedback
- Use "regenerate" for a fresh approach
- Ensure extracted information is relevant

## 🔮 Future Enhancements

- [ ] PowerPoint/Presentation file support
- [ ] Video content analysis
- [ ] LinkedIn analytics integration
- [ ] Scheduled posting capability
- [ ] Multi-language support
- [ ] Template library

## 📄 License

This project is provided as-is for educational and professional use.

---

Built with ❤️ using LangChain, LangGraph, and cutting-edge AI models.