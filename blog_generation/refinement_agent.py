import json
from typing import Optional, Tuple, List
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from blog_generation.config import BlogPost, CritiqueResult, BlogConfig
from blog_generation.prompt_templates import (
    REFINER_SYSTEM_PROMPT,
    build_refinement_prompt
)

class RefinementAgent:
    """Content refinement agent for iterative improvement based on critique using LangChain"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=BlogConfig.GROQ_API_KEY,
            model_name=BlogConfig.PRIMARY_MODEL,
            temperature=0.5,  # Moderate temperature for creative refinement
            max_tokens=BlogConfig.MAX_TOKENS
        )
        
    def refine_blog(
        self, 
        original_post: BlogPost, 
        critique: CritiqueResult,
        focus_areas: List[str] = None,
        human_feedback: str = ""
    ) -> Tuple[Optional[BlogPost], str]:
        """Refine blog post based on critique feedback"""
        print(f"🔧 Refining blog (Quality: {critique.quality_score}/10 → Target: {critique.quality_score + 2}/10)")
        
        prompt = build_refinement_prompt(
            original_post=original_post,
            critique=critique,
            focus_areas=focus_areas,
            human_feedback=human_feedback
        )
        
        try:
            messages = [
                SystemMessage(content=REFINER_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            refined_post = self._parse_refinement_response(content)
            
            if refined_post:
                print(f"✅ Successfully refined blog")
                return refined_post, ""
            else:
                return None, "Failed to parse refinement response"
                
        except Exception as e:
            return None, f"Refinement failed: {str(e)}"
    
    
    def _parse_refinement_response(self, content: str) -> Optional[BlogPost]:
        """Parse LLM response into refined BlogPost object"""
        try:
            # Clean up the response
            content = content.strip()
            # Remove all markdown code blocks
            import re
            content = re.sub(r'```(?:json)?\s*|\s*```', '', content).strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Create BlogPost with validation
            refined_post = BlogPost(**data)
            
            # Ensure hashtags have # prefix
            refined_post.hashtags = [
                tag if tag.startswith('#') else f"#{tag.lstrip('#')}" 
                for tag in refined_post.hashtags
            ]
            
            return refined_post
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Refinement parsing error: {str(e)}")
            return None
    