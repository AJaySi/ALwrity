// Utility functions for research component

export const formatKeywords = (keywords: string[]): string => {
  return keywords.join(', ');
};

export const parseKeywords = (keywordsString: string): string[] => {
  return keywordsString
    .split(',')
    .map(k => k.trim())
    .filter(Boolean);
};

export const validateKeywords = (keywords: string[]): boolean => {
  return keywords.length > 0 && keywords.every(k => k.trim().length > 0);
};

