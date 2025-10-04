"""
Shared data models to avoid circular imports between modules
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum

class AggregationStrategy(str, Enum):
    """Strategy for aggregating multiple files"""
    SYNTHESIS = "synthesis"      # Blend all insights together
    COMPARISON = "comparison"    # Compare/contrast sources
    SEQUENCE = "sequence"        # Sequential narrative
    TIMELINE = "timeline"        # Chronological story

class MultiSourceContent(BaseModel):
    """Content aggregated from multiple sources"""
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    unified_insights: List[str] = Field(default_factory=list)
    cross_references: Dict[str, List[str]] = Field(default_factory=dict)
    aggregation_strategy: AggregationStrategy
    total_content_length: int = 0
    source_types: List[str] = Field(default_factory=list)
    processing_metadata: Dict[str, Any] = Field(default_factory=dict)
