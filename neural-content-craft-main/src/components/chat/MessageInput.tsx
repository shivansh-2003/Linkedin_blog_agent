import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Sparkles } from 'lucide-react';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onFileUpload?: (files: File[]) => void;
  disabled?: boolean;
  placeholder?: string;
  compactMode?: boolean;
}

// ============================================================================
// COMPONENT
// ============================================================================

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  onFileUpload,
  disabled = false,
  placeholder = 'Type your message here...',
  compactMode = false,
}) => {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const maxCharacters = 5000;
  const warningThreshold = 4500;

  // ==========================================================================
  // AUTO-RESIZE TEXTAREA
  // ==========================================================================

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
  }, [message]);

  // ==========================================================================
  // EVENT HANDLERS
  // ==========================================================================

  const handleSend = () => {
    if (message.trim() && !disabled && message.length <= maxCharacters) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (files.length > 0 && onFileUpload) {
      onFileUpload(files);
    }
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleFileButtonClick = () => {
    if (onFileUpload) {
      fileInputRef.current?.click();
    }
  };

  const characterCount = message.length;
  const isOverLimit = characterCount > maxCharacters;
  const isNearLimit = characterCount > warningThreshold;

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <div className={`space-y-3 ${compactMode ? 'space-y-2' : 'space-y-3'}`}>
      {/* AI Suggestions (optional) */}
      {showSuggestions && message.length > 50 && !compactMode && (
        <div className="glass-card rounded-xl p-4 border border-accent-primary/20 animate-[slideInUp_0.3s_ease-out]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-accent-primary flex items-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span>AI Suggestions</span>
            </h4>
            <button
              onClick={() => setShowSuggestions(false)}
              className="text-text-muted hover:text-text-primary text-xs"
            >
              Hide ▲
            </button>
          </div>

          <div className="space-y-2">
            <p className="text-xs text-text-secondary mb-2">💡 Quick actions:</p>
            <div className="flex flex-wrap gap-2">
              {['Make it more professional', 'Add statistics', 'Simplify language'].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => setMessage(message + '\n\n' + suggestion)}
                  className="px-3 py-1 bg-background-elevated text-accent-primary text-xs rounded-lg border border-accent-primary/30 hover:bg-accent-primary/10 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Input Area */}
      <div className="glass-card rounded-2xl border border-border-primary focus-within:border-accent-primary/50 transition-all duration-200 overflow-hidden">
        <div className={compactMode ? 'p-3' : 'p-4'}>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={disabled ? 'AI is generating response...' : placeholder}
            disabled={disabled}
            className={`w-full bg-transparent text-text-primary placeholder-text-muted resize-none outline-none ${
              compactMode ? 'min-h-[40px] max-h-[100px]' : 'min-h-[56px] max-h-[120px]'
            }`}
            rows={1}
          />
        </div>

        {/* Action Bar */}
        <div
          className={`flex items-center justify-between border-t border-border-secondary ${
            compactMode ? 'px-3 py-2' : 'px-4 py-3'
          }`}
        >
          <div className={`flex items-center ${compactMode ? 'space-x-1' : 'space-x-2'}`}>
            {/* File Upload Button */}
            <button
              onClick={handleFileButtonClick}
              disabled={!onFileUpload || disabled}
              className={`text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200 ${
                !onFileUpload ? 'opacity-50 cursor-not-allowed' : ''
              } ${compactMode ? 'p-1.5' : 'p-2'}`}
              title="Attach Files"
            >
              <Paperclip className={compactMode ? 'w-4 h-4' : 'w-5 h-5'} />
            </button>

            {/* AI Suggestions Button */}
            {!compactMode && (
              <button
                onClick={() => setShowSuggestions(!showSuggestions)}
                disabled={disabled}
                className={`text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200 p-2`}
                title="AI Suggestions"
              >
                <Sparkles className="w-5 h-5" />
              </button>
            )}
          </div>

          <div className={`flex items-center ${compactMode ? 'space-x-2' : 'space-x-3'}`}>
            {/* Character Count */}
            {!compactMode && (
              <div className="text-xs">
                <span
                  className={`
                  ${
                    isOverLimit
                      ? 'text-accent-error font-semibold'
                      : isNearLimit
                      ? 'text-accent-warning'
                      : 'text-text-muted'
                  }
                `}
                >
                  {characterCount}/{maxCharacters}
                </span>
              </div>
            )}

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={disabled || !message.trim() || isOverLimit}
              className={`
                flex items-center rounded-lg font-medium transition-all duration-200 ${
                  compactMode ? 'space-x-1 px-3 py-1.5' : 'space-x-2 px-5 py-2.5'
                }
                ${
                  disabled || !message.trim() || isOverLimit
                    ? 'bg-background-elevated text-text-muted cursor-not-allowed'
                    : 'bg-gradient-to-r from-accent-primary to-primary text-background-primary hover:shadow-glow hover:scale-105'
                }
              `}
            >
              <Send className={compactMode ? 'w-3.5 h-3.5' : 'w-4 h-4'} />
              <span className={compactMode ? 'text-sm' : ''}>Send</span>
            </button>
          </div>
        </div>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.ppt,.pptx,.txt,.md,.py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.jpg,.jpeg,.png,.gif,.webp,.json,.xml,.csv,.yaml,.yml"
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
};

export default MessageInput;
