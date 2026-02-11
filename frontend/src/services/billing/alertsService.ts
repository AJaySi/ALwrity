/**
 * Alerts Service
 * Handles usage alerts and alert management
 */

import axios from 'axios';
import { billingAPI } from './api';
import { UsageAlert } from './types';
import { emitApiEvent } from '../../utils/apiEvents';

/**
 * Get usage alerts for a user
 */
export const getUsageAlerts = async (userId?: string, unreadOnly: boolean = false): Promise<UsageAlert[]> => {
  try {
    const actualUserId = userId || localStorage.getItem('user_id') || 'demo-user';
    const response = await billingAPI.get(`/alerts/${actualUserId}`, {
      params: { unread_only: unreadOnly }
    });
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to fetch usage alerts');
    }
    
    emitApiEvent({ url: `/alerts/${actualUserId}`, method: 'GET', source: 'billing' });
    return response.data.data.alerts;
  } catch (error) {
    console.error('Error fetching usage alerts:', error);
    throw error;
  }
};

/**
 * Mark an alert as read
 */
export const markAlertRead = async (alertId: number): Promise<void> => {
  try {
    const response = await billingAPI.post(`/alerts/${alertId}/mark-read`);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to mark alert as read');
    }
  } catch (error) {
    console.error('Error marking alert as read:', error);
    throw error;
  }
};
