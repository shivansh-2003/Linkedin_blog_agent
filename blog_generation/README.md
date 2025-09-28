# Blog Generation Subsystem Documentation

## 🎯 Overview

The blog generation subsystem uses LangGraph to orchestrate a sophisticated AI workflow that creates high-quality LinkedIn posts through a circular Generate → Critique → Refine process. It features multi-agent collaboration, quality gates, and human-in-the-loop optimization.

## 🏗️ Architecture

```
┌─────────────────┐
│ BlogGeneration  │ ◄── LangGraph Workflow
│    Workflow     │
└─────┬───────────┘
      │
      ├── Generate Content Node ──┐
      ├── Critique Content Node ──┼── Circular Flow
      ├── Refine Content Node ────┘
      ├── Human Review Node
      ├── Final Polish Node
      └── Error Recovery Node

Agents:
├── BlogGeneratorAgent    (Content creation)
├── CritiqueAgent        (Quality assessment)
└── RefinementAgent      (Iterative improvement)
```

## 📁 File Structure

```
blog_generation/
├── workflow.py           # LangGraph circular workflow
├── blog_generator.py     # Content generation agent
├── critique_agent.py     # Quality assessment agent
├── refinement_agent.py   # Content improvement agent
├── config.py            # Data models & configuration
├── prompt_templates.py  # Centralized prompts
├── main.py             # Standalone runner
├── requirements.txt    # Dependencies
└── README.md          # This file
```

## 🚀 Quick Start

### Basic Usage

```python
from blog_generation.workflow import BlogGenerationWorkflow
from blog_generation.config import BlogGenerationState

# Create workflow
workflow = BlogGenerationWorkflow()

# Create initial state
initial_state = BlogGenerationState(
    source_content="Your content here...",
    user_requirements="Professional tone for tech audience",
    max_iterations=3
)

# Run workflow
result = workflow.run_workflow(initial_state)

if result.final_blog:
    print(f"Title: {result.final_blog.title}")
    print(f"Content: {result.final_blog.content}")
    print(f"Quality Score: {result.latest_critique.quality_score}/10")
```

### With Human Feedback

```python
from blog_generation.config import HumanFeedback

# Add human feedback
feedback = HumanFeedback(
    feedback_text="Make it more engaging and add statistics",
    satisfaction_level=3,
    specific_changes=["Add data points", "Improve hook"],
    request_regeneration=False
)

# Update state and continue
updated_state = workflow.add_human_feedback(result, feedback)
final_result = workflow.run_workflow(updated_state)
```

### Multi-Source Content

```python
from blog_generation.config import AggregatedBlogGenerationState
from ingestion.multi_file_processor import MultiFileProcessor

# Process multiple files
processor = MultiFileProcessor()
multi_content = await processor.process_multiple_files(
    ["doc1.pdf", "code.py", "presentation.pptx"],
    AggregationStrategy.SYNTHESIS
)

# Generate blog from multiple sources
initial_state = AggregatedBlogGenerationState(
    source_content="",
    multi_source_content=multi_content,
    aggregation_strategy=AggregationStrategy.SYNTHESIS,
    user_requirements="Technical audience, engaging tone"
)

result = workflow.run_workflow(initial_state)
```

## 📊 Data Models

### BlogPost (Output)

```python
class BlogPost(BaseModel):
    title: str                              # Compelling title
    content: str                           # Full LinkedIn post
    hook: str                             # Opening hook
    hashtags: List[str]                   # 5-8 relevant hashtags
    call_to_action: str                   # Engagement CTA
    target_audience: str                  # Primary audience
    estimated_engagement_score: Optional[int]  # 1-10 prediction
```

### CritiqueResult (Quality Assessment)

```python
class CritiqueResult(BaseModel):
    quality_score: int                    # 1-10 overall score
    quality_level: BlogQuality           # draft/good/excellent/publish_ready
    strengths: List[str]                 # What works well
    weaknesses: List[str]                # Areas for improvement
    specific_improvements: List[str]      # Actionable suggestions
    tone_feedback: str                   # Tone analysis
    engagement_feedback: str             # Engagement potential
    linkedin_optimization_feedback: str   # Platform-specific tips
    approved_for_publish: bool           # Ready to publish?
```

### BlogGenerationState (Workflow State)

```python
class BlogGenerationState(BaseModel):
    # Input
    source_content: str                   # Original content
    content_insights: List[str]           # Key insights from ingestion
    user_requirements: str                # User specifications
    
    # Processing
    current_status: ProcessingStatus      # Current workflow stage
    iteration_count: int                  # Number of iterations
    max_iterations: int = 3               # Maximum iterations
    
    # Generated content
    current_blog: Optional[BlogPost]      # Latest version
    blog_history: List[BlogPost]          # All versions
    
    # Quality control
    latest_critique: Optional[CritiqueResult]  # Latest assessment
    critique_history: List[CritiqueResult]     # All assessments
    
    # Human interaction
    human_feedback: str                   # User feedback
    human_approved: bool                  # User approval
    
    # Output
    final_blog: Optional[BlogPost]        # Approved final version
    generation_complete: bool             # Workflow finished
```

## 🔄 Workflow Details

### 1. Generate Content Node

**Purpose:** Create initial LinkedIn post using AI

**Process:**
1. Analyze source content and insights
2. Apply user requirements
3. Generate structured blog post
4. Validate basic structure

**Agent:** `BlogGeneratorAgent`
**Model:** Groq Llama 3.3 70B (configurable)

```python
def generate_content_node(self, state) -> dict:
    blog_post, error = self.generator.generate_blog(state)
    if blog_post:
        state.current_blog = blog_post
        state.blog_history.append(blog_post)
    return updated_state_dict
```

### 2. Critique Content Node

**Purpose:** Assess quality across multiple dimensions

**Assessment Criteria:**
- **Hook Effectiveness** (1-10): Attention-grabbing potential
- **Value Delivery** (1-10): Actionable insights provided
- **LinkedIn Optimization** (1-10): Platform algorithm compatibility
- **Engagement Potential** (1-10): Comment/share likelihood
- **Professional Tone** (1-10): Authenticity and appropriateness

**Agent:** `CritiqueAgent`
**Model:** Groq Llama 3.3 70B (lower temperature for consistency)

```python
def critique_content_node(self, state) -> dict:
    critique, error = self.critic.critique_blog(state.current_blog)
    if critique:
        state.latest_critique = critique
        state.critique_history.append(critique)
    return updated_state_dict
```

### 3. Refine Content Node

**Purpose:** Improve content based on critique feedback

**Refinement Areas:**
- Strengthen weak hooks
- Enhance value delivery
- Improve engagement triggers
- Optimize for LinkedIn algorithm
- Maintain authentic voice

**Agent:** `RefinementAgent`
**Model:** Groq Llama 3.3 70B (moderate temperature)

```python
def refine_content_node(self, state) -> dict:
    focus_areas = self._extract_focus_areas(state.latest_critique)
    refined_post, error = self.refiner.refine_blog(
        original_post=state.current_blog,
        critique=state.latest_critique,
        focus_areas=focus_areas,
        human_feedback=state.human_feedback
    )
    return updated_state_dict
```

### 4. Routing Logic

**Quality Gate Routing:**
```python
def after_critique_routing(self, state) -> str:
    if not state.latest_critique:
        return "error_recovery"
    
    score = state.latest_critique.quality_score
    if score >= BlogConfig.MIN_QUALITY_SCORE:  # Default: 7
        return "final_polish"
    
    if state.iteration_count >= state.max_iterations:
        return "human_review"
    
    return "refine_content"
```

**Human Feedback Routing:**
```python
def after_human_review_routing(self, state) -> str:
    if state.human_approved:
        return "final_polish"
    
    feedback = state.human_feedback.lower()
    if "regenerate" in feedback:
        return "generate_content"
    
    if feedback.strip():
        return "refine_content"
    
    return "END"
```

## 🤖 AI Agent Details

### BlogGeneratorAgent

**Capabilities:**
- Content structure creation
- Hook generation
- LinkedIn optimization
- Hashtag selection
- CTA creation

**Prompt Strategy:**
```python
system_prompt = """
You are a LinkedIn content creation expert specializing in viral, engaging professional posts.
- Create content between 150-1300 characters for optimal engagement
- Include 5-8 relevant hashtags
- Start with powerful hook (first 1-2 sentences)
- End with clear call-to-action
- Focus on genuine value for professional audience
"""
```

### CritiqueAgent

**Capabilities:**
- Multi-dimensional quality assessment
- LinkedIn-specific optimization analysis
- Engagement potential prediction
- Constructive feedback generation

**Analysis Framework:**
```python
evaluation_criteria = {
    "hook_effectiveness": "Does opening grab attention?",
    "value_delivery": "Does content provide clear value?",
    "linkedin_optimization": "Is it optimized for LinkedIn algorithm?",
    "engagement_potential": "Will it generate comments/shares?",
    "professional_tone": "Is voice authentic and appropriate?"
}
```

### RefinementAgent

**Capabilities:**
- Targeted improvement implementation
- Strength preservation
- Weakness addressing
- Iterative enhancement

**Refinement Principles:**
- Preserve what's working well
- Address critique points systematically
- Enhance rather than completely rewrite
- Maintain original message and value

## 🎛️ Configuration

### Model Selection

```python
class ProcessingModel(str, Enum):
    GROQ_LLAMA_70B = "llama-3.3-70b-versatile"     # Primary
    GROQ_LLAMA_8B = "llama-3.1-8b-instant"        # Fallback
    GROQ_GEMMA = "gemma2-9b-it"                    # Fallback
    GROQ_GPT_OSS_20B = "openai/gpt-oss-20b"       # Alternative
```

### Quality Thresholds

```python
class BlogConfig:
    MIN_QUALITY_SCORE = 7         # Minimum score to approve
    EXCELLENT_THRESHOLD = 9       # Excellent quality threshold
    MAX_ITERATIONS = 3            # Maximum refinement cycles
    TEMPERATURE = 0.7             # Generation creativity
    MAX_TOKENS = 2500            # Response length limit
```

### LinkedIn Optimization

```python
OPTIMAL_POST_LENGTH = (150, 1300)    # Character range
MAX_HASHTAGS = 8                     # Maximum hashtags
IDEAL_HASHTAGS = 5                   # Ideal hashtag count

REQUIRED_ELEMENTS = [
    "engaging_hook",
    "clear_value_proposition",
    "actionable_insights", 
    "call_to_action"
]
```

## 🧪 Testing

### Unit Tests

```bash
# Test individual agents
python -m pytest blog_generation/tests/test_blog_generator.py
python -m pytest blog_generation/tests/test_critique_agent.py
python -m pytest blog_generation/tests/test_refinement_agent.py

# Test workflow
python -m pytest blog_generation/tests/test_workflow.py
```

### Integration Tests

```bash
# Test complete workflow
python blog_generation/main.py

# Test with different content types
python blog_generation/tests/test_integration.py
```

### Quality Tests

```bash
# Test quality assessment
python blog_generation/tests/test_quality_gates.py

# Test human feedback integration
python blog_generation/tests/test_human_feedback.py
```

## 🔧 Customization

### Adding New Quality Criteria

1. **Update CritiqueResult:**
```python
class CritiqueResult(BaseModel):
    # Existing fields...
    new_criterion_score: int = Field(ge=1, le=10)
    new_criterion_feedback: str = ""
```

2. **Update Critique Prompts:**
```python
# In prompt_templates.py
CRITIQUE_CRITERIA = {
    # Existing criteria...
    "new_criterion": "Assessment description"
}
```

3. **Update Routing Logic:**
```python
# In workflow.py
def quality_gate_check(self, critique: CritiqueResult) -> bool:
    return (critique.quality_score >= threshold and
            critique.new_criterion_score >= new_threshold)
```

### Custom Content Templates

1. **Create Template:**
```python
# In prompt_templates.py
CUSTOM_TEMPLATE = PromptTemplate(
    input_variables=["content", "audience", "tone"],
    template="""Create a LinkedIn post for {audience} with {tone} tone:
    Content: {content}
    Requirements: [Your custom requirements]
    """
)
```

2. **Register Template:**
```python
# In blog_generator.py
def generate_custom_content(self, content, audience, tone):
    prompt = CUSTOM_TEMPLATE.format(
        content=content, audience=audience, tone=tone
    )
    return self.llm.invoke([HumanMessage(content=prompt)])
```

### Multi-Source Strategies

```python
# Add new aggregation strategy
class AggregationStrategy(str, Enum):
    SYNTHESIS = "synthesis"
    COMPARISON = "comparison"
    SEQUENCE = "sequence"
    TIMELINE = "timeline"
    CUSTOM_STRATEGY = "custom"     # Your new strategy
```





### With API

```python
# FastAPI endpoint
@app.post("/api/generate-blog")
async def generate_blog(request: BlogRequest):
    initial_state = BlogGenerationState(
        source_content=request.text,
        user_requirements=f"Audience: {request.target_audience}, Tone: {request.tone}",
        max_iterations=request.max_iterations
    )
    
    result = workflow.run_workflow(initial_state)
    
    return BlogResponse(
        success=result.current_status == ProcessingStatus.COMPLETED,
        blog_post=result.final_blog.dict() if result.final_blog else None,
        quality_score=result.latest_critique.quality_score if result.latest_critique else None
    )
```


---

**Next Steps:**
- See [Chatbot README](../chatbot/README.md) for conversational interface
- See [Ingestion README](../ingestion/README.md) for content processing
- See [API Documentation](../api.md) for REST endpoints