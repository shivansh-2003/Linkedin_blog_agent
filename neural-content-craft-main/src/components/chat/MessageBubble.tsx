import React from 'react';
import { User, Bot, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import BlogPostPreview from './BlogPostPreview';

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

interface MessageBubbleProps {
  message: Message;
  compactMode?: boolean;
  showTimestamps?: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, compactMode = false, showTimestamps = true }) => {
  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    
    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;
    
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    
    return timestamp.toLocaleDateString();
  };

  const renderFilePreview = (files: File[]) => (
    <div className={`space-y-2 ${compactMode ? 'mt-2' : 'mt-3'}`}>
      {files.map((file, index) => (
        <div
          key={index}
          className={`flex items-center ${
            compactMode ? 'p-2' : 'p-3'
          } bg-background-elevated rounded-lg border border-border-secondary`}
        >
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className={compactMode ? "text-lg" : "text-2xl"}>📄</span>
              <div>
                <p className={`font-medium text-text-primary ${compactMode ? 'text-xs' : 'text-sm'}`}>
                  {file.name}
                </p>
                <p className="text-xs text-text-tertiary">
                  {(file.size / 1024 / 1024).toFixed(2)} MB • {file.type || 'Unknown type'}
                </p>
              </div>
            </div>
          </div>
          {message.metadata?.processing ? (
            <div className="flex items-center space-x-2 text-accent-warning">
              <Clock className={`animate-spin ${compactMode ? 'w-3 h-3' : 'w-4 h-4'}`} />
              <span className="text-xs">Processing...</span>
            </div>
          ) : (
            <CheckCircle className={`text-accent-success ${compactMode ? 'w-4 h-4' : 'w-5 h-5'}`} />
          )}
        </div>
      ))}
    </div>
  );

  const renderAnalysisResults = (results: Message['metadata']['analysisResults']) => {
    if (!results) return null;
    
    return (
      <div className={`mt-3 p-3 bg-accent-success/10 border border-accent-success/30 rounded-lg ${
        compactMode ? 'text-xs' : 'text-sm'
      }`}>
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-accent-success">📊</span>
          <span className="font-medium text-text-primary">Analysis Complete</span>
        </div>
        <div className="space-y-1 text-text-secondary">
          <p>• {results.keyInsights} key insights extracted</p>
          <p>• Focus: {results.focusArea}</p>
          <p>• Target: {results.audience}</p>
        </div>
      </div>
    );
  };

  if (message.type === 'user') {
    return (
      <div className="flex justify-end animate-[slideInRight_0.3s_ease-out]">
        <div className={`max-w-[70%] space-y-2 ${compactMode ? 'space-y-1' : 'space-y-2'}`}>
          <div className="flex items-end space-x-2">
            <div className={`bg-gradient-to-r from-accent-primary to-primary ${
              compactMode ? 'p-3' : 'p-4'
            } rounded-2xl rounded-br-md`}>
              <p className={`text-background-primary font-medium ${compactMode ? 'text-sm' : ''}`}>
                {message.content}
              </p>
              {message.metadata?.files && renderFilePreview(message.metadata.files)}
            </div>
            <div className={`bg-background-elevated rounded-full flex items-center justify-center ${
              compactMode ? 'w-6 h-6' : 'w-8 h-8'
            }`}>
              <User className={`text-text-secondary ${compactMode ? 'w-3 h-3' : 'w-4 h-4'}`} />
            </div>
          </div>
          {showTimestamps && (
            <div className="text-right">
              <span className="text-xs text-text-muted">{formatTimestamp(message.timestamp)}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (message.type === 'system') {
    return (
      <div className="flex justify-center animate-[fadeIn_0.3s_ease-out]">
        <div className={`max-w-md ${
          compactMode ? 'p-2' : 'p-3'
        } bg-background-elevated border border-border-secondary rounded-lg`}>
          <div className="flex items-center space-x-2">
            <AlertCircle className={`text-accent-warning ${compactMode ? 'w-3 h-3' : 'w-4 h-4'}`} />
            <span className={`text-text-secondary ${compactMode ? 'text-xs' : 'text-sm'}`}>
              {message.content}
            </span>
          </div>
          {message.metadata?.files && renderFilePreview(message.metadata.files)}
        </div>
      </div>
    );
  }

  // AI message
  return (
    <div className="flex justify-start animate-[slideInLeft_0.3s_ease-out]">
      <div className={`max-w-[70%] space-y-2 ${compactMode ? 'space-y-1' : 'space-y-2'}`}>
        <div className="flex items-end space-x-2">
          <div className={`bg-gradient-ai rounded-full flex items-center justify-center ${
            compactMode ? 'w-6 h-6' : 'w-8 h-8'
          }`}>
            <Bot className={`text-background-primary ${compactMode ? 'w-3 h-3' : 'w-4 h-4'}`} />
          </div>
          <div className={`glass-card bg-background-tertiary/80 border border-accent-primary/20 ${
            compactMode ? 'p-3' : 'p-4'
          } rounded-2xl rounded-bl-md`}>
            <p className={`text-text-primary leading-relaxed ${compactMode ? 'text-sm' : ''}`}>
              {message.content}
            </p>
            
            {message.metadata?.analysisResults && renderAnalysisResults(message.metadata.analysisResults)}
            
            {message.metadata?.blogPost && (
              <div className={compactMode ? 'mt-3' : 'mt-4'}>
                <BlogPostPreview 
                  blogPost={message.metadata.blogPost}
                  qualityScore={message.metadata.qualityScore || 8.5}
                />
              </div>
            )}
          </div>
        </div>
        {showTimestamps && (
          <div className={`${compactMode ? 'ml-8' : 'ml-10'}`}>
            <span className="text-xs text-text-muted">{formatTimestamp(message.timestamp)}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;