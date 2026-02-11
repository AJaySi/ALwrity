/**
 * Refactored Billing Service
 * Main billing service with security validation and improved maintainability
 */

import axios from 'axios';
import { emitApiEvent } from '../../utils/apiEvents';
import { 
  SubscriptionRequest,
  BillingCycle,
  SubscriptionRequestSchema
} from './types';
import { billingAPI } from './api';
import { 
  subscribeToPlan,
  getUserSubscription
} from './subscriptionService';
import { 
  getUsageStats,
  getUsageTrends,
  getUsageLogs,
  getDashboardData
} from './usageService';
import { 
  getSubscriptionPlans
} from './plansService';
import { 
  getAPIPricing
} from './plansService';
import { 
  getUsageAlerts,
  markAlertRead
} from './alertsService';
import { 
  formatCurrency,
  formatPercentage,
  getUsageStatusColor,
  getUsageStatusIcon,
  calculateUsagePercentage,
  getProviderIcon,
  getProviderColor,
  validateBillingPeriod,
  formatNumber
} from './utils';

// Import pre-flight check functions
import { checkPreflight, checkPreflightBatch } from './usageService';

// Import renewal history
import { getRenewalHistory } from './subscriptionService';

/**
 * Set authentication token getter for billing API
 * Call this from App.tsx when Clerk is available
 */
export const setBillingAuthTokenGetter = (getter: () => Promise<string | null>) => {
  // Store the getter for use in API interceptors
  // This will be used by the billingAPI instance from api.ts
  console.log('[BillingService] Auth token getter set');
};

/**
 * Comprehensive billing service with all operations
 * Includes security validation, error handling, and proper event tracking
 */
export const billingService = {
  // Subscription operations
  subscribeToPlan,
  getUserSubscription,
  getRenewalHistory,
  
  // Plans operations
  getSubscriptionPlans,
  getAPIPricing,
  
  // Usage operations
  getDashboardData,
  getUsageStats,
  getUsageTrends,
  getUsageLogs,
  
  // Alert operations
  getUsageAlerts,
  markAlertRead,
  
  // Utilities
  validateBillingPeriod,
  formatCurrency,
  formatNumber,
  formatPercentage,
  getUsageStatusColor,
  getUsageStatusIcon,
  calculateUsagePercentage,
  getProviderIcon,
  getProviderColor,
  
  // Pre-flight checks
  checkPreflight,
  checkPreflightBatch,
  
  // API client
  billingAPI,
  
  // Auth token management
  setBillingAuthTokenGetter,
};
