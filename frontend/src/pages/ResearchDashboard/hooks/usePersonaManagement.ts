import { useState, useEffect } from 'react';
import { getResearchConfig, PersonaDefaults, refreshResearchPersona, ResearchPersona } from '../../../api/researchConfig';
import { ResearchPreset } from '../types';
import { generatePersonaPresets } from '../utils/presetUtils';
import { SAMPLE_PRESETS } from '../constants';

/**
 * Hook to manage research persona state and operations
 */
export const usePersonaManagement = () => {
  const [personaData, setPersonaData] = useState<PersonaDefaults | null>(null);
  const [researchPersona, setResearchPersona] = useState<ResearchPersona | null>(null);
  const [personaExists, setPersonaExists] = useState(false);
  const [personaChecked, setPersonaChecked] = useState(false);
  const [displayPresets, setDisplayPresets] = useState<ResearchPreset[]>(SAMPLE_PRESETS);
  const [showPersonaModal, setShowPersonaModal] = useState(false);
  const [loadingPersonaDetails, setLoadingPersonaDetails] = useState(false);

  // Load persona data on mount
  useEffect(() => {
    const loadPersonaPresets = async () => {
      console.log('[ResearchDashboard] Starting persona check...');
      try {
        const config = await getResearchConfig();
        console.log('[ResearchDashboard] 📥 Config received:', {
          hasResearchPersona: !!config.research_persona,
          hasResearchPersonaFlag: config.persona_defaults?.has_research_persona,
          onboardingCompleted: config.onboarding_completed,
          personaScheduled: config.persona_scheduled,
        });
        
        setPersonaData(config.persona_defaults || null);
        
        // Check if persona exists
        const hasPersonaObject = config.research_persona && 
          typeof config.research_persona === 'object' && 
          Object.keys(config.research_persona).length > 0;
        const hasPersonaFlag = config.persona_defaults?.has_research_persona === true;
        const hasPersona = hasPersonaObject || hasPersonaFlag;
        
        console.log('[ResearchDashboard] 🔍 Persona check:', {
          hasPersonaObject,
          hasPersonaFlag,
          hasPersona,
        });
        
        if (hasPersona && config.research_persona) {
          console.log('[ResearchDashboard] ✅ Research persona found in database');
          setResearchPersona(config.research_persona);
          setPersonaExists(true);
          
          // Use AI-generated presets if persona exists
          if (config.research_persona.recommended_presets && 
              config.research_persona.recommended_presets.length > 0) {
            console.log('[ResearchDashboard] Using AI-generated presets from persona');
            const aiPresets = config.research_persona.recommended_presets.map((preset: any) => ({
              name: preset.name,
              keywords: typeof preset.keywords === 'string' 
                ? preset.keywords 
                : Array.isArray(preset.keywords) 
                  ? preset.keywords.join(', ')
                  : 'N/A',
              industry: config.persona_defaults?.industry || 'General',
              targetAudience: config.persona_defaults?.target_audience || 'General',
              researchMode: preset.config?.mode || 'comprehensive',
              icon: preset.icon || '🔍',
              gradient: preset.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              config: preset.config || {}
            }));
            setDisplayPresets([...aiPresets, ...SAMPLE_PRESETS.slice(0, 2)]);
          } else {
            console.log('[ResearchDashboard] Persona exists but no recommended presets, using rule-based presets');
            const dynamicPresets = generatePersonaPresets(config.persona_defaults || null);
            setDisplayPresets(dynamicPresets);
          }
        } else {
          console.log('[ResearchDashboard] ⚠️ Research persona NOT found in database');
          const dynamicPresets = generatePersonaPresets(config.persona_defaults || null);
          setDisplayPresets(dynamicPresets);
          
          // Show modal when research persona is missing
          console.log('[ResearchDashboard] ✅ Research persona missing - SHOWING MODAL');
          setShowPersonaModal(true);
          setPersonaExists(false);
        }
        
        setPersonaChecked(true);
      } catch (error) {
        console.error('[ResearchDashboard] ❌ ERROR: Failed to load persona data:', error);
        setDisplayPresets(SAMPLE_PRESETS);
        setPersonaChecked(true);
      }
    };
    
    loadPersonaPresets();
  }, []);

  const handleGeneratePersona = async () => {
    console.log('[ResearchDashboard] 🔄 User clicked "Generate Persona" - starting generation...');
    try {
      const persona = await refreshResearchPersona(true);
      console.log('[ResearchDashboard] ✅ Persona generated successfully:', {
        defaultIndustry: persona.default_industry,
        hasRecommendedPresets: !!persona.recommended_presets
      });
      
      setResearchPersona(persona);
      setPersonaExists(true);
      
      // Reload config to get updated presets
      const config = await getResearchConfig();
      if (config.research_persona?.recommended_presets && 
          config.research_persona.recommended_presets.length > 0) {
        console.log('[ResearchDashboard] Updating presets with AI-generated presets');
        const aiPresets = config.research_persona.recommended_presets.map((preset: any) => ({
          name: preset.name,
          keywords: typeof preset.keywords === 'string' 
            ? preset.keywords 
            : Array.isArray(preset.keywords) 
              ? preset.keywords.join(', ')
              : 'N/A',
          industry: config.persona_defaults?.industry || 'General',
          targetAudience: config.persona_defaults?.target_audience || 'General',
          researchMode: preset.config?.mode || 'comprehensive',
          icon: preset.icon || '🔍',
          gradient: preset.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          config: preset.config || {}
        }));
        setDisplayPresets([...aiPresets, ...SAMPLE_PRESETS.slice(0, 2)]);
      }
      
      console.log('[ResearchDashboard] ✅ Persona generation complete - closing modal');
      setShowPersonaModal(false);
    } catch (error) {
      console.error('[ResearchDashboard] ❌ Failed to generate research persona:', error);
      throw error; // Let modal handle the error display
    }
  };

  const handleCancelPersona = () => {
    console.log('[ResearchDashboard] ✅ User cancelled persona generation');
    setShowPersonaModal(false);
  };

  const handleOpenPersonaDetails = async () => {
    setLoadingPersonaDetails(true);
    
    try {
      const config = await getResearchConfig();
      if (config.research_persona) {
        setResearchPersona(config.research_persona);
      }
    } catch (error) {
      console.error('[ResearchDashboard] Error loading persona details:', error);
    } finally {
      setLoadingPersonaDetails(false);
    }
  };

  return {
    personaData,
    researchPersona,
    personaExists,
    personaChecked,
    displayPresets,
    showPersonaModal,
    loadingPersonaDetails,
    handleGeneratePersona,
    handleCancelPersona,
    handleOpenPersonaDetails,
    setShowPersonaModal,
    setPersonaExists,
    setResearchPersona,
    setDisplayPresets,
  };
};
