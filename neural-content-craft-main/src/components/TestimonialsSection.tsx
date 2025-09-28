import { useState, useEffect } from "react";
import { Star, Quote, ChevronLeft, ChevronRight, TrendingUp, Clock, ThumbsUp } from "lucide-react";

const TestimonialsSection = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);

  const testimonials = [
    {
      id: 1,
      name: "Sarah Chen",
      title: "Marketing Director",
      company: "TechCorp",
      avatar: "👩‍💼",
      rating: 5,
      content: "This tool completely transformed my LinkedIn strategy. I went from struggling to create one post per week to generating high-quality content daily. The AI understands context better than I expected.",
      results: {
        engagement: "500% ↑",
        timeSaved: "25 min → 3 min",
        satisfaction: "Outstanding"
      }
    },
    {
      id: 2,
      name: "Marcus Rodriguez", 
      title: "Senior Developer",
      company: "InnovateStack",
      avatar: "👨‍💻",
      rating: 5,
      content: "As a developer, I struggled to translate technical concepts into engaging LinkedIn posts. BlogAI Assistant bridges that gap perfectly, making my technical insights accessible and engaging.",
      results: {
        engagement: "300% ↑",
        timeSaved: "30 min → 5 min", 
        satisfaction: "Excellent"
      }
    },
    {
      id: 3,
      name: "Dr. Emma Watson",
      title: "Research Director",
      company: "BioTech Solutions",
      avatar: "👩‍🔬",
      rating: 5,
      content: "Turning academic research into LinkedIn content used to be impossible. Now I can share my findings with a broader audience while maintaining scientific accuracy. Game-changer!",
      results: {
        engagement: "450% ↑",
        timeSaved: "45 min → 8 min",
        satisfaction: "Revolutionary"
      }
    },
    {
      id: 4,
      name: "James Liu",
      title: "Content Strategist", 
      company: "Growth Partners",
      avatar: "👨‍💼",
      rating: 5,
      content: "The quality consistency is remarkable. Every post maintains professional standards while feeling authentic. My engagement rates have never been higher, and I'm spending 80% less time on content creation.",
      results: {
        engagement: "650% ↑",
        timeSaved: "40 min → 6 min",
        satisfaction: "Amazing"
      }
    }
  ];

  const stats = [
    {
      icon: TrendingUp,
      value: "500%",
      label: "Avg Engagement Increase",
      description: "Higher likes, comments & shares"
    },
    {
      icon: Clock,
      value: "15 min → 2 min",
      label: "Time Saved Per Post",
      description: "Focus on what matters most"
    },
    {
      icon: ThumbsUp,
      value: "95%",
      label: "Would Recommend", 
      description: "User satisfaction rate"
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);

    return () => clearInterval(interval);
  }, [testimonials.length]);

  const handlePrevious = () => {
    setCurrentTestimonial((prev) => 
      prev === 0 ? testimonials.length - 1 : prev - 1
    );
  };

  const handleNext = () => {
    setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
  };

  const currentUser = testimonials[currentTestimonial];

  return (
    <section id="testimonials" className="py-20 bg-background-primary">
      <div className="container mx-auto px-6">
        <div className="text-center mb-16">
          <h2 className="text-section-title text-text-primary mb-6">
            What Our <span className="gradient-text-primary">Users Say</span>
          </h2>
          <p className="text-body-large max-w-2xl mx-auto">
            Join thousands of professionals who've transformed their LinkedIn presence 
            with AI-powered content creation.
          </p>
        </div>

        {/* Main Testimonial */}
        <div className="max-w-4xl mx-auto mb-16">
          <div className="glass-card-elevated p-12 rounded-3xl relative overflow-hidden">
            {/* Background Quote */}
            <Quote className="absolute top-8 left-8 w-16 h-16 text-accent-primary/10" />
            
            <div className="relative z-10">
              {/* Testimonial Content */}
              <blockquote className="text-2xl md:text-3xl font-light text-text-primary leading-relaxed mb-8 italic">
                "{currentUser.content}"
              </blockquote>

              {/* User Info */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 rounded-full bg-gradient-ai flex items-center justify-center text-2xl">
                    {currentUser.avatar}
                  </div>
                  <div>
                    <div className="text-xl font-semibold text-text-primary">
                      {currentUser.name}
                    </div>
                    <div className="text-accent-primary font-medium">
                      {currentUser.title}
                    </div>
                    <div className="text-text-tertiary">
                      {currentUser.company}
                    </div>
                  </div>
                </div>

                {/* Rating */}
                <div className="flex flex-col items-end">
                  <div className="flex space-x-1 mb-2">
                    {[...Array(currentUser.rating)].map((_, i) => (
                      <Star 
                        key={i} 
                        className="w-6 h-6 text-accent-warning fill-current"
                      />
                    ))}
                  </div>
                  <div className="text-text-tertiary text-sm">
                    {currentUser.rating}/5 stars
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-center mt-8 space-x-6">
            <button
              onClick={handlePrevious}
              className="p-3 rounded-full glass-card hover-scale group"
            >
              <ChevronLeft className="w-6 h-6 text-text-secondary group-hover:text-accent-primary transition-colors" />
            </button>

            {/* Indicators */}
            <div className="flex space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all duration-300 ${
                    index === currentTestimonial 
                      ? "bg-accent-primary w-8" 
                      : "bg-background-elevated hover:bg-accent-primary/50"
                  }`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              className="p-3 rounded-full glass-card hover-scale group"
            >
              <ChevronRight className="w-6 h-6 text-text-secondary group-hover:text-accent-primary transition-colors" />
            </button>
          </div>
        </div>

        {/* Results Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
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
              <div className="text-lg font-semibold text-accent-primary mb-2">
                {stat.label}
              </div>
              <div className="text-sm text-text-tertiary">
                {stat.description}
              </div>
            </div>
          ))}
        </div>

        {/* Individual Results */}
        <div className="mt-12 glass-card p-8 rounded-2xl">
          <h3 className="text-2xl font-bold text-text-primary text-center mb-8">
            Real Results from {currentUser.name}
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-success mb-1">
                {currentUser.results.engagement}
              </div>
              <div className="text-text-secondary">Engagement Increase</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-primary mb-1">
                {currentUser.results.timeSaved}
              </div>
              <div className="text-text-secondary">Time Saved</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-accent-ai mb-1">
                {currentUser.results.satisfaction}
              </div>
              <div className="text-text-secondary">Experience Rating</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;