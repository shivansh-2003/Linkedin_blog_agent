import React, { useState } from 'react';
import { Copy, Check, Edit, RotateCcw, ThumbsUp, TrendingUp } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface BlogPost {
  title?: string;
  hook: string;
  content: string;
  call_to_action: string;
  cta?: string;
  hashtags: string[];
  target_audience?: string;
  targetAudience?: string;
  engagement_score?: number;
  source_file?: string;
}

interface BlogPostCardProps {
  blogPost: BlogPost;
  qualityScore: number;
  compactMode?: boolean;
  onApprove?: () => void;
  onRequestChanges?: () => void;
  onRegenerate?: () => void;
}

// ============================================================================
// COMPONENT
// ============================================================================

const BlogPostCard: React.FC<BlogPostCardProps> = ({
  blogPost,
  qualityScore,
  compactMode = false,
  onApprove,
  onRequestChanges,
  onRegenerate,
}) => {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const { toast } = useToast();

  // ==========================================================================
  // HELPERS
  // ==========================================================================

  const getScoreColor = (score: number) => {
    if (score >= 9) return 'text-accent-success';
    if (score >= 7) return 'text-accent-primary';
    if (score >= 5) return 'text-accent-warning';
    return 'text-accent-error';
  };

  const getScoreRing = (score: number) => {
    if (score >= 9) return 'border-accent-success';
    if (score >= 7) return 'border-accent-primary';
    if (score >= 5) return 'border-accent-warning';
    return 'border-accent-error';
  };

  const formatFullPost = () => {
    const cta = blogPost.call_to_action || blogPost.cta || '';
    return `${blogPost.hook}\n\n${blogPost.content}\n\n${cta}\n\n${blogPost.hashtags.join(' ')}`;
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(formatFullPost());
      setCopied(true);
      toast({
        title: '✅ Copied!',
        description: 'Blog post copied to clipboard',
      });
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast({
        title: '❌ Copy failed',
        description: 'Please try again',
        variant: 'destructive',
      });
    }
  };

  const truncateContent = (text: string, maxLength: number = 150) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const characterCount = formatFullPost().length;
  const targetAudience = blogPost.target_audience || blogPost.targetAudience || 'General audience';

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <div className="glass-card border-2 border-accent-primary/30 rounded-2xl p-6 bg-gradient-to-br from-background-tertiary/50 to-background-elevated/50 animate-[scaleIn_0.4s_ease-out]">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <span className="text-lg">📝</span>
          <h3 className="text-lg font-bold text-text-primary">Generated LinkedIn Post</h3>
        </div>
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            <TrendingUp className="w-4 h-4 text-accent-primary" />
            <span className={`text-sm font-semibold ${getScoreColor(qualityScore)}`}>
              {qualityScore.toFixed(1)}/10
            </span>
          </div>
          <div
            className={`w-10 h-10 rounded-full border-4 ${getScoreRing(
              qualityScore
            )} flex items-center justify-center`}
          >
            <span className={`text-xs font-bold ${getScoreColor(qualityScore)}`}>
              {Math.round(qualityScore)}
            </span>
          </div>
        </div>
      </div>

      {/* Hook */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-base">🪝</span>
          <h4 className="text-sm font-semibold text-accent-primary">Hook</h4>
        </div>
        <div className="bg-background-elevated/50 rounded-lg p-3 border border-border-secondary">
          <p className="text-text-primary font-medium italic">"{blogPost.hook}"</p>
        </div>
      </div>

      {/* Content */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <span className="text-base">📄</span>
            <h4 className="text-sm font-semibold text-accent-primary">Content</h4>
          </div>
          {blogPost.content.length > 150 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="text-xs text-accent-primary hover:text-accent-secondary transition-colors"
            >
              {expanded ? 'Show less' : 'Read more'}
            </button>
          )}
        </div>
        <div className="bg-background-elevated/50 rounded-lg p-3 border border-border-secondary">
          <p className="text-text-secondary whitespace-pre-wrap">
            {expanded ? blogPost.content : truncateContent(blogPost.content)}
          </p>
        </div>
      </div>

      {/* Call to Action */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-base">🎯</span>
          <h4 className="text-sm font-semibold text-accent-primary">Call to Action</h4>
        </div>
        <div className="bg-accent-primary/5 rounded-lg p-3 border border-accent-primary/20">
          <p className="text-text-primary font-medium">
            "{blogPost.call_to_action || blogPost.cta}"
          </p>
        </div>
      </div>

      {/* Hashtags */}
      <div className="mb-4">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-base">🏷️</span>
          <h4 className="text-sm font-semibold text-accent-primary">Hashtags</h4>
        </div>
        <div className="flex flex-wrap gap-2">
          {blogPost.hashtags.map((tag, index) => (
            <span
              key={index}
              className="px-3 py-1 bg-accent-primary/10 text-accent-primary rounded-full text-sm border border-accent-primary/20"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Metadata */}
      <div className="flex items-center justify-between text-xs text-text-tertiary mb-4 pb-4 border-b border-border-secondary">
        <div className="flex items-center space-x-4">
          <span>👥 {targetAudience}</span>
          <span>📊 {characterCount} characters</span>
          {blogPost.source_file && <span>📄 From: {blogPost.source_file}</span>}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleCopy}
          className="flex items-center space-x-2 px-4 py-2 bg-background-elevated text-text-primary rounded-lg border border-border-secondary hover:bg-background-tertiary hover:border-accent-primary/50 transition-all duration-200"
        >
          {copied ? (
            <>
              <Check className="w-4 h-4 text-accent-success" />
              <span className="text-sm">Copied!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span className="text-sm">Copy</span>
            </>
          )}
        </button>

        {onApprove && (
          <button
            onClick={onApprove}
            className="flex items-center space-x-2 px-4 py-2 bg-accent-success text-background-primary rounded-lg hover:bg-accent-success/90 hover:shadow-glow transition-all duration-200 font-medium"
          >
            <ThumbsUp className="w-4 h-4" />
            <span className="text-sm">Approve</span>
          </button>
        )}

        {onRequestChanges && (
          <button
            onClick={onRequestChanges}
            className="flex items-center space-x-2 px-4 py-2 bg-transparent text-accent-primary rounded-lg border border-accent-primary hover:bg-accent-primary/10 transition-all duration-200"
          >
            <Edit className="w-4 h-4" />
            <span className="text-sm">Request Changes</span>
          </button>
        )}

        {onRegenerate && (
          <button
            onClick={onRegenerate}
            className="flex items-center space-x-2 px-4 py-2 bg-transparent text-accent-secondary rounded-lg border border-accent-secondary hover:bg-accent-secondary/10 transition-all duration-200"
          >
            <RotateCcw className="w-4 h-4" />
            <span className="text-sm">Regenerate</span>
          </button>
        )}
      </div>
    </div>
  );
};

export default BlogPostCard;
