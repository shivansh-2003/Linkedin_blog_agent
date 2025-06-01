
import { Card, CardContent } from '@/components/ui/card';

const useCases = [
  {
    title: 'Developers',
    description: 'Share coding insights and tutorials',
    icon: '👨‍💻',
    gradient: 'from-blue-500 to-cyan-500'
  },
  {
    title: 'Researchers',
    description: 'Transform papers into digestible content',
    icon: '🔬',
    gradient: 'from-purple-500 to-pink-500'
  },
  {
    title: 'Speakers',
    description: 'Convert presentations to engaging posts',
    icon: '🎤',
    gradient: 'from-green-500 to-emerald-500'
  },
  {
    title: 'Entrepreneurs',
    description: 'Share business learnings and insights',
    icon: '🚀',
    gradient: 'from-orange-500 to-red-500'
  },
  {
    title: 'Consultants',
    description: 'Showcase expertise and case studies',
    icon: '💼',
    gradient: 'from-indigo-500 to-purple-500'
  },
  {
    title: 'Educators',
    description: 'Create educational content from materials',
    icon: '📚',
    gradient: 'from-cyan-500 to-blue-500'
  }
];

const UseCasesSection = () => {
  return (
    <section className="py-20 bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Perfect for Every{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Professional
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Whether you're sharing expertise or building your personal brand
          </p>
        </div>

        <div className="mt-16 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {useCases.map((useCase, index) => (
            <Card key={index} className="group relative overflow-hidden border-0 shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
              <div className={`absolute inset-0 bg-gradient-to-br ${useCase.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-10`}></div>
              <CardContent className="relative p-6 text-center">
                <div className={`inline-flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-r ${useCase.gradient} text-3xl mb-4 shadow-lg`}>
                  {useCase.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {useCase.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {useCase.description}
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default UseCasesSection;
