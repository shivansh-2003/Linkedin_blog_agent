# worker.py - Background worker for processing tasks

import os
import time
import asyncio
from pathlib import Path
from ingestion.unified_processor import UnifiedProcessor
from blog_generation.workflow import BlogGenerationWorkflow
from blog_generation.config import BlogGenerationState

def main():
    """Background worker for processing files and generating blogs"""
    
    print("🔧 Worker started - Monitoring input directory")
    
    worker_type = os.getenv("WORKER_TYPE", "ingestion")
    print(f"📌 Worker Type: {worker_type}")
    
    # Initialize processors
    ingestion_processor = UnifiedProcessor()
    blog_workflow = BlogGenerationWorkflow()
    
    # Create directories
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    processed_dir = Path("/app/output/processed")
    failed_dir = Path("/app/output/failed")
    
    for directory in [input_dir, output_dir, processed_dir, failed_dir]:
        directory.mkdir(parents=True, exist_ok=True)
    
    print(f"📂 Monitoring: {input_dir}")
    print(f"📂 Output: {output_dir}")
    
    while True:
        try:
            # Process files in input directory
            for file_path in input_dir.glob("*"):
                if file_path.is_file():
                    print(f"\n📄 Found file: {file_path.name}")
                    
                    try:
                        if worker_type == "ingestion":
                            # Ingestion processing
                            print(f"🔍 Processing: {file_path.name}")
                            result = ingestion_processor.process_file(str(file_path))
                            
                            if result.success:
                                print(f"✅ Ingestion complete: {file_path.name}")
                                
                                # Save analysis
                                output_file = output_dir / f"{file_path.stem}_analysis.txt"
                                with open(output_file, 'w') as f:
                                    f.write(f"File: {file_path.name}\n")
                                    f.write(f"\nAI Analysis:\n{result.ai_analysis}\n")
                                    f.write(f"\nKey Insights:\n")
                                    for insight in result.key_insights:
                                        f.write(f"- {insight}\n")
                                
                                # Move to processed
                                file_path.rename(processed_dir / file_path.name)
                            else:
                                print(f"❌ Processing failed: {result.error_message}")
                                file_path.rename(failed_dir / file_path.name)
                        
                        elif worker_type == "blog_generation":
                            # Blog generation processing
                            print(f"✨ Generating blog: {file_path.name}")
                            
                            # Read file content
                            content = file_path.read_text()
                            
                            # Generate blog
                            state = BlogGenerationState(
                                source_content=content,
                                source_file_path=str(file_path),
                                user_requirements="Professional LinkedIn post"
                            )
                            
                            result = blog_workflow.run_workflow(state)
                            
                            if result.final_blog:
                                print(f"✅ Blog generated: {file_path.name}")
                                
                                # Save blog
                                blog_file = output_dir / f"{file_path.stem}_blog.txt"
                                with open(blog_file, 'w') as f:
                                    f.write(f"Title: {result.final_blog.title}\n\n")
                                    f.write(f"Hook: {result.final_blog.hook}\n\n")
                                    f.write(f"Content:\n{result.final_blog.content}\n\n")
                                    f.write(f"CTA: {result.final_blog.call_to_action}\n\n")
                                    f.write(f"Hashtags: {' '.join(result.final_blog.hashtags)}\n")
                                
                                # Move to processed
                                file_path.rename(processed_dir / file_path.name)
                            else:
                                print(f"❌ Blog generation failed")
                                file_path.rename(failed_dir / file_path.name)
                        
                    except Exception as e:
                        print(f"❌ Error processing {file_path.name}: {e}")
                        file_path.rename(failed_dir / file_path.name)
            
            # Sleep before next check
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 Worker stopped by user")
            break
        except Exception as e:
            print(f"❌ Worker error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
