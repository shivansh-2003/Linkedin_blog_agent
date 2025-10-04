import json
from typing import Optional, Tuple
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from blog_generation.config import BlogPost, BlogGenerationState, BlogConfig
from blog_generation.prompt_templates import (
    BLOG_GENERATOR_SYSTEM_PROMPT,
    build_blog_generation_prompt
)

class BlogGeneratorAgent:
    """Content generator agent using LangChain and Groq models"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=BlogConfig.GROQ_API_KEY,
            model_name=BlogConfig.PRIMARY_MODEL,
            temperature=BlogConfig.TEMPERATURE,
            max_tokens=BlogConfig.MAX_TOKENS
        )
        
    def generate_blog(self, state: BlogGenerationState) -> Tuple[Optional[BlogPost], str]:
        """Generate a LinkedIn blog post from source content"""
        print(f"🤖 Generating blog content (iteration {state.iteration_count + 1})...")
        
        # Build generation prompt
        prompt = build_blog_generation_prompt(
            source_content=state.source_content,
            insights=state.content_insights,
            user_requirements=state.user_requirements,
            iteration_count=state.iteration_count,
            previous_feedback=self._get_previous_feedback(state)
        )
        
        # Generate blog post using LangChain
        try:
            messages = [
                SystemMessage(content=BLOG_GENERATOR_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            blog_post = self._parse_blog_response(content)
            
            if blog_post:
                print(f"✅ Successfully generated blog")
                return blog_post, ""
            else:
                return None, "Failed to parse blog response"
                
        except Exception as e:
            return None, f"Generation failed: {str(e)}"
    
    
    def _parse_blog_response(self, content: str) -> Optional[BlogPost]:
        """Parse LLM response into BlogPost object"""
        try:
            # Clean up the response - remove all markdown code blocks
            import re
            content = content.strip()
            # Remove all markdown code blocks (```json, ```, etc.)
            content = re.sub(r'```(?:json)?\s*|\s*```', '', content).strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Create BlogPost object with validation
            blog_post = BlogPost(**data)
            
            # Additional validation
            if not blog_post.title or not blog_post.content:
                return None
                
            # Ensure hashtags have # prefix
            blog_post.hashtags = [
                tag if tag.startswith('#') else f"#{tag.lstrip('#')}" 
                for tag in blog_post.hashtags
            ]
            
            return blog_post
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Blog parsing error: {str(e)}")
            return None
    
    def _get_previous_feedback(self, state: BlogGenerationState) -> str:
        """Extract previous feedback for iteration context"""
        feedback_parts = []
        
        if state.latest_critique:
            critique = state.latest_critique
            feedback_parts.append(f"Previous quality score: {critique.quality_score}/10")
            
            if critique.weaknesses:
                feedback_parts.append("Key weaknesses: " + "; ".join(critique.weaknesses[:3]))
                
            if critique.specific_improvements:
                feedback_parts.append("Required improvements: " + "; ".join(critique.specific_improvements[:3]))
        
        if state.human_feedback:
            feedback_parts.append(f"Human feedback: {state.human_feedback}")
        
        return " | ".join(feedback_parts)