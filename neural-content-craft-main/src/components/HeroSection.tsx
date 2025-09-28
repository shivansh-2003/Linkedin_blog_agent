import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Play, FileText, Zap, Target, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";

const HeroSection = () => {
  const [currentText, setCurrentText] = useState("");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTyping, setIsTyping] = useState(true);

  const heroTexts = [
    "Transform Any Content Into",
    "Turn Your Ideas Into", 
    "Convert Your Files Into"
  ];

  const subTexts = [
    "Viral LinkedIn Posts",
    "Engaging Professional Content",
    "High-Quality Blog Posts"
  ];

  useEffect(() => {
    const text = heroTexts[currentIndex];
    if (isTyping) {
      if (currentText.length < text.length) {
        setTimeout(() => {
          setCurrentText(text.slice(0, currentText.length + 1));
        }, 100);
      } else {
        setTimeout(() => setIsTyping(false), 2000);
      }
    } else {
      if (currentText.length > 0) {
        setTimeout(() => {
          setCurrentText(currentText.slice(0, -1));
        }, 50);
      } else {
        setCurrentIndex((prev) => (prev + 1) % heroTexts.length);
        setIsTyping(true);
      }
    }
  }, [currentText, currentIndex, isTyping, heroTexts]);

  const features = [
    { icon: FileText, text: "25+ File Formats" },
    { icon: Zap, text: "AI Analysis" },
    { icon: Target, text: "Quality Score" }
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 pb-16">
      <div className="container mx-auto px-6 text-center">
        <div className="max-w-5xl mx-auto">
          {/* Main Headline */}
          <div className="mb-8">
            <h1 className="text-hero gradient-text-primary mb-4">
              {currentText}
              <span className="animate-pulse">|</span>
            </h1>
            <h2 className="text-hero text-accent-primary mb-6">
              {subTexts[currentIndex]}
            </h2>
          </div>

          {/* Subheadline */}
          <p className="text-body-large max-w-3xl mx-auto mb-12">
            AI-powered blog creation that turns your files, presentations, and ideas 
            into engaging professional content in minutes, not hours.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <Link to="/chat">
              <Button className="btn-hero group">
                <Zap className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
                Start Creating Now
              </Button>
            </Link>
            <Button variant="outline" className="btn-ghost group">
              <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform" />
              Watch Demo
            </Button>
          </div>

          {/* Feature Pills */}
          <div className="flex flex-wrap justify-center gap-6 mb-16">
            {features.map((feature, index) => (
              <div
                key={feature.text}
                className={`glass-card px-6 py-3 rounded-full flex items-center space-x-3 hover-scale stagger-${index + 1}`}
              >
                <feature.icon className="w-5 h-5 text-accent-primary" />
                <span className="text-text-secondary font-medium">{feature.text}</span>
                <CheckCircle className="w-4 h-4 text-accent-success" />
              </div>
            ))}
          </div>

          {/* Demo Preview Card */}
          <div className="glass-card-elevated p-8 rounded-3xl max-w-4xl mx-auto hover-lift">
            <div className="text-left">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-feature-title text-text-primary">
                  📝 Generated LinkedIn Post
                </h3>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-text-tertiary">Quality:</span>
                  <div className="flex space-x-1">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <div
                        key={i}
                        className={`w-3 h-3 rounded-full ${
                          i <= 4 ? "bg-accent-success" : "bg-background-elevated"
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-accent-success font-semibold">8.5/10</span>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <span className="text-accent-primary font-medium">🪝 Hook:</span>
                  <p className="text-text-secondary mt-1">
                    "What if AI could revolutionize your content creation process?"
                  </p>
                </div>

                <div>
                  <span className="text-accent-primary font-medium">📄 Content:</span>
                  <p className="text-text-secondary mt-1">
                    AI is transforming how professionals create content. From research papers 
                    to engaging posts, the future is here...
                  </p>
                </div>

                <div>
                  <span className="text-accent-primary font-medium">🎯 CTA:</span>
                  <p className="text-text-secondary mt-1">
                    "Share your AI content experiences below!"
                  </p>
                </div>

                <div>
                  <span className="text-accent-primary font-medium">🏷️ Tags:</span>
                  <p className="text-accent-ai mt-1">
                    #AIContent #LinkedIn #Innovation #TechTrends #ContentCreation
                  </p>
                </div>
              </div>

              <div className="flex flex-wrap gap-3 mt-6">
                <Button size="sm" className="bg-accent-success/20 text-accent-success hover:bg-accent-success/30">
                  ✅ Approve
                </Button>
                <Button size="sm" variant="outline" className="border-accent-warning text-accent-warning">
                  ✏️ Refine
                </Button>
                <Button size="sm" variant="outline">
                  🔄 Regenerate
                </Button>
                <Button size="sm" variant="outline">
                  📋 Copy
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;