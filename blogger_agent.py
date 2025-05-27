# blogger_agent.py

from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.types import Command, interrupt
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.checkpoint.memory import MemorySaver
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import uuid
import os

class BlogState(TypedDict):
    """State definition for the blog generation workflow"""
    extracted_info: str
    source_type: str
    generated_post: Annotated[List[str], add_messages]
    human_feedback: Annotated[List[str], add_messages]
    iteration_count: int

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
        """Build the LangGraph workflow"""
        graph = StateGraph(BlogState)
        
        # Add nodes
        graph.add_node("blog_generator", self.blog_generator_node)
        graph.add_node("human_review", self.human_review_node)
        graph.add_node("finalize", self.finalize_node)
        
        # Define flow
        graph.add_edge(START, "blog_generator")
        graph.add_edge("blog_generator", "human_review")
        
        # Set finish point
        graph.set_finish_point("finalize")
        
        return graph
    
    def blog_generator_node(self, state: BlogState) -> BlogState:
        """Generate or refine LinkedIn blog post based on extracted information and feedback"""
        print("\n[Blog Generator] Creating LinkedIn post...")
        
        extracted_info = state["extracted_info"]
        source_type = state["source_type"]
        feedback = state.get("human_feedback", [])
        iteration = state.get("iteration_count", 0)
        
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
            previous_post = state["generated_post"][-1].content if state["generated_post"] else ""
            
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
            "generated_post": [AIMessage(content=generated_post)],
            "human_feedback": feedback,
            "iteration_count": iteration + 1
        }
    
    def human_review_node(self, state: BlogState) -> Command:
        """Human review and feedback node"""
        print("\n[Human Review] Awaiting feedback...")
        
        generated_post = state["generated_post"][-1].content if state["generated_post"] else ""
        iteration = state.get("iteration_count", 0)
        
        # Show current post and get feedback
        user_feedback = interrupt({
            "current_post": generated_post,
            "iteration": iteration,
            "message": "Review the post above. Provide feedback or type 'done' to finalize, 'regenerate' for a fresh version"
        })
        
        print(f"[Human Review] Received feedback: {user_feedback}")
        
        # Handle different user inputs
        if user_feedback.lower() == "done":
            return Command(
                update={"human_feedback": state["human_feedback"] + ["Approved"]},
                goto="finalize"
            )
        elif user_feedback.lower() == "regenerate":
            return Command(
                update={
                    "human_feedback": state["human_feedback"] + ["Please regenerate with a different approach"],
                    "iteration_count": 0  # Reset iteration for fresh start
                },
                goto="blog_generator"
            )
        else:
            # Continue refining with feedback
            return Command(
                update={"human_feedback": state["human_feedback"] + [user_feedback]},
                goto="blog_generator"
            )
    
    def finalize_node(self, state: BlogState) -> BlogState:
        """Finalize the blog post with analytics tips"""
        print("\n[Finalize] Process completed!")
        
        final_post = state["generated_post"][-1].content if state["generated_post"] else ""
        
        # Add posting tips
        tips = """
📊 LinkedIn Posting Best Practices:
• Best times: Tuesday-Thursday, 8-10 AM or 5-6 PM (your timezone)
• Engage with comments in the first hour
• Reply to every comment to boost visibility
• Consider reposting successful content after 3-4 months
• Track performance: Views, reactions, comments, shares
"""
        
        print(f"\nFINAL LINKEDIN POST:\n{'='*50}\n{final_post}\n{'='*50}")
        print(f"\n{tips}")
        
        return {
            "generated_post": state["generated_post"],
            "human_feedback": state["human_feedback"] + ["Finalized with tips"]
        }
    
    def compile(self):
        """Compile the graph with memory"""
        checkpointer = MemorySaver()
        return self.graph.compile(checkpointer=checkpointer)
    
    def generate_blog_post(self, extracted_info: str, source_type: str) -> str:
        """Main method to generate a blog post with human-in-the-loop"""
        app = self.compile()
        
        thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
        
        initial_state = {
            "extracted_info": extracted_info,
            "source_type": source_type,
            "generated_post": [],
            "human_feedback": [],
            "iteration_count": 0
        }
        
        # Run the workflow
        try:
            for chunk in app.stream(initial_state, config=thread_config):
                for node_id, value in chunk.items():
                    if node_id == "__interrupt__":
                        # Handle interrupt - get current state
                        current_state = app.get_state(thread_config)
                        current_values = current_state.values
                        
                        # Display current post
                        if current_values.get("generated_post"):
                            current_post = current_values["generated_post"][-1].content
                            iteration = current_values.get("iteration_count", 1)
                            
                            print(f"\n{'='*50}\nCURRENT POST (Iteration {iteration}):\n{'='*50}")
                            print(current_post)
                            print(f"{'='*50}\n")
                        
                        # Get user feedback
                        user_feedback = input("\n🔄 Provide feedback (or 'done' to finalize, 'regenerate' for fresh start): ")
                        
                        # Resume with feedback
                        try:
                            app.invoke(Command(resume=user_feedback), config=thread_config)
                        except Exception as e:
                            print(f"Resume error: {e}")
                            # Fallback: update state and continue
                            app.update_state(thread_config, {"human_feedback": current_values.get("human_feedback", []) + [user_feedback]})
                        
                        if user_feedback.lower() in ["done", "regenerate"]:
                            break
        except Exception as e:
            print(f"Workflow error: {e}")
            # Fallback to simple generation
            return self._fallback_generation(extracted_info, source_type)
        
        # Return the final post
        try:
            final_state = app.get_state(thread_config).values
            return final_state["generated_post"][-1].content if final_state["generated_post"] else ""
        except:
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