# Chatbot Subsystem Documentation

## 🎯 Overview

The chatbot subsystem provides an intelligent conversational interface for LinkedIn blog creation. It features persistent memory, context-aware intent recognition, and seamless integration with ingestion and blog generation systems.

## 🏗️ Architecture

```
┌─────────────────────┐
│ ChatbotOrchestrator │ ◄── Main Conversation Manager
└─────────┬───────────┘
          │
          ├── ConversationMemoryManager (LangChain + Persistent Storage)
          ├── ContextualIntentRecognizer (Pattern + LLM-based)
          ├── UnifiedProcessor (File Processing)
          ├── BlogGenerationWorkflow (Content Creation)
          └── MultiFileProcessor (Multi-file Aggregation)

Conversation Flow:
User Input → Intent Recognition → Route to Handler → Process → 
Update Memory → Generate Response → Track Context
```

## 📁 File Structure

```
chatbot/
├── chatbot_orchastrator.py   # Main conversation manager
├── conversation_memory.py     # Persistent memory & LangChain integration
├── intent_recognition.py     # Intent classification & entity extraction
├── config.py                 # Data models & conversation states
├── main.py                   # Interactive CLI interface
└── README.md                 # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from chatbot.chatbot_orchastrator import ChatbotOrchestrator

# Create chatbot session
bot = ChatbotOrchestrator()

# Process user input
response = await bot.process_user_input(
    "I want to create a LinkedIn post about machine learning"
)
print(response)

# Continue conversation
response = await bot.process_user_input(
    "Make it more technical and add code examples"
)
print(response)
```

### Interactive Mode

```python
from chatbot.main import InteractiveChatbot

chatbot = InteractiveChatbot()
chatbot.start_interactive_session()
```

### Session Management

```python
# Create specific session
bot = ChatbotOrchestrator(session_id="user_123")

# Resume existing session
bot = ChatbotOrchestrator(session_id="existing_session")

# Export conversation
conversation_data = bot.export_conversation()
```

## 📊 Data Models

### ChatMessage

```python
class ChatMessage(BaseModel):
    message_id: str                    # Unique message identifier
    message_type: MessageType          # user/assistant/system/file_upload
    content: str                       # Message content
    timestamp: datetime               # When message was sent
    metadata: Dict[str, Any]          # Additional data
    file_path: Optional[str]          # Associated file (if any)
    blog_data: Optional[Dict[str, Any]]  # Blog context (if relevant)
```

### BlogContext

```python
class BlogContext(BaseModel):
    source_file_path: Optional[str]    # Original file
    source_content: str               # Extracted content
    ai_analysis: str                  # AI analysis results
    key_insights: List[str]           # Extracted insights
    current_draft: Optional[Dict[str, Any]]  # Current blog draft
    draft_history: List[Dict[str, Any]]      # All draft versions
    quality_scores: List[int]         # Quality progression
    user_requirements: str            # User specifications
    feedback_history: List[str]       # All feedback provided
```

### ConversationState

```python
class ConversationState(BaseModel):
    session_id: str                   # Unique session identifier
    current_stage: ChatStage          # Current conversation stage
    messages: List[ChatMessage]       # All messages in session
    blog_context: Optional[BlogContext]  # Current blog being worked on
    user_preferences: Dict[str, Any]  # User preferences
    created_at: datetime             # Session creation time
    last_updated: datetime           # Last activity time
    total_blogs_generated: int       # Number of completed blogs
```

### UserIntent

```python
class UserIntent(BaseModel):
    intent_type: str                  # Detected intent category
    confidence: float                # Confidence score (0-1)
    entities: Dict[str, str]         # Extracted entities
    file_path: Optional[str]         # File reference (if any)
    feedback_type: Optional[str]     # Type of feedback (if applicable)
    specific_requests: List[str]     # Specific change requests
```

## 🗨️ Conversation Stages

### Stage Flow

```python
class ChatStage(str, Enum):
    INITIAL = "initial"                    # Welcome state
    AWAITING_INPUT = "awaiting_input"      # Waiting for content
    PROCESSING_FILE = "processing_file"    # Processing uploaded file
    ANALYZING_CONTENT = "analyzing_content" # AI analysis in progress
    GENERATING_BLOG = "generating_blog"    # Creating blog post
    PRESENTING_DRAFT = "presenting_draft"  # Showing generated content
    AWAITING_FEEDBACK = "awaiting_feedback" # Waiting for user feedback
    REFINING_BLOG = "refining_blog"        # Improving based on feedback
    COMPLETED = "completed"                # Blog approved and saved
    ERROR = "error"                        # Error state
```

### Stage Transitions

```
INITIAL → AWAITING_INPUT → PROCESSING_FILE → ANALYZING_CONTENT → 
GENERATING_BLOG → PRESENTING_DRAFT → AWAITING_FEEDBACK → 
REFINING_BLOG → PRESENTING_DRAFT (loop) → COMPLETED
```

## 🧠 Intent Recognition

### Intent Types

```python
INTENT_PATTERNS = {
    "file_upload": [
        "process this file", "analyze document", "upload", "file"
    ],
    "start_blog": [
        "create blog", "generate post", "write article", "linkedin post"
    ],
    "provide_feedback": [
        "change", "improve", "modify", "different", "better"
    ],
    "approve_draft": [
        "looks good", "approve", "perfect", "publish", "ready"
    ],
    "start_over": [
        "start over", "new blog", "restart", "fresh start"
    ],
    "ask_question": [
        "what", "how", "why", "help", "can you"
    ]
}
```

### Pattern-Based Recognition

```python
def _pattern_based_recognition(self, user_input: str, current_stage: ChatStage) -> UserIntent:
    user_input_lower = user_input.lower().strip()
    
    # Stage-specific intent detection
    if current_stage == ChatStage.AWAITING_FEEDBACK:
        return self._detect_feedback_intent(user_input_lower)
    
    # General intent detection
    intent_scores = {}
    for intent, keywords in self.patterns.items():
        score = self._calculate_keyword_score(user_input_lower, keywords)
        if score > 0:
            intent_scores[intent] = score
    
    # Return best match
    if intent_scores:
        best_intent = max(intent_scores.items(), key=lambda x: x[1])
        return UserIntent(intent_type=best_intent[0], confidence=best_intent[1])
```

### LLM-Enhanced Recognition

```python
def _llm_based_recognition(self, user_input: str, current_stage: ChatStage) -> UserIntent:
    system_prompt = f"""
    Analyze user message and classify intent. Current stage: {current_stage}
    
    Respond with JSON:
    {{
      "intent_type": "file_upload|start_blog|provide_feedback|approve_draft|start_over|ask_question",
      "confidence": 0.0-1.0,
      "entities": {{"key": "value"}},
      "feedback_type": "content|style|tone|structure|general",
      "specific_requests": ["list of specific changes"]
    }}
    """
    
    response = self.llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ])
    
    return UserIntent(**json.loads(response.content))
```

## 💾 Memory Management

### LangChain Integration

```python
class ConversationMemoryManager:
    def __init__(self, session_id: str):
        self.session_id = session_id
        
        # LangChain conversation buffer memory
        self.langchain_memory = ConversationBufferWindowMemory(
            k=ChatbotConfig.MEMORY_BUFFER_SIZE,
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Load persistent state
        self.conversation_state = self._load_or_create_state()
        self._sync_langchain_memory()
```

### Persistent Storage

```python
def _save_state(self):
    """Save conversation state to disk"""
    state_file = self.memory_dir / f"{self.session_id}.json"
    
    # Convert to dict with datetime serialization
    state_dict = self.conversation_state.dict()
    state_dict['created_at'] = self.conversation_state.created_at.isoformat()
    state_dict['last_updated'] = self.conversation_state.last_updated.isoformat()
    
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state_dict, f, indent=2, ensure_ascii=False)
```

### Context Management

```python
def get_context_for_llm(self) -> Dict[str, Any]:
    """Get context for LLM processing"""
    context = {
        "session_id": self.session_id,
        "current_stage": self.conversation_state.current_stage,
        "message_count": len(self.conversation_state.messages),
        "blogs_generated": self.conversation_state.total_blogs_generated
    }
    
    if self.conversation_state.blog_context:
        blog_ctx = self.conversation_state.blog_context
        context.update({
            "has_current_draft": bool(blog_ctx.current_draft),
            "draft_iterations": len(blog_ctx.draft_history),
            "feedback_count": len(blog_ctx.feedback_history),
            "latest_quality_score": blog_ctx.quality_scores[-1] if blog_ctx.quality_scores else None
        })
    
    return context
```

## 🎛️ Request Handlers

### File Upload Handler

```python
async def _handle_file_upload(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
    """Handle file upload and processing"""
    
    # Determine file path
    target_file = file_path or intent.entities.get("file_path")
    
    if not target_file or not os.path.exists(target_file):
        return "File not found. Please check the path and try again."
    
    # Update stage and process file
    self._update_stage(ChatStage.PROCESSING_FILE)
    
    try:
        # Process through ingestion system
        result = self.ingestion_processor.process_file(target_file)
        
        if not result.success:
            return f"Error processing file: {result.error_message}"
        
        # Update blog context
        blog_context = BlogContext(
            source_file_path=target_file,
            source_content=result.extracted_content.raw_text,
            ai_analysis=result.ai_analysis,
            key_insights=result.key_insights
        )
        self.memory.update_blog_context(blog_context)
        
        # Automatically start blog generation
        self._update_stage(ChatStage.GENERATING_BLOG)
        return await self._generate_initial_blog()
        
    except Exception as e:
        self._update_stage(ChatStage.ERROR)
        return f"Processing failed: {str(e)}"
```

### Feedback Handler

```python
async def _handle_provide_feedback(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
    """Handle user feedback for blog refinement"""
    
    blog_context = self.memory.get_blog_context()
    if not blog_context or not blog_context.current_draft:
        return "No current draft to improve. Would you like to create a new blog post?"
    
    # Add feedback to context
    self.memory.add_feedback(user_input)
    
    # Create human feedback object
    human_feedback = HumanFeedback(
        feedback_text=user_input,
        satisfaction_level=3,  # Default moderate
        specific_changes=intent.specific_requests or [],
        approve_current=False
    )
    
    # Refine blog using workflow
    self._update_stage(ChatStage.REFINING_BLOG)
    return await self._refine_blog_with_feedback(user_input, intent)
```

### Multi-File Handler

```python
async def _handle_multi_file_upload(self, intent: UserIntent, user_input: str, file_paths: List[str] = None) -> str:
    """Handle multiple file aggregation"""
    
    if len(file_paths) < 2:
        return "Multi-file processing requires at least 2 files."
    
    # Detect aggregation strategy
    strategy = self._detect_aggregation_strategy(user_input)
    
    # Process files
    multi_source_content = await self.multi_file_processor.process_multiple_files(
        file_paths, strategy
    )
    
    # Update context and generate blog
    blog_context = BlogContext(
        source_file_path=", ".join(file_paths),
        ai_analysis=f"Multi-source analysis using {strategy.value} strategy",
        key_insights=multi_source_content.unified_insights
    )
    
    self.memory.update_blog_context(blog_context)
    return await self._generate_initial_blog()
```

## 🔄 Response Templates

### Dynamic Responses

```python
RESPONSE_TEMPLATES = {
    "welcome": [
        "Hello! I'm {name}, your LinkedIn blog creation assistant! 🚀",
        "I can help you transform any content into engaging LinkedIn posts.",
        "Share text, upload files, or tell me what you'd like to write about!"
    ],
    "file_received": [
        "Great! I've received your {file_type} file: {filename}",
        "Let me analyze this content for you... 🔍"
    ],
    "processing_complete": [
        "✅ Analysis complete! Here's what I found:",
        "📊 Content length: {length} characters",
        "💡 Key insights extracted: {insights_count}",
        "Now I'll generate an engaging LinkedIn post..."
    ]
}
```

### Context-Aware Responses

```python
def _get_help_response(self) -> str:
    """Get contextual help based on current stage"""
    help_text = [
        f"Hi! I'm {ChatbotConfig.CHATBOT_NAME}, your LinkedIn blog assistant! 🤖",
        "",
        "📁 **File Processing:** Upload PDFs, Word docs, PowerPoint, code files",
        "📝 **Text Input:** Share any text content",
        "✨ **Blog Generation:** I'll create engaging LinkedIn posts",
        "🔄 **Refinement:** Give feedback and I'll improve the post",
        "",
        f"**Current stage:** {self.current_stage.replace('_', ' ').title()}",
        "Just tell me what you'd like to create a post about!"
    ]
    return "\n".join(help_text)
```

## 🧪 Testing

### Unit Tests

```python
# Test intent recognition
def test_intent_recognition():
    recognizer = ContextualIntentRecognizer()
    
    # Test file upload intent
    intent = recognizer.recognize_intent("Please process this PDF file")
    assert intent.intent_type == "file_upload"
    assert intent.confidence > 0.7
    
    # Test feedback intent
    intent = recognizer.recognize_intent("Make it more engaging", ChatStage.PRESENTING_DRAFT)
    assert intent.intent_type == "provide_feedback"

# Test memory management
def test_memory_persistence():
    memory = ConversationMemoryManager("test_session")
    
    # Add messages
    memory.add_message(MessageType.USER, "Hello")
    memory.add_message(MessageType.ASSISTANT, "Hi there!")
    
    # Verify persistence
    assert len(memory.conversation_state.messages) == 2
    
    # Test reload
    memory2 = ConversationMemoryManager("test_session")
    assert len(memory2.conversation_state.messages) == 2
```

### Integration Tests

```python
# Test complete conversation flow
async def test_complete_flow():
    bot = ChatbotOrchestrator()
    
    # Start conversation
    response1 = await bot.process_user_input("Hi!")
    assert "LinkedIn blog assistant" in response1
    
    # Upload file
    response2 = await bot.process_user_input("Process my document", file_path="test.pdf")
    assert "analysis complete" in response2.lower()
    
    # Provide feedback
    response3 = await bot.process_user_input("Make it more technical")
    assert "refining" in response3.lower()
    
    # Approve
    response4 = await bot.process_user_input("Perfect!")
    assert "approved" in response4.lower()
```

### Performance Tests

```python
# Test memory usage
def test_memory_usage():
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Create multiple sessions
    bots = [ChatbotOrchestrator() for _ in range(10)]
    
    final_memory = process.memory_info().rss
    memory_per_session = (final_memory - initial_memory) / len(bots)
    
    assert memory_per_session < 50 * 1024 * 1024  # Less than 50MB per session
```

## 🔧 Configuration

### Chatbot Settings

```python
class ChatbotConfig:
    # Memory Configuration
    MEMORY_BUFFER_SIZE = 20           # Messages in active memory
    SESSION_TIMEOUT_HOURS = 24        # Session expiration time
    
    # Processing Configuration  
    MAX_FILE_SIZE_MB = 50            # Maximum file size
    SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.pptx', ...]
    
    # Response Configuration
    MAX_RESPONSE_LENGTH = 2000        # Maximum response length
    TYPING_DELAY = 0.5               # Simulated typing delay
    
    # Blog Generation Configuration
    MAX_REFINEMENT_ITERATIONS = 3     # Maximum refinement cycles
    AUTO_IMPROVE_THRESHOLD = 6        # Auto-refine below this score
    
    # Personality Configuration
    CHATBOT_NAME = "BlogBot"
    PERSONALITY_TRAITS = {
        "helpful": True,
        "professional": True,
        "encouraging": True,
        "detail_oriented": True
    }
```

### Environment Variables

```bash
# Required API keys
GROQ_API_KEY=your_groq_key
GOOGLE_API_KEY=your_google_key

# Optional: Session configuration
CHAT_SESSION_TIMEOUT=24           # Hours
CHAT_MEMORY_SIZE=20              # Message buffer size
CHAT_MAX_FILE_SIZE=50            # MB

# Optional: Feature flags
ENABLE_MULTI_FILE=true
ENABLE_ADVANCED_INTENT=true
ENABLE_TYPING_SIMULATION=false
```

## 🔄 Conversation Examples

### File Upload Conversation

```
User: Hi! I have a research paper I'd like to turn into a LinkedIn post.

Bot: Hello! I'm BlogBot, your LinkedIn blog creation assistant! 🚀
     I'd be happy to help you create an engaging post from your research paper.
     Please share your file, and I'll analyze the content for you.

User: [uploads research_paper.pdf]

Bot: Great! I've received your PDF file: research_paper.pdf
     Let me analyze this content for you... 🔍
     
     ✅ Analysis complete! Here's what I found:
     📊 Content length: 15,847 characters
     💡 Key insights extracted: 7
     
     Now I'll generate an engaging LinkedIn post based on this content...
     
     🎉 Your LinkedIn blog post is ready! Here's the draft:
     [Generated blog post content]
     
     📈 Quality Score: 8/10
     
     What do you think? You can ask me to make specific changes!

User: This looks great, but can you make it more accessible to non-researchers?

Bot: Got it! Let me refine the post to make it more accessible for a general professional audience...
     
     ✨ Here's your refined version:
     [Improved blog post with simpler language]
     
     📈 New Quality Score: 9/10
     
     I've simplified the technical jargon and added more context for general readers.

User: Perfect! I approve this version.

Bot: ✅ Blog approved and finalized! Your LinkedIn post is ready to publish.
     Would you like to create another post or need help with anything else?
```

### Multi-File Conversation

```
User: I want to create a comprehensive post comparing AI frameworks from multiple sources.

Bot: Excellent idea! I can help you create a comprehensive comparison post.
     For multi-source content, please upload 2-10 files and I'll aggregate them using an appropriate strategy.

User: I have three files: tensorflow_guide.pdf, pytorch_tutorial.py, and comparison_chart.png

Bot: Perfect! I'll process these three files using a comparison strategy since you mentioned comparing frameworks.
     
     📁 Processing 3 files for aggregation:
        1. tensorflow_guide.pdf (PDF)
        2. pytorch_tutorial.py (CODE)  
        3. comparison_chart.png (IMAGE)
     
     ✅ Multi-file processing complete!
        📊 Strategy: comparison
        📝 Sources: 3
        🔗 Cross-references: 2
        💡 Unified insights: 8
     
     🎉 Your comprehensive LinkedIn post is ready!
     [Generated comparison post incorporating all sources]
     
     This post synthesizes insights from your PDF guide, code tutorial, and comparison chart.

User: Great! Can you emphasize the practical applications more?

Bot: Absolutely! Let me enhance the practical applications section...
     [Refined post with more practical focus]
     
     I've added more real-world use cases and practical implementation tips.
```

## 📈 Analytics & Insights

### Conversation Analytics

```python
def get_session_analytics(session_id: str) -> Dict[str, Any]:
    """Get detailed session analytics"""
    memory = ConversationMemoryManager(session_id)
    state = memory.conversation_state
    
    return {
        "session_duration": (state.last_updated - state.created_at).total_seconds(),
        "message_count": len(state.messages),
        "blogs_generated": state.total_blogs_generated,
        "stages_visited": list(set(msg.metadata.get("stage") for msg in state.messages)),
        "file_types_processed": list(set(msg.metadata.get("file_type") for msg in state.messages if msg.file_path)),
        "avg_quality_score": sum(state.blog_context.quality_scores) / len(state.blog_context.quality_scores) if state.blog_context and state.blog_context.quality_scores else None,
        "feedback_cycles": len(state.blog_context.feedback_history) if state.blog_context else 0
    }
```

### User Behavior Patterns

```python
def analyze_user_patterns(sessions: List[str]) -> Dict[str, Any]:
    """Analyze patterns across multiple sessions"""
    patterns = {
        "common_intents": defaultdict(int),
        "stage_transitions": defaultdict(int),
        "file_type_preferences": defaultdict(int),
        "feedback_patterns": defaultdict(int)
    }
    
    for session_id in sessions:
        memory = ConversationMemoryManager(session_id)
        # Analyze patterns...
    
    return patterns
```

## 🔧 Customization

### Adding New Intent Types

1. **Define Intent Pattern:**
```python
# In config.py
INTENT_PATTERNS["new_intent"] = [
    "trigger phrase 1", "trigger phrase 2"
]
```

2. **Create Handler:**
```python
# In chatbot_orchestrator.py
async def _handle_new_intent(self, intent: UserIntent, user_input: str) -> str:
    # Your custom logic
    return "Response for new intent"
```

3. **Register Handler:**
```python
# In _route_intent method
handlers["new_intent"] = self._handle_new_intent
```

### Custom Response Templates

```python
# Add to RESPONSE_TEMPLATES
RESPONSE_TEMPLATES["custom_response"] = [
    "Your custom response template",
    "With variables: {variable1}, {variable2}"
]

# Use in handlers
response = self._get_response_template("custom_response").format(
    variable1="value1", variable2="value2"
)
```

### Personality Customization

```python
# Modify in config.py
PERSONALITY_TRAITS = {
    "helpful": True,
    "professional": True,
    "encouraging": True,
    "detail_oriented": True,
    "casual": False,        # Add custom traits
    "technical": True,
    "creative": False
}

# Adapt responses based on personality
def adapt_response_to_personality(self, response: str) -> str:
    if self.personality_traits.get("casual"):
        response = response.replace("excellent", "awesome")
    if self.personality_traits.get("technical"):
        response += "\n\nTechnical details available upon request."
    return response
```

## 🛠️ Deployment

### Session Scaling

```python
# For production: use Redis for session storage
class RedisMemoryManager(ConversationMemoryManager):
    def __init__(self, session_id: str, redis_client):
        self.redis_client = redis_client
        super().__init__(session_id)
    
    def _save_state(self):
        state_json = json.dumps(self.conversation_state.dict())
        self.redis_client.setex(
            f"session:{self.session_id}", 
            self.session_timeout, 
            state_json
        )
```

### Load Balancing

```python
# Stateless design allows horizontal scaling
@app.post("/api/chat/message")
async def chat_endpoint(request: ChatRequest):
    # Each request creates fresh orchestrator
    bot = ChatbotOrchestrator(request.session_id)
    response = await bot.process_user_input(request.message)
    return {"response": response}
```

### Monitoring

```python
# Add metrics collection
@trace_step("chat_message_processing", "workflow")
async def process_user_input(self, user_input: str) -> str:
    # Automatic LangSmith tracing
    # Custom metrics
    start_time = time.time()
    response = await self._process_message(user_input)
    
    # Log metrics
    self._log_metrics({
        "processing_time": time.time() - start_time,
        "session_id": self.session_id,
        "current_stage": self.current_stage,
        "response_length": len(response)
    })
    
    return response
```

---

**Next Steps:**
- See [API Documentation](../api.md) for REST endpoint integration
- See [Blog Generation README](../blog_generation/README.md) for workflow details
- See [Ingestion README](../ingestion/README.md) for file processing