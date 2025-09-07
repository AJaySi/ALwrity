/**
 * Platform Persona Types
 * TypeScript interfaces mapping to backend persona models from PR #226
 */

// Core Writing Persona Interface
export interface WritingPersona {
  id: number;
  user_id: number;
  persona_name: string;
  archetype: string;
  core_belief: string;
  brand_voice_description: string;
  linguistic_fingerprint: LinguisticFingerprint;
  platform_adaptations: PlatformAdaptation[];
  onboarding_session_id: number;
  source_website_analysis: any;
  source_research_preferences: any;
  ai_analysis_version: string;
  confidence_score: number;
  analysis_date: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

// Linguistic Fingerprint Interface
export interface LinguisticFingerprint {
  sentence_metrics: SentenceMetrics;
  lexical_features: LexicalFeatures;
  rhetorical_devices: RhetoricalDevices;
}

// Sentence Metrics Interface
export interface SentenceMetrics {
  average_sentence_length_words: number;
  preferred_sentence_type: string;
  active_to_passive_ratio: string;
  sentence_complexity: string;
  paragraph_structure: string;
}

// Lexical Features Interface
export interface LexicalFeatures {
  go_to_words: string[];
  go_to_phrases: string[];
  avoid_words: string[];
  contractions: string;
  vocabulary_level: string;
  industry_terminology: string[];
  emotional_tone_words: string[];
}

// Rhetorical Devices Interface
export interface RhetoricalDevices {
  metaphors: string;
  analogies: string;
  rhetorical_questions: string;
  storytelling_approach: string;
  persuasion_techniques: string[];
}

// Platform Types
export type PlatformType = 
  | "twitter" 
  | "linkedin" 
  | "instagram" 
  | "facebook" 
  | "blog" 
  | "medium" 
  | "substack";

// Platform Adaptation Interface
export interface PlatformAdaptation {
  id: number;
  writing_persona_id: number;
  platform_type: PlatformType;
  sentence_metrics: PlatformSentenceMetrics;
  lexical_features: PlatformLexicalFeatures;
  rhetorical_devices: PlatformRhetoricalDevices;
  tonal_range: TonalRange;
  stylistic_constraints: StylisticConstraints;
  content_format_rules: ContentFormatRules;
  engagement_patterns: EngagementPatterns;
  posting_frequency: PostingFrequency;
  content_types: ContentTypes;
  platform_best_practices: PlatformBestPractices;
  created_at: string;
  updated_at: string;
}

// Platform-Specific Sentence Metrics
export interface PlatformSentenceMetrics {
  optimal_length: string;
  character_limit: number;
  sentence_structure: string;
  paragraph_breaks: string;
  readability_score: number;
}

// Platform-Specific Lexical Features
export interface PlatformLexicalFeatures {
  hashtag_strategy: string;
  platform_specific_terms: string[];
  engagement_phrases: string[];
  call_to_action_style: string;
}

// Platform-Specific Rhetorical Devices
export interface PlatformRhetoricalDevices {
  question_frequency: string;
  story_elements: string;
  visual_descriptions: string;
  interactive_elements: string;
}

// Tonal Range Interface
export interface TonalRange {
  default_tone: string;
  permissible_tones: string[];
  forbidden_tones: string[];
  emotional_range: string;
  formality_level: string;
}

// Stylistic Constraints Interface
export interface StylisticConstraints {
  punctuation_preferences: string;
  formatting_rules: string;
  emoji_usage: string;
  link_placement: string;
  media_integration: string;
}

// Content Format Rules Interface
export interface ContentFormatRules {
  character_limit: number;
  optimal_length: string;
  word_count: string;
  hashtag_limit: number;
  media_requirements: string;
  link_restrictions: string;
}

// Engagement Patterns Interface
export interface EngagementPatterns {
  posting_frequency: string;
  best_timing: string;
  interaction_style: string;
  response_strategy: string;
  community_approach: string;
}

// Posting Frequency Interface
export interface PostingFrequency {
  frequency: string;
  optimal_days: string[];
  optimal_times: string[];
  seasonal_adjustments: string;
}

// Content Types Interface
export interface ContentTypes {
  primary_content: string[];
  secondary_content: string[];
  content_mix: string;
  seasonal_content: string[];
}

// Platform Best Practices Interface
export interface PlatformBestPractices {
  algorithm_tips: string[];
  engagement_tactics: string[];
  content_strategies: string[];
  growth_hacks: string[];
}

// Persona Analysis Result Interface
export interface PersonaAnalysisResult {
  id: number;
  writing_persona_id: number;
  analysis_prompt: string;
  linguistic_analysis: any;
  platform_recommendations: any;
  confidence_score: number;
  analysis_date: string;
  ai_model_version: string;
}

// Persona Validation Result Interface
export interface PersonaValidationResult {
  id: number;
  writing_persona_id: number;
  stylometric_accuracy: number;
  consistency_score: number;
  platform_compliance: number;
  user_satisfaction: number;
  validation_date: string;
  improvement_suggestions: string[];
}

// API Response Interfaces
export interface PersonaGenerationResponse {
  success: boolean;
  persona_id?: number;
  message: string;
  confidence_score?: number;
  data_sufficiency?: number;
  platforms_generated?: string[];
}

export interface PersonaReadinessResponse {
  ready: boolean;
  message: string;
  missing_steps: string[];
  data_sufficiency: number;
  recommendations?: string[];
}

export interface PersonaPreviewResponse {
  preview: {
    identity: {
      persona_name: string;
      archetype: string;
      core_belief: string;
      brand_voice_description: string;
    };
    linguistic_fingerprint: any;
    tonal_range: any;
    sample_platform: {
      platform: string;
      adaptation: any;
    };
  };
  confidence_score: number;
  data_sufficiency: number;
}

// Platform Information Interface
export interface PlatformInfo {
  id: string;
  name: string;
  description: string;
  character_limit?: number;
  optimal_length?: string;
  word_count?: string;
  seo_optimized?: boolean;
  storytelling_focus?: boolean;
  subscription_focus?: boolean;
}

// Supported Platforms Response Interface
export interface SupportedPlatformsResponse {
  platforms: PlatformInfo[];
}

// User Personas Response Interface
export interface UserPersonasResponse {
  personas: WritingPersona[];
  total_count: number;
  active_count: number;
}

// Platform Persona Response Interface
export interface PlatformPersonaResponse {
  platform_type: PlatformType;
  sentence_metrics: PlatformSentenceMetrics;
  lexical_features: PlatformLexicalFeatures;
  content_format_rules: ContentFormatRules;
  engagement_patterns: EngagementPatterns;
  platform_best_practices: PlatformBestPractices;
}

// Content Generation Request Interface
export interface ContentGenerationRequest {
  platform: PlatformType;
  topic: string;
  content_type: string;
  additional_context?: string;
}

// Content Generation Response Interface
export interface ContentGenerationResponse {
  success: boolean;
  content: string;
  metadata: {
    character_count: number;
    word_count: number;
    persona_compliance_score: number;
    platform_optimization_score: number;
    generated_at: string;
  };
  suggestions?: string[];
}

// Export Persona Request Interface
export interface ExportPersonaRequest {
  platform: PlatformType;
  format: "prompt" | "json" | "markdown";
  include_metadata?: boolean;
}

// Export Persona Response Interface
export interface ExportPersonaResponse {
  success: boolean;
  content: string;
  format: string;
  export_date: string;
  version: string;
}
