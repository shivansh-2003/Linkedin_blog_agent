#!/usr/bin/env python3
"""
LinkedIn Blog AI Assistant - Streamlit Chat Application

A comprehensive chat interface that integrates:
- Chatbot orchestrator for conversational interactions
- Blog generation workflow with LangGraph
- Ingestion system for document processing
- LangSmith tracing for monitoring
"""

import streamlit as st
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import json

# Add project root to path
sys.path.append(str(Path(__file__).parent))

# Import all modules
from chatbot.chatbot_orchastrator import ChatbotOrchestrator
from chatbot.config import ChatStage, UserIntent
from blog_generation.workflow import BlogGenerationWorkflow
from blog_generation.config import BlogGenerationState, ProcessingStatus
from ingestion.unified_processor import UnifiedProcessor
from langsmith_config import trace_step, verify_langsmith_setup

# Page configuration
st.set_page_config(
    page_title="LinkedIn Blog AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0077b5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .system-message {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-ready { background-color: #4caf50; }
    .status-processing { background-color: #ff9800; }
    .status-error { background-color: #f44336; }
    .file-upload-area {
        border: 2px dashed #ccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "blog_workflow" not in st.session_state:
    st.session_state.blog_workflow = None
if "ingestion_processor" not in st.session_state:
    st.session_state.ingestion_processor = None
if "langsmith_ready" not in st.session_state:
    st.session_state.langsmith_ready = False
if "current_stage" not in st.session_state:
    st.session_state.current_stage = ChatStage.INITIAL
if "blog_context" not in st.session_state:
    st.session_state.blog_context = None

@trace_step("streamlit_app_initialization", "tool")
def initialize_components():
    """Initialize all system components"""
    try:
        # Initialize LangSmith
        if verify_langsmith_setup():
            st.session_state.langsmith_ready = True
            st.success("✅ LangSmith tracing enabled")
        else:
            st.warning("⚠️ LangSmith not configured - tracing disabled")
        
        # Initialize Chatbot
        if st.session_state.chatbot is None:
            st.session_state.chatbot = ChatbotOrchestrator()
            st.success("✅ Chatbot initialized")
        
        # Initialize Blog Generation Workflow
        if st.session_state.blog_workflow is None:
            st.session_state.blog_workflow = BlogGenerationWorkflow()
            st.success("✅ Blog generation workflow initialized")
        
        # Initialize Ingestion Processor
        if st.session_state.ingestion_processor is None:
            st.session_state.ingestion_processor = UnifiedProcessor()
            st.success("✅ Document ingestion processor initialized")
        
        return True
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        return False

@trace_step("streamlit_chat_processing", "workflow")
async def process_chat_message(user_input: str, uploaded_file: Optional[bytes] = None, file_name: Optional[str] = None) -> str:
    """Process user input and generate response"""
    try:
        chatbot = st.session_state.chatbot
        
        # Handle file upload if present
        if uploaded_file and file_name:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file_name).suffix) as tmp_file:
                tmp_file.write(uploaded_file)
                tmp_file_path = tmp_file.name
            
            try:
                # Process file through ingestion
                with st.spinner("📁 Processing uploaded file..."):
                    result = st.session_state.ingestion_processor.process_file(tmp_file_path)
                
                if result.success:
                    # Add file processing result to context
                    file_context = f"File '{file_name}' processed successfully. Content type: {result.content_type.value}. AI Analysis: {result.ai_analysis[:200]}..."
                    user_input = f"{user_input}\n\n[File Context: {file_context}]"
                    st.success(f"✅ File processed: {result.content_type.value}")
                else:
                    st.error(f"❌ File processing failed: {result.error}")
                    return "I'm sorry, but I couldn't process the uploaded file. Please try again or provide the content in text format."
            finally:
                # Clean up temporary file
                os.unlink(tmp_file_path)
        
        # Process through chatbot
        with st.spinner("🤖 Processing your message..."):
            response = await chatbot.process_user_input(user_input)
        
        return response
    except Exception as e:
        st.error(f"❌ Error processing message: {str(e)}")
        return "I'm sorry, but I encountered an error processing your request. Please try again."

@trace_step("streamlit_blog_generation", "workflow")
async def generate_blog_post(content: str, requirements: str = "") -> Dict[str, Any]:
    """Generate a blog post using the blog generation workflow"""
    try:
        workflow = st.session_state.blog_workflow
        
        # Create initial state
        initial_state = BlogGenerationState(
            source_content=content,
            user_requirements=requirements or "Create an engaging LinkedIn blog post",
            max_iterations=2,
            current_status=ProcessingStatus.GENERATING
        )
        
        # Run workflow
        with st.spinner("📝 Generating blog post..."):
            result_state = workflow.run_workflow(initial_state)
        
        return {
            "success": result_state.current_status == ProcessingStatus.COMPLETED,
            "blog_post": result_state.final_blog,
            "quality_score": result_state.latest_critique.quality_score if result_state.latest_critique else 0,
            "iterations": result_state.iteration_count,
            "error": result_state.last_error
        }
    except Exception as e:
        return {
            "success": False,
            "blog_post": None,
            "quality_score": 0,
            "iterations": 0,
            "error": str(e)
        }

def display_chat_message(message: Dict[str, Any]):
    """Display a chat message with appropriate styling"""
    if message["role"] == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>You:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    elif message["role"] == "assistant":
        st.markdown(f"""
        <div class="chat-message bot-message">
            <strong>BlogBot:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-message system-message">
            <strong>System:</strong> {message["content"]}
        </div>
        """, unsafe_allow_html=True)

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 LinkedIn Blog AI Assistant</h1>', unsafe_allow_html=True)
    
    # Sidebar for system status and controls
    with st.sidebar:
        st.header("🔧 System Status")
        
        # Initialize components
        if st.button("🔄 Initialize System"):
            initialize_components()
        
        # Display system status
        st.subheader("Component Status")
        
        # LangSmith status
        langsmith_status = "🟢 Ready" if st.session_state.langsmith_ready else "🔴 Not Configured"
        st.write(f"LangSmith: {langsmith_status}")
        
        # Chatbot status
        chatbot_status = "🟢 Ready" if st.session_state.chatbot else "🔴 Not Initialized"
        st.write(f"Chatbot: {chatbot_status}")
        
        # Blog workflow status
        blog_status = "🟢 Ready" if st.session_state.blog_workflow else "🔴 Not Initialized"
        st.write(f"Blog Generation: {blog_status}")
        
        # Ingestion status
        ingestion_status = "🟢 Ready" if st.session_state.ingestion_processor else "🔴 Not Initialized"
        st.write(f"Document Ingestion: {ingestion_status}")
        
        # Current stage
        st.subheader("Current Stage")
        st.write(f"Stage: {st.session_state.current_stage.value}")
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.session_state.current_stage = ChatStage.INITIAL
            st.session_state.blog_context = None
            st.rerun()
        
        # Export chat button
        if st.button("📥 Export Chat"):
            chat_data = {
                "messages": st.session_state.messages,
                "timestamp": time.time(),
                "langsmith_ready": st.session_state.langsmith_ready
            }
            st.download_button(
                label="Download Chat History",
                data=json.dumps(chat_data, indent=2),
                file_name=f"chat_history_{int(time.time())}.json",
                mime="application/json"
            )
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat Interface")
        
        # Display chat messages
        for message in st.session_state.messages:
            display_chat_message(message)
        
        # File upload section
        st.subheader("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a file to process",
            type=['pdf', 'docx', 'pptx', 'txt', 'py', 'js', 'java', 'cpp', 'c', 'go', 'rs', 'png', 'jpg', 'jpeg'],
            help="Supported formats: PDF, Word, PowerPoint, Text, Code files, Images"
        )
        
        # Chat input
        user_input = st.text_area(
            "Type your message here...",
            placeholder="Ask me to create a blog post, process a document, or just chat!",
            height=100
        )
        
        # Send button
        col_send1, col_send2, col_send3 = st.columns([1, 1, 2])
        
        with col_send1:
            if st.button("💬 Send Message", type="primary"):
                if user_input.strip() or uploaded_file:
                    # Add user message to chat
                    st.session_state.messages.append({
                        "role": "user",
                        "content": user_input,
                        "timestamp": time.time(),
                        "file": uploaded_file.name if uploaded_file else None
                    })
                    
                    # Process message
                    if st.session_state.chatbot:
                        # Run async function
                        response = asyncio.run(process_chat_message(
                            user_input, 
                            uploaded_file.read() if uploaded_file else None,
                            uploaded_file.name if uploaded_file else None
                        ))
                        
                        # Add bot response to chat
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response,
                            "timestamp": time.time()
                        })
                        
                        st.rerun()
                    else:
                        st.error("❌ Chatbot not initialized. Please initialize the system first.")
                else:
                    st.warning("⚠️ Please enter a message or upload a file.")
        
        with col_send2:
            if st.button("📝 Generate Blog"):
                if user_input.strip():
                    if st.session_state.blog_workflow:
                        # Generate blog post
                        result = asyncio.run(generate_blog_post(user_input))
                        
                        if result["success"] and result["blog_post"]:
                            blog_content = f"""
**Blog Post Generated Successfully!**

**Title:** {result["blog_post"].title}

**Content:**
{result["blog_post"].content}

**Hashtags:** {', '.join(result["blog_post"].hashtags)}

**Quality Score:** {result["quality_score"]}/10
**Iterations:** {result["iterations"]}
                            """
                            
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": blog_content,
                                "timestamp": time.time()
                            })
                            st.rerun()
                        else:
                            st.error(f"❌ Blog generation failed: {result['error']}")
                    else:
                        st.error("❌ Blog workflow not initialized. Please initialize the system first.")
                else:
                    st.warning("⚠️ Please enter content for blog generation.")
    
    with col2:
        st.subheader("📊 Quick Actions")
        
        # Quick blog generation
        st.markdown("**Quick Blog Generation**")
        quick_content = st.text_area(
            "Enter content for quick blog:",
            placeholder="e.g., AI trends in 2024...",
            height=100
        )
        
        if st.button("⚡ Quick Blog"):
            if quick_content.strip() and st.session_state.blog_workflow:
                with st.spinner("Generating quick blog..."):
                    result = asyncio.run(generate_blog_post(quick_content))
                    
                    if result["success"] and result["blog_post"]:
                        st.success("✅ Blog generated!")
                        st.markdown(f"**{result['blog_post'].title}**")
                        st.markdown(result["blog_post"].content[:200] + "...")
                        st.markdown(f"**Quality:** {result['quality_score']}/10")
                    else:
                        st.error(f"❌ Failed: {result['error']}")
            else:
                st.warning("⚠️ Enter content and ensure system is initialized")
        
        # System information
        st.subheader("ℹ️ System Info")
        st.markdown("""
        **Features:**
        - 🤖 Conversational AI chatbot
        - 📝 AI-powered blog generation
        - 📁 Multi-format document processing
        - 🔍 LangSmith tracing & monitoring
        - 💬 Interactive chat interface
        
        **Supported File Types:**
        - Documents: PDF, Word, PowerPoint
        - Code: Python, JavaScript, Java, C++, Go, Rust
        - Images: PNG, JPG, JPEG
        - Text: TXT files
        """)
        
        # LangSmith dashboard link
        if st.session_state.langsmith_ready:
            st.markdown("**🔍 Monitoring:**")
            st.markdown("[View LangSmith Dashboard](https://smith.langchain.com)")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "LinkedIn Blog AI Assistant | Powered by LangChain, Groq, and Gemini"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    # Initialize components on startup
    if not any([st.session_state.chatbot, st.session_state.blog_workflow, st.session_state.ingestion_processor]):
        initialize_components()
    
    main()
