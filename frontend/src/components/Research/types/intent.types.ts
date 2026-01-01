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
  keywords: string[];
  use_persona: boolean;
  use_competitor_data: boolean;
}

export interface AnalyzeIntentResponse {
  success: boolean;
  intent: ResearchIntent;
  analysis_summary: string;
  suggested_queries: ResearchQuery[];
  suggested_keywords: string[];
  suggested_angles: string[];
  quick_options: QuickOption[];
  error_message: string | null;
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
