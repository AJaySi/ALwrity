/**
 * Intelligent input parser - handles sentences, keywords, URLs
 */
export const parseIntelligentInput = (value: string): string[] => {
  // If empty, return empty array
  if (!value.trim()) return [];
  
  // Detect if input contains URLs
  const urlPattern = /(https?:\/\/[^\s,]+)/g;
  const urls = value.match(urlPattern) || [];
  
  // Check if input looks like a sentence/paragraph (contains multiple words without commas)
  const hasCommas = value.includes(',');
  const wordCount = value.trim().split(/\s+/).length;
  
  if (urls.length > 0) {
    // User provided URLs - extract them as separate keywords
    const textWithoutUrls = value.replace(urlPattern, '').trim();
    const textKeywords = textWithoutUrls ? [textWithoutUrls] : [];
    return [...urls, ...textKeywords];
  } else if (!hasCommas && wordCount > 5) {
    // Looks like a sentence/paragraph - treat entire input as single research topic
    return [value.trim()];
  } else if (hasCommas) {
    // Traditional comma-separated keywords
    return value.split(',').map(k => k.trim()).filter(Boolean);
  } else {
    // Short phrase or single keyword
    return [value.trim()];
  }
};

