export interface DiffSegment {
  value: string;
  added?: boolean;
  removed?: boolean;
}

export interface SectionDiff {
  id: string;
  heading: string;
  originalContent: string;
  newContent: string;
  segments: DiffSegment[];
  changed: boolean;
}

export interface DiffPreviewData {
  introductionDiff: DiffSegment[] | null;
  introductionChanged: boolean;
  originalIntroduction: string;
  newIntroduction: string;
  sectionDiffs: SectionDiff[];
}

function tokenize(text: string): string[] {
  return text.split(/(\s+|[.,!?;:()\[\]{}"'——-])/).filter(Boolean);
}

function computeLCS(oldTokens: string[], newTokens: string[]): number[][] {
  const m = oldTokens.length;
  const n = newTokens.length;
  const dp: number[][] = Array.from({ length: m + 1 }, () => new Array(n + 1).fill(0));
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (oldTokens[i - 1] === newTokens[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  return dp;
}

function backtrackLCS(
  dp: number[][], oldTokens: string[], newTokens: string[],
  i: number, j: number, oldIdx: number, newIdx: number,
  segments: { type: 'same' | 'removed' | 'added'; token: string }[]
) {
  if (i === 0 && j === 0) return;
  if (i > 0 && j > 0 && oldTokens[i - 1] === newTokens[j - 1]) {
    backtrackLCS(dp, oldTokens, newTokens, i - 1, j - 1, oldIdx - 1, newIdx - 1, segments);
    segments.push({ type: 'same', token: oldTokens[i - 1] });
  } else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {
    backtrackLCS(dp, oldTokens, newTokens, i, j - 1, oldIdx, newIdx - 1, segments);
    segments.push({ type: 'added', token: newTokens[j - 1] });
  } else if (i > 0) {
    backtrackLCS(dp, oldTokens, newTokens, i - 1, j, oldIdx - 1, newIdx, segments);
    segments.push({ type: 'removed', token: oldTokens[i - 1] });
  }
}

function computeWordDiff(original: string, updated: string): DiffSegment[] {
  const oldTokens = tokenize(original || '');
  const newTokens = tokenize(updated || '');
  const dp = computeLCS(oldTokens, newTokens);
  const aligned: { type: 'same' | 'removed' | 'added'; token: string }[] = [];
  backtrackLCS(dp, oldTokens, newTokens, oldTokens.length, newTokens.length, oldTokens.length, newTokens.length, aligned);

  const merged: DiffSegment[] = [];
  for (const item of aligned) {
    if (item.type === 'same') {
      const last = merged[merged.length - 1];
      if (last && !last.added && !last.removed) {
        last.value += item.token;
      } else {
        merged.push({ value: item.token });
      }
    } else if (item.type === 'removed') {
      const last = merged[merged.length - 1];
      if (last && last.removed) {
        last.value += item.token;
      } else {
        merged.push({ value: item.token, removed: true });
      }
    } else {
      const last = merged[merged.length - 1];
      if (last && last.added) {
        last.value += item.token;
      } else {
        merged.push({ value: item.token, added: true });
      }
    }
  }
  return merged;
}

export function getSectionDiffs(
  outlineHeadings: { id: string; heading: string }[],
  originalSections: Record<string, string>,
  newSections: Record<string, string>,
  originalIntroduction?: string,
  newIntroduction?: string
): DiffPreviewData {
  const sectionDiffs: SectionDiff[] = outlineHeadings.map(({ id, heading }) => {
    const originalContent = originalSections[id] || '';
    const newContent = newSections[id] || '';
    const segments = computeWordDiff(originalContent, newContent);
    const changed = segments.some(s => s.added || s.removed);
    return { id, heading, originalContent, newContent, segments, changed };
  });

  let introductionDiff: DiffSegment[] | null = null;
  let introductionChanged = false;
  if (originalIntroduction !== undefined && newIntroduction !== undefined) {
    introductionDiff = computeWordDiff(originalIntroduction || '', newIntroduction || '');
    introductionChanged = introductionDiff && introductionDiff.some(s => s.added || s.removed);
  }

  return { introductionDiff, introductionChanged, originalIntroduction: originalIntroduction || '', newIntroduction: newIntroduction || '', sectionDiffs };
}

export { computeWordDiff };
