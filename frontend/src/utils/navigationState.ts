/**
 * Global Navigation State Utility
 * 
 * Manages navigation state preservation across subscription renewals and redirects.
 * Supports:
 * - Page path preservation
 * - Phase state (for tools with phases like Blog Writer)
 * - Tool-specific context (extensible for future tools)
 */

export interface NavigationState {
  path: string;
  phase?: string; // Phase ID for tools with phases (e.g., 'research', 'outline', 'content')
  tool?: string; // Tool identifier (e.g., 'blog-writer', 'other-tool')
  context?: Record<string, any>; // Tool-specific context data
  timestamp: number; // When this state was saved
}

const NAVIGATION_STATE_KEY = 'subscription_navigation_state';

/**
 * Save navigation state before redirecting to pricing/subscription pages
 * 
 * @param path - Current page path (e.g., '/blog-writer')
 * @param phase - Current phase ID (optional, for tools with phases)
 * @param tool - Tool identifier (optional, defaults to detecting from path)
 * @param context - Additional tool-specific context (optional)
 */
export const saveNavigationState = (
  path: string,
  phase?: string,
  tool?: string,
  context?: Record<string, any>
): void => {
  try {
    // Auto-detect tool from path if not provided
    const detectedTool = tool || detectToolFromPath(path);
    
    const state: NavigationState = {
      path,
      phase,
      tool: detectedTool,
      context,
      timestamp: Date.now()
    };
    
    sessionStorage.setItem(NAVIGATION_STATE_KEY, JSON.stringify(state));
    console.log('[NavigationState] Saved navigation state:', state);
  } catch (error) {
    console.error('[NavigationState] Failed to save navigation state:', error);
  }
};

/**
 * Restore navigation state after returning from pricing/subscription pages
 * 
 * @returns NavigationState or null if not found/invalid
 */
export const restoreNavigationState = (): NavigationState | null => {
  try {
    const stored = sessionStorage.getItem(NAVIGATION_STATE_KEY);
    if (!stored) {
      return null;
    }
    
    const state: NavigationState = JSON.parse(stored);
    
    // Validate state (must have path and reasonable timestamp)
    if (!state.path || !state.timestamp) {
      console.warn('[NavigationState] Invalid navigation state:', state);
      return null;
    }
    
    // Clear state after reading (one-time use)
    sessionStorage.removeItem(NAVIGATION_STATE_KEY);
    
    console.log('[NavigationState] Restored navigation state:', state);
    return state;
  } catch (error) {
    console.error('[NavigationState] Failed to restore navigation state:', error);
    sessionStorage.removeItem(NAVIGATION_STATE_KEY);
    return null;
  }
};

/**
 * Get navigation state without clearing it (for inspection)
 */
export const peekNavigationState = (): NavigationState | null => {
  try {
    const stored = sessionStorage.getItem(NAVIGATION_STATE_KEY);
    if (!stored) {
      return null;
    }
    
    return JSON.parse(stored);
  } catch (error) {
    console.error('[NavigationState] Failed to peek navigation state:', error);
    return null;
  }
};

/**
 * Clear navigation state (useful for cleanup)
 */
export const clearNavigationState = (): void => {
  try {
    sessionStorage.removeItem(NAVIGATION_STATE_KEY);
    console.log('[NavigationState] Cleared navigation state');
  } catch (error) {
    console.error('[NavigationState] Failed to clear navigation state:', error);
  }
};

/**
 * Detect tool identifier from path
 */
const detectToolFromPath = (path: string): string | undefined => {
  if (path.includes('/blog-writer') || path.includes('/blogwriter')) {
    return 'blog-writer';
  }
  // Add more tool detection logic as needed
  // if (path.includes('/other-tool')) {
  //   return 'other-tool';
  // }
  return undefined;
};

/**
 * Get current phase from localStorage for a specific tool
 * This is a helper for tools that store phases in localStorage
 */
export const getCurrentPhaseForTool = (tool: string): string | null => {
  try {
    if (tool === 'blog-writer') {
      return localStorage.getItem('blogwriter_current_phase') || null;
    }
    // Add more tool-specific phase retrieval as needed
    return null;
  } catch (error) {
    console.error(`[NavigationState] Failed to get phase for tool ${tool}:`, error);
    return null;
  }
};

/**
 * Save current phase to localStorage for a specific tool
 * This is a helper for tools that store phases in localStorage
 */
export const saveCurrentPhaseForTool = (tool: string, phase: string): void => {
  try {
    if (tool === 'blog-writer') {
      localStorage.setItem('blogwriter_current_phase', phase);
      console.log(`[NavigationState] Saved phase '${phase}' for ${tool}`);
    }
    // Add more tool-specific phase saving as needed
  } catch (error) {
    console.error(`[NavigationState] Failed to save phase for tool ${tool}:`, error);
  }
};

