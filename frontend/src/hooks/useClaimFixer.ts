import { useCallback } from 'react';
import { BlogOutlineSection } from '../services/blogWriterApi';

export const useClaimFixer = (
  outline: BlogOutlineSection[],
  sections: Record<string, string>,
  onSectionsUpdate: (sections: Record<string, string>) => void
) => {
  // Sentence-level claim mapping and patching helpers
  const normalized = useCallback((s: string) => s.toLowerCase().replace(/\s+/g, ' ').trim(), []);

  const fuzzyScore = useCallback((a: string, b: string) => {
    // Dice's coefficient over word bigrams for robustness (no deps)
    const bigrams = (s: string) => {
      const t = s.split(/\W+/).filter(Boolean);
      const grams: string[] = [];
      for (let i = 0; i < t.length - 1; i++) grams.push(`${t[i]} ${t[i+1]}`);
      return grams;
    };
    const A = new Set(bigrams(a));
    const B = new Set(bigrams(b));
    if (!A.size || !B.size) return 0;
    let overlap = 0;
    A.forEach(g => { if (B.has(g)) overlap++; });
    return (2 * overlap) / (A.size + B.size);
  }, []);

  const findSentenceForClaim = useCallback((md: string, claimText: string) => {
    const text = md || '';
    // Split by sentence enders; keep delimiters
    const sentences = text.split(/(?<=[.!?])\s+/);
    const normalizedClaim = claimText.trim().toLowerCase();
    // Direct includes first
    let bestIndex = sentences.findIndex(s => s.toLowerCase().includes(normalizedClaim));
    if (bestIndex >= 0) return { sentence: sentences[bestIndex], index: bestIndex, sentences };
    // Fallback: overlap ratio by words
    const claimWords = normalizedClaim.split(/\W+/).filter(Boolean);
    let bestScore = 0; bestIndex = -1;
    sentences.forEach((s, i) => {
      const sw = s.toLowerCase().split(/\W+/).filter(Boolean);
      const overlap = claimWords.filter(w => sw.includes(w)).length;
      const score = overlap / Math.max(claimWords.length, 1);
      if (score > bestScore) { bestScore = score; bestIndex = i; }
    });
    // Second fallback: Dice coefficient on normalized strings
    if (bestIndex < 0) {
      let diceBest = 0; let diceIdx = -1;
      sentences.forEach((s, i) => {
        const sc = fuzzyScore(normalized(s), normalized(claimText));
        if (sc > diceBest) { diceBest = sc; diceIdx = i; }
      });
      if (diceIdx >= 0) return { sentence: sentences[diceIdx], index: diceIdx, sentences };
    }
    if (bestIndex >= 0) return { sentence: sentences[bestIndex], index: bestIndex, sentences };
    return { sentence: '', index: -1, sentences };
  }, [normalized, fuzzyScore]);

  const buildFullMarkdown = useCallback(() => {
    if (!outline.length) return '';
    return outline.map(s => `## ${s.heading}\n\n${sections[s.id] || ''}`).join('\n\n');
  }, [outline, sections]);

  const buildUpdatedMarkdownForClaim = useCallback((claimText: string, supportingUrl?: string) => {
    const md = buildFullMarkdown();
    const { sentence, index, sentences } = findSentenceForClaim(md, claimText);
    if (!sentence || index < 0) return { original: '', updated: '', updatedMarkdown: md };
    const alreadyHasLink = /\[[^\]]+\]\(([^)]+)\)/.test(sentence);
    const fix = supportingUrl && !alreadyHasLink ? `${sentence} [source](${supportingUrl})` : sentence;
    const updatedSentences = [...sentences];
    updatedSentences[index] = fix;
    const updatedMarkdown = updatedSentences.join(' ');
    return { original: sentence, updated: fix, updatedMarkdown };
  }, [buildFullMarkdown, findSentenceForClaim]);

  const applyClaimFix = useCallback((claimText: string, supportingUrl?: string) => {
    // Naive fix: append citation footnote to the first occurrence of claim text
    const { updatedMarkdown } = buildUpdatedMarkdownForClaim(claimText, supportingUrl);
    const updated = updatedMarkdown;
    // Re-split content back to per-section, by headings
    const parts = updated.split(/^## /gm).filter(Boolean);
    const newSections: Record<string, string> = {};
    outline.forEach((s, idx) => {
      const body = parts[idx] ? parts[idx].replace(new RegExp(`^${s.heading}\n\n?`), '') : (sections[s.id] || '');
      newSections[s.id] = body;
    });
    onSectionsUpdate(newSections);
  }, [buildUpdatedMarkdownForClaim, outline, sections, onSectionsUpdate]);

  return {
    buildFullMarkdown,
    buildUpdatedMarkdownForClaim,
    applyClaimFix
  };
};
