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
    if (!md) return '';
    
    let html = md;
    
    // Headings (must be first, before other replacements)
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');
    
    // Bold and Italic
    html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
    
    // Links [text](url) - handle both http and data:image URLs
    html = html.replace(/\[(.+?)\]\((.+?)\)/g, (match, text, url) => {
      const safeUrl = url.replace(/"/g, '&quot;');
      if (url.startsWith('data:image') || url.startsWith('http')) {
        return `<img src="${safeUrl}" alt="${text}" style="max-width:100%;height:auto;border-radius:8px;margin:1rem 0;" />`;
      }
      return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer" style="color:#4f46e5;text-decoration:underline;">${text}</a>`;
    });
    
    // Images ![alt](url) - explicit image syntax
    html = html.replace(/!\[(.+?)\]\((.+?)\)/g, '<img src="$2" alt="$1" style="max-width:100%;height:auto;border-radius:8px;margin:1rem 0;" />');
    
    // Blockquotes
    html = html.replace(/^> (.+)$/gm, '<blockquote style="border-left:4px solid #e5e7eb;margin:1rem 0;padding:0.5rem 1rem;background:#f9fafb;color:#6b7280;font-style:italic;">$1</blockquote>');
    
    // Inline code
    html = html.replace(/`(.+?)`/g, '<code style="background:#f1f5f9;padding:2px 6px;border-radius:4px;font-family:monospace;font-size:0.9em;color:#dc2626;">$1</code>');
    
    // Horizontal rules
    html = html.replace(/^-{3,}$/gm, '<hr style="border:none;border-top:1px solid #e5e7eb;margin:1.5rem 0;" />');
    
    // Unordered lists (- item or * item)
    html = html.replace(/^[-*] (.+)$/gm, '<li style="margin-bottom:0.5rem;">$1</li>');
    // Wrap consecutive <li> tags in <ul>
    html = html.replace(/(<li style="margin-bottom:0.5rem;">.+<\/li>\n?)+/g, (match) => {
      return `<ul style="padding-left:1.5rem;margin:1rem 0;list-style-type:disc;">${match}</ul>`;
    });
    
    // Ordered lists (1. item, 2. item, etc.)
    html = html.replace(/^\d+\. (.+)$/gm, '<li style="margin-bottom:0.5rem;">$1</li>');
    // Wrap consecutive <li> tags in <ol> (simplified - assumes ordered lists come after unordered processing)
    
    // Paragraphs (double newlines)
    html = html.replace(/\n\n/g, '</p><p>');
    html = `<p>${html}</p>`;
    
    // Clean up empty paragraphs
    html = html.replace(/<p><\/p>/g, '');
    html = html.replace(/<p>(<h[1-3]>)/g, '$1');
    html = html.replace(/(<\/h[1-3]>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ul>)/g, '$1');
    html = html.replace(/(<\/ul>)<\/p>/g, '$1');
    html = html.replace(/<p>(<ol>)/g, '$1');
    html = html.replace(/(<\/ol>)<\/p>/g, '$1');
    html = html.replace(/<p>(<blockquote>)/g, '$1');
    html = html.replace(/(<\/blockquote>)<\/p>/g, '$1');
    html = html.replace(/<p>(<hr)/g, '$1');
    html = html.replace(/(<img[^>]*\/>)<\/p>/g, '$1');
    html = html.replace(/<p>(<img)/g, '$1');
    
    return html;
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
