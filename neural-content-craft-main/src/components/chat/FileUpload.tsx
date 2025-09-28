import React, { useState, useRef, useCallback, useEffect } from 'react';
import { Upload, FileText, Code, Image, File, X, Check, AlertCircle, FileImage, FileVideo, FileAudio, Archive, Database, Globe } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { apiService, IngestionResponse } from '@/services/api';

interface FileUploadProps {
  onFileUpload: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // in MB
  acceptedTypes?: string[];
}

interface UploadedFile {
  file: File;
  id: string;
  status: 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
  analysisResults?: IngestionResponse;
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  maxFiles = 10,
  maxSize = 50,
  acceptedTypes = [
    '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.md',
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
    '.jpg', '.jpeg', '.png', '.gif', '.webp',
    '.json', '.xml', '.csv', '.yaml', '.yml'
  ]
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [aggregationStrategy, setAggregationStrategy] = useState<'synthesis' | 'comparison' | 'sequence' | 'timeline'>('synthesis');
  const [showFormatSupport, setShowFormatSupport] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    // Document types
    if (['pdf', 'doc', 'docx', 'txt', 'md', 'rtf'].includes(extension || '')) {
      return <FileText className="w-6 h-6 text-accent-primary" />;
    }
    // Code files
    if (['py', 'js', 'ts', 'jsx', 'tsx', 'java', 'cpp', 'c', 'cs', 'php', 'rb', 'go', 'rs'].includes(extension || '')) {
      return <Code className="w-6 h-6 text-accent-success" />;
    }
    // Images
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'tiff'].includes(extension || '')) {
      return <Image className="w-6 h-6 text-accent-warning" />;
    }
    // Presentations
    if (['ppt', 'pptx', 'key', 'odp'].includes(extension || '')) {
      return <FileImage className="w-6 h-6 text-accent-secondary" />;
    }
    // Videos
    if (['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'].includes(extension || '')) {
      return <FileVideo className="w-6 h-6 text-accent-error" />;
    }
    // Audio
    if (['mp3', 'wav', 'flac', 'aac', 'ogg'].includes(extension || '')) {
      return <FileAudio className="w-6 h-6 text-accent-ai" />;
    }
    // Archives
    if (['zip', 'rar', '7z', 'tar', 'gz'].includes(extension || '')) {
      return <Archive className="w-6 h-6 text-text-tertiary" />;
    }
    // Data files
    if (['csv', 'json', 'xml', 'yaml', 'yml', 'sql', 'db'].includes(extension || '')) {
      return <Database className="w-6 h-6 text-accent-primary" />;
    }
    // Web files
    if (['html', 'htm', 'css', 'scss', 'less'].includes(extension || '')) {
      return <Globe className="w-6 h-6 text-accent-secondary" />;
    }
    
    return <File className="w-6 h-6 text-text-secondary" />;
  };

  const validateFile = (file: File): string | null => {
    if (file.size > maxSize * 1024 * 1024) {
      return `File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max size is ${maxSize}MB.`;
    }
    
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(extension)) {
      return `Unsupported file type (${extension}). Please use supported formats.`;
    }
    
    return null;
  };

  const processFiles = useCallback(async (files: FileList) => {
    const validFiles: File[] = [];
    const newUploadedFiles: UploadedFile[] = [];

    Array.from(files).forEach(file => {
      const error = validateFile(file);
      const uploadedFile: UploadedFile = {
        file,
        id: Date.now().toString() + Math.random(),
        status: error ? 'error' : 'uploading',
        progress: error ? 0 : 20,
        error
      };

      newUploadedFiles.push(uploadedFile);
      if (!error) validFiles.push(file);
    });

    setUploadedFiles(prev => [...prev, ...newUploadedFiles]);

    // Show toast for errors
    const errorCount = newUploadedFiles.filter(f => f.status === 'error').length;
    if (errorCount > 0) {
      toast({
        title: "Upload Issues",
        description: `${errorCount} file${errorCount > 1 ? 's' : ''} couldn't be uploaded. Check file sizes and formats.`,
        variant: "destructive",
      });
    }

    // Process each valid file through the API
    for (const uploadedFile of newUploadedFiles) {
      if (uploadedFile.status !== 'error') {
        try {
          // Update status to processing
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadedFile.id 
              ? { ...f, status: 'processing', progress: 50 }
              : f
          ));

          // Upload and process file through API
          const result = await apiService.uploadFile(uploadedFile.file);
          
          // Update with successful results
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadedFile.id 
              ? { 
                  ...f, 
                  status: result.success ? 'success' : 'error',
                  progress: 100,
                  error: result.success ? undefined : result.error,
                  analysisResults: result.success ? result : undefined
                }
              : f
          ));

          if (result.success) {
            toast({
              title: "File Processed Successfully",
              description: `${uploadedFile.file.name} has been analyzed and is ready for blog generation.`,
            });
          } else {
            toast({
              title: "Processing Failed",
              description: `Failed to process ${uploadedFile.file.name}: ${result.error}`,
              variant: "destructive",
            });
          }

        } catch (error) {
          // Handle API errors
          setUploadedFiles(prev => prev.map(f => 
            f.id === uploadedFile.id 
              ? { 
                  ...f, 
                  status: 'error', 
                  progress: 0,
                  error: error instanceof Error ? error.message : 'Unknown error occurred'
                }
              : f
          ));

          toast({
            title: "Upload Failed",
            description: `Failed to upload ${uploadedFile.file.name}: ${error instanceof Error ? error.message : 'Unknown error'}`,
            variant: "destructive",
          });
        }
      }
    }

    // Call onFileUpload callback with successfully processed files
    const successfulFiles = newUploadedFiles
      .filter(f => f.status === 'success')
      .map(f => f.file);
    
    if (successfulFiles.length > 0) {
      onFileUpload(successfulFiles);
    }
  }, [onFileUpload, maxSize, acceptedTypes, toast]);

  const getFileType = (filename: string): string => {
    const extension = filename.split('.').pop()?.toLowerCase() || '';
    if (['pdf', 'doc', 'docx'].includes(extension)) return 'document';
    if (['ppt', 'pptx'].includes(extension)) return 'presentation';
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension)) return 'image';
    if (['py', 'js', 'ts', 'jsx', 'tsx', 'java', 'cpp', 'c'].includes(extension)) return 'code';
    if (['txt', 'md'].includes(extension)) return 'text';
    return 'other';
  };

  const getFocusAreaFromFile = (file: File): string => {
    const extension = file.name.split('.').pop()?.toLowerCase();
    
    if (['pdf', 'doc', 'docx'].includes(extension || '')) {
      return 'Document Analysis';
    } else if (['py', 'js', 'ts', 'java'].includes(extension || '')) {
      return 'Code Review';
    } else if (['jpg', 'png', 'gif'].includes(extension || '')) {
      return 'Visual Content';
    } else if (['ppt', 'pptx'].includes(extension || '')) {
      return 'Presentation Analysis';
    } else if (['mp4', 'avi', 'mov'].includes(extension || '')) {
      return 'Video Content';
    } else if (['csv', 'json', 'xml'].includes(extension || '')) {
      return 'Data Analysis';
    }
    
    return 'Content Processing';
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragCounter(0);
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      processFiles(files);
    }
  }, [processFiles]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragCounter(prev => prev + 1);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragCounter(prev => prev - 1);
    if (dragCounter <= 1) {
      setIsDragging(false);
    }
  }, [dragCounter]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      processFiles(files);
    }
  };

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const browseFiles = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-4">
      {/* Upload Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        className={`
          glass-card border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-300 relative overflow-hidden
          ${isDragging 
            ? 'border-accent-primary bg-accent-primary/10 scale-[1.02] shadow-glow' 
            : 'border-accent-primary/30 hover:border-accent-primary/60 hover:bg-accent-primary/5'
          }
        `}
        onClick={browseFiles}
      >
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className={`
              w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300
              ${isDragging 
                ? 'bg-accent-primary/20 animate-pulse' 
                : 'bg-background-elevated hover:bg-accent-primary/10'
              }
            `}>
              <Upload className={`w-8 h-8 transition-colors duration-300 ${
                isDragging ? 'text-accent-primary' : 'text-text-secondary'
              }`} />
            </div>
          </div>
          
          <div>
            <h3 className="text-lg font-semibold text-text-primary mb-2">
              {isDragging ? '⬇️ Drop Files Here!' : '📂 Upload Your Content'}
            </h3>
            <p className="text-text-secondary mb-4">
              {isDragging 
                ? 'Release to upload files'
                : 'Drag & drop files here or click to browse'
              }
            </p>
            
            <div className="flex justify-center space-x-4 text-sm text-text-tertiary mb-4">
              <span>📄 Documents</span>
              <span>💻 Code</span>
              <span>📊 Presentations</span>
              <span>🖼️ Media</span>
              <span>📊 Data</span>
            </div>
            
            <div className="flex justify-center space-x-6 text-xs text-text-muted mb-4">
              <span>✨ Max {maxSize}MB</span>
              <span>•</span>
              <span>📁 Multiple files</span>
              <span>•</span>
              <span>🎯 AI Analysis</span>
            </div>

            <div className="flex justify-center space-x-4">
              <button className="px-4 py-2 bg-accent-primary/10 text-accent-primary rounded-lg text-sm font-medium hover:bg-accent-primary/20 transition-colors">
                📎 Browse Files
              </button>
              <button 
                className="px-4 py-2 bg-background-elevated text-text-secondary rounded-lg text-sm font-medium hover:bg-background-elevated/80 transition-colors"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowFormatSupport(!showFormatSupport);
                }}
              >
                📋 Supported Formats
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Format Support Modal */}
      {showFormatSupport && (
        <div className="glass-card rounded-xl p-6 border border-accent-primary/20 animate-[slideInUp_0.3s_ease-out]">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-text-primary">📋 Supported File Types</h4>
            <button
              onClick={() => setShowFormatSupport(false)}
              className="text-text-muted hover:text-text-primary transition-colors"
            >
              ✕
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-accent-primary" />
                <span className="font-medium text-text-primary">Documents</span>
              </div>
              <p className="text-xs text-text-tertiary">PDF, Word, Text, Markdown, RTF</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Code className="w-5 h-5 text-accent-success" />
                <span className="font-medium text-text-primary">Code Files</span>
              </div>
              <p className="text-xs text-text-tertiary">Python, JavaScript, TypeScript, Java, C++, PHP, Go, Rust</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <FileImage className="w-5 h-5 text-accent-secondary" />
                <span className="font-medium text-text-primary">Presentations</span>
              </div>
              <p className="text-xs text-text-tertiary">PowerPoint, Keynote, OpenDocument</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Image className="w-5 h-5 text-accent-warning" />
                <span className="font-medium text-text-primary">Images</span>
              </div>
              <p className="text-xs text-text-tertiary">JPG, PNG, GIF, WebP, SVG, BMP, TIFF</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Database className="w-5 h-5 text-accent-primary" />
                <span className="font-medium text-text-primary">Data Files</span>
              </div>
              <p className="text-xs text-text-tertiary">CSV, JSON, XML, YAML, SQL</p>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center space-x-2">
                <Globe className="w-5 h-5 text-accent-secondary" />
                <span className="font-medium text-text-primary">Web Files</span>
              </div>
              <p className="text-xs text-text-tertiary">HTML, CSS, SCSS, LESS</p>
            </div>
          </div>
        </div>
      )}

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-text-primary">📊 Processing Files</h4>
            <div className="text-xs text-text-tertiary">
              {uploadedFiles.filter(f => f.status === 'success').length} of {uploadedFiles.length} complete
            </div>
          </div>
          
          {uploadedFiles.map(uploadedFile => (
            <div
              key={uploadedFile.id}
              className={`
                glass-card rounded-lg border transition-all duration-300 overflow-hidden
                ${uploadedFile.status === 'error' 
                  ? 'bg-accent-error/10 border-accent-error/30' 
                  : uploadedFile.status === 'success'
                  ? 'bg-accent-success/10 border-accent-success/30'
                  : 'bg-background-elevated border-border-secondary'
                }
              `}
            >
              <div className="p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      {getFileIcon(uploadedFile.file)}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-text-primary truncate">
                        {uploadedFile.file.name}
                      </p>
                      <p className="text-xs text-text-tertiary">
                        {formatFileSize(uploadedFile.file.size)} • {uploadedFile.file.type || 'Unknown type'}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {uploadedFile.status === 'success' && (
                      <div className="flex items-center space-x-1 text-accent-success">
                        <Check className="w-4 h-4" />
                        <span className="text-xs">Complete</span>
                      </div>
                    )}
                    {uploadedFile.status === 'error' && (
                      <div className="flex items-center space-x-1 text-accent-error">
                        <AlertCircle className="w-4 h-4" />
                        <span className="text-xs">Error</span>
                      </div>
                    )}
                    {uploadedFile.status === 'processing' && (
                      <div className="flex items-center space-x-1 text-accent-warning">
                        <div className="w-4 h-4 border-2 border-accent-warning border-t-transparent rounded-full animate-spin" />
                        <span className="text-xs">Processing</span>
                      </div>
                    )}
                    {uploadedFile.status === 'uploading' && (
                      <div className="flex items-center space-x-1 text-accent-primary">
                        <div className="w-4 h-4 border-2 border-accent-primary border-t-transparent rounded-full animate-spin" />
                        <span className="text-xs">Uploading</span>
                      </div>
                    )}
                    
                    <button
                      onClick={() => removeFile(uploadedFile.id)}
                      className="text-text-muted hover:text-accent-error transition-colors p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Progress Bar */}
                {uploadedFile.status !== 'error' && (
                  <div className="mb-3">
                    <div className="w-full bg-background-elevated rounded-full h-2">
                      <div
                        className="h-2 bg-gradient-to-r from-accent-primary to-accent-secondary rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${uploadedFile.progress}%` }}
                      />
                    </div>
                    <div className="flex justify-between mt-1">
                      <span className="text-xs text-text-muted">{uploadedFile.progress}% complete</span>
                      {uploadedFile.status === 'uploading' && (
                        <span className="text-xs text-accent-primary">Uploading...</span>
                      )}
                      {uploadedFile.status === 'processing' && (
                        <span className="text-xs text-accent-warning">Analyzing content...</span>
                      )}
                    </div>
                  </div>
                )}
                
                {/* Error Message */}
                {uploadedFile.status === 'error' && uploadedFile.error && (
                  <div className="mb-3 p-3 bg-accent-error/10 border border-accent-error/30 rounded-lg">
                    <p className="text-xs text-accent-error">{uploadedFile.error}</p>
                  </div>
                )}
                
                {/* Analysis Results */}
                {uploadedFile.status === 'success' && uploadedFile.analysisResults && (
                  <div className="bg-accent-success/10 border border-accent-success/30 rounded-lg p-3">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-accent-success">📊</span>
                      <span className="text-sm font-medium text-text-primary">Analysis Complete</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs text-text-secondary">
                      <div>• {uploadedFile.analysisResults.key_insights?.length || 0} key insights</div>
                      <div>• {Math.ceil((uploadedFile.analysisResults.extracted_content?.raw_text?.length || 0) / 1000)} min read</div>
                      <div className="col-span-2">• Type: {uploadedFile.analysisResults.content_type}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Multi-File Aggregation Strategy */}
      {uploadedFiles.filter(f => f.status === 'success').length > 1 && (
        <div className="glass-card rounded-lg p-6 border border-accent-primary/20 animate-[slideInUp_0.3s_ease-out]">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-semibold text-text-primary">📚 Multi-File Aggregation Strategy</h4>
            <div className="text-xs text-text-tertiary">
              {uploadedFiles.filter(f => f.status === 'success').length} files ready
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <label className="cursor-pointer">
              <input
                type="radio"
                name="aggregation"
                value="synthesis"
                checked={aggregationStrategy === 'synthesis'}
                onChange={(e) => setAggregationStrategy(e.target.value as any)}
                className="sr-only"
              />
              <div className={`
                p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]
                ${aggregationStrategy === 'synthesis' 
                  ? 'border-accent-primary bg-accent-primary/10 shadow-glow' 
                  : 'border-border-secondary hover:border-accent-primary/50 hover:bg-accent-primary/5'
                }
              `}>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-2xl">🔄</span>
                  <span className="font-semibold text-text-primary">Synthesis</span>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  Blend insights from all files into unified narrative
                </p>
                <div className="text-xs text-text-tertiary">
                  Best for: Comprehensive posts from diverse sources
                </div>
              </div>
            </label>

            <label className="cursor-pointer">
              <input
                type="radio"
                name="aggregation"
                value="comparison"
                checked={aggregationStrategy === 'comparison'}
                onChange={(e) => setAggregationStrategy(e.target.value as any)}
                className="sr-only"
              />
              <div className={`
                p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]
                ${aggregationStrategy === 'comparison' 
                  ? 'border-accent-primary bg-accent-primary/10 shadow-glow' 
                  : 'border-border-secondary hover:border-accent-primary/50 hover:bg-accent-primary/5'
                }
              `}>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-2xl">⚖️</span>
                  <span className="font-semibold text-text-primary">Comparison</span>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  Compare and contrast findings across sources
                </p>
                <div className="text-xs text-text-tertiary">
                  Best for: Analyzing different approaches or solutions
                </div>
              </div>
            </label>

            <label className="cursor-pointer">
              <input
                type="radio"
                name="aggregation"
                value="sequence"
                checked={aggregationStrategy === 'sequence'}
                onChange={(e) => setAggregationStrategy(e.target.value as any)}
                className="sr-only"
              />
              <div className={`
                p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]
                ${aggregationStrategy === 'sequence' 
                  ? 'border-accent-primary bg-accent-primary/10 shadow-glow' 
                  : 'border-border-secondary hover:border-accent-primary/50 hover:bg-accent-primary/5'
                }
              `}>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-2xl">📈</span>
                  <span className="font-semibold text-text-primary">Sequence</span>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  Create sequential story from multiple sources
                </p>
                <div className="text-xs text-text-tertiary">
                  Best for: Step-by-step tutorials or processes
                </div>
              </div>
            </label>

            <label className="cursor-pointer">
              <input
                type="radio"
                name="aggregation"
                value="timeline"
                checked={aggregationStrategy === 'timeline'}
                onChange={(e) => setAggregationStrategy(e.target.value as any)}
                className="sr-only"
              />
              <div className={`
                p-4 rounded-lg border transition-all duration-200 hover:scale-[1.02]
                ${aggregationStrategy === 'timeline' 
                  ? 'border-accent-primary bg-accent-primary/10 shadow-glow' 
                  : 'border-border-secondary hover:border-accent-primary/50 hover:bg-accent-primary/5'
                }
              `}>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-2xl">📅</span>
                  <span className="font-semibold text-text-primary">Timeline</span>
                </div>
                <p className="text-sm text-text-secondary mb-2">
                  Chronological narrative from multiple sources
                </p>
                <div className="text-xs text-text-tertiary">
                  Best for: Historical analysis or project evolution
                </div>
              </div>
            </label>
          </div>

          <div className="flex justify-center mt-6 space-x-3">
            <button className="px-6 py-2 bg-background-elevated text-text-primary rounded-lg font-medium hover:bg-background-elevated/80 transition-colors border border-border-primary">
              📋 Preview Strategy
            </button>
            <button className="px-6 py-2 bg-gradient-to-r from-accent-primary to-primary text-background-primary rounded-lg font-medium hover:shadow-glow hover:scale-105 transition-all">
              ⚡ Start Processing
            </button>
          </div>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept={acceptedTypes.join(',')}
        onChange={handleFileSelect}
        className="hidden"
      />
    </div>
  );
};

export default FileUpload;