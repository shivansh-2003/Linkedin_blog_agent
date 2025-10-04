# shared/models.py - Shared data models

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class AggregationStrategy(str, Enum):
    """Strategy for aggregating multiple files"""
    SYNTHESIS = "synthesis"
    COMPARISON = "comparison"
    SEQUENCE = "sequence"
    TIMELINE = "timeline"

class MultiSourceContent(BaseModel):
    """Content aggregated from multiple sources"""
    sources: List[Any]  # List of ProcessedContent
    aggregation_strategy: AggregationStrategy
    unified_insights: List[str] = Field(default_factory=list)
    cross_references: Dict[str, List[str]] = Field(default_factory=dict)
    source_relationships: Dict[str, str] = Field(default_factory=dict)