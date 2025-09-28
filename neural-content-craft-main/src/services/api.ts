const API_BASE_URL = 'https://linkedin-blog-agent-1.onrender.com';

// Types for API responses
export interface IngestionResponse {
  success: boolean;
  error?: string;
  source_file: string;
  content_type: string;
  ai_analysis?: string;
  key_insights?: string[];
  metadata?: any;
  extracted_content?: {
    content_type: string;
    file_path: string;
    raw_text: string;
    structured_data?: any;
    metadata?: any;
    processing_model: string;
    processing_time: number;
  };
}

export interface BlogResponse {
  success: boolean;
  error?: string;
  blog_post?: {
    title: string;
    hook: string;
    content: string;
    call_to_action: string;
    hashtags: string[];
    target_audience: string;
    engagement_score: number;
    source_file?: string;
    ingestion_analysis?: string;
    aggregation_strategy?: string;
    source_count?: number;
    source_types?: string[];
    unified_insights?: string[];
    cross_references?: any;
  };
  workflow_status?: string;
  iterations?: number;
  quality_score?: number;
}

export interface ChatSessionResponse {
  session_id: string;
  current_stage: string;
  message_count: number;
  blog_context?: any;
  created_at: string;
}

export interface ChatMessageResponse {
  success: boolean;
  response: string;
  session_id: string;
  current_stage: string;
  blog_context?: any;
  error?: string;
}

export interface ChatHistoryResponse {
  session_id: string;
  messages: Array<{
    message_id: string;
    message_type: string;
    content: string;
    timestamp: string;
    metadata?: any;
  }>;
  current_stage: string;
  blog_context?: any;
}

// API Service Class
class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Generic fetch wrapper with error handling
  private async fetchWithErrorHandling<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  // File Upload and Ingestion
  async uploadFile(file: File): Promise<IngestionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/ingest`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Upload failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // Blog Generation from Text
  async generateBlogFromText(
    text: string,
    targetAudience: string = "General professional audience",
    tone: string = "Professional and engaging",
    maxIterations: number = 3
  ): Promise<BlogResponse> {
    return this.fetchWithErrorHandling<BlogResponse>('/api/generate-blog', {
      method: 'POST',
      body: JSON.stringify({
        text,
        target_audience: targetAudience,
        tone,
        max_iterations: maxIterations,
      }),
    });
  }

  // Blog Generation from File
  async generateBlogFromFile(
    file: File,
    targetAudience: string = "General professional audience",
    tone: string = "Professional and engaging",
    maxIterations: number = 3
  ): Promise<BlogResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('target_audience', targetAudience);
    formData.append('tone', tone);
    formData.append('max_iterations', maxIterations.toString());

    const response = await fetch(`${this.baseURL}/api/generate-blog-from-file`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Blog generation failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // Multi-file Aggregation
  async aggregateFiles(
    files: File[],
    aggregationStrategy: string = "synthesis",
    targetAudience: string = "General professional audience",
    tone: string = "Professional and engaging",
    maxIterations: number = 3
  ): Promise<BlogResponse> {
    const formData = new FormData();
    
    files.forEach(file => {
      formData.append('files', file);
    });
    
    formData.append('aggregation_strategy', aggregationStrategy);
    formData.append('target_audience', targetAudience);
    formData.append('tone', tone);
    formData.append('max_iterations', maxIterations.toString());

    const response = await fetch(`${this.baseURL}/api/aggregate`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `File aggregation failed: ${response.statusText}`);
    }

    return await response.json();
  }

  // Chat Session Management
  async startChatSession(): Promise<ChatSessionResponse> {
    return this.fetchWithErrorHandling<ChatSessionResponse>('/api/chat/start', {
      method: 'POST',
    });
  }

  async sendChatMessage(
    message: string,
    sessionId?: string
  ): Promise<ChatMessageResponse> {
    return this.fetchWithErrorHandling<ChatMessageResponse>('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  }

  async getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
    return this.fetchWithErrorHandling<ChatHistoryResponse>(`/api/chat/history/${sessionId}`);
  }

  async submitFeedback(
    sessionId: string,
    feedback: string,
    feedbackType: string = "general"
  ): Promise<ChatMessageResponse> {
    return this.fetchWithErrorHandling<ChatMessageResponse>('/api/chat/feedback', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        feedback,
        feedback_type: feedbackType,
      }),
    });
  }

  async approveBlog(
    sessionId: string,
    approved: boolean,
    finalNotes?: string
  ): Promise<ChatMessageResponse> {
    return this.fetchWithErrorHandling<ChatMessageResponse>('/api/chat/approve', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        approved,
        final_notes: finalNotes,
      }),
    });
  }

  async deleteChatSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    return this.fetchWithErrorHandling(`/api/chat/session/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async listChatSessions(): Promise<{
    sessions: Array<{
      session_id: string;
      created_at: string;
      current_stage: string;
      message_count: number;
      has_blog_context: boolean;
    }>;
    total_sessions: number;
  }> {
    return this.fetchWithErrorHandling('/api/chat/sessions');
  }

  // Health Check
  async healthCheck(): Promise<{
    status: string;
    ingestion_ready: boolean;
    blog_generation_ready: boolean;
    chatbot_ready: boolean;
    multi_file_processing_ready: boolean;
    active_sessions: number;
    version: string;
  }> {
    return this.fetchWithErrorHandling('/health');
  }

  // API Information
  async getApiInfo(): Promise<{
    message: string;
    version: string;
    description: string;
    endpoints: Record<string, string>;
    features: Record<string, string>;
  }> {
    return this.fetchWithErrorHandling('/');
  }
}

// Create and export a singleton instance
export const apiService = new ApiService();

// Export the class for custom instances if needed
export default ApiService;
