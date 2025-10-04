"""
Centralized prompt templates for blog generation and critique workflow using LangChain.

Contains templates for:
- Blog content generation
- Content critique and analysis
- Content refinement and improvement
"""

from typing import List, Dict, Any
from langchain.prompts import PromptTemplate
from blog_generation.config import BlogPost, CritiqueResult, BlogConfig

# ===== CONTENT GENERATOR PROMPTS =====

BLOG_GENERATOR_SYSTEM_PROMPT = """You are a LinkedIn content creation expert specializing in viral, engaging professional posts. 

Your expertise includes:
- Crafting compelling hooks that stop scrolling
- Writing valuable, actionable content 
- Optimizing for LinkedIn algorithm and engagement
- Creating authentic professional voice
- Using storytelling and data to drive engagement

CRITICAL REQUIREMENTS:
- Always respond with valid JSON matching the BlogPost schema
- Create content between 150-1300 characters for optimal LinkedIn engagement
- Include 5-8 relevant hashtags
- Start with a powerful hook (first 1-2 sentences)
- End with a clear call-to-action
- Focus on providing genuine value to professional audience

JSON Schema for BlogPost:
{
  "title": "Compelling title (10-60 chars)",
  "hook": "Opening hook ONLY (first 1-2 sentences that grab attention)",
  "content": "Main body content AFTER the hook (value, insights, context - do NOT repeat the hook)",
  "call_to_action": "Specific engagement request (question or CTA)",
  "hashtags": ["#relevant", "#professional", "#hashtags"],
  "target_audience": "Primary professional audience",
  "estimated_engagement_score": 1-10
}

CRITICAL: The 'hook' and 'content' are SEPARATE fields. Do NOT include the hook text in the content field."""

# LangChain PromptTemplate for blog generation
BLOG_GENERATION_TEMPLATE = PromptTemplate(
    input_variables=["source_content", "insights", "user_requirements", "iteration_count", "previous_feedback"],
    template="""Generate a LinkedIn blog post from this content:

SOURCE CONTENT:
{source_content}

KEY INSIGHTS:
{insights}

{user_requirements}

{previous_feedback}

LINKEDIN POST GUIDELINES:
1. CREATE compelling hook in the 'hook' field (question, surprising fact, bold statement)
2. WRITE main content in 'content' field WITHOUT repeating the hook
3. PROVIDE clear value in content (insights, tips, lessons, or data)
4. USE conversational, professional tone
5. INCLUDE personal touches or industry perspective
6. ADD specific call-to-action in 'call_to_action' field
7. ADD 5-8 relevant hashtags
8. KEEP total post within 150-1300 characters (hook + content + CTA combined)

ENGAGEMENT TACTICS TO INCLUDE:
- Ask questions to encourage comments
- Share actionable insights or tips
- Use numbers/statistics when relevant
- Tell brief stories or examples
- Challenge conventional thinking
- Provide industry perspective

OUTPUT FORMAT: Valid JSON only, matching BlogPost schema exactly. No additional text."""
)

def build_blog_generation_prompt(
    source_content: str,
    insights: List[str],
    user_requirements: str = "",
    iteration_count: int = 0,
    previous_feedback: str = ""
) -> str:
    """Build blog generation prompt with context using LangChain"""
    
    # Format insights as bullet points
    insights_text = "\n".join(f"• {insight}" for insight in insights[:5])
    
    # Format user requirements
    user_req_text = f"USER REQUIREMENTS:\n{user_requirements}\n" if user_requirements else ""
    
    # Format previous feedback
    feedback_text = ""
    if iteration_count > 0 and previous_feedback:
        feedback_text = f"""PREVIOUS FEEDBACK (Iteration {iteration_count}):
{previous_feedback}

IMPORTANT: Address the feedback above while maintaining the content's core value.
"""
    
    # Truncate source content if too long
    truncated_content = source_content[:2000] + ('...' if len(source_content) > 2000 else '')
    
    return BLOG_GENERATION_TEMPLATE.format(
        source_content=truncated_content,
        insights=insights_text,
        user_requirements=user_req_text,
        iteration_count=iteration_count,
        previous_feedback=feedback_text
    )

# ===== CONTENT CRITIC PROMPTS =====

CRITIQUE_SYSTEM_PROMPT = """You are a LinkedIn content strategy expert and professional copywriter specializing in viral content analysis.

Your role is to provide detailed, constructive critique of LinkedIn posts across these dimensions:

EVALUATION CRITERIA:
1. HOOK EFFECTIVENESS (1-10): Does the opening grab attention and stop scrolling?
2. VALUE DELIVERY (1-10): Does the content provide clear, actionable value?
3. LINKEDIN OPTIMIZATION (1-10): Is it optimized for the LinkedIn algorithm and format?
4. ENGAGEMENT POTENTIAL (1-10): Will it generate comments, shares, and meaningful discussions?
5. PROFESSIONAL TONE (1-10): Is the voice authentic and professionally appropriate?

CRITICAL ANALYSIS AREAS:
- Content structure and flow
- Hook strength and memorability
- Value proposition clarity
- Call-to-action effectiveness
- Hashtag relevance and strategy
- Length and readability
- Engagement trigger effectiveness

Always respond with valid JSON matching the CritiqueResult schema.

JSON Schema for CritiqueResult:
{
  "quality_score": 1-10,
  "quality_level": "draft|good|excellent|publish_ready",
  "strengths": ["specific strength points"],
  "weaknesses": ["specific weakness points"], 
  "specific_improvements": ["actionable improvement suggestions"],
  "tone_feedback": "detailed tone analysis",
  "engagement_feedback": "engagement potential analysis",
  "linkedin_optimization_feedback": "LinkedIn-specific optimization notes",
  "approved_for_publish": boolean
}"""

# LangChain PromptTemplate for critique
CRITIQUE_TEMPLATE = PromptTemplate(
    input_variables=["title", "hook", "content", "call_to_action", "hashtags", "target_audience", "context"],
    template="""Analyze this LinkedIn blog post comprehensively:

BLOG POST TO ANALYZE:
Title: {title}
Hook: {hook}

Content:
{content}

Call-to-Action: {call_to_action}
Hashtags: {hashtags}
Target Audience: {target_audience}

{context}

DETAILED ANALYSIS REQUIRED:

1. HOOK ANALYSIS:
   - Does it create curiosity or surprise?
   - Is it relevant to the target audience?
   - Would it stop someone from scrolling?

2. VALUE ASSESSMENT:
   - What specific value does this provide?
   - Are insights actionable and practical?
   - Is the content depth appropriate?

3. LINKEDIN OPTIMIZATION:
   - Content length (optimal: 150-1300 chars)
   - Hashtag strategy and relevance
   - Algorithm-friendly formatting
   - Mobile readability

4. ENGAGEMENT POTENTIAL:
   - Does it encourage comments/discussion?
   - Are there conversation starters?
   - Is the CTA compelling and specific?

5. PROFESSIONAL VOICE:
   - Is the tone authentic and professional?
   - Does it build authority/credibility?
   - Is it appropriate for LinkedIn audience?

SCORING GUIDE:
- 1-3: Poor, needs major revision
- 4-6: Good, needs improvement  
- 7-8: Excellent, minor tweaks needed
- 9-10: Publish-ready, viral potential

Provide specific, actionable feedback. Be constructive but honest about weaknesses.

OUTPUT FORMAT: Valid JSON only, matching CritiqueResult schema exactly. No additional text."""
)

def build_critique_prompt(blog_post: BlogPost, context: str = "") -> str:
    """Build critique prompt for blog analysis using LangChain"""
    
    context_text = f"CONTEXT: {context}" if context else ""
    
    return CRITIQUE_TEMPLATE.format(
        title=blog_post.title,
        hook=blog_post.hook,
        content=blog_post.content,
        call_to_action=blog_post.call_to_action,
        hashtags=', '.join(blog_post.hashtags),
        target_audience=blog_post.target_audience,
        context=context_text
    )

# ===== CONTENT REFINER PROMPTS =====

REFINER_SYSTEM_PROMPT = """You are a LinkedIn content optimization specialist focused on iterative improvement.

Your role is to take existing content and critique feedback to create improved versions that address specific weaknesses while preserving strengths.

KEY CAPABILITIES:
- Strengthen weak hooks and openings
- Enhance value delivery and clarity
- Improve engagement triggers
- Optimize for LinkedIn algorithm
- Maintain authentic professional voice
- Address specific critique points

REFINEMENT PRINCIPLES:
- Preserve what's working well
- Address critique points systematically
- Enhance rather than completely rewrite
- Maintain the original message and value
- Improve engagement potential
- Optimize technical LinkedIn factors

Always respond with valid JSON matching the BlogPost schema."""

# LangChain PromptTemplate for refinement
REFINEMENT_TEMPLATE = PromptTemplate(
    input_variables=["title", "content", "hook", "call_to_action", "hashtags", "quality_score", "quality_level", 
                    "strengths", "weaknesses", "improvements", "tone_feedback", "engagement_feedback", 
                    "linkedin_feedback", "focus_areas", "human_feedback"],
    template="""Refine this LinkedIn post based on the detailed critique provided:

ORIGINAL POST:
Title: {title}
Hook (separate field): {hook}
Content (body text AFTER hook): {content}
CTA: {call_to_action}
Hashtags: {hashtags}

IMPORTANT: Keep 'hook' and 'content' as SEPARATE fields. Do NOT repeat the hook in the content.

CRITIQUE ANALYSIS:
Quality Score: {quality_score}/10
Quality Level: {quality_level}

STRENGTHS TO PRESERVE:
{strengths}

WEAKNESSES TO ADDRESS:
{weaknesses}

SPECIFIC IMPROVEMENTS NEEDED:
{improvements}

DETAILED FEEDBACK:
Tone: {tone_feedback}
Engagement: {engagement_feedback}
LinkedIn Optimization: {linkedin_feedback}

{focus_areas}{human_feedback}

REFINEMENT INSTRUCTIONS:
1. PRESERVE the strengths identified in the critique
2. SYSTEMATICALLY address each weakness and improvement point
3. ENHANCE the hook if it scored low on attention-grabbing
4. STRENGTHEN value delivery with more specific, actionable insights
5. IMPROVE engagement triggers and call-to-action effectiveness
6. OPTIMIZE for LinkedIn best practices (length, hashtags, formatting)
7. MAINTAIN the authentic professional voice and core message

OUTPUT: Enhanced version that addresses critique while preserving what works.
GOAL: Increase overall quality score by at least 1-2 points.

OUTPUT FORMAT: Valid JSON only, matching BlogPost schema exactly. No additional text."""
)

def build_refinement_prompt(
    original_post: BlogPost,
    critique: CritiqueResult,
    focus_areas: List[str] = None,
    human_feedback: str = ""
) -> str:
    """Build refinement prompt for content improvement using LangChain"""
    
    focus_text = f"PRIORITY FOCUS AREAS: {', '.join(focus_areas)}\n" if focus_areas else ""
    human_text = f"HUMAN FEEDBACK: {human_feedback}\n" if human_feedback else ""
    
    return REFINEMENT_TEMPLATE.format(
        title=original_post.title,
        content=original_post.content,
        hook=original_post.hook,
        call_to_action=original_post.call_to_action,
        hashtags=', '.join(original_post.hashtags),
        quality_score=critique.quality_score,
        quality_level=critique.quality_level,
        strengths="\n".join(f"✓ {strength}" for strength in critique.strengths),
        weaknesses="\n".join(f"✗ {weakness}" for weakness in critique.weaknesses),
        improvements="\n".join(f"→ {improvement}" for improvement in critique.specific_improvements),
        tone_feedback=critique.tone_feedback,
        engagement_feedback=critique.engagement_feedback,
        linkedin_feedback=critique.linkedin_optimization_feedback,
        focus_areas=focus_text,
        human_feedback=human_text
    )

# ===== HUMAN FEEDBACK INTEGRATION PROMPTS =====

def build_human_feedback_prompt(
    blog_post: BlogPost,
    human_feedback: str,
    satisfaction_level: int
) -> str:
    """Build prompt incorporating human feedback"""
    
    satisfaction_text = {
        1: "Very unsatisfied - major changes needed",
        2: "Unsatisfied - significant improvements required", 
        3: "Neutral - moderate changes needed",
        4: "Satisfied - minor tweaks needed",
        5: "Very satisfied - minimal changes needed"
    }.get(satisfaction_level, "Unknown satisfaction level")
    
    return f"""Revise this LinkedIn post based on specific human feedback:

CURRENT POST:
{blog_post.content}

HUMAN FEEDBACK:
{human_feedback}

SATISFACTION LEVEL: {satisfaction_level}/5 ({satisfaction_text})

REVISION INSTRUCTIONS:
1. Carefully analyze the human feedback for specific requests
2. Maintain the post's core value and message
3. Address feedback points while preserving LinkedIn optimization
4. If satisfaction is low (1-2), consider more substantial changes
5. If satisfaction is high (4-5), make subtle refinements only
6. Ensure changes align with LinkedIn best practices

OUTPUT FORMAT: Valid JSON only, matching BlogPost schema exactly. No additional text."""

# ============================================================================
# MULTI-SOURCE BLOG GENERATION PROMPTS
# ============================================================================

MULTI_SOURCE_SYSTEM_PROMPT = """You are a LinkedIn content strategist specializing in synthesizing insights from multiple sources into cohesive, engaging posts.

Your expertise includes:
- Connecting insights across different content types (documents, presentations, code, images)
- Creating unified narratives from diverse sources
- Highlighting cross-references and relationships between sources
- Maintaining source attribution while creating smooth flow
- Adapting content strategy based on aggregation approach (synthesis, comparison, sequence, timeline)

Always create content that feels unified, not like a collection of separate summaries. The goal is to create a single, compelling LinkedIn post that leverages the collective wisdom of all sources."""

def build_multi_source_prompt(
    multi_source_content,
    user_requirements: str = ""
) -> str:
    """Build prompt for multi-source blog generation"""
    
    # Summarize sources
    sources_summary = []
    for i, source in enumerate(multi_source_content.sources):
        sources_summary.append(f"""
Source {i+1} ({source.content_type.value}): {source.source_file}
Key insights: {', '.join(source.key_insights[:3])}
Analysis: {source.ai_analysis[:200]}...
""")
    
    # Format unified insights
    unified_insights_text = '\n'.join(f"• {insight}" for insight in multi_source_content.unified_insights)
    
    strategy_instructions = {
        "synthesis": "Blend all insights into a unified narrative that shows how the sources complement each other. Create a cohesive story that weaves together the best elements from each source.",
        "comparison": "Compare and contrast the sources, highlighting similarities, differences, and complementary perspectives. Show how different approaches or viewpoints contribute to a complete picture.",
        "sequence": "Create a sequential story that flows logically from one source to the next. Build a narrative arc that takes readers through a journey or process.",
        "timeline": "Present insights in chronological order, showing evolution or progression over time. Highlight how things have changed or developed across the sources."
    }
    
    strategy_instruction = strategy_instructions.get(
        multi_source_content.aggregation_strategy.value,
        "Synthesize the sources effectively."
    )
    
    # Format cross-references
    cross_refs_text = ""
    if multi_source_content.cross_references:
        cross_refs_text = "\nCROSS-REFERENCES:\n"
        for source_id, related_sources in multi_source_content.cross_references.items():
            if related_sources:
                cross_refs_text += f"• {source_id} relates to: {', '.join(related_sources)}\n"
    
    return f"""Create a LinkedIn post from multiple sources using {multi_source_content.aggregation_strategy.value} strategy.

SOURCES:
{''.join(sources_summary)}

UNIFIED INSIGHTS:
{unified_insights_text}
{cross_refs_text}

STRATEGY: {strategy_instruction}

REQUIREMENTS:
{user_requirements}

Create a cohesive LinkedIn post that:
1. Seamlessly integrates insights from all sources
2. Maintains natural flow (not just a list of separate points)
3. Shows relationships between different sources
4. Provides clear value to professional audience
5. Includes engaging hook and strong call-to-action
6. Uses 5-8 relevant hashtags
7. Adapts tone and structure to the aggregation strategy

OUTPUT FORMAT: Valid JSON matching BlogPost schema."""

def build_multi_source_critique_prompt(
    blog_post,
    multi_source_content,
    previous_critique: str = ""
) -> str:
    """Build critique prompt for multi-source blog posts"""
    
    sources_count = len(multi_source_content.sources)
    strategy = multi_source_content.aggregation_strategy.value
    
    return f"""Critique this LinkedIn post generated from {sources_count} sources using {strategy} strategy.

BLOG POST:
Title: {blog_post.title}
Content: {blog_post.content}
Hashtags: {', '.join(blog_post.hashtags)}

SOURCE DIVERSITY:
- Total sources: {sources_count}
- Content types: {', '.join(set(s.content_type.value for s in multi_source_content.sources))}
- Strategy used: {strategy}

UNIFIED INSIGHTS COVERED:
{chr(10).join(f"• {insight}" for insight in multi_source_content.unified_insights[:5])}

PREVIOUS CRITIQUE: {previous_critique}

EVALUATION CRITERIA:
1. **Source Integration**: Does the post effectively blend insights from all sources?
2. **Strategy Alignment**: Does the content match the {strategy} approach?
3. **Coherence**: Does it read as a unified post, not separate summaries?
4. **Value**: Does it provide clear professional value?
5. **Engagement**: Will it drive LinkedIn engagement?
6. **Cross-References**: Are relationships between sources clear?

OUTPUT FORMAT: Valid JSON matching CritiqueResult schema."""

def build_multi_source_refinement_prompt(
    blog_post,
    critique_result,
    multi_source_content,
    user_feedback: str = ""
) -> str:
    """Build refinement prompt for multi-source blog posts"""
    
    strategy = multi_source_content.aggregation_strategy.value
    sources_summary = f"{len(multi_source_content.sources)} sources ({', '.join(set(s.content_type.value for s in multi_source_content.sources))})"
    
    return f"""Refine this LinkedIn post generated from {sources_summary} using {strategy} strategy.

CURRENT POST:
Title: {blog_post.title}
Content: {blog_post.content}
Hashtags: {', '.join(blog_post.hashtags)}

CRITIQUE FEEDBACK:
Quality Score: {critique_result.quality_score}/10
Quality Level: {critique_result.quality_level}
Strengths: {', '.join(critique_result.strengths[:3])}
Areas for Improvement: {', '.join(critique_result.areas_for_improvement[:3])}

USER FEEDBACK: {user_feedback}

REFINEMENT FOCUS:
1. **Source Balance**: Ensure all sources contribute meaningfully
2. **Strategy Consistency**: Maintain {strategy} approach throughout
3. **Flow Improvement**: Create smoother transitions between source insights
4. **Engagement Enhancement**: Strengthen hook and call-to-action
5. **LinkedIn Optimization**: Optimize for platform best practices

UNIFIED INSIGHTS TO PRESERVE:
{chr(10).join(f"• {insight}" for insight in multi_source_content.unified_insights[:5])}

OUTPUT FORMAT: Valid JSON matching BlogPost schema."""