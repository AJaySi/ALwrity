/**
 * Alternative Research Angles Utility
 * Generates related research angles based on user query intent using rule-based patterns
 */

// Pattern-based angle generation templates
const anglePatterns: Record<string, string[]> = {
  tools: [
    'Compare {topic}',
    '{topic} ROI analysis',
    'Best {topic} for {industry}',
    '{topic} implementation guide',
    'Top {topic} features and pricing',
  ],
  trends: [
    'Latest {topic} trends',
    '{topic} market analysis',
    '{topic} future predictions',
    '{topic} adoption rates',
    'Emerging {topic} technologies',
  ],
  strategies: [
    '{topic} implementation guide',
    '{topic} best practices',
    '{topic} case studies',
    '{topic} success strategies',
    '{topic} optimization techniques',
  ],
  analysis: [
    '{topic} competitive analysis',
    '{topic} market share',
    '{topic} industry leaders',
    '{topic} SWOT analysis',
    '{topic} benchmarking',
  ],
  guides: [
    '{topic} getting started guide',
    '{topic} for beginners',
    '{topic} step-by-step tutorial',
    '{topic} troubleshooting',
    '{topic} expert tips',
  ],
  comparison: [
    '{topic} vs alternatives',
    'Best {topic} comparison',
    '{topic} feature comparison',
    '{topic} pricing comparison',
    '{topic} pros and cons',
  ],
  general: [
    'What is {topic}',
    'How {topic} works',
    '{topic} benefits and challenges',
    '{topic} industry insights',
    '{topic} expert opinions',
  ],
};

// Keywords that indicate query intent
const intentKeywords: Record<string, string[]> = {
  tools: ['tools', 'software', 'platform', 'system', 'solution', 'app', 'application', 'toolkit', 'suite'],
  trends: ['trends', 'future', 'emerging', 'latest', 'new', 'innovation', 'development', 'growth'],
  strategies: ['strategy', 'plan', 'approach', 'method', 'best practices', 'how to', 'guide', 'implementation'],
  analysis: ['analysis', 'compare', 'review', 'evaluate', 'assessment', 'study', 'research'],
  guides: ['guide', 'tutorial', 'how to', 'getting started', 'learn', 'tips', 'advice'],
  comparison: ['vs', 'versus', 'compare', 'comparison', 'alternative', 'difference'],
};

/**
 * Detects the primary intent of a query
 */
function detectQueryIntent(query: string): string {
  const queryLower = query.toLowerCase();
  
  // Check each intent category
  for (const [intent, keywords] of Object.entries(intentKeywords)) {
    if (keywords.some(keyword => queryLower.includes(keyword))) {
      return intent;
    }
  }
  
  return 'general';
}

/**
 * Extracts the main topic from a query
 */
function extractTopic(query: string, industry: string): string {
  // Remove common intent words to get the core topic
  const intentWords = Object.values(intentKeywords).flat();
  let topic = query.toLowerCase();
  
  // Remove intent keywords
  for (const word of intentWords) {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    topic = topic.replace(regex, '').trim();
  }
  
  // Clean up extra whitespace and common stop words
  topic = topic
    .replace(/\s+/g, ' ')
    .replace(/\b(a|an|the|in|on|at|for|with|to|of|and|or|but)\b/g, '')
    .trim();
  
  // If topic is too short or empty, use original query
  if (topic.length < 3 || topic.split(' ').length === 0) {
    topic = query.toLowerCase();
  }
  
  // Capitalize first letter
  return topic.charAt(0).toUpperCase() + topic.slice(1);
}

/**
 * Generates alternative research angles based on user query
 * @param query - User's research query/keywords
 * @param industry - Selected industry (optional)
 * @returns Array of alternative research angle suggestions
 */
export function generateResearchAngles(query: string, industry: string = 'General'): string[] {
  if (!query || query.trim().length === 0) {
    return [];
  }

  // Detect primary intent
  const intent = detectQueryIntent(query);
  
  // Extract main topic
  const topic = extractTopic(query, industry);
  
  // Get patterns for detected intent (fallback to general)
  const patterns = anglePatterns[intent] || anglePatterns.general;
  
  // Generate angles using patterns
  const angles: string[] = [];
  
  for (const pattern of patterns.slice(0, 5)) { // Limit to 5 angles
    let angle = pattern.replace('{topic}', topic);
    
    // Replace industry placeholder if present
    if (industry && industry !== 'General') {
      angle = angle.replace('{industry}', industry);
    } else {
      // Remove industry-specific placeholder if no industry
      angle = angle.replace(' for {industry}', '');
    }
    
    // Capitalize first letter
    angle = angle.charAt(0).toUpperCase() + angle.slice(1);
    
    // Skip if angle is too similar to original query
    const angleLower = angle.toLowerCase();
    const queryLower = query.toLowerCase();
    
    if (angleLower !== queryLower && !queryLower.includes(angleLower) && !angleLower.includes(queryLower)) {
      angles.push(angle);
    }
  }
  
  // Add industry-specific angle if industry is set
  if (industry && industry !== 'General' && angles.length < 5) {
    const industryAngle = `${topic} in ${industry} industry`;
    if (!angles.some(a => a.toLowerCase() === industryAngle.toLowerCase())) {
      angles.push(industryAngle);
    }
  }
  
  // If we have fewer than 3 angles, add some general ones
  if (angles.length < 3) {
    const generalPatterns = anglePatterns.general.slice(0, 3 - angles.length);
    for (const pattern of generalPatterns) {
      const angle = pattern.replace('{topic}', topic);
      if (!angles.some(a => a.toLowerCase() === angle.toLowerCase())) {
        angles.push(angle);
      }
    }
  }
  
  // Remove duplicates and limit to 5
  const uniqueAngles = Array.from(new Set(angles.map(a => a.toLowerCase())))
    .slice(0, 5)
    .map(a => a.charAt(0).toUpperCase() + a.slice(1));
  
  return uniqueAngles;
}

/**
 * Formats an angle for display
 */
export function formatAngle(angle: string): string {
  if (!angle) return angle;
  return angle.charAt(0).toUpperCase() + angle.slice(1);
}
