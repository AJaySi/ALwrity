/**
 * Subscription Plans Service
 * Fetches available subscription plans with proper error handling
 */

import axios from 'axios';
import { billingAPI } from './api';
import { SubscriptionPlan, APIPricing } from './types';

/**
 * Get all available subscription plans
 */
export const getSubscriptionPlans = async (): Promise<SubscriptionPlan[]> => {
  try {
    const response = await billingAPI.get('/plans');
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch subscription plans');
    }
    
    return response.data.data.plans;
  } catch (error) {
    console.error('Error fetching subscription plans:', error);
    throw error;
  }
};

/**
 * Get API pricing information
 */
export const getAPIPricing = async (provider?: string): Promise<APIPricing[]> => {
  try {
    const params = provider ? { provider } : {};
    const response = await billingAPI.get('/pricing', { params });
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch API pricing');
    }
    
    return response.data.data.pricing;
  } catch (error) {
    console.error('Error fetching API pricing:', error);
    throw error;
  }
};
