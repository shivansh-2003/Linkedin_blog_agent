# research_feature_agent.py

from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from deepagents import create_deep_agent
from blogger_agent import EnhancedLinkedInBloggerAgent, CritiqueResult
import uuid
import os
import json
import requests
from datetime import datetime, timedelta
import asyncio
from dataclasses import dataclass

@dataclass
class ResearchResult:
    topic: str
    key_insights: List[str]
    statistics: List[Dict[str, Any]]
    trends: List[str]
    expert_quotes: List[str]
    sources: List[str]
    credibility_score: float
    research_depth: str

class ResearchBlogState(TypedDict):
    """State for research-driven blog generation"""
    # Input
    user_prompt: str
    research_scope: str  # "basic", "comprehensive", "expert"
    target_audience: str
    
    # Research pipeline
    research_plan: str
    research_queries: List[str]
    research_results: List[ResearchResult]
    synthesized_research: str
    
    # Content generation
    content_strategy: str
    generated_content: str
    
    # Critique and refinement
    critique_results: List[CritiqueResult]
    current_critique: CritiqueResult
    revision_count: int
    
    # Final output
    final_post: str
    research_citations: List[str]
    confidence_score: float
    status: str

class ResearchFeatureAgent:
    def __init__(self, 
                 anthropic_api_key: str = None,
                 openai_api_key: str = None):
        """Initialize research agent with multiple AI models and tools"""
        
        # Research agent (Claude for deep analysis)
        self.research_llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.4,
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        
        # Content generator (GPT-4 for structured output)
        self.content_llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.7,
            api_key=openai_api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Deep reasoning agent for research planning
        self.deep_agent = create_deep_agent(
            model="claude-3-opus-20240229",
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY"),
            max_depth=4,
            reflection_enabled=True,
            tools_enabled=True
        )
        
        # Initialize the critique system from enhanced blogger
        self.critique_agent = EnhancedLinkedInBloggerAgent(
            anthropic_api_key=anthropic_api_key,
            openai_api_key=openai_api_key
        )
        
        self.graph = self._build_research_workflow()
        self.max_research_iterations = 3
        
    def _build_research_workflow(self):
        """Build research-driven content generation workflow"""
        graph = StateGraph(ResearchBlogState)
        
        # Add nodes
        graph.add_node("analyze_prompt", self.analyze_prompt_node)
        graph.add_node("create_research_plan", self.create_research_plan_node)
        graph.add_node("execute_research", self.execute_research_node)
        graph.add_node("synthesize_findings", self.synthesize_findings_node)
        graph.add_node("create_content_strategy", self.create_content_strategy_node)
        graph.add_node("generate_content", self.generate_content_node)
        graph.add_node("critique_content", self.critique_content_node)
        graph.add_node("revise_content", self.revise_content_node)
        graph.add_node("finalize_research_post", self.finalize_research_post_node)
        
        # Define workflow
        graph.add_edge(START, "analyze_prompt")
        graph.add_edge("analyze_prompt", "create_research_plan")
        graph.add_edge("create_research_plan", "execute_research")
        graph.add_edge("execute_research", "synthesize_findings")
        graph.add_edge("synthesize_findings", "create_content_strategy")
        graph.add_edge("create_content_strategy", "generate_content")
        graph.add_edge("generate_content", "critique_content")
        
        # Conditional routing after critique
        graph.add_conditional_edges(
            "critique_content",
            self._decide_research_revision,
            {
                "revise": "revise_content",
                "finalize": "finalize_research_post"
            }
        )
        
        graph.add_edge("revise_content", "critique_content")
        graph.add_edge("finalize_research_post", END)
        
        return graph
    
    def _decide_research_revision(self, state: ResearchBlogState) -> Literal["revise", "finalize"]:
        """Decide if content revision is needed"""
        current_critique = state.get("current_critique")
        revision_count = state.get("revision_count", 0)
        
        if (revision_count >= 2 or 
            not current_critique.needs_revision or
            (current_critique.language_score >= 8 and 
             current_critique.content_score >= 8 and 
             current_critique.engagement_score >= 8)):
            return "finalize"
        
        return "revise"
    
    def analyze_prompt_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Analyze user prompt to understand research requirements"""
        print("\n[Prompt Analyzer] Analyzing research requirements...")
        
        prompt_analysis_query = f"""
        Analyze this user prompt for LinkedIn content creation and determine optimal research strategy:
        
        USER PROMPT: "{state['user_prompt']}"
        
        Provide detailed analysis:
        1. Topic identification and scope
        2. Required research depth (basic/comprehensive/expert)
        3. Target audience identification
        4. Key research areas needed
        5. Content angle opportunities
        6. Potential challenges or limitations
        7. Success metrics for the content
        
        Return structured analysis to guide deep research.
        """
        
        analysis_response = self.deep_agent.run(prompt_analysis_query)
        
        # Extract research scope and audience (simplified extraction)
        research_scope = "comprehensive"  # Default to comprehensive
        target_audience = "professionals"  # Default audience
        
        # Try to extract more specific info from analysis
        if "expert" in analysis_response.lower():
            research_scope = "expert"
        elif "basic" in analysis_response.lower():
            research_scope = "basic"
        
        print(f"[Analysis Complete] Research Scope: {research_scope}, Target: {target_audience}")
        
        return {
            **state,
            "research_scope": research_scope,
            "target_audience": target_audience,
            "status": "prompt_analyzed"
        }
    
    def create_research_plan_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Create comprehensive research plan"""
        print("\n[Research Planner] Creating research strategy...")
        
        planning_query = f"""
        Create a comprehensive research plan for this LinkedIn content topic:
        
        TOPIC: {state['user_prompt']}
        RESEARCH SCOPE: {state['research_scope']}
        TARGET AUDIENCE: {state['target_audience']}
        
        Design a research plan including:
        1. Primary research questions (5-7 questions)
        2. Secondary research areas
        3. Data and statistics needed
        4. Industry expert perspectives required
        5. Current trends to investigate
        6. Credible sources to prioritize
        7. Research methodology and approach
        8. Timeline and priority order
        
        Make this plan comprehensive enough to generate authoritative, engaging LinkedIn content.
        """
        
        research_plan = self.deep_agent.run(planning_query)
        
        # Extract specific research queries
        query_extraction_prompt = f"""
        Based on this research plan, create 7-10 specific search queries for deep research:
        
        RESEARCH PLAN:
        {research_plan}
        
        Generate specific, focused search queries that will yield high-quality information.
        Return as a Python list format.
        """
        
        queries_response = self.research_llm.invoke([
            SystemMessage(content="Extract specific research queries from the plan."),
            HumanMessage(content=query_extraction_prompt)
        ])
        
        # Parse queries (simplified - in production, use proper parsing)
        research_queries = [
            f"latest trends in {state['user_prompt']}",
            f"statistics and data about {state['user_prompt']}",
            f"expert opinions on {state['user_prompt']}",
            f"case studies related to {state['user_prompt']}",
            f"future predictions for {state['user_prompt']}"
        ]
        
        return {
            **state,
            "research_plan": research_plan,
            "research_queries": research_queries,
            "status": "research_planned"
        }
    
    def execute_research_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Execute deep research using multiple sources"""
        print(f"\n[Research Executor] Conducting deep research with {len(state['research_queries'])} queries...")
        
        research_results = []
        
        for i, query in enumerate(state['research_queries'][:5], 1):  # Limit to 5 for demo
            print(f"  Researching query {i}: {query[:50]}...")
            
            # Simulate research execution (in production, integrate with real APIs)
            research_prompt = f"""
            Conduct comprehensive research on this query: "{query}"
            
            Research Requirements:
            - Find latest information and trends
            - Identify key statistics and data points
            - Gather expert insights and quotes
            - Assess information credibility
            - Note important sources and references
            
            Topic Context: {state['user_prompt']}
            Target Audience: {state['target_audience']}
            
            Provide detailed research findings with sources and credibility assessment.
            """
            
            # Use deep agent for thorough research
            research_response = self.deep_agent.run(research_prompt)
            
            # Create research result object
            research_result = ResearchResult(
                topic=query,
                key_insights=self._extract_insights(research_response),
                statistics=self._extract_statistics(research_response),
                trends=self._extract_trends(research_response),
                expert_quotes=self._extract_quotes(research_response),
                sources=self._extract_sources(research_response),
                credibility_score=8.5,  # Simulated credibility score
                research_depth="comprehensive"
            )
            
            research_results.append(research_result)
        
        print(f"[Research Complete] Gathered {len(research_results)} comprehensive research results")
        
        return {
            **state,
            "research_results": research_results,
            "status": "research_executed"
        }
    
    def synthesize_findings_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Synthesize all research findings into coherent insights"""
        print("\n[Research Synthesizer] Synthesizing findings into key insights...")
        
        # Combine all research results
        all_findings = []
        for result in state['research_results']:
            findings_text = f"""
            Topic: {result.topic}
            Key Insights: {'; '.join(result.key_insights)}
            Trends: {'; '.join(result.trends)}
            Statistics: {result.statistics}
            Expert Quotes: {'; '.join(result.expert_quotes)}
            Sources: {'; '.join(result.sources)}
            """
            all_findings.append(findings_text)
        
        synthesis_prompt = f"""
        Synthesize these research findings into a coherent, comprehensive summary for LinkedIn content creation:
        
        ORIGINAL TOPIC: {state['user_prompt']}
        TARGET AUDIENCE: {state['target_audience']}
        
        RESEARCH FINDINGS:
        {chr(10).join(all_findings)}
        
        Create a synthesis that includes:
        1. Core insights and key takeaways
        2. Most compelling statistics and data points
        3. Strongest expert perspectives
        4. Current trends and future implications
        5. Unique angles and perspectives
        6. Potential controversial or debate-worthy points
        7. Actionable advice and recommendations
        8. Story elements and examples
        
        Organize this synthesis for maximum LinkedIn engagement potential.
        """
        
        synthesis_response = self.deep_agent.run(synthesis_prompt)
        
        return {
            **state,
            "synthesized_research": synthesis_response,
            "status": "research_synthesized"
        }
    
    def create_content_strategy_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Create content strategy based on research synthesis"""
        print("\n[Content Strategist] Developing content strategy...")
        
        strategy_prompt = f"""
        Based on this comprehensive research synthesis, create a winning LinkedIn content strategy:
        
        RESEARCH SYNTHESIS:
        {state['synthesized_research']}
        
        ORIGINAL PROMPT: {state['user_prompt']}
        TARGET AUDIENCE: {state['target_audience']}
        
        Develop a content strategy including:
        1. Hook options (3 different approaches)
        2. Content structure and flow
        3. Key messages and value propositions
        4. Engagement tactics and CTAs
        5. Hashtag strategy
        6. Tone and style recommendations
        7. Visual content suggestions
        8. Timing and posting recommendations
        
        Make this strategy data-driven and optimized for maximum engagement.
        """
        
        strategy_response = self.deep_agent.run(strategy_prompt)
        
        return {
            **state,
            "content_strategy": strategy_response,
            "status": "strategy_created"
        }
    
    def generate_content_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Generate LinkedIn content based on research and strategy"""
        print("\n[Content Generator] Generating research-based LinkedIn post...")
        
        content_prompt = f"""
        Generate a high-impact LinkedIn post based on this research-driven strategy:
        
        CONTENT STRATEGY:
        {state['content_strategy']}
        
        RESEARCH FOUNDATION:
        {state['synthesized_research']}
        
        REQUIREMENTS:
        1. Hook: Compelling, research-backed opening
        2. Value: Rich insights from research findings
        3. Data: Include 1-2 key statistics or findings
        4. Structure: LinkedIn-optimized formatting
        5. Engagement: Strong CTA based on research
        6. Authority: Position as thought leadership
        7. Length: 200-350 words for comprehensive content
        8. Hashtags: Research-informed hashtag selection
        
        Generate a post that demonstrates deep expertise and provides genuine value.
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content creator specializing in research-driven thought leadership posts."),
            HumanMessage(content=content_prompt)
        ])
        
        generated_content = response.content
        
        print(f"[Content Generated] {len(generated_content)} character research-based post created")
        
        return {
            **state,
            "generated_content": generated_content,
            "status": "content_generated"
        }
    
    def critique_content_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Critique generated content using the enhanced critique system"""
        print("\n[Critique Agent] Analyzing content quality and research integration...")
        
        # Use the critique system from enhanced blogger agent
        # Create a temporary state for the critique system
        critique_state = {
            "current_post": state['generated_content'],
            "content_brief": state['content_strategy'],
            "extracted_info": state['synthesized_research']
        }
        
        # Run critique analysis
        critique_result = self.critique_agent.critique_post_node(critique_state)
        current_critique = critique_result.get('current_critique')
        
        # Additional research-specific critique
        research_critique_prompt = f"""
        Evaluate this research-based LinkedIn post for:
        
        POST:
        {state['generated_content']}
        
        RESEARCH FOUNDATION:
        {state['synthesized_research']}
        
        Research Integration Assessment:
        1. How well does it leverage the research findings?
        2. Are the insights presented authoritatively?
        3. Is the data/statistics used effectively?
        4. Does it demonstrate thought leadership?
        5. Is the research credibly presented?
        
        Provide specific feedback on research integration and authority building.
        """
        
        research_critique = self.research_llm.invoke([
            SystemMessage(content="Evaluate research integration and thought leadership positioning."),
            HumanMessage(content=research_critique_prompt)
        ])
        
        # Enhance critique with research-specific feedback
        if current_critique:
            current_critique.content_feedback += f"\n\nResearch Integration: {research_critique.content}"
        
        return {
            **state,
            "current_critique": current_critique,
            "critique_results": state.get("critique_results", []) + [current_critique],
            "status": "content_critiqued"
        }
    
    def revise_content_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Revise content based on critique"""
        print(f"\n[Content Reviser] Revising based on critique (Revision {state.get('revision_count', 0) + 1})...")
        
        revision_prompt = f"""
        Revise this research-based LinkedIn post based on critique feedback:
        
        CURRENT POST:
        {state['generated_content']}
        
        CRITIQUE FEEDBACK:
        {state['current_critique'].content_feedback}
        {state['current_critique'].language_feedback}
        {state['current_critique'].engagement_feedback}
        
        RESEARCH FOUNDATION TO LEVERAGE:
        {state['synthesized_research']}
        
        Create an improved version that:
        - Addresses all critique points
        - Better integrates research findings
        - Strengthens thought leadership positioning
        - Maintains research credibility
        - Optimizes for LinkedIn engagement
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="You are an expert at revising research-based LinkedIn content for maximum impact."),
            HumanMessage(content=revision_prompt)
        ])
        
        return {
            **state,
            "generated_content": response.content,
            "revision_count": state.get("revision_count", 0) + 1,
            "status": "content_revised"
        }
    
    def finalize_research_post_node(self, state: ResearchBlogState) -> ResearchBlogState:
        """Finalize research-driven post with citations and confidence scoring"""
        print("\n[Finalizer] Finalizing research-driven LinkedIn post...")
        
        # Extract research citations
        citations = []
        for result in state['research_results']:
            citations.extend(result.sources[:2])  # Top 2 sources per research result
        
        # Calculate confidence score based on research quality
        confidence_factors = {
            "research_depth": len(state['research_results']) * 10,
            "critique_quality": (state['current_critique'].content_score + 
                               state['current_critique'].language_score + 
                               state['current_critique'].engagement_score) / 3 * 10,
            "synthesis_quality": 85,  # Simulated synthesis quality score
            "revision_optimization": max(0, (3 - state.get('revision_count', 0)) * 10)
        }
        
        confidence_score = min(95, sum(confidence_factors.values()) / len(confidence_factors))
        
        # Final polish
        final_prompt = f"""
        Apply final optimization to this research-driven LinkedIn post:
        
        {state['generated_content']}
        
        Final enhancements:
        1. Perfect formatting for LinkedIn mobile
        2. Optimize research integration presentation
        3. Strengthen authority and credibility
        4. Enhance call-to-action
        5. Final grammar and style polish
        
        Create the final, publication-ready post.
        """
        
        response = self.content_llm.invoke([
            SystemMessage(content="Apply final polish to research-driven LinkedIn content."),
            HumanMessage(content=final_prompt)
        ])
        
        print(f"\n🎯 RESEARCH POST COMPLETE:")
        print(f"Confidence Score: {confidence_score:.1f}%")
        print(f"Research Depth: {len(state['research_results'])} comprehensive research areas")
        print(f"Citations Available: {len(citations)} sources")
        
        return {
            **state,
            "final_post": response.content,
            "research_citations": citations,
            "confidence_score": confidence_score,
            "status": "research_post_completed"
        }
    
    # Helper methods for research extraction
    def _extract_insights(self, research_text: str) -> List[str]:
        """Extract key insights from research text"""
        # Simplified extraction - in production, use NLP techniques
        insights = []
        lines = research_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['insight:', 'key finding:', 'important:', 'reveals:']):
                insights.append(line.strip())
        return insights[:3]  # Return top 3
    
    def _extract_statistics(self, research_text: str) -> List[Dict[str, Any]]:
        """Extract statistics from research text"""
        # Simplified extraction
        import re
        stats = []
        numbers = re.findall(r'\d+%|\d+\.\d+%|\$\d+|\d+\s*billion|\d+\s*million', research_text)
        for num in numbers[:3]:
            stats.append({"value": num, "context": "research finding"})
        return stats
    
    def _extract_trends(self, research_text: str) -> List[str]:
        """Extract trends from research text"""
        trends = []
        lines = research_text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['trend:', 'trending:', 'growth:', 'increasing:', 'emerging:']):
                trends.append(line.strip())
        return trends[:2]  # Return top 2
    
    def _extract_quotes(self, research_text: str) -> List[str]:
        """Extract expert quotes from research text"""
        import re
        quotes = re.findall(r'"([^"]*)"', research_text)
        return quotes[:2]  # Return top 2 quotes
    
    def _extract_sources(self, research_text: str) -> List[str]:
        """Extract sources from research text"""
        # Simplified source extraction
        sources = ["Industry Research Report", "Expert Analysis", "Market Study"]
        return sources[:2]
    
    def compile(self):
        """Compile the research workflow graph"""
        checkpointer = MemorySaver()
        return self.graph.compile(checkpointer=checkpointer)
    
    def generate_research_driven_post(self, user_prompt: str) -> Dict[str, Any]:
        """Main method to generate research-driven LinkedIn post"""
        app = self.compile()
        
        thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        initial_state = {
            "user_prompt": user_prompt,
            "research_scope": "",
            "target_audience": "",
            "research_plan": "",
            "research_queries": [],
            "research_results": [],
            "synthesized_research": "",
            "content_strategy": "",
            "generated_content": "",
            "critique_results": [],
            "current_critique": None,
            "revision_count": 0,
            "final_post": "",
            "research_citations": [],
            "confidence_score": 0.0,
            "status": "initialized"
        }
        
        print("🔬 Starting Research-Driven LinkedIn Content Generation...")
        print(f"📝 User Prompt: {user_prompt}")
        print(f"🎯 Research Mode: Deep Analysis + Content Generation")
        
        try:
            # Run the complete research workflow
            result = app.invoke(initial_state, config=thread_config)
            
            # Get final state
            final_state = app.get_state(thread_config).values
            
            return {
                "final_post": final_state.get("final_post", ""),
                "research_summary": final_state.get("synthesized_research", ""),
                "confidence_score": final_state.get("confidence_score", 0),
                "research_citations": final_state.get("research_citations", []),
                "research_depth": len(final_state.get("research_results", [])),
                "content_strategy": final_state.get("content_strategy", ""),
                "critique_history": final_state.get("critique_results", []),
                "revision_count": final_state.get("revision_count", 0),
                "status": "success"
            }
            
        except Exception as e:
            print(f"❌ Research workflow error: {e}")
            return {
                "final_post": "",
                "error": str(e),
                "status": "error"
            }