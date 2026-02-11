/**
 * Subscription Service
 * Core subscription management operations with security validation
 */

import axios, { AxiosResponse } from 'axios';
import { emitApiEvent } from '../../utils/apiEvents';
import { 
  SubscriptionRequest,
  BillingCycle,
  SubscriptionRequestSchema,
  RenewalHistoryResponse,
  RenewalHistoryAPIResponse
} from './types';
import { billingAPI } from './api';
import { checkRateLimit } from './utils';

/**
 * Subscribe to a plan with security validation
 * Validates input parameters before making API request
 */
export const subscribeToPlan = async (
  userId: string,
  planId: number,
  billingCycle: BillingCycle = 'MONTHLY'
): Promise<any> => {
  try {
    // Client-side rate limiting check
    const rateLimitKey = `subscribe_${userId}`;
    if (!checkRateLimit(rateLimitKey, 3, 300000)) { // 3 requests per 5 minutes
      throw new Error('Too many subscription attempts. Please wait a few minutes before trying again.');
    }
    
    // Frontend validation for security
    if (planId <= 0) {
      throw new Error('Plan ID must be a positive number');
    }
      
    if (!['MONTHLY', 'YEARLY'].includes(billingCycle)) {
      throw new Error('Billing cycle must be MONTHLY or YEARLY');
    }

    // Validate request with Zod schema
    const validationResult = SubscriptionRequestSchema.safeParse({
      plan_id: planId,
      billing_cycle: billingCycle
    });
      
    if (!validationResult.success) {
      const errorMessages = validationResult.error.errors.map((err: any) => err.message).join(', ');
      throw new Error(`Validation failed: ${errorMessages}`);
    }

    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const response = await billingAPI.post(`/subscribe/${actualUserId}`, {
      plan_id: planId,
      billing_cycle: billingCycle
    });
      
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to subscribe to plan');
    }
      
    emitApiEvent({ url: `/subscribe/${actualUserId}`, method: 'POST', source: 'billing' });
    return response.data.data;
  } catch (error) {
    console.error('Error subscribing to plan:', error);
    throw error;
  }
};

/**
 * Get user's current subscription information
 */
export const getUserSubscription = async (userId?: string) => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const response = await billingAPI.get(`/user/${actualUserId}/subscription`);
      
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch user subscription');
    }
      
    return response.data.data;
  } catch (error) {
    console.error('Error fetching user subscription:', error);
    throw error;
  }
};

/**
 * Get subscription renewal history for the current user
 */
export const getRenewalHistory = async (
  userId?: string,
  limit: number = 50,
  offset: number = 0
): Promise<RenewalHistoryResponse> => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const params: any = { limit, offset };
    
    const response = await billingAPI.get<RenewalHistoryAPIResponse>(
      `/renewal-history/${actualUserId}`,
      { params }
    );
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch renewal history');
    }
    
    emitApiEvent({ url: `/renewal-history/${actualUserId}`, method: 'GET', source: 'billing' });
    return response.data.data;
  } catch (error: any) {
    console.error('Error fetching renewal history:', error);
    throw new Error(
      error.response?.data?.detail ||
        error.message ||
        'Failed to fetch renewal history'
    );
  }
};
