
import { ArrowRight } from 'lucide-react';

const steps = [
  {
    icon: '☁️',
    title: 'Upload Content',
    description: 'Upload your PDF, image, code, or presentation file',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    icon: '🧠',
    title: 'AI Analysis',
    description: 'Our AI models extract key insights and valuable information',
    color: 'from-purple-500 to-pink-500'
  },
  {
    icon: '👁️',
    title: 'Human Review',
    description: 'Review the generated post and provide specific feedback',
    color: 'from-green-500 to-emerald-500'
  },
  {
    icon: '✨',
    title: 'Perfect Post',
    description: 'Get your optimized LinkedIn post ready to publish',
    color: 'from-orange-500 to-red-500'
  }
];

const HowItWorksSection = () => {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            From Content to Viral Post in{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Minutes
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Our streamlined process makes content transformation effortless
          </p>
        </div>

        <div className="mt-16">
          <div className="grid gap-8 lg:grid-cols-4">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <div className="flex flex-col items-center text-center">
                  <div className={`inline-flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r ${step.color} text-3xl text-white shadow-lg mb-6`}>
                    {step.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed max-w-xs">
                    {step.description}
                  </p>
                </div>
                
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-8 left-full w-full">
                    <ArrowRight className="h-6 w-6 text-gray-400 mx-auto" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorksSection;
