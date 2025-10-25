# Chatbot System v2.0

**Simplified conversational interface for autonomous blog generation.**

## 🚀 Quick Start

```python
from chatbot import ChatbotOrchestrator

# Initialize chatbot (creates new session)
bot = ChatbotOrchestrator()

# Or resume existing session
bot = ChatbotOrchestrator(session_id="session_abc123")

# Process user input
response = await bot.process_message("Create a post about AI in healthcare")

# With file upload
response = await bot.process_message(
    "Make this technical",
    file_path="/path/to/document.pdf"
)

# Get current blog draft
blog = bot.get_current_blog()
```

## 📁 File Structure

```
chatbot/
├── config.py         # Pure data models (Pydantic)
├── memory.py         # Conversation memory with LangChain
├── orchestrator.py   # Main chatbot logic
├── __init__.py       # Public API exports
└── README.md         # This file
```

## ✨ Key Features

- ✅ **Simple**: 3 clean files, ~800 lines total
- ✅ **Stateful**: Persistent conversation memory
- ✅ **Integrated**: Works seamlessly with blog workflow
- ✅ **Observable**: Comprehensive LangSmith tracing
- ✅ **Intent Detection**: Pattern-based routing (no extra LLM calls)

## 🔄 Conversation Flow

```
User Input
    ↓
Intent Detection (pattern matching)
    ↓
├── File? → Ingestion → Blog Generation
├── Text? → Blog Generation
├── Feedback? → Refinement
├── Approval? → Complete
└── General? → Guide User
    ↓
Update Memory
    ↓
Return Response
```

## 📊 Models

### ConversationState
Complete session state with persistence:
- `session_id`: Unique identifier
- `current_stage`: ChatStage (4 stages)
- `messages`: List of ChatMessage
- `blog_context`: Optional BlogContext
- `blogs_completed`: Counter

### ChatMessage
Individual messages:
- `message_type`: USER | ASSISTANT | SYSTEM
- `content`: Message text
- `timestamp`: When sent
- `metadata`: Optional extras

### BlogContext
Active blog work:
- `source_content`: Original input
- `content_insights`: AI analysis
- `current_blog`: Latest draft
- `current_critique`: Quality assessment
- `blog_versions`: History
- `quality_scores`: Score progression

## 🎯 Chat Stages

1. **CONVERSING** - General conversation
2. **AWAITING_CONTENT** - Processing file/text
3. **REVIEWING_DRAFT** - User reviewing generated blog
4. **COMPLETED** - Blog approved, ready for next

## 💡 Usage Examples

### Example 1: File Upload

```python
bot = ChatbotOrchestrator()

# User uploads file
response = await bot.process_message(
    user_input="Create a professional post from this",
    file_path="research_paper.pdf"
)

# Bot automatically:
# 1. Processes file through ingestion
# 2. Generates blog post
# 3. Returns draft for review

print(response)
# 🎉 Your LinkedIn post is ready!
# Quality Score: 8/10
# ...
```

### Example 2: Text Content

```python
bot = ChatbotOrchestrator()

content = """
Artificial Intelligence is transforming healthcare.
AI-powered diagnostics detect diseases 40% earlier.
Hospitals save 2 hours per day on documentation.
"""

response = await bot.process_message(content)
# Automatically generates blog from text
```

### Example 3: Refinement with Feedback

```python
# After initial generation
response1 = await bot.process_message("Create a post about AI")

# User provides feedback
response2 = await bot.process_message("Make it more technical")
# Bot refines based on feedback

# More feedback
response3 = await bot.process_message("Add specific examples")
# Bot refines again

# Approve final version
response4 = await bot.process_message("Perfect!")
# 🎊 Great! Your LinkedIn post is ready to publish.
```

### Example 4: Session Resume

```python
# First session
bot1 = ChatbotOrchestrator()
print(bot1.session_id)  # "session_abc123"

# Generate blog
await bot1.process_message("Create post about Python")

# Later - resume same session
bot2 = ChatbotOrchestrator(session_id="session_abc123")

# Continue where left off
await bot2.process_message("Make it shorter")
```

## 🔧 Configuration

### Environment Variables

```bash
# Required for blog generation
GROQ_API_KEY="your-key"

# Optional for tracing
LANGSMITH_API_KEY="your-key"
LANGSMITH_PROJECT="linkedin-blog-agent"
LANGSMITH_TRACING="true"
```

### Customization

```python
from chatbot import ChatbotConfig

# Memory settings
ChatbotConfig.MEMORY_BUFFER_SIZE = 20  # Messages to keep
ChatbotConfig.SESSION_TIMEOUT_HOURS = 24

# Blog generation
ChatbotConfig.DEFAULT_MAX_ITERATIONS = 3
ChatbotConfig.DEFAULT_TONE = "Professional and engaging"
```

## 🧠 Intent Detection

Simple pattern-based detection (no extra LLM calls):

**File Upload**
- Triggered by: `file_path` parameter

**Text Content**
- Triggered by: Long text (>100 chars) OR phrases like:
  - "here's my content"
  - "create a post about"
  - "write about"

**Feedback**
- Must be in `REVIEWING_DRAFT` stage
- Triggered by: "make it", "change", "add more", "improve"

**Approval**
- Triggered by: "looks good", "perfect", "approved", "publish"

**Start Over**
- Triggered by: "start over", "new post", "something else"

**General Chat**
- Everything else (provides guidance)

## 🔍 LangSmith Tracing

Every operation traced:

```python
@trace_step("chatbot_process_message", "workflow")  # Main entry
@trace_step("handle_file_input", "workflow")        # File handling
@trace_step("handle_text_input", "workflow")        # Text handling
@trace_step("generate_blog", "workflow")            # Generation
@trace_step("handle_feedback", "workflow")          # Refinement
@trace_step("handle_approval", "workflow")          # Completion
```

**View in LangSmith:**
- User intent classification
- Processing time per step
- Memory operations
- Blog generation progress
- Error traces

## 📈 Performance

**Typical Flow:**
- Intent detection: <100ms (pattern matching)
- File processing: 3-8 seconds
- Blog generation: 10-25 seconds
- Refinement: 5-10 seconds

**Memory:**
- Session file: ~5-50KB per session
- Memory buffer: 20 messages (configurable)
- Auto-cleanup: After 24 hours

## 🆘 Troubleshooting

### Issue: Session Not Found

```python
# List all sessions
from chatbot import ConversationMemory

sessions = ConversationMemory.list_sessions()
print(sessions)

# Delete old session
ConversationMemory.delete_session("session_abc123")
```

### Issue: Bot Not Detecting Intent

```python
# Check current stage
info = bot.get_session_info()
print(info['current_stage'])

# Manually update stage
bot.memory.update_stage(ChatStage.CONVERSING)
```

### Issue: Feedback Not Working

**Requirements:**
1. Must have active blog context
2. Must be in `REVIEWING_DRAFT` stage
3. Feedback must contain keywords

```python
# Check blog context
blog_context = bot.memory.get_blog_context()
print(f"Has blog: {blog_context is not None}")

# Check stage
print(f"Stage: {bot.memory.get_current_stage()}")
```

## 🧪 Testing

```python
import asyncio
from chatbot import ChatbotOrchestrator

async def test_full_flow():
    # Initialize
    bot = ChatbotOrchestrator()
    
    # Generate blog
    response1 = await bot.process_message(
        "Create a post about Python programming"
    )
    assert "Quality Score:" in response1
    
    # Refine
    response2 = await bot.process_message(
        "Make it more beginner-friendly"
    )
    assert "Updated version" in response2
    
    # Approve
    response3 = await bot.process_message("Perfect!")
    assert "ready to publish" in response3
    
    print("✅ All tests passed!")

# Run test
asyncio.run(test_full_flow())
```

## 📚 API Reference

### ChatbotOrchestrator

**Main Methods:**

```python
async def process_message(user_input: str, file_path: str = None) -> str
    """Main entry point for all user input"""

def get_welcome_message() -> str
    """Get welcome message for new users"""

def get_session_info() -> Dict[str, Any]
    """Get current session information"""

def get_current_blog() -> Optional[Dict[str, Any]]
    """Get current blog draft"""

def get_conversation_history(count: int = 10) -> list
    """Get recent messages"""
```

### ConversationMemory

**Main Methods:**

```python
def add_user_message(content: str, metadata: dict = None) -> ChatMessage
def add_assistant_message(content: str, metadata: dict = None) -> ChatMessage

def create_blog_context(...) -> BlogContext
def add_blog_version(blog_post: dict, critique: dict, quality_score: int)
def add_feedback(feedback: str)

def update_stage(new_stage: ChatStage)
def complete_blog()
def clear_blog_context()

@staticmethod
def list_sessions() -> List[str]
@staticmethod
def delete_session(session_id: str)
```

## 🎯 Architecture

**Clean Separation:**
1. **config.py**: Data models only (Pydantic)
2. **memory.py**: State management + LangChain integration
3. **orchestrator.py**: Intent routing + business logic

**No Heavy Dependencies:**
- No separate LLM for intent classification
- Pattern-based intent detection
- Thin integration layer

**Integration Points:**
- `ingestion.UnifiedProcessor` for file processing
- `blog_generation.BlogWorkflow` for blog creation
- LangChain memory for conversation context

## 📊 Comparison: Before vs After

| Aspect | Before | After |
|--------|--------|-------|
| **Files** | 7 files | 4 files (3 core + README) |
| **LoC** | ~1,500 lines | ~800 lines |
| **Intent Detection** | Separate LLM agent | Pattern matching |
| **Complexity** | High | Low |
| **Latency** | ~1-2s for intent | <100ms for intent |
| **Maintainability** | Medium | High |

## 🚀 Production Ready

This system is ready for:
- ✅ Multi-user conversations
- ✅ Session persistence
- ✅ Error recovery
- ✅ File uploads
- ✅ Iterative refinement
- ✅ Full observability

---

**Version**: 2.0.0  
**License**: MIT  
**Maintained By**: Neural Content Craft Team
