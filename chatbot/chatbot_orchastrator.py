import os
import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from chatbot.config import (
    ChatStage, MessageType, ChatMessage, BlogContext, ConversationState,
    ChatbotConfig, UserIntent
)
from chatbot.conversation_memory import ConversationMemoryManager, MemoryUtils
from chatbot.intent_recognition import ContextualIntentRecognizer

# Import ingestion and blog generation systems
try:
    from ingestion.unified_processor import UnifiedProcessor
    from ingestion.multi_file_processor import MultiFileProcessor
    from blog_generation.workflow import BlogGenerationWorkflow
    from blog_generation.config import BlogGenerationState, HumanFeedback, AggregatedBlogGenerationState, AggregationStrategy
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Core systems not available: {e}")
    SYSTEMS_AVAILABLE = False

class ChatbotOrchestrator:
    """Main chatbot orchestrator that manages conversation flow and system integration"""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or MemoryUtils.create_session_id()
        
        # Initialize core components
        self.memory = ConversationMemoryManager(self.session_id)
        self.intent_recognizer = ContextualIntentRecognizer()
        
        # Initialize processing systems
        if SYSTEMS_AVAILABLE:
            self.ingestion_processor = UnifiedProcessor()
            self.multi_file_processor = MultiFileProcessor()
            self.blog_workflow = BlogGenerationWorkflow()
        else:
            self.ingestion_processor = None
            self.multi_file_processor = None
            self.blog_workflow = None
            print("⚠️  Running in limited mode - ingestion and blog generation unavailable")
        
        # State tracking
        self.current_stage = self.memory.conversation_state.current_stage
        self.processing_lock = False
        
        print(f"🤖 ChatBot initialized with session: {self.session_id}")
    
    async def process_user_input(self, user_input: str, file_path: str = None) -> str:
        """Main entry point for processing user input"""
        
        if self.processing_lock:
            return "Please wait, I'm still processing your previous request..."
        
        try:
            self.processing_lock = True
            
            # Add user message to memory
            self.memory.add_message(
                MessageType.USER, 
                user_input,
                file_path=file_path
            )
            
            # Recognize user intent
            intent = self.intent_recognizer.recognize_intent_with_context(
                user_input, 
                self.current_stage
            )
            
            print(f"🔍 Detected intent: {intent.intent_type} (confidence: {intent.confidence:.2f})")
            
            # Route to appropriate handler
            response = await self._route_intent(intent, user_input, file_path)
            
            # Add assistant response to memory
            self.memory.add_message(MessageType.ASSISTANT, response)
            
            # Update context for intent recognizer
            self.intent_recognizer.update_context(user_input, response, self.current_stage)
            
            return response
            
        except Exception as e:
            error_response = f"I encountered an error: {str(e)}. Let's try again!"
            self.memory.add_message(MessageType.ASSISTANT, error_response)
            return error_response
        
        finally:
            self.processing_lock = False
    
    async def _route_intent(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Route user intent to appropriate handler"""
        
        handlers = {
            "file_upload": self._handle_file_upload,
            "start_blog": self._handle_start_blog,
            "provide_feedback": self._handle_provide_feedback,
            "approve_draft": self._handle_approve_draft,
            "start_over": self._handle_start_over,
            "ask_question": self._handle_ask_question
        }
        
        handler = handlers.get(intent.intent_type, self._handle_unknown)
        return await handler(intent, user_input, file_path)
    
    async def _handle_file_upload(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle file upload and processing"""
        
        if not SYSTEMS_AVAILABLE:
            return "File processing is not available in this mode. Please provide text content directly."
        
        # Determine file path
        target_file = file_path or intent.entities.get("file_path")
        
        if not target_file:
            self._update_stage(ChatStage.AWAITING_INPUT)
            return self._get_response_template("ask_for_input")
        
        if not os.path.exists(target_file):
            return f"I couldn't find the file: {target_file}. Please check the path and try again."
        
        # Update stage and process file
        self._update_stage(ChatStage.PROCESSING_FILE)
        
        # Show processing message
        filename = Path(target_file).name
        file_type = Path(target_file).suffix[1:].upper()
        
        processing_msg = self._get_response_template("file_received").format(
            file_type=file_type,
            filename=filename
        )
        
        # Process file through ingestion system
        try:
            result = self.ingestion_processor.process_file(target_file)
            
            if not result.success:
                self._update_stage(ChatStage.ERROR)
                return f"I had trouble processing your file: {result.error_message}. Please try a different file or provide text content directly."
            
            # Update blog context
            blog_context = BlogContext(
                source_file_path=target_file,
                source_content=result.extracted_content.raw_text,
                ai_analysis=result.ai_analysis,
                key_insights=result.key_insights
            )
            
            self.memory.update_blog_context(blog_context)
            
            # Show processing complete message
            complete_msg = self._get_response_template("processing_complete").format(
                length=len(result.extracted_content.raw_text),
                insights_count=len(result.key_insights)
            )
            
            # Automatically start blog generation
            self._update_stage(ChatStage.GENERATING_BLOG)
            blog_response = await self._generate_initial_blog()
            
            return f"{processing_msg}\n\n{complete_msg}\n\n{blog_response}"
            
        except Exception as e:
            self._update_stage(ChatStage.ERROR)
            return self._get_response_template("error").format(error=str(e))

    async def _handle_multi_file_upload(self, intent: UserIntent, user_input: str, file_paths: List[str] = None) -> str:
        """Handle multiple file upload and aggregation"""
        
        if not SYSTEMS_AVAILABLE:
            return "Multi-file processing is not available in this mode. Please provide text content directly."
        
        # Determine file paths
        target_files = file_paths or intent.entities.get("file_paths", [])
        
        if not target_files:
            self._update_stage(ChatStage.AWAITING_INPUT)
            return "Please provide multiple files for aggregation. You can upload 2-10 files to create a comprehensive LinkedIn post."
        
        if len(target_files) < 2:
            return "Multi-file processing requires at least 2 files. Please provide more files or use single file processing."
        
        if len(target_files) > 10:
            return "Too many files! Please provide 2-10 files for optimal processing."
        
        # Check if all files exist
        missing_files = [f for f in target_files if not os.path.exists(f)]
        if missing_files:
            return f"I couldn't find these files: {', '.join(missing_files)}. Please check the paths and try again."
        
        # Update stage and process files
        self._update_stage(ChatStage.PROCESSING_FILE)
        
        # Show processing message
        filenames = [Path(f).name for f in target_files]
        file_types = [Path(f).suffix[1:].upper() for f in target_files]
        
        processing_msg = f"📁 Processing {len(target_files)} files for aggregation:\n"
        for i, (filename, file_type) in enumerate(zip(filenames, file_types), 1):
            processing_msg += f"   {i}. {filename} ({file_type})\n"
        
        # Determine aggregation strategy from user input
        strategy = self._detect_aggregation_strategy(user_input)
        
        # Process files through multi-file processor
        try:
            multi_source_content = await self.multi_file_processor.process_multiple_files(
                target_files, 
                strategy
            )
            
            # Update blog context with multi-source information
            blog_context = BlogContext(
                source_file_path=", ".join(target_files),
                source_content="",  # Will be populated from multi_source_content
                ai_analysis=f"Multi-source analysis using {strategy.value} strategy",
                key_insights=multi_source_content.unified_insights
            )
            
            # Store multi-source content in memory for later use
            self.memory.conversation_state.blog_context = blog_context
            self.memory.conversation_state.metadata["multi_source_content"] = multi_source_content
            self.memory.conversation_state.metadata["aggregation_strategy"] = strategy.value
            
            # Show processing complete message
            complete_msg = f"✅ Multi-file processing complete!\n"
            complete_msg += f"   📊 Strategy: {strategy.value}\n"
            complete_msg += f"   📝 Sources: {len(multi_source_content.sources)}\n"
            complete_msg += f"   🔗 Cross-references: {len(multi_source_content.cross_references)}\n"
            complete_msg += f"   💡 Unified insights: {len(multi_source_content.unified_insights)}\n"
            
            # Automatically start blog generation
            self._update_stage(ChatStage.GENERATING_BLOG)
            blog_response = await self._generate_initial_blog()
            
            return f"{processing_msg}\n{complete_msg}\n\n{blog_response}"
            
        except Exception as e:
            self._update_stage(ChatStage.ERROR)
            return self._get_response_template("error").format(error=str(e))

    def _detect_aggregation_strategy(self, user_input: str) -> AggregationStrategy:
        """Detect aggregation strategy from user input"""
        
        user_input_lower = user_input.lower()
        
        if any(word in user_input_lower for word in ["compare", "comparison", "versus", "vs", "contrast"]):
            return AggregationStrategy.COMPARISON
        elif any(word in user_input_lower for word in ["sequence", "step", "process", "journey", "flow"]):
            return AggregationStrategy.SEQUENCE
        elif any(word in user_input_lower for word in ["timeline", "chronological", "evolution", "history", "over time"]):
            return AggregationStrategy.TIMELINE
        else:
            return AggregationStrategy.SYNTHESIS  # Default strategy
    
    async def _handle_start_blog(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle request to start blog creation"""
        
        if not SYSTEMS_AVAILABLE:
            return "Blog generation is not available in this mode."
        
        blog_context = self.memory.get_blog_context()
        
        if not blog_context or not blog_context.source_content:
            # No source content available
            self._update_stage(ChatStage.AWAITING_INPUT)
            return "I'd be happy to help you create a LinkedIn post! " + self._get_response_template("ask_for_input")
        
        # Ask for any specific requirements
        if not blog_context.user_requirements:
            blog_context.user_requirements = user_input
            self.memory.update_blog_context(blog_context)
        
        # Generate blog
        self._update_stage(ChatStage.GENERATING_BLOG)
        return await self._generate_initial_blog()
    
    async def _handle_provide_feedback(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle user feedback for blog refinement"""
        
        if not SYSTEMS_AVAILABLE:
            return "Blog refinement is not available in this mode."
        
        blog_context = self.memory.get_blog_context()
        
        if not blog_context or not blog_context.current_draft:
            return "I don't have a current draft to improve. Would you like to create a new blog post?"
        
        # Add feedback to context
        self.memory.add_feedback(user_input)
        
        # Show feedback received message
        focus_areas = intent.specific_requests or ["overall improvement"]
        feedback_msg = self._get_response_template("feedback_received").format(
            focus_areas=", ".join(focus_areas)
        )
        
        # Update stage and refine blog
        self._update_stage(ChatStage.REFINING_BLOG)
        refinement_response = await self._refine_blog_with_feedback(user_input, intent)
        
        return f"{feedback_msg}\n\n{refinement_response}"
    
    async def _handle_approve_draft(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle draft approval"""
        
        blog_context = self.memory.get_blog_context()
        
        if not blog_context or not blog_context.current_draft:
            return "I don't have a current draft to approve. Would you like to create a new blog post?"
        
        # Mark as completed
        self._update_stage(ChatStage.COMPLETED)
        
        # Save the final blog
        self._save_final_blog(blog_context.current_draft)
        
        # Clear context for next blog
        self.memory.clear_blog_context()
        
        return self._get_response_template("session_complete")
    
    async def _handle_start_over(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle request to start over"""
        
        # Clear current blog context
        self.memory.clear_blog_context()
        
        # Reset to initial stage
        self._update_stage(ChatStage.INITIAL)
        
        return "Sure! Let's start fresh. " + self._get_response_template("ask_for_input")
    
    async def _handle_ask_question(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle general questions and help requests"""
        
        # Context-aware responses
        if "help" in user_input.lower():
            return self._get_help_response()
        
        if "what can you do" in user_input.lower():
            return self._get_capabilities_response()
        
        if self.current_stage == ChatStage.INITIAL:
            return self._get_response_template("welcome") + "\n\n" + self._get_response_template("ask_for_input")
        
        # Default response based on current stage
        stage_responses = {
            ChatStage.AWAITING_INPUT: self._get_response_template("ask_for_input"),
            ChatStage.AWAITING_FEEDBACK: self._get_response_template("ask_for_feedback"),
            ChatStage.PRESENTING_DRAFT: "What would you like me to change about the current draft?",
            ChatStage.COMPLETED: "Would you like to create another LinkedIn post?"
        }
        
        return stage_responses.get(self.current_stage, self._get_response_template("clarify_intent"))
    
    async def _handle_unknown(self, intent: UserIntent, user_input: str, file_path: str = None) -> str:
        """Handle unrecognized intents"""
        return self._get_response_template("clarify_intent")
    
    async def _generate_initial_blog(self) -> str:
        """Generate initial blog post using workflow"""
        
        if not SYSTEMS_AVAILABLE:
            return "Blog generation system is not available."
        
        blog_context = self.memory.get_blog_context()
        if not blog_context:
            return "No content available for blog generation."
        
        try:
            # Create blog generation state
            initial_state = BlogGenerationState(
                source_content=blog_context.source_content,
                source_file_path=blog_context.source_file_path or "",
                content_insights=blog_context.key_insights,
                user_requirements=blog_context.user_requirements
            )
            
            # Run workflow
            final_state = self.blog_workflow.run_workflow(initial_state)
            
            if final_state.final_blog:
                # Store the generated blog
                blog_data = {
                    "title": final_state.final_blog.title,
                    "content": final_state.final_blog.content,
                    "hook": final_state.final_blog.hook,
                    "call_to_action": final_state.final_blog.call_to_action,
                    "hashtags": final_state.final_blog.hashtags,
                    "target_audience": final_state.final_blog.target_audience
                }
                
                quality_score = final_state.latest_critique.quality_score if final_state.latest_critique else 7
                
                # Update blog context
                blog_context.current_draft = blog_data
                self.memory.add_blog_draft(blog_data, quality_score)
                
                # Update stage
                self._update_stage(ChatStage.PRESENTING_DRAFT)
                
                # Format response
                return self._get_response_template("draft_ready").format(
                    title=blog_data["title"],
                    hook=blog_data["hook"],
                    content=blog_data["content"],
                    cta=blog_data["call_to_action"],
                    hashtags=" ".join(blog_data["hashtags"]),
                    quality_score=quality_score
                )
            
            else:
                self._update_stage(ChatStage.ERROR)
                return "I had trouble generating your blog post. Let's try a different approach."
        
        except Exception as e:
            self._update_stage(ChatStage.ERROR)
            return f"Blog generation failed: {str(e)}"
    
    async def _refine_blog_with_feedback(self, feedback: str, intent: UserIntent) -> str:
        """Refine blog based on user feedback"""
        
        if not SYSTEMS_AVAILABLE:
            return "Blog refinement system is not available."
        
        blog_context = self.memory.get_blog_context()
        if not blog_context or not blog_context.current_draft:
            return "No current draft available for refinement."
        
        try:
            # Create human feedback object
            human_feedback = HumanFeedback(
                feedback_text=feedback,
                satisfaction_level=3,  # Default moderate satisfaction
                specific_changes=intent.specific_requests or [],
                approve_current=False,
                request_regeneration=False
            )
            
            # Create blog generation state with current context
            current_state = BlogGenerationState(
                source_content=blog_context.source_content,
                content_insights=blog_context.key_insights,
                user_requirements=blog_context.user_requirements,
                human_feedback=feedback,
                iteration_count=len(blog_context.draft_history)
            )
            
            # Add human feedback and re-run workflow
            updated_state = self.blog_workflow.add_human_feedback(current_state, human_feedback)
            refined_state = self.blog_workflow.run_workflow(updated_state)
            
            if refined_state.final_blog:
                # Store refined blog
                refined_data = {
                    "title": refined_state.final_blog.title,
                    "content": refined_state.final_blog.content,
                    "hook": refined_state.final_blog.hook,
                    "call_to_action": refined_state.final_blog.call_to_action,
                    "hashtags": refined_state.final_blog.hashtags,
                    "target_audience": refined_state.final_blog.target_audience
                }
                
                new_quality_score = refined_state.latest_critique.quality_score if refined_state.latest_critique else 7
                old_quality_score = blog_context.quality_scores[-1] if blog_context.quality_scores else 6
                
                # Update context
                blog_context.current_draft = refined_data
                self.memory.add_blog_draft(refined_data, new_quality_score)
                
                # Generate improvement summary
                improvements = self._generate_improvement_summary(intent, refined_data)
                
                # Update stage back to presenting draft
                self._update_stage(ChatStage.PRESENTING_DRAFT)
                
                # Format refinement response
                refinement_response = self._get_response_template("refinement_complete").format(
                    improvements=improvements,
                    quality_score=new_quality_score,
                    old_score=old_quality_score
                )
                
                # Add the refined draft
                draft_response = self._get_response_template("draft_ready").format(
                    title=refined_data["title"],
                    hook=refined_data["hook"],
                    content=refined_data["content"],
                    cta=refined_data["call_to_action"],
                    hashtags=" ".join(refined_data["hashtags"]),
                    quality_score=new_quality_score
                )
                
                return f"{refinement_response}\n\n{draft_response}"
            
            else:
                return "I had trouble refining the post. The current draft is still available. Would you like to try different feedback?"
        
        except Exception as e:
            return f"Refinement failed: {str(e)}. The current draft is still available."
    
    def _generate_improvement_summary(self, intent: UserIntent, refined_data: Dict[str, Any]) -> str:
        """Generate a summary of improvements made"""
        improvements = []
        
        if intent.feedback_type == "content":
            improvements.append("Enhanced content depth and value")
        elif intent.feedback_type == "style":
            improvements.append("Adjusted tone and writing style")
        elif intent.feedback_type == "structure":
            improvements.append("Improved organization and flow")
        elif intent.feedback_type == "engagement":
            improvements.append("Strengthened hook and engagement elements")
        
        if intent.specific_requests:
            improvements.extend([f"Applied: {req}" for req in intent.specific_requests[:2]])
        
        return "\n".join(f"• {imp}" for imp in improvements) if improvements else "• General refinements applied"
    
    def _save_final_blog(self, blog_data: Dict[str, Any]):
        """Save the final approved blog"""
        try:
            output_dir = Path("output/blogs")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            filename = f"blog_{self.session_id}_{int(time.time())}.txt"
            filepath = output_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("LinkedIn Blog Post\n")
                f.write("="*50 + "\n\n")
                f.write(f"Title: {blog_data['title']}\n\n")
                f.write(f"Hook: {blog_data['hook']}\n\n")
                f.write("Content:\n")
                f.write("-"*20 + "\n")
                f.write(blog_data['content'] + "\n\n")
                f.write(f"Call-to-Action: {blog_data['call_to_action']}\n\n")
                f.write(f"Hashtags: {' '.join(blog_data['hashtags'])}\n\n")
                f.write(f"Target Audience: {blog_data.get('target_audience', 'Professional LinkedIn users')}\n")
            
            print(f"💾 Final blog saved to: {filepath}")
            
        except Exception as e:
            print(f"Error saving blog: {e}")
    
    def _update_stage(self, new_stage: ChatStage):
        """Update conversation stage"""
        self.current_stage = new_stage
        self.memory.update_stage(new_stage)
    
    def _get_response_template(self, template_key: str) -> str:
        """Get response template by key"""
        templates = ChatbotConfig.RESPONSE_TEMPLATES
        flow_messages = ChatbotConfig.FLOW_MESSAGES
        
        if template_key in templates:
            template = templates[template_key]
            if isinstance(template, list):
                return "\n".join(template)
            return template
        
        if template_key in flow_messages:
            return flow_messages[template_key]
        
        return "I'm not sure how to respond to that. Can you help me understand what you need?"
    
    def _get_help_response(self) -> str:
        """Get contextual help response"""
        help_text = [
            f"Hi! I'm {ChatbotConfig.CHATBOT_NAME}, your LinkedIn blog creation assistant! 🤖",
            "",
            "Here's how I can help you:",
            "",
            "📁 **File Processing:** Upload PDFs, Word docs, PowerPoint, code files, or images",
            "📝 **Text Input:** Share any text content you want to turn into a blog post",
            "✨ **Blog Generation:** I'll create engaging LinkedIn posts with hooks, content, and CTAs",
            "🔄 **Refinement:** Give me feedback and I'll improve the post",
            "💡 **Optimization:** I ensure posts are optimized for LinkedIn engagement",
            "",
            "**Current stage:** " + self.current_stage.replace("_", " ").title(),
            "",
            "Just tell me what you'd like to create a post about!"
        ]
        
        return "\n".join(help_text)
    
    def _get_capabilities_response(self) -> str:
        """Get capabilities overview"""
        capabilities = [
            "🚀 **My Capabilities:**",
            "",
            "📄 **Multi-format Processing:**",
            "• PDFs, Word documents, PowerPoint presentations",
            "• Code files (Python, JavaScript, Java, etc.)",
            "• Text files and markdown",
            "• Images (with AI vision analysis)",
            "",
            "✍️ **LinkedIn Blog Creation:**",
            "• Attention-grabbing hooks",
            "• Engaging, valuable content",
            "• Strong calls-to-action",
            "• Optimized hashtags",
            "• Professional tone",
            "",
            "🔄 **Interactive Refinement:**",
            "• Quality scoring (1-10 scale)",
            "• Specific feedback incorporation", 
            "• Multiple iteration support",
            "• Human-in-the-loop optimization",
            "",
            "What would you like to create today?"
        ]
        
        return "\n".join(capabilities)
    
    def get_session_summary(self) -> str:
        """Get summary of current session"""
        return self.memory.get_conversation_summary()
    
    def export_conversation(self) -> Dict[str, Any]:
        """Export conversation for analysis"""
        return self.memory.export_conversation()

# Utility functions for easy integration

def create_chatbot_session(session_id: str = None) -> ChatbotOrchestrator:
    """Create a new chatbot session"""
    return ChatbotOrchestrator(session_id)

def get_welcome_message() -> str:
    """Get welcome message for new users"""
    templates = ChatbotConfig.RESPONSE_TEMPLATES["welcome"]
    return "\n".join(templates).format(name=ChatbotConfig.CHATBOT_NAME)

async def quick_process(user_input: str, file_path: str = None, session_id: str = None) -> Tuple[str, str]:
    """Quick processing for simple interactions"""
    bot = ChatbotOrchestrator(session_id)
    response = await bot.process_user_input(user_input, file_path)
    return response, bot.session_id