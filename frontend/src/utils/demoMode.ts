/**
 * Consolidated feature mode detection utilities.
 * 
 * Primary: REACT_APP_ENABLED_FEATURES (format: "all" or "podcast,core")
 * 
 * DEPRECATED (fallback order):
 * - REACT_APP_APP_MODE
 * - REACT_APP_DEMO_MODE
 * - REACT_APP_PODCAST_ONLY_DEMO_MODE
 */

const ENABLED_FEATURES_STORAGE_KEYS = [
  'enabled_features',  // Primary
  'app_mode',
  'demo_mode',
  'podcast_only_demo_mode',
];

const ENABLED_FEATURES_ENV_KEYS = [
  'REACT_APP_ENABLED_FEATURES',  // Primary - use this!
  'REACT_APP_APP_MODE',           // DEPRECATED
  'REACT_APP_DEMO_MODE',          // DEPRECATED
  'REACT_APP_PODCAST_ONLY_DEMO_MODE', // DEPRECATED
];

/**
 * Get enabled features from localStorage or environment.
 * Returns a set of enabled feature names.
 */
export function getEnabledFeatures(): Set<string> {
  // Check localStorage first
  for (const key of ENABLED_FEATURES_STORAGE_KEYS) {
    const value = localStorage.getItem(key);
    if (value) {
      const features = value.toLowerCase().split(',').map(f => f.trim());
      if (features.includes('all')) {
        return new Set(['all']);
      }
      return new Set(features.filter(f => f));
    }
  }

  // Check environment variables
  for (const key of ENABLED_FEATURES_ENV_KEYS) {
    const value = process.env[key];
    if (value) {
      const features = value.toLowerCase().split(',').map(f => f.trim());
      if (features.includes('all')) {
        return new Set(['all']);
      }
      return new Set(features.filter(f => f));
    }
  }

  // Default: all features enabled
  return new Set(['all']);
}

/**
 * Check if a specific feature is enabled.
 */
export function isFeatureEnabled(feature: string): boolean {
  const enabled = getEnabledFeatures();
  return enabled.has('all') || enabled.has(feature);
}

/**
 * Check if podcast-only mode is enabled.
 * Returns true when podcast is enabled but not "all".
 */
export function isPodcastOnlyDemoMode(): boolean {
  const enabled = getEnabledFeatures();
  return enabled.has('podcast') && !enabled.has('all');
}

/**
 * Check if the app should skip onboarding entirely.
 * Returns true in podcast-only demo mode or when not using all features.
 */
export function shouldSkipOnboarding(): boolean {
  const enabled = getEnabledFeatures();
  return enabled.has('podcast') || !enabled.has('all');
}
