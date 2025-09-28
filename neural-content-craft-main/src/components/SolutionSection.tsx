import { useState, useEffect, useRef } from "react";
import { Brain, Zap, Target, CheckCircle, ArrowRight, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

const SolutionSection = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const sectionRef = useRef<HTMLDivElement>(null);

  const steps = [
    {
      icon: Brain,
      title: "AI Analysis",
      description: "Advanced AI understands your content and extracts key insights"
    },
    {
      icon: Zap,
      title: "Generation", 
      description: "Creates engaging LinkedIn posts optimized for maximum impact"
    },
    {
      icon: Target,
      title: "Optimization",
      description: "Fine-tunes content for LinkedIn algorithm and audience"
    },
    {
      icon: CheckCircle,
      title: "Approval",
      description: "Human-in-the-loop refinement for perfect results"
    }
  ];

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setIsVisible(true);
          
          // Animate through steps
          steps.forEach((_, index) => {
            setTimeout(() => {
              setCurrentStep(index);
            }, index * 800);
          });
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
    <section ref={sectionRef} className="py-20 bg-background-secondary/30">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            Meet Your <span className="gradient-text-primary">AI-Powered</span> Content Assistant
          </h2>
          <p className="text-body-large max-w-3xl mx-auto">
            Our advanced AI understands your content, extracts key insights, and transforms 
            them into engaging LinkedIn posts that drive real professional results.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Left Side - AI Visualization */}
          <div className="relative">
            <div className="glass-card-elevated p-12 rounded-3xl relative overflow-hidden">
              {/* Animated Background */}
              <div className="absolute inset-0 opacity-10">
                <div className="w-full h-full bg-gradient-ai animate-gradient" />
              </div>

              {/* AI Brain Visualization */}
              <div className="relative z-10 text-center">
                <div className="relative mb-8">
                  <div className="w-32 h-32 mx-auto rounded-full bg-gradient-ai/20 flex items-center justify-center animate-glow-pulse">
                    <Brain className="w-16 h-16 text-accent-primary" />
                  </div>
                  
                  {/* Floating Sparkles */}
                  <Sparkles className="w-6 h-6 text-accent-ai absolute top-4 right-8 animate-float" />
                  <Sparkles className="w-4 h-4 text-accent-secondary absolute bottom-6 left-6 animate-float" style={{ animationDelay: '1s' }} />
                  <Sparkles className="w-5 h-5 text-accent-primary absolute top-12 left-4 animate-float" style={{ animationDelay: '2s' }} />
                </div>

                <h3 className="text-2xl font-bold text-text-primary mb-4">
                  Intelligent Content Processing
                </h3>
                <p className="text-text-secondary">
                  Advanced neural networks analyze your content at a deep level, 
                  understanding context, tone, and key insights.
                </p>
              </div>
            </div>
          </div>

          {/* Right Side - Process Steps */}
          <div className="space-y-6">
            {steps.map((step, index) => (
              <div
                key={step.title}
                className={`glass-card p-6 rounded-xl transition-all duration-500 ${
                  isVisible && currentStep >= index
                    ? "opacity-100 transform translate-x-0"
                    : "opacity-50 transform translate-x-8"
                }`}
              >
                <div className="flex items-center space-x-4">
                  <div className={`p-3 rounded-full transition-all duration-300 ${
                    currentStep >= index 
                      ? "bg-accent-primary/20 scale-110" 
                      : "bg-background-elevated"
                  }`}>
                    <step.icon className={`w-6 h-6 ${
                      currentStep >= index ? "text-accent-primary" : "text-text-tertiary"
                    }`} />
                  </div>
                  
                  <div className="flex-1">
                    <h4 className={`font-semibold transition-colors ${
                      currentStep >= index ? "text-text-primary" : "text-text-tertiary"
                    }`}>
                      {index + 1}. {step.title}
                    </h4>
                    <p className={`text-sm transition-colors ${
                      currentStep >= index ? "text-text-secondary" : "text-text-muted"
                    }`}>
                      {step.description}
                    </p>
                  </div>

                  {currentStep >= index && (
                    <CheckCircle className="w-5 h-5 text-accent-success animate-pulse" />
                  )}
                </div>

                {index < steps.length - 1 && (
                  <div className="ml-8 mt-4">
                    <ArrowRight className={`w-5 h-5 transition-colors ${
                      currentStep > index ? "text-accent-primary" : "text-text-muted"
                    }`} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center mt-16">
          <div className="glass-card p-8 rounded-2xl max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-text-primary mb-4">
              Ready to Transform Your Content Strategy?
            </h3>
            <p className="text-text-secondary mb-6">
              Join thousands of professionals who've revolutionized their LinkedIn presence 
              with AI-powered content creation.
            </p>
            <Button className="btn-hero group">
              <Zap className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
              See How It Works
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SolutionSection;