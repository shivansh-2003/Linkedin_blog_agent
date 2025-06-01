
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';

const DemoSection = () => {
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showConversation, setShowConversation] = useState(false);

  const handleGenerate = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setShowConversation(true);
    }, 2000);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Try It Now - See the{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Magic in Action
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Experience the human-in-the-loop AI refinement process
          </p>
        </div>

        <div className="mt-16 mx-auto max-w-4xl">
          <Tabs defaultValue="text" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-8">
              <TabsTrigger value="text" className="text-lg py-3">Text Input</TabsTrigger>
              <TabsTrigger value="upload" className="text-lg py-3">File Upload</TabsTrigger>
            </TabsList>
            
            <TabsContent value="text" className="space-y-6">
              <Card className="border-2 border-dashed border-gray-200 hover:border-blue-300 transition-colors">
                <CardContent className="p-6">
                  <Textarea
                    placeholder="Paste your content here or describe your project, insights, or learning..."
                    value={textInput}
                    onChange={(e) => setTextInput(e.target.value)}
                    className="min-h-[200px] text-lg resize-none border-0 focus:ring-0"
                  />
                  <div className="flex items-center justify-between mt-4">
                    <span className="text-sm text-gray-500">{textInput.length} characters</span>
                    <Button 
                      onClick={handleGenerate}
                      disabled={isProcessing || !textInput.trim()}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                    >
                      {isProcessing ? 'Processing...' : 'Generate Post'}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
            
            <TabsContent value="upload" className="space-y-6">
              <Card className="border-2 border-dashed border-gray-200 hover:border-blue-300 transition-colors">
                <CardContent className="p-12 text-center">
                  <div className="text-6xl mb-4">📁</div>
                  <h3 className="text-xl font-semibold mb-2">Drag and drop your files here</h3>
                  <p className="text-gray-600 mb-6">
                    Supported formats: PDF, PPT, Images (JPG, PNG), Code files, Text files
                  </p>
                  <div className="flex flex-wrap justify-center gap-4 mb-6">
                    <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">PDF</span>
                    <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">PPT</span>
                    <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">Images</span>
                    <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm">Code</span>
                  </div>
                  <Button variant="outline" className="border-blue-300 text-blue-600 hover:bg-blue-50">
                    Choose Files
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {showConversation && (
            <Card className="mt-8 shadow-lg border-0">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-6 text-center">Human-in-the-Loop Refinement</h3>
                <div className="space-y-4">
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="font-medium text-blue-900 mb-2">🤖 AI Generated Post:</p>
                    <p className="text-gray-700">
                      "Just launched my new project! 🚀 Here's what I learned about building scalable applications with React and TypeScript. The key insights that transformed my development process..."
                    </p>
                  </div>
                  
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="font-medium text-green-900 mb-2">👤 Your Feedback:</p>
                    <p className="text-gray-700">
                      "Make it more technical and add a personal story about the challenges I faced"
                    </p>
                  </div>
                  
                  <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                    <p className="font-medium text-purple-900 mb-2">🤖 Refined Post:</p>
                    <p className="text-gray-700">
                      "After 6 months of debugging TypeScript generics at 2 AM ☕, I finally cracked the code for building truly scalable React applications. Here's the technical deep-dive that would have saved me countless hours..."
                    </p>
                    <Button className="mt-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700">
                      Approve Final Version
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </section>
  );
};

export default DemoSection;
