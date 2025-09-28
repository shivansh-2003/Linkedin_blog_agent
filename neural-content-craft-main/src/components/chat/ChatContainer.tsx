import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Settings, BookOpen, HelpCircle, RotateCcw, Volume2, VolumeX, Maximize2, Minimize2 } from 'lucide-react';
import MessageBubble from './MessageBubble';
import TypingIndicator from './TypingIndicator';
import FileUpload from './FileUpload';
import MessageInput from './MessageInput';
import { useToast } from '@/components/ui/use-toast';
import { 
  useKeyboardNavigation, 
  useScreenReaderAnnouncements, 
  useFocusManagement,
  useReducedMotion,
  AccessibilityAnnouncements,
  SkipLinks,
  FocusIndicator 
} from './AccessibilityEnhancements';
import { apiService, BlogResponse } from '@/services/api';

interface Message {
  id: string;
  type: 'user' | 'ai' | 'system';
  content: string;
  timestamp: Date;
  metadata?: {
    files?: File[];
    blogPost?: any;
    processing?: boolean;
    qualityScore?: number;
    isError?: boolean;
    errorMessage?: string;
    analysisResults?: {
      keyInsights: number;
      focusArea: string;
      audience: string;
    };
  };
}

interface ChatSettings {
  soundEnabled: boolean;
  autoScroll: boolean;
  showTimestamps: boolean;
  compactMode: boolean;
}

const ChatContainer: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'ai',
      content: "Hello! I'm BlogAI, your LinkedIn content assistant. I can help transform any content into engaging professional posts. What would you like to create?",
      timestamp: new Date(),
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [aiStatus, setAiStatus] = useState<'online' | 'processing' | 'offline'>('online');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [settings, setSettings] = useState<ChatSettings>({
    soundEnabled: true,
    autoScroll: true,
    showTimestamps: true,
    compactMode: false,
  });
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  // Accessibility hooks
  useKeyboardNavigation();
  const { announcements, announce } = useScreenReaderAnnouncements();
  const { saveFocus, restoreFocus } = useFocusManagement();
  const prefersReducedMotion = useReducedMotion();

  // Initialize chat session
  const initializeChatSession = useCallback(async () => {
    if (!chatSessionId) {
      try {
        const session = await apiService.startChatSession();
        setChatSessionId(session.session_id);
        announce(`Chat session started. Session ID: ${session.session_id}`);
      } catch (error) {
        toast({
          title: "Failed to Start Chat",
          description: error instanceof Error ? error.message : "Could not connect to chat service",
          variant: "destructive",
        });
      }
    }
  }, [chatSessionId, announce, toast]);

  const scrollToBottom = useCallback(() => {
    if (settings.autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [settings.autoScroll]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Keyboard shortcuts
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
          case '/':
            e.preventDefault();
            toast({
              title: "Keyboard Shortcuts",
              description: "Ctrl+K: New Chat, Ctrl+F: Fullscreen, Ctrl+/: Help",
            });
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [isFullscreen, toast]);

  const handleSendMessage = useCallback(async (content: string, files?: File[]) => {
    // Initialize chat session if needed
    await initializeChatSession();

    const newMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content,
      timestamp: new Date(),
      metadata: { files }
    };

    setMessages(prev => [...prev, newMessage]);
    setIsTyping(true);
    setIsProcessing(true);
    setAiStatus('processing');

    // Play sound if enabled
    if (settings.soundEnabled) {
      const audio = new Audio('/sounds/message-sent.mp3');
      audio.volume = 0.3;
      audio.play().catch(() => {}); // Ignore errors if audio file doesn't exist
    }

    try {
      let response: string;
      let blogContext: any = null;

      if (files && files.length > 0) {
        // Generate blog from uploaded files
        const blogResponse = await apiService.generateBlogFromFile(
          files[0], // Use first file for now
          "General professional audience",
          "Professional and engaging",
          3
        );

        if (blogResponse.success && blogResponse.blog_post) {
          response = `I've analyzed your file and generated a LinkedIn post for you!\n\n**Title:** ${blogResponse.blog_post.title}\n\n**Hook:** ${blogResponse.blog_post.hook}\n\n**Content:** ${blogResponse.blog_post.content}\n\n**Call to Action:** ${blogResponse.blog_post.call_to_action}\n\n**Hashtags:** ${blogResponse.blog_post.hashtags.join(' ')}`;
          blogContext = blogResponse.blog_post;
        } else {
          response = `I encountered an issue processing your file: ${blogResponse.error || 'Unknown error occurred'}`;
        }
      } else if (content.trim()) {
        // Send message to chatbot
        const chatResponse = await apiService.sendChatMessage(content, chatSessionId || undefined);
        response = chatResponse.response;
        blogContext = chatResponse.blog_context;
      } else {
        response = "Please provide some content or upload a file for me to analyze.";
      }

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: response,
        timestamp: new Date(),
        metadata: {
          analysisResults: blogContext,
          isError: false
        }
      };

      setMessages(prev => [...prev, aiResponse]);

      // Play AI response sound
      if (settings.soundEnabled) {
        const audio = new Audio('/sounds/ai-response.mp3');
        audio.volume = 0.2;
        audio.play().catch(() => {});
      }

      announce("AI response received");

    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: `I encountered an error: ${error instanceof Error ? error.message : 'Unknown error occurred'}. Please try again.`,
        timestamp: new Date(),
        metadata: {
          isError: true,
          errorMessage: error instanceof Error ? error.message : 'Unknown error'
        }
      };

      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to process your request",
        variant: "destructive",
      });

      announce("Error occurred while processing your request");
    } finally {
      setIsTyping(false);
      setIsProcessing(false);
      setAiStatus('online');
    }
  }, [initializeChatSession, chatSessionId, settings.soundEnabled, announce, toast]);

  const handleFileUpload = useCallback((files: File[]) => {
    const fileMessage: Message = {
      id: Date.now().toString(),
      type: 'system',
      content: `Uploaded ${files.length} file${files.length > 1 ? 's' : ''} for processing`,
      timestamp: new Date(),
      metadata: { files, processing: true }
    };

    setMessages(prev => [...prev, fileMessage]);
    handleSendMessage('', files);

    toast({
      title: "Files Uploaded",
      description: `${files.length} file${files.length > 1 ? 's' : ''} uploaded successfully`,
    });
  }, [handleSendMessage, toast]);

  const handleNewChat = useCallback(() => {
    setMessages([
      {
        id: '1',
        type: 'ai',
        content: "Hello! I'm BlogAI, your LinkedIn content assistant. I can help transform any content into engaging professional posts. What would you like to create?",
        timestamp: new Date(),
      }
    ]);
    
    announce("New chat started. Ready for a fresh conversation!");
    
    toast({
      title: "New Chat Started",
      description: "Ready for a fresh conversation!",
    });
  }, [toast, announce]);

  const toggleSettings = (key: keyof ChatSettings) => {
    setSettings(prev => ({
      ...prev,
      [key]: !prev[key]
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

  return (
    <div className={`flex flex-col bg-background-primary transition-all duration-300 ${
      isFullscreen ? 'fixed inset-0 z-50 h-screen' : 'h-screen'
    } ${prefersReducedMotion ? 'motion-safe' : ''}`}>
      {/* Skip Links */}
      <SkipLinks />
      
      {/* Accessibility Announcements */}
      <AccessibilityAnnouncements announcements={announcements} />
      
      {/* Chat Header */}
      <nav className="sticky top-0 z-10 bg-background-tertiary/95 backdrop-blur-md border-b border-border-primary" id="navigation">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 rounded-full bg-gradient-ai flex items-center justify-center">
                <span className="text-sm font-bold text-background-primary">AI</span>
              </div>
              <div>
                <h2 className="text-lg font-semibold text-text-primary">BlogAI Assistant</h2>
                <div className="flex items-center space-x-2">
                  {getStatusIndicator()}
                  <span className="text-sm text-text-secondary">{getStatusText()}</span>
                  {isTyping && (
                    <span className="text-xs text-accent-primary animate-pulse">• Processing</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-1">
            {/* Sound Toggle */}
            <button
              onClick={() => toggleSettings('soundEnabled')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                settings.soundEnabled 
                  ? 'text-accent-primary bg-accent-primary/10' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated'
              }`}
              aria-label="Toggle Sound"
            >
              {settings.soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
            </button>

            {/* Settings */}
            <button
              onClick={() => toggleSettings('compactMode')}
              className={`p-2 rounded-lg transition-all duration-200 ${
                settings.compactMode 
                  ? 'text-accent-primary bg-accent-primary/10' 
                  : 'text-text-secondary hover:text-text-primary hover:bg-background-elevated'
              }`}
              aria-label="Compact Mode"
            >
              <Settings className="w-5 h-5" />
            </button>

            {/* Chat History */}
            <button
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              aria-label="Chat History"
            >
              <BookOpen className="w-5 h-5" />
            </button>

            {/* Help */}
            <button
              onClick={() => toast({
                title: "Help & Shortcuts",
                description: "Ctrl+K: New Chat, Ctrl+F: Fullscreen, Ctrl+/: Help. Use the settings to customize your experience!",
              })}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              aria-label="Help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>

            {/* Fullscreen Toggle */}
            <button
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              aria-label={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}
            >
              {isFullscreen ? <Minimize2 className="w-5 h-5" /> : <Maximize2 className="w-5 h-5" />}
            </button>

            {/* New Chat */}
            <button
              onClick={handleNewChat}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-background-elevated rounded-lg transition-all duration-200"
              aria-label="New Chat"
            >
              <RotateCcw className="w-5 h-5" />
            </button>
          </div>
        </div>
      </nav>

      {/* Messages Area */}
      <main 
        ref={chatContainerRef}
        className={`flex-1 overflow-y-auto mobile-scroll ${
          settings.compactMode ? 'p-4 space-y-4' : 'p-6 space-y-6'
        }`}
        role="log"
        aria-live="polite"
        aria-label="Chat conversation"
        id="main-content"
        tabIndex={-1}
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

      {/* File Upload Area */}
      <div className={settings.compactMode ? "px-4" : "px-6"}>
        <FileUpload 
          onFileUpload={handleFileUpload}
        />
      </div>

      {/* Message Input */}
      <FocusIndicator>
        <div className={`bg-background-secondary border-t border-border-primary ${
          settings.compactMode ? 'p-4' : 'p-6'
        }`} id="chat-input">
          <MessageInput 
            onSendMessage={handleSendMessage} 
            disabled={isTyping}
            compactMode={settings.compactMode}
          />
        </div>
      </FocusIndicator>
    </div>
  );
};

export default ChatContainer;