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

    // This would typically come from usage tracking
    // For now, return the limit as remaining usage
    switch (feature) {
      case 'gemini_calls':
        return subscription.limits.gemini_calls;
      case 'openai_calls':
        return subscription.limits.openai_calls;
      case 'anthropic_calls':
        return subscription.limits.anthropic_calls;
      case 'mistral_calls':
        return subscription.limits.mistral_calls;
      case 'tavily_calls':
        return subscription.limits.tavily_calls;
      case 'serper_calls':
        return subscription.limits.serper_calls;
      case 'metaphor_calls':
        return subscription.limits.metaphor_calls;
      case 'firecrawl_calls':
        return subscription.limits.firecrawl_calls;
      case 'stability_calls':
        return subscription.limits.stability_calls;
      case 'video_calls':
        return subscription.limits.video_calls || 0;
      case 'image_edit_calls':
        return subscription.limits.image_edit_calls || 0;
      case 'audio_calls':
        return subscription.limits.audio_calls || 0;
      case 'ai_text_generation_calls':
        return subscription.limits.ai_text_generation_calls || 0;
      case 'exa_calls':
        return subscription.limits.exa_calls || 0;
      case 'wavespeed_calls':
        return subscription.limits.wavespeed_calls || 0;
      case 'monthly_cost':
        return subscription.limits.monthly_cost;
      default:
        return 0;
    }
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
