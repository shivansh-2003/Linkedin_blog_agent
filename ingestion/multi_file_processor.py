"""
Multi-File Processing Module

Processes and aggregates multiple files into unified content for LinkedIn blog generation.
Supports different aggregation strategies: synthesis, comparison, sequence, and timeline.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

# Import from ingestion module
from ingestion.config import ProcessedContent, ContentType
from ingestion.unified_processor import UnifiedProcessor

# Import from blog_generation module (avoiding circular import)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blog_generation.config import AggregationStrategy, MultiSourceContent

class MultiFileProcessor:
    """Process and aggregate multiple files into unified content"""
    
    def __init__(self):
        self.unified_processor = UnifiedProcessor()
    
    async def process_multiple_files(
        self, 
        file_paths: List[str], 
        aggregation_strategy: AggregationStrategy = AggregationStrategy.SYNTHESIS
    ) -> MultiSourceContent:
        """Process multiple files and aggregate their content"""
        
        print(f"🔄 Processing {len(file_paths)} files with {aggregation_strategy.value} strategy...")
        
        # Process all files concurrently
        tasks = [
            asyncio.to_thread(self.unified_processor.process_file, file_path)
            for file_path in file_paths
        ]
        
        processed_files = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results and handle exceptions
        successful_results = []
        for i, result in enumerate(processed_files):
            if isinstance(result, Exception):
                print(f"⚠️ Failed to process {file_paths[i]}: {result}")
            elif result.success:
                successful_results.append(result)
            else:
                print(f"⚠️ Failed to process {file_paths[i]}: {result.error_message}")
        
        if not successful_results:
            raise ValueError("No files were successfully processed")
        
        print(f"✅ Successfully processed {len(successful_results)}/{len(file_paths)} files")
        
        # Aggregate content based on strategy
        aggregated_content = self._aggregate_content(
            successful_results, 
            aggregation_strategy
        )
        
        return aggregated_content
    
    def _aggregate_content(
        self, 
        processed_files: List[ProcessedContent], 
        strategy: AggregationStrategy
    ) -> MultiSourceContent:
        """Aggregate processed files using specified strategy"""
        
        print(f"🔗 Aggregating content using {strategy.value} strategy...")
        
        if strategy == AggregationStrategy.SYNTHESIS:
            return self._synthesize_content(processed_files)
        elif strategy == AggregationStrategy.COMPARISON:
            return self._compare_content(processed_files)
        elif strategy == AggregationStrategy.SEQUENCE:
            return self._sequence_content(processed_files)
        elif strategy == AggregationStrategy.TIMELINE:
            return self._timeline_content(processed_files)
        else:
            raise ValueError(f"Unknown aggregation strategy: {strategy}")
    
    def _synthesize_content(self, processed_files: List[ProcessedContent]) -> MultiSourceContent:
        """Blend insights from all files into unified narrative"""
        
        # Combine all insights
        all_insights = []
        source_map = {}
        
        for i, file_result in enumerate(processed_files):
            source_id = f"source_{i}_{file_result.content_type.value}"
            source_map[source_id] = file_result.source_file
            
            for insight in file_result.key_insights:
                all_insights.append({
                    "insight": insight,
                    "source": source_id,
                    "content_type": file_result.content_type.value
                })
        
        # Find common themes across sources
        unified_insights = self._extract_unified_insights(all_insights)
        
        # Create cross-references between sources
        cross_references = self._create_cross_references(processed_files)
        
        return MultiSourceContent(
            sources=processed_files,
            aggregation_strategy=AggregationStrategy.SYNTHESIS,
            unified_insights=unified_insights,
            cross_references=cross_references,
            source_relationships=source_map
        )
    
    def _compare_content(self, processed_files: List[ProcessedContent]) -> MultiSourceContent:
        """Compare and contrast findings across files"""
        
        # Group by content type for comparison
        by_type = {}
        for file_result in processed_files:
            content_type = file_result.content_type.value
            if content_type not in by_type:
                by_type[content_type] = []
            by_type[content_type].append(file_result)
        
        # Create comparison insights
        comparison_insights = []
        
        # Compare within same types
        for content_type, files in by_type.items():
            if len(files) > 1:
                comparison_insights.extend(
                    self._compare_similar_files(files, content_type)
                )
        
        # Compare across different types
        if len(by_type) > 1:
            comparison_insights.extend(
                self._compare_different_types(by_type)
            )
        
        return MultiSourceContent(
            sources=processed_files,
            aggregation_strategy=AggregationStrategy.COMPARISON,
            unified_insights=comparison_insights,
            cross_references=self._create_cross_references(processed_files)
        )
    
    def _sequence_content(self, processed_files: List[ProcessedContent]) -> MultiSourceContent:
        """Create sequential narrative from multiple sources"""
        
        # Order files by logical sequence (could be enhanced with AI)
        ordered_files = self._order_files_logically(processed_files)
        
        # Create sequential narrative
        sequential_insights = []
        for i, file_result in enumerate(ordered_files):
            phase = f"Phase {i+1}"
            sequential_insights.append(f"{phase}: {file_result.source_file}")
            sequential_insights.extend([
                f"{phase} - {insight}" for insight in file_result.key_insights[:3]
            ])
        
        return MultiSourceContent(
            sources=ordered_files,
            aggregation_strategy=AggregationStrategy.SEQUENCE,
            unified_insights=sequential_insights,
            cross_references=self._create_cross_references(ordered_files)
        )
    
    def _timeline_content(self, processed_files: List[ProcessedContent]) -> MultiSourceContent:
        """Create chronological narrative from multiple sources"""
        
        # Sort by creation date or file modification time
        sorted_files = sorted(
            processed_files,
            key=lambda f: f.metadata.creation_date if f.metadata and f.metadata.creation_date else "0"
        )
        
        # Create timeline insights
        timeline_insights = []
        for file_result in sorted_files:
            date_info = file_result.metadata.creation_date if file_result.metadata else "Unknown date"
            timeline_insights.append(f"[{date_info}] {file_result.source_file}")
            timeline_insights.extend(file_result.key_insights[:2])
        
        return MultiSourceContent(
            sources=sorted_files,
            aggregation_strategy=AggregationStrategy.TIMELINE,
            unified_insights=timeline_insights,
            cross_references=self._create_cross_references(sorted_files)
        )
    
    def _extract_unified_insights(self, all_insights: List[Dict]) -> List[str]:
        """Extract unified insights from multiple sources"""
        
        # Simple keyword-based clustering (could be enhanced with AI)
        theme_clusters = {}
        
        for insight_data in all_insights:
            insight = insight_data["insight"]
            # Extract key themes (simplified)
            words = insight.lower().split()
            key_words = [w for w in words if len(w) > 4]  # Filter short words
            
            # Find existing cluster or create new one
            assigned = False
            for theme, cluster_insights in theme_clusters.items():
                if any(word in theme.lower() for word in key_words[:3]):
                    cluster_insights.append(insight_data)
                    assigned = True
                    break
            
            if not assigned and key_words:
                theme_clusters[key_words[0]] = [insight_data]
        
        # Create unified insights from clusters
        unified = []
        for theme, cluster in theme_clusters.items():
            if len(cluster) > 1:  # Only themes with multiple sources
                sources = list(set(item["source"] for item in cluster))
                unified.append(
                    f"Across {len(sources)} sources: {cluster[0]['insight']}"
                )
            else:
                unified.append(cluster[0]["insight"])
        
        return unified[:7]  # Limit to top insights
    
    def _create_cross_references(self, processed_files: List[ProcessedContent]) -> Dict[str, List[str]]:
        """Create cross-references between sources"""
        
        cross_refs = {}
        
        for i, file1 in enumerate(processed_files):
            file1_id = f"source_{i}"
            cross_refs[file1_id] = []
            
            for j, file2 in enumerate(processed_files):
                if i != j:
                    file2_id = f"source_{j}"
                    # Simple overlap detection (could be enhanced)
                    overlap = self._calculate_content_overlap(file1, file2)
                    if overlap > 0.1:  # Threshold for relevance
                        cross_refs[file1_id].append(file2_id)
        
        return cross_refs
    
    def _calculate_content_overlap(self, file1: ProcessedContent, file2: ProcessedContent) -> float:
        """Calculate content overlap between two files"""
        
        # Simple word overlap calculation
        words1 = set(file1.ai_analysis.lower().split())
        words2 = set(file2.ai_analysis.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _compare_similar_files(self, files: List[ProcessedContent], content_type: str) -> List[str]:
        """Compare files of the same type"""
        
        insights = []
        for i in range(len(files)):
            for j in range(i + 1, len(files)):
                file1, file2 = files[i], files[j]
                insights.append(
                    f"Comparing {content_type} files: {file1.source_file} vs {file2.source_file}"
                )
        
        return insights
    
    def _compare_different_types(self, by_type: Dict[str, List[ProcessedContent]]) -> List[str]:
        """Compare files of different types"""
        
        insights = []
        types = list(by_type.keys())
        
        for i in range(len(types)):
            for j in range(i + 1, len(types)):
                type1, type2 = types[i], types[j]
                insights.append(
                    f"Cross-analysis: {type1} content complements {type2} findings"
                )
        
        return insights
    
    def _order_files_logically(self, files: List[ProcessedContent]) -> List[ProcessedContent]:
        """Order files in logical sequence"""
        
        # Simple ordering by content type priority
        type_priority = {
            ContentType.TEXT: 1,        # Context first
            ContentType.PDF: 2,         # Documentation
            ContentType.POWERPOINT: 3,  # Presentation
            ContentType.CODE: 4,        # Implementation
            ContentType.IMAGE: 5        # Supporting visuals
        }
        
        return sorted(files, key=lambda f: type_priority.get(f.content_type, 999))

# Example usage and testing
if __name__ == "__main__":
    async def test_multi_file_processing():
        """Test the multi-file processor"""
        
        # Example file paths (replace with actual files)
        test_files = [
            "test/sample1.pdf",
            "test/sample2.docx", 
            "test/sample3.py"
        ]
        
        processor = MultiFileProcessor()
        
        try:
            # Test synthesis strategy
            result = await processor.process_multiple_files(
                test_files, 
                AggregationStrategy.SYNTHESIS
            )
            
            print(f"✅ Multi-file processing successful!")
            print(f"   Strategy: {result.aggregation_strategy}")
            print(f"   Sources: {len(result.sources)}")
            print(f"   Unified insights: {len(result.unified_insights)}")
            print(f"   Cross-references: {len(result.cross_references)}")
            
        except Exception as e:
            print(f"❌ Multi-file processing failed: {e}")
    
    # Run test
    asyncio.run(test_multi_file_processing())
