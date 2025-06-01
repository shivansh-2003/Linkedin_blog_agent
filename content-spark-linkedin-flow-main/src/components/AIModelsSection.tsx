
const aiModels = [
  {
    name: 'OpenAI GPT-4',
    description: 'Text and document analysis',
    logo: '🧠',
    color: 'from-green-500 to-emerald-500'
  },
  {
    name: 'Anthropic Claude',
    description: 'Code understanding and blog generation',
    logo: '🔮',
    color: 'from-orange-500 to-red-500'
  },
  {
    name: 'Google Gemini Flash 1.5',
    description: 'Vision and image analysis',
    logo: '👁️',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    name: 'LangGraph',
    description: 'Human-in-the-loop workflow orchestration',
    logo: '🔗',
    color: 'from-purple-500 to-pink-500'
  }
];

const AIModelsSection = () => {
  return (
    <section className="py-20 bg-white">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Powered by Leading{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              AI Technologies
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Built on the most advanced AI models for superior content processing
          </p>
        </div>

        <div className="mt-16 grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {aiModels.map((model, index) => (
            <div key={index} className="group relative">
              <div className="relative rounded-2xl bg-white p-6 shadow-lg transition-all duration-300 hover:shadow-xl hover:-translate-y-2 border border-gray-100">
                <div className={`inline-flex h-16 w-16 items-center justify-center rounded-xl bg-gradient-to-r ${model.color} text-3xl mb-4 shadow-lg`}>
                  {model.logo}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {model.name}
                </h3>
                <p className="text-gray-600 text-sm leading-relaxed">
                  {model.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default AIModelsSection;
