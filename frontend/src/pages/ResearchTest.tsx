import React, { useState, useEffect } from 'react';
import { ResearchWizard } from '../components/Research';
import { BlogResearchResponse } from '../services/blogWriterApi';
import { getResearchConfig, PersonaDefaults, refreshResearchPersona, ResearchPersona, getCompetitorAnalysis, CompetitorAnalysisResponse } from '../api/researchConfig';
import { ResearchPersonaModal } from '../components/Research/ResearchPersonaModal';
import { OnboardingCompetitorModal } from '../components/Research/OnboardingCompetitorModal';
import { Tooltip } from '@mui/material';
import { AutoAwesome } from '@mui/icons-material';

const samplePresets = [
  {
    name: 'AI Marketing Tools',
    keywords: 'Research latest AI-powered marketing automation tools and customer engagement platforms',
    industry: 'Technology',
    targetAudience: 'Marketing professionals and SaaS founders',
    researchMode: 'comprehensive' as const,
    icon: '🤖',
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    config: {
      mode: 'comprehensive' as const,
      provider: 'google' as const,
      max_sources: 15,
      include_statistics: true,
      include_expert_quotes: true,
      include_competitors: true,
      include_trends: true,
    }
  },
  {
    name: 'Small Business SEO',
    keywords: 'Write a blog on local SEO strategies for small businesses and Google My Business optimization',
    industry: 'Marketing',
    targetAudience: 'Small business owners and local entrepreneurs',
    researchMode: 'targeted' as const,
    icon: '📈',
    gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    config: {
      mode: 'targeted' as const,
      provider: 'google' as const,
      max_sources: 12,
      include_statistics: true,
      include_expert_quotes: false,
      include_competitors: true,
      include_trends: true,
    }
  },
  {
    name: 'Content Strategy',
    keywords: 'Analyze content planning frameworks and editorial calendar best practices for B2B marketing',
    industry: 'Marketing',
    targetAudience: 'Content marketers and marketing managers',
    researchMode: 'comprehensive' as const,
    icon: '✍️',
    gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    config: {
      mode: 'comprehensive' as const,
      provider: 'exa' as const,
      max_sources: 20,
      include_statistics: true,
      include_expert_quotes: true,
      include_competitors: false,
      include_trends: true,
      exa_category: 'research paper',
      exa_search_type: 'neural' as const,
    }
  },
  {
    name: 'Crypto Trends',
    keywords: 'Explore cryptocurrency market trends and blockchain adoption in enterprise',
    industry: 'Finance',
    targetAudience: 'Investors and blockchain developers',
    researchMode: 'comprehensive' as const,
    icon: '₿',
    gradient: 'linear-gradient(135deg, #f7931a 0%, #ffa94d 100%)',
    config: {
      mode: 'comprehensive' as const,
      provider: 'exa' as const,
      max_sources: 25,
      include_statistics: true,
      include_expert_quotes: true,
      include_competitors: true,
      include_trends: true,
      exa_category: 'news',
      exa_search_type: 'neural' as const,
    }
  },
  {
    name: 'Healthcare Tech',
    keywords: 'Research telemedicine platforms and remote patient monitoring technologies',
    industry: 'Healthcare',
    targetAudience: 'Healthcare administrators and medical professionals',
    researchMode: 'comprehensive' as const,
    icon: '⚕️',
    gradient: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
    config: {
      mode: 'comprehensive' as const,
      provider: 'exa' as const,
      max_sources: 20,
      include_statistics: true,
      include_expert_quotes: true,
      include_competitors: false,
      include_trends: true,
      exa_category: 'research paper',
      exa_search_type: 'neural' as const,
      exa_include_domains: ['pubmed.gov', 'nejm.org', 'thelancet.com'],
    }
  },
];

// Generate persona-specific presets dynamically
const generatePersonaPresets = (persona: PersonaDefaults | null): typeof samplePresets => {
  if (!persona || !persona.industry || persona.industry === 'General') {
    return samplePresets;
  }
  
  const industry = persona.industry;
  const audience = persona.target_audience || 'professionals';
  const exaCategory = persona.suggested_exa_category || '';
  const exaDomains = persona.suggested_domains || [];
  
  // Build config objects conditionally based on whether we have Exa options
  const baseConfig1: any = {
    mode: 'comprehensive' as const,
    provider: 'exa' as const,
    max_sources: 20,
    include_statistics: true,
    include_expert_quotes: true,
    include_competitors: true,
    include_trends: true,
    exa_search_type: 'neural' as const,
    ...(exaCategory ? { exa_category: exaCategory } : {}),
    ...(exaDomains.length > 0 ? { exa_include_domains: exaDomains } : {}),
  };
  
  const baseConfig2: any = {
    mode: 'targeted' as const,
    provider: 'exa' as const,
    max_sources: 15,
    include_statistics: true,
    include_expert_quotes: true,
    include_competitors: false,
    include_trends: true,
    exa_search_type: 'neural' as const,
    ...(exaCategory ? { exa_category: exaCategory } : {}),
    ...(exaDomains.length > 0 ? { exa_include_domains: exaDomains } : {}),
  };
  
  const baseConfig3: any = {
    mode: 'comprehensive' as const,
    provider: 'exa' as const,
    max_sources: 18,
    include_statistics: true,
    include_expert_quotes: true,
    include_competitors: true,
    include_trends: false,
    exa_search_type: 'neural' as const,
    ...(exaCategory ? { exa_category: exaCategory } : {}),
    ...(exaDomains.length > 0 ? { exa_include_domains: exaDomains } : {}),
  };
  
  const generatedPresets = [
    {
      name: `${industry} Trends`,
      keywords: `Research latest trends and innovations in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'comprehensive' as const,
      icon: '📊',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      config: baseConfig1,
    },
    {
      name: `${audience} Insights`,
      keywords: `Analyze ${audience} pain points and preferences in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'targeted' as const,
      icon: '🎯',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      config: baseConfig2,
    },
    {
      name: `${industry} Best Practices`,
      keywords: `Investigate best practices and success stories in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'comprehensive' as const,
      icon: '⭐',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      config: baseConfig3,
    }
  ];
  
  return [...generatedPresets, ...samplePresets.slice(0, 2)] as typeof samplePresets;
};

export const ResearchTest: React.FC = () => {
  const [results, setResults] = useState<BlogResearchResponse | null>(null);
  const [showDebug, setShowDebug] = useState(false);
  const [presetKeywords, setPresetKeywords] = useState<string[] | undefined>();
  const [presetIndustry, setPresetIndustry] = useState<string | undefined>();
  const [presetTargetAudience, setPresetTargetAudience] = useState<string | undefined>();
  const [presetMode, setPresetMode] = useState<any>();
  const [presetConfig, setPresetConfig] = useState<any>();
  const [personaData, setPersonaData] = useState<PersonaDefaults | null>(null);
  const [displayPresets, setDisplayPresets] = useState(samplePresets);
  const [showPersonaModal, setShowPersonaModal] = useState(false);
  const [personaChecked, setPersonaChecked] = useState(false);
  const [researchPersona, setResearchPersona] = useState<ResearchPersona | null>(null);
  const [showCompetitorModal, setShowCompetitorModal] = useState(false);
  const [competitorData, setCompetitorData] = useState<CompetitorAnalysisResponse | null>(null);
  const [loadingCompetitors, setLoadingCompetitors] = useState(false);
  const [competitorError, setCompetitorError] = useState<string | null>(null);
  const [showPersonaDetailsModal, setShowPersonaDetailsModal] = useState(false);
  const [personaExists, setPersonaExists] = useState(false);
  const [loadingPersonaDetails, setLoadingPersonaDetails] = useState(false);
  
  // Debug: Track modal state changes
  useEffect(() => {
    console.log('[ResearchTest] 🔍 Modal state changed:', showPersonaModal);
  }, [showPersonaModal]);
  
  // Check for research persona and load persona data
  useEffect(() => {
    const loadPersonaPresets = async () => {
      console.log('[ResearchTest] Starting persona check...');
      try {
        const config = await getResearchConfig();
        console.log('[ResearchTest] 📥 Config received:', {
          hasResearchPersona: !!config.research_persona,
          researchPersonaType: typeof config.research_persona,
          researchPersonaKeys: config.research_persona ? Object.keys(config.research_persona) : null,
          hasResearchPersonaFlag: config.persona_defaults?.has_research_persona,
          onboardingCompleted: config.onboarding_completed,
          personaScheduled: config.persona_scheduled,
          personaDefaults: config.persona_defaults
        });
        
        setPersonaData(config.persona_defaults || null);
        
        // CASE 1: Research persona exists in database
        // Check both research_persona object and has_research_persona flag for robustness
        const hasPersonaObject = config.research_persona && typeof config.research_persona === 'object' && Object.keys(config.research_persona).length > 0;
        const hasPersonaFlag = config.persona_defaults?.has_research_persona === true;
        const hasPersona = hasPersonaObject || hasPersonaFlag;
        
        console.log('[ResearchTest] 🔍 Persona check:', {
          hasPersonaObject,
          hasPersonaFlag,
          hasPersona,
          researchPersona: config.research_persona
        });
        
        if (hasPersona && config.research_persona) {
          console.log('[ResearchTest] ✅ CASE 1: Research persona found in database');
          console.log('[ResearchTest] Persona details:', {
            defaultIndustry: config.research_persona.default_industry,
            defaultTargetAudience: config.research_persona.default_target_audience,
            hasRecommendedPresets: !!config.research_persona.recommended_presets,
            presetCount: config.research_persona.recommended_presets?.length || 0
          });
          
          setResearchPersona(config.research_persona);
          setPersonaExists(true);
          
          // Use AI-generated presets if persona exists
          if (config.research_persona.recommended_presets && config.research_persona.recommended_presets.length > 0) {
            console.log('[ResearchTest] Using AI-generated presets from persona');
            // Convert AI presets to display format
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
            setDisplayPresets([...aiPresets, ...samplePresets.slice(0, 2)]);
          } else {
            console.log('[ResearchTest] Persona exists but no recommended presets, using rule-based presets');
            const dynamicPresets = generatePersonaPresets(config.persona_defaults || null);
            setDisplayPresets(dynamicPresets);
          }
        } else {
          // CASE 2 & 3: No research persona found
          console.log('[ResearchTest] ⚠️ CASE 2/3: Research persona NOT found in database');
          console.log('[ResearchTest] Onboarding status:', {
            onboardingCompleted: config.onboarding_completed,
            personaScheduled: config.persona_scheduled
          });
          
          const dynamicPresets = generatePersonaPresets(config.persona_defaults || null);
          setDisplayPresets(dynamicPresets);
          
                     // Show modal when research persona is missing
           // This allows users to generate a research persona even if onboarding isn't completed yet
           // or if the cached persona has expired
           console.log('[ResearchTest] ✅ Research persona missing - SHOWING MODAL');
           console.log('[ResearchTest] Setting showPersonaModal to true');
           setShowPersonaModal(true);
           setPersonaExists(false);

          // Log onboarding and scheduling status for context
          if (config.onboarding_completed) {
            if (config.persona_scheduled) {
              console.log('[ResearchTest] ℹ️ Research persona generation scheduled for 20 minutes from now');
            } else {
              console.log('[ResearchTest] ℹ️ Onboarding completed - user can generate persona now or wait for scheduled generation');
            }
          } else {
            console.log('[ResearchTest] ℹ️ Onboarding not completed yet - user can still generate research persona');
          }
        }
        
        setPersonaChecked(true);
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        console.error('[ResearchTest] ❌ ERROR: Failed to load persona data:', error);
        console.error('[ResearchTest] Error details:', errorMessage);
        
        // Use fallback presets on error
        setDisplayPresets(samplePresets);
        setPersonaChecked(true);
        
        // Don't show modal on error - user can still use default presets
        // Error is already logged to console for debugging
      }
    };
    
    loadPersonaPresets();
  }, []);
  
  // Handle research persona generation
  const handleGeneratePersona = async () => {
    console.log('[ResearchTest] 🔄 User clicked "Generate Persona" - starting generation...');
    try {
      // Force refresh to generate new persona
      console.log('[ResearchTest] Calling refreshResearchPersona with force_refresh=true');
      const persona = await refreshResearchPersona(true);
      console.log('[ResearchTest] ✅ Persona generated successfully:', {
        defaultIndustry: persona.default_industry,
        hasRecommendedPresets: !!persona.recommended_presets
      });
      
      setResearchPersona(persona);
      setPersonaExists(true);
      
      // Reload config to get updated presets
      const config = await getResearchConfig();
      if (config.research_persona?.recommended_presets && config.research_persona.recommended_presets.length > 0) {
        console.log('[ResearchTest] Updating presets with AI-generated presets');
        const aiPresets = config.research_persona.recommended_presets.map((preset: any) => ({
          name: preset.name,
          keywords: typeof preset.keywords === 'string' 
            ? preset.keywords 
            : Array.isArray(preset.keywords) 
              ? preset.keywords.join(', ')
              : 'N/A',
          industry: config.persona_defaults.industry || 'General',
          targetAudience: config.persona_defaults.target_audience || 'General',
          researchMode: preset.config?.mode || 'comprehensive',
          icon: preset.icon || '🔍',
          gradient: preset.gradient || 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          config: preset.config || {}
        }));
        setDisplayPresets([...aiPresets, ...samplePresets.slice(0, 2)]);
      }
      
      console.log('[ResearchTest] ✅ Persona generation complete - closing modal');
      setShowPersonaModal(false);
    } catch (error) {
      console.error('[ResearchTest] ❌ Failed to generate research persona:', error);
      console.error('[ResearchTest] Error details:', error instanceof Error ? error.message : String(error));
      throw error; // Let modal handle the error display
    }
  };
  
  // Handle cancel - user chooses to skip persona generation
  const handleCancelPersona = () => {
    console.log('[ResearchTest] ✅ CASE 3: User cancelled persona generation');
    console.log('[ResearchTest] Continuing with rule-based suggestions');
    setShowPersonaModal(false);
    // Continue with rule-based suggestions (already set as displayPresets)
  };

  const handleComplete = (researchResults: BlogResearchResponse) => {
    setResults(researchResults);
  };

  const handlePresetClick = (preset: typeof samplePresets[0]) => {
    // Pass full research query as single keyword for intelligent parsing
    setPresetKeywords([preset.keywords]);
    setPresetIndustry(preset.industry);
    setPresetTargetAudience(preset.targetAudience);
    setPresetMode(preset.researchMode);
    setPresetConfig(preset.config);
    setResults(null);
  };

  const handleReset = () => {
    setPresetKeywords(undefined);
    setPresetIndustry(undefined);
    setResults(null);
  };

  const handleOpenCompetitorModal = async () => {
    console.log('[handleOpenCompetitorModal] ===== START: Opening competitor analysis modal =====');
    setShowCompetitorModal(true);
    setLoadingCompetitors(true);
    setCompetitorError(null);
    
    try {
      console.log('[handleOpenCompetitorModal] Calling getCompetitorAnalysis()...');
      const data = await getCompetitorAnalysis();
      console.log('[handleOpenCompetitorModal] Received data:', {
        success: data.success,
        competitorsCount: data.competitors?.length || 0,
        error: data.error,
        hasCompetitors: !!data.competitors && data.competitors.length > 0
      });
      
      setCompetitorData(data);
      if (!data.success) {
        const errorMsg = data.error || 'Failed to load competitor data';
        console.error('[handleOpenCompetitorModal] ❌ Failed to load competitor data:', errorMsg);
        setCompetitorError(errorMsg);
      } else {
        console.log('[handleOpenCompetitorModal] ✅ Successfully loaded competitor data');
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to load competitor data';
      console.error('[handleOpenCompetitorModal] ❌ EXCEPTION:', error);
      setCompetitorError(errorMsg);
      setCompetitorData(null);
    } finally {
      setLoadingCompetitors(false);
      console.log('[handleOpenCompetitorModal] ===== END: Opening competitor analysis modal =====');
    }
  };

  const handleOpenPersonaDetails = async () => {
    setShowPersonaDetailsModal(true);
    setLoadingPersonaDetails(true);
    
    try {
      // Fetch fresh persona data
      const config = await getResearchConfig();
      if (config.research_persona) {
        setResearchPersona(config.research_persona);
      }
    } catch (error) {
      console.error('[ResearchTest] Error loading persona details:', error);
    } finally {
      setLoadingPersonaDetails(false);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Animated Background Elements */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '5%',
        width: '400px',
        height: '400px',
        background: 'radial-gradient(circle, rgba(14,165,233,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 20s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '5%',
        width: '300px',
        height: '300px',
        background: 'radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%)',
        borderRadius: '50%',
        filter: 'blur(40px)',
        animation: 'float 15s ease-in-out infinite reverse',
      }} />
      
             <style>{`
         @keyframes float {
           0%, 100% { transform: translate(0, 0); }
           50% { transform: translate(20px, 20px); }
         }
         @keyframes shimmer {
           0% { background-position: -1000px 0; }
           100% { background-position: 1000px 0; }
         }
         @keyframes fadeInUp {
           from {
             opacity: 0;
             transform: translateY(20px);
           }
           to {
             opacity: 1;
             transform: translateY(0);
           }
         }
         @keyframes glow-green {
           0%, 100% { box-shadow: 0 0 20px rgba(34, 197, 94, 0.5), 0 2px 8px rgba(34, 197, 94, 0.3); }
           50% { box-shadow: 0 0 30px rgba(34, 197, 94, 0.8), 0 2px 12px rgba(34, 197, 94, 0.5); }
         }
         @keyframes glow-red {
           0%, 100% { box-shadow: 0 0 20px rgba(239, 68, 68, 0.5), 0 2px 8px rgba(239, 68, 68, 0.3); }
           50% { box-shadow: 0 0 30px rgba(239, 68, 68, 0.8), 0 2px 12px rgba(239, 68, 68, 0.5); }
         }
         @keyframes pulse {
           0%, 100% { opacity: 1; }
           50% { opacity: 0.5; }
         }
         .card-hover {
           transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
         }
         .card-hover:hover {
           transform: translateY(-4px);
           box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
         }
       `}</style>
      {/* Header */}
      <div style={{
        background: 'rgba(255, 255, 255, 0.7)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(14, 165, 233, 0.15)',
        padding: '16px 24px',
        marginBottom: '20px',
        position: 'relative',
        zIndex: 10,
        boxShadow: '0 1px 3px rgba(14, 165, 233, 0.1)',
      }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '24px',
              boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
            }}>
              🔬
            </div>
                          <div style={{ flex: 1 }}>
                <h1 style={{
                  margin: 0,
                  fontSize: '24px',
                  fontWeight: '700',
                  color: '#0c4a6e',
                  letterSpacing: '-0.01em',
                }}>
                  AI-Powered Research Lab
                </h1>
                <p style={{
                  margin: '2px 0 0 0',
                  fontSize: '13px',
                  color: '#0369a1',
                  fontWeight: '400',
                }}>
                  Enterprise-grade research intelligence at your fingertips     
                </p>
              </div>
                             <button
                 onClick={handleOpenCompetitorModal}
                 style={{
                   padding: '10px 20px',
                   backgroundColor: '#0284c7',
                   color: 'white',
                   border: 'none',
                   borderRadius: '8px',
                   cursor: 'pointer',
                   fontSize: '14px',
                   fontWeight: '500',
                   display: 'flex',
                   alignItems: 'center',
                   gap: '8px',
                   boxShadow: '0 2px 8px rgba(2, 132, 199, 0.2)',
                   transition: 'all 0.2s ease',
                 }}
                 onMouseEnter={(e) => {
                   e.currentTarget.style.backgroundColor = '#0369a1';
                   e.currentTarget.style.transform = 'translateY(-1px)';
                   e.currentTarget.style.boxShadow = '0 4px 12px rgba(2, 132, 199, 0.3)';
                 }}
                 onMouseLeave={(e) => {
                   e.currentTarget.style.backgroundColor = '#0284c7';
                   e.currentTarget.style.transform = 'translateY(0)';
                   e.currentTarget.style.boxShadow = '0 2px 8px rgba(2, 132, 199, 0.2)';
                 }}
               >
                 <span>📊</span>
                 <span>View Competitor Analysis</span>
               </button>
               <button
                 onClick={handleOpenPersonaDetails}
                 style={{
                   padding: '10px 20px',
                   backgroundColor: personaExists ? '#22c55e' : '#ef4444',
                   color: 'white',
                   border: 'none',
                   borderRadius: '8px',
                   cursor: 'pointer',
                   fontSize: '14px',
                   fontWeight: '500',
                   display: 'flex',
                   alignItems: 'center',
                   gap: '8px',
                   boxShadow: personaExists 
                     ? '0 0 20px rgba(34, 197, 94, 0.5), 0 2px 8px rgba(34, 197, 94, 0.3)'
                     : '0 0 20px rgba(239, 68, 68, 0.5), 0 2px 8px rgba(239, 68, 68, 0.3)',
                   transition: 'all 0.2s ease',
                   animation: personaExists ? 'glow-green 2s ease-in-out infinite' : 'glow-red 2s ease-in-out infinite',
                 }}
                 onMouseEnter={(e) => {
                   e.currentTarget.style.transform = 'translateY(-1px)';
                   if (personaExists) {
                     e.currentTarget.style.boxShadow = '0 0 30px rgba(34, 197, 94, 0.7), 0 4px 12px rgba(34, 197, 94, 0.4)';
                   } else {
                     e.currentTarget.style.boxShadow = '0 0 30px rgba(239, 68, 68, 0.7), 0 4px 12px rgba(239, 68, 68, 0.4)';
                   }
                 }}
                 onMouseLeave={(e) => {
                   e.currentTarget.style.transform = 'translateY(0)';
                   if (personaExists) {
                     e.currentTarget.style.boxShadow = '0 0 20px rgba(34, 197, 94, 0.5), 0 2px 8px rgba(34, 197, 94, 0.3)';
                   } else {
                     e.currentTarget.style.boxShadow = '0 0 20px rgba(239, 68, 68, 0.5), 0 2px 8px rgba(239, 68, 68, 0.3)';
                   }
                 }}
               >
                 <span style={{
                   width: '8px',
                   height: '8px',
                   borderRadius: '50%',
                   background: 'white',
                   boxShadow: personaExists 
                     ? '0 0 8px rgba(255, 255, 255, 0.8)'
                     : '0 0 8px rgba(255, 255, 255, 0.8)',
                   animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                 }} />
                 <span>{personaExists ? '✓ Research Persona' : '✗ No Persona'}</span>
               </button>
          </div>
          
          {/* Status Badge - Moved to Header */}
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'rgba(34, 197, 94, 0.1)',
            border: '1px solid rgba(34, 197, 94, 0.25)',
            borderRadius: '20px',
            fontSize: '12px',
            color: '#16a34a',
            fontWeight: '600',
          }}>
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#22c55e',
              boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)',
              animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }} />
            System Online • AI Models Ready
          </div>
        </div>
      </div>

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 24px', display: 'flex', gap: '20px', flexWrap: 'wrap', position: 'relative', zIndex: 10 }}>
        {/* Left Panel - Controls */}
        <div style={{ flex: '1 1 280px', minWidth: '280px' }}>
          {/* Presets Card */}
          <div className="card-hover" style={{
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '16px',
            padding: '20px',
            marginBottom: '20px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
            animation: 'fadeInUp 0.6s ease-out',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '36px',
                height: '36px',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
                borderRadius: '10px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '18px',
              }}>
                🎯
              </div>
              <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px' }}>
                Quick Start Presets
                {personaExists && (
                  <Tooltip
                    title={
                      <div style={{ padding: '4px 0' }}>
                        <div style={{ fontWeight: 600, marginBottom: '4px', fontSize: '13px' }}>
                          Personalized Presets
                        </div>
                        <div style={{ fontSize: '12px', lineHeight: '1.5' }}>
                          These presets are customized based on your content types, writing patterns, and website topics from your research persona.
                        </div>
                      </div>
                    }
                    arrow
                    placement="top"
                  >
                    <span style={{ display: 'inline-flex', alignItems: 'center', cursor: 'help', color: '#0ea5e9' }}>
                      <AutoAwesome sx={{ fontSize: 16 }} />
                    </span>
                  </Tooltip>
                )}
              </h3>
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {displayPresets.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => handlePresetClick(preset)}
                  className="card-hover"
                  style={{
                    padding: '14px',
                    background: 'rgba(255, 255, 255, 0.9)',
                    border: '1px solid rgba(14, 165, 233, 0.2)',
                    borderRadius: '12px',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '14px',
                    transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateX(4px)';
                    e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 233, 0.2)';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.4)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateX(0)';
                    e.currentTarget.style.boxShadow = 'none';
                    e.currentTarget.style.borderColor = 'rgba(14, 165, 233, 0.2)';
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                    <span style={{ fontSize: '20px' }}>{preset.icon}</span>
                    <div style={{ fontWeight: '600', color: '#0c4a6e', fontSize: '14px' }}>
                      {preset.name}
                    </div>
                  </div>
                  <div style={{ fontSize: '11px', color: '#64748b', lineHeight: '1.5' }}>
                    {preset.keywords}
                  </div>
                  <div style={{
                    marginTop: '6px',
                    display: 'inline-block',
                    padding: '3px 10px',
                    background: 'rgba(14, 165, 233, 0.1)',
                    borderRadius: '10px',
                    fontSize: '10px',
                    color: '#0369a1',
                    fontWeight: '600',
                  }}>
                    {preset.industry}
                  </div>
                </button>
              ))}
            </div>
            
            <button
              onClick={handleReset}
              style={{
                marginTop: '12px',
                padding: '10px 16px',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                borderRadius: '10px',
                cursor: 'pointer',
                fontSize: '13px',
                width: '100%',
                color: '#dc2626',
                fontWeight: '500',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
                e.currentTarget.style.borderColor = 'rgba(239, 68, 68, 0.25)';
              }}
            >
              ↻ Reset Research
            </button>
          </div>

          {/* Debug Panel */}
          <div className="card-hover" style={{
            background: 'rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(12px)',
            border: '1px solid rgba(14, 165, 233, 0.2)',
            borderRadius: '16px',
            padding: '20px',
            boxShadow: '0 4px 12px rgba(14, 165, 233, 0.08)',
            animation: 'fadeInUp 0.8s ease-out',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #f97316 100%)',
                  borderRadius: '10px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '18px',
                }}>
                  🐛
                </div>
                <h3 style={{ margin: 0, color: '#0c4a6e', fontSize: '18px', fontWeight: '600' }}>
                  Debug Console
                </h3>
              </div>
              <label style={{ 
                cursor: 'pointer', 
                fontSize: '12px',
                color: '#64748b',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}>
                <input
                  type="checkbox"
                  checked={showDebug}
                  onChange={(e) => setShowDebug(e.target.checked)}
                  style={{ 
                    marginRight: '0',
                    width: '14px',
                    height: '14px',
                    cursor: 'pointer',
                  }}
                />
                Show Data
              </label>
            </div>

            {showDebug && (
              <div style={{
                background: 'rgba(15, 23, 42, 0.05)',
                borderRadius: '10px',
                padding: '12px',
                fontSize: '11px',
                fontFamily: "'Fira Code', 'Monaco', monospace",
                maxHeight: '350px',
                overflow: 'auto',
                border: '1px solid rgba(14, 165, 233, 0.1)',
              }}>
                <pre style={{ 
                  margin: 0, 
                  whiteSpace: 'pre-wrap', 
                  wordBreak: 'break-word',
                  color: '#475569',
                  lineHeight: '1.6',
                }}>
                  {JSON.stringify(results, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Main Content - Wizard */}
        <div style={{ flex: '2 1 800px', animation: 'fadeInUp 0.4s ease-out' }}>
          <ResearchWizard
            initialKeywords={presetKeywords}
            initialIndustry={presetIndustry}
            initialTargetAudience={presetTargetAudience}
            initialResearchMode={presetMode}
            initialConfig={presetConfig}
            onComplete={handleComplete}
          />
        </div>
      </div>

      {/* Footer Stats */}
      {results && (
        <div style={{
          background: 'rgba(255, 255, 255, 0.7)',
          backdropFilter: 'blur(12px)',
          borderTop: '1px solid rgba(14, 165, 233, 0.15)',
          padding: '24px',
          marginTop: '32px',
          position: 'relative',
          zIndex: 10,
        }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div style={{
                width: '40px',
                height: '40px',
                background: 'linear-gradient(135deg, #0ea5e9 0%, #38bdf8 100%)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '20px',
                boxShadow: '0 4px 12px rgba(14, 165, 233, 0.25)',
              }}>
                📊
              </div>
              <h3 style={{ 
                margin: 0, 
                color: '#0c4a6e', 
                fontSize: '20px',
                fontWeight: '600',
              }}>
                Research Intelligence Report
              </h3>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Sources Discovered
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.sources.length}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  High-quality references
                </div>
              </div>

              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Content Angles
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.suggested_angles.length}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  Unique perspectives
                </div>
              </div>

              <div className="card-hover" style={{
                background: 'rgba(255, 255, 255, 0.9)',
                padding: '20px',
                borderRadius: '14px',
                border: '1px solid rgba(14, 165, 233, 0.2)',
                boxShadow: '0 2px 8px rgba(14, 165, 233, 0.08)',
              }}>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#0369a1', 
                  fontWeight: '600', 
                  marginBottom: '8px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em',
                }}>
                  Search Queries
                </div>
                <div style={{ 
                  fontSize: '36px', 
                  fontWeight: '700', 
                  color: '#0284c7',
                  lineHeight: '1',
                }}>
                  {results.search_queries?.length || 0}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: '#64748b', 
                  marginTop: '6px',
                }}>
                  Optimized searches
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Research Persona Generation Modal */}
      <ResearchPersonaModal
        open={showPersonaModal}
        onClose={() => {
          console.log('[ResearchTest] Modal onClose called');
          setShowPersonaModal(false);
        }}
        onGenerate={handleGeneratePersona}
        onCancel={handleCancelPersona}
      />

             {/* Competitor Analysis Modal */}
       <OnboardingCompetitorModal
         open={showCompetitorModal}
         onClose={() => setShowCompetitorModal(false)}
         data={competitorData}
         loading={loadingCompetitors}
         error={competitorError}
         onRefresh={(newData) => {
           setCompetitorData(newData);
           setCompetitorError(null);
         }}
       />

       {/* Research Persona Details Modal */}
       {showPersonaDetailsModal && (
         <div
           style={{
             position: 'fixed',
             top: 0,
             left: 0,
             right: 0,
             bottom: 0,
             backgroundColor: 'rgba(0, 0, 0, 0.5)',
             display: 'flex',
             alignItems: 'center',
             justifyContent: 'center',
             zIndex: 9999,
             padding: '20px',
           }}
           onClick={() => setShowPersonaDetailsModal(false)}
         >
           <div
             style={{
               background: 'linear-gradient(135deg, #fff 0%, #f8fafc 100%)',
               borderRadius: '16px',
               padding: '32px',
               maxWidth: '800px',
               width: '100%',
               maxHeight: '90vh',
               overflow: 'auto',
               boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
               position: 'relative',
             }}
             onClick={(e) => e.stopPropagation()}
           >
             <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
               <h2 style={{ margin: 0, fontSize: '24px', fontWeight: '700', color: '#0f172a' }}>
                 Research Persona Details
               </h2>
               <button
                 onClick={() => setShowPersonaDetailsModal(false)}
                 style={{
                   background: 'transparent',
                   border: 'none',
                   fontSize: '24px',
                   cursor: 'pointer',
                   color: '#64748b',
                   padding: '4px 8px',
                 }}
               >
                 ×
               </button>
             </div>

             {loadingPersonaDetails ? (
               <div style={{ textAlign: 'center', padding: '40px' }}>
                 <div style={{ fontSize: '18px', color: '#64748b' }}>Loading persona details...</div>
               </div>
             ) : researchPersona ? (
               <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                 {/* Status Badge */}
                 <div style={{
                   display: 'inline-flex',
                   alignItems: 'center',
                   gap: '8px',
                   padding: '8px 16px',
                   background: 'rgba(34, 197, 94, 0.1)',
                   border: '1px solid rgba(34, 197, 94, 0.25)',
                   borderRadius: '20px',
                   fontSize: '14px',
                   color: '#16a34a',
                   fontWeight: '600',
                   width: 'fit-content',
                 }}>
                   <span style={{
                     width: '8px',
                     height: '8px',
                     borderRadius: '50%',
                     background: '#22c55e',
                     boxShadow: '0 0 8px rgba(34, 197, 94, 0.6)',
                   }} />
                   Persona Active
                 </div>

                 {/* Basic Info */}
                 <div style={{
                   background: 'rgba(255, 255, 255, 0.9)',
                   padding: '20px',
                   borderRadius: '12px',
                   border: '1px solid rgba(14, 165, 233, 0.2)',
                 }}>
                   <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                     Default Settings
                   </h3>
                   <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '12px' }}>
                     <div>
                       <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Industry</div>
                       <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>
                         {researchPersona.default_industry || 'N/A'}
                       </div>
                     </div>
                     <div>
                       <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Target Audience</div>
                       <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>
                         {researchPersona.default_target_audience || 'N/A'}
                       </div>
                     </div>
                     <div>
                       <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Research Mode</div>
                       <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>
                         {researchPersona.default_research_mode || 'N/A'}
                       </div>
                     </div>
                     <div>
                       <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Provider</div>
                       <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a' }}>
                         {researchPersona.default_provider || 'N/A'}
                       </div>
                     </div>
                   </div>
                 </div>

                 {/* Suggested Keywords */}
                 {researchPersona.suggested_keywords && researchPersona.suggested_keywords.length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Suggested Keywords ({researchPersona.suggested_keywords.length})
                     </h3>
                     <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                       {researchPersona.suggested_keywords.map((keyword, idx) => (
                         <span
                           key={idx}
                           style={{
                             padding: '6px 12px',
                             background: 'rgba(14, 165, 233, 0.1)',
                             borderRadius: '16px',
                             fontSize: '14px',
                             color: '#0369a1',
                             fontWeight: '500',
                           }}
                         >
                           {keyword}
                         </span>
                       ))}
                     </div>
                   </div>
                 )}

                 {/* Research Angles */}
                 {researchPersona.research_angles && researchPersona.research_angles.length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Research Angles ({researchPersona.research_angles.length})
                     </h3>
                     <ul style={{ margin: 0, paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                       {researchPersona.research_angles.map((angle, idx) => (
                         <li key={idx} style={{ fontSize: '14px', color: '#475569', lineHeight: '1.6' }}>
                           {angle}
                         </li>
                       ))}
                     </ul>
                   </div>
                 )}

                 {/* Recommended Presets */}
                 {researchPersona.recommended_presets && researchPersona.recommended_presets.length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Recommended Presets ({researchPersona.recommended_presets.length})
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                       {researchPersona.recommended_presets.map((preset, idx) => (
                         <div
                           key={idx}
                           style={{
                             padding: '12px',
                             background: 'rgba(14, 165, 233, 0.05)',
                             borderRadius: '8px',
                             border: '1px solid rgba(14, 165, 233, 0.1)',
                           }}
                         >
                           <div style={{ fontSize: '16px', fontWeight: '600', color: '#0f172a', marginBottom: '4px' }}>
                             {preset.name || `Preset ${idx + 1}`}
                           </div>
                                                       <div style={{ fontSize: '14px', color: '#64748b' }}>
                              {typeof preset.keywords === 'string' 
                                ? preset.keywords 
                                : Array.isArray(preset.keywords) 
                                  ? (preset.keywords as string[]).join(', ')
                                  : 'N/A'}
                            </div>
                         </div>
                       ))}
                     </div>
                   </div>
                 )}

                 {/* Keyword Expansion Patterns */}
                 {researchPersona.keyword_expansion_patterns && Object.keys(researchPersona.keyword_expansion_patterns).length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Keyword Expansion Patterns ({Object.keys(researchPersona.keyword_expansion_patterns).length})
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                       {Object.entries(researchPersona.keyword_expansion_patterns).map(([keyword, expansions], idx) => (
                         <div key={idx} style={{ padding: '12px', background: 'rgba(14, 165, 233, 0.05)', borderRadius: '8px' }}>
                           <div style={{ fontSize: '14px', fontWeight: '600', color: '#0f172a', marginBottom: '6px' }}>
                             {keyword}:
                           </div>
                           <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                             {(expansions as string[]).map((expansion, expIdx) => (
                               <span
                                 key={expIdx}
                                 style={{
                                   padding: '4px 10px',
                                   background: 'rgba(14, 165, 233, 0.1)',
                                   borderRadius: '12px',
                                   fontSize: '12px',
                                   color: '#0369a1',
                                 }}
                               >
                                 {expansion}
                               </span>
                             ))}
                           </div>
                         </div>
                       ))}
                     </div>
                   </div>
                 )}

                 {/* Exa Provider Settings */}
                 {(researchPersona.suggested_exa_domains?.length > 0 || researchPersona.suggested_exa_category || researchPersona.suggested_exa_search_type) && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Exa Provider Settings
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '14px' }}>
                       {researchPersona.suggested_exa_domains && researchPersona.suggested_exa_domains.length > 0 && (
                         <div>
                           <div style={{ color: '#64748b', marginBottom: '6px' }}>Suggested Domains:</div>
                           <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                             {researchPersona.suggested_exa_domains.map((domain, idx) => (
                               <span
                                 key={idx}
                                 style={{
                                   padding: '4px 10px',
                                   background: 'rgba(14, 165, 233, 0.1)',
                                   borderRadius: '12px',
                                   fontSize: '12px',
                                   color: '#0369a1',
                                 }}
                               >
                                 {domain}
                               </span>
                             ))}
                           </div>
                         </div>
                       )}
                       {researchPersona.suggested_exa_category && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Category:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_exa_category}</span>
                         </div>
                       )}
                       {researchPersona.suggested_exa_search_type && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Search Type:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_exa_search_type}</span>
                         </div>
                       )}
                     </div>
                   </div>
                 )}

                 {/* Tavily Provider Settings */}
                 {(researchPersona.suggested_tavily_topic || researchPersona.suggested_tavily_search_depth || researchPersona.suggested_tavily_include_answer || researchPersona.suggested_tavily_time_range || researchPersona.suggested_tavily_raw_content_format) && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Tavily Provider Settings
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '14px' }}>
                       {researchPersona.suggested_tavily_topic && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Topic:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_tavily_topic}</span>
                         </div>
                       )}
                       {researchPersona.suggested_tavily_search_depth && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Search Depth:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_tavily_search_depth}</span>
                         </div>
                       )}
                       {researchPersona.suggested_tavily_include_answer && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Include Answer:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_tavily_include_answer}</span>
                         </div>
                       )}
                       {researchPersona.suggested_tavily_time_range && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Time Range:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_tavily_time_range}</span>
                         </div>
                       )}
                       {researchPersona.suggested_tavily_raw_content_format && (
                         <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b' }}>Raw Content Format:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.suggested_tavily_raw_content_format}</span>
                         </div>
                       )}
                     </div>
                   </div>
                 )}

                 {/* Provider Recommendations */}
                 {researchPersona.provider_recommendations && Object.keys(researchPersona.provider_recommendations).length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Provider Recommendations
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '14px' }}>
                        {Object.entries(researchPersona.provider_recommendations).map(([useCase, provider], idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ color: '#64748b', textTransform: 'capitalize' }}>{useCase.replace('_', ' ')}:</span>
                            <span style={{ color: '#0f172a', fontWeight: '500', textTransform: 'uppercase' }}>{String(provider)}</span>
                          </div>
                        ))}
                     </div>
                   </div>
                 )}

                 {/* Query Enhancement Rules */}
                 {researchPersona.query_enhancement_rules && Object.keys(researchPersona.query_enhancement_rules).length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Query Enhancement Rules ({Object.keys(researchPersona.query_enhancement_rules).length})
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                       {Object.entries(researchPersona.query_enhancement_rules).map(([pattern, template], idx) => (
                         <div key={idx} style={{ padding: '12px', background: 'rgba(14, 165, 233, 0.05)', borderRadius: '8px' }}>
                           <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px', textTransform: 'capitalize' }}>
                             {pattern.replace('_', ' ')}:
                           </div>
                           <div style={{ fontSize: '14px', color: '#0f172a', fontWeight: '500' }}>
                             {template as string}
                           </div>
                         </div>
                       ))}
                     </div>
                   </div>
                 )}

                 {/* Research Preferences */}
                 {researchPersona.research_preferences && Object.keys(researchPersona.research_preferences).length > 0 && (
                   <div style={{
                     background: 'rgba(255, 255, 255, 0.9)',
                     padding: '20px',
                     borderRadius: '12px',
                     border: '1px solid rgba(14, 165, 233, 0.2)',
                   }}>
                     <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                       Research Preferences
                     </h3>
                     <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '14px' }}>
                       {Object.entries(researchPersona.research_preferences).map(([key, value], idx) => (
                         <div key={idx} style={{ display: 'flex', justifyContent: 'space-between' }}>
                           <span style={{ color: '#64748b', textTransform: 'capitalize' }}>{key.replace('_', ' ')}:</span>
                           <span style={{ color: '#0f172a', fontWeight: '500' }}>
                             {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                           </span>
                         </div>
                       ))}
                     </div>
                   </div>
                 )}

                 {/* Metadata */}
                 <div style={{
                   background: 'rgba(255, 255, 255, 0.9)',
                   padding: '20px',
                   borderRadius: '12px',
                   border: '1px solid rgba(14, 165, 233, 0.2)',
                 }}>
                   <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '600', color: '#0f172a' }}>
                     Metadata
                   </h3>
                   <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '14px' }}>
                     {researchPersona.generated_at && (
                       <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                         <span style={{ color: '#64748b' }}>Generated At:</span>
                         <span style={{ color: '#0f172a', fontWeight: '500' }}>
                           {new Date(researchPersona.generated_at).toLocaleString()}
                         </span>
                       </div>
                     )}
                     {researchPersona.confidence_score !== undefined && (
                       <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                         <span style={{ color: '#64748b' }}>Confidence Score:</span>
                         <span style={{ color: '#0f172a', fontWeight: '500' }}>
                           {(researchPersona.confidence_score * 100).toFixed(1)}%
                         </span>
                       </div>
                     )}
                     {researchPersona.version && (
                       <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                         <span style={{ color: '#64748b' }}>Version:</span>
                         <span style={{ color: '#0f172a', fontWeight: '500' }}>{researchPersona.version}</span>
                       </div>
                     )}
                   </div>
                 </div>
               </div>
             ) : (
               <div style={{
                 textAlign: 'center',
                 padding: '40px',
                 background: 'rgba(239, 68, 68, 0.1)',
                 borderRadius: '12px',
                 border: '1px solid rgba(239, 68, 68, 0.2)',
               }}>
                 <div style={{ fontSize: '48px', marginBottom: '16px' }}>⚠️</div>
                 <div style={{ fontSize: '18px', fontWeight: '600', color: '#dc2626', marginBottom: '8px' }}>
                   No Research Persona Found
                 </div>
                 <div style={{ fontSize: '14px', color: '#64748b' }}>
                   Generate a research persona to get personalized research suggestions and presets.
                 </div>
               </div>
             )}
           </div>
         </div>
       )}
     </div>
   );
 };

export default ResearchTest;

