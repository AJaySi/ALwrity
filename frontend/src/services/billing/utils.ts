/**
 * Billing Utilities
 * Utility functions for billing operations
 */

import { getApiUrl } from '../../api/client';

/**
 * Validate billing period format (YYYY-MM)
 * Ensures backend billing period validation requirements are met
 */
export const validateBillingPeriod = (period: string): boolean => {
  if (!period || typeof period !== 'string') {
    return false;
  }
  
  // Regex for YYYY-MM format (e.g., 2026-02)
  const billingPeriodRegex = /^\d{4}-(0[1-9]|1[0-2])$/;
  return billingPeriodRegex.test(period);
};

/**
 * Format currency amount for display
 */
export const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 4,
  }).format(amount);
};

/**
 * Format percentage for display
 */
export const formatPercentage = (value: number): string => {
  return `${value.toFixed(1)}%`;
};

/**
 * Get usage status color based on status
 */
export const getUsageStatusColor = (status: string): string => {
  switch (status) {
    case 'active':
      return '#22c55e'; // Green
    case 'warning':
      return '#f59e0b'; // Orange
    case 'limit_reached':
      return '#ef4444'; // Red
    default:
      return '#6b7280'; // Gray
  }
};

/**
 * Get usage status icon based on status
 */
export const getUsageStatusIcon = (status: string): string => {
  switch (status) {
    case 'active':
      return '✅';
    case 'warning':
      return '⚠️';
    case 'limit_reached':
      return '🚨';
    default:
      return '❓';
  }
};

/**
 * Calculate usage percentage
 */
export const calculateUsagePercentage = (current: number, limit: number): number => {
  if (limit === 0) return 0;
  return Math.min((current / limit) * 100, 100);
};

/**
 * Get provider icon based on provider name
 */
export const getProviderIcon = (provider: string): string => {
  const icons: { [key: string]: string } = {
    gemini: '🤖',
    huggingface: '🤗', // HuggingFace icon
  };
  return icons[provider.toLowerCase()] || '🔧';
};

/**
 * Get provider color based on provider name
 */
export const getProviderColor = (provider: string): string => {
  const colors: { [key: string]: string } = {
    gemini: '#4285f4',
    huggingface: '#ffd21e', // HuggingFace yellow color
  };
  return colors[provider.toLowerCase()] || '#6b7280';
};

/**
 * Format number for display
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('en-US').format(num);
};

// Client-side rate limiting for better UX
interface RateLimitEntry {
  timestamp: number;
  count: number;
}

const rateLimitStore = new Map<string, RateLimitEntry>();

/**
 * Client-side rate limiter to prevent API spam
 * @param key - Unique identifier for the operation
 * @param maxRequests - Maximum requests allowed
 * @param windowMs - Time window in milliseconds
 * @returns true if request is allowed, false if rate limited
 */
export const checkRateLimit = (
  key: string, 
  maxRequests: number = 5, 
  windowMs: number = 60000
): boolean => {
  const now = Date.now();
  const entry = rateLimitStore.get(key);
  
  if (!entry || now - entry.timestamp > windowMs) {
    // Reset or create new entry
    rateLimitStore.set(key, { timestamp: now, count: 1 });
    return true;
  }
  
  if (entry.count >= maxRequests) {
    return false; // Rate limited
  }
  
  // Increment count
  entry.count++;
  return true;
};

/**
 * Get rate limit status for an operation
 * @param key - Unique identifier for the operation
 * @returns Rate limit information
 */
export const getRateLimitStatus = (key: string): {
  remaining: number;
  resetTime: number;
  isLimited: boolean;
} => {
  const entry = rateLimitStore.get(key);
  const now = Date.now();
  
  if (!entry || now - entry.timestamp > 60000) {
    return { remaining: 5, resetTime: now + 60000, isLimited: false };
  }
  
  const remaining = Math.max(0, 5 - entry.count);
  const resetTime = entry.timestamp + 60000;
  
  return {
    remaining,
    resetTime,
    isLimited: remaining === 0
  };
};

/**
 * Clear rate limit for a specific key
 * @param key - Unique identifier for the operation
 */
export const clearRateLimit = (key: string): void => {
  rateLimitStore.delete(key);
};
