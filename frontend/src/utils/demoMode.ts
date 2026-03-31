/**
 * Consolidated feature mode detection utilities.
 * 
 * Primary env var: REACT_APP_ENABLED_FEATURES
 * Format: "all" or comma-separated: "podcast,core"
 */

const PRIMARY_STORAGE_KEY = 'enabled_features';
const PRIMARY_ENV_KEY = 'REACT_APP_ENABLED_FEATURES';

/**
 * Get enabled features from localStorage or environment.
 * Returns a Set of enabled feature names.
 */
export function getEnabledFeatures(): Set<string> {
  // Check localStorage first
  const storageValue = localStorage.getItem(PRIMARY_STORAGE_KEY);
  if (storageValue) {
    const features = storageValue.toLowerCase().split(',').map(f => f.trim());
    if (features.includes('all')) {
      return new Set(['all']);
    }
    return new Set(features.filter(f => f));
  }

  // Check environment variable
  const envValue = process.env[PRIMARY_ENV_KEY];
  if (envValue) {
    const features = envValue.toLowerCase().split(',').map(f => f.trim());
    if (features.includes('all')) {
      return new Set(['all']);
    }
    return new Set(features.filter(f => f));
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
 * Check if the app should skip onboarding.
 * Returns true in podcast-only mode.
 */
export function shouldSkipOnboarding(): boolean {
  const enabled = getEnabledFeatures();
  return enabled.has('podcast') || !enabled.has('all');
}
