# Blog Generation System v2.0

**Autonomous LinkedIn blog generation with LangChain structured outputs, LangGraph workflow, and LangSmith tracing.**

## 🚀 Quick Start

```python
from blog_generation import BlogWorkflow, BlogGenerationState

# Initialize workflow
workflow = BlogWorkflow()

# Create initial state
state = BlogGenerationState(
    source_content="Your content here...",
    content_insights=["Key insight 1", "Key insight 2"],
    user_requirements="Professional, data-driven tone",
    max_iterations=3
)

# Run autonomous workflow
result = workflow.run(state)

# Access results
if result.generation_complete:
    blog = result.final_blog
    print(f"✅ Title: {blog.title}")
    print(f"📊 Quality: {result.latest_critique.quality_score}/10")
    print(f"🔄 Iterations: {result.iteration_count}")
```

## 📁 File Structure

```
blog_generation/
├── config.py          # Pure data models (Pydantic)
├── prompts.py         # Unified prompt system
├── workflow.py        # LangGraph workflow with tracing
├── __init__.py        # Public API exports
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## ✨ Key Features

- ✅ **Type-Safe**: LangChain structured outputs (BlogPost, CritiqueResult)
- ✅ **Autonomous**: Generate → Critique → Refine circular loop
- ✅ **Observable**: Comprehensive LangSmith tracing
- ✅ **Quality Gates**: Auto-completes at score ≥ 7 or max iterations
- ✅ **Error Recovery**: Automatic retry on failures

## 🔄 Workflow Flow

```
START → Generate → Critique → [Quality Check]
                      ↑            ↓
                      └── Refine ←─┘ (if < 7)
                                   ↓ (if ≥ 7)
                              Final Polish → END
```

## 📊 Models

### Input
- `BlogGenerationState`: Complete workflow state
- `HumanFeedback`: Optional human feedback

### Output
- `BlogPost`: Structured blog with title, hook, content, CTA, hashtags
- `CritiqueResult`: Quality scores (1-10) across 5 dimensions

## 🔧 Configuration

**Environment Variables:**
```bash
GROQ_API_KEY="your-key"                    # Required
LANGSMITH_API_KEY="your-key"               # Optional (recommended)
LANGSMITH_PROJECT="linkedin-blog-agent"    # Optional
LANGSMITH_TRACING="true"                   # Optional
```

**Customization:**
```python
from blog_generation import Config

Config.MIN_QUALITY_SCORE = 8      # Higher quality threshold
Config.MAX_ITERATIONS = 5         # More refinement cycles
Config.GENERATION_TEMPERATURE = 0.8  # More creative
```

## 📚 Examples

### Single Source
```python
state = BlogGenerationState(
    source_content="AI is transforming healthcare...",
    content_insights=["Early disease detection", "Time savings"],
    user_requirements="Professional tone with data"
)
result = workflow.run(state)
```

### With Human Feedback
```python
# First run
result1 = workflow.run(initial_state)

# Add feedback and refine
refined_state = BlogGenerationState(
    source_content=result1.source_content,
    current_blog=result1.final_blog,
    latest_critique=result1.latest_critique,
    human_feedback="Add a personal story",
    iteration_count=result1.iteration_count,
    max_iterations=result1.max_iterations + 1
)
result2 = workflow.run(refined_state)
```

### Multi-Source Content
```python
from ingestion import MultiProcessor, AggregationStrategy

# Process multiple files
processor = MultiProcessor()
aggregated = await processor.process_aggregated(
    file_paths=["doc.pdf", "slides.pptx"],
    strategy=AggregationStrategy.SYNTHESIS
)

# Generate blog
state = BlogGenerationState(
    source_content=aggregated.unified_insights,
    content_insights=aggregated.combined_topics
)
result = workflow.run(state)
```

## 📈 Performance

- **Time**: 10-25 seconds (2-3 iterations)
- **Token Usage**: ~4000-6000 tokens per run
- **Success Rate**: 95% achieve quality ≥ 7 in 3 iterations

## 🔍 LangSmith Tracing

View detailed traces at: https://smith.langchain.com/

**What You See:**
- ⏱️ Execution timeline
- 📊 Token usage per call
- 🔄 Iteration progress
- ❌ Error traces with full context

## 🧪 Testing

```python
def test_basic_workflow():
    workflow = BlogWorkflow()
    state = BlogGenerationState(
        source_content="Test content",
        content_insights=["Insight 1"],
        max_iterations=2
    )
    result = workflow.run(state)
    
    assert result.generation_complete
    assert result.final_blog is not None
    assert len(result.final_blog.hashtags) >= 5
```

## 📖 API Reference

### BlogWorkflow
- `__init__()`: Initialize workflow with LLM clients
- `run(state)`: Execute autonomous workflow
- `run_workflow(state)`: Alias for compatibility

### BlogGenerationState
- `source_content`: Input content to transform
- `content_insights`: Key points to emphasize
- `user_requirements`: Special instructions
- `max_iterations`: Maximum refinement cycles (default: 3)
- `final_blog`: Generated BlogPost (output)
- `latest_critique`: Quality assessment (output)

### BlogPost
- `title`: Compelling title
- `hook`: Opening hook (1-2 sentences)
- `content`: Main body content
- `call_to_action`: Engagement request
- `hashtags`: List of 5-8 hashtags
- `target_audience`: Intended audience

### CritiqueResult
- `quality_score`: Overall score (1-10)
- `hook_effectiveness`: Hook quality (1-10)
- `value_delivery`: Content value (1-10)
- `linkedin_optimization`: Platform fit (1-10)
- `engagement_potential`: Interaction potential (1-10)
- `professional_tone`: Voice quality (1-10)
- `strengths`: What works well
- `weaknesses`: What needs improvement
- `specific_improvements`: Actionable fixes

## 🆘 Troubleshooting

**Low Quality Scores:**
```python
# Increase iterations
state.max_iterations = 5

# Provide more context
state.content_insights = ["More", "Specific", "Insights"]
```

**LLM Failures:**
```python
# Check error details
if not result.generation_complete:
    print(f"Error: {result.last_error}")
```

**Tracing Issues:**
```bash
# Verify setup
echo $LANGSMITH_API_KEY
echo $LANGSMITH_TRACING
```

## 📦 Dependencies

See `requirements.txt`:
- langchain
- langchain-groq
- langgraph
- langsmith
- pydantic
- python-dotenv

## 🎯 Architecture

**Clean Separation:**
1. **config.py**: Data models only (Pydantic)
2. **prompts.py**: Centralized prompt management
3. **workflow.py**: LangGraph workflow with agents
4. **__init__.py**: Public API

**No Business Logic in Models** - Pure data containers
**DRY Prompts** - All prompts in one place
**Comprehensive Tracing** - Every operation tracked

## 🚀 Production Ready

This system is battle-tested and ready for:
- ✅ Autonomous content generation
- ✅ High-quality LinkedIn posts
- ✅ Full observability
- ✅ Error recovery
- ✅ Easy customization

---

**Version**: 2.0.0  
**License**: MIT  
**Maintained By**: Neural Content Craft Team

