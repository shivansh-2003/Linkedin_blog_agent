"""
Data models and enums for blog generation workflow.
Pure Pydantic models with no business logic.
"""

import os
from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from shared.models import AggregationStrategy

load_dotenv()


# ===== ENUMS =====

class BlogQuality(str, Enum):
    """Quality levels for generated content"""
    DRAFT = "draft"
    GOOD = "good"
    EXCELLENT = "excellent"
    PUBLISH_READY = "publish_ready"


class ProcessingStatus(str, Enum):
    """Current state of the workflow"""
    GENERATING = "generating"
    CRITIQUING = "critiquing"
    REFINING = "refining"
    AWAITING_HUMAN = "awaiting_human"
    COMPLETED = "completed"
    FAILED = "failed"


# ===== OUTPUT MODELS =====

class BlogPost(BaseModel):
    """LinkedIn blog post structure"""
    title: str = Field(description="Compelling title (10-60 chars)")
    hook: str = Field(description="Opening hook that grabs attention (1-2 sentences)")
    content: str = Field(description="Main body content AFTER the hook")
    call_to_action: str = Field(description="Specific engagement request")
    hashtags: List[str] = Field(
        default_factory=list,
        description="5-8 relevant professional hashtags",
        min_length=5,
        max_length=8
    )
    target_audience: str = Field(default="Professional network")
    estimated_engagement_score: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
        description="Predicted engagement potential"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "5 AI Trends Reshaping Healthcare",
                "hook": "Healthcare AI isn't future tech—it's saving lives today. Here's what 10,000 hospitals are doing right now:",
                "content": "1. Diagnostic AI reducing errors by 40%\n2. Predictive models catching diseases earlier\n3. Automated documentation saving 2 hours/day\n\nThe data is clear: AI-assisted diagnosis outperforms human-only approaches in 23 medical specialties.\n\nBut here's the twist: The best results come from human + AI collaboration, not replacement.",
                "call_to_action": "What's your take on AI in healthcare? Share your experience below 👇",
                "hashtags": ["#HealthTech", "#AIinHealthcare", "#MedicalInnovation", "#DigitalHealth", "#FutureOfMedicine"],
                "target_audience": "Healthcare professionals and tech leaders",
                "estimated_engagement_score": 8
            }
        }


class CritiqueResult(BaseModel):
    """Quality assessment across multiple dimensions"""
    quality_score: int = Field(ge=1, le=10, description="Overall quality score")
    quality_level: BlogQuality
    
    # Dimension scores (1-10 each)
    hook_effectiveness: int = Field(ge=1, le=10)
    value_delivery: int = Field(ge=1, le=10)
    linkedin_optimization: int = Field(ge=1, le=10)
    engagement_potential: int = Field(ge=1, le=10)
    professional_tone: int = Field(ge=1, le=10)
    
    # Detailed feedback
    strengths: List[str] = Field(default_factory=list, max_length=5)
    weaknesses: List[str] = Field(default_factory=list, max_length=5)
    specific_improvements: List[str] = Field(default_factory=list, max_length=5)
    
    # Additional feedback
    tone_feedback: str = ""
    engagement_feedback: str = ""
    linkedin_optimization_feedback: str = ""
    
    approved_for_publish: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "quality_score": 8,
                "quality_level": "excellent",
                "hook_effectiveness": 9,
                "value_delivery": 8,
                "linkedin_optimization": 8,
                "engagement_potential": 7,
                "professional_tone": 8,
                "strengths": [
                    "Strong hook with specific data",
                    "Clear value propositions",
                    "Good use of numbers and statistics"
                ],
                "weaknesses": [
                    "CTA could be more specific",
                    "Missing personal perspective"
                ],
                "specific_improvements": [
                    "Add a personal anecdote",
                    "Strengthen the call-to-action"
                ]
            }
        }


# ===== INPUT MODELS =====

class HumanFeedback(BaseModel):
    """Human feedback on generated content"""
    feedback_text: str
    satisfaction_level: int = Field(ge=1, le=5, description="1=Very unsatisfied, 5=Very satisfied")
    specific_changes: List[str] = Field(default_factory=list)
    approve_current: bool = False
    request_regeneration: bool = False


# ===== WORKFLOW STATE =====

class BlogGenerationState(BaseModel):
    """Complete state for LangGraph workflow"""
    
    # Input
    source_content: str = ""
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
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True


class AggregatedBlogGenerationState(BlogGenerationState):
    """Extended state for multi-source content"""
    multi_source_content: Optional[dict] = None  # From ingestion.AggregatedContent
    aggregation_strategy: AggregationStrategy = AggregationStrategy.SYNTHESIS


# ===== CONFIGURATION =====

class Config:
    """System configuration - read-only constants"""
    
    # API Keys
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # Model Configuration
    PRIMARY_MODEL = "llama-3.3-70b-versatile"
    FALLBACK_MODELS = ["llama-3.1-8b-instant", "gemma2-9b-it"]
    
    # Generation Parameters
    GENERATION_TEMPERATURE = 0.7
    CRITIQUE_TEMPERATURE = 0.3
    REFINEMENT_TEMPERATURE = 0.5
    MAX_TOKENS = 2500
    
    # Quality Thresholds
    MIN_QUALITY_SCORE = 7
    EXCELLENT_THRESHOLD = 9
    
    # LinkedIn Optimization
    MIN_POST_LENGTH = 150
    MAX_POST_LENGTH = 1300
    MIN_HASHTAGS = 5
    MAX_HASHTAGS = 8
    IDEAL_HASHTAGS = 6
    
    # Validation
    @classmethod
    def validate(cls) -> None:
        """Validate configuration on startup"""
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY environment variable not set")
    
    @classmethod
    def get_model_params(cls, agent_type: str) -> dict:
        """Get model parameters for specific agent"""
        temps = {
            "generator": cls.GENERATION_TEMPERATURE,
            "critic": cls.CRITIQUE_TEMPERATURE,
            "refiner": cls.REFINEMENT_TEMPERATURE
        }
        
        return {
            "model": cls.PRIMARY_MODEL,
            "temperature": temps.get(agent_type, 0.5),
            "max_tokens": cls.MAX_TOKENS
        }


# Validate config on import
Config.validate()


# Export all
__all__ = [
    # Enums
    'BlogQuality',
    'ProcessingStatus',
    
    # Models
    'BlogPost',
    'CritiqueResult',
    'HumanFeedback',
    'BlogGenerationState',
    'AggregatedBlogGenerationState',
    
    # Config
    'Config',
]
