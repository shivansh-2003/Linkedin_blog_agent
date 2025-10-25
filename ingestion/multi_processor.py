"""Batch and multi-file aggregation processing"""

import asyncio
import os
import sys
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add parent directory to path for langsmith_config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langsmith_config import trace_step

from .config import (
    AggregationStrategy,
    ProcessedContent,
    AggregatedContent,
    ContentType
)
from .unified_processor import UnifiedProcessor


class MultiProcessor:
    """Handles batch processing and multi-file aggregation"""
    
    def __init__(self):
        """Initialize with unified processor"""
        self.processor = UnifiedProcessor()
    
    @trace_step("process_batch", "workflow")
    async def process_batch(
        self,
        file_paths: List[str],
        enable_ai: bool = True,
        max_concurrent: int = 5
    ) -> List[ProcessedContent]:
        """
        Process multiple files independently in parallel
        
        Args:
            file_paths: List of file paths to process
            enable_ai: Whether to run AI analysis
            max_concurrent: Maximum concurrent processing tasks
        
        Returns:
            List of ProcessedContent results
        """
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_with_limit(file_path: str):
            async with semaphore:
                return await self.processor.process_file(file_path, enable_ai)
        
        # Process all files concurrently
        tasks = [process_with_limit(fp) for fp in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                error_result = ProcessedContent(
                    source_file=file_paths[i],
                    content_type=ContentType.TEXT,
                    raw_content="",
                    insights=None,
                    success=False,
                    error_message=str(result)
                )
                processed_results.append(error_result)
            else:
                processed_results.append(result)
        
        return processed_results
    
    @trace_step("process_aggregated", "workflow")
    async def process_aggregated(
        self,
        file_paths: List[str],
        strategy: AggregationStrategy = AggregationStrategy.SYNTHESIS,
        enable_ai: bool = True
    ) -> AggregatedContent:
        """
        Process multiple files and aggregate insights
        
        Args:
            file_paths: List of file paths to process
            strategy: How to combine the files
            enable_ai: Whether to run AI analysis
        
        Returns:
            AggregatedContent with unified insights
        """
        
        # First process all files
        results = await self.process_batch(file_paths, enable_ai)
        
        # Filter successful results
        successful = [r for r in results if r.success]
        
        if not successful:
            raise ValueError("No files processed successfully")
        
        # Aggregate based on strategy
        aggregated = await self._aggregate_results(successful, strategy)
        
        return aggregated
    
    @trace_step("aggregate_results", "chain")
    async def _aggregate_results(
        self,
        results: List[ProcessedContent],
        strategy: AggregationStrategy
    ) -> AggregatedContent:
        """Aggregate multiple processed contents"""
        
        # Collect all topics
        all_topics = []
        for result in results:
            if result.insights:
                all_topics.extend(result.insights.main_topics)
        
        # Remove duplicates while preserving order
        combined_topics = list(dict.fromkeys(all_topics))
        
        # Generate unified insights based on strategy
        if strategy == AggregationStrategy.SYNTHESIS:
            unified_insights = self._synthesize_insights(results)
        elif strategy == AggregationStrategy.COMPARISON:
            unified_insights = self._compare_insights(results)
        elif strategy == AggregationStrategy.SEQUENCE:
            unified_insights = self._sequence_insights(results)
        elif strategy == AggregationStrategy.TIMELINE:
            unified_insights = self._timeline_insights(results)
        else:
            unified_insights = "Multiple sources analyzed"
        
        # Generate cross-references
        cross_refs = self._generate_cross_references(results)
        
        # Create narrative flow
        narrative = self._create_narrative(results, strategy)
        
        return AggregatedContent(
            sources=results,
            unified_insights=unified_insights,
            cross_references=cross_refs,
            aggregation_strategy=strategy,
            combined_topics=combined_topics,
            narrative_flow=narrative,
            metadata={
                "file_count": len(results),
                "content_types": list(set(r.content_type for r in results)),
                "processing_timestamp": datetime.now().isoformat()
            }
        )
    
    @trace_step("synthesize_insights", "chain")
    def _synthesize_insights(self, results: List[ProcessedContent]) -> str:
        """Blend insights from multiple sources"""
        
        insights_parts = []
        
        insights_parts.append("SYNTHESIZED INSIGHTS FROM MULTIPLE SOURCES:")
        insights_parts.append("")
        
        # Collect all key insights
        all_insights = []
        for result in results:
            if result.insights and result.insights.key_insights:
                all_insights.extend(result.insights.key_insights)
        
        # Group similar insights (simple version)
        unique_insights = list(dict.fromkeys(all_insights))
        
        for i, insight in enumerate(unique_insights[:10], 1):
            insights_parts.append(f"{i}. {insight}")
        
        insights_parts.append("")
        insights_parts.append(f"Synthesized from {len(results)} sources")
        
        return "\n".join(insights_parts)
    
    @trace_step("compare_insights", "chain")
    def _compare_insights(self, results: List[ProcessedContent]) -> str:
        """Compare and contrast multiple sources"""
        
        parts = []
        parts.append("COMPARATIVE ANALYSIS:")
        parts.append("")
        
        # Group by content type
        by_type = {}
        for result in results:
            type_name = result.content_type.value
            if type_name not in by_type:
                by_type[type_name] = []
            by_type[type_name].append(result)
        
        # Compare within types
        for content_type, type_results in by_type.items():
            if len(type_results) > 1:
                parts.append(f"Comparing {len(type_results)} {content_type} sources:")
                for result in type_results:
                    source_name = result.source_file.split('/')[-1]
                    parts.append(f"  - {source_name}")
                parts.append("")
        
        # Compare across types
        if len(by_type) > 1:
            parts.append("Cross-type analysis:")
            parts.append(f"  {len(by_type)} different content types provide complementary perspectives")
            parts.append("")
        
        return "\n".join(parts)
    
    def _sequence_insights(self, results: List[ProcessedContent]) -> str:
        """Create sequential narrative"""
        
        parts = []
        parts.append("SEQUENTIAL ANALYSIS:")
        parts.append("")
        
        for i, result in enumerate(results, 1):
            source_name = result.source_file.split('/')[-1]
            parts.append(f"Step {i}: {source_name}")
            
            if result.insights and result.insights.key_insights:
                for insight in result.insights.key_insights[:3]:
                    parts.append(f"  • {insight}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _timeline_insights(self, results: List[ProcessedContent]) -> str:
        """Create chronological narrative"""
        
        # Sort by timestamp
        sorted_results = sorted(results, key=lambda r: r.timestamp)
        
        parts = []
        parts.append("CHRONOLOGICAL TIMELINE:")
        parts.append("")
        
        for result in sorted_results:
            source_name = result.source_file.split('/')[-1]
            timestamp = result.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            parts.append(f"[{timestamp}] {source_name}")
            
            if result.insights and result.insights.main_topics:
                topics = ", ".join(result.insights.main_topics[:3])
                parts.append(f"  Topics: {topics}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _generate_cross_references(
        self,
        results: List[ProcessedContent]
    ) -> List[str]:
        """Find connections between sources"""
        
        cross_refs = []
        
        # Find topic overlaps
        topic_map = {}
        for result in results:
            if result.insights:
                for topic in result.insights.main_topics:
                    if topic not in topic_map:
                        topic_map[topic] = []
                    source = result.source_file.split('/')[-1]
                    topic_map[topic].append(source)
        
        # Create references for shared topics
        for topic, sources in topic_map.items():
            if len(sources) > 1:
                source_list = ", ".join(sources)
                cross_refs.append(f"Topic '{topic}' appears in: {source_list}")
        
        return cross_refs
    
    def _create_narrative(
        self,
        results: List[ProcessedContent],
        strategy: AggregationStrategy
    ) -> str:
        """Create narrative flow description"""
        
        file_count = len(results)
        types = list(set(r.content_type.value for r in results))
        
        if strategy == AggregationStrategy.SYNTHESIS:
            return f"Synthesized insights from {file_count} sources ({', '.join(types)}) to create unified understanding"
        elif strategy == AggregationStrategy.COMPARISON:
            return f"Compared and contrasted {file_count} sources to highlight similarities and differences"
        elif strategy == AggregationStrategy.SEQUENCE:
            return f"Organized {file_count} sources into logical sequence for step-by-step understanding"
        elif strategy == AggregationStrategy.TIMELINE:
            return f"Arranged {file_count} sources chronologically to show evolution and progression"
        else:
            return f"Aggregated {file_count} sources"


# Export
__all__ = ['MultiProcessor']

