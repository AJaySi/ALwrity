/**
 * Hook for keyword expansion with persona support
 */

import { useState, useEffect } from 'react';
import { expandKeywords, expandKeywordsWithPersona } from '../../../../utils/keywordExpansion';

interface ResearchPersona {
  keyword_expansion_patterns?: Record<string, string[]>;
  suggested_keywords?: string[];
}

interface KeywordExpansion {
  original: string[];
  expanded: string[];
  suggestions: string[];
}

export const useKeywordExpansion = (
  keywords: string[],
  industry: string,
  researchPersona: ResearchPersona | null
): KeywordExpansion | null => {
  const [keywordExpansion, setKeywordExpansion] = useState<KeywordExpansion | null>(null);

  useEffect(() => {
    if (keywords.length > 0) {
      let expansion;
      
      // If we have research persona with keyword expansion patterns, use them
      if (researchPersona?.keyword_expansion_patterns && Object.keys(researchPersona.keyword_expansion_patterns).length > 0) {
        expansion = expandKeywordsWithPersona(
          keywords,
          researchPersona.keyword_expansion_patterns,
          researchPersona.suggested_keywords
        );
      } else if (industry !== 'General') {
        // Fallback to industry-based expansion
        expansion = expandKeywords(keywords, industry);
      } else {
        expansion = { original: keywords, expanded: keywords, suggestions: [] };
      }
      
      setKeywordExpansion(expansion);
    } else {
      setKeywordExpansion(null);
    }
  }, [keywords, industry, researchPersona]);

  return keywordExpansion;
};
