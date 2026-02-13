import { useCallback } from 'react';
import { useSubscription } from '../contexts/SubscriptionContext';

interface ApiError {
  response?: {
    status?: number;
    data?: any;
  };
  message?: string;
}

export const useSubscriptionErrorHandler = () => {
  const { showExpiredModal } = useSubscription();

  const handleApiError = useCallback((error: ApiError) => {
    // Check if it's a subscription-related error
    const status = error.response?.status;

    if (status === 429 || status === 402) {
      console.log('Subscription error detected, letting global handler manage modal');

      // Don't show modal directly - let the global API client handler manage it
      // This ensures proper subscription state checking and modal spam prevention
      return true; // Indicates subscription error was detected
    }

    return false; // Not a subscription error
  }, []);

  const handleSubscriptionExpired = useCallback(() => {
    console.log('Manually triggering subscription expired modal');
    showExpiredModal();
  }, [showExpiredModal]);

  return {
    handleApiError,
    handleSubscriptionExpired
  };
};
