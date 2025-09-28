import { FileText, Brain, Target, MessageSquare, RefreshCw, BarChart3 } from "lucide-react";

const FeaturesSection = () => {
  // Color mapping to ensure Tailwind includes these classes
  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { bg: string; text: string; bgOpacity: string; gradient: string }> = {
      "accent-primary": {
        bg: "bg-accent-primary",
        text: "text-accent-primary", 
        bgOpacity: "bg-accent-primary/20",
        gradient: "from-accent-primary"
      },
      "accent-ai": {
        bg: "bg-accent-ai",
        text: "text-accent-ai",
        bgOpacity: "bg-accent-ai/20", 
        gradient: "from-accent-ai"
      },
      "accent-success": {
        bg: "bg-accent-success",
        text: "text-accent-success",
        bgOpacity: "bg-accent-success/20",
        gradient: "from-accent-success"
      },
      "accent-secondary": {
        bg: "bg-accent-secondary", 
        text: "text-accent-secondary",
        bgOpacity: "bg-accent-secondary/20",
        gradient: "from-accent-secondary"
      },
      "accent-warning": {
        bg: "bg-accent-warning",
        text: "text-accent-warning", 
        bgOpacity: "bg-accent-warning/20",
        gradient: "from-accent-warning"
      }
    };
    return colorMap[color] || colorMap["accent-primary"];
  };
  const features = [
    {
      icon: FileText,
      title: "Multi-Format Support",
      description: "Upload PDFs, Word docs, PowerPoint, code files, images, and more",
      details: [
        "25+ supported file formats",
        "Drag & drop interface",
        "Batch upload capability",
        "Real-time processing"
      ],
      color: "accent-primary"
    },
    {
      icon: Brain,
      title: "AI-Powered Analysis",
      description: "Intelligent content extraction with key insight generation",
      details: [
        "Deep content understanding",
        "Context-aware processing",
        "Key insight extraction",
        "Professional tone adaptation"
      ],
      color: "accent-ai"
    },
    {
      icon: Target,
      title: "LinkedIn Optimized",
      description: "Algorithm-friendly formatting with perfect engagement optimization",
      details: [
        "Platform-specific optimization",
        "Engagement-driven structure",
        "Hashtag recommendations",
        "Call-to-action suggestions"
      ],
      color: "accent-success"
    },
    {
      icon: MessageSquare,
      title: "Smart Conversation",
      description: "Natural language interaction with AI assistant",
      details: [
        "Conversational interface",
        "Context retention",
        "Follow-up questions",
        "Refinement requests"
      ],
      color: "accent-secondary"
    },
    {
      icon: RefreshCw,
      title: "Iterative Refinement",
      description: "Human-in-the-loop feedback and improvement cycles",
      details: [
        "Real-time feedback",
        "Multiple iterations",
        "Version comparison",
        "Approval workflow"
      ],
      color: "accent-warning"
    },
    {
      icon: BarChart3,
      title: "Quality Scoring",
      description: "1-10 scale assessment with detailed improvement suggestions",
      details: [
        "Multi-dimensional scoring",
        "Improvement recommendations",
        "Performance benchmarks",
        "Quality guarantees"
      ],
      color: "accent-primary"
    }
  ];

  return (
    <section id="features" className="py-20 bg-background-primary">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            Powerful <span className="gradient-text-primary">Features</span>
          </h2>
          <p className="text-body-large max-w-3xl mx-auto">
            Everything you need to create professional LinkedIn content that drives 
            real engagement and builds your personal brand.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
        <div
          key={feature.title}
          className={`glass-card-elevated p-8 rounded-2xl hover-lift group stagger-${(index % 6) + 1} relative overflow-hidden`}
        >
          {/* Background Gradient */}
          <div className="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity">
            <div className={`w-full h-full bg-gradient-to-br ${getColorClasses(feature.color).gradient} to-transparent`} />
              </div>

              <div className="relative z-10">
            {/* Icon */}
            <div className="flex justify-center mb-6">
              <div className={`p-4 rounded-full ${getColorClasses(feature.color).bgOpacity} group-hover:scale-110 transition-transform`}>
                <feature.icon className={`w-8 h-8 ${getColorClasses(feature.color).text}`} />
              </div>
            </div>

                {/* Title */}
                <h3 className="text-feature-title text-text-primary text-center mb-4">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-text-secondary text-center mb-6">
                  {feature.description}
                </p>

                {/* Details */}
                <div className="space-y-3">
                {feature.details.map((detail, detailIndex) => (
                  <div 
                    key={detailIndex}
                    className="flex items-center space-x-3 text-sm"
                  >
                    <div className={`w-1.5 h-1.5 rounded-full ${getColorClasses(feature.color).bg} flex-shrink-0`} />
                    <span className="text-text-tertiary">{detail}</span>
                    </div>
                  ))}
                </div>

                {/* Feature Badge */}
                <div className="mt-6 pt-6 border-t border-border-primary">
              <div className="text-center">
                <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getColorClasses(feature.color).bgOpacity} ${getColorClasses(feature.color).text}`}>
                  {index < 3 ? "Core Feature" : "Advanced"}
                </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="mt-16 text-center">
          <div className="glass-card p-8 rounded-2xl max-w-2xl mx-auto">
            <h3 className="text-2xl font-bold text-text-primary mb-4">
              Built for Professional Excellence
            </h3>
            <p className="text-text-secondary mb-6">
              Every feature is designed with one goal: helping you create LinkedIn content 
              that drives real professional results and builds meaningful connections.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-success" />
                <span className="text-sm text-text-tertiary">Enterprise Ready</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-primary" />
                <span className="text-sm text-text-tertiary">AI Powered</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-ai" />
                <span className="text-sm text-text-tertiary">Quality Focused</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;