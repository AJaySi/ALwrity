/**
 * Billing Services Index
 * Central export point for all billing-related services
 */

// Core billing service
export { default as billingService } from './billingService';

// Types and validation
export * from './types';
export { 
  SubscriptionRequest,
  BillingCycle,
  SubscriptionRequestSchema
} from './types';

// Utilities
export {
  validateBillingPeriod,
  formatCurrency,
  formatPercentage,
  getUsageStatusColor,
  getUsageStatusIcon,
  calculateUsagePercentage,
  getProviderIcon,
  getProviderColor,
  checkRateLimit,
  getRateLimitStatus,
  clearRateLimit
} from './utils';

// API clients
export { billingAPI } from './api';
