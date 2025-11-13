/**
 * Hook for polling OAuth token alerts and showing toast notifications
 * 
 * This hook periodically checks for new OAuth token failure alerts
 * and displays toast notifications when detected.
 */

import { useEffect, useRef } from 'react';
import { billingService } from '../services/billingService';
import { UsageAlert } from '../types/billing';
import { showToastNotification } from '../utils/toastNotifications';

interface UseOAuthTokenAlertsOptions {
  /**
   * Polling interval in milliseconds
   * @default 60000 (1 minute)
   */
  interval?: number;
  
  /**
   * Whether to enable polling
   * @default true
   */
  enabled?: boolean;
  
  /**
   * User ID - if not provided, will use localStorage or skip polling
   */
  userId?: string;
}

/**
 * Hook to poll for OAuth token alerts and show toast notifications
 * 
 * Polls the UsageAlert API for new OAuth token alerts (oauth_token_failure, oauth_token_warning)
 * and displays toast notifications when new unread alerts are detected.
 * 
 * @param options Polling configuration options
 * @returns Object with polling state and controls
 */
export function useOAuthTokenAlerts(options: UseOAuthTokenAlertsOptions = {}) {
  const {
    interval = 60000, // 1 minute default
    enabled = true,
    userId
  } = options;
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastAlertIdsRef = useRef<Set<number>>(new Set());
  const isPollingRef = useRef(false);
  
  useEffect(() => {
    if (!enabled) {
      return;
    }
    
    const actualUserId = userId || localStorage.getItem('user_id');
    if (!actualUserId) {
      console.debug('useOAuthTokenAlerts: No user ID available, skipping polling');
      return;
    }
    
    const pollAlerts = async () => {
      // Prevent concurrent polls
      if (isPollingRef.current) {
        return;
      }
      
      try {
        isPollingRef.current = true;
        
        // Fetch unread alerts only
        const alerts = await billingService.getUsageAlerts(actualUserId, true);
        
        // Filter for OAuth token alerts
        const oauthAlerts = alerts.filter(
          (alert: UsageAlert) => 
            alert.type === 'oauth_token_failure' || 
            alert.type === 'oauth_token_warning'
        );
        
        // Find new alerts (not in our tracked set)
        const newAlerts = oauthAlerts.filter(
          (alert: UsageAlert) => !lastAlertIdsRef.current.has(alert.id)
        );
        
        // Show toast notifications for new alerts
        for (const alert of newAlerts) {
          // Map severity to notification type
          const notificationType = 
            alert.severity === 'error' ? 'error' :
            alert.severity === 'warning' ? 'warning' :
            'info';
          
          // Show toast notification
          showToastNotification(alert.message, notificationType);
          
          // Track this alert ID
          lastAlertIdsRef.current.add(alert.id);
          
          console.log(`OAuth token alert notification: ${alert.title}`, {
            type: alert.type,
            severity: alert.severity,
            platform: extractPlatformFromTitle(alert.title)
          });
        }
        
        // Update tracked alert IDs (keep only current alerts to handle deletions)
        lastAlertIdsRef.current = new Set(oauthAlerts.map((a: UsageAlert) => a.id));
        
      } catch (error) {
        console.error('Error polling OAuth token alerts:', error);
        // Don't show error to user - this is background polling
      } finally {
        isPollingRef.current = false;
      }
    };
    
    // Poll immediately on mount
    pollAlerts();
    
    // Set up periodic polling
    intervalRef.current = setInterval(pollAlerts, interval);
    
    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [enabled, interval, userId]);
  
  return {
    isPolling: isPollingRef.current
  };
}

// Note: showToastNotification is now imported from utils/toastNotifications.ts
// This ensures consistent toast notifications across the app

/**
 * Extract platform name from alert title
 * Used for logging/debugging
 */
function extractPlatformFromTitle(title: string): string {
  const match = title.match(/^(Google Search Console|Bing Webmaster Tools|WordPress|Wix)/);
  return match ? match[1] : 'Unknown';
}

