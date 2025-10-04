import streamlit as st
import requests
import json
from datetime import datetime
from pathlib import Path
import time

# Backend API URL
API_BASE_URL = "https://linkedin-blog-agent-1.onrender.com"

# Page configuration
st.set_page_config(
    page_title="LinkedIn Blog Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0A66C2;
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
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #0A66C2;
        margin: 1rem 0;
    }
    .quality-score {
        font-size: 1.5rem;
        font-weight: bold;
        color: #0A66C2;
    }
    .success-message {
        background-color: #d4edda;
        border-color: #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border-color: #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0A66C2;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #084d8f;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_blog' not in st.session_state:
    st.session_state.current_blog = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "🏠 Home"

# Helper functions
def make_api_request(endpoint, method="GET", data=None, files=None):
    """Make API request to backend"""
    url = f"{API_BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, data=data, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json(), None
        else:
            return None, f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return None, f"Connection error: {str(e)}"

def display_blog_post(blog_data, quality_score=None):
    """Display a blog post in a nice format"""
    st.markdown('<div class="blog-card">', unsafe_allow_html=True)
    
    if quality_score:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"### 📝 {blog_data.get('title', 'Untitled')}")
        with col2:
            st.markdown(f'<div class="quality-score">⭐ {quality_score}/10</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"### 📝 {blog_data.get('title', 'Untitled')}")
    
    st.markdown("#### 🎣 Hook")
    st.write(blog_data.get('hook', ''))
    
    st.markdown("#### 📄 Content")
    st.write(blog_data.get('content', ''))
    
    st.markdown("#### 📢 Call to Action")
    st.write(blog_data.get('call_to_action', ''))
    
    st.markdown("#### 🏷️ Hashtags")
    st.write(" ".join(blog_data.get('hashtags', [])))
    
    if blog_data.get('target_audience'):
        st.markdown("#### 🎯 Target Audience")
        st.write(blog_data.get('target_audience', ''))
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=100)
    st.title("LinkedIn Blog Assistant")
    st.markdown("---")
    
    # Navigation
    st.session_state.active_tab = st.radio(
        "Navigation",
        ["🏠 Home", "📁 File Upload", "💬 Chatbot", "📊 Multi-File", "ℹ️ About"],
        index=["🏠 Home", "📁 File Upload", "💬 Chatbot", "📊 Multi-File", "ℹ️ About"].index(st.session_state.active_tab)
    )
    
    st.markdown("---")
    
    # API Status
    st.subheader("🔌 API Status")
    with st.spinner("Checking..."):
        health_data, error = make_api_request("/health")
        if health_data:
            st.success("✅ Connected")
            st.caption(f"Version: {health_data.get('version', 'Unknown')}")
        else:
            st.error("❌ Disconnected")
    
    st.markdown("---")
    st.caption("© 2024 LinkedIn Blog Assistant")

# Main content area
if st.session_state.active_tab == "🏠 Home":
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

elif st.session_state.active_tab == "📁 File Upload":
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
        st.info(f"📄 Selected: {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
        
        if st.button("🚀 Generate Blog Post", type="primary"):
            with st.spinner("Processing file and generating blog post..."):
                # Save uploaded file temporarily
                temp_path = f"/tmp/{uploaded_file.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Upload and generate blog
                files = {'file': (uploaded_file.name, uploaded_file.getvalue())}
                data = {
                    'target_audience': target_audience,
                    'tone': tone,
                    'max_iterations': max_iterations
                }
                
                result, error = make_api_request(
                    "/api/generate-blog-from-file",
                    method="POST",
                    data=data,
                    files=files
                )
                
                if result and result.get('success'):
                    st.markdown('<div class="success-message">✅ Blog post generated successfully!</div>', unsafe_allow_html=True)
                    
                    # Display results
                    blog_post = result.get('blog_post')
                    if blog_post:
                        display_blog_post(blog_post, result.get('quality_score'))
                        
                        # Download option
                        st.markdown("---")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            blog_text = f"""LinkedIn Blog Post
{'=' * 50}

Title: {blog_post.get('title', '')}

Hook: {blog_post.get('hook', '')}

Content:
{blog_post.get('content', '')}

Call-to-Action: {blog_post.get('call_to_action', '')}

Hashtags: {' '.join(blog_post.get('hashtags', []))}

Target Audience: {blog_post.get('target_audience', '')}
"""
                            st.download_button(
                                "📥 Download Blog Post",
                                blog_text,
                                file_name=f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            if st.button("🔄 Generate Another Version"):
                                st.rerun()
                else:
                    st.markdown(f'<div class="error-message">❌ {error or "Generation failed"}</div>', unsafe_allow_html=True)

elif st.session_state.active_tab == "💬 Chatbot":
    st.markdown("## 💬 Conversational Blog Assistant")
    st.write("Chat with the AI to create and refine your LinkedIn posts")
    
    # Session management
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.session_id:
            st.success(f"📌 Session: {st.session_state.session_id[:8]}...")
        else:
            st.info("No active session")
    
    with col2:
        if st.button("🆕 New Session"):
            result, error = make_api_request("/api/chat/start", method="POST")
            if result:
                st.session_state.session_id = result.get('session_id')
                st.session_state.chat_history = []
                st.success("New session started!")
                st.rerun()
    
    with col3:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Start session if needed
    if not st.session_state.session_id:
        result, error = make_api_request("/api/chat/start", method="POST")
        if result:
            st.session_state.session_id = result.get('session_id')
    
    st.markdown("---")
    
    # Chat history display
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)
    
    # File upload in chat
    uploaded_chat_file = st.file_uploader(
        "Upload a file (optional)",
        type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'jpg', 'png'],
        key="chat_file_uploader"
    )
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_message = st.text_input(
            "Your message",
            placeholder="Type your message here...",
            key="chat_input",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 Send", type="primary")
    
    if send_button and user_message:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        with st.spinner("Thinking..."):
            # Prepare request
            data = {
                "message": user_message,
                "session_id": st.session_state.session_id
            }
            
            # Send message
            result, error = make_api_request("/api/chat/message", method="POST", data=data)
            
            if result and result.get('success'):
                response = result.get('response', '')
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Update blog context if available
                if result.get('blog_context'):
                    st.session_state.current_blog = result['blog_context']
                
                st.rerun()
            else:
                st.error(f"Error: {error}")
    
    # Quick actions
    if st.session_state.current_blog and st.session_state.current_blog.get('current_draft'):
        st.markdown("---")
        st.markdown("### 📝 Current Draft")
        
        draft = st.session_state.current_blog['current_draft']
        display_blog_post(draft)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("✅ Approve Draft"):
                data = {
                    "session_id": st.session_state.session_id,
                    "approved": True,
                    "final_notes": "Approved via Streamlit interface"
                }
                result, error = make_api_request("/api/chat/approve", method="POST", data=data)
                if result:
                    st.success("Draft approved!")
                    st.rerun()
        
        with col2:
            if st.button("🔄 Request Changes"):
                st.session_state.feedback_mode = True
        
        with col3:
            blog_text = f"{draft.get('title', '')}\n\n{draft.get('hook', '')}\n\n{draft.get('content', '')}\n\n{draft.get('call_to_action', '')}\n\n{' '.join(draft.get('hashtags', []))}"
            st.download_button(
                "📥 Download",
                blog_text,
                file_name="linkedin_post.txt"
            )

elif st.session_state.active_tab == "📊 Multi-File":
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
                with st.spinner("Processing files and generating comprehensive blog post..."):
                    files = [('files', (f.name, f.getvalue())) for f in uploaded_files]
                    data = {
                        'aggregation_strategy': strategy,
                        'target_audience': target_audience,
                        'tone': tone,
                        'max_iterations': 3
                    }
                    
                    result, error = make_api_request(
                        "/api/aggregate",
                        method="POST",
                        data=data,
                        files=files
                    )
                    
                    if result and result.get('success'):
                        st.markdown('<div class="success-message">✅ Aggregated blog post generated!</div>', unsafe_allow_html=True)
                        
                        blog_post = result.get('blog_post')
                        if blog_post:
                            # Show aggregation info
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Source Files", blog_post.get('source_count', 0))
                            with col2:
                                st.metric("Content Types", len(blog_post.get('source_types', [])))
                            with col3:
                                st.metric("Quality Score", f"{blog_post.get('engagement_score', 0)}/10")
                            
                            # Display blog
                            display_blog_post(blog_post, blog_post.get('engagement_score'))
                            
                            # Show insights
                            if blog_post.get('unified_insights'):
                                st.markdown("### 💡 Unified Insights")
                                for insight in blog_post.get('unified_insights', []):
                                    st.write(f"• {insight}")
                    else:
                        st.markdown(f'<div class="error-message">❌ {error or "Generation failed"}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please upload between 2 and 10 files")

elif st.session_state.active_tab == "ℹ️ About":
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
    - Python for backend communication
    
    **Backend**
    - FastAPI for REST API
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
    
    ### 📞 Support
    
    For issues or questions, please refer to the project documentation.
    
    ### 📊 API Endpoints
    
    - `GET /health` - API health check
    - `POST /api/ingest` - Process file
    - `POST /api/generate-blog` - Generate from text
    - `POST /api/generate-blog-from-file` - Generate from file
    - `POST /api/aggregate` - Multi-file processing
    - `POST /api/chat/*` - Chatbot endpoints
    
    ---
    
    **Version:** 2.0.0  
    **Last Updated:** 2024  
    **License:** MIT
    """)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Made with ❤️ using Streamlit | Powered by AI</p>
    </div>
    """,
    unsafe_allow_html=True
)