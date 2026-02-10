/**
 * Dashboard utilities for the Backlinking Dashboard
 *
 * Shared utilities, constants, and helper functions
 */

import { Campaign } from '../types/dashboard.types';
import { People as PeopleIcon, Send as SendIcon, TrendingUp as TrendingUpIcon, Business as BusinessIcon } from '@mui/icons-material';

export const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'success';
    case 'paused':
      return 'warning';
    case 'completed':
      return 'info';
    default:
      return 'default';
  }
};

export const getStatusIcon = (status: string) => {
  switch (status) {
    case 'active':
      return 'play_arrow';
    case 'paused':
      return 'pause';
    case 'completed':
      return 'check_circle';
    default:
      return 'schedule';
  }
};

export const getStatusIconComponent = (status: string) => {
  switch (status) {
    case 'active':
      return 'PlayArrow';
    case 'paused':
      return 'Pause';
    case 'completed':
      return 'CheckCircle';
    default:
      return 'Schedule';
  }
};

export const calculateQuickStats = (campaigns: Campaign[]) => {
  const totalProspects = campaigns.reduce((sum, campaign) => sum + (campaign.email_stats?.sent || 0), 0);
  const totalEmailsSent = campaigns.reduce((sum, campaign) => sum + (campaign.email_stats?.sent || 0), 0);
  const avgSuccessRate = campaigns.length > 0
    ? campaigns.reduce((sum, campaign) => {
        const sent = campaign.email_stats?.sent || 0;
        const replied = campaign.email_stats?.replied || 0;
        return sum + (sent > 0 ? (replied / sent) * 100 : 0);
      }, 0) / campaigns.length
    : 0;
  const avgDomainAuthority = 68.5; // This could be calculated from campaign data

  return [
    { icon: PeopleIcon, label: 'Active Prospects', value: totalProspects.toLocaleString(), color: '#60A5FA' },
    { icon: SendIcon, label: 'Emails This Week', value: totalEmailsSent.toString(), color: '#A855F7' },
    { icon: TrendingUpIcon, label: 'Success Rate', value: `${avgSuccessRate.toFixed(1)}%`, color: '#10B981' },
    { icon: BusinessIcon, label: 'Avg Domain DA', value: avgDomainAuthority.toString(), color: '#F59E0B' },
  ];
};

export const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString();
};

export const formatTime = (date: Date) => {
  return date.toLocaleTimeString();
};