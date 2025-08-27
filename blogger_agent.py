
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from deepagents import create_deep_agent
import uuid
import os
import json
from dataclasses import dataclass

@dataclass
class CritiqueResult:
    language_score: int  # 1-10
    content_score: int   # 1-10
    engagement_score: int # 1-10
    language_feedback: str
    content_feedback: str
    engagement_feedback: str
    overall_recommendation: str
    needs_revision: bool

class EnhancedBlogState(TypedDict):
    """Enhanced state for blog generation with critique workflow"""
    # Input data
    extracted_info: str
    source_type: str
    user_context: Dict[str, Any]  # User's industry, expertise, audience
    
    # Generation pipeline
    content_brief: str
    generated_posts: List[str]
    current_post: str
    
    # Critique pipeline  
    critique_results: List[CritiqueResult]
    current_critique: CritiqueResult
    revision_count: int
    
    # Final output
    final_post: str
    performance_prediction: Dict[str, Any]
    status: str

class EnhancedLinkedInBloggerAgent:
    def __init__(self, 
                 anthropic_api_key: str = None,
                 openai_api_key: str = None):
        """Initialize enhanced blogger with multiple AI models"""
        
        # Primary content generator (Claude for creativity)
        self.content_llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.8,
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Critique agent (GPT-4 for analytical thinking)
        self.critique_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.3,
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Deep reasoning agent for content strategy
        self.deep_agent = create_deep_agent(
            model="claude-3-opus-20240229",
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
            max_depth=3,
            reflection_enabled=True
        )
        
        self.graph = self._build_workflow()
        self.max_revisions = 3
        
    def _build_workflow(self):
        """Build the enhanced LangGraph workflow"""
        graph = StateGraph(EnhancedBlogState)
        
        # Add nodes
        graph.add_node("analyze_context", self.analyze_context_node)
        graph.add_node("generate_content_brief", self.generate_content_brief_node)  
        graph.add_node("generate_post", self.generate_post_node)
        graph.add_node("critique_post", self.critique_post_node)
        graph.add_node("revise_post", self.revise_post_node)
        graph.add_node("finalize_post", self.finalize_post_node)
        graph.add_node("predict_performance", self.predict_performance_node)
        
        # Define workflow
        graph.add_edge(START, "analyze_context")
        graph.add_edge("analyze_context", "generate_content_brief")
        graph.add_edge("generate_content_brief", "generate_post")
        graph.add_edge("generate_post", "critique_post")
        
        # Conditional routing after critique
        graph.add_conditional_edges(
            "critique_post",
            self._decide_revision_needed,
            {
                "revise": "revise_post",
                "finalize": "finalize_post"
            }
        )
        
        graph.add_edge("revise_post", "critique_post")  # Re-critique after revision
        graph.add_edge("finalize_post", "predict_performance")
        graph.add_edge("predict_performance", END)
        
        return graph
    
    def _decide_revision_needed(self, state: EnhancedBlogState) -> Literal["revise", "finalize"]:
        """Decide if revision is needed based on critique"""
        current_critique = state.get("current_critique")
        revision_count = state.get("revision_count", 0)
        
        # Finalize if max revisions reached or critique is good enough
        if (revision_count >= self.max_revisions or 
            not current_critique.needs_revision or
            (current_critique.language_score >= 8 and 
             current_critique.content_score >= 8 and 
             current_critique.engagement_score >= 8)):
            return "finalize"
        
        return "revise"
    
    def analyze_context_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Analyze user context and content requirements using deep agent"""
        print("\n[Context Analyzer] Analyzing content context and user requirements...")
        
        context_prompt = f"""
        Analyze the following extracted information and determine the optimal LinkedIn content strategy:
        
        Source Type: {state['source_type']}
        Extracted Information: {state['extracted_info']}
        
        Provide a comprehensive context analysis including:
        1. Target audience identification
        2. Content theme and key messages
        3. Optimal content structure and tone
        4. Industry-specific considerations
        5. Engagement optimization opportunities
        
        Return as structured JSON.
        """
        
        # Use deep agent for sophisticated context analysis
        context_analysis = self.deep_agent.run(context_prompt)
        
        user_context = {
            "analysis": context_analysis,
            "source_type": state['source_type'],
            "complexity_level": self._assess_complexity(state['extracted_info'])
        }
        
        return {
            **state,
            "user_context": user_context,
            "status": "context_analyzed"
        }
    
    def generate_content_brief_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Generate content brief using deep reasoning"""
        print("\n[Brief Generator] Creating content strategy brief...")
        
        brief_prompt = f"""
        Create a detailed content brief for a high-performing LinkedIn post based on:
        
        Context Analysis: {state['user_context']['analysis']}
        Source Material: {state['extracted_info']}
        
        The brief should include:
        1. Hook strategy and opening line options
        2. Content structure and key points
        3. Call-to-action strategy
        4. Hashtag recommendations
        5. Engagement optimization tactics
        6. Tone and style guidelines
        
        Make this brief comprehensive for exceptional content creation.
        """
        
        brief_response = self.deep_agent.run(brief_prompt)
        
        return {
            **state,
            "content_brief": brief_response,
            "status": "brief_created"
        }
    
    def generate_post_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Generate LinkedIn post based on brief"""
        print("\n[Content Generator] Generating LinkedIn post...")
        
        generation_prompt = f"""
        You are an expert LinkedIn content creator. Generate a viral, engaging LinkedIn post following this brief:
        
        CONTENT BRIEF:
        {state['content_brief']}
        
        SOURCE MATERIAL:
        {state['extracted_info']}
        
        REQUIREMENTS:
        1. Hook: Compelling opening that stops scrolling
        2. Structure: Short paragraphs (1-2 sentences) with strategic line breaks
        3. Value: Clear, actionable insights and takeaways
        4. Engagement: Thought-provoking question at the end
        5. Length: 150-300 words for optimal engagement
        6. Hashtags: 3-5 strategic hashtags
        7. Emojis: 2-3 relevant emojis (not overdone)
        8. Tone: Professional yet conversational
        
        Generate the post ready for LinkedIn publishing.
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content strategist focused on viral, high-engagement posts."),
            HumanMessage(content=generation_prompt)
        ])
        
        generated_post = response.content
        
        return {
            **state,
            "current_post": generated_post,
            "generated_posts": state.get("generated_posts", []) + [generated_post],
            "status": "post_generated"
        }
    
    def critique_post_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Comprehensive critique of generated post"""
        print("\n[Critique Agent] Analyzing post quality and engagement potential...")
        
        current_post = state['current_post']
        
        critique_prompt = f"""
        You are an expert LinkedIn content critic. Analyze this post comprehensively:
        
        POST TO ANALYZE:
        {current_post}
        
        ORIGINAL BRIEF:
        {state['content_brief']}
        
        Provide detailed critique in these areas:
        
        1. LANGUAGE ANALYSIS (Score 1-10):
           - Grammar and syntax
           - Clarity and readability  
           - Professional tone
           - Flow and rhythm
        
        2. CONTENT ANALYSIS (Score 1-10):
           - Value proposition
           - Insight quality
           - Relevance to audience
           - Information accuracy
        
        3. ENGAGEMENT ANALYSIS (Score 1-10):
           - Hook effectiveness
           - Call-to-action strength
           - Hashtag strategy
           - Viral potential
        
        4. SPECIFIC FEEDBACK:
           - What works well
           - What needs improvement
           - Specific suggestions for enhancement
        
        5. REVISION RECOMMENDATION:
           - Does this need revision? (true/false)
           - Priority areas for improvement
           - Expected impact of changes
        
        Return response as structured JSON with all scores and detailed feedback.
        """
        
        critique_response = self.critique_llm.invoke([
            SystemMessage(content="You are a LinkedIn content expert providing detailed, constructive critique."),
            HumanMessage(content=critique_prompt)
        ])
        
        # Parse critique response (assuming JSON format)
        try:
            critique_data = json.loads(critique_response.content)
            
            critique_result = CritiqueResult(
                language_score=critique_data.get("language_score", 7),
                content_score=critique_data.get("content_score", 7),
                engagement_score=critique_data.get("engagement_score", 7),
                language_feedback=critique_data.get("language_feedback", ""),
                content_feedback=critique_data.get("content_feedback", ""),
                engagement_feedback=critique_data.get("engagement_feedback", ""),
                overall_recommendation=critique_data.get("overall_recommendation", ""),
                needs_revision=critique_data.get("needs_revision", False)
            )
        except:
            # Fallback if JSON parsing fails
            critique_result = CritiqueResult(
                language_score=7, content_score=7, engagement_score=7,
                language_feedback=critique_response.content[:200],
                content_feedback="Critique parsing error - using raw feedback",
                engagement_feedback="", overall_recommendation="Manual review needed",
                needs_revision=True
            )
        
        print(f"[Critique Results] Language: {critique_result.language_score}/10, Content: {critique_result.content_score}/10, Engagement: {critique_result.engagement_score}/10")
        
        return {
            **state,
            "current_critique": critique_result,
            "critique_results": state.get("critique_results", []) + [critique_result],
            "status": "post_critiqued"
        }
    
    def revise_post_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Revise post based on critique feedback"""
        print(f"\n[Revision Agent] Revising post (Iteration {state.get('revision_count', 0) + 1})...")
        
        current_post = state['current_post']
        critique = state['current_critique']
        
        revision_prompt = f"""
        Revise this LinkedIn post based on the detailed critique feedback:
        
        CURRENT POST:
        {current_post}
        
        CRITIQUE FEEDBACK:
        Language Issues: {critique.language_feedback}
        Content Issues: {critique.content_feedback}
        Engagement Issues: {critique.engagement_feedback}
        Overall Recommendation: {critique.overall_recommendation}
        
        SCORES TO IMPROVE:
        - Language Score: {critique.language_score}/10
        - Content Score: {critique.content_score}/10  
        - Engagement Score: {critique.engagement_score}/10
        
        Create an improved version that addresses all critique points while maintaining:
        - The core message and value
        - LinkedIn best practices
        - Viral engagement potential
        - Professional tone
        
        Generate the revised post ready for LinkedIn.
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="You are an expert content editor focused on creating high-performing LinkedIn posts."),
            HumanMessage(content=revision_prompt)
        ])
        
        revised_post = response.content
        
        return {
            **state,
            "current_post": revised_post,
            "generated_posts": state.get("generated_posts", []) + [revised_post],
            "revision_count": state.get("revision_count", 0) + 1,
            "status": "post_revised"
        }
    
    def finalize_post_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Finalize the post with additional optimizations"""
        print("\n[Finalizer] Finalizing optimized LinkedIn post...")
        
        final_post = state['current_post']
        
        # Add final polish
        polish_prompt = f"""
        Apply final polish to this LinkedIn post for maximum impact:
        
        {final_post}
        
        Add final touches:
        1. Optimize spacing for mobile readability
        2. Ensure perfect grammar and punctuation
        3. Enhance emotional impact while maintaining professionalism
        4. Verify optimal hashtag placement
        5. Strengthen the call-to-action
        
        Return the final, publication-ready post.
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="You are a LinkedIn content expert applying final optimizations."),
            HumanMessage(content=polish_prompt)
        ])
        
        return {
            **state,
            "final_post": response.content,
            "status": "post_finalized"
        }
    
    def predict_performance_node(self, state: EnhancedBlogState) -> EnhancedBlogState:
        """Predict post performance metrics"""
        print("\n[Performance Predictor] Analyzing engagement potential...")
        
        final_post = state['final_post']
        critique_results = state.get('critique_results', [])
        
        # Calculate average scores
        if critique_results:
            latest_critique = critique_results[-1]
            avg_language = latest_critique.language_score
            avg_content = latest_critique.content_score
            avg_engagement = latest_critique.engagement_score
        else:
            avg_language = avg_content = avg_engagement = 7
        
        # Performance prediction logic
        performance_prediction = {
            "engagement_likelihood": min(95, (avg_engagement * 10 + 5)),
            "viral_potential": min(90, ((avg_engagement + avg_content) * 5)),
            "professional_score": avg_language * 10,
            "content_quality": avg_content * 10,
            "predicted_reach": "Medium" if avg_engagement < 7 else "High" if avg_engagement < 9 else "Very High",
            "optimization_score": round((avg_language + avg_content + avg_engagement) / 3 * 10, 1),
            "recommendations": [
                "Post during peak engagement hours (8-10 AM or 5-7 PM)",
                "Engage actively with comments in first hour",
                "Consider cross-posting to other platforms",
                "Track performance for future optimization"
            ]
        }
        
        print(f"\n🎯 PERFORMANCE PREDICTION:")
        print(f"Engagement Likelihood: {performance_prediction['engagement_likelihood']}%")
        print(f"Viral Potential: {performance_prediction['viral_potential']}%")
        print(f"Optimization Score: {performance_prediction['optimization_score']}/100")
        print(f"Predicted Reach: {performance_prediction['predicted_reach']}")
        
        return {
            **state,
            "performance_prediction": performance_prediction,
            "status": "completed"
        }
    
    def _assess_complexity(self, content: str) -> str:
        """Assess content complexity level"""
        if len(content) > 5000:
            return "high"
        elif len(content) > 2000:
            return "medium"
        else:
            return "low"
    
    def compile(self):
        """Compile the graph"""
        checkpointer = MemorySaver()
        return self.graph.compile(checkpointer=checkpointer)
    
    def generate_enhanced_blog_post(self, extracted_info: str, source_type: str) -> Dict[str, Any]:
        """Main method to generate enhanced blog post with critique workflow"""
        app = self.compile()
        
        thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        initial_state = {
            "extracted_info": extracted_info,
            "source_type": source_type,
            "user_context": {},
            "content_brief": "",
            "generated_posts": [],
            "current_post": "",
            "critique_results": [],
            "current_critique": None,
            "revision_count": 0,
            "final_post": "",
            "performance_prediction": {},
            "status": "initialized"
        }
        
        print("🚀 Starting Enhanced LinkedIn Blog Generation Workflow...")
        print(f"📄 Source Type: {source_type}")
        print(f"📝 Content Length: {len(extracted_info)} characters")
        
        try:
            # Run the complete workflow
            result = app.invoke(initial_state, config=thread_config)
            
            # Get final state
            final_state = app.get_state(thread_config).values
            
            return {
                "final_post": final_state.get("final_post", ""),
                "performance_prediction": final_state.get("performance_prediction", {}),
                "critique_history": final_state.get("critique_results", []),
                "revision_count": final_state.get("revision_count", 0),
                "all_versions": final_state.get("generated_posts", []),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Enhanced workflow error: {e}")
            return {
                "final_post": "",
                "error": str(e),
                "status": "error"
            }