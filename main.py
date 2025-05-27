# main.py

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv
from pdf_text_pipeline import PDFTextPipeline
from image_pipeline import ImagePipeline
from code_pipeline import CodePipeline
from blogger_agent import LinkedInBloggerAgent

load_dotenv()

class LinkedInBlogAIAssistant:
    def __init__(self, 
                 openai_key: Optional[str] = None,
                 anthropic_key: Optional[str] = None,
                 google_key: Optional[str] = None):
        """Initialize all pipelines and the blogger agent"""
        
        # Initialize pipelines
        self.pdf_text_pipeline = PDFTextPipeline(api_key=openai_key)
        self.image_pipeline = ImagePipeline(api_key=google_key)
        self.code_pipeline = CodePipeline(api_key=anthropic_key)
        self.blogger_agent = LinkedInBloggerAgent(anthropic_api_key=anthropic_key)
        
        print("✅ LinkedIn Blog AI Assistant initialized!")
        print("Available input methods:")
        print("1. Text input or PDF files")
        print("2. Images (jpg, png, etc.)")
        print("3. Code files (py, js, go, etc.)")
        print("4. Mixed inputs (combine multiple sources)\n")
    
    def process_text_input(self, text: str) -> dict:
        """Process direct text input"""
        print("📝 Processing text input...")
        return self.pdf_text_pipeline.extract_from_text(text)
    
    def process_pdf_file(self, pdf_path: str) -> dict:
        """Process PDF file"""
        print(f"📄 Processing PDF: {pdf_path}")
        return self.pdf_text_pipeline.extract_from_pdf(pdf_path)
    
    def process_image(self, image_path: str) -> dict:
        """Process image file"""
        print(f"🖼️ Processing image: {image_path}")
        return self.image_pipeline.extract_from_image(image_path)
    
    def process_code_file(self, code_path: str) -> dict:
        """Process code file"""
        print(f"💻 Processing code file: {code_path}")
        return self.code_pipeline.extract_from_code(code_path)
    
    def process_file(self, file_path: str) -> dict:
        """Process a single file based on its extension"""
        if not os.path.exists(file_path):
            return {"status": "error", "error": f"File not found: {file_path}"}
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.process_pdf_file(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return self.process_image(file_path)
        elif self.code_pipeline.is_supported_format(file_path):
            return self.process_code_file(file_path)
        elif file_ext == '.txt':
            return self.pdf_text_pipeline.extract_from_text_file(file_path)
        else:
            return {"status": "error", "error": f"Unsupported file type: {file_path}"}
    
    def process_multiple_files(self, file_paths: List[str]) -> dict:
        """Process multiple files of different types"""
        all_extractions = []
        
        for file_path in file_paths:
            result = self.process_file(file_path)
            
            if result["status"] == "success":
                all_extractions.append(result)
            else:
                print(f"⚠️ {result['error']}")
        
        # Combine all extractions
        if all_extractions:
            combined_info = "\n\n=== Combined Information ===\n\n"
            for i, extraction in enumerate(all_extractions, 1):
                combined_info += f"Source {i} ({extraction['source_type']}):\n"
                combined_info += extraction["extracted_info"] + "\n\n"
            
            return {
                "source_type": "multiple_sources",
                "extracted_info": combined_info,
                "status": "success"
            }
        else:
            return {
                "status": "error",
                "error": "No valid files processed"
            }
    
    def generate_blog(self, extraction_result: dict) -> str:
        """Generate LinkedIn blog post from extracted information"""
        if extraction_result["status"] != "success":
            print(f"❌ Error: {extraction_result.get('error', 'Unknown error')}")
            return None
        
        print("\n🚀 Starting blog generation with human-in-the-loop...\n")
        
        return self.blogger_agent.generate_blog_post(
            extracted_info=extraction_result["extracted_info"],
            source_type=extraction_result["source_type"]
        )
    
    def save_post(self, post_content: str, filename: str = None) -> str:
        """Save the generated post to a file"""
        if not filename:
            filename = input("Enter filename (without extension): ") + "_linkedin_post.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(post_content)
        print(f"✅ Post saved to {filename}")
        return filename
    
    def run(self):
        """Main interactive mode"""
        print("\n🎯 LinkedIn Blog AI Assistant - Interactive Mode")
        print("=" * 50)
        
        while True:
            print("\nChoose input method:")
            print("1. Text input")
            print("2. Single file (PDF, image, code, or text)")
            print("3. Multiple files")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            extraction_result = None
            
            if choice == "1":
                print("\nEnter your text (type 'END' on a new line to finish):")
                full_text = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    full_text.append(line)
                
                if full_text:
                    extraction_result = self.process_text_input("\n".join(full_text))
                
            elif choice == "2":
                file_path = input("\nEnter file path: ").strip()
                extraction_result = self.process_file(file_path)
                
            elif choice == "3":
                print("\nEnter file paths (one per line, type 'DONE' to finish):")
                file_paths = []
                while True:
                    path = input().strip()
                    if path == "DONE":
                        break
                    if path:
                        file_paths.append(path)
                
                if file_paths:
                    extraction_result = self.process_multiple_files(file_paths)
                    
            elif choice == "4":
                print("\n👋 Thank you for using LinkedIn Blog AI Assistant!")
                break
            else:
                print("❌ Invalid choice! Please enter 1-4.")
                continue
            
            # Generate blog if extraction was successful
            if extraction_result and extraction_result["status"] == "success":
                final_post = self.generate_blog(extraction_result)
                
                if final_post:
                    # Ask if user wants to save the post
                    save_choice = input("\n💾 Save the final post to file? (y/n): ").lower()
                    if save_choice == 'y':
                        self.save_post(final_post)

def main():
    """Main entry point - simplified without argparse"""
    print("🚀 Starting LinkedIn Blog AI Assistant...")
    print("Note: You can set API keys as environment variables:")
    print("- OPENAI_API_KEY")
    print("- ANTHROPIC_API_KEY") 
    print("- GOOGLE_API_KEY")

    
    # Get API keys from environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    # Initialize and run assistant
    assistant = LinkedInBlogAIAssistant(
        openai_key=openai_key,
        anthropic_key=anthropic_key,
        google_key=google_key
    )
    
    assistant.run()

if __name__ == "__main__":
    main()