import { useCallback } from 'react';
import { BlogOutlineSection } from '../services/blogWriterApi';

export const useMarkdownProcessor = (
  outline: BlogOutlineSection[],
  sections: Record<string, string>
) => {
  const buildFullMarkdown = useCallback(() => {
    if (!outline.length) return '';
    return outline.map(s => `## ${s.heading}\n\n${sections[s.id] || ''}`).join('\n\n');
  }, [outline, sections]);

  const convertMarkdownToHTML = useCallback((md: string) => {
    return md
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
      .replace(/\*(.*)\*/gim, '<em>$1</em>')
      .replace(/\n\n/g, '<br/><br/>');
  }, []);

  const getTotalWords = useCallback(() => {
    const fullMarkdown = buildFullMarkdown();
    return fullMarkdown.split(/\s+/).filter(word => word.length > 0).length;
  }, [buildFullMarkdown]);

  const getSectionWordCount = useCallback((sectionId: string) => {
    const content = sections[sectionId] || '';
    return content.split(/\s+/).filter(word => word.length > 0).length;
  }, [sections]);

  const getOutlineStats = useCallback(() => {
    const totalWords = getTotalWords();
    const totalSections = outline.length;
    const totalSubheadings = outline.reduce((sum, section) => sum + section.subheadings.length, 0);
    const totalKeyPoints = outline.reduce((sum, section) => sum + section.key_points.length, 0);
    
    return {
      totalWords,
      totalSections,
      totalSubheadings,
      totalKeyPoints,
      averageWordsPerSection: totalSections > 0 ? Math.round(totalWords / totalSections) : 0
    };
  }, [outline, getTotalWords]);

  return {
    buildFullMarkdown,
    convertMarkdownToHTML,
    getTotalWords,
    getSectionWordCount,
    getOutlineStats
  };
};
