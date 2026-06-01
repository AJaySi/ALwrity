import { useCallback } from 'react';
import { marked } from 'marked';
import { BlogOutlineSection } from '../services/blogWriterApi';

marked.use({
  gfm: true,
  breaks: false,
  pedantic: false,
});

const countWords = (text: string): number =>
  text.split(/\s+/).filter(Boolean).length;

export const useMarkdownProcessor = (
  outline: BlogOutlineSection[],
  sections: Record<string, string>
) => {
  const buildFullMarkdown = useCallback(() => {
    if (!outline.length) return '';
    return outline.map(s => `## ${s.heading}\n\n${sections[s.id] || ''}`).join('\n\n');
  }, [outline, sections]);

  const convertMarkdownToHTML = useCallback((md: string): string => {
    if (!md) return '';
    try {
      const rendered = marked.parse(md);
      const html = typeof rendered === 'string' ? rendered : '';
      return html.replace(/<table>/g, '<div class="table-wrapper"><table>').replace(/<\/table>/g, '</table></div>');
    } catch {
      return `<p style="color:#991b1b;">Could not render this section. Unexpected markdown syntax encountered.</p>`;
    }
  }, []);

  const getTotalWords = useCallback(() => countWords(buildFullMarkdown()), [buildFullMarkdown]);

  const getSectionWordCount = useCallback((sectionId: string) => countWords(sections[sectionId] || ''), [sections]);

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
