/**
 * Dashboard Types
 *
 * Shared type definitions for the Backlinking Dashboard
 */

export interface Campaign {
  campaign_id: string;
  user_id: string;
  name: string;
  keywords: string[];
  status: string;
  created_at: string;
  email_stats: {
    sent: number;
    replied: number;
    bounced: number;
  };
}

export interface SnackbarState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'info' | 'warning';
}

export interface StatItem {
  icon: React.ComponentType<any>;
  label: string;
  value: string | number;
  color: string;
}