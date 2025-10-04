import os
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from enum import Enum
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BlogQuality(str, Enum):
    DRAFT = "draft"
    GOOD = "good"
    EXCELLENT = "excellent"
    PUBLISH_READY = "publish_ready"

class AgentRole(str, Enum):
    GENERATOR = "content_generator"
    CRITIC = "content_critic"
    REFINER = "content_refiner"

class ProcessingStatus(str, Enum):
    GENERATING = "generating"
    CRITIQUING = "critiquing"
    REFINING = "refining"
    COMPLETED = "completed"
    FAILED = "failed"

# Import from shared models to avoid circular imports
from shared.models import AggregationStrategy

class BlogPost(BaseModel):
    title: str
    content: str
    hook: str = ""
    hashtags: List[str] = Field(default_factory=list)
    call_to_action: str = ""
    target_audience: str = ""
    estimated_engagement_score: Optional[int] = None

class CritiqueResult(BaseModel):
    quality_score: int = Field(ge=1, le=10)  # 1-10 scale
    quality_level: BlogQuality
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    specific_improvements: List[str] = Field(default_factory=list)
    tone_feedback: str = ""
    engagement_feedback: str = ""
    linkedin_optimization_feedback: str = ""
    approved_for_publish: bool = False

class RefinementRequest(BaseModel):
    original_post: BlogPost
    critique: CritiqueResult
    focus_areas: List[str] = Field(default_factory=list)
    preserve_elements: List[str] = Field(default_factory=list)

class BlogGenerationState(BaseModel):
    # Input
    source_content: str = ""
    source_file_path: str = ""
    content_insights: List[str] = Field(default_factory=list)
    user_requirements: str = ""
    
    # Processing state
    current_status: ProcessingStatus = ProcessingStatus.GENERATING
    iteration_count: int = 0
    max_iterations: int = 3
    
    # Generated content
    current_blog: Optional[BlogPost] = None
    blog_history: List[BlogPost] = Field(default_factory=list)
    
    # Quality control
    latest_critique: Optional[CritiqueResult] = None
    critique_history: List[CritiqueResult] = Field(default_factory=list)
    
    # Human feedback
    human_feedback: str = ""
    human_approved: bool = False
    
    # Error handling
    error_count: int = 0
    max_errors: int = 3
    last_error: str = ""
    
    # Final output
    final_blog: Optional[BlogPost] = None
    generation_complete: bool = False

class HumanFeedback(BaseModel):
    feedback_text: str
    satisfaction_level: int = Field(ge=1, le=5)  # 1-5 scale
    specific_changes: List[str] = Field(default_factory=list)
    approve_current: bool = False
    request_regeneration: bool = False

class BlogConfig:
    # API Configuration
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # If using OpenAI fallback
    
    # Model Configuration
    PRIMARY_MODEL = "openai/gpt-oss-20b"
    
    # Generation Parameters
    MAX_ITERATIONS = 3
    MAX_ERRORS = 3
    TEMPERATURE = 0.7
    MAX_TOKENS = 2500
    
    # Quality Thresholds
    MIN_QUALITY_SCORE = 7  # Minimum score to approve for publish
    EXCELLENT_THRESHOLD = 9
    
    # LinkedIn Optimization
    OPTIMAL_POST_LENGTH = (150, 1300)  # Character range
    MAX_HASHTAGS = 8
    IDEAL_HASHTAGS = 5
    
    # Content Guidelines
    REQUIRED_ELEMENTS = [
        "engaging_hook",
        "clear_value_proposition", 
        "actionable_insights",
        "call_to_action"
    ]
    
    TONE_OPTIONS = [
        "professional",
        "conversational", 
        "educational",
        "inspiring",
        "thought_leadership"
    ]
    
    # Engagement Factors
    ENGAGEMENT_FACTORS = [
        "storytelling",
        "personal_anecdotes",
        "industry_insights",
        "actionable_tips",
        "controversial_takes",
        "data_points",
        "questions_to_audience"
    ]

class ValidationRules:
    """Content validation rules for quality gates"""
    
    @staticmethod
    def validate_blog_structure(blog: BlogPost) -> List[str]:
        """Validate basic blog structure"""
        issues = []
        
        if not blog.title or len(blog.title.strip()) < 10:
            issues.append("Title is too short or missing")
        
        if not blog.hook or len(blog.hook.strip()) < 20:
            issues.append("Hook is too short or missing")
            
        if not blog.content or len(blog.content.strip()) < 100:
            issues.append("Content is too short (minimum 100 characters)")
            
        if len(blog.content) > 3000:
            issues.append("Content is too long (maximum 3000 characters)")
            
        if not blog.hashtags or len(blog.hashtags) < 3:
            issues.append("Need at least 3 hashtags")
            
        if len(blog.hashtags) > BlogConfig.MAX_HASHTAGS:
            issues.append(f"Too many hashtags (maximum {BlogConfig.MAX_HASHTAGS})")
            
        if not blog.call_to_action or len(blog.call_to_action.strip()) < 10:
            issues.append("Call-to-action is missing or too short")
            
        return issues
    
    @staticmethod
    def validate_linkedin_optimization(blog: BlogPost) -> List[str]:
        """Validate LinkedIn-specific optimization"""
        issues = []
        
        # Check content length
        content_length = len(blog.content)
        min_len, max_len = BlogConfig.OPTIMAL_POST_LENGTH
        
        if content_length < min_len:
            issues.append(f"Content too short for optimal LinkedIn engagement (current: {content_length}, recommended: {min_len}-{max_len})")
        elif content_length > max_len:
            issues.append(f"Content too long for optimal LinkedIn engagement (current: {content_length}, recommended: {min_len}-{max_len})")
        
        # Check for engagement elements
        content_lower = blog.content.lower()
        
        if "?" not in blog.content:
            issues.append("Consider adding questions to encourage engagement")
            
        if not any(word in content_lower for word in ["insight", "tip", "strategy", "learn", "discover"]):
            issues.append("Content should include learning/value keywords")
            
        # Hashtag validation
        for hashtag in blog.hashtags:
            if not hashtag.startswith('#'):
                issues.append(f"Hashtag '{hashtag}' should start with #")
            if len(hashtag) > 30:
                issues.append(f"Hashtag '{hashtag}' is too long")
                
        return issues

# Multi-File Processing Models
# Import from shared models to avoid circular imports
from shared.models import MultiSourceContent

class AggregatedBlogGenerationState(BlogGenerationState):
    """Extended state for multi-source blog generation"""
    multi_source_content: Optional[MultiSourceContent] = None
    source_weights: Dict[str, float] = Field(default_factory=dict)
    aggregation_strategy: AggregationStrategy = AggregationStrategy.SYNTHESIS