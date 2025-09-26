import google.generativeai as genai
from groq import Groq
from typing import List
from config import Config, ExtractedContent, ProcessingModel, ContentType
from prompt_templates import (
    CODE_SYSTEM_PROMPT,
    PPT_SYSTEM_PROMPT,
    build_code_user_prompt,
    build_ppt_user_prompt,
)

class AIAnalyzer:
    """AI-powered content analysis using Groq and Gemini models"""
    
    def __init__(self):
        # Initialize Groq client
        self.groq_client = Groq(api_key=Config.GROQ_API_KEY)
        
        # Initialize Gemini
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')
    
    def analyze_content(self, extracted_content: ExtractedContent) -> tuple[str, List[str]]:
        """Analyze extracted content and return summary and insights"""
        
        if extracted_content.content_type == ContentType.IMAGE:
            return self._analyze_with_gemini(extracted_content)
        elif extracted_content.content_type == ContentType.POWERPOINT:
            # Multimodal: run Gemini on each image, aggregate into the Groq prompt
            slides = extracted_content.structured_data.get('slides', [])
            image_captions = []
            for slide in slides:
                for img in slide.get('images', []):
                    try:
                        response = self.gemini_model.generate_content([
                            "Provide a brief professional caption and any detected text.",
                            {"mime_type": img.get("mime_type", "image/png"), "data": img.get("image_bytes")}
                        ])
                        caption = response.text if hasattr(response, 'text') else str(response)
                        image_captions.append({
                            "slide": slide.get('slide_number'),
                            "caption": caption[:500]
                        })
                    except Exception:
                        continue
            # Attach image captions to structured_data for downstream prompt
            extracted_content.structured_data["image_captions"] = image_captions
            return self._analyze_with_groq(extracted_content)
        else:
            return self._analyze_with_groq(extracted_content)
    
    def _analyze_with_groq(self, extracted_content: ExtractedContent) -> tuple[str, List[str]]:
        """Analyze content using Groq models with robust fallbacks"""
        
        # Select appropriate model
        model = extracted_content.processing_model.value
        
        # Create analysis prompt based on content type
        prompt = self._create_analysis_prompt(extracted_content)
        
        def _analyze_with_model(model_name: str) -> tuple[str, List[str]]:
            response = self.groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            CODE_SYSTEM_PROMPT if extracted_content.content_type == ContentType.CODE else PPT_SYSTEM_PROMPT
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.35
            )
            analysis_local = response.choices[0].message.content
            insights_local = self._extract_insights(analysis_local)
            return analysis_local, insights_local

        # Build ordered list of models to try: primary then fallbacks (env may override)
        fallback_env = (Config.__dict__.get("GROQ_FALLBACK_MODELS") or "").strip()
        env_models = [m.strip() for m in fallback_env.split(",") if m.strip()] if fallback_env else []
        candidates = [model] + env_models + [
            ProcessingModel.GROQ_LLAMA_8B.value,
            ProcessingModel.GROQ_GEMMA.value,
        ]

        last_error: str | None = None
        for candidate in candidates:
            try:
                return _analyze_with_model(candidate)
            except Exception as e:  # Try next candidate
                last_error = str(e)
                continue
        return f"Analysis failed: {last_error}", []
    
    def _analyze_with_gemini(self, extracted_content: ExtractedContent) -> tuple[str, List[str]]:
        """Analyze visual content using Gemini"""
        try:
            # We expect structured_data to include either 'image_bytes' or 'image_url'
            image_bytes = extracted_content.structured_data.get('image_bytes')
            image_url = extracted_content.structured_data.get('image_url')

            prompt = (
                "You are an expert visual content analyst for professional posts. "
                "Describe the image succinctly, extract any text, identify charts/diagrams, "
                "and propose 3-5 LinkedIn post angles with hashtags."
            )

            if image_bytes is not None:
                response = self.gemini_model.generate_content([
                    prompt,
                    {"mime_type": extracted_content.metadata.get("mime_type", "image/png"), "data": image_bytes}
                ])
            elif image_url is not None:
                response = self.gemini_model.generate_content([prompt, image_url])
            else:
                return "No image data provided for analysis.", []

            analysis = response.text if hasattr(response, 'text') else str(response)
            insights = self._extract_insights(analysis)
            return analysis, insights
        except Exception as e:
            return f"Gemini analysis failed: {str(e)}", []
    
    def _create_analysis_prompt(self, extracted_content: ExtractedContent) -> str:
        """Create analysis prompt based on content type"""
        
        base_info = f"""
Content Type: {extracted_content.content_type.value}
File: {extracted_content.file_path}
Length: {len(extracted_content.raw_text)} characters

Content:
{extracted_content.raw_text[:2000]}{'...' if len(extracted_content.raw_text) > 2000 else ''}
"""
        
        if extracted_content.content_type == ContentType.PDF:
            return f"""{base_info}

Analyze this PDF document and provide:
1. Main topics and themes
2. Key insights and takeaways  
3. Document structure and organization
4. Potential LinkedIn blog angles
5. Target audience recommendations

Metadata: {extracted_content.metadata}"""

        elif extracted_content.content_type == ContentType.CODE:
            return build_code_user_prompt(
                base_info,
                extracted_content.structured_data.get('analysis', {})
            )

        elif extracted_content.content_type == ContentType.POWERPOINT:
            slides = extracted_content.structured_data.get('slides', [])
            # Summarize images and captions compactly to keep prompt small
            images_summary = []
            for s in slides[:10]:
                if s.get('images'):
                    images_summary.append({
                        "slide": s.get('slide_number'),
                        "images_count": len(s['images'])
                    })
            image_captions = extracted_content.structured_data.get('image_captions', [])[:10]
            for ic in image_captions:
                if isinstance(ic.get('caption'), str) and len(ic['caption']) > 500:
                    ic['caption'] = ic['caption'][:500] + '...'
            return build_ppt_user_prompt(
                base_info,
                images_summary,
                image_captions,
                extracted_content.structured_data.get('presentation_metadata', {})
            )

        elif extracted_content.content_type == ContentType.WORD:
            return f"""{base_info}

Analyze this document and provide:
1. Document purpose and main arguments
2. Key insights and professional takeaways
3. Industry relevance and trends mentioned
4. LinkedIn engagement opportunities
5. Target professional audience"""

        else:  # TEXT
            return f"""{base_info}

Analyze this text content and provide:
1. Main themes and topics covered
2. Professional insights and learnings
3. Industry relevance and applications
4. LinkedIn content opportunities
5. Engagement potential and target audience"""
    
    def _extract_insights(self, analysis_text: str) -> List[str]:
        """Extract key insights from analysis text"""
        insights = []
        
        # Simple extraction - look for numbered points or bullet points
        lines = analysis_text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered insights or bullet points
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Clean up the insight
                insight = line.lstrip('0123456789.-• ').strip()
                if len(insight) > 10:  # Filter out very short insights
                    insights.append(insight)
        
        # If no structured insights found, try to extract sentences with key phrases
        if not insights:
            key_phrases = ['key insight', 'important', 'significant', 'notable', 'main', 'primary']
            sentences = analysis_text.split('.')
            
            for sentence in sentences:
                sentence = sentence.strip()
                if any(phrase in sentence.lower() for phrase in key_phrases) and len(sentence) > 20:
                    insights.append(sentence + '.')
        
        return insights[:5]  # Return top 5 insights