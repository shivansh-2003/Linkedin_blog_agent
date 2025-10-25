"""
Streamlined LangGraph workflow for autonomous blog generation.
Pure Generate → Critique → Refine loop without human review node.
Human interaction handled separately via chatbot with conversation memory.
"""

from typing import Literal, Optional, Tuple, List, Dict, Any
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
import sys
from pathlib import Path

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent.parent))

# LangSmith tracing
from langsmith_config import trace_step

# Local imports
from .config import (
    BlogPost,
    CritiqueResult,
    BlogGenerationState,
    AggregatedBlogGenerationState,
    ProcessingStatus,
    BlogQuality,
    Config
)
from .prompts import LinkedInPrompts


class BlogWorkflow:
    """
    Autonomous workflow for blog generation.
    Completes Generate → Critique → Refine loop without human intervention.
    Human feedback handled separately via chatbot interface.
    """
    
    def __init__(self):
        """Initialize workflow with shared LLM client"""
        self.prompts = LinkedInPrompts()
        self._init_llm_clients()
        self.graph = None
        self._build_graph()
    
    def _init_llm_clients(self):
        """Initialize LangChain LLM clients with structured output support"""
        base_llm = ChatGroq(
            api_key=Config.GROQ_API_KEY,
            model=Config.PRIMARY_MODEL,
            max_tokens=Config.MAX_TOKENS
        )
        
        # Structured output LLMs for each agent
        self.generator_llm = base_llm.with_structured_output(
            BlogPost,
            method="json_mode"
        ).with_config({"temperature": Config.GENERATION_TEMPERATURE})
        
        self.critic_llm = base_llm.with_structured_output(
            CritiqueResult,
            method="json_mode"
        ).with_config({"temperature": Config.CRITIQUE_TEMPERATURE})
        
        self.refiner_llm = base_llm.with_structured_output(
            BlogPost,
            method="json_mode"
        ).with_config({"temperature": Config.REFINEMENT_TEMPERATURE})
    
    # ===== AGENT IMPLEMENTATIONS =====
    
    @trace_step("blog_generation", "llm")
    def _generate_blog(self, state: BlogGenerationState) -> Tuple[Optional[BlogPost], str]:
        """Content generation agent"""
        print(f"🎨 Generating blog content (Iteration {state.iteration_count})...")
        
        try:
            # Build prompt with previous feedback context
            previous_feedback = ""
            if state.latest_critique:
                weaknesses = "; ".join(state.latest_critique.weaknesses[:3])
                improvements = "; ".join(state.latest_critique.specific_improvements[:3])
                previous_feedback = (
                    f"Previous score: {state.latest_critique.quality_score}/10\n"
                    f"Issues: {weaknesses}\n"
                    f"Needed: {improvements}"
                )
            
            if state.human_feedback:
                previous_feedback += f"\n\nHuman feedback (priority): {state.human_feedback}"
            
            user_prompt = self.prompts.build_generation_prompt(
                source_content=state.source_content,
                insights=state.content_insights,
                user_requirements=state.user_requirements,
                iteration=state.iteration_count,
                previous_feedback=previous_feedback
            )
            
            system_prompt = self.prompts.get_generator_system_prompt()
            
            # Call LLM with structured output
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            blog_post = self.generator_llm.invoke(messages)
            
            # Validate and fix hashtags
            if blog_post.hashtags:
                blog_post.hashtags = [
                    tag if tag.startswith('#') else f"#{tag}"
                    for tag in blog_post.hashtags
                ]
            
            print(f"✅ Generated: {blog_post.title[:50]}...")
            return blog_post, ""
            
        except Exception as e:
            error_msg = f"Generation failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    @trace_step("blog_critique", "llm")
    def _critique_blog(self, blog_post: BlogPost, context: str = "") -> Tuple[Optional[CritiqueResult], str]:
        """Quality critique agent"""
        print(f"🔍 Critiquing blog quality...")
        
        try:
            # Build prompt
            user_prompt = self.prompts.build_critique_prompt(blog_post, context)
            system_prompt = self.prompts.get_critique_system_prompt()
            
            # Call LLM with structured output
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            critique = self.critic_llm.invoke(messages)
            
            # Calculate overall score from dimensions if not set
            if not critique.quality_score:
                critique.quality_score = round((
                    critique.hook_effectiveness +
                    critique.value_delivery +
                    critique.linkedin_optimization +
                    critique.engagement_potential +
                    critique.professional_tone
                ) / 5)
            
            # Determine quality level
            if critique.quality_score >= Config.EXCELLENT_THRESHOLD:
                critique.quality_level = BlogQuality.PUBLISH_READY
            elif critique.quality_score >= Config.MIN_QUALITY_SCORE:
                critique.quality_level = BlogQuality.EXCELLENT
            elif critique.quality_score >= 5:
                critique.quality_level = BlogQuality.GOOD
            else:
                critique.quality_level = BlogQuality.DRAFT
            
            # Auto-approve if excellent
            critique.approved_for_publish = (critique.quality_score >= Config.MIN_QUALITY_SCORE)
            
            print(f"📊 Quality Score: {critique.quality_score}/10 ({critique.quality_level.value})")
            return critique, ""
            
        except Exception as e:
            error_msg = f"Critique failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    @trace_step("blog_refinement", "llm")
    def _refine_blog(
        self,
        original_post: BlogPost,
        critique: CritiqueResult,
        focus_areas: List[str] = None,
        human_feedback: str = ""
    ) -> Tuple[Optional[BlogPost], str]:
        """Content refinement agent"""
        print(f"🔧 Refining blog (Target: {min(critique.quality_score + 2, 10)}/10)...")
        
        try:
            # Build prompt
            user_prompt = self.prompts.build_refinement_prompt(
                original_post=original_post,
                critique=critique,
                focus_areas=focus_areas or [],
                human_feedback=human_feedback
            )
            
            system_prompt = self.prompts.get_refinement_system_prompt()
            
            # Call LLM with structured output
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            refined_post = self.refiner_llm.invoke(messages)
            
            # Validate hashtags
            if refined_post.hashtags:
                refined_post.hashtags = [
                    tag if tag.startswith('#') else f"#{tag}"
                    for tag in refined_post.hashtags
                ]
            
            print(f"✅ Refined successfully")
            return refined_post, ""
            
        except Exception as e:
            error_msg = f"Refinement failed: {str(e)}"
            print(f"❌ {error_msg}")
            return None, error_msg
    
    # ===== GRAPH NODES =====
    
    @trace_step("generate_node", "workflow")
    def generate_node(self, state: BlogGenerationState) -> Dict:
        """Generate content node"""
        print(f"\n{'='*60}")
        print(f"🎨 GENERATE NODE (Iteration {state.iteration_count + 1})")
        print(f"{'='*60}")
        
        state.current_status = ProcessingStatus.GENERATING
        state.iteration_count += 1
        
        blog_post, error = self._generate_blog(state)
        
        if blog_post:
            state.current_blog = blog_post
            state.blog_history.append(blog_post)
            state.last_error = ""
            
            return {
                "current_blog": blog_post,
                "blog_history": state.blog_history,
                "iteration_count": state.iteration_count,
                "current_status": ProcessingStatus.GENERATING,
                "last_error": ""
            }
        else:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED
            }
    
    @trace_step("critique_node", "workflow")
    def critique_node(self, state: BlogGenerationState) -> Dict:
        """Critique content node"""
        print(f"\n{'='*60}")
        print(f"🔍 CRITIQUE NODE")
        print(f"{'='*60}")
        
        if not state.current_blog:
            return {
                "error_count": state.error_count + 1,
                "last_error": "No blog to critique",
                "current_status": ProcessingStatus.FAILED
            }
        
        state.current_status = ProcessingStatus.CRITIQUING
        
        context = f"Iteration {state.iteration_count}"
        if state.latest_critique:
            context += f", Previous score: {state.latest_critique.quality_score}"
        
        critique, error = self._critique_blog(state.current_blog, context)
        
        if critique:
            state.latest_critique = critique
            state.critique_history.append(critique)
            
            return {
                "latest_critique": critique,
                "critique_history": state.critique_history,
                "current_status": ProcessingStatus.CRITIQUING,
                "last_error": ""
            }
        else:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED
            }
    
    @trace_step("refine_node", "workflow")
    def refine_node(self, state: BlogGenerationState) -> Dict:
        """Refine content node"""
        print(f"\n{'='*60}")
        print(f"🔧 REFINE NODE")
        print(f"{'='*60}")
        
        if not state.current_blog or not state.latest_critique:
            return {
                "error_count": state.error_count + 1,
                "last_error": "Missing blog or critique for refinement",
                "current_status": ProcessingStatus.FAILED
            }
        
        state.current_status = ProcessingStatus.REFINING
        
        # Extract focus areas from critique
        focus_areas = self._extract_focus_areas(state.latest_critique)
        
        refined_post, error = self._refine_blog(
            original_post=state.current_blog,
            critique=state.latest_critique,
            focus_areas=focus_areas,
            human_feedback=state.human_feedback
        )
        
        if refined_post:
            state.current_blog = refined_post
            state.blog_history.append(refined_post)
            state.human_feedback = ""  # Clear after use
            
            return {
                "current_blog": refined_post,
                "blog_history": state.blog_history,
                "current_status": ProcessingStatus.REFINING,
                "human_feedback": "",
                "last_error": ""
            }
        else:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED
            }
    
    @trace_step("final_polish_node", "workflow")
    def final_polish_node(self, state: BlogGenerationState) -> Dict:
        """Final polish and completion"""
        print(f"\n{'='*60}")
        print(f"✨ FINAL POLISH NODE")
        print(f"{'='*60}")
        
        if state.current_blog:
            state.final_blog = state.current_blog
            state.generation_complete = True
            state.current_status = ProcessingStatus.COMPLETED
            
            print(f"✅ Blog generation complete!")
            print(f"📊 Final Quality Score: {state.latest_critique.quality_score if state.latest_critique else 'N/A'}/10")
            print(f"🔄 Total Iterations: {state.iteration_count}")
            
            return {
                "final_blog": state.final_blog,
                "generation_complete": True,
                "current_status": ProcessingStatus.COMPLETED
            }
        else:
            return {
                "error_count": state.error_count + 1,
                "last_error": "No blog available for final polish",
                "current_status": ProcessingStatus.FAILED
            }
    
    @trace_step("error_recovery_node", "workflow")
    def error_recovery_node(self, state: BlogGenerationState) -> Dict:
        """Error recovery node"""
        print(f"\n{'='*60}")
        print(f"⚠️  ERROR RECOVERY NODE")
        print(f"{'='*60}")
        
        print(f"❌ Error: {state.last_error}")
        print(f"🔄 Error count: {state.error_count}/{state.max_errors}")
        
        if state.error_count >= state.max_errors:
            state.current_status = ProcessingStatus.FAILED
            print(f"💔 Max errors reached. Workflow failed.")
            
            return {
                "current_status": ProcessingStatus.FAILED,
                "generation_complete": True
            }
        
        # Try to recover by regenerating
        print(f"🔄 Attempting recovery via regeneration...")
        return {
            "current_status": ProcessingStatus.GENERATING,
            "iteration_count": state.iteration_count  # Don't increment for recovery
        }
    
    # ===== ROUTING LOGIC (SIMPLIFIED) =====
    
    def route_after_generation(self, state: BlogGenerationState) -> Literal["critique_node", "error_recovery_node"]:
        """Route after generation"""
        if state.current_blog:
            return "critique_node"
        else:
            return "error_recovery_node"
    
    def route_after_critique(
        self, 
        state: BlogGenerationState
    ) -> Literal["refine_node", "final_polish_node", "error_recovery_node"]:
        """
        Route after critique - AUTONOMOUS DECISION
        
        Logic:
        1. If quality >= threshold (7) → Done, go to final polish
        2. If iterations < max → Continue refinement
        3. If iterations >= max → Best effort, go to final polish
        """
        
        if not state.latest_critique:
            return "error_recovery_node"
        
        score = state.latest_critique.quality_score
        
        # High quality achieved - finish successfully
        if score >= Config.MIN_QUALITY_SCORE:
            print(f"✅ Quality threshold met ({score}/10 >= {Config.MIN_QUALITY_SCORE})")
            return "final_polish_node"
        
        # Max iterations reached - finish with best effort
        if state.iteration_count >= state.max_iterations:
            print(f"⏱️  Max iterations reached ({state.iteration_count}/{state.max_iterations})")
            print(f"📝 Completing with current quality: {score}/10")
            return "final_polish_node"
        
        # Continue refining
        print(f"🔄 Quality below threshold ({score}/10 < {Config.MIN_QUALITY_SCORE}), refining...")
        return "refine_node"
    
    def route_after_refinement(
        self, 
        state: BlogGenerationState
    ) -> Literal["critique_node", "error_recovery_node"]:
        """Route after refinement - CIRCULAR LOOP BACK TO CRITIQUE"""
        if state.current_blog:
            print(f"♻️  Routing back to critique for evaluation")
            return "critique_node"  # CIRCULAR LOOP
        else:
            return "error_recovery_node"
    
    def route_after_error(
        self, 
        state: BlogGenerationState
    ) -> Literal["generate_node", END]:
        """Route after error recovery"""
        if state.error_count < state.max_errors:
            return "generate_node"
        else:
            return END
    
    # ===== HELPER METHODS =====
    
    def _extract_focus_areas(self, critique: CritiqueResult) -> List[str]:
        """Extract focus areas from critique for targeted refinement"""
        areas = []
        
        # Check each dimension score
        if critique.hook_effectiveness < 7:
            areas.append("hook")
        if critique.value_delivery < 7:
            areas.append("value")
        if critique.engagement_potential < 7:
            areas.append("engagement")
        if critique.linkedin_optimization < 7:
            areas.append("linkedin_optimization")
        if critique.professional_tone < 7:
            areas.append("tone")
        
        # If nothing specific, focus on overall quality
        return areas or ["overall_quality"]
    
    # ===== GRAPH CONSTRUCTION =====
    
    def _build_graph(self):
        """Build the autonomous LangGraph workflow"""
        workflow = StateGraph(BlogGenerationState)
        
        # Add nodes (NO HUMAN REVIEW NODE)
        workflow.add_node("generate_node", self.generate_node)
        workflow.add_node("critique_node", self.critique_node)
        workflow.add_node("refine_node", self.refine_node)
        workflow.add_node("final_polish_node", self.final_polish_node)
        workflow.add_node("error_recovery_node", self.error_recovery_node)
        
        # Set entry point
        workflow.add_edge(START, "generate_node")
        
        # Add conditional edges for autonomous flow
        workflow.add_conditional_edges(
            "generate_node",
            self.route_after_generation,
            {
                "critique_node": "critique_node",
                "error_recovery_node": "error_recovery_node"
            }
        )
        
        workflow.add_conditional_edges(
            "critique_node",
            self.route_after_critique,
            {
                "refine_node": "refine_node",
                "final_polish_node": "final_polish_node",
                "error_recovery_node": "error_recovery_node"
            }
        )
        
        # CIRCULAR LOOP: Refine → Critique
        workflow.add_conditional_edges(
            "refine_node",
            self.route_after_refinement,
            {
                "critique_node": "critique_node",  # ← CIRCULAR BACK TO CRITIQUE
                "error_recovery_node": "error_recovery_node"
            }
        )
        
        workflow.add_conditional_edges(
            "error_recovery_node",
            self.route_after_error,
            {
                "generate_node": "generate_node",
                END: END
            }
        )
        
        # Terminal node
        workflow.add_edge("final_polish_node", END)
        
        # Compile
        self.graph = workflow.compile()
        
        print("✅ Workflow compiled successfully")
        print(f"📊 Nodes: generate → critique → refine (circular) → final_polish")
    
    # ===== PUBLIC API =====
    
    @trace_step("workflow_execution", "workflow")
    def run(self, initial_state: BlogGenerationState) -> BlogGenerationState:
        """
        Execute autonomous blog generation workflow.
        Completes Generate → Critique → Refine loop without human intervention.
        
        Args:
            initial_state: Initial workflow state with source content
            
        Returns:
            Final workflow state with generated blog (guaranteed)
        """
        print(f"\n{'='*70}")
        print(f"🚀 STARTING AUTONOMOUS BLOG GENERATION WORKFLOW")
        print(f"{'='*70}")
        print(f"📄 Source: {initial_state.source_content[:80]}...")
        print(f"🎯 Max Iterations: {initial_state.max_iterations}")
        print(f"📏 Quality Threshold: {Config.MIN_QUALITY_SCORE}/10")
        print(f"{'='*70}\n")
        
        # Execute workflow
        final_state = self.graph.invoke(initial_state)
        
        print(f"\n{'='*70}")
        print(f"🏁 WORKFLOW COMPLETE")
        print(f"{'='*70}")
        print(f"✅ Status: {final_state.get('current_status', 'unknown')}")
        print(f"🔄 Iterations Used: {final_state.get('iteration_count', 0)}/{initial_state.max_iterations}")
        
        if final_state.get('final_blog'):
            score = final_state.get('latest_critique', {})
            if isinstance(score, dict):
                score = score.get('quality_score', 'N/A')
            elif hasattr(score, 'quality_score'):
                score = score.quality_score
            else:
                score = 'N/A'
            
            print(f"📊 Final Quality Score: {score}/10")
            print(f"✅ Blog generated successfully")
        else:
            print(f"❌ Blog generation failed: {final_state.get('last_error', 'Unknown error')}")
        
        print(f"{'='*70}\n")
        
        # Convert dict back to state object
        if isinstance(final_state, dict):
            return BlogGenerationState(**final_state)
        return final_state
    
    def run_workflow(self, initial_state: BlogGenerationState) -> BlogGenerationState:
        """Alias for compatibility with existing code"""
        return self.run(initial_state)


__all__ = ['BlogWorkflow']
