import React from 'react';
import { User, Bot, AlertCircle, XCircle, CheckCircle } from 'lucide-react';
import BlogPostCard from './BlogPostCard';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface Message {
  id: string;
  type: 'user' | 'ai' | 'system' | 'error' | 'success';
  content: string;
  timestamp: Date;
  metadata?: {
    files?: File[];
    blogPost?: any;
    qualityScore?: number;
    processing?: boolean;
    isError?: boolean;
    errorMessage?: string;
    onApprove?: () => void;
    onRequestChanges?: () => void;
    onRegenerate?: () => void;
  };
}

interface MessageBubbleProps {
  message: Message;
  compactMode?: boolean;
  showTimestamps?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  compactMode = false,
  showTimestamps = true,
}) => {
  // ==========================================================================
  // HELPERS
  // ==========================================================================

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes} min ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;

    return timestamp.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const formatContent = (content: string) => {
    const lines = content.split('\n');

    return lines.map((line, index) => {
      // Bold headers
      if (line.startsWith('**') && line.endsWith('**')) {
        return (
          <p key={index} className="font-bold text-text-primary mb-2">
            {line.slice(2, -2)}
          </p>
        );
      }

      // H2 headers
      if (line.startsWith('## ')) {
        return (
          <h3 key={index} className="text-lg font-semibold text-text-primary mt-3 mb-2">
            {line.slice(3)}
          </h3>
        );
      }

      // Bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <li key={index} className="ml-4 text-text-secondary mb-1">
            {line.trim().slice(1).trim()}
          </li>
        );
      }

      // Empty lines
      if (line.trim() === '') {
        return <br key={index} />;
      }

      // Regular text with inline bold
      const parts = line.split(/(\*\*[^*]+\*\*)/g);
      return (
        <p key={index} className="text-text-secondary mb-1">
          {parts.map((part, i) => {
            if (part.startsWith('**') && part.endsWith('**')) {
              return (
                <strong key={i} className="text-text-primary font-semibold">
                  {part.slice(2, -2)}
                </strong>
              );
            }
            return part;
          })}
        </p>
      );
    });
  };

  // ==========================================================================
  // USER MESSAGE
  // ==========================================================================

  if (message.type === 'user') {
    return (
      <div className="flex justify-end animate-[slideInRight_0.3s_ease-out] mb-4">
        <div className="max-w-[80%] space-y-1">
          <div className="flex items-end justify-end space-x-2">
            <div
              className={`bg-gradient-to-r from-accent-primary to-primary rounded-2xl rounded-tr-sm ${
                compactMode ? 'p-3' : 'p-4'
              }`}
            >
              <p
                className={`text-background-primary font-medium whitespace-pre-wrap ${
                  compactMode ? 'text-sm' : ''
                }`}
              >
                {message.content}
              </p>
            </div>
            <div
              className={`bg-background-elevated rounded-full flex items-center justify-center flex-shrink-0 ${
                compactMode ? 'w-7 h-7' : 'w-10 h-10'
              }`}
            >
              <User
                className={`text-text-secondary ${compactMode ? 'w-4 h-4' : 'w-5 h-5'}`}
              />
            </div>
          </div>
          {showTimestamps && (
            <div className="text-right">
              <span className="text-xs text-text-muted">
                You • {formatTimestamp(message.timestamp)}
              </span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ==========================================================================
  // SYSTEM MESSAGE
  // ==========================================================================

  if (message.type === 'system') {
    return (
      <div className="flex justify-center animate-[fadeIn_0.3s_ease-out] mb-4">
        <div
          className={`max-w-2xl ${
            compactMode ? 'p-3' : 'p-4'
          } bg-background-elevated border border-border-secondary rounded-xl`}
        >
          <div className="flex items-start space-x-3">
            <AlertCircle
              className={`text-accent-warning flex-shrink-0 mt-0.5 ${
                compactMode ? 'w-4 h-4' : 'w-5 h-5'
              }`}
            />
            <div className="flex-1">
              <div
                className={`text-text-secondary whitespace-pre-wrap ${
                  compactMode ? 'text-xs' : 'text-sm'
                }`}
              >
                {formatContent(message.content)}
              </div>
              {message.metadata?.processing && (
                <div className="mt-3">
                  <div className="w-full bg-background-primary rounded-full h-2">
                    <div
                      className="h-2 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full animate-[progressIndeterminate_2s_ease-in-out_infinite]"
                      style={{ width: '40%' }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================================
  // SUCCESS MESSAGE
  // ==========================================================================

  if (message.type === 'success') {
    return (
      <div className="flex justify-center animate-[fadeIn_0.3s_ease-out] mb-4">
        <div
          className={`max-w-2xl ${
            compactMode ? 'p-3' : 'p-4'
          } bg-accent-success/10 border border-accent-success/30 rounded-xl`}
        >
          <div className="flex items-start space-x-3">
            <CheckCircle
              className={`text-accent-success flex-shrink-0 ${
                compactMode ? 'w-5 h-5' : 'w-6 h-6'
              }`}
            />
            <div className="flex-1">
              <div className={`whitespace-pre-wrap ${compactMode ? 'text-sm' : 'text-base'}`}>
                {formatContent(message.content)}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================================
  // ERROR MESSAGE
  // ==========================================================================

  if (message.type === 'error') {
    return (
      <div className="flex justify-center animate-[fadeIn_0.3s_ease-out] mb-4">
        <div
          className={`max-w-2xl ${
            compactMode ? 'p-3' : 'p-4'
          } bg-accent-error/10 border-2 border-accent-error/30 rounded-xl`}
        >
          <div className="flex items-start space-x-3">
            <XCircle
              className={`text-accent-error flex-shrink-0 ${
                compactMode ? 'w-5 h-5' : 'w-6 h-6'
              }`}
            />
            <div className="flex-1">
              <div className={`whitespace-pre-wrap ${compactMode ? 'text-sm' : 'text-base'}`}>
                {formatContent(message.content)}
              </div>
            </div>
          </div>
          {showTimestamps && (
            <div className="text-right mt-2">
              <span className="text-xs text-text-muted">{formatTimestamp(message.timestamp)}</span>
            </div>
          )}
        </div>
      </div>
    );
  }

  // ==========================================================================
  // AI MESSAGE
  // ==========================================================================

  return (
    <div className="flex justify-start animate-[slideInLeft_0.3s_ease-out] mb-4">
      <div className="max-w-[85%] space-y-1">
        <div className="flex items-end space-x-2">
          <div
            className={`bg-gradient-to-br from-accent-primary via-accent-secondary to-primary rounded-full flex items-center justify-center flex-shrink-0 ${
              compactMode ? 'w-7 h-7' : 'w-10 h-10'
            }`}
          >
            <Bot
              className={`text-background-primary ${compactMode ? 'w-4 h-4' : 'w-5 h-5'}`}
            />
          </div>
          <div
            className={`glass-card bg-background-tertiary/80 border border-accent-primary/20 ${
              compactMode ? 'p-3' : 'p-4'
            } rounded-2xl rounded-tl-sm flex-1`}
          >
            <div
              className={`leading-relaxed whitespace-pre-wrap ${compactMode ? 'text-sm' : ''}`}
            >
              {formatContent(message.content)}
            </div>

            {message.metadata?.blogPost && (
              <div className={compactMode ? 'mt-3' : 'mt-4'}>
                <BlogPostCard
                  blogPost={message.metadata.blogPost}
                  qualityScore={message.metadata.qualityScore || 8.0}
                  compactMode={compactMode}
                  onApprove={message.metadata.onApprove}
                  onRequestChanges={message.metadata.onRequestChanges}
                  onRegenerate={message.metadata.onRegenerate}
                />
              </div>
            )}
          </div>
        </div>
        {showTimestamps && (
          <div className={`${compactMode ? 'ml-9' : 'ml-12'}`}>
            <span className="text-xs text-text-muted">
              BlogBot • {formatTimestamp(message.timestamp)}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
