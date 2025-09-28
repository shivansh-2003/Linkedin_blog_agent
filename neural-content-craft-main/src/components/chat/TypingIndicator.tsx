import React from 'react';
import { Bot } from 'lucide-react';

interface TypingIndicatorProps {
  compactMode?: boolean;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ compactMode = false }) => {
  return (
    <div className="flex justify-start animate-[slideInLeft_0.3s_ease-out]">
      <div className="flex items-end space-x-2">
        <div className={`bg-gradient-ai rounded-full flex items-center justify-center ${
          compactMode ? 'w-6 h-6' : 'w-8 h-8'
        }`}>
          <Bot className={`text-background-primary ${compactMode ? 'w-3 h-3' : 'w-4 h-4'}`} />
        </div>
        <div className={`glass-card bg-background-tertiary/80 border border-accent-primary/20 ${
          compactMode ? 'p-3' : 'p-4'
        } rounded-2xl rounded-bl-md relative overflow-hidden`}>
          <div className="flex items-center space-x-2">
            <span className={`text-text-secondary ${compactMode ? 'text-sm' : ''}`}>
              BlogAI is analyzing your content...
            </span>
            <div className="flex space-x-1">
              <div 
                className={`bg-accent-primary rounded-full animate-[typingDots_1.4s_ease-in-out_infinite] ${
                  compactMode ? 'w-1.5 h-1.5' : 'w-2 h-2'
                }`}
                style={{ animationDelay: '0ms' }}
              />
              <div 
                className={`bg-accent-primary rounded-full animate-[typingDots_1.4s_ease-in-out_infinite] ${
                  compactMode ? 'w-1.5 h-1.5' : 'w-2 h-2'
                }`}
                style={{ animationDelay: '200ms' }}
              />
              <div 
                className={`bg-accent-primary rounded-full animate-[typingDots_1.4s_ease-in-out_infinite] ${
                  compactMode ? 'w-1.5 h-1.5' : 'w-2 h-2'
                }`}
                style={{ animationDelay: '400ms' }}
              />
            </div>
          </div>
          
          {/* Progress bar for longer operations */}
          <div className={`${compactMode ? 'mt-2' : 'mt-3'} relative z-10`}>
            <div className="w-full bg-background-elevated rounded-full h-1">
              <div 
                className="h-1 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full animate-[progressIndeterminate_2s_ease-in-out_infinite]"
                style={{ width: '30%' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;