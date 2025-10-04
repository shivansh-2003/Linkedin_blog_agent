import React, { useState, useRef, useEffect, useCallback } from 'react';
import { RotateCcw, Settings, Maximize2, Minimize2, AlertCircle, Sparkles } from 'lucide-react';
import MessageBubble, { Message } from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import MessageInput from './MessageInput';
import { useToast } from '@/components/ui/use-toast';
import { apiService } from '@/services/api';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface ChatSettings {
  autoScroll: boolean;
  showTimestamps: boolean;
  compactMode: boolean;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

const ChatContainer: React.FC = () => {
  // ==========================================================================
  // STATE
  // ==========================================================================

  const [messages, setMessages] = useState<Message[]>([]);

  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState<'online' | 'processing' | 'offline'>('online');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [settings, setSettings] = useState<ChatSettings>({
    autoScroll: true,
    showTimestamps: true,
    compactMode: false,
  });
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  // Feedback modal state
  const [feedbackModalOpen, setFeedbackModalOpen] = useState(false);
  const [feedbackText, setFeedbackText] = useState('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // ==========================================================================
  // INITIALIZATION
  // ==========================================================================

  useEffect(() => {
    initializeChatSession();
  }, []);

  const initializeChatSession = async () => {
    try {
      console.log('🔄 Initializing chat session...');
      setAiStatus('processing');

      // Health check first
      const health = await apiService.healthCheck();
      console.log('✅ Backend health check passed:', health);

      const session = await apiService.startChatSession();
      setChatSessionId(session.session_id);
      setConnectionError(null);
      setAiStatus('online');

      console.log('✅ Chat session initialized:', session.session_id);
      
      // Add welcome message
      addMessage({
        type: 'ai',
        content: `👋 Hello! I'm your LinkedIn Blog AI Assistant.

I can help you:
• Transform files into engaging LinkedIn posts
• Analyze and extract key insights from your content
• Generate professional posts with quality scoring

To get started:
1. Upload a file (PDF, Word, PowerPoint, Code, Images, etc.)
2. Or just tell me what you'd like to create

What would you like to work on today?`,
      });
    } catch (error) {
      console.error('❌ Failed to initialize chat:', error);
      setAiStatus('offline');

      const errorMessage = error instanceof Error ? error.message : 'Unable to connect to server';
      setConnectionError(errorMessage);

      addMessage({
        type: 'error',
        content: `⚠️ **Connection Error**\n\n${errorMessage}\n\nPlease check:\n• Your internet connection\n• The backend server is running\n• CORS is properly configured`,
      });

      toast({
        title: 'Connection Failed',
        description: 'Unable to connect to the backend. Please check the console for details.',
        variant: 'destructive',
      });
    }
  };

  // ==========================================================================
  // SCROLL MANAGEMENT
  // ==========================================================================

  const scrollToBottom = useCallback(() => {
    if (settings.autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [settings.autoScroll]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // ==========================================================================
  // KEYBOARD SHORTCUTS
  // ==========================================================================

  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        switch (e.key) {
          case 'k':
            e.preventDefault();
            handleNewChat();
            break;
          case 'f':
            e.preventDefault();
            setIsFullscreen(!isFullscreen);
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isFullscreen]);

  // ==========================================================================
  // MESSAGE HELPERS
  // ==========================================================================

  const addMessage = (msg: Partial<Message> & { id?: string }) => {
    const newMessage: Message = {
      id: msg.id || Date.now().toString(),
      type: msg.type || 'ai',
      content: msg.content || '',
      timestamp: new Date(),
      metadata: msg.metadata,
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  // ==========================================================================
  // TEXT MESSAGE HANDLER
  // ==========================================================================

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      // Check session
      if (!chatSessionId) {
        toast({
          title: 'No Active Session',
          description: 'Initializing a new session...',
        });
        await initializeChatSession();
        return;
      }

      // Add user message
      addMessage({
        type: 'user',
        content,
      });

      setIsTyping(true);
      setAiStatus('processing');

      try {
        console.log('📤 Sending message:', content);
        const response = await apiService.sendMessage(content, chatSessionId);

        console.log('📥 Received response:', response);

        // Add AI response
        addMessage({
          type: 'ai',
          content: response.response,
          metadata: {
            blogPost: response.blog_context?.current_draft,
            qualityScore: response.blog_context?.current_draft?.engagement_score,
            onApprove: handleApproveBlog,
            onRequestChanges: handleRequestChanges,
          },
        });

        setAiStatus('online');
      } catch (error) {
        console.error('❌ Message error:', error);

        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';

        addMessage({
          type: 'error',
          content: `❌ **Error Processing Message**\n\n${errorMessage}\n\nPlease try again or start a new session.`,
          metadata: {
            isError: true,
            errorMessage,
          },
        });

        toast({
          title: 'Message Failed',
          description: errorMessage,
          variant: 'destructive',
        });

        setAiStatus('online');
      } finally {
        setIsTyping(false);
      }
    },
    [chatSessionId, toast]
  );

  // ==========================================================================
  // FILE UPLOAD HANDLER
  // ==========================================================================

  const handleFileUpload = useCallback(
    async (files: File[]) => {
      if (files.length === 0) return;

      // Check session
      if (!chatSessionId) {
        toast({
          title: 'No Active Session',
          description: 'Initializing a new session...',
        });
        await initializeChatSession();
        return;
      }

      // Add file upload message with unique ID
      const processingMessageId = `processing-${Date.now()}`;
      addMessage({
        id: processingMessageId,
        type: 'system',
        content: `📎 Uploading ${files.length} file${files.length > 1 ? 's' : ''}...\n\n${files
          .map((f) => `• ${f.name} (${(f.size / 1024 / 1024).toFixed(2)}MB)`)
          .join('\n')}`,
        metadata: { files, processing: true },
      });

      setIsTyping(true);
      setAiStatus('processing');

      try {
        // Process each file through chatbot session for proper context
        for (const file of files) {
          console.log(`📤 Processing file through chat session: ${file.name}`);

          // Step 1: Upload and ingest the file
          const ingestionResult = await apiService.uploadFile(file);
          console.log('✅ File ingested:', ingestionResult);

          // Step 2: Send extracted content to chatbot with explicit blog creation request
          // Use truncated content to avoid token limits - avoid file-related keywords!
          const contentPreview = ingestionResult.extracted_content.raw_text.substring(0, 2000);
          const blogCreationMessage = `Write a professional LinkedIn post about:\n\n${contentPreview}\n\nKey themes: ${ingestionResult.key_insights.slice(0, 3).join(', ')}`;
          
          const chatResponse = await apiService.sendMessage(blogCreationMessage, chatSessionId);
          console.log('✅ Chat response received:', chatResponse);
          console.log('📊 Blog context:', chatResponse.blog_context);
          console.log('📝 Current draft:', chatResponse.blog_context?.current_draft);

          // Step 3: Remove processing message and display the AI response with blog post
          setMessages((prev) => prev.filter((m) => m.id !== processingMessageId));
          
          // Check if we have a blog post
          const hasBlog = chatResponse.blog_context?.current_draft;
          console.log(`${hasBlog ? '✅' : '❌'} Has blog post:`, hasBlog);
          
          addMessage({
            type: 'ai',
            content: chatResponse.response,
            metadata: {
              blogPost: hasBlog,
              qualityScore: hasBlog?.engagement_score || 8.0,
              onApprove: handleApproveBlog,
              onRequestChanges: handleRequestChanges,
              onRegenerate: () => handleFileUpload([file]),
            },
          });
        }

        toast({
          title: '✅ Files Processed',
          description: `Successfully analyzed ${files.length} file${files.length > 1 ? 's' : ''}`,
        });

        setAiStatus('online');
      } catch (error) {
        // Remove processing message on error
        setMessages((prev) => prev.filter((m) => m.id !== processingMessageId));
        
        console.error('❌ File upload error:', error);

        const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';

        addMessage({
          type: 'error',
          content: `❌ **File Upload Failed**\n\n${errorMessage}\n\nPlease check:\n• File size is under 50MB\n• File format is supported\n• Network connection is stable`,
          metadata: {
            isError: true,
            errorMessage,
          },
        });

        toast({
          title: 'Upload Failed',
          description: errorMessage,
          variant: 'destructive',
        });

        setAiStatus('online');
      } finally {
        setIsTyping(false);
      }
    },
    [chatSessionId, toast]
  );

  // ==========================================================================
  // BLOG POST ACTIONS
  // ==========================================================================

  const handleRequestChanges = () => {
    setFeedbackModalOpen(true);
  };

  const handleSubmitFeedback = async () => {
    if (!feedbackText.trim() || !chatSessionId) return;

    setFeedbackModalOpen(false);
    setIsTyping(true);
    setAiStatus('processing');

    try {
      const response = await apiService.submitFeedback(chatSessionId, feedbackText, 'specific');

      addMessage({
        type: 'ai',
        content: response.response,
        metadata: {
          blogPost: response.blog_context?.current_draft,
          qualityScore: response.blog_context?.current_draft?.engagement_score,
          onApprove: handleApproveBlog,
          onRequestChanges: handleRequestChanges,
        },
      });

      setFeedbackText('');
      toast({
        title: 'Feedback Submitted',
        description: 'AI is refining your post...',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit feedback';
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsTyping(false);
      setAiStatus('online');
    }
  };

  const handleApproveBlog = async () => {
    if (!chatSessionId) return;

    try {
      const response = await apiService.approveBlog(chatSessionId, true, 'Approved for publication');

      addMessage({
        type: 'success',
        content: `✅ **Blog Post Approved!**\n\n🎉 ${response.response}\n\nYour post is ready for publication on LinkedIn!`,
      });

      toast({
        title: '✅ Blog Approved',
        description: 'Your post is ready to publish!',
      });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to approve blog';
      toast({
        title: 'Error',
        description: errorMessage,
        variant: 'destructive',
      });
    }
  };

  // ==========================================================================
  // NEW CHAT
  // ==========================================================================

  const handleNewChat = useCallback(async () => {
    // Clear messages first
    setMessages([]);

    // Reinitialize session (will add welcome message)
    await initializeChatSession();

    toast({
      title: 'New Chat Started',
      description: 'Ready for a fresh conversation!',
    });
  }, [toast, initializeChatSession]);

  // ==========================================================================
  // UI HELPERS
  // ==========================================================================

  const toggleSettings = (key: keyof ChatSettings) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const getStatusIndicator = () => {
    switch (aiStatus) {
      case 'online':
        return <div className="w-2 h-2 bg-accent-success rounded-full animate-pulse" />;
      case 'processing':
        return <div className="w-2 h-2 bg-accent-warning rounded-full animate-spin" />;
      case 'offline':
        return <div className="w-2 h-2 bg-accent-error rounded-full" />;
    }
  };

  const getStatusText = () => {
    switch (aiStatus) {
      case 'online':
        return 'Online';
      case 'processing':
        return 'Processing...';
      case 'offline':
        return 'Offline';
    }
  };

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <div
      className={`flex flex-col bg-background-primary transition-all duration-300 ${
        isFullscreen ? 'fixed inset-0 z-50 h-screen' : 'h-screen'
      }`}
    >
      {/* Header */}
      <nav className="sticky top-0 z-10 bg-background-tertiary/95 backdrop-blur-md border-b border-border-primary">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-accent-primary via-accent-secondary to-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-background-primary" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-text-primary">BlogAI Assistant</h2>
                <div className="flex items-center space-x-2">
                  {getStatusIndicator()}
                  <span className="text-sm text-text-secondary">{getStatusText()}</span>
                  {isTyping && (
                    <span className="text-xs text-accent-primary animate-pulse">• Processing</span>
                  )}
                  {connectionError && (
                    <span className="text-xs text-accent-error">• Connection Issue</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => toggleSettings('compactMode')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                settings.compactMode
                  ? 'text-accent-primary bg-accent-primary/10'
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated'
              }`}
              title="Compact Mode"
            >
              <Settings className="w-5 h-5" />
            </button>

            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
            >
              {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
            </button>

            <button
              onClick={handleNewChat}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              title="New Chat (Ctrl+K)"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Connection Error Banner */}
        {connectionError && (
          <div className="px-6 py-3 bg-accent-error/10 border-t border-accent-error/30">
            <div className="flex items-center space-x-2 text-sm">
              <AlertCircle className="w-4 h-4 text-accent-error" />
              <span className="text-accent-error font-medium">Connection Error:</span>
              <span className="text-text-secondary">{connectionError}</span>
              <button
                onClick={initializeChatSession}
                className="ml-auto px-3 py-1 bg-accent-error/20 text-accent-error rounded hover:bg-accent-error/30 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Messages Area */}
      <main
        className={`flex-1 overflow-y-auto mobile-scroll ${
          settings.compactMode ? 'p-4' : 'p-6'
        }`}
        role="log"
        aria-live="polite"
        aria-label="Chat conversation"
      >
        {messages.map((message) => (
          <MessageBubble
            key={message.id}
            message={message}
            compactMode={settings.compactMode}
            showTimestamps={settings.showTimestamps}
          />
        ))}

        {isTyping && <TypingIndicator compactMode={settings.compactMode} />}

        <div ref={messagesEndRef} />
      </main>

      {/* Message Input */}
      <div
        className={`bg-background-secondary border-t border-border-primary ${
          settings.compactMode ? 'p-4' : 'p-6'
        }`}
      >
        <MessageInput
          onSendMessage={handleSendMessage}
          onFileUpload={handleFileUpload}
          disabled={isTyping || aiStatus === 'offline'}
          compactMode={settings.compactMode}
          placeholder={aiStatus === 'offline' ? 'Reconnecting...' : 'Type your message...'}
        />
      </div>

      {/* Feedback Modal */}
      <Dialog open={feedbackModalOpen} onOpenChange={setFeedbackModalOpen}>
        <DialogContent className="bg-background-tertiary border-border-primary">
          <DialogHeader>
            <DialogTitle className="text-text-primary">✏️ Request Changes</DialogTitle>
            <DialogDescription className="text-text-secondary">
              Tell the AI how you'd like to improve the blog post
            </DialogDescription>
          </DialogHeader>
          <Textarea
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            placeholder="E.g., Make it more technical, add statistics, improve the hook..."
            className="min-h-[120px] bg-background-elevated border-border-secondary text-text-primary"
          />
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setFeedbackModalOpen(false)}
              className="border-border-secondary"
            >
              Cancel
            </Button>
            <Button
              onClick={handleSubmitFeedback}
              disabled={!feedbackText.trim()}
              className="bg-gradient-to-r from-accent-primary to-primary"
            >
              Submit Feedback
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default ChatContainer;
