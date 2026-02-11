import { apiClient, aiApiClient, pollingApiClient } from "../api/client";
// Import research types for use in this file
import type { ResearchMode, ResearchSource, ResearchConfig, ResearchResponse } from './researchApi';
// Re-export research types for backward compatibility
// TODO: Update all blog writer code to import from researchApi.ts directly
export type { ResearchMode, ResearchSource, ResearchConfig, ResearchResponse } from './researchApi';

export interface PersonaInfo {
  persona_id?: string;
  tone?: string;
  audience?: string;
  industry?: string;
}

export interface BlogResearchRequest {
  keywords: string[];
  topic?: string;
  industry?: string;
  target_audience?: string;
  tone?: string;
  word_count_target?: number;
  persona?: PersonaInfo;
  research_mode?: ResearchMode;
  config?: ResearchConfig;
}

export interface GroundingChunk {
  title: string;
  url: string;
  confidence_score?: number;
}

export interface GroundingSupport {
  confidence_scores: number[];
  grounding_chunk_indices: number[];
  segment_text: string;
  start_index?: number;
  end_index?: number;
}

export interface Citation {
  citation_type: string;
  start_index: number;
  end_index: number;
  text: string;
  source_indices: number[];
  reference: string;
}

export interface GroundingMetadata {
  grounding_chunks: GroundingChunk[];
  grounding_supports: GroundingSupport[];
  citations: Citation[];
  search_entry_point?: string;
  web_search_queries: string[];
}

export interface BlogResearchResponse extends ResearchResponse {
  // Blog Writer specific extensions
  search_widget?: string;
  grounding_metadata?: GroundingMetadata;
}

export interface BlogOutlineSection {
  id: string;
  heading: string;
  subheadings: string[];
  key_points: string[];
  references: ResearchSource[];
  target_words?: number;
  keywords: string[];
}

export interface SourceMappingStats {
  total_sources_mapped: number;
  coverage_percentage: number;
  average_relevance_score: number;
  high_confidence_mappings: number;
}

export interface GroundingInsights {
  confidence_analysis?: {
    average_confidence: number;
    confidence_distribution: { high: number; medium: number; low: number };
    high_confidence_sources_count: number;
    high_confidence_insights: string[];
  };
  authority_analysis?: {
    average_authority_score: number;
    authority_distribution: { high: number; medium: number; low: number };
    high_authority_sources: Array<{ title: string; url: string; score: number }>;
  };
  temporal_analysis?: {
    recency_score: number;
    trending_topics: string[];
    temporal_balance: string;
  };
  content_relationships?: {
    related_concepts: string[];
    content_gaps: string[];
    concept_coverage_score: number;
    gap_count: number;
  };
  citation_insights?: {
    total_citations: number;
    citation_types: Record<string, number>;
    citation_density: number;
    citation_quality_score: number;
  };
  search_intent_insights?: {
    primary_intent: string;
    user_questions: string[];
    intent_signals_count: number;
  };
  quality_indicators?: {
    overall_quality_score: number;
    quality_grade: string;
    key_quality_factors: {
      confidence: number;
      authority: number;
      citations: number;
      coverage: number;
    };
  };
}

export interface OptimizationResults {
  overall_quality_score: number;
  improvements_made: string[];
  optimization_focus: string;
}

export interface ResearchCoverage {
  sources_utilized: number;
  content_gaps_identified: number;
  competitive_advantages: string[];
}

export interface BlogOutlineResponse {
  success: boolean;
  title_options: string[];
  outline: BlogOutlineSection[];
  
  // Additional metadata for enhanced UI
  source_mapping_stats?: SourceMappingStats;
  grounding_insights?: GroundingInsights;
  optimization_results?: OptimizationResults;
  research_coverage?: ResearchCoverage;
}

export interface BlogSectionResponse {
  success: boolean;
  markdown: string;
  citations: ResearchSource[];
  continuity_metrics?: { flow?: number; consistency?: number; progression?: number };
}

export interface BlogSEOActionableRecommendation {
  category: string;
  priority: 'High' | 'Medium' | 'Low' | string;
  recommendation: string;
  impact: string;
}

export interface BlogSEOAnalysisSummary {
  overall_grade: string;
  status: string;
  strongest_category: string;
  weakest_category: string;
  key_strengths: string[];
  key_weaknesses: string[];
  ai_summary: string;
}

export interface BlogSEOAnalyzeResponse {
  success: boolean;
  analysis_id?: string;
  overall_score: number;
  category_scores: Record<string, number>;
  analysis_summary: BlogSEOAnalysisSummary;
  actionable_recommendations: BlogSEOActionableRecommendation[];
  detailed_analysis?: any;
  visualization_data?: any;
  generated_at?: string;
  error?: string;
}

export interface BlogSEOApplyRecommendationsRequest {
  title: string;
  sections: Array<{ id: string; heading: string; content: string }>;
  outline: BlogOutlineSection[];
  research: Record<string, any>;
  recommendations: BlogSEOActionableRecommendation[];
  persona?: Record<string, any>;
  tone?: string;
  audience?: string;
}

export interface BlogSEOApplyRecommendationsResponse {
  success: boolean;
  title?: string;
  sections: Array<{ id: string; heading: string; content: string; notes?: string[] }>;
  applied?: Array<{ category: string; summary: string }>;
  error?: string;
}

export interface BlogSEOMetadataResponse {
  success: boolean;
  title_options: string[];
  meta_descriptions: string[];
  seo_title?: string;
  meta_description?: string;
  url_slug?: string;
  blog_tags: string[];
  blog_categories: string[];
  social_hashtags: string[];
  open_graph: Record<string, any>;
  twitter_card: Record<string, any>;
  json_ld_schema?: Record<string, any>;
  schema?: Record<string, any>; // Legacy field name
  canonical_url?: string;
  reading_time?: number;
  focus_keyword?: string;
  generated_at?: string;
  optimization_score?: number;
  error?: string;
}

export interface BlogPublishResponse {
  success: boolean;
  platform: string;
  url?: string;
  post_id?: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  created_at: string;
  progress_messages: Array<{
    timestamp: string;
    message: string;
  }>;
  result?: BlogResearchResponse;
  error?: string;
  // Subscription error details (set by backend when subscription limit is exceeded)
  error_status?: number; // HTTP status code (429 for usage limit, 402 for subscription expired)
  error_data?: {
    error?: string;
    message?: string;
    provider?: string;
    usage_info?: {
      provider?: string;
      current_calls?: number;
      limit?: number;
      type?: string;
      breakdown?: {
        gemini?: number;
        openai?: number;
        anthropic?: number;
        mistral?: number;
      };
    };
    [key: string]: any; // Allow additional fields
  };
}

export const blogWriterApi = {
  // Async polling endpoints
  async startResearch(payload: BlogResearchRequest): Promise<{task_id: string; status: string}> {
    const { data } = await apiClient.post("/api/blog/research/start", payload);
    return data;
  },

  async pollResearchStatus(taskId: string): Promise<TaskStatusResponse> {
    const { data } = await pollingApiClient.get(`/api/blog/research/status/${taskId}`);
    return data;
  },

  async startOutlineGeneration(payload: { research: BlogResearchResponse; persona?: PersonaInfo; word_count?: number; custom_instructions?: string }): Promise<{task_id: string; status: string}> {
    const { data } = await aiApiClient.post("/api/blog/outline/start", payload);
    return data;
  },

  async pollOutlineStatus(taskId: string): Promise<TaskStatusResponse> {
    const { data } = await pollingApiClient.get(`/api/blog/outline/status/${taskId}`);
    return data;
  },


  async getContinuity(sectionId: string): Promise<{ section_id: string; continuity_metrics?: Record<string, number> }> {
    const { data } = await apiClient.get(`/api/blog/section/${encodeURIComponent(sectionId)}/continuity`);
    return data;
  },

  // Blog Rewrite API
  async rewriteBlog(payload: {
    title: string;
    sections: Array<{
      id: string;
      heading: string;
      content: string;
    }>;
    research: BlogResearchResponse;
    outline: BlogOutlineSection[];
    feedback: string;
    tone?: string;
    audience?: string;
    focus?: string;
  }): Promise<{
    success: boolean;
    taskId?: string;
    error?: string;
  }> {
    const { data } = await aiApiClient.post('/api/blog/rewrite/start', payload);
    return data;
  },

  async pollRewriteStatus(taskId: string): Promise<TaskStatusResponse> {
    const { data } = await pollingApiClient.get(`/api/blog/rewrite/status/${taskId}`);
    return data;
  },

  async applySeoRecommendations(payload: BlogSEOApplyRecommendationsRequest): Promise<BlogSEOApplyRecommendationsResponse> {
    const { data } = await apiClient.post('/api/blog/seo/apply-recommendations', payload);
    return data;
  },

  // Flow Analysis APIs
  async analyzeFlowBasic(payload: {
    title: string;
    sections: Array<{
      id: string;
      heading: string;
      content: string;
    }>;
  }): Promise<{
    success: boolean;
    analysis?: {
      overall_flow_score: number;
      overall_consistency_score: number;
      overall_progression_score: number;
      sections: Array<{
        section_id: string;
        heading: string;
        flow_score: number;
        consistency_score: number;
        progression_score: number;
        suggestions: string[];
      }>;
      overall_suggestions: string[];
    };
    mode: string;
    error?: string;
  }> {
    const { data } = await aiApiClient.post('/api/blog/flow-analysis/basic', payload);
    return data;
  },

  async analyzeFlowAdvanced(payload: {
    title: string;
    sections: Array<{
      id: string;
      heading: string;
      content: string;
    }>;
  }): Promise<{
    success: boolean;
    analysis?: {
      overall_flow_score: number;
      overall_consistency_score: number;
      overall_progression_score: number;
      sections: Array<{
        section_id: string;
        heading: string;
        flow_score: number;
        consistency_score: number;
        progression_score: number;
        detailed_analysis: string;
        suggestions: string[];
      }>;
    };
    mode: string;
    error?: string;
  }> {
    const { data } = await aiApiClient.post('/api/blog/flow-analysis/advanced', payload);
    return data;
  },


  async refineOutline(payload: { outline: BlogOutlineSection[]; operation: string; section_id?: string; payload?: any }): Promise<BlogOutlineResponse> {
    const { data } = await apiClient.post("/api/blog/outline/refine", payload);
    return data;
  },

  async generateSection(payload: { section: BlogOutlineSection; keywords?: string[]; tone?: string; persona?: PersonaInfo; mode?: 'draft' | 'polished' }): Promise<BlogSectionResponse> {
    const { data } = await apiClient.post("/api/blog/section/generate", payload);
    return data;
  },

  // Removed old seoAnalyze - now using comprehensive SEO analysis through modal

  async seoMetadata(payload: { content: string; title?: string; keywords?: string[] }): Promise<BlogSEOMetadataResponse> {
    const { data } = await apiClient.post("/api/blog/seo/metadata", payload);
    return data;
  },

  async publish(payload: { platform: 'wix' | 'wordpress'; html: string; metadata: BlogSEOMetadataResponse; schedule_time?: string }): Promise<BlogPublishResponse> {
    const { data } = await apiClient.post("/api/blog/publish", payload);
    return data;
  },

  async generateSEOTitles(payload: {
    research: BlogResearchResponse;
    outline: BlogOutlineSection[];
    primary_keywords: string[];
    secondary_keywords: string[];
    content_angles: string[];
    search_intent?: string;
    word_count?: number;
  }): Promise<{ success: boolean; titles: string[] }> {
    const { data } = await aiApiClient.post('/api/blog/titles/generate-seo', payload);
    return data;
  },

  async generateIntroductions(payload: {
    blog_title: string;
    research: BlogResearchResponse;
    outline: BlogOutlineSection[];
    sections_content: Record<string, string>;
    primary_keywords: string[];
    search_intent?: string;
  }): Promise<{ success: boolean; introductions: string[] }> {
    const { data } = await aiApiClient.post('/api/blog/introductions/generate', payload);
    return data;
  },

  // Enhanced Outline Methods
  async enhanceSection(section: BlogOutlineSection, focus: string = 'general improvement'): Promise<BlogOutlineSection> {
    const { data } = await apiClient.post("/api/blog/outline/enhance-section", section, {
      params: { focus }
    });
    return data;
  },

  async optimizeOutline(payload: { outline: BlogOutlineSection[] }, focus: string = 'general optimization'): Promise<{ outline: BlogOutlineSection[] }> {
    const { data } = await apiClient.post("/api/blog/outline/optimize", payload, {
      params: { focus }
    });
    return data;
  },

  async rebalanceOutline(payload: { outline: BlogOutlineSection[] }, targetWords: number = 1500): Promise<{ outline: BlogOutlineSection[] }> {
    const { data } = await apiClient.post("/api/blog/outline/rebalance", payload, {
      params: { target_words: targetWords }
    });
    return data;
  }
};

// Medium blog generation (≤1000 words)
export interface MediumSectionOutlinePayload {
  id: string;
  heading: string;
  keyPoints?: string[];
  subheadings?: string[];
  keywords?: string[];
  targetWords?: number;
  references?: ResearchSource[];
}

export interface MediumGenerationRequestPayload {
  title: string;
  sections: MediumSectionOutlinePayload[];
  persona?: PersonaInfo;
  tone?: string;
  audience?: string;
  globalTargetWords?: number;
  researchKeywords?: string[];  // Original research keywords for better caching
}

export interface MediumGenerationResultPayload {
  success: boolean;
  title: string;
  sections: Array<{ id: string; heading: string; content: string; wordCount: number; sources?: ResearchSource[] }>;
  model?: string;
  generation_time_ms?: number;
}

export const mediumBlogApi = {
  async startMediumGeneration(payload: MediumGenerationRequestPayload): Promise<{ task_id: string; status: string }> {
    const { data } = await aiApiClient.post('/api/blog/generate/medium/start', payload);
    return data;
  },
  async pollMediumGeneration(taskId: string): Promise<TaskStatusResponse & { result?: MediumGenerationResultPayload }> {
    const { data } = await pollingApiClient.get(`/api/blog/generate/medium/status/${taskId}`);
    return data;
  }
};

// Assistive Writing API
export interface AssistiveSuggestion {
  text: string;
  confidence: number;
  sources: Array<{
    title: string;
    url: string;
    text?: string;
    author?: string;
    published_date?: string;
    score: number;
  }>;
}

export interface AssistiveSuggestionResponse {
  success: boolean;
  suggestions: AssistiveSuggestion[];
}

export const assistiveWritingApi = {
  async getSuggestion(text: string, maxResults: number = 1): Promise<AssistiveSuggestionResponse> {
    const { data } = await aiApiClient.post('/api/writing-assistant/suggest', {
      text,
      max_results: maxResults
    });
    return data;
  }
};


