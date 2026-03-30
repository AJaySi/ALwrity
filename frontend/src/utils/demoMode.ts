/**
 * Demo mode detection utilities for podcast-only demo mode.
 */

const DEMO_MODE_STORAGE_KEYS = [
  'app_mode',
  'demo_mode',
  'podcast_only_demo_mode',
];

const DEMO_MODE_ENV_KEYS = [
  'REACT_APP_APP_MODE',
  'REACT_APP_DEMO_MODE',
  'REACT_APP_PODCAST_ONLY_DEMO_MODE',
];

/**
 * Check if podcast-only demo mode is enabled.
 * Checks localStorage first, then environment variables.
 */
export function isPodcastOnlyDemoMode(): boolean {
  // Check localStorage
  for (const key of DEMO_MODE_STORAGE_KEYS) {
    const value = (localStorage.getItem(key) || '').toLowerCase();
    if (value === 'true' || value === 'podcast-only' || value === 'podcast_only') {
      return true;
    }
  }

  // Check environment variables
  for (const key of DEMO_MODE_ENV_KEYS) {
    const value = (process.env[key] || '').toLowerCase();
    if (value === 'true' || value === 'podcast-only' || value === 'podcast_only') {
      return true;
    }
  }

  return false;
}

/**
 * Check if the app should skip onboarding entirely.
 * Returns true in podcast-only demo mode.
 */
export function shouldSkipOnboarding(): boolean {
  return isPodcastOnlyDemoMode();
}
