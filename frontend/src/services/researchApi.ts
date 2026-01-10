/**
 * Research API Types and Interfaces
 * 
 * Dedicated types for the Research Engine, separate from Blog Writer.
 * This ensures proper separation of concerns.
 * 
 * Author: ALwrity Team
 * Version: 1.0
 */

// ============================================================================
// Core Research Types
// ============================================================================

export type ResearchMode = 'basic' | 'comprehensive' | 'targeted';
export type ResearchProvider = 'google' | 'exa' | 'tavily';
export type SourceType = 'web' | 'academic' | 'news' | 'industry' | 'expert';
export type DateRange = 'last_week' | 'last_month' | 'last_3_months' | 'last_6_months' | 'last_year' | 'all_time';

// ============================================================================
// Research Source
// ============================================================================

export interface ResearchSource {
  title: string;
  url: string;
  excerpt?: string;
  credibility_score?: number;
  published_at?: string;
  index?: number;
  source_type?: string;
}

// ============================================================================
// Research Configuration
// ============================================================================

export interface ResearchConfig {
  mode?: ResearchMode;
  provider?: ResearchProvider;
  date_range?: DateRange;
  source_types?: SourceType[];
  max_sources?: number;
  include_statistics?: boolean;
  include_expert_quotes?: boolean;
  include_competitors?: boolean;
  include_trends?: boolean;
  
  // Exa-specific options
  exa_category?: string;
  exa_include_domains?: string[];
  exa_exclude_domains?: string[];
  exa_search_type?: 'auto' | 'keyword' | 'neural' | 'fast' | 'deep';
  exa_num_results?: number;
  exa_date_filter?: string; // ISO date string for startPublishedDate (e.g., "2025-01-01T00:00:00.000Z")
  exa_end_published_date?: string; // ISO date string for endPublishedDate
  exa_start_crawl_date?: string; // ISO date string for startCrawlDate
  exa_end_crawl_date?: string; // ISO date string for endCrawlDate
  exa_include_text?: string[]; // Text that must be present in webpage text (max 1 string, up to 5 words)
  exa_exclude_text?: string[]; // Text that must not be present in webpage text (max 1 string, up to 5 words)
  exa_highlights?: boolean;
  exa_highlights_num_sentences?: number; // Number of sentences per highlight (default: 2)
  exa_highlights_per_url?: number; // Number of highlights per URL (default: 3)
  exa_context?: boolean | { maxCharacters?: number }; // Context string: boolean or object with maxCharacters
  exa_context_max_characters?: number; // Max characters for context string (recommended: 10000+)
  exa_text_max_characters?: number; // Max characters for full page text (default: 1000)
  exa_summary_query?: string; // Custom query for LLM-generated summary
  exa_additional_queries?: string[]; // Additional query variations for Deep search (only works with type="deep")
  
  // Tavily-specific options
  tavily_topic?: 'general' | 'news' | 'finance';
  tavily_search_depth?: 'basic' | 'advanced';
  tavily_include_domains?: string[];
  tavily_exclude_domains?: string[];
  tavily_include_answer?: boolean | 'basic' | 'advanced';
  tavily_include_raw_content?: boolean | 'markdown' | 'text';
  tavily_include_images?: boolean;
  tavily_include_image_descriptions?: boolean;
  tavily_include_favicon?: boolean;
  tavily_time_range?: 'day' | 'week' | 'month' | 'year' | 'd' | 'w' | 'm' | 'y';
  tavily_start_date?: string; // YYYY-MM-DD
  tavily_end_date?: string; // YYYY-MM-DD
  tavily_country?: string;
  tavily_chunks_per_source?: number; // 1-3
  tavily_auto_parameters?: boolean;
}

// ============================================================================
// Research Response (Generic)
// ============================================================================

export interface ResearchResponse {
  success: boolean;
  keywords?: string[];
  sources: ResearchSource[];
  keyword_analysis: Record<string, any>;
  competitor_analysis: Record<string, any>;
  suggested_angles: string[];
  search_queries?: string[];
  original_keywords?: string[];
  error_message?: string;
}

// ============================================================================
// Research Request
// ============================================================================

export interface ResearchRequest {
  keywords: string[];
  topic?: string;
  industry?: string;
  target_audience?: string;
  tone?: string;
  research_mode?: ResearchMode;
  config?: ResearchConfig;
}
