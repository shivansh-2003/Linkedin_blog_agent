
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';

const CTASection = () => {
  return (
    <section className="py-20 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 relative overflow-hidden">
      <div className="absolute inset-0 bg-black/20"></div>
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/30 to-purple-600/30 blur-3xl"></div>
      </div>
      
      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl lg:text-5xl">
          Start Creating Viral Content Today
        </h2>
        <p className="mx-auto mt-6 max-w-2xl text-xl text-blue-100">
          Free to try - No credit card required
        </p>
        <p className="mx-auto mt-2 max-w-xl text-lg text-blue-200">
          Join 1000+ professionals already using our platform
        </p>

        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link to="/generator">
            <Button 
              size="lg" 
              className="group bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold shadow-lg transition-all duration-300 hover:shadow-xl hover:scale-105"
            >
              Get Started Now
              <ArrowRight className="ml-2 h-5 w-5 transition-transform duration-300 group-hover:translate-x-1" />
            </Button>
          </Link>
        </div>

        <div className="mt-12 grid grid-cols-2 gap-8 md:grid-cols-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-white">1000+</div>
            <div className="text-blue-200">Active Users</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">50K+</div>
            <div className="text-blue-200">Posts Generated</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">95%</div>
            <div className="text-blue-200">Satisfaction Rate</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-white">10M+</div>
            <div className="text-blue-200">Engagements</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTASection;
