# blogger_agent.py
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command, interrupt
from typing import TypedDict, Annotated, List, Dict, Any, Literal
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import uuid
import os

class BlogState(TypedDict):
    """State definition for the blog generation workflow"""
    extracted_info: str
    source_type: str
    generated_post: str
    human_feedback: List[str]
    iteration_count: int
    user_decision: str  # "continue", "done", "regenerate"

class LinkedInBloggerAgent:
    def __init__(self, anthropic_api_key: str = None):
        """Initialize the LinkedIn Blogger Agent"""
        self.llm = ChatAnthropic(
            model="claude-3-opus-20240229",
            temperature=0.7,
            api_key=anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        )
        self.graph = self._build_graph()
        
    def _build_graph(self):
        """Build the LangGraph workflow with proper conditional routing"""
        graph = StateGraph(BlogState)
        
        # Add nodes
        graph.add_node("blog_generator", self.blog_generator_node)
        graph.add_node("human_review", self.human_review_node)
        graph.add_node("finalize", self.finalize_node)
        
        # Define the initial flow
        graph.add_edge(START, "blog_generator")
        graph.add_edge("blog_generator", "human_review")
        
        # Add conditional edges from human_review based on user decision
        graph.add_conditional_edges(
            "human_review",
            self.decide_next_step,
            {
                "continue": "blog_generator",  # Continue refining
                "regenerate": "blog_generator",  # Fresh start
                "done": "finalize"  # Finalize the post
            }
        )
        
        # Finalize leads to END
        graph.add_edge("finalize", END)
        
        return graph
    
    def decide_next_step(self, state: BlogState) -> Literal["continue", "regenerate", "done"]:
        """Conditional routing function to decide the next step based on user feedback"""
        user_decision = state.get("user_decision", "continue")
        print(f"[Router] User decision: {user_decision}")
        return user_decision
    
    def blog_generator_node(self, state: BlogState) -> BlogState:
        """Generate or refine LinkedIn blog post based on extracted information and feedback"""
        print("\n[Blog Generator] Creating LinkedIn post...")
        
        extracted_info = state["extracted_info"]
        source_type = state["source_type"]
        feedback = state.get("human_feedback", [])
        iteration = state.get("iteration_count", 0)
        user_decision = state.get("user_decision", "")
        
        # Reset iteration count if regenerating
        if user_decision == "regenerate":
            iteration = 0
        
        # Construct prompt based on iteration
        if iteration == 0:
            prompt = f"""
You are an expert LinkedIn content creator. Create a viral, engaging LinkedIn blog post based on the following extracted information.

Source Type: {source_type}
Extracted Information:
{extracted_info}

Requirements for the LinkedIn post:
1. **Hook**: Start with a compelling hook that stops scrolling (question, bold statement, or intriguing fact)
2. **Structure**: Use short paragraphs (1-2 sentences max) with line breaks for readability
3. **Value**: Provide actionable insights and practical takeaways
4. **Engagement**: Include a thought-provoking question at the end
5. **Hashtags**: Add 3-5 relevant hashtags at the bottom
6. **Emojis**: Use 2-3 relevant emojis strategically (not overdone)
7. **Length**: Aim for 150-300 words for optimal engagement
8. **Tone**: Professional yet conversational, avoid jargon unless necessary

Format the post to be copy-paste ready for LinkedIn.
"""
        else:
            # Refining based on feedback
            latest_feedback = feedback[-1] if feedback else "No specific feedback"
            previous_post = state.get("generated_post", "")
            
            prompt = f"""
Refine the LinkedIn blog post based on the human feedback.

Previous Post:
{previous_post}

Human Feedback:
{latest_feedback}

Original Information:
{extracted_info}

Please incorporate the feedback while maintaining:
- Viral potential and engagement
- Professional tone
- Clear value proposition
- Proper LinkedIn formatting

Generate the improved version of the post.
"""
        
        # Generate response
        response = self.llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content strategist who creates viral, engaging posts."),
            HumanMessage(content=prompt)
        ])
        
        generated_post = response.content
        print(f"\n[Blog Generator] Generated post:\n{generated_post}\n")
        
        return {
            **state,  # Preserve all existing state
            "generated_post": generated_post,
            "iteration_count": iteration + 1,
            "user_decision": ""  # Reset user decision
        }
    
    def human_review_node(self, state: BlogState) -> BlogState:
        """Human review and feedback node - this will be interrupted"""
        print("\n[Human Review] Post ready for review...")
        
        generated_post = state.get("generated_post", "")
        iteration = state.get("iteration_count", 0)
        
        print(f"\n{'='*60}")
        print(f"CURRENT POST (Iteration {iteration}):")
        print(f"{'='*60}")
        print(generated_post)
        print(f"{'='*60}\n")
        
        print("📝 Your Options:")
        print("🔄 Type specific feedback to refine the post")
        print("✅ Type any of these to FINALIZE: done, approved, satisfied, good, perfect, exit, end, finish, ready, publish")
        print("🔄 Type 'regenerate' to start fresh with a completely different approach")
        print("⏹️  Press Ctrl+C to stop anytime")
        
        # This node will be interrupted before execution
        # The user input will be handled in the main execution loop
        return state
    
    def finalize_node(self, state: BlogState) -> BlogState:
        """Finalize the blog post with analytics tips"""
        print("\n[Finalize] Process completed!")
        
        final_post = state.get("generated_post", "")
        
        # Add posting tips
        tips = """
📊 LinkedIn Posting Best Practices:
• Best times: Tuesday-Thursday, 8-10 AM or 5-6 PM (your timezone)
• Engage with comments in the first hour
• Reply to every comment to boost visibility
• Consider reposting successful content after 3-4 months
• Track performance: Views, reactions, comments, shares
"""
        
        print(f"\n🎉 FINAL LINKEDIN POST:")
        print(f"{'='*60}")
        print(final_post)
        print(f"{'='*60}")
        print(f"\n{tips}")
        
        return {
            **state,
            "human_feedback": state.get("human_feedback", []) + ["Finalized with posting tips"]
        }
    
    def compile(self):
        """Compile the graph with memory and interrupt configuration"""
        checkpointer = MemorySaver()
        return self.graph.compile(
            checkpointer=checkpointer,
            interrupt_before=["human_review"]  # Interrupt before human review
        )
    
    def generate_blog_post(self, extracted_info: str, source_type: str) -> str:
        """Main method to generate a blog post with human-in-the-loop"""
        app = self.compile()
        
        thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        initial_state = {
            "extracted_info": extracted_info,
            "source_type": source_type,
            "generated_post": "",
            "human_feedback": [],
            "iteration_count": 0,
            "user_decision": ""
        }
        
        # Define termination keywords
        termination_keywords = {
            'done', 'approved', 'exit', 'end', 'satisfied', 'good', 'perfect', 
            'final', 'finish', 'complete', 'stop', 'ok', 'yes', 'accept', 
            'finalize', 'ready', 'publish', 'post'
        }
        
        print("🚀 Starting LinkedIn blog post generation workflow...")
        print(f"📄 Source Type: {source_type}")
        print(f"📝 Extracted Info: {extracted_info[:100]}{'...' if len(extracted_info) > 100 else ''}")
        print(f"\n💡 Tip: You can stop anytime by typing: {', '.join(list(termination_keywords)[:8])}...\n")
        
        try:
            # Start the workflow
            result = app.invoke(initial_state, config=thread_config)
            
            # Main interaction loop
            while True:
                # Get current state
                current_state = app.get_state(thread_config)
                
                # Check if workflow is complete
                if not current_state.next:
                    break
                
                # If we're at an interrupt (human_review), get user input
                if "human_review" in current_state.next:
                    # The human_review_node has already displayed the post
                    user_feedback = input("\n🔄 Your input: ").strip()
                    
                    # Check if user wants to terminate with any keyword
                    if user_feedback.lower() in termination_keywords:
                        print(f"✅ User satisfaction detected with '{user_feedback}' - finalizing post...")
                        user_decision = "done"
                        feedback_list = current_state.values.get("human_feedback", []) + [f"User approved with: {user_feedback}"]
                    elif user_feedback.lower() == "regenerate":
                        user_decision = "regenerate"
                        feedback_list = current_state.values.get("human_feedback", []) + ["Regenerate with different approach"]
                    else:
                        user_decision = "continue"
                        feedback_list = current_state.values.get("human_feedback", []) + [user_feedback]
                    
                    # Update state with user decision
                    app.update_state(thread_config, {
                        "human_feedback": feedback_list,
                        "user_decision": user_decision
                    })
                    
                    # Continue execution
                    result = app.invoke(None, config=thread_config)
                else:
                    # Continue with other nodes
                    result = app.invoke(None, config=thread_config)
            
            # Return the final post
            final_state = app.get_state(thread_config).values
            return final_state.get("generated_post", "")
            
        except KeyboardInterrupt:
            print("\n⏹️  Workflow interrupted by user (Ctrl+C)")
            # Return current post if available
            try:
                current_state = app.get_state(thread_config).values
                return current_state.get("generated_post", "")
            except:
                return ""
        except Exception as e:
            print(f"❌ Workflow error: {e}")
            print("🔄 Falling back to simple generation...")
            return self._fallback_generation(extracted_info, source_type)
    
    def _fallback_generation(self, extracted_info: str, source_type: str) -> str:
        """Fallback method for simple post generation"""
        print("\n[Fallback] Using simple generation...")
        
        prompt = f"""
You are an expert LinkedIn content creator. Create a viral, engaging LinkedIn blog post based on the following extracted information.

Source Type: {source_type}
Extracted Information:
{extracted_info}

Requirements for the LinkedIn post:
1. **Hook**: Start with a compelling hook that stops scrolling (question, bold statement, or intriguing fact)
2. **Structure**: Use short paragraphs (1-2 sentences max) with line breaks for readability
3. **Value**: Provide actionable insights and practical takeaways
4. **Engagement**: Include a thought-provoking question at the end
5. **Hashtags**: Add 3-5 relevant hashtags at the bottom
6. **Emojis**: Use 2-3 relevant emojis strategically (not overdone)
7. **Length**: Aim for 150-300 words for optimal engagement
8. **Tone**: Professional yet conversational, avoid jargon unless necessary

Format the post to be copy-paste ready for LinkedIn.
"""
        
        response = self.llm.invoke([
            SystemMessage(content="You are an expert LinkedIn content strategist who creates viral, engaging posts."),
            HumanMessage(content=prompt)
        ])
        
        return response.content