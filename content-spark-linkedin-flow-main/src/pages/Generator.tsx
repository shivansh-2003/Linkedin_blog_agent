
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Copy, Check, ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { toast } from '@/hooks/use-toast';

const Generator = () => {
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showConversation, setShowConversation] = useState(false);
  const [showFinalPost, setShowFinalPost] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [isCopied, setIsCopied] = useState(false);

  const finalPost = "After 6 months of debugging TypeScript generics at 2 AM ☕, I finally cracked the code for building truly scalable React applications. Here's the technical deep-dive that would have saved me countless hours...";

  const handleGenerate = () => {
    setIsProcessing(true);
    setTimeout(() => {
      setIsProcessing(false);
      setShowConversation(true);
    }, 2000);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const fileArray = Array.from(files);
      setUploadedFiles(fileArray);
      toast({
        title: "Files uploaded successfully",
        description: `${fileArray.length} file(s) uploaded`,
      });
    }
  };

  const handleApprove = () => {
    setShowFinalPost(true);
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(finalPost);
      setIsCopied(true);
      toast({
        title: "Copied to clipboard",
        description: "Post has been copied to your clipboard",
      });
      setTimeout(() => setIsCopied(false), 2000);
    } catch (err) {
      toast({
        title: "Failed to copy",
        description: "Could not copy to clipboard",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <Link to="/" className="inline-flex items-center text-blue-600 hover:text-blue-700">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Home
          </Link>
        </div>

        <div className="text-center mb-16">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl">
            Generate Your{' '}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              LinkedIn Post
            </span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-lg text-gray-600">
            Transform your content into engaging LinkedIn posts with AI assistance
          </p>
        </div>

        <div className="mx-auto max-w-4xl">
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
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.ppt,.pptx,.jpg,.jpeg,.png,.gif,.js,.ts,.jsx,.tsx,.py,.java,.cpp,.c,.html,.css,.txt,.md"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload">
                    <Button variant="outline" className="border-blue-300 text-blue-600 hover:bg-blue-50" asChild>
                      <span className="cursor-pointer">Choose Files</span>
                    </Button>
                  </label>
                  {uploadedFiles.length > 0 && (
                    <div className="mt-4">
                      <p className="text-sm text-gray-600 mb-2">Uploaded files:</p>
                      <div className="flex flex-wrap gap-2">
                        {uploadedFiles.map((file, index) => (
                          <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                            {file.name}
                          </span>
                        ))}
                      </div>
                      <Button 
                        onClick={handleGenerate}
                        disabled={isProcessing}
                        className="mt-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                      >
                        {isProcessing ? 'Processing...' : 'Generate Post'}
                      </Button>
                    </div>
                  )}
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
                      {finalPost}
                    </p>
                    <Button 
                      onClick={handleApprove}
                      className="mt-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                    >
                      Approve Final Version
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {showFinalPost && (
            <Card className="mt-8 shadow-lg border-0 bg-gradient-to-r from-green-50 to-emerald-50">
              <CardContent className="p-6">
                <h3 className="text-xl font-semibold mb-6 text-center text-green-800">✅ Final Post Ready!</h3>
                <div className="bg-white rounded-lg p-6 shadow-sm">
                  <p className="text-gray-800 mb-4 leading-relaxed">{finalPost}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-500">Ready to post on LinkedIn</span>
                    <Button 
                      onClick={handleCopy}
                      className={`transition-all duration-300 ${
                        isCopied 
                          ? 'bg-green-600 hover:bg-green-700' 
                          : 'bg-blue-600 hover:bg-blue-700'
                      }`}
                    >
                      {isCopied ? (
                        <>
                          <Check className="mr-2 h-4 w-4" />
                          Copied!
                        </>
                      ) : (
                        <>
                          <Copy className="mr-2 h-4 w-4" />
                          Copy Post
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default Generator;
