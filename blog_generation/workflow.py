from typing import Literal
from langgraph.graph import StateGraph, END, START
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langsmith_config import trace_step, langsmith_client
from blog_generation.config import (
    BlogGenerationState, BlogPost, CritiqueResult, HumanFeedback,
    ProcessingStatus, BlogQuality, BlogConfig
)
from blog_generation.blog_generator import BlogGeneratorAgent
from blog_generation.critique_agent import CritiqueAgent
from blog_generation.refinement_agent import RefinementAgent


class BlogGenerationWorkflow:
    """LangGraph-powered circular workflow for blog generation and critique"""
    
    def __init__(self):
        self.generator = BlogGeneratorAgent()
        self.critic = CritiqueAgent()
        self.refiner = RefinementAgent()
        self.workflow = None
        self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow with circular critique loop"""
        workflow = StateGraph(BlogGenerationState)
        
        # Nodes
        workflow.add_node("generate_content", self.generate_content_node)
        workflow.add_node("critique_content", self.critique_content_node)
        workflow.add_node("refine_content", self.refine_content_node)
        workflow.add_node("human_review", self.human_review_node)
        workflow.add_node("final_polish", self.final_polish_node)
        workflow.add_node("error_recovery", self.error_recovery_node)
        
        # Edges
        workflow.add_edge(START, "generate_content")
        
        workflow.add_conditional_edges(
            "generate_content",
            self.after_generation_routing,
            {
                "critique_content": "critique_content",
                "error_recovery": "error_recovery",
                "generate_content": "generate_content",
            },
        )
        
        workflow.add_conditional_edges(
            "critique_content",
            self.after_critique_routing,
            {
                "refine_content": "refine_content",
                "human_review": "human_review",
                "final_polish": "final_polish",
                "error_recovery": "error_recovery",
            },
        )
        
        workflow.add_conditional_edges(
            "refine_content",
            self.after_refinement_routing,
            {
                "critique_content": "critique_content",
                "human_review": "human_review",
                "final_polish": "final_polish",
                "error_recovery": "error_recovery",
            },
        )
        
        workflow.add_conditional_edges(
            "human_review",
            self.after_human_review_routing,
            {
                "final_polish": "final_polish",
                "refine_content": "refine_content",
                "generate_content": "generate_content",
                "END": END,
            },
        )
        
        workflow.add_conditional_edges(
            "error_recovery",
            self.after_error_recovery_routing,
            {
                "generate_content": "generate_content",
                "critique_content": "critique_content",
                "refine_content": "refine_content",
                "END": END,
            },
        )
        
        workflow.add_edge("final_polish", END)
        
        self.workflow = workflow.compile()
    
    # ===== NODE IMPLEMENTATIONS =====
    
    @trace_step("blog_generation", "llm")
    def generate_content_node(self, state: BlogGenerationState) -> dict:
        """
        Generate blog content with detailed tracing
        
        This shows you:
        - Input prompt construction
        - Model response quality
        - Parsing success/failure
        - Generation time
        """
        print(f"\n🤖 === GENERATE CONTENT NODE (Iteration {state.iteration_count + 1}) ===")
        try:
            state.current_status = ProcessingStatus.GENERATING
            state.iteration_count += 1
            
            blog_post, error = self.generator.generate_blog(state)
            if blog_post:
                state.current_blog = blog_post
                state.blog_history.append(blog_post)
                return {
                    "current_blog": blog_post,
                    "blog_history": state.blog_history,
                    "current_status": ProcessingStatus.GENERATING,
                    "iteration_count": state.iteration_count,
                    "last_error": "",
                }
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED,
            }
        except Exception as e:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": str(e),
                "current_status": ProcessingStatus.FAILED,
            }
    
    def critique_content_node(self, state: BlogGenerationState) -> dict:
        """Critique generated content for quality and engagement"""
        print(f"\n🔍 === CRITIQUE CONTENT NODE ===")
        try:
            if not state.current_blog:
                return {
                    "error_count": state.error_count + 1,
                    "last_error": "No blog content to critique",
                    "current_status": ProcessingStatus.FAILED,
                }
            state.current_status = ProcessingStatus.CRITIQUING
            context = f"Iteration {state.iteration_count}, Previous score: {state.latest_critique.quality_score if state.latest_critique else 'N/A'}"
            critique, error = self.critic.critique_blog(state.current_blog, context)
            if critique:
                state.latest_critique = critique
                state.critique_history.append(critique)
                return {
                    "latest_critique": critique,
                    "critique_history": state.critique_history,
                    "current_status": ProcessingStatus.CRITIQUING,
                    "last_error": "",
                }
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED,
            }
        except Exception as e:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": str(e),
                "current_status": ProcessingStatus.FAILED,
            }
    
    def refine_content_node(self, state: BlogGenerationState) -> dict:
        """Refine content based on critique feedback"""
        print(f"\n🔧 === REFINE CONTENT NODE ===")
        try:
            if not state.current_blog or not state.latest_critique:
                return {
                    "error_count": state.error_count + 1,
                    "last_error": "Missing blog content or critique for refinement",
                    "current_status": ProcessingStatus.FAILED,
                }
            state.current_status = ProcessingStatus.REFINING
            focus_areas = self._extract_focus_areas(state.latest_critique)
            refined_post, error = self.refiner.refine_blog(
                original_post=state.current_blog,
                critique=state.latest_critique,
                focus_areas=focus_areas,
                human_feedback=state.human_feedback,
            )
            if refined_post:
                state.current_blog = refined_post
                state.blog_history.append(refined_post)
                return {
                    "current_blog": refined_post,
                    "blog_history": state.blog_history,
                    "current_status": ProcessingStatus.REFINING,
                    "last_error": "",
                }
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": error,
                "current_status": ProcessingStatus.FAILED,
            }
        except Exception as e:
            state.error_count += 1
            return {
                "error_count": state.error_count,
                "last_error": str(e),
                "current_status": ProcessingStatus.FAILED,
            }
    
    def human_review_node(self, state: BlogGenerationState) -> dict:
        """Human-in-the-loop review step (placeholder)"""
        print(f"\n🧑‍⚖️ === HUMAN REVIEW NODE ===")
        return {
            "human_feedback": state.human_feedback,
            "human_approved": state.human_approved,
            "current_status": state.current_status,
        }
    
    def final_polish_node(self, state: BlogGenerationState) -> dict:
        """Finalize the blog post for publication"""
        print(f"\n✨ === FINAL POLISH NODE ===")
        if state.current_blog:
            state.final_blog = state.current_blog
            state.generation_complete = True
            state.current_status = ProcessingStatus.COMPLETED
            return self._get_complete_state_dict(state, {
                "final_blog": state.final_blog,
                "generation_complete": True,
                "current_status": ProcessingStatus.COMPLETED,
                "last_error": "",
            })
        return self._get_complete_state_dict(state, {
            "current_status": ProcessingStatus.FAILED,
            "last_error": "No blog available to finalize",
        })
    
    def error_recovery_node(self, state: BlogGenerationState) -> dict:
        """Attempt to recover from previous error by deciding next retry target"""
        print(f"\n🩹 === ERROR RECOVERY NODE ===")
        state.error_count += 1
        return {
            "error_count": state.error_count,
            "last_error": state.last_error,
        }
    
    # ===== ROUTING FUNCTIONS =====
    def after_generation_routing(self, state: BlogGenerationState) -> Literal["critique_content", "error_recovery", "generate_content"]:
        if state.current_blog:
            return "critique_content"
        if state.error_count >= state.max_errors:
            return "error_recovery"
        return "generate_content"
    
    def after_critique_routing(self, state: BlogGenerationState) -> Literal["refine_content", "human_review", "final_polish", "error_recovery"]:
        if not state.latest_critique:
            return "error_recovery" if state.error_count >= state.max_errors else "refine_content"
        score = state.latest_critique.quality_score
        if score >= BlogConfig.MIN_QUALITY_SCORE:
            return "final_polish"
        if state.iteration_count >= state.max_iterations:
            return "human_review"
        return "refine_content"
    
    def after_refinement_routing(self, state: BlogGenerationState) -> Literal["critique_content", "human_review", "final_polish", "error_recovery"]:
        if state.error_count >= state.max_errors:
            return "error_recovery"
        if state.iteration_count >= state.max_iterations:
            return "final_polish"
        return "critique_content"
    
    def after_human_review_routing(self, state: BlogGenerationState) -> Literal["final_polish", "refine_content", "generate_content", "END"]:
        if state.human_approved:
            return "final_polish"
        fb = (state.human_feedback or "").lower()
        if "regenerate" in fb:
            return "generate_content"
        if fb.strip():
            return "refine_content"
        return "END"
    
    def after_error_recovery_routing(self, state: BlogGenerationState) -> Literal["generate_content", "critique_content", "refine_content", "END"]:
        if state.error_count >= state.max_errors:
            return "END"
        if state.current_status == ProcessingStatus.GENERATING:
            return "generate_content"
        if state.current_status == ProcessingStatus.CRITIQUING:
            return "critique_content"
        if state.current_status == ProcessingStatus.REFINING:
            return "refine_content"
        return "generate_content"
    
    # ===== HELPERS =====
    def _get_complete_state_dict(self, state: BlogGenerationState, updates: dict = None) -> dict:
        """Get complete state as dictionary with optional updates"""
        state_dict = {
            "source_content": state.source_content,
            "source_file_path": state.source_file_path,
            "content_insights": state.content_insights,
            "user_requirements": state.user_requirements,
            "current_blog": state.current_blog,
            "final_blog": state.final_blog,
            "blog_history": state.blog_history,
            "latest_critique": state.latest_critique,
            "critique_history": state.critique_history,
            "human_feedback": state.human_feedback,
            "human_approved": state.human_approved,
            "generation_complete": state.generation_complete,
            "current_status": state.current_status,
            "iteration_count": state.iteration_count,
            "error_count": state.error_count,
            "last_error": state.last_error,
            "max_iterations": state.max_iterations,
            "max_errors": state.max_errors,
        }
        
        if updates:
            state_dict.update(updates)
        
        return state_dict
    
    def _extract_focus_areas(self, critique: CritiqueResult) -> list[str]:
        areas = []
        for weakness in critique.weaknesses[:5]:
            wl = weakness.lower()
            if "hook" in wl:
                areas.append("hook")
            if "value" in wl or "insight" in wl:
                areas.append("value")
            if "engagement" in wl:
                areas.append("engagement")
            if "hashtag" in wl:
                areas.append("hashtags")
            if "cta" in wl or "call" in wl:
                areas.append("cta")
            if "length" in wl:
                areas.append("length")
        return list(dict.fromkeys(areas))
    
    # ===== PUBLIC RUNNER =====
    @trace_step("workflow_execution", "workflow")
    def run(self, initial_state: BlogGenerationState) -> BlogGenerationState:
        """
        Execute workflow with comprehensive tracing
        
        This will show you:
        - The complete workflow execution path
        - Time spent in each node
        - State transitions between nodes
        - Quality improvements across iterations
        """
        assert self.workflow is not None, "Workflow not compiled"
        
        # LangGraph will automatically trace the workflow execution
        # Each node will appear as a separate trace step
        result = self.workflow.invoke(initial_state)
        
        # Ensure we return a proper BlogGenerationState object
        if isinstance(result, dict):
            # Convert dict back to BlogGenerationState
            return BlogGenerationState(**result)
        return result
    
    def run_workflow(self, initial_state: BlogGenerationState) -> BlogGenerationState:
        """Alias for run() method for compatibility with main.py"""
        return self.run(initial_state)
    
    def add_human_feedback(self, state: BlogGenerationState, feedback: HumanFeedback) -> BlogGenerationState:
        """Add human feedback to the state and prepare for refinement"""
        state.human_feedback = feedback.feedback_text
        state.human_approved = feedback.approve_current
        state.current_status = ProcessingStatus.REFINING
        return state