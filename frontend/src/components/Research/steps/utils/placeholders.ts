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
      "AI diagnostic tools: accuracy rates and clinical implementation",
      "Telemedicine adoption statistics and patient satisfaction outcomes",
      "Personalized medicine: genomic testing costs and benefits",
      "Healthcare automation: workflow optimization case studies",
      "Compare telehealth platforms: features, pricing, and ROI",
      "Future of healthcare AI: predictions for 2025-2026"
    ],
    Technology: [
      "Latest AI advancements in multimodal content generation 2026",
      "Compare cloud providers: AWS vs Azure vs GCP pricing and features",
      "Edge computing deployment strategies and IoT best practices",
      "Quantum computing breakthroughs and real-world applications",
      "How to implement AI automation in small businesses",
      "Future of AI: predictions and emerging opportunities 2025-2030"
    ],
    Finance: [
      "DeFi regulations: compliance strategies and risk management",
      "Digital banking: customer retention tactics and ROI",
      "ESG investing trends: performance metrics and market analysis",
      "Fintech innovations: comparison of top payment platforms",
      "Cryptocurrency adoption: statistics and future outlook 2025",
      "How to choose the right financial software for small businesses"
    ],
    Marketing: [
      "AI marketing automation tools: comparison and ROI analysis",
      "Influencer marketing ROI: statistics and best practices 2025",
      "Privacy-first marketing strategies in cookieless world",
      "Content marketing trends: what works in 2025",
      "How to measure marketing attribution and conversion rates",
      "Social media marketing: platform comparison and audience insights"
    ],
    Business: [
      "Remote work policies: best practices and productivity metrics",
      "Supply chain resilience: diversification strategies and case studies",
      "Sustainability initiatives: ESG programs and ROI analysis",
      "Business automation: tools comparison and implementation guides",
      "How to scale a startup: funding strategies and growth tactics",
      "Customer retention: strategies that work in 2025"
    ],
    Education: [
      "EdTech tools: comparison of top learning platforms",
      "Microlearning: effectiveness statistics and best practices",
      "AI tutoring systems: student outcomes and implementation",
      "Online learning platforms: ROI and engagement metrics",
      "How to create effective online courses: step-by-step guide",
      "Future of education: predictions and emerging technologies"
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

  // Default placeholders - diverse, actionable examples that inspire research
  return industryExamples[industry] || [
    "What are the latest trends in [your industry] for 2025-2026?",
    "Compare top solutions: [solution A] vs [solution B]",
    "Best practices and real-world case studies",
    "Expert insights and statistics on [topic]",
    "How to [achieve goal] - step-by-step guide",
    "Future predictions and emerging opportunities"
  ];
};

