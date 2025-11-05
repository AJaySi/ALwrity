import { ResearchMode } from '../services/blogWriterApi';

export interface ResearchHistoryEntry {
  keywords: string[];
  industry: string;
  targetAudience: string;
  researchMode: ResearchMode;
  timestamp: number;
  resultSummary?: string; // Optional: show snippet from results
}

const HISTORY_STORAGE_KEY = 'alwrity_research_history';
const MAX_HISTORY_ENTRIES = 5;

/**
 * Get all research history entries, sorted by most recent first
 */
export function getResearchHistory(): ResearchHistoryEntry[] {
  try {
    const stored = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!stored) return [];
    
    const entries = JSON.parse(stored) as ResearchHistoryEntry[];
    if (!Array.isArray(entries)) return [];
    
    // Sort by timestamp (most recent first) and limit to MAX_HISTORY_ENTRIES
    return entries
      .sort((a, b) => b.timestamp - a.timestamp)
      .slice(0, MAX_HISTORY_ENTRIES);
  } catch (error) {
    console.warn('Failed to load research history:', error);
    return [];
  }
}

/**
 * Add a new research entry to history
 */
export function addResearchHistory(entry: Omit<ResearchHistoryEntry, 'timestamp'>): void {
  try {
    const currentHistory = getResearchHistory();
    
    // Create new entry with timestamp
    const newEntry: ResearchHistoryEntry = {
      ...entry,
      timestamp: Date.now(),
    };
    
    // Check if similar entry already exists (same keywords, industry, audience)
    const existingIndex = currentHistory.findIndex(
      (e) =>
        JSON.stringify(e.keywords.sort()) === JSON.stringify(entry.keywords.sort()) &&
        e.industry === entry.industry &&
        e.targetAudience === entry.targetAudience &&
        e.researchMode === entry.researchMode
    );
    
    // If exists, remove it (we'll add it back at the top)
    const updatedHistory =
      existingIndex >= 0
        ? currentHistory.filter((_, i) => i !== existingIndex)
        : currentHistory;
    
    // Add new entry at the beginning and limit to MAX_HISTORY_ENTRIES
    const finalHistory = [newEntry, ...updatedHistory].slice(0, MAX_HISTORY_ENTRIES);
    
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(finalHistory));
  } catch (error) {
    console.warn('Failed to save research history:', error);
  }
}

/**
 * Clear all research history
 */
export function clearResearchHistory(): void {
  try {
    localStorage.removeItem(HISTORY_STORAGE_KEY);
  } catch (error) {
    console.warn('Failed to clear research history:', error);
  }
}

/**
 * Remove a specific entry from history by timestamp
 */
export function removeResearchHistoryEntry(timestamp: number): void {
  try {
    const currentHistory = getResearchHistory();
    const updatedHistory = currentHistory.filter((e) => e.timestamp !== timestamp);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updatedHistory));
  } catch (error) {
    console.warn('Failed to remove research history entry:', error);
  }
}

/**
 * Format timestamp for display (e.g., "2 hours ago", "Yesterday")
 */
export function formatHistoryTimestamp(timestamp: number): string {
  const now = Date.now();
  const diffMs = now - timestamp;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins} min${diffMins > 1 ? 's' : ''} ago`;
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays === 1) return 'Yesterday';
  if (diffDays < 7) return `${diffDays} days ago`;
  
  // For older entries, show date
  const date = new Date(timestamp);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Generate a short summary from keywords for display
 */
export function getHistorySummary(entry: ResearchHistoryEntry): string {
  if (entry.resultSummary) {
    return entry.resultSummary.length > 60
      ? entry.resultSummary.substring(0, 60) + '...'
      : entry.resultSummary;
  }
  
  // Fallback to first keyword or keywords joined
  if (entry.keywords.length === 0) return 'Research query';
  if (entry.keywords.length === 1) return entry.keywords[0];
  return entry.keywords.slice(0, 2).join(', ') + (entry.keywords.length > 2 ? '...' : '');
}
