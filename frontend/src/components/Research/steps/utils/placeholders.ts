/**
 * Industry-specific placeholder examples for personalized experience
 * Enhanced to use research persona data (research_angles and recommended_presets)
 */
export interface PersonaPlaceholderData {
  research_angles?: string[];
  recommended_presets?: Array<{
    name: string;
    keywords: string | string[];
    description?: string;
  }>;
  industry?: string;
  target_audience?: string;
}

export const getIndustryPlaceholders = (
  industry: string,
  personaData?: PersonaPlaceholderData
): string[] => {
  // If we have research persona data, use it to generate personalized placeholders
  if (personaData) {
    const personalizedPlaceholders: string[] = [];
    
    // Priority 1: Use recommended presets (most actionable)
    if (personaData.recommended_presets && personaData.recommended_presets.length > 0) {
      const presets = personaData.recommended_presets.slice(0, 4); // Use first 4 presets
      presets.forEach((preset) => {
        const keywords = typeof preset.keywords === 'string' 
          ? preset.keywords 
          : Array.isArray(preset.keywords) 
            ? preset.keywords.join(', ')
            : '';
        
        if (keywords && keywords.trim().length > 0) {
          // Make placeholders concise and actionable
          personalizedPlaceholders.push(keywords.trim());
        }
      });
    }
    
    // Priority 2: Use research angles (formatted as actionable queries)
    if (personaData.research_angles && personaData.research_angles.length > 0 && personalizedPlaceholders.length < 4) {
      const angles = personaData.research_angles.slice(0, 4 - personalizedPlaceholders.length);
      angles.forEach((angle) => {
        // Format angle as a concise research query
        let placeholder = angle;
        
        // Replace topic placeholders with industry if available
        if (placeholder.includes('{topic}') || placeholder.includes('{{topic}}')) {
          placeholder = placeholder.replace(/\{topic\}/g, industry || 'your topic')
                                   .replace(/\{\{topic\}\}/g, industry || 'your topic');
        }
        
        // Make it concise - remove "Research:" prefix if present, keep it natural
        placeholder = placeholder.replace(/^Research:\s*/i, '').trim();
        
        if (placeholder && placeholder.length > 10) { // Only add meaningful angles
          personalizedPlaceholders.push(placeholder);
        }
      });
    }
    
    // If we have personalized placeholders, return them (with fallback to industry defaults)
    if (personalizedPlaceholders.length > 0) {
      // Add 1-2 industry-specific ones as backup for variety
      const industryDefaults = getIndustryDefaults(industry);
      const needed = Math.max(0, 5 - personalizedPlaceholders.length);
      return [...personalizedPlaceholders, ...industryDefaults.slice(0, needed)];
    }
  }
  
  // Fallback to industry-specific defaults
  return getIndustryDefaults(industry);
};

/**
 * Get industry-specific default placeholders (original logic)
 */
const getIndustryDefaults = (industry: string): string[] => {
  const industryExamples: Record<string, string[]> = {
    Healthcare: [
      "AI diagnostic tools and clinical applications",
      "Telemedicine adoption and patient outcomes",
      "Personalized medicine and genomic testing",
      "Healthcare automation and workflow optimization"
    ],
    Technology: [
      "Edge computing and IoT deployment strategies",
      "Cloud provider comparison and cost optimization",
      "Quantum computing breakthroughs and applications",
      "AI and machine learning industry trends"
    ],
    Finance: [
      "DeFi regulations and compliance strategies",
      "Digital banking and customer retention",
      "ESG investing trends and performance",
      "Fintech innovations and market analysis"
    ],
    Marketing: [
      "AI marketing automation and personalization",
      "Influencer marketing ROI and best practices",
      "Privacy-first marketing in cookieless world",
      "Content marketing strategies and trends"
    ],
    Business: [
      "Remote work policies and hybrid models",
      "Supply chain resilience and diversification",
      "Sustainability initiatives and ESG programs",
      "Business automation and efficiency"
    ],
    Education: [
      "EdTech tools and personalized learning",
      "Microlearning and skill-based education",
      "AI tutoring systems and student support",
      "Online learning platforms and outcomes"
    ],
    'Real Estate': [
      "PropTech innovations and property management",
      "Virtual staging and 3D property tours",
      "Real estate tokenization and fractional ownership",
      "Smart building technologies and IoT"
    ],
    Travel: [
      "Sustainable tourism and eco-travel trends",
      "AI travel personalization and recommendations",
      "Bleisure travel and workation destinations",
      "Travel technology and booking platforms"
    ]
  };

  // Default placeholders - concise and actionable
  return industryExamples[industry] || [
    "Latest AI trends and innovations",
    "Best practices and case studies",
    "Market analysis and competitor insights",
    "Emerging technologies and future predictions"
  ];
};

