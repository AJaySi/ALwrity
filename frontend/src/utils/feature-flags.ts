/**
 * Feature Flags for Gradual Rollout
 * Controls optimization features to ensure safe deployment
 */

interface FeatureFlags {
  lazyLoading: boolean;
  performanceMonitoring: boolean;
  bundleOptimization: boolean;
  errorBoundaries: boolean;
}

// Default feature flags - can be overridden by environment variables
const DEFAULT_FLAGS: FeatureFlags = {
  lazyLoading: process.env.REACT_APP_LAZY_LOADING === 'true',
  performanceMonitoring: process.env.REACT_APP_PERFORMANCE_MONITORING !== 'false',
  bundleOptimization: process.env.REACT_APP_BUNDLE_OPTIMIZATION !== 'false',
  errorBoundaries: process.env.REACT_APP_ERROR_BOUNDARIES !== 'false',
};

/**
 * Get feature flag value
 */
export const getFeatureFlag = (flag: keyof FeatureFlags): boolean => {
  // Check environment variable first
  const envValue = process.env[`REACT_APP_${flag.toUpperCase()}`];
  if (envValue !== undefined) {
    return envValue === 'true';
  }
  
  // Fall back to default
  return DEFAULT_FLAGS[flag];
};

/**
 * Get all feature flags
 */
export const getAllFeatureFlags = (): FeatureFlags => {
  return {
    lazyLoading: getFeatureFlag('lazyLoading'),
    performanceMonitoring: getFeatureFlag('performanceMonitoring'),
    bundleOptimization: getFeatureFlag('bundleOptimization'),
    errorBoundaries: getFeatureFlag('errorBoundaries'),
  };
};

/**
 * Feature flag status for debugging
 */
export const logFeatureFlags = (): void => {
  const flags = getAllFeatureFlags();
  console.log('🚩 Feature Flags Status:');
  console.log('======================');
  Object.entries(flags).forEach(([flag, enabled]) => {
    const status = enabled ? '✅ ENABLED' : '❌ DISABLED';
    console.log(`${flag}: ${status}`);
  });
  console.log('======================');
};

export default DEFAULT_FLAGS;
