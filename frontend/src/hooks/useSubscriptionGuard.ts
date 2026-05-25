import { useEffect, useState } from 'react';
import { useSubscription } from '../contexts/SubscriptionContext';

export interface SubscriptionGuardOptions {
  requireActive?: boolean;
  redirectToPricing?: boolean;
  showModal?: boolean;
  fallbackComponent?: React.ReactNode;
}

export const useSubscriptionGuard = (options: SubscriptionGuardOptions = {}) => {
  const { subscription, loading, error, checkSubscription } = useSubscription();
  const [isGuarded, setIsGuarded] = useState(false);

  const {
    requireActive = true,
    redirectToPricing = true,
    showModal = true,
    fallbackComponent
  } = options;

  useEffect(() => {
    if (loading || !subscription) return;

    if (requireActive && !subscription.active) {
      setIsGuarded(true);

      if (redirectToPricing) {
        // Redirect to pricing page or show upgrade modal
        console.warn('Subscription not active, redirecting to pricing');
        // For now, just log - in a real app you'd redirect or show modal
      }

      if (showModal && !fallbackComponent) {
        // Show upgrade modal
        console.warn('Showing subscription upgrade modal');
      }
    } else {
      setIsGuarded(false);
    }
  }, [subscription, loading, requireActive, redirectToPricing, showModal, fallbackComponent]);

  const checkFeatureAccess = (feature: string, currentUsage?: number, limit?: number): boolean => {
    if (!subscription?.active) return false;

    if (limit === undefined) {
      // If no limit specified, assume unlimited or check other conditions
      return true;
    }

    if (currentUsage === undefined) {
      // Can't check usage if we don't have current usage data
      return true; // Allow for now, middleware will enforce
    }

    return currentUsage < limit;
  };

  const getRemainingUsage = (feature: string): number => {
    if (!subscription?.active) return 0;

    const limit = subscription.limits[feature as keyof typeof subscription.limits] ?? 0;
    const used = subscription.currentUsage?.[feature as keyof typeof subscription.limits] ?? 0;
    const remaining = Math.max(0, limit - used);
    return remaining;
  };

  return {
    subscription,
    loading,
    error,
    isGuarded,
    checkSubscription,
    checkFeatureAccess,
    getRemainingUsage,
    canUseFeature: (feature: string) => checkFeatureAccess(feature),
    isFeatureAvailable: (feature: string) => subscription?.active && checkFeatureAccess(feature),
  };
};
