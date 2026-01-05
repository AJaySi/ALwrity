/**
 * Hook for loading and managing research configuration and persona defaults
 */

import { useState, useEffect } from 'react';
import { getResearchConfig, ProviderAvailability } from '../../../../api/researchConfig';
import { WizardState } from '../../types/research.types';
import { ResearchProvider } from '../../../../services/blogWriterApi';

interface ResearchPersona {
  research_angles?: string[];
  recommended_presets?: Array<{
    name: string;
    keywords: string | string[];
    description?: string;
  }>;
  suggested_keywords?: string[];
  keyword_expansion_patterns?: Record<string, string[]>;
  industry?: string;
  target_audience?: string;
}

interface UseResearchConfigResult {
  providerAvailability: ProviderAvailability | null;
  researchPersona: ResearchPersona | null;
  loadingConfig: boolean;
  applyPersonaDefaults: (state: WizardState, onUpdate: (updates: Partial<WizardState>) => void) => void;
}

export const useResearchConfig = (): UseResearchConfigResult => {
  const [providerAvailability, setProviderAvailability] = useState<ProviderAvailability | null>(null);
  const [researchPersona, setResearchPersona] = useState<ResearchPersona | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [configData, setConfigData] = useState<any>(null);

  // Load research configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await getResearchConfig();
        setConfigData(config);
        
        // Set provider availability with fallback
        setProviderAvailability(config?.provider_availability || {
          google_available: true,
          exa_available: false,
          tavily_available: false,
          tavily_key_status: 'missing',
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
        
        // Store research persona data if available
        if (config?.research_persona || config?.persona_defaults) {
          const defaults = config.persona_defaults || {};
          setResearchPersona({
            research_angles: config.research_persona?.research_angles || defaults.research_angles,
            recommended_presets: config.research_persona?.recommended_presets || [],
            suggested_keywords: config.research_persona?.suggested_keywords || defaults.suggested_keywords,
            keyword_expansion_patterns: config.research_persona?.keyword_expansion_patterns,
            industry: config.research_persona?.default_industry || defaults.industry,
            target_audience: config.research_persona?.default_target_audience || defaults.target_audience
          });
        }
      } catch (error) {
        console.error('[useResearchConfig] Failed to load research config:', error);
        setProviderAvailability({
          google_available: true,
          exa_available: false,
          tavily_available: false,
          tavily_key_status: 'missing',
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
      } finally {
        setLoadingConfig(false);
      }
    };
    
    loadConfig();
  }, []);

  const applyPersonaDefaults = (state: WizardState, onUpdate: (updates: Partial<WizardState>) => void) => {
    if (!configData?.persona_defaults) return;

    const defaults = configData.persona_defaults;
    
    // Apply industry if provided and user hasn't customized
    if (defaults.industry && (!state.industry || state.industry === 'General')) {
      onUpdate({ industry: defaults.industry });
    }
    
    // Apply target audience if provided
    if (defaults.target_audience && (!state.targetAudience || state.targetAudience === 'General')) {
      onUpdate({ targetAudience: defaults.target_audience });
    }
    
    // Apply suggested Exa domains if Exa is available and not already set
    if (configData.provider_availability?.exa_available && defaults.suggested_domains?.length > 0) {
      if (!state.config.exa_include_domains || state.config.exa_include_domains.length === 0) {
        onUpdate({ 
          config: { 
            ...state.config, 
            exa_include_domains: defaults.suggested_domains 
          } 
        });
      }
    }
    
    // Apply suggested Exa category if available
    if (defaults.suggested_exa_category && !state.config.exa_category) {
      onUpdate({
        config: {
          ...state.config,
          exa_category: defaults.suggested_exa_category
        }
      });
    }

    // Apply enhanced Exa defaults from research persona
    if (defaults.suggested_exa_search_type && !state.config.exa_search_type) {
      onUpdate({
        config: {
          ...state.config,
          exa_search_type: defaults.suggested_exa_search_type as 'auto' | 'keyword' | 'neural'
        }
      });
    }

    // Apply Tavily defaults from research persona
    if (defaults.suggested_tavily_topic && !state.config.tavily_topic) {
      onUpdate({
        config: {
          ...state.config,
          tavily_topic: defaults.suggested_tavily_topic as 'general' | 'news' | 'finance'
        }
      });
    }

    if (defaults.suggested_tavily_search_depth && !state.config.tavily_search_depth) {
      onUpdate({
        config: {
          ...state.config,
          tavily_search_depth: defaults.suggested_tavily_search_depth as 'basic' | 'advanced'
        }
      });
    }

    if (defaults.suggested_tavily_include_answer && !state.config.tavily_include_answer) {
      const answerValue = defaults.suggested_tavily_include_answer === 'true' ? true :
                         defaults.suggested_tavily_include_answer === 'false' ? false :
                         defaults.suggested_tavily_include_answer as 'basic' | 'advanced';
      onUpdate({
        config: {
          ...state.config,
          tavily_include_answer: answerValue
        }
      });
    }

    if (defaults.suggested_tavily_time_range && !state.config.tavily_time_range) {
      onUpdate({
        config: {
          ...state.config,
          tavily_time_range: defaults.suggested_tavily_time_range as 'day' | 'week' | 'month' | 'year'
        }
      });
    }

    if (defaults.suggested_tavily_raw_content_format && !state.config.tavily_include_raw_content) {
      const rawContentValue = defaults.suggested_tavily_raw_content_format === 'true' ? true :
                             defaults.suggested_tavily_raw_content_format === 'false' ? false :
                             defaults.suggested_tavily_raw_content_format as 'markdown' | 'text';
      onUpdate({
        config: {
          ...state.config,
          tavily_include_raw_content: rawContentValue
        }
      });
    }
    
    // Apply additional hyper-personalization defaults from research persona
    if (defaults.has_research_persona) {
      // Apply default research mode if not already customized
      if (defaults.default_research_mode && state.researchMode === 'comprehensive') {
        const validModes = ['basic', 'comprehensive', 'targeted'] as const;
        if (validModes.includes(defaults.default_research_mode as typeof validModes[number])) {
          onUpdate({ researchMode: defaults.default_research_mode as typeof validModes[number] });
        }
      }
      
      // Apply default provider (only if it's available)
      if (defaults.default_provider) {
        const validProviders = ['exa', 'tavily', 'google'] as const;
        type ValidProvider = typeof validProviders[number];
        
        if (validProviders.includes(defaults.default_provider as ValidProvider)) {
          const providerAvailable = 
            (defaults.default_provider === 'exa' && configData.provider_availability?.exa_available) ||
            (defaults.default_provider === 'tavily' && configData.provider_availability?.tavily_available) ||
            (defaults.default_provider === 'google' && configData.provider_availability?.google_available);
          
          if (providerAvailable && !state.config.provider) {
            onUpdate({
              config: {
                ...state.config,
                provider: defaults.default_provider as ValidProvider
              }
            });
          }
        }
      }
    }
  };

  return {
    providerAvailability,
    researchPersona,
    loadingConfig,
    applyPersonaDefaults,
  };
};
