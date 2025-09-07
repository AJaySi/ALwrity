/**
 * Platform Persona Provider
 * React Context provider for platform-specific persona data
 * Integrates with existing persona API client and injects data into CopilotKit
 */

import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { useCopilotReadable } from '@copilotkit/react-core';
import { 
  WritingPersona, 
  PlatformAdaptation, 
  PlatformType,
  UserPersonasResponse
} from '../../../types/PlatformPersonaTypes';
import { 
  getUserPersonas, 
  getPlatformPersona 
} from '../../../api/persona';

// Context interface
interface PlatformPersonaContextType {
  corePersona: WritingPersona | null;
  platformPersona: PlatformAdaptation | null;
  platform: PlatformType;
  loading: boolean;
  error: string | null;
  refreshPersonas: () => Promise<void>;
}

// Create the context
const PlatformPersonaContext = createContext<PlatformPersonaContextType | null>(null);

// Provider props interface
interface PlatformPersonaProviderProps {
  children: ReactNode;
  platform: PlatformType;
  userId?: number; // Default to 1 for now, can be enhanced with auth context later
}

// Provider component
export const PlatformPersonaProvider: React.FC<PlatformPersonaProviderProps> = ({ 
  children, 
  platform, 
  userId = 1 
}) => {
  // State management
  const [corePersona, setCorePersona] = useState<WritingPersona | null>(null);
  const [platformPersona, setPlatformPersona] = useState<PlatformAdaptation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add request throttling
  const lastRequestTime = useRef<number>(0);
  const requestInProgress = useRef<boolean>(false);
  const dataCacheTime = useRef<number>(0);
  
  // Cache duration: 5 minutes
  const CACHE_DURATION = 5 * 60 * 1000;

  // Fetch persona data function
  const fetchPersonas = useCallback(async () => {
    const now = Date.now();
    
    // Prevent multiple simultaneous requests
    if (requestInProgress.current) {
      console.log('🔄 Request already in progress, skipping...');
      return;
    }
    
    // Check cache validity
    if (corePersona && platformPersona && (now - dataCacheTime.current) < CACHE_DURATION) {
      console.log('✅ Using cached persona data');
      return;
    }
    
    // Rate limiting: minimum 2 seconds between requests
    if (now - lastRequestTime.current < 2000) {
      console.log('⏱️ Rate limit: waiting before next request...');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Fetch both core persona and platform-specific data
      const [userPersonasResponse, platformPersonaResponse] = await Promise.all([
        getUserPersonas(userId),
        getPlatformPersona(userId, platform)
      ]);

      // Handle core persona data
      if (userPersonasResponse.personas && userPersonasResponse.personas.length > 0) {
        const primaryPersona = userPersonasResponse.personas[0];
        
        // Convert API response to WritingPersona format
        const convertedPersona: WritingPersona = {
          id: primaryPersona.persona_id,
          user_id: userId,
          persona_name: primaryPersona.persona_name,
          archetype: primaryPersona.archetype,
          core_belief: primaryPersona.core_belief,
          brand_voice_description: primaryPersona.core_belief, // Use core_belief as fallback
          linguistic_fingerprint: {
            sentence_metrics: {
              average_sentence_length_words: 15,
              preferred_sentence_type: "compound",
              active_to_passive_ratio: "80:20",
              sentence_complexity: "moderate",
              paragraph_structure: "standard"
            },
            lexical_features: {
              go_to_words: ["leverage", "optimize", "strategic"],
              go_to_phrases: ["Let's explore", "Here's the thing"],
              avoid_words: ["utilize", "synergize"],
              contractions: "moderate",
              vocabulary_level: "professional",
              industry_terminology: [],
              emotional_tone_words: []
            },
            rhetorical_devices: {
              metaphors: "tech_mechanics",
              analogies: "everyday_to_tech",
              rhetorical_questions: "occasional",
              storytelling_approach: "case_study",
              persuasion_techniques: ["logic", "credibility"]
            }
          },
          platform_adaptations: [],
          onboarding_session_id: 1,
          source_website_analysis: {},
          source_research_preferences: {},
          ai_analysis_version: "1.0",
          confidence_score: primaryPersona.confidence_score,
          analysis_date: primaryPersona.created_at,
          created_at: primaryPersona.created_at,
          updated_at: primaryPersona.created_at,
          is_active: true
        };
        
        setCorePersona(convertedPersona);
        
        console.log('✅ Core persona loaded:', {
          name: convertedPersona.persona_name,
          archetype: convertedPersona.archetype,
          confidence: convertedPersona.confidence_score
        });
      } else {
        console.warn('⚠️ No core personas found for user');
        setCorePersona(null);
      }

      // Handle platform-specific persona data
      if (platformPersonaResponse) {
        // Convert API response to PlatformAdaptation format
        const convertedPlatformPersona: PlatformAdaptation = {
          id: 1,
          writing_persona_id: corePersona?.id || 1,
          platform_type: platform,
          sentence_metrics: {
            optimal_length: "150-300 words",
            character_limit: platform === 'linkedin' ? 3000 : 280,
            sentence_structure: "varied",
            paragraph_breaks: "frequent",
            readability_score: 8.5
          },
          lexical_features: {
            hashtag_strategy: "3-5 relevant hashtags",
            platform_specific_terms: [],
            engagement_phrases: ["What do you think?", "Share your thoughts"],
            call_to_action_style: "gentle"
          },
          rhetorical_devices: {
            question_frequency: "occasional",
            story_elements: "personal_anecdotes",
            visual_descriptions: "minimal",
            interactive_elements: "questions"
          },
          tonal_range: {
            default_tone: "professional_friendly",
            permissible_tones: ["inspiring", "thoughtful"],
            forbidden_tones: ["salesy", "academic"],
            emotional_range: "moderate",
            formality_level: "semi_formal"
          },
          stylistic_constraints: {
            punctuation_preferences: "standard",
            formatting_rules: "clean",
            emoji_usage: "minimal",
            link_placement: "end",
            media_integration: "encouraged"
          },
          content_format_rules: {
            character_limit: platform === 'linkedin' ? 3000 : 280,
            optimal_length: platform === 'linkedin' ? "150-300 words" : "120-150 characters",
            word_count: platform === 'linkedin' ? "150-300" : "20-25",
            hashtag_limit: platform === 'instagram' ? 30 : 3,
            media_requirements: "optional",
            link_restrictions: "unlimited"
          },
          engagement_patterns: {
            posting_frequency: "2-3 times per week",
            best_timing: "9 AM - 11 AM, 1 PM - 3 PM",
            interaction_style: "conversational",
            response_strategy: "within 2 hours",
            community_approach: "collaborative"
          },
          posting_frequency: {
            frequency: "2-3 times per week",
            optimal_days: ["Tuesday", "Wednesday", "Thursday"],
            optimal_times: ["9:00 AM", "1:00 PM"],
            seasonal_adjustments: "moderate"
          },
          content_types: {
            primary_content: ["thought_leadership", "industry_insights"],
            secondary_content: ["personal_stories", "tips"],
            content_mix: "70% professional, 30% personal",
            seasonal_content: ["trending_topics", "industry_events"]
          },
          platform_best_practices: {
            algorithm_tips: ["post_consistently", "engage_with_community"],
            engagement_tactics: ["ask_questions", "share_stories"],
            content_strategies: ["value_first", "authentic_voice"],
            growth_hacks: ["cross_promotion", "collaboration"]
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        
        setPlatformPersona(convertedPlatformPersona);
        
        console.log('✅ Platform persona loaded:', {
          platform: convertedPlatformPersona.platform_type,
          characterLimit: convertedPlatformPersona.content_format_rules?.character_limit,
          optimalLength: convertedPlatformPersona.content_format_rules?.optimal_length
        });
      } else {
        console.warn(`⚠️ No platform-specific persona found for ${platform}`);
        setPlatformPersona(null);
      }

    } catch (error) {
      console.error('❌ Error fetching personas:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch persona data');
      
      // Set fallback data if available
      if (corePersona) {
        console.log('🔄 Using existing core persona data');
      }
    } finally {
      setLoading(false);
      lastRequestTime.current = Date.now();
      dataCacheTime.current = Date.now();
      requestInProgress.current = false;
    }
  }, [userId, platform, corePersona]);

  // Initial data fetch
  useEffect(() => {
    fetchPersonas();
  }, [fetchPersonas]);

  // Refresh function for manual updates
  const refreshPersonas = async () => {
    await fetchPersonas();
  };

  // Inject core persona into CopilotKit context
  useCopilotReadable({
    description: `Core writing persona: ${corePersona?.persona_name || 'Loading...'}`,
    value: corePersona,
    categories: ["core-persona", "writing-style", "user-preferences"],
    parentId: corePersona?.id?.toString()
  });

  // Inject platform-specific persona into CopilotKit context
  useCopilotReadable({
    description: `${platform} platform optimization rules and constraints`,
    value: platformPersona,
    categories: ["platform-persona", platform, "content-optimization"],
    parentId: corePersona?.id?.toString()
  });

  // Inject combined persona context for comprehensive understanding
  useCopilotReadable({
    description: `Complete ${platform} writing persona with linguistic fingerprint and platform optimization`,
    value: {
      core: corePersona,
      platform: platformPersona,
      combined: {
        persona_name: corePersona?.persona_name,
        archetype: corePersona?.archetype,
        platform: platform,
        linguistic_fingerprint: corePersona?.linguistic_fingerprint,
        platform_constraints: platformPersona?.content_format_rules,
        engagement_patterns: platformPersona?.engagement_patterns
      }
    },
    categories: ["complete-persona", platform, "writing-guidance"],
    parentId: corePersona?.id?.toString()
  });

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
          <p className="text-sm text-gray-600">Loading {platform} persona...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error && !corePersona) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Failed to load persona data</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
            <button
              onClick={refreshPersonas}
              className="mt-2 text-sm text-red-600 hover:text-red-500 underline"
            >
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Success state - provide context
  return (
    <PlatformPersonaContext.Provider value={{ 
      corePersona, 
      platformPersona, 
      platform,
      loading,
      error,
      refreshPersonas
    }}>
      {children}
    </PlatformPersonaContext.Provider>
  );
};
// Custom hook to use the context
export const usePlatformPersonaContext = () => {
  const context = useContext(PlatformPersonaContext);
  if (!context) {
    throw new Error('usePlatformPersonaContext must be used within PlatformPersonaProvider');
  }
  return context;
};

// Export the context for direct access if needed
export { PlatformPersonaContext };

