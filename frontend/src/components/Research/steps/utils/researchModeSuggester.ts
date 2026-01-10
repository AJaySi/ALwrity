import { ResearchMode } from '../../../../services/researchApi';

/**
 * Smart mode suggestion based on query complexity
 */
export const suggestResearchMode = (keywords: string[]): ResearchMode => {
  if (keywords.length === 0) return 'basic';
  
  const totalText = keywords.join(' ');
  const totalWords = totalText.split(/\s+/).length;
  const hasURL = keywords.some(k => k.startsWith('http'));
  
  // URL detected → comprehensive research
  if (hasURL) return 'comprehensive';
  
  // Long detailed query → comprehensive
  if (totalWords > 20) return 'comprehensive';
  
  // Medium complexity → targeted
  if (totalWords > 10 || keywords.length > 3) return 'targeted';
  
  // Simple query → basic
  return 'basic';
};

