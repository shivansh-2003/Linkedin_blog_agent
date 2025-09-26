#!/usr/bin/env python3
"""
Multi-Format Input Processing System Demo
Supports: PDF, Word, PowerPoint, Code, Text files
Uses: Groq API (Llama, Mixtral, Gemma) + Gemini Flash 1.5
"""

import os
import sys
from pathlib import Path
from typing import List

from unified_processor import UnifiedProcessor
from batch_processor import BatchProcessor
from config import Config

def check_api_keys():
    """Check if required API keys are set"""
    missing_keys = []
    
    if not Config.GROQ_API_KEY:
        missing_keys.append("GROQ_API_KEY")
    
    if not Config.GEMINI_API_KEY:
        missing_keys.append("GOOGLE_API_KEY")
    
    if missing_keys:
        print("❌ Missing required API keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set these environment variables and try again.")
        return False
    
    return True

def print_supported_formats():
    """Print supported file formats"""
    print("\n📁 Supported File Formats:")
    print("   Documents: .pdf, .docx, .doc, .pptx, .ppt")
    print("   Code: .py, .js, .jsx, .ts, .tsx, .java, .cpp, .c, .cs, .go, .rs")
    print("   Text: .txt, .md")
    print("   Images: .jpg, .jpeg, .png, .gif, .bmp, .webp")

def process_single_file():
    """Interactive single file processing"""
    print("\n🔄 Single File Processing")
    file_path = input("Enter file path: ").strip().strip('"')
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    processor = UnifiedProcessor()
    print(f"\n⏳ Processing {Path(file_path).name}...")
    
    result = processor.process_file(file_path)
    
    # Display results
    print("\n" + "="*60)
    print(processor.get_processing_summary(result))
    
    if result.success:
        print(f"\n📊 AI Analysis:")
        print(result.ai_analysis)
        
        if result.key_insights:
            print(f"\n💡 Key Insights:")
            for i, insight in enumerate(result.key_insights, 1):
                print(f"{i}. {insight}")
        
        # Ask if user wants to see raw content
        show_content = input("\nShow raw extracted content? (y/N): ").lower() == 'y'
        if show_content and result.extracted_content:
            print(f"\n📝 Raw Content (first 500 chars):")
            print(result.extracted_content.raw_text[:500])
            if len(result.extracted_content.raw_text) > 500:
                print("...")

def process_multiple_files():
    """Interactive batch processing"""
    print("\n🔄 Batch Processing")
    print("Enter file paths (one per line, empty line to finish):")
    
    file_paths = []
    while True:
        path = input("> ").strip().strip('"')
        if not path:
            break
        if os.path.exists(path):
            file_paths.append(path)
        else:
            print(f"❌ File not found: {path}")
    
    if not file_paths:
        print("No valid files provided.")
        return
    
    batch_processor = BatchProcessor()
    print(f"\n⏳ Processing {len(file_paths)} files...")
    
    results = batch_processor.process_multiple_files(file_paths)
    
    # Display summary
    summary = batch_processor.generate_batch_summary(results)
    print(f"\n" + "="*60)
    print("📊 BATCH PROCESSING SUMMARY")
    print("="*60)
    print(f"Total Files: {summary['total_files']}")
    print(f"Successful: {summary['successful']}")
    print(f"Failed: {summary['failed']}")
    print(f"Total Processing Time: {summary['total_processing_time']:.2f}s")
    print(f"Average Time per File: {summary['average_processing_time']:.2f}s")
    
    if summary['by_content_type']:
        print(f"\n📁 Files by Type:")
        for file_type, count in summary['by_content_type'].items():
            print(f"   {file_type}: {count}")
    
    # Show detailed results for successful files
    successful_results = [r for r in results if r.success]
    if successful_results:
        print(f"\n💡 All Insights ({summary['total_insights']} total):")
        insight_num = 1
        for result in successful_results:
            if result.key_insights:
                print(f"\n📄 {Path(result.source_file).name}:")
                for insight in result.key_insights:
                    print(f"   {insight_num}. {insight}")
                    insight_num += 1
    
    # Save detailed summary
    save_summary = input("\nSave detailed summary to file? (y/N): ").lower() == 'y'
    if save_summary:
        batch_processor.save_results_summary(results)

def process_directory():
    """Process all files in a directory"""
    print("\n🔄 Directory Processing")
    dir_path = input("Enter directory path: ").strip().strip('"')
    
    if not os.path.exists(dir_path):
        print(f"❌ Directory not found: {dir_path}")
        return
    
    recursive = input("Process subdirectories recursively? (Y/n): ").lower() != 'n'
    
    batch_processor = BatchProcessor()
    print(f"\n⏳ Scanning directory...")
    
    try:
        results = batch_processor.process_directory(dir_path, recursive)
        
        if not results:
            return
        
        # Display summary (same as batch processing)
        summary = batch_processor.generate_batch_summary(results)
        print(f"\n" + "="*60)
        print("📊 DIRECTORY PROCESSING SUMMARY")
        print("="*60)
        print(f"Directory: {dir_path}")
        print(f"Recursive: {recursive}")
        print(f"Total Files: {summary['total_files']}")
        print(f"Successful: {summary['successful']}")
        print(f"Failed: {summary['failed']}")
        
        # Automatically save summary for directory processing
        output_file = f"directory_summary_{Path(dir_path).name}.txt"
        batch_processor.save_results_summary(results, output_file)
        
    except Exception as e:
        print(f"❌ Directory processing failed: {e}")

def main():
    """Main application"""
    print("="*60)
    print("🚀 MULTI-FORMAT INPUT PROCESSING SYSTEM")
    print("="*60)
    
    # Check API keys
    if not check_api_keys():
        return
    
    print_supported_formats()
    
    while True:
        print(f"\n{'='*60}")
        print("Choose an option:")
        print("1. Process single file")
        print("2. Process multiple files")
        print("3. Process directory")
        print("4. Show supported formats")
        print("0. Exit")
        
        choice = input("\nEnter choice (0-4): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            process_single_file()
        elif choice == '2':
            process_multiple_files()
        elif choice == '3':
            process_directory()
        elif choice == '4':
            print_supported_formats()
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)