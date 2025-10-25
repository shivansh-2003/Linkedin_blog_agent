"""
Simplified chatbot orchestrator - thin integration layer.
Routes user input to appropriate systems and manages conversation flow.
"""

import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

# Add parent for imports
sys.path.append(str(Path(__file__).parent.parent))

# LangSmith tracing
from langsmith_config import trace_step

# Local imports
from .config import (
    ChatStage,
    MessageType,
    ChatbotConfig,
    ResponseTemplates
)
from .memory import ConversationMemory

# System imports
from ingestion.unified_processor import UnifiedProcessor
from ingestion.config import ProcessedContent

from blog_generation.workflow import BlogWorkflow
from blog_generation.config import BlogGenerationState, BlogPost, CritiqueResult


class ChatbotOrchestrator:
    """
    Simplified chatbot orchestrator.
    
    Architecture:
    - User input → Detect intent (simple pattern matching)
    - Route to: Ingestion (files) or Blog Workflow (generation/refinement)
    - Update conversation memory
    - Return response to user
    """
    
    def __init__(self, session_id: str = None):
        """
        Initialize chatbot orchestrator.
        
        Args:
            session_id: Optional session ID for resuming conversations
        """
        # Initialize memory
        self.memory = ConversationMemory(session_id)
        self.session_id = self.memory.session_id
        
        # Initialize processing systems
        self.ingestion = UnifiedProcessor()
        self.blog_workflow = BlogWorkflow()
        
        print(f"🤖 {ChatbotConfig.CHATBOT_NAME} initialized")
        print(f"📝 Session: {self.session_id}")
    
    # ===== MAIN ENTRY POINT =====
    
    @trace_step("chatbot_process_message", "workflow")
    async def process_message(
        self,
        user_input: str,
        file_path: Optional[str] = None
    ) -> str:
        """
        Main entry point for processing user messages.
        
        Args:
            user_input: User's message text
            file_path: Optional file path if user uploaded file
            
        Returns:
            Assistant's response text
        """
        # Add user message to memory
        self.memory.add_user_message(user_input)
        
        # Route based on simple intent detection
        try:
            if file_path:
                response = await self._handle_file_input(file_path, user_input)
            elif self._is_text_content(user_input):
                response = await self._handle_text_input(user_input)
            elif self._is_feedback(user_input):
                response = await self._handle_feedback(user_input)
            elif self._is_approval(user_input):
                response = await self._handle_approval()
            elif self._is_start_over(user_input):
                response = self._handle_start_over()
            else:
                response = self._handle_general_chat(user_input)
            
            # Add response to memory
            self.memory.add_assistant_message(response)
            
            return response
            
        except Exception as e:
            error_response = ResponseTemplates.ERROR.format(error=str(e))
            self.memory.add_assistant_message(error_response)
            return error_response
    
    # ===== INTENT DETECTION (SIMPLE) =====
    
    def _is_text_content(self, text: str) -> bool:
        """Check if user is providing content to process"""
        # Long text (>100 chars) or starts with content indicators
        if len(text) > 100:
            return True
        
        indicators = [
            "here's my content", "here is my content",
            "please process this", "create a post about",
            "write about", "make a post about"
        ]
        return any(phrase in text.lower() for phrase in indicators)
    
    def _is_feedback(self, text: str) -> bool:
        """Check if user is providing feedback for refinement"""
        # Only if we have a blog context
        if not self.memory.state.blog_context:
            return False
        
        # Only if currently reviewing draft
        if self.memory.state.current_stage != ChatStage.REVIEWING_DRAFT:
            return False
        
        feedback_keywords = [
            "make it", "change", "add more", "remove",
            "more technical", "more simple", "more engaging",
            "shorter", "longer", "improve", "enhance",
            "can you", "could you"
        ]
        return any(keyword in text.lower() for keyword in feedback_keywords)
    
    def _is_approval(self, text: str) -> bool:
        """Check if user approves current draft"""
        approval_phrases = [
            "looks good", "perfect", "great", "awesome",
            "love it", "that's it", "approved", "publish",
            "done", "ready", "good to go"
        ]
        return any(phrase in text.lower() for phrase in approval_phrases)
    
    def _is_start_over(self, text: str) -> bool:
        """Check if user wants to start over"""
        restart_phrases = [
            "start over", "new post", "different topic",
            "something else", "another post", "fresh start"
        ]
        return any(phrase in text.lower() for phrase in restart_phrases)
    
    # ===== REQUEST HANDLERS =====
    
    @trace_step("handle_file_input", "workflow")
    async def _handle_file_input(self, file_path: str, user_text: str) -> str:
        """
        Handle file upload and automatic blog generation.
        
        Flow: File → Ingestion → Blog Generation → Present Draft
        """
        print(f"📁 Processing file: {file_path}")
        
        # Update stage
        self.memory.update_stage(ChatStage.AWAITING_CONTENT)
        
        # Process file through ingestion
        processed = await self.ingestion.process_file(file_path)
        
        if not processed.success:
            return f"❌ Sorry, I couldn't process that file: {processed.error_message}"
        
        # Create blog context
        self.memory.create_blog_context(
            source_content=processed.raw_content,
            source_type="file",
            source_path=file_path,
            content_insights=processed.insights.key_insights if processed.insights else [],
            user_requirements=self._extract_requirements(user_text)
        )
        
        # Generate blog automatically
        return await self._generate_blog()
    
    @trace_step("handle_text_input", "workflow")
    async def _handle_text_input(self, text: str) -> str:
        """
        Handle text content input and automatic blog generation.
        
        Flow: Text → Blog Generation → Present Draft
        """
        print(f"📝 Processing text input ({len(text)} chars)")
        
        # Update stage
        self.memory.update_stage(ChatStage.AWAITING_CONTENT)
        
        # Create blog context
        self.memory.create_blog_context(
            source_content=text,
            source_type="text",
            user_requirements=self._extract_requirements(text)
        )
        
        # Generate blog automatically
        return await self._generate_blog()
    
    @trace_step("generate_blog", "workflow")
    async def _generate_blog(self) -> str:
        """
        Generate blog using autonomous workflow.
        
        This runs the complete Generate → Critique → Refine loop.
        """
        print(f"🎨 Generating blog post...")
        
        blog_context = self.memory.get_blog_context()
        if not blog_context:
            return "❌ No content to generate blog from."
        
        # Create workflow state
        state = BlogGenerationState(
            source_content=blog_context.source_content,
            content_insights=blog_context.content_insights,
            user_requirements=blog_context.user_requirements,
            max_iterations=ChatbotConfig.DEFAULT_MAX_ITERATIONS
        )
        
        # Run autonomous workflow (completes fully)
        result = self.blog_workflow.run(state)
        
        if not result.final_blog:
            return f"❌ Blog generation failed: {result.last_error}"
        
        # Store result in context
        self.memory.add_blog_version(
            blog_post=result.final_blog.model_dump(),
            critique=result.latest_critique.model_dump() if result.latest_critique else None,
            quality_score=result.latest_critique.quality_score if result.latest_critique else None
        )
        
        # Update stage
        self.memory.update_stage(ChatStage.REVIEWING_DRAFT)
        
        # Format response
        return self._format_blog_presentation(result.final_blog, result.latest_critique)
    
    @trace_step("handle_feedback", "workflow")
    async def _handle_feedback(self, feedback: str) -> str:
        """
        Handle user feedback and refine blog.
        
        Creates new state with feedback and re-runs workflow for ONE refinement.
        """
        print(f"💬 Processing feedback: {feedback[:50]}...")
        
        blog_context = self.memory.get_blog_context()
        if not blog_context or not blog_context.current_blog:
            return "❌ No blog to refine. Let's start fresh!"
        
        # Add feedback to history
        self.memory.add_feedback(feedback)
        
        # Convert current blog back to BlogPost
        current_blog = BlogPost(**blog_context.current_blog)
        current_critique = CritiqueResult(**blog_context.current_critique) if blog_context.current_critique else None
        
        if not current_critique:
            return "❌ Missing critique data. Please try generating a new post."
        
        # Create new state with human feedback for ONE MORE iteration
        state = BlogGenerationState(
            source_content=blog_context.source_content,
            content_insights=blog_context.content_insights,
            user_requirements=blog_context.user_requirements,
            current_blog=current_blog,
            blog_history=[current_blog],
            latest_critique=current_critique,
            critique_history=[current_critique],
            human_feedback=feedback,
            iteration_count=blog_context.workflow_iterations,
            max_iterations=blog_context.workflow_iterations + 1  # Allow ONE more iteration
        )
        
        # Run workflow (will refine based on feedback)
        result = self.blog_workflow.run(state)
        
        if not result.final_blog:
            return "❌ Refinement failed. Please try different feedback or start over."
        
        # Store refined version
        old_score = current_critique.quality_score
        new_score = result.latest_critique.quality_score if result.latest_critique else old_score
        
        self.memory.add_blog_version(
            blog_post=result.final_blog.model_dump(),
            critique=result.latest_critique.model_dump() if result.latest_critique else None,
            quality_score=new_score
        )
        
        # Format response
        return self._format_refinement_response(
            result.final_blog,
            result.latest_critique,
            old_score,
            new_score
        )
    
    @trace_step("handle_approval", "workflow")
    async def _handle_approval(self) -> str:
        """Handle user approval of current draft"""
        print(f"✅ User approved blog")
        
        blog_context = self.memory.get_blog_context()
        if not blog_context or not blog_context.current_blog:
            return "❌ No blog to approve."
        
        # Mark as completed
        self.memory.complete_blog()
        
        quality_score = blog_context.quality_scores[-1] if blog_context.quality_scores else "N/A"
        
        return ResponseTemplates.COMPLETION.format(quality_score=quality_score)
    
    def _handle_start_over(self) -> str:
        """Handle request to start over"""
        print(f"🔄 Starting over")
        
        self.memory.clear_blog_context()
        self.memory.update_stage(ChatStage.CONVERSING)
        
        return "🔄 Great! Let's start fresh. What would you like to create a LinkedIn post about?"
    
    def _handle_general_chat(self, user_input: str) -> str:
        """Handle general conversation"""
        
        # Check for help request
        if any(word in user_input.lower() for word in ['help', 'how', 'what can you']):
            return ResponseTemplates.WELCOME
        
        # Check for greeting
        if any(word in user_input.lower() for word in ['hi', 'hello', 'hey']):
            return ResponseTemplates.WELCOME
        
        # Default: guide user
        return """
I'm here to help you create LinkedIn posts! 

**Here's what I can do:**
📁 Process documents (PDF, Word, PowerPoint, code files)
📝 Convert text into engaging posts
✨ Refine posts based on your feedback

**To get started:**
- Upload a file, or
- Share the content you want to turn into a post

What would you like to do?
"""
    
    # ===== FORMATTING HELPERS =====
    
    def _format_blog_presentation(
        self,
        blog: BlogPost,
        critique: Optional[CritiqueResult]
    ) -> str:
        """Format blog post for presentation"""
        
        quality_score = critique.quality_score if critique else "N/A"
        quality_level = critique.quality_level.value if critique else "unknown"
        
        # Format blog preview
        preview_parts = [
            f"**{blog.title}**",
            "",
            f"🪝 {blog.hook}",
            "",
            blog.content[:300] + "..." if len(blog.content) > 300 else blog.content,
            "",
            f"👉 {blog.call_to_action}",
            "",
            f"🏷️ {' '.join(blog.hashtags[:5])}"
        ]
        
        blog_preview = "\n".join(preview_parts)
        
        return ResponseTemplates.BLOG_GENERATED.format(
            quality_score=quality_score,
            quality_level=quality_level,
            blog_preview=blog_preview
        )
    
    def _format_refinement_response(
        self,
        blog: BlogPost,
        critique: Optional[CritiqueResult],
        old_score: int,
        new_score: int
    ) -> str:
        """Format refinement response"""
        
        # Format blog preview
        preview_parts = [
            f"**{blog.title}**",
            "",
            f"🪝 {blog.hook}",
            "",
            blog.content[:300] + "..." if len(blog.content) > 300 else blog.content,
            "",
            f"👉 {blog.call_to_action}",
            "",
            f"🏷️ {' '.join(blog.hashtags[:5])}"
        ]
        
        blog_preview = "\n".join(preview_parts)
        
        return ResponseTemplates.REFINEMENT_COMPLETE.format(
            old_score=old_score,
            new_score=new_score,
            blog_preview=blog_preview
        )
    
    def _extract_requirements(self, text: str) -> str:
        """Extract user requirements from text"""
        # Simple extraction - look for audience/tone indicators
        requirements = []
        
        if "technical" in text.lower():
            requirements.append("Technical audience")
        if "beginner" in text.lower() or "simple" in text.lower():
            requirements.append("Beginner-friendly")
        if "professional" in text.lower():
            requirements.append("Professional tone")
        if "casual" in text.lower():
            requirements.append("Casual tone")
        
        return ", ".join(requirements) if requirements else ChatbotConfig.DEFAULT_TONE
    
    # ===== PUBLIC API =====
    
    def get_welcome_message(self) -> str:
        """Get welcome message for new sessions"""
        return ResponseTemplates.WELCOME
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get session information"""
        return self.memory.get_session_info()
    
    def get_current_blog(self) -> Optional[Dict[str, Any]]:
        """Get current blog draft"""
        blog_context = self.memory.get_blog_context()
        return blog_context.current_blog if blog_context else None
    
    def get_conversation_history(self, count: int = 10) -> list:
        """Get recent conversation messages"""
        recent = self.memory.get_recent_messages(count)
        return [
            {
                "type": msg.message_type.value,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat()
            }
            for msg in recent
        ]


# Export
__all__ = ['ChatbotOrchestrator']

