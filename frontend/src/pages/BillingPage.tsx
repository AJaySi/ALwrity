/**
 * Billing Page
 * Dedicated page for billing and usage information with terminal-themed UI.
 */

import React, { useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { DollarSign } from 'lucide-react';
import { styled } from '@mui/material/styles';
import EnhancedBillingDashboard from '../components/billing/EnhancedBillingDashboard';
import UsageLogsTable from '../components/billing/UsageLogsTable';
import SubscriptionRenewalHistory from '../components/billing/SubscriptionRenewalHistory';
import { showToastNotification } from '../utils/toastNotifications';
import { useSubscription } from '../contexts/SubscriptionContext';

// Terminal-themed styled components
const TerminalContainer = styled(Container)(({ theme }) => ({
  backgroundColor: '#0a0a0a',
  minHeight: '100vh',
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  padding: theme.spacing(3),
  '& *': {
    fontFamily: 'inherit',
  }
}));

const TerminalHeader = styled(Box)({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 24,
  paddingBottom: 16,
  borderBottom: '2px solid #00ff00',
});

const TerminalTitle = styled(Typography)<{ component?: React.ElementType }>(({ theme }) => ({
  color: '#00ff00',
  fontFamily: 'inherit',
  fontSize: '1.75rem',
  fontWeight: 'bold',
  textShadow: '0 0 10px rgba(0, 255, 0, 0.5)',
  letterSpacing: '2px',
}));

const TerminalSubtitle = styled(Typography)({
  color: '#00ff88',
  fontFamily: 'inherit',
  fontSize: '0.875rem',
  marginTop: 4,
  opacity: 0.8,
});

const TerminalIconButton = styled(IconButton)({
  color: '#00ff00',
  border: '1px solid #00ff00',
  '&:hover': {
    backgroundColor: 'rgba(0, 255, 0, 0.1)',
    boxShadow: '0 0 10px rgba(0, 255, 0, 0.3)',
  },
});

const BillingPage: React.FC = () => {
  const { subscription, checkSubscription } = useSubscription();
  
  // Monitor subscription status and show toast notifications
  useEffect(() => {
    if (subscription) {
      // Only show toast for subscription renewal (not for every status check)
      const wasJustRenewed = sessionStorage.getItem('subscription_renewed');
      if (wasJustRenewed && subscription.active) {
        showToastNotification(
          `🎉 Subscription renewed successfully! Your ${subscription.plan} plan is now active.`,
          'success',
          { duration: 6000 }
        );
        sessionStorage.removeItem('subscription_renewed');
      }
      // Note: Subscription expiration toast is handled by SubscriptionContext
      // We don't show toast here for inactive subscriptions to avoid duplicate toasts
    }
  }, [subscription]);
  
  // Check subscription on mount
  useEffect(() => {
    checkSubscription();
  }, [checkSubscription]);
  
  // Listen for subscription renewal events
  useEffect(() => {
    const handleSubscriptionRenewed = () => {
      // Mark that subscription was renewed (will show toast in subscription status effect)
      sessionStorage.setItem('subscription_renewed', 'true');
      // Refresh subscription status to get latest data
      checkSubscription();
    };
    
    window.addEventListener('subscription-updated', handleSubscriptionRenewed);
    return () => {
      window.removeEventListener('subscription-updated', handleSubscriptionRenewed);
    };
  }, [checkSubscription]);
  
  // Listen for subscription limit exceeded events (429 errors from anywhere in the app)
  useEffect(() => {
    const handleSubscriptionLimitExceeded = (event: Event) => {
      const customEvent = event as CustomEvent;
      const { provider, usage_info, message /*, error */ } = customEvent.detail || {};
      
      console.log('BillingPage: Subscription limit exceeded event received', {
        provider,
        usage_info,
        message
      });
      
      // Show toast notification with detailed message
      if (message) {
        // Format message for better readability
        const formattedMessage = message.includes('limit would be exceeded') 
          ? `⚠️ ${message}` // Add warning emoji if not present
          : message;
        showToastNotification(formattedMessage, 'warning', { duration: 10000 }); // Longer duration for detailed messages
      } else {
        // Fallback message if no specific message provided
        const fallbackMessage = usage_info 
          ? `⚠️ Usage limit exceeded for ${provider || 'API'}. Current: ${(usage_info.current_tokens || usage_info.current_calls || 0).toLocaleString()}, Limit: ${(usage_info.limit || 0).toLocaleString()}`
          : '⚠️ You\'ve reached your monthly usage limit. Upgrade your plan to get higher limits.';
        showToastNotification(fallbackMessage, 'warning', { duration: 8000 });
      }
      
      // Refresh billing data to show updated usage
      // Note: EnhancedBillingDashboard will refresh automatically via API events,
      // but we trigger a manual refresh here to ensure immediate update
      setTimeout(() => {
        checkSubscription();
        // Trigger a custom event to refresh billing dashboard
        window.dispatchEvent(new CustomEvent('billing-refresh-requested'));
      }, 500);
    };
    
    window.addEventListener('subscription-limit-exceeded', handleSubscriptionLimitExceeded);
    return () => {
      window.removeEventListener('subscription-limit-exceeded', handleSubscriptionLimitExceeded);
    };
  }, [checkSubscription]);
  
  // Note: EnhancedBillingDashboard has its own refresh functionality
  // This page-level refresh button triggers a full page reload
  const handleRefresh = () => {
    showToastNotification('Refreshing billing data...', 'info', { duration: 2000 });
    checkSubscription();
    // Trigger a full page reload after a short delay to ensure fresh data
    setTimeout(() => {
      window.location.reload();
    }, 500);
  };

  return (
    <TerminalContainer maxWidth="xl">
      {/* Header */}
      <TerminalHeader>
        <Box display="flex" flexDirection="column" gap={2} flex={1}>
          {/* Title Row */}
          <Box display="flex" alignItems="center" justifyContent="space-between">
            <Box display="flex" alignItems="center" gap={2}>
              <DollarSign size={32} color="#00ff00" />
              <Box>
                <TerminalTitle component="h1">
                  BILLING & USAGE DASHBOARD
                </TerminalTitle>
                <TerminalSubtitle>
                  Monitor API usage, costs, and system performance
                </TerminalSubtitle>
              </Box>
            </Box>
            <Box display="flex" alignItems="center" gap={2}>
              <Tooltip 
                title="Refresh billing data"
                arrow
              >
                <TerminalIconButton
                  onClick={handleRefresh}
                >
                  <RefreshIcon />
                </TerminalIconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>
      </TerminalHeader>

          {/* Billing Dashboard Content */}
          <Box>
            <EnhancedBillingDashboard terminalTheme={true} />

            {/* Subscription Renewal History Section */}
            <SubscriptionRenewalHistory 
              userId={undefined} 
              terminalTheme={true}
              initialLimit={20}
            />

            {/* Usage Logs Section */}
            <Box sx={{ mt: 4 }}>
              <UsageLogsTable initialLimit={50} />
            </Box>
          </Box>
    </TerminalContainer>
  );
};

export default BillingPage;

