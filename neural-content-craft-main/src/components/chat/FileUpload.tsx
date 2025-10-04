import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, Code, Image, File, X, Check, AlertCircle, Loader } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

interface FileUploadProps {
  onFileUpload: (files: File[]) => void;
  maxFiles?: number;
  maxSize?: number; // in MB
  compactMode?: boolean;
}

interface SelectedFile {
  file: File;
  id: string;
  valid: boolean;
  error?: string;
  uploading?: boolean;
  progress?: number;
}

// ============================================================================
// COMPONENT
// ============================================================================

const FileUpload: React.FC<FileUploadProps> = ({
  onFileUpload,
  maxFiles = 5,
  maxSize = 50,
  compactMode = false,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const acceptedTypes = [
    '.pdf',
    '.doc',
    '.docx',
    '.ppt',
    '.pptx',
    '.txt',
    '.md',
    '.py',
    '.js',
    '.ts',
    '.jsx',
    '.tsx',
    '.java',
    '.cpp',
    '.c',
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.webp',
    '.json',
    '.xml',
    '.csv',
    '.yaml',
    '.yml',
  ];

  // ==========================================================================
  // HELPERS
  // ==========================================================================

  const getFileIcon = (file: File) => {
    const extension = file.name.split('.').pop()?.toLowerCase();

    if (['pdf', 'doc', 'docx', 'txt', 'md', 'ppt', 'pptx'].includes(extension || '')) {
      return <FileText className="w-5 h-5 text-accent-primary" />;
    }
    if (['py', 'js', 'ts', 'jsx', 'tsx', 'java', 'cpp', 'c'].includes(extension || '')) {
      return <Code className="w-5 h-5 text-accent-success" />;
    }
    if (['jpg', 'jpeg', 'png', 'gif', 'webp'].includes(extension || '')) {
      return <Image className="w-5 h-5 text-accent-warning" />;
    }
    return <File className="w-5 h-5 text-text-secondary" />;
  };

  const validateFile = (file: File): string | null => {
    // Check file size
    if (file.size > maxSize * 1024 * 1024) {
      return `File too large (${(file.size / 1024 / 1024).toFixed(1)}MB). Max size is ${maxSize}MB.`;
    }

    // Check file type
    const extension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(extension)) {
      return `Unsupported file type (${extension}).`;
    }

    return null;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  // ==========================================================================
  // EVENT HANDLERS
  // ==========================================================================

  const processFiles = useCallback(
    (files: FileList) => {
      const newFiles: SelectedFile[] = [];

      Array.from(files).forEach((file) => {
        const error = validateFile(file);
        newFiles.push({
          file,
          id: Date.now().toString() + Math.random(),
          valid: !error,
          error,
        });
      });

      setSelectedFiles((prev) => [...prev, ...newFiles].slice(0, maxFiles));

      const errorCount = newFiles.filter((f) => !f.valid).length;
      if (errorCount > 0) {
        toast({
          title: 'Some Files Invalid',
          description: `${errorCount} file${
            errorCount > 1 ? 's' : ''
          } couldn't be added. Check file sizes and formats.`,
          variant: 'destructive',
        });
      }
    },
    [maxFiles, toast]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files.length > 0) {
        processFiles(files);
      }
    },
    [processFiles]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      processFiles(files);
    }
  };

  const removeFile = (fileId: string) => {
    setSelectedFiles((prev) => prev.filter((f) => f.id !== fileId));
  };

  const handleUpload = () => {
    const validFiles = selectedFiles.filter((f) => f.valid).map((f) => f.file);

    if (validFiles.length === 0) {
      toast({
        title: 'No Valid Files',
        description: 'Please select valid files to upload.',
        variant: 'destructive',
      });
      return;
    }

    onFileUpload(validFiles);
    setSelectedFiles([]);
  };

  // ==========================================================================
  // RENDER
  // ==========================================================================

  return (
    <div className={`space-y-3 ${compactMode ? 'space-y-2' : 'space-y-3'}`}>
      {/* Upload Zone */}
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`
          glass-card border-2 border-dashed rounded-2xl text-center cursor-pointer transition-all duration-300
          ${compactMode ? 'p-6' : 'p-8'}
          ${
            isDragging
              ? 'border-accent-primary bg-accent-primary/10 scale-[1.01] shadow-glow'
              : 'border-border-secondary hover:border-accent-primary/60 hover:bg-accent-primary/5'
          }
        `}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="space-y-4">
          <div className="flex justify-center">
            <div
              className={`
              ${compactMode ? 'w-14 h-14' : 'w-16 h-16'} rounded-full flex items-center justify-center transition-all duration-300
              ${
                isDragging
                  ? 'bg-accent-primary/20 scale-110 animate-pulse'
                  : 'bg-background-elevated'
              }
            `}
            >
              <Upload
                className={`${compactMode ? 'w-7 h-7' : 'w-8 h-8'} ${
                  isDragging ? 'text-accent-primary' : 'text-text-secondary'
                }`}
              />
            </div>
          </div>

          <div>
            <h3 className={`font-semibold text-text-primary mb-1 ${compactMode ? 'text-base' : 'text-lg'}`}>
              {isDragging ? '⬇️ Drop Files Here' : '📂 Upload Content'}
            </h3>
            <p className="text-sm text-text-secondary mb-3">
              {isDragging ? 'Release to add files' : 'Drag & drop or click to browse'}
            </p>

            <div className="flex justify-center flex-wrap gap-3 text-sm text-text-tertiary mb-2">
              <span>📄 Docs</span>
              <span>💻 Code</span>
              <span>🖼️ Images</span>
              <span>📊 Data</span>
            </div>

            <div className="flex justify-center gap-4 text-xs text-text-muted">
              <span>Max {maxSize}MB per file</span>
              <span>•</span>
              <span>Up to {maxFiles} files</span>
            </div>
          </div>
        </div>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium text-text-primary">
              📎 Selected Files ({selectedFiles.length}/{maxFiles})
            </h4>
            <button
              onClick={() => setSelectedFiles([])}
              className="text-xs text-text-muted hover:text-accent-error transition-colors"
            >
              Clear All
            </button>
          </div>

          {selectedFiles.map((selectedFile) => (
            <div
              key={selectedFile.id}
              className={`
                glass-card rounded-lg p-3 border transition-all duration-200
                ${
                  selectedFile.valid
                    ? 'border-border-secondary hover:border-accent-primary/50'
                    : 'border-accent-error/30 bg-accent-error/5'
                }
              `}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3 flex-1 min-w-0">
                  <div className="flex-shrink-0">{getFileIcon(selectedFile.file)}</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-text-primary truncate">
                      {selectedFile.file.name}
                    </p>
                    <p className="text-xs text-text-tertiary">
                      {formatFileSize(selectedFile.file.size)}
                    </p>
                    {selectedFile.error && (
                      <p className="text-xs text-accent-error mt-1">{selectedFile.error}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2 flex-shrink-0">
                  {selectedFile.uploading ? (
                    <Loader className="w-4 h-4 text-accent-primary animate-spin" />
                  ) : selectedFile.valid ? (
                    <Check className="w-4 h-4 text-accent-success" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-accent-error" />
                  )}
                  <button
                    onClick={() => removeFile(selectedFile.id)}
                    className="text-text-muted hover:text-accent-error transition-colors p-1"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={selectedFiles.filter((f) => f.valid).length === 0}
            className={`
              w-full py-3 px-4 rounded-lg font-medium transition-all duration-200
              ${
                selectedFiles.filter((f) => f.valid).length > 0
                  ? 'bg-gradient-to-r from-accent-primary to-primary text-background-primary hover:shadow-glow hover:scale-[1.02]'
                  : 'bg-background-elevated text-text-muted cursor-not-allowed'
              }
            `}
          >
            ⚡ Upload & Analyze {selectedFiles.filter((f) => f.valid).length} File
            {selectedFiles.filter((f) => f.valid).length !== 1 ? 's' : ''}
          </button>
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
