/**
 * Intent-Driven Research Types
 * 
 * Types for the new intent-driven research system that:
 * - Infers user intent from minimal input
 * - Generates targeted queries
 * - Analyzes results based on what user needs
 */

// ============================================================================
// Enums
// ============================================================================

export type ResearchPurpose = 
  | 'learn'
  | 'create_content'
  | 'make_decision'
  | 'compare'
  | 'solve_problem'
  | 'find_data'
  | 'explore_trends'
  | 'validate'
  | 'generate_ideas';

export type ContentOutput = 
  | 'blog'
  | 'podcast'
  | 'video'
  | 'social_post'
  | 'newsletter'
  | 'presentation'
  | 'report'
  | 'whitepaper'
  | 'email'
  | 'general';

export type ExpectedDeliverable = 
  | 'key_statistics'
  | 'expert_quotes'
  | 'case_studies'
  | 'comparisons'
  | 'trends'
  | 'best_practices'
  | 'step_by_step'
  | 'pros_cons'
  | 'definitions'
  | 'citations'
  | 'examples'
  | 'predictions';

export type ResearchDepthLevel = 'overview' | 'detailed' | 'expert';

export type InputType = 'keywords' | 'question' | 'goal' | 'mixed';

// ============================================================================
// Core Intent Types
// ============================================================================

export interface ResearchIntent {
  primary_question: string;
  secondary_questions: string[];
  purpose: ResearchPurpose;
  content_output: ContentOutput;
  expected_deliverables: ExpectedDeliverable[];
  depth: ResearchDepthLevel;
  focus_areas: string[];
  also_answering: string[];
  perspective: string | null;
  time_sensitivity: string | null;
  input_type: InputType;
  original_input: string;
  confidence: number;
  needs_clarification: boolean;
  clarifying_questions: string[];
}

export interface ResearchQuery {
  query: string;
  purpose: ExpectedDeliverable;
  provider: 'exa' | 'tavily' | 'google';
  priority: number;
  expected_results: string;
}

// ============================================================================
// Deliverable Types
// ============================================================================

export interface StatisticWithCitation {
  statistic: string;
  value: string | null;
  context: string;
  source: string;
  url: string;
  credibility: number;
  recency: string | null;
}

export interface ExpertQuote {
  quote: string;
  speaker: string;
  title: string | null;
  organization: string | null;
  context: string | null;
  source: string;
  url: string;
}

export interface CaseStudySummary {
  title: string;
  organization: string;
  challenge: string;
  solution: string;
  outcome: string;
  key_metrics: string[];
  source: string;
  url: string;
}

export interface TrendAnalysis {
  trend: string;
  direction: 'growing' | 'declining' | 'emerging' | 'stable';
  evidence: string[];
  impact: string | null;
  timeline: string | null;
  sources: string[];
  // Google Trends specific (optional)
  google_trends_data?: GoogleTrendsData;
  interest_score?: number; // 0-100 from Google Trends
  regional_interest?: Record<string, number>;
  related_topics?: {
    top: string[];
    rising: string[];
  };
  related_queries?: {
    top: string[];
    rising: string[];
  };
}

export interface GoogleTrendsData {
  interest_over_time: Array<Record<string, any>>;
  interest_by_region: Array<Record<string, any>>;
  related_topics: {
    top: Array<Record<string, any>>;
    rising: Array<Record<string, any>>;
  };
  related_queries: {
    top: Array<Record<string, any>>;
    rising: Array<Record<string, any>>;
  };
  trending_searches?: string[];
  timeframe: string;
  geo: string;
  keywords: string[];
  timestamp: string;
  cached?: boolean;
  error?: string;
}

export interface TrendsConfig {
  enabled: boolean;
  keywords: string[];
  keywords_justification: string;
  timeframe: string;
  timeframe_justification: string;
  geo: string;
  geo_justification: string;
  expected_insights: string[];
}

export interface ComparisonItem {
  name: string;
  description: string | null;
  pros: string[];
  cons: string[];
  features: Record<string, string>;
  rating: number | null;
  source: string | null;
}

export interface ComparisonTable {
  title: string;
  criteria: string[];
  items: ComparisonItem[];
  winner: string | null;
  verdict: string | null;
}

export interface ProsCons {
  subject: string;
  pros: string[];
  cons: string[];
  balanced_verdict: string;
}

export interface SourceWithRelevance {
  title: string;
  url: string;
  excerpt: string | null;
  relevance_score: number;
  relevance_reason: string | null;
  content_type: string | null;
  published_date: string | null;
  credibility_score: number;
}

// ============================================================================
// API Request/Response Types
// ============================================================================

export interface AnalyzeIntentRequest {
  user_input: string;
  keywords?: string[];
  use_persona?: boolean;
  use_competitor_data?: boolean;
  // User-provided intent settings (optional - if provided, use these instead of inferring)
  user_provided_purpose?: ResearchPurpose;
  user_provided_content_output?: ContentOutput;
  user_provided_depth?: ResearchDepthLevel;
}

// Optimized provider configuration with AI-driven justifications
export interface OptimizedConfig {
  provider: 'exa' | 'tavily' | 'google';
  provider_justification?: string;
  
  // Exa settings with justifications
  exa_type?: string;
  exa_type_justification?: string;
  exa_category?: string;
  exa_category_justification?: string;
  exa_include_domains?: string[];
  exa_include_domains_justification?: string;
  exa_num_results?: number;
  exa_num_results_justification?: string;
  exa_date_filter?: string;
  exa_date_justification?: string;
  exa_end_published_date?: string;
  exa_end_published_date_justification?: string;
  exa_start_crawl_date?: string;
  exa_start_crawl_date_justification?: string;
  exa_end_crawl_date?: string;
  exa_end_crawl_date_justification?: string;
  exa_include_text?: string[];
  exa_include_text_justification?: string;
  exa_exclude_text?: string[];
  exa_exclude_text_justification?: string;
  exa_highlights?: boolean;
  exa_highlights_justification?: string;
  exa_highlights_num_sentences?: number;
  exa_highlights_num_sentences_justification?: string;
  exa_highlights_per_url?: number;
  exa_highlights_per_url_justification?: string;
  exa_context?: boolean | { maxCharacters?: number };
  exa_context_justification?: string;
  exa_context_max_characters?: number;
  exa_context_max_characters_justification?: string;
  exa_text_max_characters?: number;
  exa_text_max_characters_justification?: string;
  exa_summary_query?: string;
  exa_summary_query_justification?: string;
  exa_additional_queries?: string[];
  exa_additional_queries_justification?: string;
  // Note: exa_search_type is mapped from exa_type in the backend
  
  // Tavily settings with justifications
  tavily_topic?: string;
  tavily_topic_justification?: string;
  tavily_search_depth?: string;
  tavily_search_depth_justification?: string;
  tavily_include_answer?: boolean | string;
  tavily_include_answer_justification?: string;
  tavily_time_range?: string;
  tavily_time_range_justification?: string;
  tavily_max_results?: number;
  tavily_max_results_justification?: string;
  tavily_raw_content?: string;
  tavily_raw_content_justification?: string;
}

export interface AnalyzeIntentResponse {
  success: boolean;
  intent: ResearchIntent;
  analysis_summary: string;
  suggested_queries: ResearchQuery[];
  suggested_keywords: string[];
  suggested_angles: string[];
  quick_options: QuickOption[];
  confidence_reason?: string;
  great_example?: string;
  error_message: string | null;
  
  // Unified: Optimized provider parameters based on intent
  optimized_config?: OptimizedConfig;
  recommended_provider?: 'exa' | 'tavily' | 'google';
  
  // Google Trends configuration (if trends in deliverables)
  trends_config?: TrendsConfig;
}

export interface QuickOption {
  id: string;
  label: string;
  value: string | string[];
  display: string | string[];
  alternatives: string[];
  confidence: number;
  multi_select?: boolean;
}

export interface IntentDrivenResearchRequest {
  user_input: string;
  confirmed_intent?: ResearchIntent;
  selected_queries?: ResearchQuery[];
  max_sources: number;
  include_domains: string[];
  exclude_domains: string[];
  trends_config?: TrendsConfig; // Google Trends configuration
  skip_inference: boolean;
}

export interface IntentDrivenResearchResponse {
  success: boolean;
  
  // Direct answers
  primary_answer: string;
  secondary_answers: Record<string, string>;
  
  // Deliverables
  statistics: StatisticWithCitation[];
  expert_quotes: ExpertQuote[];
  case_studies: CaseStudySummary[];
  trends: TrendAnalysis[];
  comparisons: ComparisonTable[];
  best_practices: string[];
  step_by_step: string[];
  pros_cons: ProsCons | null;
  definitions: Record<string, string>;
  examples: string[];
  predictions: string[];
  
  // Content-ready outputs
  executive_summary: string;
  key_takeaways: string[];
  suggested_outline: string[];
  
  // Sources and metadata
  sources: SourceWithRelevance[];
  confidence: number;
  gaps_identified: string[];
  follow_up_queries: string[];
  
  // The intent used
  intent: ResearchIntent | null;
  
  // Google Trends data (if trends were analyzed)
  google_trends_data?: GoogleTrendsData;
  
  // Error
  error_message: string | null;
}

// ============================================================================
// UI State Types
// ============================================================================

export interface IntentWizardState {
  // User input
  userInput: string;
  keywords: string[];
  
  // Inferred/confirmed intent
  intent: ResearchIntent | null;
  
  // Suggested queries
  suggestedQueries: ResearchQuery[];
  selectedQueries: ResearchQuery[];
  
  // Quick options for confirmation
  quickOptions: QuickOption[];
  
  // Analysis
  analysisSummary: string;
  suggestedKeywords: string[];
  suggestedAngles: string[];
  
  // State
  isAnalyzing: boolean;
  isResearching: boolean;
  hasConfirmedIntent: boolean;
  
  // Results
  result: IntentDrivenResearchResponse | null;
  
  // Errors
  error: string | null;
}

// ============================================================================
// Display Helpers
// ============================================================================

export const PURPOSE_DISPLAY: Record<ResearchPurpose, string> = {
  learn: 'Understand this topic',
  create_content: 'Create content about this',
  make_decision: 'Make a decision',
  compare: 'Compare options',
  solve_problem: 'Solve a problem',
  find_data: 'Find specific data',
  explore_trends: 'Explore trends',
  validate: 'Validate information',
  generate_ideas: 'Generate ideas',
};

export const CONTENT_OUTPUT_DISPLAY: Record<ContentOutput, string> = {
  blog: 'Blog Post',
  podcast: 'Podcast',
  video: 'Video',
  social_post: 'Social Post',
  newsletter: 'Newsletter',
  presentation: 'Presentation',
  report: 'Report',
  whitepaper: 'Whitepaper',
  email: 'Email',
  general: 'General Research',
};

export const DELIVERABLE_DISPLAY: Record<ExpectedDeliverable, string> = {
  key_statistics: 'Key Statistics',
  expert_quotes: 'Expert Quotes',
  case_studies: 'Case Studies',
  comparisons: 'Comparisons',
  trends: 'Trends',
  best_practices: 'Best Practices',
  step_by_step: 'Step-by-Step Guide',
  pros_cons: 'Pros & Cons',
  definitions: 'Definitions',
  citations: 'Citations',
  examples: 'Examples',
  predictions: 'Predictions',
};

export const DEPTH_DISPLAY: Record<ResearchDepthLevel, string> = {
  overview: 'Quick Overview',
  detailed: 'Detailed Analysis',
  expert: 'Expert-Level Deep Dive',
};
