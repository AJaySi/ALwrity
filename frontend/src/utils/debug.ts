/**
 * Debug utility for controlling frontend logging
 */

// Check for debug mode via localStorage or URL parameter
const getDebugMode = (): boolean => {
  // Check URL parameter first (e.g., ?debug=true)
  if (typeof window !== 'undefined') {
    const urlParams = new URLSearchParams(window.location.search);
    const urlDebug = urlParams.get('debug');
    if (urlDebug === 'true') return true;
    if (urlDebug === 'false') return false;
    
    // Check localStorage
    const stored = localStorage.getItem('alwrity-debug');
    if (stored === 'true') return true;
    if (stored === 'false') return false;
  }
  
  // Default to false in production, true in development
  return process.env.NODE_ENV === 'development';
};

let isDebugMode = getDebugMode();

export const debug = {
  /**
   * Check if debug mode is enabled
   */
  isEnabled: () => isDebugMode,
  
  /**
   * Enable debug mode
   */
  enable: () => {
    isDebugMode = true;
    if (typeof window !== 'undefined') {
      localStorage.setItem('alwrity-debug', 'true');
    }
  },
  
  /**
   * Disable debug mode
   */
  disable: () => {
    isDebugMode = false;
    if (typeof window !== 'undefined') {
      localStorage.setItem('alwrity-debug', 'false');
    }
  },
  
  /**
   * Toggle debug mode
   */
  toggle: () => {
    if (isDebugMode) {
      debug.disable();
    } else {
      debug.enable();
    }
  },
  
  /**
   * Log a message only if debug mode is enabled
   */
  log: (message: string, ...args: any[]) => {
    if (isDebugMode) {
      console.log(`🔍 ${message}`, ...args);
    }
  },
  
  /**
   * Log an error (always shown)
   */
  error: (message: string, ...args: any[]) => {
    console.error(`❌ ${message}`, ...args);
  },
  
  /**
   * Log a warning (always shown)
   */
  warn: (message: string, ...args: any[]) => {
    console.warn(`⚠️ ${message}`, ...args);
  },
  
  /**
   * Log an info message (always shown)
   */
  info: (message: string, ...args: any[]) => {
    console.info(`ℹ️ ${message}`, ...args);
  }
};

// Expose global toggle for easy access
if (typeof window !== 'undefined') {
  (window as any).toggleDebug = debug.toggle;
  (window as any).debugMode = debug;
}

