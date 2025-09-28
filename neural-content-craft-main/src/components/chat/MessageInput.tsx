import React, { useState, useRef, useEffect } from 'react';
import { Send, Paperclip, Sparkles, Palette, BarChart, Mic, Zap, Hash } from 'lucide-react';

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  compactMode?: boolean;
}

interface AIsuggestion {
  type: 'content' | 'angle' | 'audience';
  text: string;
  icon: string;
}

const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  disabled = false,
  placeholder = "Type your message here...",
  compactMode = false
}) => {
  const [message, setMessage] = useState('');
  const [showAISuggestions, setShowAISuggestions] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [aiSuggestions, setAISuggestions] = useState<AIsuggestion[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = Math.min(textarea.scrollHeight, 200) + 'px';
    }
  }, [message]);

  // Generate AI suggestions based on content
  useEffect(() => {
    if (message.length > 20) {
      // Simulate AI analysis
      const suggestions: AIsuggestion[] = [
        {
          type: 'content',
          text: 'Consider adding specific metrics or data',
          icon: '📊'
        },
        {
          type: 'angle',
          text: 'Try a beginner-friendly approach',
          icon: '🎯'
        },
        {
          type: 'audience',
          text: 'Target: Data Scientists (Detected)',
          icon: '👥'
        }
      ];
      setAISuggestions(suggestions);
      setShowAISuggestions(true);
    } else {
      setShowAISuggestions(false);
    }
  }, [message]);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setShowAISuggestions(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const insertTemplate = (template: string) => {
    setMessage(prev => prev + template);
    textareaRef.current?.focus();
  };

  const quickTemplates = [
    { label: 'Tutorial', template: 'I want to create a step-by-step tutorial about ' },
    { label: 'Case Study', template: 'Help me share a case study about ' },
    { label: 'Best Practice', template: 'I\'d like to share best practices for ' },
    { label: 'Innovation', template: 'Let\'s discuss the latest innovation in ' }
  ];

  const characterCount = message.length;
  const maxCharacters = 2000;
  const warningThreshold = 1800;

  return (
    <div className={`space-y-3 ${compactMode ? 'space-y-2' : 'space-y-3'}`}>
      {/* AI Suggestions Panel */}
      {showAISuggestions && !compactMode && (
        <div className="glass-card rounded-lg p-4 border border-accent-primary/20 animate-[slideInUp_0.3s_ease-out]">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-accent-primary flex items-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span>AI Suggestions</span>
            </h4>
            <button
              onClick={() => setShowAISuggestions(false)}
              className="text-text-muted hover:text-text-primary text-xs"
            >
              Hide ▲
            </button>
          </div>

          <div className="space-y-2">
            <div>
              <p className="text-xs text-text-secondary mb-2">💡 Consider adding:</p>
              <div className="space-y-1">
                {aiSuggestions.filter(s => s.type === 'content').map((suggestion, index) => (
                  <p key={index} className="text-xs text-text-tertiary">
                    • {suggestion.text}
                  </p>
                ))}
              </div>
            </div>

            <div>
              <p className="text-xs text-text-secondary mb-2">🎯 Suggested angles:</p>
              <div className="flex flex-wrap gap-2">
                {['Technical Deep-dive', 'Beginner-friendly', 'Case Study'].map((angle) => (
                  <button
                    key={angle}
                    onClick={() => insertTemplate(`Focus on ${angle.toLowerCase()}: `)}
                    className="px-2 py-1 bg-background-elevated text-accent-primary text-xs rounded border border-accent-primary/30 hover:bg-accent-primary/10 transition-colors"
                  >
                    {angle}
                  </button>
                ))}
              </div>
            </div>

            {aiSuggestions.find(s => s.type === 'audience') && (
              <div>
                <p className="text-xs text-accent-success">
                  📊 {aiSuggestions.find(s => s.type === 'audience')?.text}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Input Area */}
      <div className="glass-card rounded-xl border border-border-primary focus-within:border-accent-primary/50 transition-all duration-200">
        <div className={compactMode ? 'p-3' : 'p-4'}>
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={disabled ? "AI is generating response..." : placeholder}
            disabled={disabled}
            className={`w-full bg-transparent text-text-primary placeholder-text-muted resize-none outline-none ${
              compactMode ? 'min-h-[40px] max-h-[120px]' : 'min-h-[60px] max-h-[200px]'
            }`}
            rows={1}
          />
        </div>

        {/* Action Bar */}
        <div className={`flex items-center justify-between border-t border-border-secondary ${
          compactMode ? 'px-3 py-2' : 'px-4 py-3'
        }`}>
          <div className={`flex items-center ${compactMode ? 'space-x-1' : 'space-x-2'}`}>
            {/* Quick Action Buttons */}
            <button
              className={`text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200 ${
                compactMode ? 'p-1.5' : 'p-2'
              }`}
              title="Attach Files"
            >
              <Paperclip className={compactMode ? 'w-3 h-3' : 'w-4 h-4'} />
            </button>

            {!compactMode && (
              <div className="relative group">
                <button
                  className="p-2 text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200"
                  title="Quick Templates"
                >
                  <Zap className="w-4 h-4" />
                </button>
                
                {/* Template Dropdown */}
                <div className="absolute bottom-full left-0 mb-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                  <div className="glass-card rounded-lg p-2 border border-accent-primary/20 w-48">
                    <p className="text-xs text-text-secondary mb-2">Quick Templates:</p>
                    {quickTemplates.map((template) => (
                      <button
                        key={template.label}
                        onClick={() => insertTemplate(template.template)}
                        className="w-full text-left px-2 py-1 text-xs text-text-primary hover:bg-background-elevated rounded transition-colors"
                      >
                        {template.label}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            <button
              className={`text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200 ${
                compactMode ? 'p-1.5' : 'p-2'
              }`}
              title="AI Suggestions"
              onClick={() => setShowAISuggestions(!showAISuggestions)}
            >
              <Sparkles className={compactMode ? 'w-3 h-3' : 'w-4 h-4'} />
            </button>

            {!compactMode && (
              <>
                <button
                  className="p-2 text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200"
                  title="Format Text"
                >
                  <Palette className="w-4 h-4" />
                </button>

                <button
                  className="p-2 text-text-secondary hover:text-accent-primary rounded-lg hover:bg-background-elevated transition-all duration-200"
                  title="Add Data/Stats"
                >
                  <BarChart className="w-4 h-4" />
                </button>
              </>
            )}

            <button
              className={`rounded-lg transition-all duration-200 ${
                compactMode ? 'p-1.5' : 'p-2'
              } ${
                isRecording 
                  ? 'text-accent-error bg-accent-error/10' 
                  : 'text-text-secondary hover:text-accent-primary hover:bg-background-elevated'
              }`}
              title="Voice Input"
              onClick={() => setIsRecording(!isRecording)}
            >
              <Mic className={compactMode ? 'w-3 h-3' : 'w-4 h-4'} />
            </button>
          </div>

          <div className={`flex items-center ${compactMode ? 'space-x-2' : 'space-x-3'}`}>
            {/* Character Count */}
            {!compactMode && (
              <div className="text-xs">
                <span className={`
                  ${characterCount > warningThreshold 
                    ? characterCount > maxCharacters 
                      ? 'text-accent-error' 
                      : 'text-accent-warning'
                    : 'text-text-muted'
                  }
                `}>
                  💬 {characterCount}/{maxCharacters}
                </span>
              </div>
            )}

            {/* Send Button */}
            <button
              onClick={handleSend}
              disabled={disabled || !message.trim() || characterCount > maxCharacters}
              className={`
                flex items-center rounded-lg font-medium transition-all duration-200 ${
                  compactMode ? 'space-x-1 px-3 py-1.5' : 'space-x-2 px-4 py-2'
                }
                ${disabled || !message.trim() || characterCount > maxCharacters
                  ? 'bg-background-elevated text-text-muted cursor-not-allowed'
                  : 'bg-gradient-to-r from-accent-primary to-primary text-background-primary hover:shadow-glow hover:scale-105'
                }
              `}
            >
              <Send className={compactMode ? 'w-3 h-3' : 'w-4 h-4'} />
              <span className={compactMode ? 'text-sm' : ''}>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MessageInput;