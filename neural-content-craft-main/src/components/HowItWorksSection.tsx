import { useState, useEffect, useRef } from "react";
import { Upload, Brain, Sparkles, FileText, Zap, Target } from "lucide-react";
import { Button } from "@/components/ui/button";

const HowItWorksSection = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const sectionRef = useRef<HTMLDivElement>(null);

  const steps = [
    {
      number: 1,
      icon: Upload,
      title: "Upload",
      subtitle: "Drag & Drop Content",
      description: "Drag & drop any file or paste text content",
      details: [
        "25+ formats supported",
        "Instant validation",
        "Batch processing",
        "Secure upload"
      ],
      demoContent: {
        title: "Demo File Animation",
        files: ["Research.pdf", "Code.py", "Slides.pptx", "Article.docx"],
        status: "Ready to process"
      },
      bgColor: "from-blue-500/20 to-cyan-500/20"
    },
    {
      number: 2,
      icon: Brain,
      title: "AI Magic",
      subtitle: "Intelligent Processing",
      description: "AI analyzes content, extracts insights & generates engaging blog post",
      details: [
        "Deep content analysis",
        "Key insight extraction",
        "Context understanding",
        "Professional optimization"
      ],
      demoContent: {
        title: "Processing Animation",
        status: "Analyzing content...",
        progress: 75
      },
      bgColor: "from-purple-500/20 to-pink-500/20"
    },
    {
      number: 3,
      icon: Sparkles,
      title: "Perfect Post",
      subtitle: "LinkedIn-Ready Content",
      description: "Get your LinkedIn-ready post in minutes",
      details: [
        "Optimized structure",
        "Engagement hooks",
        "Professional tone",
        "Quality guarantee"
      ],
      demoContent: {
        title: "Sample Post Card",
        quality: 9.2,
        status: "Ready to publish"
      },
      bgColor: "from-green-500/20 to-emerald-500/20"
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
          
          // Auto-advance through steps
          const interval = setInterval(() => {
            setActiveStep((prev) => (prev + 1) % steps.length);
          }, 3000);

          return () => clearInterval(interval);
        }
      },
      { threshold: 0.3 }
    );

    if (sectionRef.current) {
      observer.observe(sectionRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section id="how-it-works" ref={sectionRef} className="py-20 bg-background-secondary/50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            How It <span className="gradient-text-primary">Works</span>
          </h2>
          <p className="text-body-large max-w-2xl mx-auto">
            <span className="font-semibold">Simple. Fast. Professional.</span>
            <br />
            Transform any content into viral LinkedIn posts in three easy steps.
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
          {steps.map((step, index) => (
            <div
              key={step.number}
              className={`relative group transition-all duration-500 ${
                isVisible ? "opacity-100 transform translate-y-0" : "opacity-0 transform translate-y-8"
              }`}
              style={{ transitionDelay: `${index * 200}ms` }}
            >
              {/* Connection Arrow */}
              {index < steps.length - 1 && (
                <div className="hidden lg:block absolute top-1/2 -right-4 z-10">
                  <div className={`w-8 h-0.5 bg-gradient-to-r transition-all duration-1000 ${
                    activeStep > index 
                      ? "from-accent-primary to-accent-secondary" 
                      : "from-border-primary to-border-secondary"
                  }`} />
                  <div className={`absolute -right-1 -top-1 w-2 h-2 rotate-45 transition-all duration-1000 ${
                    activeStep > index ? "bg-accent-secondary" : "bg-border-primary"
                  }`} />
                </div>
              )}

              <div
                className={`glass-card-elevated p-8 rounded-2xl hover-lift cursor-pointer transition-all duration-300 ${
                  activeStep === index 
                    ? "ring-2 ring-accent-primary shadow-glow" 
                    : "hover:ring-1 hover:ring-border-accent"
                }`}
                onClick={() => setActiveStep(index)}
              >
                {/* Background Gradient */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${step.bgColor} opacity-0 group-hover:opacity-100 transition-opacity`} />

                <div className="relative z-10">
                  {/* Step Number & Icon */}
                  <div className="flex items-center justify-between mb-6">
                    <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg transition-all duration-300 ${
                      activeStep === index
                        ? "bg-accent-primary text-background-primary"
                        : "bg-background-elevated text-text-tertiary"
                    }`}>
                      {step.number}
                    </div>
                    <step.icon className={`w-8 h-8 transition-all duration-300 ${
                      activeStep === index ? "text-accent-primary" : "text-text-tertiary"
                    }`} />
                  </div>

                  {/* Title */}
                  <h3 className="text-feature-title text-text-primary mb-2">
                    {step.title}
                  </h3>
                  <p className="text-accent-primary font-medium text-sm mb-4">
                    {step.subtitle}
                  </p>

                  {/* Description */}
                  <p className="text-text-secondary mb-6">
                    {step.description}
                  </p>

                  {/* Details */}
                  <div className="space-y-2 mb-6">
                    {step.details.map((detail, detailIndex) => (
                      <div key={detailIndex} className="flex items-center space-x-2 text-sm">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent-primary" />
                        <span className="text-text-tertiary">{detail}</span>
                      </div>
                    ))}
                  </div>

                  {/* Demo Content */}
                  <div className="glass-card p-4 rounded-lg">
                    <div className="text-xs font-medium text-accent-primary mb-2">
                      {step.demoContent.title}
                    </div>
                    
                    {step.number === 1 && (
                      <div className="space-y-2">
                        {step.demoContent.files?.map((file, fileIndex) => (
                          <div key={fileIndex} className="flex items-center space-x-2 text-xs">
                            <FileText className="w-3 h-3 text-text-tertiary" />
                            <span className="text-text-muted">{file}</span>
                            <div className="w-2 h-2 rounded-full bg-accent-success" />
                          </div>
                        ))}
                      </div>
                    )}

                    {step.number === 2 && (
                      <div className="space-y-2">
                        <div className="flex items-center space-x-2 text-xs">
                          <Brain className="w-3 h-3 text-accent-ai animate-pulse" />
                          <span className="text-text-muted">{step.demoContent.status}</span>
                        </div>
                        <div className="w-full bg-background-elevated rounded-full h-1">
                          <div 
                            className="bg-accent-ai h-1 rounded-full transition-all duration-1000"
                            style={{ width: `${step.demoContent.progress}%` }}
                          />
                        </div>
                      </div>
                    )}

                    {step.number === 3 && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-text-muted">Quality Score:</span>
                          <div className="flex items-center space-x-1">
                            {[...Array(5)].map((_, i) => (
                              <div 
                                key={i} 
                                className={`w-2 h-2 rounded-full ${i < 4 ? "bg-accent-success" : "bg-background-elevated"}`} 
                              />
                            ))}
                            <span className="text-accent-success font-medium ml-1">
                              {step.demoContent.quality}/10
                            </span>
                          </div>
                        </div>
                        <div className="text-xs text-accent-success">{step.demoContent.status}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="text-center">
          <Button className="btn-hero group">
            <Zap className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
            Try It Now - It's Free
          </Button>
          <p className="text-text-tertiary text-sm mt-4">
            No credit card required • Generate your first post in under 2 minutes
          </p>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;