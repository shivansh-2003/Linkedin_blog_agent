"""
LinkedIn Blog Agent - Streamlit Web Interface
=============================================

A professional conversational interface for creating LinkedIn posts from any content.

Features:
- 💬 Conversational Interface: Chat with AI assistant
- 📁 File Upload: Drag & drop files directly in chat
- 🔄 Real-time Refinement: Provide feedback and see instant improvements
- 📊 Quality Scoring: Detailed quality metrics and analysis
- 💾 Session Persistence: Conversations saved automatically
- 🎯 Intent Recognition: Smart understanding of user requests
- 🔗 Cross-tab Workflow: Seamless transitions between features

Usage:
    streamlit run app2.py

Architecture:
    - Chatbot Orchestrator: Manages conversation flow and intent detection
    - Blog Generation: AI-powered content creation with quality assessment
    - Ingestion Pipeline: Multi-format file processing and analysis
    - Memory Management: Persistent session storage and context

Supported File Types:
    - Documents: PDF, Word (.docx), PowerPoint (.pptx)
    - Code: Python, JavaScript, TypeScript, Java, C++, and 15+ more languages
    - Images: JPG, PNG, GIF with AI vision analysis
    - Text: TXT, MD, direct text input

API Keys Required:
    - GROQ_API_KEY: For LLM inference (required)
    - GOOGLE_API_KEY: For image analysis (optional)
    - LANGSMITH_API_KEY: For monitoring (optional)

Author: LinkedIn Blog AI Assistant Team
License: MIT
"""

import streamlit as st
import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import core components
from chatbot import ChatbotOrchestrator, ChatStage
from blog_generation import BlogPost, CritiqueResult

# Page configuration
st.set_page_config(
    page_title="LinkedIn Blog Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main layout */
    .main {
        background-color: #F3F4F6;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(135deg, #0077B5 0%, #005582 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .chat-message.user {
        background-color: #E3F2FD;
        border-left: 4px solid #0077B5;
    }
    
    .chat-message.assistant {
        background-color: #FFFFFF;
        border-left: 4px solid #10B981;
    }
    
    .chat-message .sender {
        font-weight: bold;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #1F2937;
    }
    
    .chat-message .timestamp {
        font-size: 0.75rem;
        color: #6B7280;
        margin-left: 0.5rem;
    }
    
    /* Blog preview card */
    .blog-preview-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .blog-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 1rem;
    }
    
    .blog-hook {
        background: #FEF3C7;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F59E0B;
        margin-bottom: 1rem;
        font-weight: 500;
    }
    
    .blog-content {
        line-height: 1.6;
        color: #374151;
        margin-bottom: 1rem;
    }
    
    .blog-cta {
        background: #DBEAFE;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3B82F6;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    
    .blog-hashtags {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 1rem;
    }
    
    .hashtag {
        background: #0077B5;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    
    /* Quality metrics */
    .quality-card {
        background: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .quality-score {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .quality-excellent {
        color: #10B981;
    }
    
    .quality-good {
        color: #3B82F6;
    }
    
    .quality-draft {
        color: #F59E0B;
    }
    
    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        text-align: center;
    }
    
    .status-conversing {
        background: #E5E7EB;
        color: #374151;
    }
    
    .status-awaiting {
        background: #FEF3C7;
        color: #92400E;
    }
    
    .status-reviewing {
        background: #DBEAFE;
        color: #1E40AF;
    }
    
    .status-completed {
        background: #D1FAE5;
        color: #065F46;
    }
    
    /* Action buttons */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        padding: 0.75rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* File uploader */
    .uploadedFile {
        border: 2px dashed #0077B5;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Progress indicator */
    .processing-indicator {
        text-align: center;
        padding: 2rem;
    }
    
    /* Empty state */
    .empty-state {
        text-align: center;
        padding: 3rem;
        color: #6B7280;
    }
    
    .empty-state-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #0077B5;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #6B7280;
        margin-top: 0.5rem;
    }
    
    /* Scrollable chat */
    .chat-container {
        max-height: 60vh;
        overflow-y: auto;
        padding-right: 1rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'current_blog' not in st.session_state:
        st.session_state.current_blog = None
    if 'current_critique' not in st.session_state:
        st.session_state.current_critique = None
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'show_welcome' not in st.session_state:
        st.session_state.show_welcome = True

def initialize_chatbot():
    """Initialize or resume chatbot session"""
    if st.session_state.chatbot is None:
        st.session_state.chatbot = ChatbotOrchestrator()
        st.session_state.session_id = st.session_state.chatbot.session_id
        
        # Add welcome message
        if st.session_state.show_welcome:
            welcome = st.session_state.chatbot.get_welcome_message()
            st.session_state.messages.append({
                "role": "assistant",
                "content": welcome,
                "timestamp": datetime.now()
            })
            st.session_state.show_welcome = False

def render_header():
    """Render application header"""
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🤖 LinkedIn Blog Assistant</div>
        <div class="header-subtitle">Transform any content into engaging LinkedIn posts with AI</div>
    </div>
    """, unsafe_allow_html=True)

def render_session_info():
    """Render session information in sidebar"""
    if st.session_state.chatbot:
        info = st.session_state.chatbot.get_session_info()
        
        st.sidebar.markdown("### 📊 Session Info")
        st.sidebar.markdown(f"**Session ID:** `{info['session_id'][:12]}...`")
        st.sidebar.markdown(f"**Messages:** {info['message_count']}")
        st.sidebar.markdown(f"**Posts Created:** {info['blogs_completed']}")
        
        # Stage indicator
        stage = info['current_stage']
        stage_colors = {
            'conversing': 'status-conversing',
            'awaiting_content': 'status-awaiting',
            'reviewing_draft': 'status-reviewing',
            'completed': 'status-completed'
        }
        stage_class = stage_colors.get(stage, 'status-conversing')
        st.sidebar.markdown(f'<div class="status-badge {stage_class}">{stage.replace("_", " ").title()}</div>', 
                          unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        
        # Settings
        st.sidebar.markdown("### ⚙️ Settings")
        if st.sidebar.button("🔄 Start New Session", use_container_width=True):
            st.session_state.chatbot = None
            st.session_state.messages = []
            st.session_state.current_blog = None
            st.session_state.current_critique = None
            st.session_state.show_welcome = True
            st.rerun()
        
        if st.sidebar.button("📥 Export Chat History", use_container_width=True):
            history = st.session_state.chatbot.get_conversation_history(100)
            st.sidebar.download_button(
                "Download JSON",
                data=str(history),
                file_name=f"chat_history_{st.session_state.session_id}.json",
                mime="application/json"
            )

def render_chat_message(message: Dict[str, Any]):
    """Render a single chat message"""
    role = message['role']
    content = message['content']
    timestamp = message.get('timestamp', datetime.now())
    
    message_class = "user" if role == "user" else "assistant"
    icon = "👤" if role == "user" else "🤖"
    sender = "You" if role == "user" else "Assistant"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="sender">{icon} {sender} <span class="timestamp">{timestamp.strftime('%H:%M')}</span></div>
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

def render_chat_interface():
    """Render left panel - chat interface"""
    st.markdown("### 💬 Conversation")
    
    # Chat history container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        if st.session_state.messages:
            for message in st.session_state.messages:
                render_chat_message(message)
        else:
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div>No messages yet. Start by uploading a file or typing your content!</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # File upload section
    st.markdown("---")
    st.markdown("### 📎 Upload File")
    
    uploaded_file = st.file_uploader(
        "Drop file here or click to browse",
        type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'html', 
              'jpg', 'jpeg', 'png', 'gif'],
        help="Supported: Documents, Code files, Images",
        key="file_uploader"
    )
    
    if uploaded_file and not st.session_state.processing:
        if st.button("🚀 Process File", type="primary", use_container_width=True):
            process_file_upload(uploaded_file)
    
    # Message input section
    st.markdown("---")
    st.markdown("### ✍️ Message")
    
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_area(
            "Type your message...",
            placeholder="Ask me anything or provide feedback on the draft...",
            height=100,
            label_visibility="collapsed"
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            submit_button = st.form_submit_button("📤 Send", type="primary", use_container_width=True)
        with col2:
            if st.form_submit_button("✨ Suggestions", use_container_width=True):
                show_suggestions()
        with col3:
            if st.form_submit_button("🔄 Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        if submit_button and user_input:
            process_user_message(user_input)

def render_blog_preview():
    """Render right panel - blog preview and actions"""
    st.markdown("### 📝 Blog Preview")
    
    if st.session_state.current_blog:
        blog = st.session_state.current_blog
        critique = st.session_state.current_critique
        
        # Quality status card
        render_quality_status(critique)
        
        # Blog preview card
        st.markdown('<div class="blog-preview-card">', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'<div class="blog-title">{blog["title"]}</div>', unsafe_allow_html=True)
        
        # Hook
        st.markdown(f'<div class="blog-hook">🪝 <strong>Hook:</strong><br>{blog["hook"]}</div>', 
                   unsafe_allow_html=True)
        
        # Content
        content_preview = blog["content"]
        if len(content_preview) > 500:
            content_preview = content_preview[:500] + "..."
            show_more = st.checkbox("Show full content", key="show_full_content")
            if show_more:
                content_preview = blog["content"]
        
        st.markdown(f'<div class="blog-content">{content_preview}</div>', unsafe_allow_html=True)
        
        # CTA
        st.markdown(f'<div class="blog-cta">💬 <strong>Call-to-Action:</strong><br>{blog["call_to_action"]}</div>', 
                   unsafe_allow_html=True)
        
        # Hashtags
        st.markdown('<div class="blog-hashtags">', unsafe_allow_html=True)
        for tag in blog.get("hashtags", [])[:6]:
            st.markdown(f'<span class="hashtag">{tag}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Action buttons
        render_action_buttons()
        
        # Quality breakdown (expandable)
        if critique:
            render_quality_breakdown(critique)
        
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div><strong>No draft yet</strong></div>
            <div>Upload a file or provide content to generate your LinkedIn post</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Example prompts
        st.markdown("### 💡 Try These Examples")
        
        if st.button("📊 Create a post about AI in healthcare", use_container_width=True):
            process_user_message("Create a professional LinkedIn post about how AI is transforming healthcare")
        
        if st.button("💻 Share coding best practices", use_container_width=True):
            process_user_message("Write a post about Python best practices for beginners")
        
        if st.button("🚀 Discuss startup lessons", use_container_width=True):
            process_user_message("Create a post about 3 key lessons from building a startup")

def render_quality_status(critique: Optional[Dict]):
    """Render quality status card"""
    if not critique:
        return
    
    score = critique.get('quality_score', 0)
    level = critique.get('quality_level', 'draft')
    
    # Determine color based on score
    if score >= 9:
        color_class = "quality-excellent"
        icon = "🌟"
    elif score >= 7:
        color_class = "quality-good"
        icon = "⭐"
    else:
        color_class = "quality-draft"
        icon = "📝"
    
    st.markdown(f"""
    <div class="quality-card">
        <div style="text-align: center;">
            <div style="font-size: 1.5rem;">{icon}</div>
            <div class="quality-score {color_class}">{score}/10</div>
            <div style="color: #6B7280; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">
                {level.replace('_', ' ')}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_action_buttons():
    """Render action buttons for current blog"""
    st.markdown("### 🎯 Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Approve & Finish", type="primary", use_container_width=True):
            process_user_message("Perfect! I approve this version.")
        
        if st.button("🔄 Regenerate", use_container_width=True):
            process_user_message("Please regenerate with a different approach")
    
    with col2:
        if st.button("📋 Copy to Clipboard", use_container_width=True):
            copy_blog_to_clipboard()
        
        if st.button("📥 Download", use_container_width=True):
            download_blog()

def render_quality_breakdown(critique: Dict):
    """Render detailed quality breakdown"""
    with st.expander("📊 Quality Breakdown", expanded=False):
        # Dimension scores
        dimensions = {
            "Hook Effectiveness": critique.get('hook_effectiveness', 0),
            "Value Delivery": critique.get('value_delivery', 0),
            "LinkedIn Optimization": critique.get('linkedin_optimization', 0),
            "Engagement Potential": critique.get('engagement_potential', 0),
            "Professional Tone": critique.get('professional_tone', 0)
        }
        
        for dim, score in dimensions.items():
            st.progress(score / 10, text=f"{dim}: {score}/10")
        
        # Strengths
        if critique.get('strengths'):
            st.markdown("**✅ Strengths:**")
            for strength in critique['strengths'][:3]:
                st.markdown(f"- {strength}")
        
        # Improvements
        if critique.get('weaknesses'):
            st.markdown("**⚠️ Areas to Improve:**")
            for weakness in critique['weaknesses'][:3]:
                st.markdown(f"- {weakness}")

def process_file_upload(uploaded_file):
    """Process uploaded file"""
    st.session_state.processing = True
    
    # Save file temporarily
    temp_path = Path(f"temp_{uploaded_file.name}")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": f"📎 Uploaded file: {uploaded_file.name}",
        "timestamp": datetime.now()
    })
    
    # Process with chatbot
    with st.spinner("🔄 Processing file and generating blog post..."):
        try:
            response = asyncio.run(
                st.session_state.chatbot.process_message(
                    f"Create a professional LinkedIn post from this file",
                    file_path=str(temp_path)
                )
            )
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            # Update current blog
            update_current_blog()
            
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        finally:
            # Clean up temp file
            if temp_path.exists():
                temp_path.unlink()
            st.session_state.processing = False
    
    st.rerun()

def process_user_message(user_input: str):
    """Process user text message"""
    st.session_state.processing = True
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # Process with chatbot
    with st.spinner("🤔 Thinking..."):
        try:
            response = asyncio.run(
                st.session_state.chatbot.process_message(user_input)
            )
            
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            # Update current blog
            update_current_blog()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            st.session_state.processing = False
    
    st.rerun()

def update_current_blog():
    """Update current blog and critique from chatbot state"""
    blog = st.session_state.chatbot.get_current_blog()
    if blog:
        st.session_state.current_blog = blog
        
        # Get critique from blog context
        blog_context = st.session_state.chatbot.memory.get_blog_context()
        if blog_context and blog_context.current_critique:
            st.session_state.current_critique = blog_context.current_critique

def copy_blog_to_clipboard():
    """Copy blog to clipboard"""
    if st.session_state.current_blog:
        blog = st.session_state.current_blog
        full_text = f"{blog['title']}\n\n{blog['hook']}\n\n{blog['content']}\n\n{blog['call_to_action']}\n\n{' '.join(blog['hashtags'])}"
        
        st.code(full_text, language=None)
        st.success("✅ Blog text displayed above - copy it manually")

def download_blog():
    """Download blog as text file"""
    if st.session_state.current_blog:
        blog = st.session_state.current_blog
        full_text = f"{blog['title']}\n\n{blog['hook']}\n\n{blog['content']}\n\n{blog['call_to_action']}\n\n{' '.join(blog['hashtags'])}"
        
        st.download_button(
            "📥 Download as .txt",
            data=full_text,
            file_name=f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

def show_suggestions():
    """Show suggestion modal"""
    st.info("""
    **💡 Quick Suggestions:**
    - "Make it more technical"
    - "Add more statistics"
    - "Make it shorter"
    - "More engaging tone"
    - "Add a personal story"
    """)

def main():
    """Main application entry point"""
    # Initialize
    init_session_state()
    initialize_chatbot()
    
    # Render header
    render_header()
    
    # Main layout - split screen
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        render_chat_interface()
    
    with col2:
        render_blog_preview()
    
    # Sidebar
    with st.sidebar:
        render_session_info()
        
        st.markdown("---")
        st.markdown("### 📚 Help")
        st.markdown("""
        **How to use:**
        1. Upload a file or type content
        2. Review the generated draft
        3. Provide feedback to refine
        4. Approve when ready
        
        **Supported files:**
        - Documents: PDF, Word, PowerPoint
        - Code: Python, JavaScript, etc.
        - Images: JPG, PNG, GIF
        """)

if __name__ == "__main__":
    main()