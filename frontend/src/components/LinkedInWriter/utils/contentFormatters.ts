// Content formatting utilities for LinkedIn Writer

// Escape HTML characters to prevent XSS
export function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// Format draft content with proper LinkedIn styling and inline citations
export function formatDraftContent(content: string, citations?: any[], researchSources?: any[]): string {
  if (!content) return '';
  
  let formatted = escapeHtml(content);
  
  // Insert inline citations if available
  if (citations && citations.length > 0 && researchSources && researchSources.length > 0) {

    // Create a map of citation references to source numbers
    const citationMap = new Map();
    citations.forEach((citation, index) => {
      if (citation.reference && citation.reference.startsWith('Source ')) {
        const sourceNum = citation.reference.replace('Source ', '');
        citationMap.set(citation.reference, sourceNum);
      }
    });

    // Since citation references don't exist in the content text,
    // we need to insert citations strategically throughout the content
    const citationEntries = Array.from(citationMap.entries());
    const totalCitations = citationEntries.length;
    
    if (totalCitations > 0) {
      // Split content into sentences for strategic citation placement
      const sentences = formatted.split(/[.!?]+/).filter(s => s.trim().length > 0);
      const sentencesWithCitations: string[] = [];
      
      citationEntries.forEach(([reference, sourceNum], index) => {
        // Distribute citations across sentences
        const targetSentenceIndex = Math.floor((index / totalCitations) * sentences.length);
        const targetSentence = sentences[targetSentenceIndex] || sentences[sentences.length - 1];
        
        // Add citation to the end of the target sentence using a superscript marker
        const citeHtml = ` <sup class="liw-cite" data-source-index="${sourceNum}">[${sourceNum}]</sup>`;
        const sentenceWithCitation = targetSentence.trim() + citeHtml;
        sentencesWithCitations[targetSentenceIndex] = sentenceWithCitation;
        
      });
      
      // Reconstruct content with citations
      formatted = sentences.map((sentence, index) => {
        return sentencesWithCitations[index] || sentence;
      }).join('. ') + '.';
    }
  }
  
  // Format hashtags
  formatted = formatted.replace(/#(\w+)/g, '<span style="color: #0a66c2; font-weight: 600;">#$1</span>');
  
  // Format mentions
  formatted = formatted.replace(/@(\w+)/g, '<span style="color: #0a66c2; font-weight: 600;">@$1</span>');
  
  // Format headers (lines starting with #)
  formatted = formatted.replace(/^# (.+)$/gm, '<h1 style="font-size: 24px; font-weight: 700; color: #1d1d1f; margin: 16px 0 12px 0; line-height: 1.3;">$1</h1>');
  formatted = formatted.replace(/^## (.+)$/gm, '<h2 style="font-size: 20px; font-weight: 600; color: #1d1d1f; margin: 14px 0 10px 0; line-height: 1.3;">$1</h2>');
  formatted = formatted.replace(/^### (.+)$/gm, '<h3 style="font-size: 18px; font-weight: 600; color: #1d1d1f; margin: 12px 0 8px 0; line-height: 1.3;">$1</h3>');
  
  // Format bold text
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong style="font-weight: 600;">$1</strong>');
  
  // Format italic text
  formatted = formatted.replace(/\*(.+?)\*/g, '<em style="font-style: italic;">$1</em>');
  
  // Format bullet points
  formatted = formatted.replace(/^[•·-] (.+)$/gm, '<div style="margin: 4px 0; padding-left: 16px;">• $1</div>');
  
  // Format numbered lists
  formatted = formatted.replace(/^\d+\. (.+)$/gm, (match, content, offset, string) => {
    const lines = string.substring(0, offset).split('\n');
    const currentLineIndex = lines.length - 1;
    const currentLine = lines[currentLineIndex];
    const number = currentLine.match(/^(\d+)\./)?.[1] || '1';
    return `<div style="margin: 4px 0; padding-left: 16px;">${number}. ${content}</div>`;
  });
  
  // Format line breaks
  formatted = formatted.replace(/\n\n/g, '</p><p style="margin: 12px 0; line-height: 1.6; color: #333;">');
  formatted = formatted.replace(/\n/g, '<br/>');
  
  // Wrap in paragraph tags
  formatted = `<p style="margin: 12px 0; line-height: 1.6; color: #333;">${formatted}</p>`;
  
  return formatted;
}

// Lightweight LCS-based diff highlighting for professional content changes
export function diffMarkup(oldText: string, newText: string): string {
  const MAX = 4000;
  const a = (oldText || '').slice(0, MAX);
  const b = (newText || '').slice(0, MAX);
  const n = a.length, m = b.length;
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      if (a[i] === b[j]) dp[i][j] = dp[i + 1][j + 1] + 1;
      else dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  
  let i = 0, j = 0;
  let out = '';
  
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      out += a[i];
      i++; j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      out += `<s class="liw-del">${escapeHtml(a[i])}</s>`;
      i++;
    } else {
      out += `<em class="liw-add">${escapeHtml(b[j])}</em>`;
      j++;
    }
  }
  
  while (i < n) { out += `<s class="liw-del">${escapeHtml(a[i++])}</s>`; }
  while (j < m) { out += `<em class="liw-add">${escapeHtml(b[j++])}</em>`; }
  
  if (oldText.length > MAX || newText.length > MAX) out += '<span class="liw-more"> …</span>';
  
  return out;
}
