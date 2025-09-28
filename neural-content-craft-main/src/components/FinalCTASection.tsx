import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Zap, Sparkles, CheckCircle, ArrowRight, Clock, Target, TrendingUp } from "lucide-react";

const FinalCTASection = () => {
  const [email, setEmail] = useState("");

  const benefits = [
    {
      icon: Clock,
      text: "Save 25+ minutes per post"
    },
    {
      icon: Target,
      text: "Professional quality guaranteed"
    },
    {
      icon: TrendingUp,
      text: "Boost engagement by 300%+"
    }
  ];

  const guarantees = [
    "✅ Free to start - no credit card required",
    "✅ 25+ file formats supported", 
    "✅ LinkedIn-optimized content",
    "✅ Quality score guarantee",
    "✅ Human-in-the-loop refinement",
    "✅ Export ready-to-publish posts"
  ];

  return (
    <section className="py-20 bg-background-primary relative overflow-hidden">
      {/* Background Elements */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-20 left-20 w-64 h-64 bg-accent-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-20 w-96 h-96 bg-accent-ai/20 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Main Headline */}
          <div className="mb-8">
            <h2 className="text-5xl md:text-6xl font-bold text-text-primary mb-6">
              Ready to <span className="gradient-text-primary">Transform</span>
              <br />
              Your Content Strategy?
            </h2>
            <p className="text-body-large max-w-2xl mx-auto">
              Join thousands of professionals who've revolutionized their LinkedIn presence. 
              Start creating viral content in minutes, not hours.
            </p>
          </div>

          {/* Benefits Row */}
          <div className="flex flex-wrap justify-center gap-8 mb-12">
            {benefits.map((benefit, index) => (
              <div
                key={benefit.text}
                className={`glass-card px-6 py-4 rounded-full flex items-center space-x-3 hover-scale stagger-${index + 1}`}
              >
                <benefit.icon className="w-5 h-5 text-accent-primary" />
                <span className="text-text-secondary font-medium whitespace-nowrap">
                  {benefit.text}
                </span>
                <CheckCircle className="w-4 h-4 text-accent-success" />
              </div>
            ))}
          </div>

          {/* Main CTA */}
          <div className="glass-card-elevated p-12 rounded-3xl mb-12">
            <div className="max-w-2xl mx-auto">
              <h3 className="text-3xl font-bold text-text-primary mb-6">
                Start Creating Amazing Content Today
              </h3>
              
              {/* Email Input */}
              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email to get started"
                  className="flex-1 px-6 py-4 rounded-xl bg-background-elevated border border-border-primary text-text-primary placeholder-text-muted focus:outline-none focus:ring-2 focus:ring-accent-primary text-lg"
                />
                <Button className="btn-hero text-lg px-8 py-4 group">
                  <Zap className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
                  Start Free Now
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                </Button>
              </div>

              <p className="text-text-tertiary text-sm mb-8">
                No credit card required • Generate your first post in under 2 minutes
              </p>

              {/* Guarantees Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-left">
                {guarantees.map((guarantee, index) => (
                  <div
                    key={index}
                    className="flex items-center space-x-3 text-sm"
                  >
                    <span className="text-accent-success">{guarantee}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Alternative CTA */}
          <div className="text-center">
            <p className="text-text-secondary mb-4">
              Want to see it in action first?
            </p>
            <Button variant="outline" className="btn-ghost group">
              <Sparkles className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform" />
              Watch 2-Minute Demo
            </Button>
          </div>

          {/* Social Proof */}
          <div className="mt-16 pt-12 border-t border-border-primary">
            <p className="text-text-tertiary text-sm mb-8">
              Trusted by professionals at
            </p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              {["🏢 TechCorp", "🔬 InnovateLab", "📊 DataDrive", "☁️ CloudSync", "🤖 AI Solutions", "💎 Digital Edge"].map((company) => (
                <div key={company} className="text-text-muted font-medium">
                  {company}
                </div>
              ))}
            </div>
          </div>

          {/* Value Proposition Reminder */}
          <div className="mt-16">
            <div className="glass-card p-6 rounded-2xl max-w-3xl mx-auto">
              <h4 className="text-xl font-bold text-text-primary mb-4">
                🚀 What You Get Starting Today:
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm">
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent-primary mb-1">5 min</div>
                  <div className="text-text-secondary">Per post creation</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent-success mb-1">8.5/10</div>
                  <div className="text-text-secondary">Average quality score</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-accent-ai mb-1">300%+</div>
                  <div className="text-text-secondary">Engagement increase</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTASection;