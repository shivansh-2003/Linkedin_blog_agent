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
    
    .post-engagement {
        display: flex;
        justify-content: space-around;
        padding: 0.5rem 0;
        border-top: 1px solid var(--linkedin-gray-2);
        margin-top: 1rem;
    }
    
    .engagement-button {
        background: none;
        border: none;
        color: #666;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 4px;
        transition: background-color 0.2s;
    }
    
    .engagement-button:hover {
        background-color: var(--linkedin-gray-1);
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

def display_error(error_message, suggestion=None):
    """Display actionable error message with suggestions"""
    with st.container():
        st.markdown(f'<div class="error-message">❌ **Error:** {error_message}</div>', unsafe_allow_html=True)
        
        if suggestion:
            st.info(f"💡 **Suggestion:** {suggestion}")
        
        with st.expander("🔍 Troubleshooting"):
            st.markdown("""
            **Common solutions:**
            - Check your internet connection
            - Try a smaller file (max 50MB)
            - Refresh the page and try again
            - Contact support if issue persists
            """)
        
        if st.button("🔄 Try Again"):
            st.rerun()

def display_blog_post(blog_data, quality_score=None):
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
    
    # Post content
    if blog_data.get('hook'):
        st.markdown(f"**{blog_data.get('hook', '')}**")
        st.markdown("")
    
    if blog_data.get('content'):
        st.markdown(blog_data.get('content', ''))
        st.markdown("")
    
    if blog_data.get('call_to_action'):
        st.markdown(f"**{blog_data.get('call_to_action', '')}**")
        st.markdown("")
    
    # Hashtags
    if blog_data.get('hashtags'):
        st.caption(" ".join(blog_data.get('hashtags', [])))
    
    st.markdown("---")
    
    # Engagement section
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.button("👍 Like", key=f"like_{id(blog_data)}")
    with col2:
        st.button("💬 Comment", key=f"comment_{id(blog_data)}")
    with col3:
        st.button("🔄 Repost", key=f"repost_{id(blog_data)}")
    with col4:
        st.button("📤 Share", key=f"share_{id(blog_data)}")
    
    # Quality score (if provided)
    if quality_score:
        st.info(f"📊 Quality Score: {quality_score}/10")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/174/174857.png", width=100)
    st.title("LinkedIn Blog Assistant")
    st.markdown("---")
    
    # Navigation
    st.markdown("### 🧭 Navigation")
    st.markdown("""
    - 🏠 **Home** - Overview and quick start
    - 📁 **File Upload** - Single file processing
    - 💬 **Chatbot** - Interactive AI assistant
    - 📊 **Multi-File** - Multiple file aggregation
    - ℹ️ **About** - Documentation and help
    """)
    
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
        
        # Preview for text files
        if uploaded_file.type in ["text/plain", "text/markdown"]:
            with st.expander("📄 Preview Content"):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    preview = content[:500] + "..." if len(content) > 500 else content
                    st.text(preview)
                    uploaded_file.seek(0)  # Reset file pointer
                except:
                    st.warning("Could not preview file content")
        
        if st.button("🚀 Generate Blog Post", type="primary"):
            # Enhanced loading with progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Upload
            status_text.text("📤 Uploading file...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            # Save uploaded file temporarily
            temp_path = f"/tmp/{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                
                # Step 2: Process
                status_text.text("🔍 Analyzing content...")
                progress_bar.progress(50)
                
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
                
                # Step 3: Generate
                status_text.text("✨ Generating blog post...")
                progress_bar.progress(75)
                time.sleep(0.5)
                
                # Step 4: Complete
                status_text.text("✅ Complete!")
                progress_bar.progress(100)
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
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
                    # Enhanced error display
                    if "Connection error" in str(error):
                        display_error(
                            "Unable to connect to the server", 
                            "Please check your internet connection and try again"
                        )
                    elif "500" in str(error):
                        display_error(
                            "Server error occurred", 
                            "The server is temporarily unavailable. Please try again in a few minutes"
                        )
                    elif "413" in str(error) or "too large" in str(error).lower():
                        display_error(
                            "File too large", 
                            "Please upload a file smaller than 50MB or compress your file first"
                        )
                    else:
                        display_error(
                            error or "Generation failed", 
                            "Please try again or contact support if the issue persists"
                        )

with tab3:
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
    
    # Chat history display with fixed height and auto-scroll
    chat_container = st.container(height=500)
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.write(message["content"])
    
    # File upload in chat
    uploaded_chat_file = st.file_uploader(
        "Upload a file (optional)",
        type=['pdf', 'docx', 'pptx', 'txt', 'md', 'py', 'js', 'java', 'cpp', 'jpg', 'png'],
        key="chat_file_uploader"
    )
    
    # Chat input with st.chat_input for better UX
    user_message = st.chat_input("Type your message here...")
    
    if user_message:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Show user message immediately
        with st.chat_message("user"):
            st.write(user_message)
        
        # Show assistant response
        with st.chat_message("assistant"):
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
                    
                    st.write(response)
                else:
                    error_msg = f"Error: {error}"
                    st.session_state.chat_history.append({"role": "assistant", "content": error_msg})
                    st.error(error_msg)
    
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