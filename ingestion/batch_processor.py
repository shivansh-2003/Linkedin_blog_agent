import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from pathlib import Path
from config import ProcessedContent, ContentType
from unified_processor import UnifiedProcessor

class BatchProcessor:
    """Handle batch processing of multiple files"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.unified_processor = UnifiedProcessor()
    
    def process_multiple_files(self, file_paths: List[str]) -> List[ProcessedContent]:
        """Process multiple files concurrently"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self.unified_processor.process_file, file_path): file_path
                for file_path in file_paths
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    results.append(result)
                    print(f"✅ Completed: {Path(file_path).name}")
                except Exception as e:
                    # Create error result
                    error_result = ProcessedContent(
                        source_file=file_path,
                        content_type=ContentType.TEXT,  # Default
                        extracted_content=None,
                        ai_analysis=f"Processing failed: {str(e)}",
                        key_insights=[],
                        metadata=None,
                        success=False,
                        error_message=str(e)
                    )
                    results.append(error_result)
                    print(f"❌ Failed: {Path(file_path).name} - {str(e)}")
        
        return results
    
    def process_directory(self, directory_path: str, recursive: bool = True) -> List[ProcessedContent]:
        """Process all supported files in a directory"""
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory_path}")
        
        # Find all supported files
        file_paths = []
        
        if recursive:
            # Recursively find files
            for file_path in directory.rglob("*"):
                if file_path.is_file() and self._is_supported_file(file_path):
                    file_paths.append(str(file_path))
        else:
            # Only files in the current directory
            for file_path in directory.glob("*"):
                if file_path.is_file() and self._is_supported_file(file_path):
                    file_paths.append(str(file_path))
        
        if not file_paths:
            print(f"No supported files found in {directory_path}")
            return []
        
        print(f"Found {len(file_paths)} files to process")
        return self.process_multiple_files(file_paths)
    
    def _is_supported_file(self, file_path: Path) -> bool:
        """Check if file is supported"""
        from config import Config
        return file_path.suffix.lower() in Config.SUPPORTED_EXTENSIONS
    
    def generate_batch_summary(self, results: List[ProcessedContent]) -> Dict[str, Any]:
        """Generate summary statistics for batch processing"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        # Group by content type
        by_type = {}
        for result in successful:
            content_type = result.content_type.value
            if content_type not in by_type:
                by_type[content_type] = 0
            by_type[content_type] += 1
        
        # Calculate total processing time
        total_processing_time = sum(
            result.extracted_content.processing_time 
            for result in successful 
            if result.extracted_content
        )
        
        # Collect all insights
        all_insights = []
        for result in successful:
            all_insights.extend(result.key_insights)
        
        return {
            "total_files": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "by_content_type": by_type,
            "total_processing_time": round(total_processing_time, 2),
            "average_processing_time": round(total_processing_time / len(successful), 2) if successful else 0,
            "total_insights": len(all_insights),
            "failed_files": [r.source_file for r in failed] if failed else []
        }
    
    def save_results_summary(self, results: List[ProcessedContent], output_file: str = "batch_results.txt"):
        """Save processing results summary to file"""
        summary = self.generate_batch_summary(results)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== BATCH PROCESSING SUMMARY ===\n\n")
            f.write(f"Total Files: {summary['total_files']}\n")
            f.write(f"Successful: {summary['successful']}\n")
            f.write(f"Failed: {summary['failed']}\n")
            f.write(f"Total Processing Time: {summary['total_processing_time']}s\n")
            f.write(f"Average Processing Time: {summary['average_processing_time']}s\n\n")
            
            f.write("Files by Type:\n")
            for content_type, count in summary['by_content_type'].items():
                f.write(f"  {content_type}: {count}\n")
            
            if summary['failed_files']:
                f.write(f"\nFailed Files:\n")
                for failed_file in summary['failed_files']:
                    f.write(f"  - {failed_file}\n")
            
            f.write("\n=== DETAILED RESULTS ===\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"{i}. {Path(result.source_file).name}\n")
                f.write(f"   Type: {result.content_type.value}\n")
                f.write(f"   Status: {'✅ Success' if result.success else '❌ Failed'}\n")
                
                if result.success and result.extracted_content:
                    f.write(f"   Processing Time: {result.extracted_content.processing_time:.2f}s\n")
                    f.write(f"   Insights: {len(result.key_insights)}\n")
                elif result.error_message:
                    f.write(f"   Error: {result.error_message}\n")
                
                f.write("\n")
        
        print(f"Results summary saved to: {output_file}")