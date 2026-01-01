import React, { useState, useEffect } from 'react';
import { WizardStepProps } from '../types/research.types';
import { ResearchProvider, ResearchMode } from '../../../services/blogWriterApi';
import { getResearchConfig, ProviderAvailability } from '../../../api/researchConfig';
import { 
  getResearchHistory, 
  ResearchHistoryEntry 
} from '../../../utils/researchHistory';
import { 
  expandKeywords,
  expandKeywordsWithPersona
} from '../../../utils/keywordExpansion';
import { 
  generateResearchAngles
} from '../../../utils/researchAngles';

// Utilities
import { parseIntelligentInput } from './utils/inputParser';
import { getIndustryPlaceholders } from './utils/placeholders';
import { suggestResearchMode } from './utils/researchModeSuggester';
import { getIndustryDomainSuggestions, getIndustryExaCategory } from './utils/industryDefaults';

// Components
import { ResearchHistory } from './components/ResearchHistory';
import { ResearchInputContainer } from './components/ResearchInputContainer';
import { SmartInputIndicator } from './components/SmartInputIndicator';
import { KeywordExpansion } from './components/KeywordExpansion';
import { CurrentKeywords } from './components/CurrentKeywords';
import { ResearchAngles } from './components/ResearchAngles';
import { TavilyOptions } from './components/TavilyOptions';
import { ExaOptions } from './components/ExaOptions';
import { PersonalizationIndicator, PersonalizationBadge } from './components/PersonalizationIndicator';
import { IntentConfirmationPanel } from './components/IntentConfirmationPanel';
import { ResearchExecution } from '../types/research.types';

interface ResearchInputProps extends WizardStepProps {
  advanced?: boolean;
  onAdvancedChange?: (advanced: boolean) => void;
  execution?: ResearchExecution;
}

export const ResearchInput: React.FC<ResearchInputProps> = ({ state, onUpdate, onNext, advanced: advancedProp, onAdvancedChange, execution }) => {
  const [currentPlaceholder, setCurrentPlaceholder] = useState(0);
  const [providerAvailability, setProviderAvailability] = useState<ProviderAvailability | null>(null);
  const [loadingConfig, setLoadingConfig] = useState(true);
  const [suggestedMode, setSuggestedMode] = useState<ResearchMode | null>(null);
  const [researchHistory, setResearchHistory] = useState<ResearchHistoryEntry[]>([]);
  const [keywordExpansion, setKeywordExpansion] = useState<{
    original: string[];
    expanded: string[];
    suggestions: string[];
  } | null>(null);
  const [researchAngles, setResearchAngles] = useState<string[]>([]);
  const [researchPersona, setResearchPersona] = useState<{
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
  } | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);
  
  // Use prop if provided, otherwise use local state
  const [localAdvanced, setLocalAdvanced] = useState<boolean>(false);
  const advanced = advancedProp !== undefined ? advancedProp : localAdvanced;
  const setAdvanced = onAdvancedChange || setLocalAdvanced;

  // Load research history on mount and when component updates
  useEffect(() => {
    const history = getResearchHistory();
    setResearchHistory(history);
  }, []); // Load once on mount

  // Reload history when keywords change (after research completes)
  useEffect(() => {
    const history = getResearchHistory();
    setResearchHistory(history);
  }, [state.keywords]);

  // Load research configuration on mount
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const config = await getResearchConfig();
        
        // Set provider availability with fallback
        setProviderAvailability(config?.provider_availability || {
          google_available: true, // Default to available, will be corrected by actual key status
          exa_available: false,
          tavily_available: false,
          tavily_key_status: 'missing',
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
        
        // Phase 2: Apply persona defaults from API
        // Backend now returns hyper-personalized values (never "General")
        // Always apply if we have values and user hasn't customized
        if (config?.persona_defaults) {
          const defaults = config.persona_defaults;
          
          // Log whether research persona exists
          console.log('[ResearchInput] Persona defaults loaded:', {
            hasResearchPersona: defaults.has_research_persona,
            industry: defaults.industry,
            targetAudience: defaults.target_audience,
            hasDomains: defaults.suggested_domains?.length > 0
          });
          
          // Apply industry if provided and user hasn't customized
          // Phase 2: Backend never returns "General", so we apply unless user has real value
          if (defaults.industry && (!state.industry || state.industry === 'General')) {
            onUpdate({ industry: defaults.industry });
          }
          
          // Apply target audience if provided
          if (defaults.target_audience && (!state.targetAudience || state.targetAudience === 'General')) {
            onUpdate({ targetAudience: defaults.target_audience });
          }
          
          // Apply suggested Exa domains if Exa is available and not already set
          if (config.provider_availability?.exa_available && defaults.suggested_domains?.length > 0) {
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

          // Phase 2+: Apply enhanced Exa defaults from research persona
          if (defaults.suggested_exa_search_type && !state.config.exa_search_type) {
            onUpdate({
              config: {
                ...state.config,
                exa_search_type: defaults.suggested_exa_search_type as 'auto' | 'keyword' | 'neural'
              }
            });
          }

          // Phase 2+: Apply Tavily defaults from research persona
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
          
          // Phase 2: Apply additional hyper-personalization defaults from research persona
          if (defaults.has_research_persona && config.research_persona) {
            console.log('[ResearchInput] Applying research persona hyper-personalization:', {
              researchMode: defaults.default_research_mode,
              provider: defaults.default_provider,
              suggestedKeywords: defaults.suggested_keywords?.length || 0,
              researchAngles: defaults.research_angles?.length || 0,
              recommendedPresets: config.research_persona.recommended_presets?.length || 0
            });
            
            // Store research persona data for personalized placeholders, keyword expansion, and research angles
            setResearchPersona({
              research_angles: config.research_persona.research_angles || defaults.research_angles,
              recommended_presets: config.research_persona.recommended_presets || [],
              suggested_keywords: config.research_persona.suggested_keywords || defaults.suggested_keywords,
              keyword_expansion_patterns: config.research_persona.keyword_expansion_patterns,
              industry: config.research_persona.default_industry || defaults.industry,
              target_audience: config.research_persona.default_target_audience || defaults.target_audience
            });
            
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
                  (defaults.default_provider === 'exa' && config.provider_availability?.exa_available) ||
                  (defaults.default_provider === 'tavily' && config.provider_availability?.tavily_available) ||
                  (defaults.default_provider === 'google' && config.provider_availability?.google_available);
                
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
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error('[ResearchInput] Failed to load research config:', errorMessage);
        
        // Set default provider availability on error
        setProviderAvailability({
          google_available: true, // Optimistically assume available
          exa_available: false,
          tavily_available: false,
          tavily_key_status: 'missing',
          gemini_key_status: 'missing',
          exa_key_status: 'missing'
        });
        
        // Continue with defaults - don't block the UI
      } finally {
        setLoadingConfig(false);
      }
    };
    
    loadConfig();
  }, []); // Only run once on mount

  // Get industry-specific placeholders, enhanced with research persona data
  const placeholderExamples = getIndustryPlaceholders(state.industry, researchPersona || undefined);
  
  // Rotate placeholder examples every 4 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPlaceholder((prev) => (prev + 1) % placeholderExamples.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [placeholderExamples.length]);
  
  // Reset placeholder index when industry changes
  useEffect(() => {
    setCurrentPlaceholder(0);
  }, [state.industry]);
  
  // Auto-set provider based on availability
  // Priority: Exa → Tavily → Google for ALL modes (including basic)
  // This provides better semantic search results for content creators
  useEffect(() => {
    if (!providerAvailability) return;
    
    // Priority: Exa → Tavily → Google for all modes
    let newProvider: ResearchProvider = 'google';
    
    if (providerAvailability.exa_available) {
      newProvider = 'exa';
    } else if (providerAvailability.tavily_available) {
      newProvider = 'tavily';
    } else {
      newProvider = 'google';
    }
    
    // Only update if provider changed
    if (state.config.provider !== newProvider) {
      console.log('[ResearchInput] Auto-selecting provider:', newProvider, 'for mode:', state.researchMode);
      onUpdate({ config: { ...state.config, provider: newProvider } });
    }
  }, [state.researchMode, providerAvailability]);
  
  // Dynamic domain suggestions when industry changes
  useEffect(() => {
    if (!providerAvailability || state.industry === 'General') return;
    
    const newDomains = getIndustryDomainSuggestions(state.industry);
    const newCategory = getIndustryExaCategory(state.industry);
    
    // Only update if Exa is available and domains/category should change
    if (providerAvailability.exa_available && newDomains.length > 0) {
      const configUpdates: any = {};
      
      // Update domains if different
      const currentDomains = state.config.exa_include_domains || [];
      if (JSON.stringify(currentDomains) !== JSON.stringify(newDomains)) {
        configUpdates.exa_include_domains = newDomains;
      }
      
      // Update category if available and different
      if (newCategory && state.config.exa_category !== newCategory) {
        configUpdates.exa_category = newCategory;
      }
      
      // Apply updates if any
      if (Object.keys(configUpdates).length > 0) {
        onUpdate({ 
          config: { 
            ...state.config, 
            ...configUpdates 
          } 
        });
      }
    }
  }, [state.industry, providerAvailability]);

  // Expand keywords when keywords or industry changes
  // Enhanced to use research persona data if available
  useEffect(() => {
    if (state.keywords.length > 0) {
      let expansion;
      
      // If we have research persona with keyword expansion patterns, use them
      if (researchPersona?.keyword_expansion_patterns && Object.keys(researchPersona.keyword_expansion_patterns).length > 0) {
        expansion = expandKeywordsWithPersona(state.keywords, researchPersona.keyword_expansion_patterns, researchPersona.suggested_keywords);
      } else if (state.industry !== 'General') {
        // Fallback to industry-based expansion
        expansion = expandKeywords(state.keywords, state.industry);
      } else {
        expansion = { original: state.keywords, expanded: state.keywords, suggestions: [] };
      }
      
      setKeywordExpansion(expansion);
    } else {
      setKeywordExpansion(null);
    }
  }, [state.keywords, state.industry, researchPersona]);

  // Generate research angles when keywords change
  // Enhanced to prioritize research persona angles if available
  useEffect(() => {
    if (state.keywords.length > 0) {
      const query = state.keywords.join(' ');
      let angles: string[] = [];
      
      // Priority 1: Use research persona angles if available and relevant
      if (researchPersona?.research_angles && researchPersona.research_angles.length > 0) {
        // Filter persona angles that are relevant to the current query
        const relevantPersonaAngles = researchPersona.research_angles
          .filter(angle => {
            const angleLower = angle.toLowerCase();
            const queryLower = query.toLowerCase();
            // Check if angle contains any keyword from query or vice versa
            return state.keywords.some(kw => angleLower.includes(kw.toLowerCase()) || queryLower.includes(kw.toLowerCase())) ||
                   angleLower.includes(queryLower) || queryLower.includes(angleLower);
          })
          .slice(0, 3); // Use top 3 relevant persona angles
        
        angles.push(...relevantPersonaAngles);
      }
      
      // Priority 2: Generate additional angles using pattern matching
      const generatedAngles = generateResearchAngles(query, state.industry);
      
      // Merge and deduplicate, prioritizing persona angles
      const allAngles = [...angles, ...generatedAngles];
      const uniqueAngles = Array.from(new Set(allAngles.map(a => a.toLowerCase())))
        .slice(0, 5) // Limit to 5 total
        .map(a => {
          // Find original casing from persona angles first, then generated
          const personaMatch = angles.find(pa => pa.toLowerCase() === a);
          if (personaMatch) return personaMatch;
          const generatedMatch = generatedAngles.find(ga => ga.toLowerCase() === a);
          return generatedMatch || a.charAt(0).toUpperCase() + a.slice(1);
        });
      
      setResearchAngles(uniqueAngles);
    } else {
      setResearchAngles([]);
    }
  }, [state.keywords, state.industry, researchPersona]);

  // Event handlers
  const handleKeywordsChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const keywords = parseIntelligentInput(value);
    onUpdate({ keywords });
    
    // Update suggested mode
    const suggested = suggestResearchMode(keywords);
    setSuggestedMode(suggested);
  };

  const handleAddSuggestion = (suggestion: string) => {
    const currentKeywords = [...state.keywords];
    // Check if suggestion already exists (case-insensitive)
    const exists = currentKeywords.some(k => k.toLowerCase() === suggestion.toLowerCase());
    if (!exists) {
      currentKeywords.push(suggestion);
      onUpdate({ keywords: currentKeywords });
    }
  };

  const handleRemoveKeyword = (keywordToRemove: string) => {
    const currentKeywords = state.keywords.filter(k => k.toLowerCase() !== keywordToRemove.toLowerCase());
    onUpdate({ keywords: currentKeywords });
  };

  const handleUseAngle = (angle: string) => {
    // Parse the angle as a new research query
    const keywords = parseIntelligentInput(angle);
    onUpdate({ keywords });
  };

  const handleIndustryChange = (industry: string) => {
    onUpdate({ industry });
  };


  const handleModeChange = (mode: ResearchMode) => {
    onUpdate({ researchMode: mode });
  };

  const handleProviderChange = (provider: ResearchProvider) => {
    onUpdate({ config: { ...state.config, provider } });
  };

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      console.log('File selected:', file.name);
      // TODO: Implement file upload logic
    }
  };

  const handleConfigUpdate = (updates: Partial<typeof state.config>) => {
    onUpdate({ config: { ...state.config, ...updates } });
  };

  const handleLoadHistory = (entry: Partial<typeof state>) => {
    onUpdate(entry);
  };

  const handleHistoryCleared = () => {
    setResearchHistory([]);
  };

  return (
    <div style={{ maxWidth: '100%' }}>
      {/* Main Input Area */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.6)',
        backdropFilter: 'blur(8px)',
        border: '2px solid rgba(14, 165, 233, 0.2)',
        borderRadius: '16px',
        padding: '20px',
        marginBottom: '20px',
        transition: 'all 0.3s ease',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(14, 165, 233, 0.12)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
        e.currentTarget.style.boxShadow = 'none';
      }}
      >
        <div style={{
          marginBottom: '12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '12px',
        }}>
          <label style={{
            fontSize: '15px',
            fontWeight: '600',
            color: '#0c4a6e',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            flex: '1',
          }}>
            <span style={{
              fontSize: '20px',
            }}>🔍</span>
            Research Topic & Keywords
            <PersonalizationIndicator 
              type="placeholder" 
              hasPersona={!!researchPersona}
              source={researchPersona ? "from your research persona" : undefined}
            />
          </label>
          
          {/* Advanced Toggle and Upload Button */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            {/* Advanced Toggle */}
            <label
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                cursor: 'pointer',
                padding: '6px 10px',
                borderRadius: '8px',
                border: `1px solid ${advanced ? 'rgba(14, 165, 233, 0.3)' : 'rgba(15, 23, 42, 0.1)'}`,
                background: advanced
                  ? 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)'
                  : '#ffffff',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                fontSize: '11px',
                fontWeight: '600',
                color: advanced ? '#0369a1' : '#475569',
                boxShadow: advanced ? '0 1px 3px rgba(14, 165, 233, 0.12)' : '0 1px 2px rgba(0, 0, 0, 0.04)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = advanced ? 'rgba(14, 165, 233, 0.4)' : 'rgba(15, 23, 42, 0.15)';
                e.currentTarget.style.boxShadow = advanced
                  ? '0 2px 4px rgba(14, 165, 233, 0.18)'
                  : '0 1px 3px rgba(0, 0, 0, 0.06)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = advanced ? 'rgba(14, 165, 233, 0.3)' : 'rgba(15, 23, 42, 0.1)';
                e.currentTarget.style.boxShadow = advanced
                  ? '0 1px 3px rgba(14, 165, 233, 0.12)'
                  : '0 1px 2px rgba(0, 0, 0, 0.04)';
              }}
              title="Enable advanced research options (Exa and Tavily configurations)"
            >
              <input
                type="checkbox"
                checked={advanced}
                onChange={(e) => {
                  if (onAdvancedChange) {
                    onAdvancedChange(e.target.checked);
                  } else {
                    setLocalAdvanced(e.target.checked);
                  }
                }}
                style={{
                  width: '14px',
                  height: '14px',
                  cursor: 'pointer',
                  accentColor: '#0ea5e9',
                }}
              />
              <span>Advanced</span>
            </label>

            {/* Upload Button */}
            <button
              onClick={handleFileUpload}
              type="button"
              style={{
                padding: '6px 10px',
                background: 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)',
                border: '1px solid rgba(14, 165, 233, 0.25)',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '11px',
                fontWeight: '600',
                color: '#0369a1',
                display: 'flex',
                alignItems: 'center',
                gap: '5px',
                transition: 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)',
                boxShadow: '0 1px 2px rgba(14, 165, 233, 0.12)',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.15) 0%, rgba(59, 130, 246, 0.15) 100%)';
                e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.35)';
                e.currentTarget.style.transform = 'translateY(-1px)';
                e.currentTarget.style.boxShadow = '0 2px 4px rgba(14, 165, 233, 0.18)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'linear-gradient(135deg, rgba(14, 165, 233, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%)';
                e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.25)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 1px 2px rgba(14, 165, 233, 0.12)';
              }}
              title="Upload Document"
            >
              <span style={{ fontSize: '13px' }}>📎</span>
              <span>Upload</span>
            </button>
          </div>
        </div>
        
        {/* Research History */}
        <ResearchHistory
          history={researchHistory}
          onLoadHistory={handleLoadHistory}
          onHistoryCleared={handleHistoryCleared}
        />
        
        {/* Main Input Container */}
        <ResearchInputContainer
          keywords={state.keywords}
          placeholder={placeholderExamples[currentPlaceholder]}
          onKeywordsChange={handleKeywordsChange}
        />
        
        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileChange}
          accept=".txt,.doc,.docx,.pdf"
          style={{ display: 'none' }}
        />
        
        {/* Smart Input Detection Indicator */}
        <SmartInputIndicator keywords={state.keywords} />

        {/* Intent Analysis Panel - Show when intent analysis is available */}
        {execution && (execution.isAnalyzingIntent || execution.intentAnalysis) && (
          <IntentConfirmationPanel
            isAnalyzing={execution.isAnalyzingIntent}
            intentAnalysis={execution.intentAnalysis}
            confirmedIntent={execution.confirmedIntent}
            onConfirm={execution.confirmIntent}
            onUpdateField={execution.updateIntentField}
            onExecute={async () => {
              const result = await execution.executeIntentResearch(state);
              if (result?.success) {
                // Skip to results step
                onUpdate({ currentStep: 3 });
              }
            }}
            onDismiss={execution.clearIntent}
            isExecuting={execution.isExecuting}
          />
        )}

        {/* Keyword Expansion Suggestions */}
        {keywordExpansion && keywordExpansion.suggestions.length > 0 && (
          <KeywordExpansion
            suggestions={keywordExpansion.suggestions}
            currentKeywords={state.keywords}
            industry={state.industry}
            onAddSuggestion={handleAddSuggestion}
          />
        )}

        {/* Current Keywords Display */}
        <CurrentKeywords
          keywords={state.keywords}
          onRemoveKeyword={handleRemoveKeyword}
        />

        {/* Alternative Research Angles */}
        <ResearchAngles
          angles={researchAngles}
          onUseAngle={handleUseAngle}
          hasPersona={!!researchPersona}
        />

      </div>


      {/* Advanced Options - Show when Advanced toggle is ON */}
      {advanced && (
        <>
          {/* Tavily-Specific Options */}
          {providerAvailability?.tavily_available && (
            <TavilyOptions
              config={state.config}
              onConfigUpdate={handleConfigUpdate}
            />
          )}

          {/* Exa-Specific Options */}
          {providerAvailability?.exa_available && (
            <ExaOptions
              config={state.config}
              onConfigUpdate={handleConfigUpdate}
            />
          )}
        </>
      )}

    </div>
  );
};
