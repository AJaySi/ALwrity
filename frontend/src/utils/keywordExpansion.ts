/**
 * Smart Keyword Expansion Utility
 * Expands user keywords with industry-specific related terms using rule-based logic
 */

// Industry-specific keyword expansion maps
// Format: { industry: { keyword: [expansions] } }
const industryKeywordExpansions: Record<string, Record<string, string[]>> = {
  Healthcare: {
    'AI': ['medical AI', 'healthcare AI', 'clinical AI', 'diagnostic AI', 'healthcare automation'],
    'tools': ['medical devices', 'clinical tools', 'diagnostic systems', 'healthcare software'],
    'automation': ['healthcare automation', 'clinical automation', 'patient care automation', 'medical workflow automation'],
    'technology': ['healthtech', 'medical technology', 'clinical technology', 'digital health'],
    'data': ['health data', 'medical records', 'patient data', 'clinical data', 'healthcare analytics'],
    'research': ['medical research', 'clinical research', 'biomedical research', 'healthcare studies'],
    'management': ['patient management', 'care coordination', 'healthcare administration'],
  },
  Technology: {
    'AI': ['machine learning', 'deep learning', 'neural networks', 'artificial intelligence applications'],
    'cloud': ['AWS', 'Azure', 'GCP', 'cloud infrastructure', 'cloud computing'],
    'security': ['cybersecurity', 'data protection', 'privacy compliance', 'information security'],
    'automation': ['IT automation', 'devops automation', 'software automation', 'process automation'],
    'development': ['software development', 'web development', 'mobile development', 'app development'],
    'tools': ['development tools', 'software tools', 'developer tools', 'tech stack'],
    'platform': ['SaaS platform', 'cloud platform', 'development platform', 'tech platform'],
  },
  Finance: {
    'fintech': ['financial technology', 'digital banking', 'payment solutions', 'financial services tech'],
    'investing': ['investment strategies', 'portfolio management', 'trading platforms', 'wealth management'],
    'cryptocurrency': ['blockchain', 'digital assets', 'DeFi', 'crypto trading'],
    'banking': ['digital banking', 'online banking', 'mobile banking', 'banking technology'],
    'payment': ['payment processing', 'payment gateways', 'digital payments', 'payment solutions'],
    'analysis': ['financial analysis', 'market analysis', 'risk analysis', 'investment analysis'],
    'compliance': ['financial compliance', 'regulatory compliance', 'fintech regulations'],
  },
  Marketing: {
    'SEO': ['search engine optimization', 'SEO strategy', 'SEO tools', 'keyword research'],
    'content': ['content marketing', 'content strategy', 'content creation', 'content distribution'],
    'social media': ['social media marketing', 'social media strategy', 'social media advertising'],
    'advertising': ['digital advertising', 'online advertising', 'PPC', 'display advertising'],
    'analytics': ['marketing analytics', 'web analytics', 'campaign analytics', 'performance metrics'],
    'automation': ['marketing automation', 'email marketing', 'lead generation', 'CRM'],
    'strategy': ['marketing strategy', 'brand strategy', 'digital strategy', 'growth strategy'],
  },
  Business: {
    'management': ['business management', 'operations management', 'strategic management'],
    'strategy': ['business strategy', 'growth strategy', 'competitive strategy', 'market strategy'],
    'startup': ['startup funding', 'venture capital', 'startup ecosystem', 'entrepreneurship'],
    'operations': ['business operations', 'process optimization', 'operational efficiency'],
    'leadership': ['business leadership', 'executive leadership', 'management leadership'],
    'innovation': ['business innovation', 'digital transformation', 'business disruption'],
    'analytics': ['business analytics', 'data analytics', 'business intelligence', 'KPIs'],
  },
  Education: {
    'e-learning': ['online learning', 'distance education', 'digital learning', 'virtual classrooms'],
    'edtech': ['education technology', 'learning management systems', 'educational software'],
    'teaching': ['teaching methods', 'pedagogy', 'instructional design', 'curriculum development'],
    'student': ['student engagement', 'student success', 'student analytics', 'learning outcomes'],
    'training': ['professional training', 'skills development', 'corporate training', 'certification'],
    'assessment': ['educational assessment', 'learning assessment', 'student evaluation'],
  },
  Real_Estate: {
    'property': ['real estate', 'real estate market', 'property investment', 'property management'],
    'technology': ['proptech', 'real estate technology', 'property tech', 'real estate software'],
    'investment': ['real estate investment', 'property investment', 'real estate portfolio'],
    'market': ['housing market', 'real estate trends', 'market analysis', 'property values'],
    'management': ['property management', 'facility management', 'real estate operations'],
  },
  Travel: {
    'tourism': ['travel industry', 'hospitality', 'travel trends', 'tourism technology'],
    'booking': ['travel booking', 'online booking', 'travel platforms', 'reservation systems'],
    'technology': ['travel tech', 'travel technology', 'tourism tech', 'hospitality technology'],
    'experience': ['travel experience', 'customer experience', 'tourism experiences'],
  },
  Science: {
    'research': ['scientific research', 'academic research', 'research methods', 'research publications'],
    'technology': ['scientific technology', 'laboratory technology', 'research tools'],
    'data': ['scientific data', 'research data', 'experimental data', 'data analysis'],
    'innovation': ['scientific innovation', 'research innovation', 'scientific breakthroughs'],
  },
  Legal: {
    'technology': ['legal tech', 'legal technology', 'law tech', 'legal software'],
    'compliance': ['legal compliance', 'regulatory compliance', 'legal requirements'],
    'automation': ['legal automation', 'document automation', 'legal process automation'],
    'research': ['legal research', 'case research', 'legal analysis'],
  },
  Manufacturing: {
    'automation': ['manufacturing automation', 'industrial automation', 'factory automation', 'production automation'],
    'technology': ['industrial technology', 'manufacturing tech', 'Industry 4.0', 'smart manufacturing'],
    'quality': ['quality control', 'quality assurance', 'quality management', 'quality standards'],
    'efficiency': ['manufacturing efficiency', 'production efficiency', 'operational efficiency'],
  },
  Retail: {
    'e-commerce': ['online retail', 'digital commerce', 'ecommerce platform', 'online shopping'],
    'technology': ['retail tech', 'retail technology', 'retail innovation', 'retail software'],
    'customer': ['customer experience', 'customer engagement', 'customer service', 'customer analytics'],
    'inventory': ['inventory management', 'stock management', 'supply chain', 'warehouse management'],
  },
  Energy: {
    'renewable': ['solar energy', 'wind energy', 'renewable technology', 'clean energy'],
    'technology': ['energy technology', 'energy innovation', 'energy management systems'],
    'efficiency': ['energy efficiency', 'energy optimization', 'energy conservation'],
  },
  Agriculture: {
    'technology': ['agtech', 'agricultural technology', 'farm technology', 'precision agriculture'],
    'automation': ['farm automation', 'agricultural automation', 'precision farming'],
    'sustainability': ['sustainable farming', 'organic farming', 'agricultural sustainability'],
  },
};

/**
 * Expands keywords based on industry context
 * @param keywords - Array of user-entered keywords
 * @param industry - Selected industry (or 'General')
 * @returns Array of expanded keywords (originals + suggestions)
 */
export function expandKeywords(keywords: string[], industry: string): {
  original: string[];
  expanded: string[];
  suggestions: string[];
} {
  if (!keywords || keywords.length === 0) {
    return { original: [], expanded: [], suggestions: [] };
  }

  // Normalize industry name (handle spaces and case)
  const normalizedIndustry = industry.replace(/\s+/g, '_');

  // Get expansion map for this industry, or empty object if not found
  const expansionMap = industryKeywordExpansions[normalizedIndustry] || {};

  const originalKeywords = [...keywords];
  const suggestions: string[] = [];
  const expandedSet = new Set<string>();

  // Add original keywords to expanded set
  originalKeywords.forEach(k => expandedSet.add(k.toLowerCase().trim()));

  // For each keyword, find expansions
  originalKeywords.forEach(keyword => {
    const keywordLower = keyword.toLowerCase().trim();

    // Direct match in expansion map
    if (expansionMap[keywordLower]) {
      expansionMap[keywordLower].forEach(expansion => {
        if (!expandedSet.has(expansion.toLowerCase())) {
          suggestions.push(expansion);
          expandedSet.add(expansion.toLowerCase());
        }
      });
    }

    // Partial match: check if keyword contains any expansion key
    Object.keys(expansionMap).forEach(expansionKey => {
      if (keywordLower.includes(expansionKey) || expansionKey.includes(keywordLower)) {
        expansionMap[expansionKey].forEach(expansion => {
          if (!expandedSet.has(expansion.toLowerCase())) {
            suggestions.push(expansion);
            expandedSet.add(expansion.toLowerCase());
          }
        });
      }
    });
  });

  // Return structure
  return {
    original: originalKeywords,
    expanded: Array.from(expandedSet).map(k => {
      // Preserve original casing if it exists in originals
      const originalMatch = originalKeywords.find(ok => ok.toLowerCase() === k);
      return originalMatch || k;
    }),
    suggestions: suggestions.slice(0, 8), // Limit to 8 suggestions to avoid overwhelming UI
  };
}

/**
 * Formats keyword for display (capitalize first letter)
 */
export function formatKeyword(keyword: string): string {
  if (!keyword) return keyword;
  return keyword.charAt(0).toUpperCase() + keyword.slice(1);
}

/**
 * Checks if a keyword is an original (user-entered) or a suggestion
 */
export function isOriginalKeyword(keyword: string, originalKeywords: string[]): boolean {
  return originalKeywords.some(ok => ok.toLowerCase() === keyword.toLowerCase());
}
