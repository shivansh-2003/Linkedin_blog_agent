#!/usr/bin/env python3
"""
Interactive LinkedIn Blog Chatbot

Features:
- Conversational interface with memory
- File upload and processing
- Blog generation with human feedback loop
- Intent recognition and context awareness
"""

import os
import sys
import asyncio
import time
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from chatbot.chatbot_orchastrator import (
    ChatbotOrchestrator, create_chatbot_session, get_welcome_message
)
from chatbot.config import ChatbotConfig, ChatStage

class InteractiveChatbot:
    """Interactive terminal-based chatbot interface"""
    
    def __init__(self):
        self.bot: Optional[ChatbotOrchestrator] = None
        self.running = False
    
    def start_interactive_session(self):
        """Start interactive chatbot session"""
        print("=" * 70)
        print("🚀 LINKEDIN BLOG CREATION CHATBOT")
        print("=" * 70)
        
        # Check API keys
        if not self._check_requirements():
            return
        
        # Create bot session
        self.bot = create_chatbot_session()
        self.running = True
        
        # Welcome message
        welcome_msg = get_welcome_message()
        print(f"\n{ChatbotConfig.CHATBOT_NAME}: {welcome_msg}")
        
        # Start conversation loop
        asyncio.run(self._conversation_loop())
    
    async def _conversation_loop(self):
        """Main conversation loop"""
        print(f"\n{ChatbotConfig.CHATBOT_NAME}: What would you like to create a LinkedIn post about?")
        print("💡 Tip: You can type 'help' for assistance, 'upload <filepath>' for files, or 'quit' to exit\n")
        
        while self.running:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    await self._handle_quit()
                    break
                
                elif user_input.lower() == 'help':
                    await self._handle_help()
                    continue
                
                elif user_input.lower() == 'status':
                    await self._handle_status()
                    continue
                
                elif user_input.lower().startswith('upload '):
                    await self._handle_file_upload(user_input)
                    continue
                
                elif user_input.lower() == 'clear':
                    await self._handle_clear()
                    continue
                
                # Show typing indicator
                print(f"{ChatbotConfig.CHATBOT_NAME}: ⌨️  Thinking...")
                
                # Process with bot
                response = await self.bot.process_user_input(user_input)
                
                # Display response with typing effect
                await self._display_response(response)
                
            except KeyboardInterrupt:
                print(f"\n\n{ChatbotConfig.CHATBOT_NAME}: Goodbye! 👋")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print(f"{ChatbotConfig.CHATBOT_NAME}: Something went wrong, but let's continue!")
    
    async def _handle_file_upload(self, command: str):
        """Handle file upload command"""
        try:
            parts = command.split(' ', 1)
            if len(parts) < 2:
                print(f"{ChatbotConfig.CHATBOT_NAME}: Please specify a file path: upload <filepath>")
                return
            
            file_path = parts[1].strip().strip('"\'')
            
            if not os.path.exists(file_path):
                print(f"{ChatbotConfig.CHATBOT_NAME}: File not found: {file_path}")
                return
            
            print(f"{ChatbotConfig.CHATBOT_NAME}: ⌨️  Processing your file...")
            response = await self.bot.process_user_input(
                f"Please process this file: {file_path}", 
                file_path=file_path
            )
            
            await self._display_response(response)
            
        except Exception as e:
            print(f"{ChatbotConfig.CHATBOT_NAME}: Error processing file: {e}")
    
    async def _handle_help(self):
        """Handle help command"""
        help_text = f"""
🤖 {ChatbotConfig.CHATBOT_NAME} Help

**Commands:**
• help - Show this help message
• upload <filepath> - Upload and process a file
• status - Show current session status
• clear - Start a new conversation
• quit/exit - End the session

**File Support:**
• PDFs, Word documents (.docx)
• PowerPoint presentations (.pptx)
• Code files (.py, .js, .java, etc.)
• Text files (.txt, .md)
• Images (.jpg, .png, etc.)

**Usage Tips:**
• Just describe what you want to write about
• Upload files for automatic content extraction
• Give specific feedback to improve drafts
• Say "approve" when you're happy with a draft

**Current Session:** {self.bot.session_id}
**Current Stage:** {self.bot.current_stage.replace('_', ' ').title()}
"""
        print(help_text)
    
    async def _handle_status(self):
        """Handle status command"""
        if self.bot:
            summary = self.bot.get_session_summary()
            print(f"\n📊 Session Status: {summary}")
            
            # Show recent messages
            recent = self.bot.memory.get_recent_messages(3)
            if recent:
                print("\n💬 Recent conversation:")
                for msg in recent:
                    timestamp = msg.timestamp.strftime("%H:%M")
                    sender = "You" if msg.message_type.value == "user" else ChatbotConfig.CHATBOT_NAME
                    content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
                    print(f"   [{timestamp}] {sender}: {content}")
        else:
            print("No active session")
    
    async def _handle_clear(self):
        """Handle clear/new conversation command"""
        print(f"{ChatbotConfig.CHATBOT_NAME}: Starting a fresh conversation! 🔄")
        self.bot = create_chatbot_session()
        welcome_msg = get_welcome_message()
        print(f"\n{ChatbotConfig.CHATBOT_NAME}: {welcome_msg}")
    
    async def _handle_quit(self):
        """Handle quit command"""
        if self.bot:
            # Export conversation summary
            summary = self.bot.export_conversation()
            print(f"\n📊 Session Summary:")
            print(f"   • Messages exchanged: {summary['total_messages']}")
            print(f"   • Blogs created: {summary['blogs_generated']}")
            print(f"   • Session duration: {summary['created_at'][:10]}")
        
        print(f"\n{ChatbotConfig.CHATBOT_NAME}: Thank you for using the LinkedIn Blog Creator! 🚀")
        print("Your session has been saved. Come back anytime to create more amazing content!")
        self.running = False
    
    async def _display_response(self, response: str):
        """Display bot response with typing effect"""
        print(f"\r{ChatbotConfig.CHATBOT_NAME}: ", end="", flush=True)
        
        # Simple typing effect for better UX
        if len(response) > 100:
            # For long responses, show immediately
            print(response)
        else:
            # For short responses, simulate typing
            for char in response:
                print(char, end="", flush=True)
                if char in '.!?':
                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(0.02)
            print()  # New line at end
    
    def _check_requirements(self) -> bool:
        """Check if required API keys and dependencies are available"""
        missing_keys = []
        
        if not os.getenv("GROQ_API_KEY"):
            missing_keys.append("GROQ_API_KEY")
        
        if missing_keys:
            print("❌ Missing required environment variables:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\nPlease set your API keys in environment variables or .env file")
            print("Visit https://console.groq.com/ to get your Groq API key")
            return False
        
        print("✅ API keys configured")
        return True

class FileChatInterface:
    """File-based chat interface for programmatic use"""
    
    def __init__(self, session_id: str = None):
        self.bot = create_chatbot_session(session_id)
    
    async def process_message(self, message: str, file_path: str = None) -> str:
        """Process a single message and return response"""
        return await self.bot.process_user_input(message, file_path)
    
    async def process_file(self, file_path: str, requirements: str = None) -> str:
        """Process a file and optionally specify requirements"""
        message = f"Please process this file"
        if requirements:
            message += f" with these requirements: {requirements}"
        
        return await self.bot.process_user_input(message, file_path)
    
    def get_session_id(self) -> str:
        """Get current session ID"""
        return self.bot.session_id
    
    def export_session(self) -> dict:
        """Export session data"""
        return self.bot.export_conversation()

# Demo functions for testing

async def demo_text_input():
    """Demo with text input"""
    print("🔄 Demo: Text Input Processing")
    
    chat = FileChatInterface()
    
    demo_text = """
    Machine Learning in Healthcare: Transforming Patient Care
    
    The healthcare industry is experiencing a revolutionary transformation through machine learning 
    applications. From diagnostic imaging to drug discovery, ML algorithms are enhancing accuracy 
    and efficiency across medical practices.
    
    Key applications include:
    - Medical imaging analysis for faster diagnosis
    - Predictive analytics for patient outcomes
    - Drug discovery acceleration
    - Personalized treatment recommendations
    - Clinical decision support systems
    
    The future holds even more promise as ML models become more sophisticated and healthcare 
    data becomes more accessible.
    """
    
    response = await chat.process_message(
        f"Create a LinkedIn post about this content: {demo_text}"
    )
    
    print(f"Response: {response}")
    return chat.get_session_id()

async def demo_feedback_loop():
    """Demo feedback and refinement"""
    print("🔄 Demo: Feedback Loop")
    
    chat = FileChatInterface()
    
    # Initial generation
    response1 = await chat.process_message(
        "Create a LinkedIn post about the importance of data privacy in the digital age"
    )
    print(f"Initial response: {response1[:200]}...")
    
    # Provide feedback
    response2 = await chat.process_message(
        "Make it more engaging and add some statistics about data breaches"
    )
    print(f"Refined response: {response2[:200]}...")
    
    # Approve
    response3 = await chat.process_message("This looks great, I approve it!")
    print(f"Final response: {response3}")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LinkedIn Blog Creation Chatbot")
    parser.add_argument("--demo", choices=["text", "feedback"], help="Run demo mode")
    parser.add_argument("--file", help="Process specific file")
    parser.add_argument("--session-id", help="Resume specific session")
    
    args = parser.parse_args()
    
    if args.demo == "text":
        asyncio.run(demo_text_input())
    elif args.demo == "feedback":
        asyncio.run(demo_feedback_loop())
    elif args.file:
        chat = FileChatInterface(args.session_id)
        response = asyncio.run(chat.process_file(args.file))
        print(f"Response: {response}")
    else:
        # Interactive mode
        chatbot = InteractiveChatbot()
        chatbot.start_interactive_session()

if __name__ == "__main__":
    main()