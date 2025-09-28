import { useEffect } from "react";
import Navigation from "@/components/Navigation";
import ThreeBackground from "@/components/ThreeBackground";
import HeroSection from "@/components/HeroSection";
import SocialProofSection from "@/components/SocialProofSection";
import ProblemSection from "@/components/ProblemSection";
import SolutionSection from "@/components/SolutionSection";
import FeaturesSection from "@/components/FeaturesSection";
import HowItWorksSection from "@/components/HowItWorksSection";
import UseCasesSection from "@/components/UseCasesSection";
import TestimonialsSection from "@/components/TestimonialsSection";
import FinalCTASection from "@/components/FinalCTASection";
import Footer from "@/components/Footer";

const Index = () => {
  useEffect(() => {
    // Smooth scroll behavior for anchor links
    const handleAnchorClick = (e: Event) => {
      const target = e.target as HTMLAnchorElement;
      if (target.hash) {
        e.preventDefault();
        const element = document.querySelector(target.hash);
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };

    document.addEventListener('click', handleAnchorClick);
    return () => document.removeEventListener('click', handleAnchorClick);
  }, []);

  return (
    <div className="min-h-screen bg-background-primary">
      {/* Three.js Background */}
      <ThreeBackground />
      
      {/* Navigation */}
      <Navigation />
      
      {/* Main Content */}
      <main>
        {/* Hero Section */}
        <HeroSection />
        
        {/* Social Proof */}
        <SocialProofSection />
        
        {/* Problem Statement */}
        <ProblemSection />
        
        {/* Solution Overview */}
        <SolutionSection />
        
        {/* Key Features */}
        <FeaturesSection />
        
        {/* How It Works */}
        <HowItWorksSection />
        
        {/* Use Cases */}
        <UseCasesSection />
        
        {/* Testimonials */}
        <TestimonialsSection />
        
        {/* Final CTA */}
        <FinalCTASection />
      </main>
      
      {/* Footer */}
      <Footer />
    </div>
  );
};

export default Index;
