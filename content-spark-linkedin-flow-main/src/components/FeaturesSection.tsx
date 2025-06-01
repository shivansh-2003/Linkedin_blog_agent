
import { Card, CardContent } from '@/components/ui/card';

const features = [
  {
    icon: '📄',
    title: 'Smart Document Processing',
    description: 'Extract key insights from PDFs, research papers, and text using OpenAI GPT-4',
    gradient: 'from-blue-500 to-cyan-500'
  },
  {
    icon: '🖼️',
    title: 'AI Vision Understanding',
    description: 'Analyze charts, diagrams, and infographics with Google Gemini Flash 1.5',
    gradient: 'from-purple-500 to-pink-500'
  },
  {
    icon: '💻',
    title: 'Technical Content Extraction',
    description: 'Transform code projects into educational posts using Anthropic Claude',
    gradient: 'from-green-500 to-emerald-500'
  },
  {
    icon: '📊',
    title: 'PowerPoint & Slide Analysis',
    description: 'Extract insights from presentations with combined text and visual analysis',
    gradient: 'from-orange-500 to-red-500'
  },
  {
    icon: '🔄',
    title: 'Interactive Refinement',
    description: 'Collaborate with AI to perfect your post through iterative feedback',
    gradient: 'from-indigo-500 to-purple-500'
  },
  {
    icon: '🚀',
    title: 'Viral Post Creation',
    description: 'Optimized hooks, formatting, hashtags, and engagement strategies',
    gradient: 'from-cyan-500 to-blue-500'
  }
];

const FeaturesSection = () => {
  return (
    <section className="py-20 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Intelligent Content Processing
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Advanced AI capabilities to transform any content into engaging LinkedIn posts
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <Card key={index} className="group relative overflow-hidden border-0 shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-5`}></div>
              <CardContent className="relative p-8">
                <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r ${feature.gradient} text-2xl mb-6`}>
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
