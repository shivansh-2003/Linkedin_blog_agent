import json
from typing import Optional, Tuple
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
from blog_generation.config import BlogPost, CritiqueResult, BlogQuality, BlogConfig
from blog_generation.prompt_templates import (
    CRITIQUE_SYSTEM_PROMPT,
    build_critique_prompt
)

class CritiqueAgent:
    """Content critique agent for analyzing blog quality and engagement potential using LangChain"""
    
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=BlogConfig.GROQ_API_KEY,
            model_name=BlogConfig.PRIMARY_MODEL,
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500
        )
        
    def critique_blog(self, blog_post: BlogPost, context: str = "") -> Tuple[Optional[CritiqueResult], str]:
        """Provide comprehensive critique of blog post"""
        print("🔍 Analyzing blog post quality and engagement potential...")
        
        prompt = build_critique_prompt(blog_post, context)
        
        try:
            messages = [
                SystemMessage(content=CRITIQUE_SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            critique_result = self._parse_critique_response(content)
            
            if critique_result:
                print(f"📊 Quality Score: {critique_result.quality_score}/10 ({critique_result.quality_level})")
                return critique_result, ""
            else:
                return None, "Failed to parse critique response"
                
        except Exception as e:
            return None, f"Critique failed: {str(e)}"
    
    
    def _parse_critique_response(self, content: str) -> Optional[CritiqueResult]:
        """Parse LLM response into CritiqueResult object"""
        try:
            # Clean up the response
            content = content.strip()
            # Remove all markdown code blocks
            import re
            content = re.sub(r'```(?:json)?\s*|\s*```', '', content).strip()
            
            # Parse JSON
            data = json.loads(content)
            
            # Create CritiqueResult with validation
            critique = CritiqueResult(**data)
            
            # Validate quality level matches score
            critique.quality_level = self._determine_quality_level(critique.quality_score)
            
            # Determine publish approval
            critique.approved_for_publish = (
                critique.quality_score >= BlogConfig.MIN_QUALITY_SCORE and
                critique.quality_level in [BlogQuality.EXCELLENT, BlogQuality.PUBLISH_READY]
            )
            
            return critique
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return None
        except Exception as e:
            print(f"Critique parsing error: {str(e)}")
            return None
    
    def _determine_quality_level(self, score: int) -> BlogQuality:
        """Determine quality level from numeric score"""
        if score >= 9:
            return BlogQuality.PUBLISH_READY
        elif score >= 7:
            return BlogQuality.EXCELLENT
        elif score >= 5:
            return BlogQuality.GOOD
        else:
            return BlogQuality.DRAFT
    