"""AI-powered content analysis using LLM and vision models"""

import os
import sys
from typing import Dict, Any, Optional, List
import asyncio

# Add parent directory to path for langsmith_config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from langsmith_config import trace_step

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage
import google.generativeai as genai

from .config import (
    ContentType, 
    ProcessingModel, 
    ExtractedContent, 
    AIInsights
)


class ContentAnalyzer:
    """Analyzes content using AI models"""
    
    def __init__(self):
        """Initialize AI clients"""
        # Initialize text analysis client
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        self.text_client = ChatGroq(
            api_key=groq_api_key,
            model_name=ProcessingModel.PRIMARY.value,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Initialize vision client for images
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.vision_client = genai.GenerativeModel(ProcessingModel.VISION.value)
        else:
            self.vision_client = None
    
    @trace_step("analyze_content", "llm")
    async def analyze(
        self, 
        content: ExtractedContent,
        content_type: ContentType
    ) -> AIInsights:
        """Main analysis dispatcher"""
        
        if content_type == ContentType.IMAGE:
            return await self._analyze_image(content)
        else:
            return await self._analyze_text(content, content_type)
    
    @trace_step("analyze_text", "llm")
    async def _analyze_text(
        self,
        content: ExtractedContent,
        content_type: ContentType
    ) -> AIInsights:
        """Analyze text-based content"""
        
        try:
            # Build context-specific prompts
            system_prompt = self._build_system_prompt(content_type)
            user_prompt = self._build_analysis_prompt(content, content_type)
            
            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            # Get AI response with fallback
            response = await self._get_response_with_fallback(messages)
            
            # Parse response into structured insights
            insights = self._parse_insights(response)
            
            return insights
            
        except Exception as e:
            print(f"Warning: AI analysis failed: {str(e)}")
            return self._create_fallback_insights(content)
    
    @trace_step("analyze_image", "llm")
    async def _analyze_image(self, content: ExtractedContent) -> AIInsights:
        """Analyze image content using vision AI"""
        
        if not self.vision_client:
            return AIInsights(
                main_topics=["Image Analysis"],
                key_insights=["Vision AI not configured"],
                professional_context="Visual content provided",
                linkedin_angles=["Share visual insights"]
            )
        
        try:
            # Get image data
            image_b64 = content.structured_data.get("image_base64")
            mime_type = content.structured_data.get("mime_type", "image/jpeg")
            
            if not image_b64:
                raise ValueError("No image data found")
            
            # Prepare vision prompt
            prompt = """Analyze this image for professional LinkedIn content:

1. What is shown in the image? (charts, diagrams, photos, etc.)
2. What text or data is visible?
3. What professional insights can be derived?
4. What audience would find this valuable?
5. What are 3 potential LinkedIn post angles?

Provide a structured analysis."""
            
            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_b64
            }
            
            # Get vision response
            response = await asyncio.to_thread(
                self.vision_client.generate_content,
                [prompt, image_part]
            )
            
            # Parse vision response
            insights = self._parse_vision_response(response.text)
            
            return insights
            
        except Exception as e:
            print(f"Warning: Image analysis failed: {str(e)}")
            return AIInsights(
                main_topics=["Visual Content"],
                key_insights=["Image analysis unavailable"],
                professional_context="Visual content provided",
                linkedin_angles=["Share visual insights with audience"]
            )
    
    @trace_step("llm_response_with_fallback", "llm")
    async def _get_response_with_fallback(
        self, 
        messages: List[Any]
    ) -> str:
        """Try primary model, fallback to alternatives if needed"""
        
        models = [
            ProcessingModel.PRIMARY.value,
            ProcessingModel.FAST.value,
            ProcessingModel.FALLBACK.value
        ]
        
        last_error = None
        
        for model_name in models:
            try:
                # Update model
                self.text_client.model_name = model_name
                
                # Get response
                response = await asyncio.to_thread(
                    self.text_client.invoke,
                    messages
                )
                
                return response.content
                
            except Exception as e:
                last_error = e
                print(f"Model {model_name} failed, trying next...")
                continue
        
        raise RuntimeError(f"All models failed. Last error: {str(last_error)}")
    
    def _build_system_prompt(self, content_type: ContentType) -> str:
        """Build system prompt based on content type"""
        
        base = """You are an expert content analyst specializing in transforming professional content into engaging LinkedIn posts. Your analysis should identify key insights, audience relevance, and content angles suitable for LinkedIn."""
        
        type_specific = {
            ContentType.PDF: "Focus on extracting main arguments, key findings, and actionable takeaways from documents.",
            ContentType.WORD: "Identify core messages, structure, and professional insights suitable for social sharing.",
            ContentType.POWERPOINT: "Extract key points from presentation slides, focusing on visual storytelling and main messages.",
            ContentType.CODE: "Analyze code for technical insights, best practices, architectural patterns, and learning opportunities for developers.",
            ContentType.TEXT: "Extract main ideas, professional insights, and shareable knowledge from the text.",
            ContentType.MARKDOWN: "Parse structured content, identify key sections, and extract shareable professional insights."
        }
        
        return f"{base}\n\n{type_specific.get(content_type, base)}"
    
    def _build_analysis_prompt(
        self,
        content: ExtractedContent,
        content_type: ContentType
    ) -> str:
        """Build analysis prompt with content"""
        
        # Truncate content if too long (keep first and last parts)
        max_length = 8000
        text = content.content
        
        if len(text) > max_length:
            half = max_length // 2
            text = f"{text[:half]}\n\n[... content truncated ...]\n\n{text[-half:]}"
        
        prompt = f"""Analyze the following {content_type.value} content and provide:

1. **Main Topics** (3-5 key topics/themes)
2. **Key Insights** (3-5 most important takeaways)
3. **Target Audience** (who would benefit from this)
4. **Professional Context** (why this matters professionally)
5. **LinkedIn Angles** (3-5 potential post angles)
6. **Technical Depth** (beginner/intermediate/advanced)
7. **Tone Suggestions** (how to present this content)

Content:
{text}

Metadata: {content.metadata}

Provide a structured response with clear sections."""
        
        return prompt
    
    @trace_step("parse_insights", "tool")
    def _parse_insights(self, response: str) -> AIInsights:
        """Parse AI response into structured insights"""
        
        # Simple parsing - extract sections
        lines = response.split('\n')
        
        insights = AIInsights()
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            lower = line.lower()
            if 'main topic' in lower or 'key topic' in lower:
                current_section = 'topics'
            elif 'key insight' in lower or 'takeaway' in lower:
                current_section = 'insights'
            elif 'target audience' in lower or 'audience' in lower:
                current_section = 'audience'
            elif 'professional context' in lower or 'context' in lower:
                current_section = 'context'
            elif 'linkedin angle' in lower or 'post angle' in lower:
                current_section = 'angles'
            elif 'technical depth' in lower or 'depth' in lower:
                current_section = 'depth'
            elif 'tone' in lower:
                current_section = 'tone'
            elif line.startswith(('-', '•', '*', '1.', '2.', '3.')):
                # It's a list item
                item = line.lstrip('-•*123456789. ').strip()
                if item:
                    if current_section == 'topics':
                        insights.main_topics.append(item)
                    elif current_section == 'insights':
                        insights.key_insights.append(item)
                    elif current_section == 'angles':
                        insights.linkedin_angles.append(item)
                    elif current_section == 'tone':
                        insights.tone_suggestions.append(item)
            else:
                # Regular text - might be audience or context
                if current_section == 'audience' and not insights.target_audience:
                    insights.target_audience = line
                elif current_section == 'context' and not insights.professional_context:
                    insights.professional_context = line
                elif current_section == 'depth' and not insights.technical_depth:
                    if any(word in lower for word in ['beginner', 'basic', 'intro']):
                        insights.technical_depth = "beginner"
                    elif any(word in lower for word in ['advanced', 'expert', 'deep']):
                        insights.technical_depth = "advanced"
                    else:
                        insights.technical_depth = "intermediate"
        
        # Ensure we have some content
        if not insights.main_topics:
            insights.main_topics = ["General professional content"]
        if not insights.key_insights:
            insights.key_insights = ["Content provides valuable professional insights"]
        if not insights.target_audience:
            insights.target_audience = "Professional audience"
        if not insights.linkedin_angles:
            insights.linkedin_angles = ["Share knowledge with network"]
        
        return insights
    
    def _parse_vision_response(self, response: str) -> AIInsights:
        """Parse vision AI response"""
        
        # Similar parsing to text
        return self._parse_insights(response)
    
    def _create_fallback_insights(self, content: ExtractedContent) -> AIInsights:
        """Create basic insights when AI fails"""
        
        return AIInsights(
            main_topics=["Professional Content"],
            key_insights=[
                "Content analysis in progress",
                "Professional insights to be extracted"
            ],
            target_audience="Professional network",
            professional_context="Valuable professional content for sharing",
            linkedin_angles=[
                "Share expertise with network",
                "Provide value to connections"
            ],
            technical_depth="intermediate",
            tone_suggestions=["Professional", "Informative"]
        )


# Export
__all__ = ['ContentAnalyzer']
