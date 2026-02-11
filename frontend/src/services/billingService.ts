/**
 * Refactored Billing Service - Main Entry Point
 * Uses modular architecture with security validation
 * 
 * MIGRATION STATUS: ✅ REFACTORED TO MODULAR DESIGN
 * All functionality preserved with improved maintainability
 */

// Import from modular services
import { billingService as modularBillingService } from './billing/billingService';

// Re-export all functionality for backward compatibility
export default modularBillingService;
export const billingAPI = modularBillingService.billingAPI;
export const setBillingAuthTokenGetter = modularBillingService.setBillingAuthTokenGetter;

// Core billing operations
export const getDashboardData = modularBillingService.getDashboardData;
export const getUsageStats = modularBillingService.getUsageStats;
export const getUsageTrends = modularBillingService.getUsageTrends;
export const getSubscriptionPlans = modularBillingService.getSubscriptionPlans;
export const getAPIPricing = modularBillingService.getAPIPricing;
export const subscribeToPlan = modularBillingService.subscribeToPlan;
export const getUserSubscription = modularBillingService.getUserSubscription;
export const getUsageAlerts = modularBillingService.getUsageAlerts;
export const markAlertRead = modularBillingService.markAlertRead;
export const getUsageLogs = modularBillingService.getUsageLogs;
export const getRenewalHistory = modularBillingService.getRenewalHistory;

// Utility functions
export const formatCurrency = modularBillingService.formatCurrency;
export const formatNumber = modularBillingService.formatNumber;
export const formatPercentage = modularBillingService.formatPercentage;
export const getUsageStatusColor = modularBillingService.getUsageStatusColor;
export const getUsageStatusIcon = modularBillingService.getUsageStatusIcon;
export const calculateUsagePercentage = modularBillingService.calculateUsagePercentage;
export const getProviderIcon = modularBillingService.getProviderIcon;
export const getProviderColor = modularBillingService.getProviderColor;

// Pre-flight checks
export const checkPreflight = modularBillingService.checkPreflight;
export const checkPreflightBatch = modularBillingService.checkPreflightBatch;

// Export types for backward compatibility
export * from './billing/types';
