import streamlit as st
import asyncio
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
import time

# Local module imports
from ingestion import UnifiedProcessor, MultiProcessor, ProcessedContent, AggregatedContent
from blog_generation import BlogWorkflow, BlogGenerationState, BlogPost
from chatbot import ChatbotOrchestrator
from shared.models import AggregationStrategy

# Page configuration
st.set_page_config(
    page_title="LinkedIn Blog Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# LinkedIn-Authentic CSS
st.markdown("""
<style>
    :root {
        --linkedin-blue: #0A66C2;
        --linkedin-dark-blue: #004182;
        --linkedin-light-blue: #378FE9;
        --linkedin-black: #000000;
        --linkedin-gray-1: #F3F2EF;
        --linkedin-gray-2: #E7E5DF;
        --linkedin-success: #057642;
        --linkedin-warning: #915907;
        --linkedin-error: #CC1016;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--linkedin-blue);
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .blog-card {
        background: white;
        border: 1px solid var(--linkedin-gray-2);
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.08);
        transition: box-shadow 0.2s;
        margin: 1rem 0;
    }
    
    .blog-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    .quality-score {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--linkedin-blue);
    }
    
    .success-message {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid var(--linkedin-success);
    }
    
    .error-message {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid var(--linkedin-error);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
        border-left: 4px solid var(--linkedin-blue);
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
        border-left: 4px solid var(--linkedin-gray-2);
    }
    
    .stButton>button {
        background-color: var(--linkedin-blue);
        color: white;
        font-weight: 600;
        border-radius: 24px;
        padding: 8px 24px;
        transition: all 0.2s;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: var(--linkedin-dark-blue);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .file-preview {
        background: var(--linkedin-gray-1);
        border: 2px dashed var(--linkedin-gray-2);
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        margin: 1rem 0;
    }
    
    .linkedin-post {
        background: white;
        border: 1px solid var(--linkedin-gray-2);
        border-radius: 8px;
        padding: 20px;
        margin: 1rem 0;
        box-shadow: 0 0 0 1px rgba(0,0,0,0.08);
    }
    
    .post-header {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    
    /* Draft action buttons */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton button[kind="primary"]:hover {
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4) !important;
        transform: translateY(-2px);
    }
    
    /* Suggestion buttons */
    .stButton button[disabled] {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
    }
    
    /* Text area styling */
    .stTextArea textarea {
        border: 2px solid #0A66C2 !important;
        border-radius: 8px !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_blog' not in st.session_state:
    st.session_state.current_blog = None
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_input_key' not in st.session_state:
    st.session_state.chat_input_key = 0
if 'transfer_to_chat' not in st.session_state:
    st.session_state.transfer_to_chat = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Helper functions
def save_uploaded_file(uploaded_file) -> str:
    """Save Streamlit uploaded file to temp directory"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def convert_processed_to_state(processed: ProcessedContent, requirements: str, max_iterations: int = 3) -> BlogGenerationState:
    """Convert ingestion output to blog generation input"""
    return BlogGenerationState(
        source_content=processed.raw_content,
        content_insights=processed.insights.key_insights if processed.insights else [],
        user_requirements=requirements,
        max_iterations=max_iterations
    )

def convert_aggregated_to_state(aggregated: AggregatedContent, requirements: str, max_iterations: int = 3) -> BlogGenerationState:
    """Convert multi-file output to blog generation input"""
    all_insights = []
    for source in aggregated.sources:
        if source.insights and source.insights.key_insights:
            all_insights.extend(source.insights.key_insights[:3])
    
    return BlogGenerationState(
        source_content=aggregated.unified_insights,
        content_insights=all_insights[:10],
        user_requirements=requirements,
        max_iterations=max_iterations
    )

def display_error(error_message, suggestion=None):
    """Display actionable error message with suggestions"""
    with st.container():
        st.markdown(f'<div class="error-message">❌ **Error:** {error_message}</div>', unsafe_allow_html=True)
        
        if suggestion:
            st.info(f"💡 **Suggestion:** {suggestion}")
        
        with st.expander("🔍 Troubleshooting"):
            st.markdown("""
            **Common solutions:**
            - Check your API keys (GROQ_API_KEY in .env)
            - Try a smaller file (max 50MB)
            - Refresh the page and try again
            - Check console for detailed error messages
            """)
        
        if st.button("🔄 Try Again"):
            st.rerun()

def get_quality_color(score):
    """Get color for quality score"""
    if score >= 7:
        return "#057642"  # Green
    elif score >= 5:
        return "#915907"  # Yellow
    else:
        return "#CC1016"  # Red

def display_blog_post(blog_data, quality_score=None, show_quality=True):
    """Display blog post in LinkedIn-like format"""
    st.markdown('<div class="linkedin-post">', unsafe_allow_html=True)
    
    # Header with profile-like section
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("https://via.placeholder.com/50/0A66C2/FFFFFF?text=U", width=50)
    with col2:
        st.markdown("**Your Name**")
        st.caption("Your Title | LinkedIn Profile")
    
    st.markdown("---")
    
    # Handle both dict and Pydantic model
    if hasattr(blog_data, 'model_dump'):
        blog_dict = blog_data.model_dump()
    elif isinstance(blog_data, dict):
        blog_dict = blog_data
    else:
        blog_dict = {}
    
    # Post content
    if blog_dict.get('hook'):
        st.markdown(f"**{blog_dict.get('hook', '')}**")
        st.markdown("")
    
    if blog_dict.get('content'):
        st.markdown(blog_dict.get('content', ''))
        st.markdown("")
    
    if blog_dict.get('call_to_action'):
        st.markdown(f"**{blog_dict.get('call_to_action', '')}**")
        st.markdown("")
    
    # Hashtags
    if blog_dict.get('hashtags'):
        st.caption(" ".join(blog_dict.get('hashtags', [])))
    
    # Quality score (if provided and show_quality is True)
    if show_quality and quality_score:
        color = get_quality_color(quality_score)
        st.markdown(f"""
        <div style='background-color: {color}15; border-left: 4px solid {color}; 
                    padding: 0.75rem; border-radius: 4px; margin-top: 1rem;'>
            <span style='color: {color}; font-weight: 600; font-size: 1.1rem;'>
                📊 Quality Score: {quality_score}/10
            </span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def check_api_keys():
    """Check if required API keys are configured"""
    groq_key = os.getenv("GROQ_API_KEY")
    return groq_key is not None

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=100)
    st.title("LinkedIn Blog Assistant")
    st.markdown("---")
    
    # System Status
    st.subheader("🔌 System Status")
    if check_api_keys():
        st.success("✅ API Keys Configured")
        st.caption("Mode: Local Processing")
    else:
        st.error("❌ API Keys Missing")
        st.caption("Set GROQ_API_KEY in .env")
    
    st.markdown("---")
    st.caption("© 2024 LinkedIn Blog Assistant v2.0")

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home", 
    "📁 File Upload", 
    "💬 Chatbot", 
    "📊 Multi-File", 
    "ℹ️ About"
])

with tab1:
    st.markdown('<div class="main-header">🚀 LinkedIn Blog Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Transform any content into engaging LinkedIn posts</div>', unsafe_allow_html=True)
    
    # Features overview
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📁 File Processing")
        st.write("Upload PDFs, Word docs, PowerPoint, code files, or images")
        st.write("✓ AI-powered content extraction")
        st.write("✓ Multi-format support")
        st.write("✓ Instant analysis")
    
    with col2:
        st.markdown("### ✨ Blog Generation")
        st.write("Create engaging LinkedIn posts automatically")
        st.write("✓ Quality scoring (1-10)")
        st.write("✓ Iterative refinement")
        st.write("✓ LinkedIn optimization")
    
    with col3:
        st.markdown("### 💬 Conversational AI")
        st.write("Interactive chatbot for personalized assistance")
        st.write("✓ Human-in-the-loop feedback")
        st.write("✓ Session memory")
        st.write("✓ Smart improvements")
    
    st.markdown("---")
    
    # Quick start guide
    st.markdown("### 🎯 Quick Start Guide")
    
    with st.expander("1️⃣ Upload a File"):
        st.write("""
        Navigate to the **File Upload** tab and:
        1. Upload your document (PDF, Word, PPT, code, image)
        2. Set your preferences (audience, tone)
        3. Click **Generate Blog Post**
        4. Review and refine the generated post
        """)
    
    with st.expander("2️⃣ Use the Chatbot"):
        st.write("""
        Navigate to the **Chatbot** tab and:
        1. Start a conversation about your content
        2. Upload files or provide text directly
        3. Give feedback to improve the posts
        4. Approve when you're satisfied
        """)
    
    with st.expander("3️⃣ Process Multiple Files"):
        st.write("""
        Navigate to the **Multi-File** tab and:
        1. Upload 2-10 files at once
        2. Choose aggregation strategy
        3. Generate a comprehensive post
        4. Download the result
        """)

with tab2:
    st.markdown("## 📁 File Upload & Blog Generation")
    st.write("Upload a file and generate a LinkedIn blog post")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'jpg', 'png'],
            help="Supported formats: PDF, Word, PowerPoint, Code, Text, Images"
        )
    
    with col2:
        target_audience = st.text_input("Target Audience", "General professional audience")
        tone = st.selectbox("Tone", ["Professional and engaging", "Casual and friendly", "Technical and detailed", "Inspirational"])
        max_iterations = st.slider("Max Refinement Iterations", 1, 5, 3)
    
    if uploaded_file:
        # File preview section
        st.markdown('<div class="file-preview">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"**📄 {uploaded_file.name}**")
            st.caption(f"Type: {uploaded_file.type or 'Unknown'}")
        
        with col2:
            file_size = uploaded_file.size / 1024
            if file_size < 1024:
                st.metric("Size", f"{file_size:.1f} KB")
            else:
                st.metric("Size", f"{file_size/1024:.1f} MB")
        
        with col3:
            st.metric("Status", "✅ Ready")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("🚀 Generate Blog Post", type="primary"):
            if not check_api_keys():
                display_error("API keys not configured", "Please set GROQ_API_KEY in your .env file")
            else:
                # Enhanced loading with progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Step 1: Save file
                    status_text.text("📤 Processing...")
                    progress_bar.progress(30)
                    
                    file_path = save_uploaded_file(uploaded_file)
                    
                    # Step 2: Process
                    status_text.text("🔍 Analyzing content...")
                    progress_bar.progress(60)
                    
                    processor = UnifiedProcessor()
                    processed = asyncio.run(processor.process_file(file_path))
                    
                    if not processed.success:
                        raise Exception(processed.error_message or "File processing failed")
                    
                    # Step 3: Generate
                    status_text.text("✨ Generating blog post...")
                    progress_bar.progress(90)
                    
                    requirements = f"Target audience: {target_audience}. Tone: {tone}."
                    state = convert_processed_to_state(processed, requirements, max_iterations)
                    
                    workflow = BlogWorkflow()
                    result = workflow.run(state)
                    
                    # Complete
                    status_text.text("✅ Complete!")
                    progress_bar.progress(100)
                    time.sleep(0.3)
                    progress_bar.empty()
                    status_text.empty()
                    
                    if result.generation_complete and result.final_blog:
                        st.markdown('<div class="success-message">✅ Blog post generated successfully!</div>', unsafe_allow_html=True)
                        
                        blog_post = result.final_blog
                        quality_score = result.latest_critique.quality_score if result.latest_critique else None
                        
                        display_blog_post(blog_post, quality_score, show_quality=True)
                        
                        # Action buttons
                        st.markdown("---")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            blog_dict = blog_post.model_dump()
                            blog_text = f"""LinkedIn Blog Post
{'=' * 50}

Title: {blog_dict.get('title', '')}

Hook: {blog_dict.get('hook', '')}

Content:
{blog_dict.get('content', '')}

Call-to-Action: {blog_dict.get('call_to_action', '')}

Hashtags: {' '.join(blog_dict.get('hashtags', []))}

Target Audience: {blog_dict.get('target_audience', '')}
"""
                            st.download_button(
                                "📥 Download (TXT)",
                                blog_text,
                                file_name=f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col2:
                            # Continue in chat button
                            if st.button("💬 Continue in Chat", use_container_width=True, type="primary"):
                                # Store blog for transfer
                                st.session_state.transfer_to_chat = {
                                    'blog': blog_post,
                                    'quality_score': quality_score,
                                    'source': 'file_upload'
                                }
                                st.success("✅ Transferred to chat!")
                                time.sleep(0.5)
                                st.switch_page
                                st.rerun()
                        
                        with col3:
                            if st.button("🔄 Generate Another", use_container_width=True):
                                st.rerun()
                    else:
                        error_msg = result.last_error or "Generation failed - no blog produced"
                        display_error(error_msg, "Try adjusting your content or increasing max iterations")
                
                except Exception as e:
                    progress_bar.empty()
                    status_text.empty()
                    display_error(str(e), "Please try again or check your input file")

with tab3:
    st.markdown("## 💬 Conversational Blog Assistant")
    
    # Check for transfer from other tabs
    if st.session_state.transfer_to_chat:
        if not st.session_state.chatbot:
            st.session_state.chatbot = ChatbotOrchestrator()
        
        transfer_data = st.session_state.transfer_to_chat
        st.info(f"📝 Continuing with blog from {transfer_data['source'].replace('_', ' ').title()}")
        
        # Set current blog
        st.session_state.current_blog = {
            'current_blog': transfer_data['blog']
        }
        
        # Clear transfer
        st.session_state.transfer_to_chat = None
    
    # Top bar with session controls
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        if st.session_state.chatbot:
            st.success("🟢 Active Chat Session")
        else:
            st.info("🔵 No active session - Click 'New Session' to start")
    
    with col2:
        if st.button("🆕 New Session", use_container_width=True):
            if not check_api_keys():
                st.error("⚠️ API keys not configured")
            else:
                try:
                    st.session_state.chatbot = ChatbotOrchestrator()
                    st.session_state.messages = []
                    st.session_state.chat_history = []
                    st.session_state.current_blog = None
                    st.success("✅ New session started!")
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to start session: {str(e)}")
                    if st.button("🔄 Retry Session"):
                        st.rerun()
    
    with col3:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()
    
    # Initialize chatbot if needed
    if not st.session_state.chatbot and check_api_keys():
        with st.spinner("Initializing chatbot..."):
            try:
                st.session_state.chatbot = ChatbotOrchestrator()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to initialize chatbot: {str(e)}")
    
    st.divider()
    
    # Welcome message if chat is empty
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; padding: 2rem; border-radius: 12px; margin-bottom: 1rem;'>
            <h3 style='margin: 0; color: white;'>👋 Welcome to your LinkedIn Blog Assistant!</h3>
            <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                I can help you create amazing LinkedIn posts. Try:
            </p>
            <ul style='margin: 0.5rem 0 0 0; opacity: 0.9;'>
                <li>Upload a file to analyze</li>
                <li>Share your ideas for a blog post</li>
                <li>Ask me to refine your content</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for idx, msg in enumerate(st.session_state.messages):
            with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🤖"):
                st.markdown(msg["content"])
    
    # File upload section (collapsible)
    uploaded_chat_file = None
    with st.expander("📎 Attach a file (optional)", expanded=False):
        uploaded_chat_file = st.file_uploader(
            "Upload document",
            type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'jpg', 'png'],
            key="chat_file_uploader",
            label_visibility="collapsed"
        )
    
        if uploaded_chat_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.success(f"✅ {uploaded_chat_file.name}")
            with col2:
                file_size = uploaded_chat_file.size / 1024
                st.caption(f"{file_size:.1f} KB")
    
    # Chat input
    user_message = st.chat_input(
        "Type your message here...",
        key=f"chat_input_{st.session_state.chat_input_key}"
    )
    
    # Process user input
    if user_message:
        if not st.session_state.chatbot:
            st.error("❌ Please start a new session first")
        else:
            st.session_state.messages.append({"role": "user", "content": user_message})
            st.session_state.chat_history.append({"role": "user", "content": user_message})
            
            with st.chat_message("user", avatar="🧑"):
                st.markdown(user_message)
            
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                message_placeholder.markdown("💭 Thinking...")
                
                try:
                    file_path = None
                    if uploaded_chat_file:
                        file_path = save_uploaded_file(uploaded_chat_file)
                    
                    response = asyncio.run(
                        st.session_state.chatbot.process_message(user_message, file_path)
                    )
                    
                    # Display response immediately (no typing animation)
                    message_placeholder.markdown(response)
                    
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    current_blog = st.session_state.chatbot.get_current_blog()
                    if current_blog:
                        st.session_state.current_blog = current_blog
                
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    message_placeholder.markdown(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    
            st.session_state.chat_input_key += 1
            st.rerun()
    
    # Current Draft Section
    if st.session_state.current_blog and st.session_state.current_blog.get('current_blog'):
        st.divider()
        
        st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 1rem 1.5rem; border-radius: 8px 8px 0 0; 
                        margin-bottom: 0;'>
                <h3 style='margin: 0; color: white;'>📝 Current Draft</h3>
                <p style='margin: 0.25rem 0 0 0; opacity: 0.9; font-size: 0.9rem;'>
                    Review your generated LinkedIn post below
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        draft = st.session_state.current_blog['current_blog']
        
        with st.container():
            st.markdown("""
                <div style='background: #f8f9fa; padding: 1.5rem; 
                            border: 2px solid #e9ecef; border-radius: 0 0 8px 8px;'>
            """, unsafe_allow_html=True)
            
        display_blog_post(draft, show_quality=False)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 8px; 
                        border: 2px solid #e9ecef; margin-top: 1rem;'>
                <h4 style='margin-top: 0; color: #0A66C2;'>🎯 What would you like to do?</h4>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 2, 2])
        
        with col1:
            st.markdown("##### ✅ Approve & Download")
            if st.button(
                "✅ Approve Draft", 
                use_container_width=True, 
                type="primary",
                key="approve_btn"
            ):
                st.success("✅ Draft approved!")
                st.balloons()
                
                blog_dict = draft.model_dump() if hasattr(draft, 'model_dump') else draft
                blog_text = f"""# {blog_dict.get('title', '')}

{blog_dict.get('hook', '')}

{blog_dict.get('content', '')}

**{blog_dict.get('call_to_action', '')}**

{' '.join(blog_dict.get('hashtags', []))}

---
Generated by LinkedIn Blog Assistant
{datetime.now().strftime('%B %d, %Y at %I:%M %p')}
"""
                st.download_button(
                    "📥 Download Approved Post",
                    blog_text,
                    file_name=f"linkedin_post_approved_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    type="primary"
                )
        
        with col2:
            st.markdown("##### 📝 Request Changes")
            
            feedback_text = st.text_area(
                "What changes would you like?",
                placeholder="e.g., Make it more casual, add statistics, shorten the hook...",
                height=100,
                key="feedback_input",
                label_visibility="collapsed"
            )
            
            if st.button(
                "📝 Improve with Feedback", 
                use_container_width=True,
                disabled=not feedback_text,
                key="improve_btn"
            ):
                if feedback_text.strip():
                    st.session_state.messages.append({
                        "role": "user", 
                        "content": f"Please improve the draft: {feedback_text}"
                    })
                    st.session_state.chat_history.append({
                        "role": "user", 
                        "content": f"Please improve the draft: {feedback_text}"
                    })
                    st.rerun()
                else:
                    st.warning("Please enter your feedback first")
        
        with col3:
            st.markdown("##### 🔄 Start Fresh")
            
            if st.button(
                "🔄 Regenerate Completely", 
                use_container_width=True,
                key="regenerate_btn"
            ):
                regenerate_prompt = "Please create a completely different version of this post with a fresh approach"
                st.session_state.messages.append({
                    "role": "user", 
                    "content": regenerate_prompt
                })
                st.session_state.chat_history.append({
                    "role": "user", 
                    "content": regenerate_prompt
                })
                st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            with st.expander("📥 More Download Options"):
                blog_dict = draft.model_dump() if hasattr(draft, 'model_dump') else draft
                
                blog_text_plain = f"""{blog_dict.get('title', '')}

{blog_dict.get('hook', '')}

{blog_dict.get('content', '')}

{blog_dict.get('call_to_action', '')}

{' '.join(blog_dict.get('hashtags', []))}
"""
                
                blog_markdown = f"""# {blog_dict.get('title', '')}

## Hook
{blog_dict.get('hook', '')}

## Content
{blog_dict.get('content', '')}

## Call to Action
{blog_dict.get('call_to_action', '')}

## Hashtags
{' '.join(blog_dict.get('hashtags', []))}
"""
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.download_button(
                        "📄 Plain Text",
                        blog_text_plain,
                        file_name="linkedin_post.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col_b:
                    st.download_button(
                        "📝 Markdown",
                        blog_markdown,
                        file_name="linkedin_post.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
        
        # Quick improvement suggestions
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background: #fff3cd; padding: 1rem; border-radius: 8px; 
                        border-left: 4px solid #ffc107;'>
                <h5 style='margin-top: 0;'>💡 Quick Improvement Suggestions</h5>
                <p style='margin-bottom: 0.5rem;'>Not sure what to ask for? Try these:</p>
            </div>
        """, unsafe_allow_html=True)
        
        suggestion_cols = st.columns(4)
        
        suggestions = [
            ("📏 Shorten", "Make this post more concise and under 1000 characters"),
            ("🎨 More Casual", "Rewrite this in a more casual, conversational tone"),
            ("📊 Add Data", "Add relevant statistics or data points to strengthen the argument"),
            ("🎯 Stronger CTA", "Create a more compelling call-to-action that encourages engagement")
        ]
        
        for idx, (label, prompt) in enumerate(suggestions):
            with suggestion_cols[idx]:
                if st.button(label, use_container_width=True, key=f"suggestion_{idx}"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.chat_history.append({"role": "user", "content": prompt})
                    st.rerun()
        
        # Simplified Draft analytics
        with st.expander("📊 Draft Analytics"):
            blog_dict = draft.model_dump() if hasattr(draft, 'model_dump') else draft
            col1, col2, col3 = st.columns(3)
            
            content_length = len(blog_dict.get('content', ''))
            hashtag_count = len(blog_dict.get('hashtags', []))
            
            with col1:
                st.metric("Characters", content_length)
                if content_length < 150:
                    st.caption("⚠️ Too short")
                elif content_length > 1300:
                    st.caption("⚠️ Too long")
                else:
                    st.caption("✅ Good length")
            
            with col2:
                st.metric("Hashtags", hashtag_count)
                if hashtag_count < 3:
                    st.caption("⚠️ Add more")
                elif hashtag_count > 10:
                    st.caption("⚠️ Too many")
                else:
                    st.caption("✅ Good count")
            
            with col3:
                engagement_score = blog_dict.get('estimated_engagement_score', 0)
                st.metric("Est. Engagement", f"{engagement_score}/10")

with tab4:
    st.markdown("## 📊 Multi-File Processing")
    st.write("Upload multiple files and create a comprehensive LinkedIn post")
    
    uploaded_files = st.file_uploader(
        "Upload 2-10 files",
        type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'jpg', 'png'],
        accept_multiple_files=True,
        help="Upload between 2 and 10 files for aggregation"
    )
    
    if uploaded_files:
        st.info(f"📁 {len(uploaded_files)} files selected")
        
        col1, col2 = st.columns(2)
        
        with col1:
            strategy = st.selectbox(
                "Aggregation Strategy",
                ["synthesis", "comparison", "sequence", "timeline"],
                help="synthesis: Blend insights | comparison: Compare sources | sequence: Sequential story | timeline: Chronological"
            )
        
        with col2:
            target_audience = st.text_input("Target Audience", "General professional audience", key="multi_audience")
            tone = st.selectbox("Tone", ["Professional and engaging", "Technical", "Inspirational"], key="multi_tone")
        
        if len(uploaded_files) >= 2 and len(uploaded_files) <= 10:
            if st.button("🚀 Generate Aggregated Post", type="primary"):
                if not check_api_keys():
                    display_error("API keys not configured", "Please set GROQ_API_KEY in your .env file")
                else:
                    try:
                        with st.spinner("Processing files and generating comprehensive blog post..."):
                            file_paths = [save_uploaded_file(f) for f in uploaded_files]
                            
                            multi_processor = MultiProcessor()
                            aggregated = asyncio.run(
                                multi_processor.process_aggregated(
                                    file_paths=file_paths,
                                    strategy=AggregationStrategy(strategy)
                                )
                            )
                            
                            requirements = f"Target audience: {target_audience}. Tone: {tone}."
                            state = convert_aggregated_to_state(aggregated, requirements, max_iterations=3)
                            
                            workflow = BlogWorkflow()
                            result = workflow.run(state)
                            
                            if result.generation_complete and result.final_blog:
                                st.markdown('<div class="success-message">✅ Aggregated blog post generated!</div>', unsafe_allow_html=True)
                                
                                blog_post = result.final_blog
                                quality_score = result.latest_critique.quality_score if result.latest_critique else None
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Source Files", len(uploaded_files))
                                with col2:
                                    st.metric("Strategy", strategy.title())
                                with col3:
                                    st.metric("Quality Score", f"{quality_score}/10" if quality_score else "N/A")
                                
                                display_blog_post(blog_post, quality_score, show_quality=True)
                                
                                st.markdown("### 💡 Source Insights")
                                for idx, source in enumerate(aggregated.sources[:5], 1):
                                    with st.expander(f"📄 {Path(source.source_file).name}"):
                                        if source.insights and source.insights.key_insights:
                                            for insight in source.insights.key_insights[:3]:
                                                st.write(f"• {insight}")
                                
                                # Action buttons
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    blog_dict = blog_post.model_dump()
                                    blog_text = f"""# {blog_dict.get('title', '')}

{blog_dict.get('hook', '')}

{blog_dict.get('content', '')}

**{blog_dict.get('call_to_action', '')}**

{' '.join(blog_dict.get('hashtags', []))}

---
Generated from {len(uploaded_files)} sources
Strategy: {strategy}
{datetime.now().strftime('%B %d, %Y')}
"""
                                    st.download_button(
                                        "📥 Download (MD)",
                                        blog_text,
                                        file_name=f"linkedin_post_aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                                        mime="text/markdown",
                                        use_container_width=True
                                    )
                                
                                with col2:
                                    if st.button("💬 Continue in Chat", use_container_width=True, type="primary"):
                                        st.session_state.transfer_to_chat = {
                                            'blog': blog_post,
                                            'quality_score': quality_score,
                                            'source': 'multi_file'
                                        }
                                        st.success("✅ Transferred to chat!")
                                        time.sleep(0.5)
                                        st.rerun()
                                
                                with col3:
                                    if st.button("🔄 Generate Another", use_container_width=True):
                                        st.rerun()
                            else:
                                error_msg = result.last_error or "Generation failed"
                                display_error(error_msg, "Try adjusting your files or strategy")
                    
                    except Exception as e:
                        display_error(str(e), "Please check your files and try again")
        else:
            st.warning("⚠️ Please upload between 2 and 10 files")

with tab5:
    st.markdown("## ℹ️ About LinkedIn Blog Assistant")
    
    st.markdown("""
    ### 🎯 What is this?
    
    The LinkedIn Blog Assistant is an AI-powered tool that transforms any content into engaging LinkedIn posts. 
    It uses advanced language models to analyze your content and create professional, optimized posts.
    
    ### ✨ Key Features
    
    **1. Multi-Format Support**
    - 📄 Documents: PDF, Word, PowerPoint
    - 💻 Code: Python, JavaScript, Java, C++, and 20+ languages
    - 📝 Text: Plain text, Markdown
    - 🖼️ Images: JPG, PNG with AI vision analysis
    
    **2. Intelligent Processing**
    - AI-powered content extraction
    - Automatic insight generation
    - Quality scoring (1-10 scale)
    - LinkedIn algorithm optimization
    
    **3. Human-in-the-Loop**
    - Interactive refinement
    - Feedback incorporation
    - Iterative improvement
    - Approval workflow
    
    **4. Multi-File Aggregation**
    - Synthesis: Blend insights from multiple sources
    - Comparison: Compare and contrast content
    - Sequence: Create sequential narratives
    - Timeline: Chronological stories
    
    ### 🔧 Technology Stack
    
    **Frontend**
    - Streamlit for interactive UI
    - Python for local processing
    
    **Backend**
    - LangChain for document processing
    - LangGraph for workflow orchestration
    - Groq for language models
    - Google Gemini for vision analysis
    
    ### 📚 How to Use
    
    1. **Upload Content**: Choose your file or provide text
    2. **Set Preferences**: Specify audience and tone
    3. **Generate Post**: Let AI create your LinkedIn content
    4. **Refine**: Provide feedback for improvements
    5. **Approve**: Download your final post
    
    ### 🎓 Best Practices
    
    - Provide clear, well-structured source content
    - Specify your target audience accurately
    - Use the chatbot for personalized assistance
    - Review and refine generated content
    - Leverage multi-file processing for comprehensive posts
    
    ### ⚙️ Setup Requirements
    
    **Required Environment Variables:**
    ```
    GROQ_API_KEY=your-groq-api-key
    ```
    
    **Optional Environment Variables:**
    ```
    LANGSMITH_API_KEY=your-langsmith-key
    LANGSMITH_PROJECT=linkedin-blog-agent
    LANGSMITH_TRACING=true
    GOOGLE_API_KEY=your-google-key  # For image processing
    ```
    
    ### 📞 Support
    
    For issues or questions, please refer to the project documentation or README files in each module:
    - `ingestion/README.md`
    - `blog_generation/README.md`
    - `chatbot/README.md`
    
    ---
    
    **Version:** 2.0.0 (Optimized)
    **Last Updated:** 2024  
    **License:** MIT
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ using Streamlit | Powered by AI | Running in Local Mode</p>
    </div>
    """,
    unsafe_allow_html=True
)
