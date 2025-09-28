import { Users, Code, GraduationCap, TrendingUp, Palette, BarChart, Building, BookOpen } from "lucide-react";

const UseCasesSection = () => {
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
  const useCases = [
    {
      icon: Users,
      title: "Business Leaders",
      description: "Share strategic insights & thought leadership",
      color: "accent-primary",
      examples: [
        "Market analysis posts",
        "Leadership insights",
        "Industry predictions",
        "Company updates"
      ],
      result: "Build executive presence"
    },
    {
      icon: Code,
      title: "Developers",
      description: "Transform code & tech projects into educational content",
      color: "accent-ai",
      examples: [
        "Technical tutorials",
        "Code walkthroughs",
        "Best practices",
        "Tool reviews"
      ],
      result: "Establish tech expertise"
    },
    {
      icon: GraduationCap,
      title: "Researchers",
      description: "Turn academic papers into accessible insights",
      color: "accent-success",
      examples: [
        "Research summaries",
        "Study findings",
        "Methodology insights",
        "Academic trends"
      ],
      result: "Share knowledge broadly"
    },
    {
      icon: TrendingUp,
      title: "Sales Teams",
      description: "Convert case studies into social proof",
      color: "accent-warning",
      examples: [
        "Success stories",
        "Client testimonials",
        "ROI demonstrations",
        "Product updates"
      ],
      result: "Drive lead generation"
    },
    {
      icon: Palette,
      title: "Creators",
      description: "Content repurposing across multiple platforms",
      color: "accent-secondary",
      examples: [
        "Multi-platform content",
        "Behind-the-scenes",
        "Creative processes",
        "Portfolio highlights"
      ],
      result: "Maximize content ROI"
    },
    {
      icon: BarChart,
      title: "Analysts",
      description: "Data-driven posts from reports & analytics",
      color: "accent-primary",
      examples: [
        "Market insights",
        "Data visualizations",
        "Trend analysis",
        "Industry reports"
      ],
      result: "Position as expert"
    },
    {
      icon: Building,
      title: "Agencies",
      description: "Scale content creation for clients",
      color: "accent-success",
      examples: [
        "Client campaigns",
        "Industry expertise",
        "Service showcases",
        "Team highlights"
      ],
      result: "Increase client value"
    },
    {
      icon: BookOpen,
      title: "Educators",
      description: "Share knowledge & build authority",
      color: "accent-ai",
      examples: [
        "Educational content",
        "Learning resources",
        "Student success",
        "Teaching insights"
      ],
      result: "Expand reach & impact"
    }
  ];

  return (
    <section id="use-cases" className="py-20 bg-background-secondary/50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            Perfect For <span className="gradient-text-primary">Every Professional</span>
          </h2>
          <p className="text-body-large max-w-3xl mx-auto">
            Whether you're a business leader, developer, researcher, or creator, 
            BlogAI Assistant adapts to your unique content needs and professional goals.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {useCases.map((useCase, index) => (
            <div
              key={useCase.title}
              className={`glass-card-elevated p-6 rounded-2xl hover-lift group stagger-${(index % 8) + 1} relative overflow-hidden`}
            >
              {/* Background Gradient */}
              <div className="absolute inset-0 opacity-5 group-hover:opacity-10 transition-opacity">
                <div className={`w-full h-full bg-gradient-to-br ${getColorClasses(useCase.color).gradient} to-transparent`} />
              </div>

              <div className="relative z-10">
                {/* Icon & Title */}
                <div className="flex items-center space-x-3 mb-4">
                  <div className={`p-3 rounded-full ${getColorClasses(useCase.color).bgOpacity} group-hover:scale-110 transition-transform`}>
                    <useCase.icon className={`w-6 h-6 ${getColorClasses(useCase.color).text}`} />
                  </div>
                  <h3 className="text-lg font-semibold text-text-primary">
                    {useCase.title}
                  </h3>
                </div>

                {/* Description */}
                <p className="text-text-secondary text-sm mb-4">
                  {useCase.description}
                </p>

                {/* Examples */}
                <div className="space-y-2 mb-4">
                  {useCase.examples.map((example, exampleIndex) => (
                    <div 
                      key={exampleIndex}
                      className="flex items-center space-x-2 text-xs"
                    >
                      <div className={`w-1 h-1 rounded-full ${getColorClasses(useCase.color).bg}`} />
                      <span className="text-text-tertiary">{example}</span>
                    </div>
                  ))}
                </div>

                {/* Result */}
                  <div className="pt-4 border-t border-border-primary">
                    <div className="flex items-center space-x-2">
                      <div className={`w-2 h-2 rounded-full ${getColorClasses(useCase.color).bg}`} />
                      <span className={`text-xs font-medium ${getColorClasses(useCase.color).text}`}>
                        {useCase.result}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Section */}
        <div className="mt-16">
          <div className="glass-card p-8 rounded-2xl text-center">
            <h3 className="text-2xl font-bold text-text-primary mb-4">
              Your Use Case Not Listed?
            </h3>
            <p className="text-text-secondary mb-6 max-w-2xl mx-auto">
              BlogAI Assistant is flexible enough to handle any content transformation challenge. 
              From technical documentation to creative portfolios, our AI adapts to your specific needs.
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-success" />
                <span className="text-sm text-text-tertiary">Any Industry</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-primary" />
                <span className="text-sm text-text-tertiary">Any Content Type</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-3 h-3 rounded-full bg-accent-ai" />
                <span className="text-sm text-text-tertiary">Custom Solutions</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default UseCasesSection;