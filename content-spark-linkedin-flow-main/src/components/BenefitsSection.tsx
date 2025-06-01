
const benefits = [
  {
    icon: '⏱️',
    title: 'Save 90% time on content creation',
    description: 'Transform hours of writing into minutes of refinement'
  },
  {
    icon: '📈',
    title: 'Increase engagement with AI-optimized posts',
    description: 'Leverage data-driven insights for viral content'
  },
  {
    icon: '🎯',
    title: 'Multi-format content support',
    description: 'Process any type of content seamlessly'
  },
  {
    icon: '🧠',
    title: 'Human creativity + AI efficiency',
    description: 'Perfect collaboration between human insight and AI power'
  },
  {
    icon: '📊',
    title: 'Data-driven posting recommendations',
    description: 'Optimize timing, hashtags, and format for maximum reach'
  },
  {
    icon: '🔒',
    title: 'Secure processing with no data retention',
    description: 'Your content is processed securely and never stored'
  }
];

const BenefitsSection = () => {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Why Choose Our{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI Assistant?
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Experience the future of content creation with measurable results
          </p>
        </div>

        <div className="mt-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {benefits.map((benefit, index) => (
            <div key={index} className="relative group">
              <div className="flex items-start space-x-4 p-6 rounded-2xl transition-all duration-300 hover:bg-gray-50">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 flex items-center justify-center rounded-xl bg-gradient-to-r from-blue-100 to-purple-100 text-2xl group-hover:scale-110 transition-transform duration-300">
                    {benefit.icon}
                  </div>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    {benefit.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {benefit.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;
