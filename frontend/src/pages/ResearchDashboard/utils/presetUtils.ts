import { PersonaDefaults } from '../../../api/researchConfig';
import { ResearchPreset } from '../types';
import { SAMPLE_PRESETS } from '../constants';

/**
 * Generate persona-specific presets dynamically based on user's persona data
 */
export const generatePersonaPresets = (persona: PersonaDefaults | null): ResearchPreset[] => {
  if (!persona || !persona.industry || persona.industry === 'General') {
    return SAMPLE_PRESETS;
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
  
  const generatedPresets: ResearchPreset[] = [
    {
      name: `${industry} Trends`,
      keywords: `Research latest trends and innovations in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'comprehensive',
      icon: '📊',
      gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      config: baseConfig1,
    },
    {
      name: `${audience} Insights`,
      keywords: `Analyze ${audience} pain points and preferences in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'targeted',
      icon: '🎯',
      gradient: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      config: baseConfig2,
    },
    {
      name: `${industry} Best Practices`,
      keywords: `Investigate best practices and success stories in ${industry}`,
      industry,
      targetAudience: audience,
      researchMode: 'comprehensive',
      icon: '⭐',
      gradient: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      config: baseConfig3,
    }
  ];
  
  return [...generatedPresets, ...SAMPLE_PRESETS.slice(0, 2)];
};
