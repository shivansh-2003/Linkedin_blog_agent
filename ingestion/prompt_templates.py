"""
Centralized prompt templates for ingestion analyzers.

Contains templates for:
- Code analysis long-form professional summary
- PowerPoint analysis long-form professional summary
"""

from typing import Dict, Any, List


CODE_SYSTEM_PROMPT = (
    "You are an expert software engineer and educator analyzing code for a professional audience. "
    "Write a detailed, structured analysis with clear headings and bullet points. "
    "Include purpose, architecture, key components, algorithms, complexity, risks, best practices, and improvements. "
    "End with a LinkedIn-ready outline and 5-8 hashtags."
)


def build_code_user_prompt(base_info: str, analysis_struct: Dict[str, Any]) -> str:
    return f"""{base_info}

Analyze this code in depth and provide a detailed professional summary:
1. What the code does and how it is structured (modules, classes, functions)
2. Key algorithms, data flows, and noteworthy implementation details
3. Complexity hotspots and potential risks or edge cases
4. Best practices followed and areas of improvement
5. How to explain this to a LinkedIn audience (learning takeaways, practical uses)
6. A suggested long-form post outline, including title and 5-8 hashtags

Code structure analysis: {analysis_struct}
"""


PPT_SYSTEM_PROMPT = (
    "You are a professional content strategist summarizing presentations for LinkedIn. "
    "Write a long, structured summary that blends text and image insights. "
    "Keep it concise but informative, with headings and bullet points, and actionable takeaways."
)


def build_ppt_user_prompt(
    base_info: str,
    images_summary_compact: List[Dict[str, Any]],
    image_captions_compact: List[Dict[str, Any]],
    presentation_metadata: Dict[str, Any]
) -> str:
    return f"""{base_info}

You are given a presentation's extracted text, slide structure, and information about embedded images.
Write a detailed professional summary optimized for LinkedIn, with sections:
- Executive summary (4-6 sentences)
- Key themes and narrative arc
- Slide-by-slide highlights (reference slide numbers where useful)
- Insights and implications for professionals
- Suggested LinkedIn post outline and 5-8 hashtags

Slides with images summary (compact): {images_summary_compact}
Image captions (vision analysis, compact): {image_captions_compact}
Presentation metadata: {presentation_metadata}
"""


