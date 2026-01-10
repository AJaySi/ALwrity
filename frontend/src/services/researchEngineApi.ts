import { apiClient } from '../api/client';
import { ResearchConfig, ResearchResponse } from './researchApi';

export interface ResearchEngineRequest {
  query: string;
  keywords: string[];
  goal?: string; // factual | trending | competitive | educational | technical | inspirational
  depth?: string; // quick | standard | comprehensive | expert
  provider?: string; // auto | exa | tavily | google
  content_type?: string; // blog | podcast | video | social | email | newsletter | whitepaper | general
  industry?: string;
  target_audience?: string;
  tone?: string;
  max_sources?: number;
  recency?: string; // day | week | month | year
  include_domains?: string[];
  exclude_domains?: string[];
  advanced_mode?: boolean;
  // Raw provider params (optional)
  exa_category?: string;
  exa_search_type?: string;
  tavily_topic?: string;
  tavily_search_depth?: string;
  tavily_include_answer?: boolean | string;
  tavily_include_raw_content?: boolean | string;
  tavily_time_range?: string;
  tavily_country?: string;
  config?: ResearchConfig;
}

export interface ResearchEngineResponse extends ResearchResponse {
  provider_used?: string;
}

export interface ResearchTaskResponse {
  task_id: string;
}

export interface ResearchTaskStatusResponse {
  status: string;
  progress_messages?: Array<{ timestamp: string; message: string }>;
  result?: ResearchEngineResponse | null;
  error?: string;
  error_status?: number;
  error_data?: any;
}

export const researchEngineApi = {
  async execute(request: ResearchEngineRequest): Promise<ResearchEngineResponse> {
    const { data } = await apiClient.post('/api/research/execute', request);
    return data;
  },

  async start(request: ResearchEngineRequest): Promise<ResearchTaskResponse> {
    const { data } = await apiClient.post('/api/research/start', request);
    return data;
  },

  async pollStatus(taskId: string): Promise<ResearchTaskStatusResponse> {
    const { data } = await apiClient.get(`/api/research/status/${taskId}`);
    // Normalize shape to match usePolling expectations
    return {
      status: data.status || 'pending',
      progress_messages: data.progress_messages || [],
      result: data.result || null,
      error: data.error,
      error_status: data.error_status,
      error_data: data.error_data,
    };
  },
};

