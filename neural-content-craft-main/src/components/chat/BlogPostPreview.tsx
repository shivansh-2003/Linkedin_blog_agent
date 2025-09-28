import React, { useState } from 'react';
import { CheckCircle, Edit, RotateCcw, Copy, ChevronDown, ChevronUp } from 'lucide-react';

interface BlogPost {
  title?: string;
  hook: string;
  content: string;
  call_to_action?: string;
  cta?: string;
  hashtags: string[];
  target_audience?: string;
  targetAudience?: string;
  engagement_score?: number;
}

interface BlogPostPreviewProps {
  blogPost: BlogPost;
  qualityScore: number;
  onApprove?: () => void;
  onRequestChanges?: () => void;
  onRegenerate?: () => void;
  onCopy?: () => void;
}

const BlogPostPreview: React.FC<BlogPostPreviewProps> = ({
  blogPost,
  qualityScore,
  onApprove,
  onRequestChanges,
  onRegenerate,
  onCopy
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const getQualityColor = (score: number) => {
    if (score >= 9) return 'text-accent-success';
    if (score >= 7) return 'text-accent-primary';
    if (score >= 5) return 'text-accent-warning';
    return 'text-accent-error';
  };

  const getQualityRing = (score: number) => {
    const percentage = (score / 10) * 100;
    return `conic-gradient(hsl(var(--accent-primary)) ${percentage}%, hsl(var(--background-elevated)) ${percentage}%)`;
  };

  const handleCopy = () => {
    const title = blogPost.title ? `${blogPost.title}\n\n` : '';
    const hook = blogPost.hook;
    const content = blogPost.content;
    const cta = blogPost.call_to_action || blogPost.cta || '';
    const hashtags = blogPost.hashtags.join(' ');
    
    const fullPost = `${title}${hook}\n\n${content}\n\n${cta}\n\n${hashtags}`;
    
    navigator.clipboard.writeText(fullPost);
    setCopied(true);
    onCopy?.();
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card-elevated rounded-xl overflow-hidden border border-accent-primary/30">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-background-elevated/50 border-b border-border-secondary">
        <div className="flex items-center space-x-3">
          <h3 className="text-lg font-semibold text-text-primary">📝 Generated LinkedIn Post</h3>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className="w-12 h-12 bg-background-elevated rounded-full flex items-center justify-center">
              <span className={`text-xs font-bold ${getQualityColor(qualityScore)}`}>
                {qualityScore.toFixed(1)}
              </span>
            </div>
            <div>
              <p className="text-sm font-medium text-text-primary">Quality Score</p>
              <p className="text-xs text-text-tertiary">{qualityScore}/10</p>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Hook */}
        <div>
          <h4 className="text-sm font-medium text-accent-primary mb-2">🪝 Hook:</h4>
          <p className="text-text-primary font-medium">{blogPost.hook}</p>
        </div>

        {/* Content */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-accent-primary">📄 Content:</h4>
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center space-x-1 text-text-secondary hover:text-text-primary text-xs transition-colors"
            >
              <span>{isExpanded ? 'Collapse' : 'Expand'}</span>
              {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>
          <div className={`text-text-secondary transition-all duration-300 ${isExpanded ? '' : 'line-clamp-3'}`}>
            {blogPost.content}
          </div>
        </div>

        {/* CTA */}
        <div>
          <h4 className="text-sm font-medium text-accent-primary mb-2">🎯 Call to Action:</h4>
          <p className="text-text-primary italic">{blogPost.call_to_action || blogPost.cta}</p>
        </div>

        {/* Hashtags */}
        <div>
          <h4 className="text-sm font-medium text-accent-primary mb-2">🏷️ Hashtags:</h4>
          <div className="flex flex-wrap gap-2">
            {blogPost.hashtags.map((tag, index) => (
              <span
                key={index}
                className="px-2 py-1 bg-background-elevated text-accent-primary text-sm rounded-md border border-accent-primary/30"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Target Audience */}
        <div>
          <h4 className="text-sm font-medium text-accent-primary mb-2">👥 Target Audience:</h4>
          <p className="text-text-tertiary text-sm">{blogPost.targetAudience}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between p-4 bg-background-elevated/30 border-t border-border-secondary">
        <div className="flex space-x-2">
          <button
            onClick={onApprove}
            className="flex items-center space-x-2 px-4 py-2 bg-accent-success text-background-primary rounded-lg font-medium hover:bg-accent-success/90 transition-colors"
          >
            <CheckCircle className="w-4 h-4" />
            <span>Approve</span>
          </button>
          
          <button
            onClick={onRequestChanges}
            className="flex items-center space-x-2 px-4 py-2 bg-background-elevated text-text-primary rounded-lg font-medium hover:bg-background-elevated/80 transition-colors border border-border-primary"
          >
            <Edit className="w-4 h-4" />
            <span>Request Changes</span>
          </button>
          
          <button
            onClick={onRegenerate}
            className="flex items-center space-x-2 px-4 py-2 bg-background-elevated text-text-primary rounded-lg font-medium hover:bg-background-elevated/80 transition-colors border border-border-primary"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Regenerate</span>
          </button>
        </div>

        <button
          onClick={handleCopy}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${
            copied 
              ? 'bg-accent-success text-background-primary' 
              : 'bg-accent-primary text-background-primary hover:bg-accent-primary/90'
          }`}
        >
          <Copy className="w-4 h-4" />
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
    </div>
  );
};

export default BlogPostPreview;