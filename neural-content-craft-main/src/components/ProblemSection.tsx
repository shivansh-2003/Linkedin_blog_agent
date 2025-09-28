import { Clock, Target, TrendingDown, AlertCircle } from "lucide-react";

const ProblemSection = () => {
  // Color mapping to ensure Tailwind includes these classes
  const getColorClasses = (color: string) => {
    const colorMap: Record<string, { bg: string; text: string; bgOpacity: string }> = {
      "accent-error": {
        bg: "bg-accent-error",
        text: "text-accent-error",
        bgOpacity: "bg-accent-error/20"
      },
      "accent-warning": {
        bg: "bg-accent-warning",
        text: "text-accent-warning",
        bgOpacity: "bg-accent-warning/20"
      }
    };
    return colorMap[color] || colorMap["accent-error"];
  };
  const problems = [
    {
      icon: Clock,
      title: "Time Drain",
      description: "30+ minutes per post creation taking away from core work",
      details: [
        "Research and ideation",
        "Writing and formatting", 
        "Editing and optimization",
        "Finding relevant hashtags"
      ],
      color: "accent-error"
    },
    {
      icon: Target,
      title: "Low Quality",
      description: "Generic content that doesn't stand out or provide value",
      details: [
        "Lacks professional polish",
        "Missing engagement hooks",
        "Poor LinkedIn optimization",
        "Inconsistent brand voice"
      ],
      color: "accent-warning"
    },
    {
      icon: TrendingDown,
      title: "Poor Results",
      description: "Low engagement rates and poor professional visibility",
      details: [
        "Minimal likes and comments",
        "Low post reach",
        "Missed networking opportunities", 
        "Weak thought leadership"
      ],
      color: "accent-error"
    }
  ];

  return (
    <section className="py-20 bg-background-primary">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            The LinkedIn <span className="gradient-text-primary">Content Challenge</span>
          </h2>
          <p className="text-body-large max-w-3xl mx-auto">
            Creating high-quality LinkedIn content consistently is one of the biggest 
            challenges professionals face in building their personal brand.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          {problems.map((problem, index) => (
            <div
              key={problem.title}
              className={`glass-card-elevated p-8 rounded-2xl hover-lift stagger-${index + 1} group relative overflow-hidden`}
            >
              {/* Background Pattern */}
              <div className="absolute inset-0 opacity-5">
                <div className="w-full h-full bg-gradient-to-br from-red-500 to-orange-500" />
              </div>

              <div className="relative z-10">
              {/* Icon */}
              <div className="flex justify-center mb-6">
                <div className={`p-4 rounded-full ${getColorClasses(problem.color).bgOpacity} group-hover:scale-110 transition-transform`}>
                  <problem.icon className={`w-8 h-8 ${getColorClasses(problem.color).text}`} />
                </div>
              </div>

                {/* Title */}
                <h3 className="text-feature-title text-text-primary text-center mb-4">
                  {problem.title}
                </h3>

                {/* Description */}
                <p className="text-text-secondary text-center mb-6">
                  {problem.description}
                </p>

                {/* Details */}
                <div className="space-y-3">
                  {problem.details.map((detail, detailIndex) => (
                    <div 
                      key={detailIndex}
                      className="flex items-center space-x-3 text-sm text-text-tertiary"
                    >
                      <AlertCircle className="w-4 h-4 text-accent-error flex-shrink-0" />
                      <span>{detail}</span>
                    </div>
                  ))}
                </div>

                {/* Impact Indicator */}
                <div className="mt-6 pt-6 border-t border-border-primary">
                <div className="text-center">
                  <span className={`text-2xl font-bold ${getColorClasses(problem.color).text}`}>
                    {index === 0 && "30+ min"}
                    {index === 1 && "Low ROI"}
                    {index === 2 && "< 2% reach"}
                  </span>
                  <p className="text-xs text-text-muted mt-1">
                      {index === 0 && "per post"}
                      {index === 1 && "on effort"}
                      {index === 2 && "average"}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom Quote */}
        <div className="text-center">
          <div className="glass-card p-8 rounded-2xl max-w-2xl mx-auto">
            <blockquote className="text-2xl font-light text-text-secondary italic mb-4">
              "There has to be a better way..."
            </blockquote>
            <div className="w-16 h-1 bg-gradient-primary mx-auto rounded-full mb-4" />
            <p className="text-text-tertiary">
              Sound familiar? You're not alone. Thousands of professionals struggle 
              with the same content creation challenges every day.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ProblemSection;