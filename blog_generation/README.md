# Blog Generation System

A LangGraph-powered LinkedIn blog generation system with circular workflow (Generate → Critique → Refine).

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in this directory with your API keys:

```bash
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional (for future extensions)
# OPENAI_API_KEY=your_openai_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Get Groq API Key
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/Login
3. Create an API key
4. Add it to your `.env` file

## Usage

```bash
python3 main.py
```

### Options:
1. **Process file** - PDF, Word, PPT, Code, Text, Image
2. **Direct text input** - Enter text directly
3. **Example demo** - Pre-built AI best practices example
4. **Batch processing** - Process multiple files

## Features

- ✅ **LangChain Integration** - All agents use LangChain
- ✅ **LangGraph Workflow** - Circular Generate → Critique → Refine loop
- ✅ **Quality Gates** - Automated quality scoring and improvement
- ✅ **Human-in-the-Loop** - Interactive feedback and approval
- ✅ **Error Handling** - Graceful failure and recovery
- ✅ **File I/O** - Save generated blogs to files
- ✅ **Multiple Input Types** - Text, files, and demo content

## Architecture

- **BlogGeneratorAgent** - Creates initial blog content
- **CritiqueAgent** - Analyzes quality and engagement potential
- **RefinementAgent** - Improves content based on critique
- **BlogGenerationWorkflow** - Orchestrates the circular workflow
