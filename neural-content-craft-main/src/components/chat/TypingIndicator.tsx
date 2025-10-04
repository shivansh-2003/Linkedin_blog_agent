import React from 'react';
import { Bot } from 'lucide-react';

interface TypingIndicatorProps {
  compactMode?: boolean;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ compactMode = false }) => {
  return (
    <div className="flex justify-start animate-[fadeIn_0.3s_ease-out] mb-4">
      <div className="flex items-end space-x-2">
        <div
          className={`bg-gradient-to-br from-accent-primary via-accent-secondary to-primary rounded-full flex items-center justify-center flex-shrink-0 ${
            compactMode ? 'w-7 h-7' : 'w-10 h-10'
          }`}
        >
          <Bot className={`text-background-primary ${compactMode ? 'w-4 h-4' : 'w-5 h-5'}`} />
        </div>
        <div
          className={`glass-card bg-background-tertiary/80 border border-accent-primary/20 ${
            compactMode ? 'p-3' : 'p-4'
          } rounded-2xl rounded-tl-sm`}
        >
          <div className="flex items-center space-x-2">
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-accent-primary rounded-full animate-[bounce_1s_ease-in-out_infinite]" />
              <div className="w-2 h-2 bg-accent-primary rounded-full animate-[bounce_1s_ease-in-out_0.2s_infinite]" />
              <div className="w-2 h-2 bg-accent-primary rounded-full animate-[bounce_1s_ease-in-out_0.4s_infinite]" />
            </div>
            <span className="text-sm text-text-tertiary">AI is thinking...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
