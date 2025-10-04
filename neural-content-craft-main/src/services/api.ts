// API Service for LinkedIn Blog AI Assistant
// Backend URL: https://linkedin-blog-agent-1.onrender.com

const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://linkedin-blog-agent-1.onrender.com';

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface ChatSessionResponse {
  session_id: string;
  current_stage: string;
  message_count: number;
  blog_context: BlogContext | null;
  created_at: string;
}

export interface ChatMessageRequest {
  message: string;
  session_id: string;
}

export interface ChatMessageResponse {
  success: boolean;
  response: string;
  session_id: string;
  current_stage: string;
  blog_context: BlogContext | null;
  error?: string;
}

export interface BlogContext {
  source_content?: string;
  ai_analysis?: string;
  key_insights?: string[];
  current_draft?: BlogPost;
  user_requirements?: string;
  feedback_history?: string[];
}

export interface BlogPost {
  title: string;
  hook: string;
  content: string;
  call_to_action: string;
  cta?: string;
  hashtags: string[];
  target_audience: string;
  targetAudience?: string;
  engagement_score: number;
  source_file?: string;
  ingestion_analysis?: string;
}

export interface FileIngestionResponse {
  success: boolean;
  error?: string;
  source_file: string;
  content_type: string;
  ai_analysis: string;
  key_insights: string[];
  metadata: {
    file_size?: number;
    total_pages?: number;
    [key: string]: any;
  };
  extracted_content: {
    raw_text: string;
    processing_time: number;
    [key: string]: any;
  };
}

export interface BlogResponse {
  success: boolean;
  error?: string;
  blog_post?: BlogPost;
  workflow_status?: string;
  iterations?: number;
  quality_score?: number;
}

export interface FeedbackRequest {
  session_id: string;
  feedback: string;
  feedback_type: string;
}

export interface ApprovalRequest {
  session_id: string;
  approved: boolean;
  final_notes?: string;
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
  blog_context: BlogContext | null;
}

export interface SessionListResponse {
  sessions: Array<{
    session_id: string;
    created_at: string;
    current_stage: string;
    message_count: number;
    has_blog_context: boolean;
  }>;
  total_sessions: number;
}

// ============================================================================
// API SERVICE CLASS
// ============================================================================

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // ========================================================================
  // HELPER METHODS
  // ========================================================================

  private async fetchWithRetry(
    url: string,
    options: RequestInit,
    retries = 3
  ): Promise<Response> {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await fetch(url, options);
        return response;
      } catch (error) {
        if (i === retries - 1) throw error;
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
      }
    }
    throw new Error('Max retries reached');
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    try {
      const url = `${this.baseURL}${endpoint}`;
      console.log(`🌐 API Call: ${options.method || 'GET'} ${url}`);

      const response = await this.fetchWithRetry(url, {
        ...options,
        headers: {
          ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
          ...options.headers,
        },
        mode: 'cors',
        credentials: 'omit',
      });

      console.log(`✅ Response Status: ${response.status}`);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.error || errorMessage;
        } catch {
          // Use status text if error response is not JSON
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      console.log('✅ Response Data:', data);
      return data;
    } catch (error) {
      console.error(`❌ API Error for ${endpoint}:`, error);
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Network error: Unable to reach the server. Please check your connection.');
      }
      throw error;
    }
  }

  // ========================================================================
  // SESSION MANAGEMENT
  // ========================================================================

  /**
   * Initialize a new chat session
   * Call on page load or when starting a new conversation
   */
  async startChatSession(): Promise<ChatSessionResponse> {
    console.log('🚀 Starting new chat session...');
    return this.request<ChatSessionResponse>('/api/chat/start', {
      method: 'POST',
    });
  }

  /**
   * Get list of all chat sessions
   */
  async getSessions(): Promise<SessionListResponse> {
    return this.request<SessionListResponse>('/api/chat/sessions');
  }

  /**
   * Get conversation history for a specific session
   */
  async getChatHistory(sessionId: string): Promise<ChatHistoryResponse> {
    return this.request<ChatHistoryResponse>(`/api/chat/history/${sessionId}`);
  }

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: string): Promise<{ success: boolean; message: string }> {
    return this.request(`/api/chat/session/${sessionId}`, {
      method: 'DELETE',
    });
  }

  // ========================================================================
  // MESSAGING
  // ========================================================================

  /**
   * Send a text message to the chatbot
   */
  async sendMessage(message: string, sessionId: string): Promise<ChatMessageResponse> {
    console.log(`💬 Sending message to session: ${sessionId}`);
    return this.request<ChatMessageResponse>('/api/chat/message', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
  }

  /**
   * Submit feedback for blog refinement
   */
  async submitFeedback(
    sessionId: string,
    feedback: string,
    feedbackType: string = 'general'
  ): Promise<ChatMessageResponse> {
    console.log(`✏️ Submitting feedback for session: ${sessionId}`);
    return this.request<ChatMessageResponse>('/api/chat/feedback', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        feedback,
        feedback_type: feedbackType,
      }),
    });
  }

  /**
   * Approve or reject blog post
   */
  async approveBlog(
    sessionId: string,
    approved: boolean,
    finalNotes?: string
  ): Promise<ChatMessageResponse> {
    console.log(`${approved ? '✅' : '❌'} ${approved ? 'Approving' : 'Rejecting'} blog for session: ${sessionId}`);
    return this.request<ChatMessageResponse>('/api/chat/approve', {
      method: 'POST',
      body: JSON.stringify({
        session_id: sessionId,
        approved,
        final_notes: finalNotes,
      }),
    });
  }

  // ========================================================================
  // FILE OPERATIONS
  // ========================================================================

  /**
   * Upload and ingest a single file
   */
  async uploadFile(file: File): Promise<FileIngestionResponse> {
    const formData = new FormData();
    formData.append('file', file);

    console.log(`📤 Uploading file: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)}MB)`);

    return this.request<FileIngestionResponse>('/api/ingest', {
      method: 'POST',
      body: formData,
    });
  }

  /**
   * Generate blog post directly from file upload
   */
  async generateBlogFromFile(
    file: File,
    targetAudience?: string,
    tone?: string,
    maxIterations?: number
  ): Promise<BlogResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (targetAudience) formData.append('target_audience', targetAudience);
    if (tone) formData.append('tone', tone);
    if (maxIterations) formData.append('max_iterations', maxIterations.toString());

    console.log(`📝 Generating blog from file: ${file.name}`);

    return this.request<BlogResponse>('/api/generate-blog-from-file', {
      method: 'POST',
      body: formData,
    });
  }

  /**
   * Aggregate multiple files into a single blog post
   */
  async aggregateFiles(
    files: File[],
    strategy: string = 'synthesis',
    targetAudience?: string,
    tone?: string
  ): Promise<BlogResponse> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('aggregation_strategy', strategy);
    if (targetAudience) formData.append('target_audience', targetAudience);
    if (tone) formData.append('tone', tone);

    console.log(`📚 Aggregating ${files.length} files with strategy: ${strategy}`);

    return this.request<BlogResponse>('/api/aggregate', {
      method: 'POST',
      body: formData,
    });
  }

  // ========================================================================
  // UTILITY
  // ========================================================================

  /**
   * Health check for backend
   */
  async healthCheck(): Promise<any> {
    return this.request('/health');
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const apiService = new ApiService();
export default ApiService;
