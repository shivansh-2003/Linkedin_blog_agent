import os
from dotenv import load_dotenv
from langsmith import Client
from langsmith import traceable

# Load environment variables
load_dotenv()

# Initialize LangSmith client - this is your connection to the monitoring system
langsmith_client = Client()

# Configure environment variables for automatic tracing
# These settings tell LangChain to automatically send traces to LangSmith
os.environ["LANGSMITH_TRACING"] = "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "linkedin-blog-agent")



def trace_step(step_name, run_type="chain"):
    """
    Custom decorator to trace individual steps in your pipeline
    
    Think of this as a way to label and track specific functions
    so you can see them clearly in your LangSmith dashboard
    """
    # Map custom run types to valid LangSmith run types
    valid_run_types = {
        "workflow": "chain",  # Map workflow to chain
        "llm": "llm",
        "tool": "tool",
        "chain": "chain"
    }
    
    mapped_run_type = valid_run_types.get(run_type, "chain")
    
    def decorator(func):
        return traceable(run_type=mapped_run_type, name=step_name)(func)
    return decorator

# Helper function to check if LangSmith is properly configured
def verify_langsmith_setup():
    """Verify that LangSmith is properly configured"""
    try:
        # Test the connection by creating a simple run
        langsmith_client.create_run(
            name="setup_verification",
            run_type="tool",
            inputs={"test": "LangSmith setup"},
            outputs={"status": "success"}
        )
        print("✅ LangSmith setup verified successfully!")
        return True
    except Exception as e:
        print(f"❌ LangSmith setup failed: {e}")
        return False