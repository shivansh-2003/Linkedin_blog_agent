#!/usr/bin/env python3
"""
LinkedIn Blog Generation System with LangGraph Circular Workflow

Features:
- Multi-format input processing integration
- LangGraph-powered Generate → Critique → Refine cycle
- Human-in-the-loop feedback integration
- Quality gates and automated validation
- Error handling with model fallbacks
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

# Add parent directory to path for ingestion imports
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from config import (
    BlogGenerationState, BlogPost, HumanFeedback, 
    ProcessingStatus, BlogConfig, ValidationRules
)
from workflow import BlogGenerationWorkflow
from blog_generator import BlogGeneratorAgent
from critique_agent import CritiqueAgent

# Import from ingestion system
try:
    from ingestion.unified_processor import UnifiedProcessor
    from ingestion.config import ProcessedContent
    INGESTION_AVAILABLE = True
except ImportError:
    INGESTION_AVAILABLE = False
    print("⚠️  Ingestion system not available. Using text input only.")

class BlogGenerationApp:
    """Main application for LinkedIn blog generation"""
    
    def __init__(self):
        self.workflow = BlogGenerationWorkflow()
        self.unified_processor = UnifiedProcessor() if INGESTION_AVAILABLE else None
        
    def run_interactive(self):
        """Run interactive blog generation session"""
        print("="*70)
        print("🚀 LINKEDIN BLOG GENERATION SYSTEM")
        print("="*70)
        print("Powered by LangGraph Circular Workflow (Generate → Critique → Refine)")
        
        if not self._check_api_keys():
            return
        
        while True:
            print(f"\n{'='*70}")
            print("Choose input method:")
            print("1. Process file (PDF, Word, PPT, Code, Text, Image)")
            print("2. Direct text input")
            print("3. Example demo")
            print("4. Batch processing")
            print("0. Exit")
            
            choice = input("\nEnter choice (0-4): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                self._process_file_input()
            elif choice == '2':
                self._process_text_input()
            elif choice == '3':
                self._run_demo()
            elif choice == '4':
                self._batch_processing()
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _process_file_input(self):
        """Process file input through ingestion system"""
        if not INGESTION_AVAILABLE:
            print("❌ File processing not available. Ingestion system not imported.")
            return
        
        print("\n📁 File Input Processing")
        file_path = input("Enter file path: ").strip().strip('"')
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        # Process file through ingestion system
        print(f"⏳ Processing {Path(file_path).name}...")
        processed_content = self.unified_processor.process_file(file_path)
        
        if not processed_content.success:
            print(f"❌ File processing failed: {processed_content.error_message}")
            return
        
        # Extract content for blog generation
        source_content = processed_content.extracted_content.raw_text
        insights = processed_content.key_insights
        
        print(f"✅ File processed successfully!")
        print(f"📊 Content length: {len(source_content)} characters")
        print(f"💡 Insights extracted: {len(insights)}")
        
        # Get user requirements
        user_requirements = input("\nAny specific requirements for the blog post? (optional): ").strip()
        
        # Create initial state
        initial_state = BlogGenerationState(
            source_content=source_content,
            source_file_path=file_path,
            content_insights=insights,
            user_requirements=user_requirements
        )
        
        # Run workflow
        self._run_blog_workflow(initial_state)
    
    def _process_text_input(self):
        """Process direct text input"""
        print("\n📝 Direct Text Input")
        print("Enter your content (press Ctrl+D or Ctrl+Z when finished):")
        
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        
        source_content = '\n'.join(lines).strip()
        
        if not source_content:
            print("❌ No content entered.")
            return
        
        print(f"📊 Content length: {len(source_content)} characters")
        
        # Extract basic insights from text
        insights = self._extract_basic_insights(source_content)
        
        # Get user requirements
        user_requirements = input("\nAny specific requirements for the blog post? (optional): ").strip()
        
        # Create initial state
        initial_state = BlogGenerationState(
            source_content=source_content,
            source_file_path="direct_input.txt",
            content_insights=insights,
            user_requirements=user_requirements
        )
        
        # Run workflow
        self._run_blog_workflow(initial_state)
    
    def _run_demo(self):
        """Run demo with sample content"""
        print("\n🎯 Demo: AI Coding Best Practices Blog")
        
        demo_content = """
        Artificial Intelligence and Machine Learning Development Best Practices

        As AI becomes increasingly integrated into business operations, following development best practices is crucial for building reliable, scalable, and maintainable AI systems.

        Key principles include:
        1. Data Quality First - Clean, diverse, and representative datasets are fundamental
        2. Model Versioning - Track experiments, model versions, and performance metrics
        3. Continuous Testing - Implement automated testing for model performance and bias
        4. Ethical AI - Consider fairness, transparency, and potential societal impacts
        5. Monitoring in Production - Track model drift, performance degradation, and user feedback

        Common pitfalls to avoid:
        - Overfitting to training data
        - Ignoring edge cases and rare scenarios
        - Lack of proper documentation
        - Insufficient stakeholder communication
        - Poor data governance practices

        The future of AI development lies in establishing robust MLOps practices that ensure models are not just accurate, but also reliable, fair, and maintainable in production environments.
        """
        
        insights = [
            "Data quality is the foundation of successful AI systems",
            "Model versioning and experiment tracking are essential for reproducibility", 
            "Continuous monitoring prevents model degradation in production",
            "Ethical considerations must be built into the development process",
            "MLOps practices bridge the gap between development and production"
        ]
        
        initial_state = BlogGenerationState(
            source_content=demo_content.strip(),
            source_file_path="demo_ai_best_practices.txt",
            content_insights=insights,
            user_requirements="Create an engaging LinkedIn post that educates professionals about AI development best practices"
        )
        
        self._run_blog_workflow(initial_state)
    
    def _batch_processing(self):
        """Process multiple files in batch"""
        if not INGESTION_AVAILABLE:
            print("❌ Batch processing not available. Ingestion system not imported.")
            return
        
        print("\n📦 Batch Processing")
        directory = input("Enter directory path: ").strip().strip('"')
        
        if not os.path.exists(directory):
            print(f"❌ Directory not found: {directory}")
            return
        
        print("⏳ Processing directory...")
        
        # This would integrate with batch processor from ingestion
        # For now, show concept
        print("🚧 Batch processing integration coming soon!")
        print("💡 Each file would be processed through the circular workflow")
    
    def _run_blog_workflow(self, initial_state: BlogGenerationState):
        """Run the complete blog generation workflow"""
        print(f"\n{'='*70}")
        print("🔄 STARTING BLOG GENERATION WORKFLOW")
        print("="*70)
        
        # Execute workflow
        final_state = self.workflow.run_workflow(initial_state)
        
        # Display results
        self._display_results(final_state)
        
        # Handle human feedback loop
        if not final_state.generation_complete:
            self._handle_human_feedback_loop(final_state)
    
    def _display_results(self, state: BlogGenerationState):
        """Display workflow results"""
        print(f"\n{'='*70}")
        print("📊 WORKFLOW RESULTS")
        print("="*70)
        
        print(f"Status: {state.current_status}")
        print(f"Iterations: {state.iteration_count}")
        print(f"Errors: {state.error_count}")
        
        if state.final_blog:
            self._display_blog_post(state.final_blog, "FINAL BLOG POST")
        elif state.current_blog:
            self._display_blog_post(state.current_blog, "CURRENT BLOG POST")
        
        if state.latest_critique:
            print(f"\n📈 Latest Quality Score: {state.latest_critique.quality_score}/10")
            print(f"Quality Level: {state.latest_critique.quality_level}")
            
            if state.latest_critique.strengths:
                print("\n✅ Strengths:")
                for strength in state.latest_critique.strengths:
                    print(f"   • {strength}")
            
            if state.latest_critique.weaknesses:
                print("\n⚠️  Areas for Improvement:")
                for weakness in state.latest_critique.weaknesses:
                    print(f"   • {weakness}")
        
        # Save to file
        save_option = input("\n💾 Save blog post to file? (y/N): ").strip().lower()
        if save_option == 'y':
            self._save_blog_to_file(state.final_blog or state.current_blog)
    
    def _display_blog_post(self, blog_post: BlogPost, title: str):
        """Display formatted blog post"""
        print(f"\n{title}")
        print("="*len(title))
        print(f"📝 Title: {blog_post.title}")
        print(f"🎣 Hook: {blog_post.hook}")
        print(f"\n📄 Content:\n{blog_post.content}")
        print(f"\n📢 Call-to-Action: {blog_post.call_to_action}")
        print(f"🏷️  Hashtags: {' '.join(blog_post.hashtags)}")
        print(f"🎯 Target Audience: {blog_post.target_audience}")
        if blog_post.estimated_engagement_score:
            print(f"📈 Engagement Score: {blog_post.estimated_engagement_score}/10")
    
    def _handle_human_feedback_loop(self, state: BlogGenerationState):
        """Handle human feedback and continuation"""
        print(f"\n{'='*70}")
        print("👤 HUMAN FEEDBACK LOOP")
        print("="*70)
        
        while not state.generation_complete and state.error_count < BlogConfig.MAX_ERRORS:
            print("\nOptions:")
            print("1. Provide feedback for refinement")
            print("2. Approve current version")
            print("3. Request complete regeneration") 
            print("4. Exit workflow")
            
            choice = input("\nEnter choice (1-4): ").strip()
            
            if choice == '1':
                feedback_text = input("Enter your feedback: ").strip()
                satisfaction = int(input("Satisfaction level (1-5): ").strip() or "3")
                
                feedback = HumanFeedback(
                    feedback_text=feedback_text,
                    satisfaction_level=satisfaction,
                    approve_current=False
                )
                
                state = self.workflow.add_human_feedback(state, feedback)
                state = self.workflow.run_workflow(state)
                self._display_results(state)
                
            elif choice == '2':
                state.human_approved = True
                state.generation_complete = True
                print("✅ Blog approved and finalized!")
                break
                
            elif choice == '3':
                # Reset for regeneration
                state.iteration_count = 0
                state.human_feedback = "Please regenerate with a completely different approach"
                state = self.workflow.run_workflow(state)
                self._display_results(state)
                
            elif choice == '4':
                print("👋 Exiting workflow")
                break
            
            else:
                print("❌ Invalid choice")
    
    def _save_blog_to_file(self, blog_post: BlogPost):
        """Save blog post to file"""
        if not blog_post:
            print("❌ No blog post to save")
            return
        
        filename = f"linkedin_blog_{blog_post.title[:30].replace(' ', '_').lower()}.txt"
        filename = "".join(c for c in filename if c.isalnum() or c in '._-')
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("LinkedIn Blog Post\n")
                f.write("="*50 + "\n\n")
                f.write(f"Title: {blog_post.title}\n\n")
                f.write(f"Hook: {blog_post.hook}\n\n")
                f.write("Content:\n")
                f.write("-" * 20 + "\n")
                f.write(blog_post.content + "\n\n")
                f.write(f"Call-to-Action: {blog_post.call_to_action}\n\n")
                f.write(f"Hashtags: {' '.join(blog_post.hashtags)}\n\n")
                f.write(f"Target Audience: {blog_post.target_audience}\n")
                
                if blog_post.estimated_engagement_score:
                    f.write(f"Estimated Engagement Score: {blog_post.estimated_engagement_score}/10\n")
            
            print(f"✅ Blog saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving file: {e}")
    
    def _extract_basic_insights(self, content: str) -> list[str]:
        """Extract basic insights from text content"""
        insights = []
        
        # Simple keyword-based insight extraction
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 50]
        
        # Look for sentences with insight keywords
        insight_keywords = ['important', 'key', 'crucial', 'essential', 'critical', 'significant']
        
        for sentence in sentences[:10]:  # Limit to first 10 sentences
            if any(keyword in sentence.lower() for keyword in insight_keywords):
                insights.append(sentence.strip() + '.')
        
        # Add some general insights if none found
        if not insights:
            insights = [
                "Content provides valuable professional insights",
                "Information relevant to industry best practices",
                "Practical applications for professional development"
            ]
        
        return insights[:5]  # Limit to 5 insights
    
    def _check_api_keys(self) -> bool:
        """Check if required API keys are set"""
        if not BlogConfig.GROQ_API_KEY:
            print("❌ Missing GROQ_API_KEY environment variable")
            print("Please set your Groq API key and try again.")
            return False
        
        print("✅ API keys configured")
        return True

def main():
    """Main entry point"""
    try:
        app = BlogGenerationApp()
        app.run_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()