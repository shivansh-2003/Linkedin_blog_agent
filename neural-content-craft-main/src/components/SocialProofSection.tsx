import { useEffect, useState } from "react";
import { TrendingUp, Users, Award, Star } from "lucide-react";

const SocialProofSection = () => {
  const [counters, setCounters] = useState({
    companies: 0,
    posts: 0,
    successRate: 0,
    rating: 0
  });

  const finalValues = {
    companies: 500,
    posts: 50000,
    successRate: 95,
    rating: 4.9
  };

  useEffect(() => {
    const duration = 2000;
    const steps = 60;
    const interval = duration / steps;

    const incrementCounters = () => {
      let step = 0;
      const timer = setInterval(() => {
        step++;
        const progress = step / steps;
        
        setCounters({
          companies: Math.floor(finalValues.companies * progress),
          posts: Math.floor(finalValues.posts * progress),
          successRate: Math.floor(finalValues.successRate * progress),
          rating: Math.round(finalValues.rating * progress * 10) / 10
        });

        if (step >= steps) {
          clearInterval(timer);
          setCounters(finalValues);
        }
      }, interval);
    };

    // Start animation when component mounts
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          incrementCounters();
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );

    const element = document.getElementById('social-proof');
    if (element) observer.observe(element);

    return () => observer.disconnect();
  }, []);

  const companies = [
    { name: "TechCorp", logo: "🏢" },
    { name: "InnovateLab", logo: "🔬" },
    { name: "DataDrive", logo: "📊" },
    { name: "CloudSync", logo: "☁️" },
    { name: "AI Solutions", logo: "🤖" },
    { name: "Digital Edge", logo: "💎" }
  ];

  const stats = [
    {
      icon: Users,
      value: `${counters.companies}+`,
      label: "Companies Using",
      description: "Professional teams"
    },
    {
      icon: TrendingUp,
      value: `${(counters.posts / 1000).toFixed(0)}K+`,
      label: "Posts Created",
      description: "High-quality content"
    },
    {
      icon: Award,
      value: `${counters.successRate}%`,
      label: "Success Rate",
      description: "Client satisfaction"
    },
    {
      icon: Star,
      value: `${counters.rating}/5`,
      label: "Rating Average",
      description: "User reviews"
    }
  ];

  return (
    <section id="social-proof" className="py-20 bg-background-secondary/50">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-text-primary mb-4">
            Trusted by <span className="gradient-text-primary">10,000+</span> professionals
          </h2>
          <p className="text-body text-text-secondary">
            From leading companies across the globe
          </p>
        </div>

        {/* Company Logos */}
        <div className="flex flex-wrap justify-center items-center gap-8 mb-16 opacity-60">
          {companies.map((company, index) => (
            <div
              key={company.name}
              className={`glass-card px-8 py-4 rounded-lg hover-scale stagger-${(index % 6) + 1}`}
            >
              <div className="flex items-center space-x-3">
                <span className="text-2xl">{company.logo}</span>
                <span className="text-text-secondary font-medium">{company.name}</span>
              </div>
            </div>
          ))}
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, index) => (
            <div
              key={stat.label}
              className={`glass-card-elevated p-8 rounded-2xl text-center hover-lift stagger-${index + 1}`}
            >
              <div className="flex justify-center mb-4">
                <div className="p-3 rounded-full bg-accent-primary/20">
                  <stat.icon className="w-8 h-8 text-accent-primary" />
                </div>
              </div>
              <div className="text-3xl font-bold text-text-primary mb-2">
                {stat.value}
              </div>
              <div className="text-lg font-semibold text-accent-primary mb-1">
                {stat.label}
              </div>
              <div className="text-sm text-text-tertiary">
                {stat.description}
              </div>
            </div>
          ))}
        </div>

        {/* Testimonial Quote */}
        <div className="text-center mt-16">
          <blockquote className="text-2xl md:text-3xl font-light text-text-secondary italic max-w-4xl mx-auto">
            "There has to be a <span className="text-accent-primary font-semibold">better way</span> 
            to create professional content..."
          </blockquote>
          <div className="mt-6 text-text-tertiary">
            — Every content creator, before discovering BlogAI Assistant
          </div>
        </div>
      </div>
    </section>
  );
};

export default SocialProofSection;