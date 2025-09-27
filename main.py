# advanced_main.py - Updated main with enhanced agents

import os
from pathlib import Path
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
from pdf_text_pipeline import PDFTextPipeline
from image_pipeline import ImagePipeline
from code_pipeline import CodePipeline
from presentation_pipeline import PresentationPipeline
from blogger_agent import EnhancedLinkedInBloggerAgent
from research_agent import ResearchFeatureAgent

load_dotenv()

class AdvancedLinkedInBlogAIAssistant:
    def __init__(self, 
                 openai_key: Optional[str] = None,
                 anthropic_key: Optional[str] = None,
                 google_key: Optional[str] = None):
        """Initialize all pipelines and advanced AI agents"""
        
        # Initialize existing pipelines
        self.pdf_text_pipeline = PDFTextPipeline(api_key=openai_key)
        self.image_pipeline = ImagePipeline(api_key=google_key)
        self.code_pipeline = CodePipeline(api_key=anthropic_key)
        self.presentation_pipeline = PresentationPipeline(api_key=openai_key, google_api_key=google_key)
    
        # Initialize advanced AI agents
        self.enhanced_blogger = EnhancedLinkedInBloggerAgent(
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key
        )
        
        self.research_agent = ResearchFeatureAgent(
            anthropic_api_key=anthropic_key,
            openai_api_key=openai_key
        )
        
        print("✅ Advanced LinkedIn Blog AI Assistant initialized!")
        print("🚀 New Features Available:")
        print("  • Enhanced multi-agent content generation with critique workflow")
        print("  • Deep research-driven content creation")
        print("  • Automated quality assessment and revision")
        print("  • Performance prediction and optimization")
        print()
    
    def generate_from_research_prompt(self, user_prompt: str) -> dict:
        """Generate LinkedIn content from user research prompt"""
        print(f"\n🔬 Starting research-driven content generation...")
        print(f"📝 Research Topic: {user_prompt}")
        
        return self.research_agent.generate_research_driven_post(user_prompt)
    
    def generate_enhanced_content(self, extraction_result: dict) -> dict:
        """Generate enhanced content with critique workflow"""
        if extraction_result["status"] != "success":
            print(f"❌ Error: {extraction_result.get('error', 'Unknown error')}")
            return {"status": "error", "error": extraction_result.get('error')}
        
        print("\n🚀 Starting enhanced blog generation with AI critique workflow...\n")
        
        return self.enhanced_blogger.generate_enhanced_blog_post(
            extracted_info=extraction_result["extracted_info"],
            source_type=extraction_result["source_type"]
        )
    
    def process_content_with_enhancement(self, content_source, content_type="auto"):
        """Process content and generate enhanced blog post"""
        
        # Process the content based on type
        if content_type == "text" or isinstance(content_source, str):
            extraction_result = self.pdf_text_pipeline.extract_from_text(content_source)
        elif content_type == "file":
            extraction_result = self.process_file(content_source)
        else:
            return {"status": "error", "error": "Invalid content type"}
        
        # Generate enhanced content
        if extraction_result["status"] == "success":
            return self.generate_enhanced_content(extraction_result)
        else:
            return extraction_result
    
    # Existing methods from original main.py
    def process_file(self, file_path: str) -> dict:
        """Process a single file based on its extension"""
        if not os.path.exists(file_path):
            return {"status": "error", "error": f"File not found: {file_path}"}
        
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.pdf_text_pipeline.extract_from_pdf(file_path)
        elif file_ext in ['.pptx', '.ppt']:
            return self.presentation_pipeline.extract_from_presentation(file_path)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return self.image_pipeline.extract_from_image(file_path)
        elif self.code_pipeline.is_supported_format(file_path):
            return self.code_pipeline.extract_from_code(file_path)
        elif file_ext == '.txt':
            return self.pdf_text_pipeline.extract_from_text_file(file_path)
        else:
            return {"status": "error", "error": f"Unsupported file type: {file_path}"}
    
    def save_advanced_results(self, results: dict, filename: str = None) -> str:
        """Save advanced results with comprehensive information"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"linkedin_post_advanced_{timestamp}.txt"
        
        content = f"""# LinkedIn Post - Advanced AI Generation Report

## Final LinkedIn Post
{results.get('final_post', 'No final post generated')}

## Performance Prediction
"""
        
        if 'performance_prediction' in results:
            perf = results['performance_prediction']
            content += f"""
- Engagement Likelihood: {perf.get('engagement_likelihood', 'N/A')}%
- Viral Potential: {perf.get('viral_potential', 'N/A')}%
- Optimization Score: {perf.get('optimization_score', 'N/A')}/100
- Predicted Reach: {perf.get('predicted_reach', 'N/A')}
"""
        
        if 'confidence_score' in results:
            content += f"\n- Research Confidence: {results['confidence_score']:.1f}%"
        
        content += f"""

## Generation Statistics
- Revision Count: {results.get('revision_count', 0)}
- Research Depth: {results.get('research_depth', 'N/A')} areas
"""
        
        if results.get('critique_history'):
            content += "\n## Quality Assessment History\n"
            for i, critique in enumerate(results['critique_history'], 1):
                content += f"""
### Iteration {i}
- Language Score: {critique.language_score}/10
- Content Score: {critique.content_score}/10  
- Engagement Score: {critique.engagement_score}/10
- Feedback: {critique.overall_recommendation[:200]}...
"""
        
        if results.get('research_citations'):
            content += f"\n## Research Sources\n"
            for i, citation in enumerate(results['research_citations'], 1):
                content += f"{i}. {citation}\n"
        
        content += f"""
## Posting Recommendations
- Best posting times: Tuesday-Thursday, 8-10 AM or 5-7 PM
- Engage with comments within the first hour
- Monitor performance and iterate based on results
- Consider A/B testing different versions

---
Generated by Advanced LinkedIn Blog AI Assistant
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Advanced results saved to {filename}")
        return filename
    
    def run_interactive_mode(self):
        """Enhanced interactive mode with advanced options"""
        print("\n🎯 Advanced LinkedIn Blog AI Assistant - Interactive Mode")
        print("=" * 60)
        
        while True:
            print("\nChoose content generation method:")
            print("1. 📚 Research-Driven Content (New! - AI researches and creates)")
            print("2. 📄 Enhanced File Processing (New! - AI critique workflow)")
            print("3. 📝 Enhanced Text Processing (New! - AI critique workflow)")  
            print("4. 🔄 Basic Mode (Original functionality)")
            print("5. 🚪 Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                # Research-driven content generation
                print("\n🔬 Research-Driven Content Generation")
                print("Enter a topic, question, or research prompt:")
                user_prompt = input("Research prompt: ").strip()
                
                if user_prompt:
                    results = self.generate_from_research_prompt(user_prompt)
                    
                    if results.get("status") == "success":
                        print("\n" + "="*60)
                        print("🎉 RESEARCH-DRIVEN LINKEDIN POST GENERATED!")
                        print("="*60)
                        print(results.get("final_post", ""))
                        print("="*60)
                        
                        print(f"\n📊 Research Quality Metrics:")
                        print(f"   • Confidence Score: {results.get('confidence_score', 0):.1f}%")
                        print(f"   • Research Areas: {results.get('research_depth', 0)}")
                        print(f"   • Revisions Made: {results.get('revision_count', 0)}")
                        
                        # Save option
                        save_choice = input("\n💾 Save results to file? (y/n): ").lower()
                        if save_choice == 'y':
                            self.save_advanced_results(results)
                    else:
                        print(f"❌ Error: {results.get('error', 'Unknown error')}")
                
            elif choice == "2":
                # Enhanced file processing
                print("\n📄 Enhanced File Processing")
                file_path = input("Enter file path: ").strip()
                
                if file_path:
                    results = self.process_content_with_enhancement(file_path, "file")
                    
                    if results.get("status") == "success":
                        print("\n" + "="*60)
                        print("🎉 ENHANCED LINKEDIN POST GENERATED!")
                        print("="*60)
                        print(results.get("final_post", ""))
                        print("="*60)
                        
                        self._display_enhancement_metrics(results)
                        
                        # Save option
                        save_choice = input("\n💾 Save results to file? (y/n): ").lower()
                        if save_choice == 'y':
                            self.save_advanced_results(results)
                    else:
                        print(f"❌ Error: {results.get('error', 'Unknown error')}")
            
            elif choice == "3":
                # Enhanced text processing
                print("\n📝 Enhanced Text Processing")
                print("Enter your text (type 'END' on a new line to finish):")
                full_text = []
                while True:
                    line = input()
                    if line == "END":
                        break
                    full_text.append(line)
                
                if full_text:
                    text_content = "\n".join(full_text)
                    results = self.process_content_with_enhancement(text_content, "text")
                    
                    if results.get("status") == "success":
                        print("\n" + "="*60)
                        print("🎉 ENHANCED LINKEDIN POST GENERATED!")
                        print("="*60)
                        print(results.get("final_post", ""))
                        print("="*60)
                        
                        self._display_enhancement_metrics(results)
                        
                        # Save option
                        save_choice = input("\n💾 Save results to file? (y/n): ").lower()
                        if save_choice == 'y':
                            self.save_advanced_results(results)
                    else:
                        print(f"❌ Error: {results.get('error', 'Unknown error')}")
            
            elif choice == "4":
                # Basic mode (original functionality)
                print("\n🔄 Basic Mode - Original Functionality")
                print("Choose input method:")
                print("1. Text input")
                print("2. File upload")
                
                basic_choice = input("Enter choice (1-2): ").strip()
                
                if basic_choice == "1":
                    print("\nEnter your text (type 'END' on a new line to finish):")
                    full_text = []
                    while True:
                        line = input()
                        if line == "END":
                            break
                        full_text.append(line)
                    
                    if full_text:
                        text_content = "\n".join(full_text)
                        extraction_result = self.pdf_text_pipeline.extract_from_text(text_content)
                        # Use basic generation (would need to implement fallback)
                        print("Basic mode content processed (enhanced generation not used)")
                
                elif basic_choice == "2":
                    file_path = input("Enter file path: ").strip()
                    extraction_result = self.process_file(file_path)
                    print("Basic mode file processed (enhanced generation not used)")
            
            elif choice == "5":
                print("\n👋 Thank you for using Advanced LinkedIn Blog AI Assistant!")
                break
            else:
                print("❌ Invalid choice! Please enter 1-5.")
    
    def _display_enhancement_metrics(self, results: dict):
        """Display enhancement and performance metrics"""
        if results.get("performance_prediction"):
            perf = results["performance_prediction"]
            print(f"\n📊 Performance Prediction:")
            print(f"   • Engagement Likelihood: {perf.get('engagement_likelihood', 0)}%")
            print(f"   • Viral Potential: {perf.get('viral_potential', 0)}%")
            print(f"   • Optimization Score: {perf.get('optimization_score', 0)}/100")
            print(f"   • Predicted Reach: {perf.get('predicted_reach', 'Unknown')}")
        
        print(f"\n🔄 Enhancement Metrics:")
        print(f"   • Revisions Made: {results.get('revision_count', 0)}")
        print(f"   • Versions Generated: {len(results.get('all_versions', []))}")
        
        if results.get("critique_history"):
            latest_critique = results["critique_history"][-1]
            print(f"   • Final Quality Scores:")
            print(f"     - Language: {latest_critique.language_score}/10")
            print(f"     - Content: {latest_critique.content_score}/10")
            print(f"     - Engagement: {latest_critique.engagement_score}/10")

def main():
    """Main entry point for advanced LinkedIn Blog AI Assistant"""
    print("🚀 Starting Advanced LinkedIn Blog AI Assistant...")
    print("Features: Enhanced AI agents, research capabilities, critique workflow")
    
    # Get API keys from environment
    openai_key = os.getenv('OPENAI_API_KEY')
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not all([openai_key, anthropic_key, google_key]):
        print("⚠️  Warning: Some API keys are missing. Set them as environment variables:")
        print("   • OPENAI_API_KEY")
        print("   • ANTHROPIC_API_KEY") 
        print("   • GOOGLE_API_KEY")
        print()
    
    # Initialize and run advanced assistant
    assistant = AdvancedLinkedInBlogAIAssistant(
        openai_key=openai_key,
        anthropic_key=anthropic_key,
        google_key=google_key
    )
    
    assistant.run_interactive_mode()

if __name__ == "__main__":
    main()