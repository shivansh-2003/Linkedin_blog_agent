# LinkedIn Blog Agent - Quick Reference Guide

## System Overview

**Three Main Components**:
1. **Streamlit Frontend** (app.py) - User interface
2. **FastAPI Backend** (api.py) - REST API orchestrator
3. **Processing Pipelines** - Ingestion, generation, chatbot

---

## Key File Locations

### Entry Points
- `app.py` - Start Streamlit UI
- `api.py` - Start FastAPI backend
- `main.py` - CLI interactive mode
- `worker.py` - Background task processor

### LLM Integration Files
- `ingestion/ai_analyzer.py` - Content analysis
- `blog_generation/blog_generator.py` - Post generation
- `blog_generation/critique_agent.py` - Quality scoring
- `blog_generation/refinement_agent.py` - Iterative improvement
- `chatbot/chatbot_orchastrator.py` - Conversation engine

### Configuration & Models
- `ingestion/config.py` - Ingestion data models
- `blog_generation/config.py` - Blog state models
- `chatbot/config.py` - Chat state models
- `shared/models.py` - Shared enums

### Monitoring
- `langsmith_config.py` - Tracing configuration

---

## Data Flow

```
User Input
    ↓
Frontend (Streamlit app.py)
    ↓
API Endpoints (FastAPI api.py)
    ↓
┌─────────────────────────────────────┐
│  Choose Path:                       │
│  1. Ingest → Analyze                │
│  2. Generate Blog                   │
│  3. Aggregate Multiple Files        │
│  4. Chat with Assistant             │
└─────────────────────────────────────┘
    ↓
LLM Processing (Groq, Google Gemini)
    ↓
LangGraph Workflow (if blog generation)
    ├→ Generate
    ├→ Critique (quality 1-10)
    ├→ Refine
    └→ Polish
    ↓
Return Result
    ↓
Frontend Display + Download
```

---

## LLM Models Used

| Component | Model | Purpose |
|-----------|-------|---------|
| Text Analysis | llama-3.3-70b-versatile (Groq) | Content insights |
| Blog Generation | llama-3.3-70b-versatile (Groq) | Create posts |
| Quality Critique | llama-3.3-70b-versatile (Groq) | Score & feedback |
| Image Analysis | gemini-2.0-flash-exp | Vision analysis |
| Intent Recognition | llama-3.1-8b-instant (Groq) | Understand user |

---

## API Endpoints Quick Map

### File Processing
- `POST /api/ingest` - Process any file (returns analysis)
- `POST /api/generate-blog-from-file` - File → Blog post
- `POST /api/aggregate` - Multiple files → Unified post

### Direct Generation
- `POST /api/generate-blog` - Text → Blog post

### Chat Interface
- `POST /api/chat/start` - Begin conversation
- `POST /api/chat/message` - Send message
- `GET /api/chat/history/{id}` - Get conversation
- `POST /api/chat/feedback` - Improve draft
- `POST /api/chat/approve` - Approve final

### Utilities
- `GET /health` - Server status
- `GET /` - API info

---

## Key Classes

### Ingestion Pipeline
- `UnifiedProcessor` - Main orchestrator
- `FormatHandler` - Extract from different file types
- `ContentAnalyzer` - AI-powered analysis
- `MultiFileProcessor` - Combine multiple files

### Blog Generation
- `BlogGenerationWorkflow` - LangGraph state machine
- `BlogGeneratorAgent` - Creates blog posts
- `CritiqueAgent` - Quality assessment
- `RefinementAgent` - Improves based on feedback

### Chatbot
- `ChatbotOrchestrator` - Main conversation engine
- `ConversationMemoryManager` - Stores/retrieves state
- `ContextualIntentRecognizer` - Understands user intent

---

## Supported File Types

| Type | Extensions | Model Used | Max Time |
|------|-----------|-----------|----------|
| PDF | .pdf | PRIMARY (70B) | 120s |
| Word | .doc, .docx | FAST (8B) | 60s |
| PowerPoint | .ppt, .pptx | PRIMARY (70B) | 180s |
| Code | .py, .js, .java, etc | PRIMARY (70B) | 90s |
| Text | .txt | FAST (8B) | 30s |
| Markdown | .md, .markdown | FAST (8B) | 30s |
| Images | .jpg, .png, .gif, etc | VISION (Gemini) | 60s |

---

## LangSmith Integration Points

### Already Decorated
- All API endpoints in `api.py`
- Blog workflow nodes in `blog_generation/workflow.py`

### Need Decoration
- `ContentAnalyzer.analyze()` in `ingestion/ai_analyzer.py`
- `BlogGeneratorAgent.generate_blog()` in `blog_generation/blog_generator.py`
- `CritiqueAgent.critique()` in `blog_generation/critique_agent.py`
- `RefinementAgent.refine()` in `blog_generation/refinement_agent.py`
- `ChatbotOrchestrator.process_user_input()` in `chatbot/chatbot_orchastrator.py`

---

## Configuration

### Environment Variables Required
```
GROQ_API_KEY=<your-groq-key>
GEMINI_API_KEY=<your-gemini-key>
LANGSMITH_API_KEY=<your-langsmith-key>
LANGSMITH_PROJECT=linkedin-blog-agent
```

### Key Settings
- Max iterations for blog refinement: 3
- Max file size: 50 MB
- Max batch files: 10
- Chat memory buffer: 50 messages
- Session timeout: 24 hours

---

## Workflow Details

### Blog Generation (6 steps)
1. **GENERATE** - Create initial post from content
2. **CRITIQUE** - Score quality (1-10), get feedback
3. **REFINE** - Apply improvements based on critique
4. **HUMAN_REVIEW** - Optional approval step
5. **POLISH** - Final enhancements
6. **END** - Return final blog

Can loop back: Generate → Critique → Refine → (repeat up to 3 times)

### Chat Session Lifecycle
1. **START** - Create session, set initial stage
2. **ACCEPT_INPUT** - User sends message
3. **RECOGNIZE_INTENT** - AI determines what user wants
4. **ROUTE** - Send to appropriate handler
5. **PROCESS** - Execute (upload, generate, feedback, etc)
6. **RETURN** - Send response back to user
7. **STORE_CONTEXT** - Save state for next turn

---

## Performance Metrics to Monitor

### With LangSmith
- Token usage per model per operation
- Latency by component (ingestion, generation, critique)
- Error rates and recovery success
- User satisfaction trends
- Model cost analysis
- Quality score progression over iterations

### Recommended Dashboards
1. **Operations Dashboard** - API latency, error rates, uptime
2. **Quality Dashboard** - Critique scores, feedback patterns
3. **Usage Dashboard** - Files processed, models used, cost
4. **Chatbot Dashboard** - Intent accuracy, user satisfaction
5. **Cost Dashboard** - Tokens per model, cost per operation

---

## Testing LangSmith Integration

Run test files to verify setup:
```bash
python test_langsmith_simple.py        # Basic test
python test_langsmith_integration.py   # Full integration test
```

Verify:
1. Traces appear in LangSmith dashboard
2. All decorated functions report
3. Token counts are accurate
4. Error tracing works

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| LangSmith traces not appearing | Check API key in .env, verify LANGSMITH_TRACING=true |
| Slow ingestion | Use FAST model for text/word, consider file size |
| Generation timeout | Increase max_iterations or reduce input size |
| Chat session expires | Sessions last 24 hours, create new one to continue |
| LLM fallback | Check API quotas, verify API keys are valid |

---

## Project Structure (One-Liner View)

```
linkedin-blog-agent/
├── app.py (Streamlit UI)
├── api.py (FastAPI backend)
├── main.py (CLI mode)
├── worker.py (Background processor)
├── langsmith_config.py (Monitoring)
├── ingestion/ (Content processing)
├── blog_generation/ (Blog creation)
├── chatbot/ (Conversation)
├── shared/ (Shared models)
└── test*.py (Testing)
```

---

## Next Steps for Enhancement

1. **Add More Decorators** - Trace all LLM calls for full visibility
2. **Custom Feedback** - Log user satisfaction to LangSmith
3. **Cost Tracking** - Monitor token usage and model costs
4. **Quality Metrics** - Export critique scores for analysis
5. **A/B Testing** - Compare models and prompts
6. **Performance Tuning** - Identify and optimize bottlenecks

---

*Quick Reference - See CODEBASE_ANALYSIS.md for detailed documentation*
