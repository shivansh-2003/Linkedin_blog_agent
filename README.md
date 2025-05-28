# LinkedIn Blog AI Assistant 🚀

An intelligent AI-powered assistant that transforms various content types (PDFs, images, code files, presentations, and text) into engaging LinkedIn blog posts using advanced language models and human-in-the-loop feedback.

## 🌟 Features

- **Multi-format Input Support**:
  - 📄 PDF documents (text extraction)
  - 📝 Text input (direct or from files)
  - 🖼️ Images (with AI vision analysis)
  - 💻 Code files (20+ programming languages)
  - 📊 Presentations (PowerPoint, PDF slides with vision analysis)
  - 🔀 Mixed inputs (combine multiple sources)

- **Intelligent Information Extraction**:
  - PDF/Text: OpenAI GPT-4 for content analysis
  - Images: Google Gemini Flash 1.5 for visual understanding
  - Code: Anthropic Claude for technical insights
  - Presentations: OpenAI GPT-4 + Gemini Flash 1.5 for slide content + visual analysis

- **Advanced Presentation Processing**:
  - PowerPoint (.pptx, .ppt) and PDF slide extraction
  - Text, images, charts, and tables from slides
  - Speaker notes extraction
  - AI-powered visual analysis using Gemini Flash 1.5
  - Selective slide processing (choose specific slides)
  - Combined text and visual insights

- **Human-in-the-Loop Blog Generation**:
  - Interactive refinement process using LangGraph
  - Real-time feedback incorporation
  - Multiple iteration support
  - "Regenerate" option for fresh approaches
  - Anthropic Claude Opus for high-quality content generation

- **Professional LinkedIn Optimization**:
  - Viral hook creation
  - Optimal formatting for engagement
  - Strategic emoji usage
  - Relevant hashtag suggestions
  - Call-to-action questions
  - Posting best practices guidance

## 📋 Prerequisites

- Python 3.8+
- API Keys for:
  - OpenAI (for PDF/text processing and presentations)
  - Anthropic (for code analysis and blog generation)
  - Google AI (for image and presentation visual analysis)

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
```

## 🚀 Usage

### Interactive Mode (Recommended)

```bash
python main.py
```

This launches an interactive menu where you can:
1. Choose your input type (text, file, presentations, multiple files)
2. For presentations: Choose image analysis and specific slides
3. Provide the content
4. Review and refine the generated post with human-in-the-loop feedback
5. Save the final result

### Presentation-Specific Features

When processing presentations, you get additional options:
- **Image Analysis**: Enable/disable AI vision analysis of charts, diagrams, and visuals
- **Selective Processing**: Choose specific slides (e.g., "1,3,5") instead of processing all
- **Visual Insights**: Gemini Flash 1.5 analyzes images for data trends and key insights

## 📁 Project Structure

```
linkedin-blog-ai-assistant/
├── main.py                    # Main orchestrator
├── pdf_text_pipeline.py       # PDF/Text extraction pipeline
├── image_pipeline.py          # Image extraction pipeline
├── code_pipeline.py           # Code extraction pipeline
├── presentation_pipeline.py   # Presentation extraction pipeline (NEW!)
├── blogger_agent.py           # LangGraph blog generation agent
├── requirements.txt           # Python dependencies
├── .env                      # API keys (create this)
└── README.md                 # This file
```

## 🔄 Workflow

1. **Input Processing**: The assistant analyzes your input using specialized pipelines
2. **Information Extraction**: Key insights, patterns, and valuable content are extracted
   - For presentations: Combines slide text + AI visual analysis
3. **Blog Generation**: Initial LinkedIn post created using Anthropic Claude Opus
4. **Human Review**: Interactive feedback loop where you can:
   - Provide specific feedback for refinement
   - Request a complete regeneration
   - Approve the final version
5. **Iteration**: The process continues until you're satisfied
6. **Final Output**: Save your optimized LinkedIn post with posting tips

## 💡 Tips for Best Results

### For Presentations:
- **PowerPoint files** work best (.pptx, .ppt)
- Enable image analysis for slides with charts, graphs, or diagrams
- Use selective slide processing for long presentations
- Include speaker notes for additional context
- Visual-heavy presentations benefit most from Gemini Flash 1.5 analysis

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

**Presentation Files**: `.pptx`, `.ppt`, `.pdf` (presentation mode)

**Code Files**: `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.go`, `.java`, `.cpp`, `.c`, `.cs`, `.rb`, `.php`, `.swift`, `.kt`, `.rs`, `.r`, `.css`, `.scss`, `.html`, `.sql`, `.sh`, `.yaml`, `.yml`, `.json`, `.xml`

**Image Files**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.bmp`, `.webp`

**Document Files**: `.pdf` (text mode), `.txt`

## 🤝 Example Use Cases

1. **Conference Presentation**: Transform your slide deck into viral LinkedIn content
2. **Technical Tutorial**: Convert your code project into an educational post
3. **Research Summary**: Transform a PDF research paper into digestible insights
4. **Data Visualization**: Turn charts and graphs into compelling narratives
5. **Product Demo**: Combine presentation slides with code examples
6. **Learning Journey**: Share insights from conference talks or presentations
7. **Project Showcase**: Combine code, images, and presentation materials

## 🎯 AI Models Used

- **Text Analysis**: OpenAI GPT-4 (PDFs, presentations, text)
- **Visual Analysis**: Google Gemini Flash 1.5 (images, presentation visuals)
- **Code Analysis**: Anthropic Claude (code understanding)
- **Blog Generation**: Anthropic Claude Opus (high-quality content creation)
- **Workflow Management**: LangGraph (human-in-the-loop automation)

## 📊 Best Posting Practices

The assistant provides LinkedIn posting tips with each generated post:
- Optimal posting times (Tuesday-Thursday, 8-10 AM or 5-6 PM)
- Engagement strategies
- Comment management tips
- Performance tracking metrics
- Reposting guidelines

## 🐛 Troubleshooting

**API Key Issues**:
- Ensure all API keys are correctly set in `.env`
- Check API quotas and limits
- Google API key needed for presentation image analysis

**File Processing Errors**:
- Verify file paths are correct
- Ensure files are in supported formats
- Check file permissions
- For presentations: Ensure proper PowerPoint format

**Presentation-Specific Issues**:
- If image analysis fails, disable it and process text only
- Large presentations may take longer to process
- PDF presentations have limited visual analysis compared to .pptx

**Generation Issues**:
- Try providing more specific feedback
- Use "regenerate" for a fresh approach
- Ensure extracted information is relevant

## 🚀 Recent Updates

- ✅ **Presentation Pipeline**: Full PowerPoint and PDF slide support
- ✅ **Gemini Flash 1.5**: Advanced visual analysis for charts and diagrams
- ✅ **Selective Processing**: Choose specific slides to analyze
- ✅ **Visual Insights**: AI-powered analysis of presentation graphics
- ✅ **Enhanced UI**: Better interactive options for presentations

## 🔮 Future Enhancements

- [ ] Video content analysis
- [ ] LinkedIn analytics integration
- [ ] Scheduled posting capability
- [ ] Multi-language support
- [ ] Template library
- [ ] Batch presentation processing
- [ ] Advanced chart data extraction

## 📄 License

This project is provided as-is for educational and professional use.

---

Built with ❤️ using LangChain, LangGraph, OpenAI GPT-4, Anthropic Claude, and Google Gemini Flash 1.5.