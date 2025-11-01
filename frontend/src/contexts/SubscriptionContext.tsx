import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback, useRef } from 'react';
import { apiClient, setGlobalSubscriptionErrorHandler } from '../api/client';
import SubscriptionExpiredModal from '../components/SubscriptionExpiredModal';

export interface SubscriptionLimits {
  gemini_calls: number;
  openai_calls: number;
  anthropic_calls: number;
  mistral_calls: number;
  tavily_calls: number;
  serper_calls: number;
  metaphor_calls: number;
  firecrawl_calls: number;
  stability_calls: number;
  monthly_cost: number;
}

export interface SubscriptionStatus {
  active: boolean;
  plan: string;
  tier: string;
  can_use_api: boolean;
  reason?: string;
  limits: SubscriptionLimits;
}

interface SubscriptionContextType {
  subscription: SubscriptionStatus | null;
  loading: boolean;
  error: string | null;
  checkSubscription: () => Promise<void>;
  refreshSubscription: () => Promise<void>;
  showExpiredModal: () => void;
  hideExpiredModal: () => void;
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined);

export const useSubscription = () => {
  const context = useContext(SubscriptionContext);
  if (!context) {
    throw new Error('useSubscription must be used within a SubscriptionProvider');
  }
  return context;
};

interface SubscriptionProviderProps {
  children: ReactNode;
}

export const SubscriptionProvider: React.FC<SubscriptionProviderProps> = ({ children }) => {
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [modalErrorData, setModalErrorData] = useState<any>(null);
  const [lastModalShowTime, setLastModalShowTime] = useState<number>(0);
  const [deferredError, setDeferredError] = useState<any>(null);
  const [lastCheckTime, setLastCheckTime] = useState<number>(0);
  // New: Grace window after plan changes to avoid noisy UX
  const [graceUntil, setGraceUntil] = useState<number>(0);
  const [planSignature, setPlanSignature] = useState<string>("");
  // Flag to track if current modal is a usage limit modal (should never be auto-closed)
  const [isUsageLimitModal, setIsUsageLimitModal] = useState<boolean>(false);

  const checkSubscription = useCallback(async () => {
    // Throttle subscription checks to prevent excessive API calls
    const now = Date.now();
    const THROTTLE_MS = 5000; // 5 seconds minimum between checks
    
    if (now - lastCheckTime < THROTTLE_MS) {
      console.log('SubscriptionContext: Check throttled (5s)');
      return;
    }
    
    setLastCheckTime(now);
    setLoading(true);
    setError(null);

    try {
      // Get user ID from localStorage or auth context
      const userId = localStorage.getItem('user_id') || 'anonymous';
      
      // Don't make API call if user is anonymous (not authenticated)
      if (userId === 'anonymous') {
        console.log('SubscriptionContext: User not authenticated, skipping subscription check');
        setLoading(false);
        return;
      }

      // Wait a moment to ensure auth token getter is installed
      // This prevents 401 errors during app initialization
      await new Promise(resolve => setTimeout(resolve, 200));

      console.log('SubscriptionContext: Checking subscription for user:', userId);
      const response = await apiClient.get(`/api/subscription/status/${userId}`);
      const subscriptionData = response.data.data;

      console.log('SubscriptionContext: Received subscription data from backend:', subscriptionData);
      setSubscription(subscriptionData);

      // Detect plan/tier change and start a grace window (5 minutes)
      try {
        const newSignature = `${subscriptionData?.plan || ''}:${subscriptionData?.tier || ''}`;
        if (newSignature && newSignature !== planSignature) {
          console.log('SubscriptionContext: Plan change detected, starting grace window');
          setPlanSignature(newSignature);
          setGraceUntil(Date.now() + 5 * 60 * 1000);
          // Close any existing modal as plan just changed
          // BUT: Don't close usage limit modals - they're important even after plan changes
          if (showModal && !isUsageLimitModal) {
            console.log('SubscriptionContext: Plan changed, closing non-usage-limit modal');
            setShowModal(false);
            setModalErrorData(null);
          } else if (showModal && isUsageLimitModal) {
            console.log('SubscriptionContext: Plan changed but usage limit modal is open, keeping it open');
          }
        }
      } catch (_e) {}
      
      // If we have a valid subscription and the modal is open, close it
      // BUT: NEVER close usage limit modals - user needs to see they hit a limit even with active subscription
      if (subscriptionData && subscriptionData.active && showModal) {
        // Check if this is a usage limit modal (using flag or checking error data)
        const hasUsageInfo = modalErrorData?.usage_info || 
                            (modalErrorData?.current_tokens !== undefined) ||
                            (modalErrorData?.current_calls !== undefined) ||
                            (modalErrorData?.limit !== undefined) ||
                            (modalErrorData?.requested_tokens !== undefined);
        
        const isUsageLimit = isUsageLimitModal || hasUsageInfo;
        
        if (isUsageLimit) {
          console.log('SubscriptionContext: Usage limit modal detected - KEEPING OPEN (never auto-close usage limit modals)', {
            isUsageLimitModal,
            hasUsageInfo,
            modalErrorDataKeys: modalErrorData ? Object.keys(modalErrorData) : []
          });
          // Do NOT close - usage limit modals should stay open until user dismisses them
        } else {
          console.log('SubscriptionContext: Non-usage-limit modal detected, closing since subscription is active');
          setShowModal(false);
          setModalErrorData(null);
          setIsUsageLimitModal(false);
          setLastModalShowTime(0); // Reset the cooldown timer
        }
      }

      // Check if we have a deferred error to process now that we have subscription data
      if (subscriptionData && deferredError) {
        console.log('SubscriptionContext: Processing deferred error now that subscription data is available');
        const error = deferredError;
        setDeferredError(null); // Clear the deferred error

        // Re-run the error handling logic now that we have subscription data
        const status = error.response?.status;
        if (status === 429 || status === 402) {
          const now = Date.now();

          // If active, suppress modal for usage limits
          if (subscriptionData.active) {
            console.log('SubscriptionContext: Active subscription (deferred); suppressing usage-limit modal');
            return;
          }

          // For inactive subscriptions, show modal immediately
          console.log('SubscriptionContext: Showing deferred modal for inactive subscription');
          const errorData = error.response?.data || {};
          setModalErrorData({
            provider: errorData.provider,
            usage_info: errorData.usage_info,
            message: errorData.message || errorData.error
          });
          setShowModal(true);
          setLastModalShowTime(now);
        }
      }
    } catch (err: any) {
      console.error('Error checking subscription:', err);

      // Check if it's a connection error that should be handled at the app level
      if (err instanceof Error && (err.name === 'NetworkError' || err.name === 'ConnectionError')) {
        // Re-throw connection errors to be handled by the app-level error boundary
        throw err;
      }

      // Handle 401 errors gracefully during initialization - don't block routing
      // 401 might happen if auth token getter isn't ready yet
      if (err?.response?.status === 401) {
        console.warn('Subscription check failed with 401 - auth may not be ready yet, will retry later');
        setError(null); // Don't set error for 401 during init
        setLoading(false);
        // Don't throw - allow routing to proceed, subscription check will retry later
        return;
      }

      setError(err instanceof Error ? err.message : 'Failed to check subscription');

      // Don't default to free tier on error - preserve existing subscription or leave null
      // This prevents overriding correct subscription data with 'free' on temporary errors
      console.warn('Subscription check failed, preserving existing data');
    } finally {
      setLoading(false);
    }
  }, [lastCheckTime, planSignature, showModal, modalErrorData, lastModalShowTime, graceUntil, isUsageLimitModal]);

  const refreshSubscription = useCallback(async () => {
    await checkSubscription();
  }, [checkSubscription]);

  const showExpiredModal = useCallback(() => {
    setIsUsageLimitModal(false);
    setShowModal(true);
  }, []);

  const hideExpiredModal = useCallback(() => {
    console.log('SubscriptionExpiredModal: User manually closed modal');
    setShowModal(false);
    setIsUsageLimitModal(false); // Reset flag when user closes modal
    setModalErrorData(null);
  }, []);

  const handleRenewSubscription = useCallback(() => {
    // Save current location so we can return after renewal
    const currentPath = window.location.pathname;
    sessionStorage.setItem('subscription_referrer', currentPath);
    
    console.log('SubscriptionContext: Navigating to pricing page, saved referrer:', currentPath);
    window.location.href = '/pricing';
  }, []);

  // Global subscription error handler for API client
  const globalSubscriptionErrorHandler = useCallback((error: any) => {
    console.log('SubscriptionContext: Global error handler triggered', error);
    
    // Check if it's a subscription-related error
    const status = error.response?.status;
    
    if (status === 429 || status === 402) {
      console.log('SubscriptionContext: Subscription error detected');
      
      const now = Date.now();

      // Check if this is a usage limit error (status 429) vs subscription expired (402)
      let errorData = error.response?.data || {};
      
      // DEBUG: Log the raw error data structure
      console.log('SubscriptionContext: Raw error data', {
        type: typeof errorData,
        isArray: Array.isArray(errorData),
        data: errorData,
        stringified: JSON.stringify(errorData)
      });
      
      // If errorData is an array, extract the first element (common FastAPI response format)
      if (Array.isArray(errorData)) {
        console.log('SubscriptionContext: errorData is array, extracting first element');
        errorData = errorData[0] || {};
      }
      
      // Check for usage_info in various possible locations
      const usageInfo = errorData.usage_info || 
                       (errorData.current_calls !== undefined ? errorData : null) ||
                       null;
      
      // Usage limit error: 429 status with usage info OR 429 status without explicit expiration
      const isUsageLimitError = status === 429 && (usageInfo || errorData.provider || errorData.message);
      const isSubscriptionExpired = status === 402 || (status === 429 && !isUsageLimitError);
      
      console.log('SubscriptionContext: Error analysis', {
        status,
        isUsageLimitError,
        isSubscriptionExpired,
        hasUsageInfo: !!usageInfo,
        errorDataType: typeof errorData,
        errorDataKeys: typeof errorData === 'object' && !Array.isArray(errorData) ? Object.keys(errorData) : 'not-an-object',
        errorData: errorData
      });
      
      // For usage limit errors (429 with usage_info), always show modal - even for active subscriptions
      // Ignore grace window and cooldown for usage limit errors (user needs to know immediately)
      if (isUsageLimitError) {
        const modalData = {
          provider: errorData.provider || usageInfo?.provider || 'unknown',
          usage_info: usageInfo || errorData,
          message: errorData.message || errorData.error || 'You have reached your usage limit.'
        };
        
        console.log('SubscriptionContext: Usage limit exceeded, showing modal (ignoring grace window/cooldown)', {
          modalData,
          errorData: Object.keys(errorData),
          usageInfo: usageInfo ? Object.keys(usageInfo) : null
        });
        
        // Set flag to mark this as a usage limit modal (should never be auto-closed)
        setIsUsageLimitModal(true);
        setModalErrorData(modalData);
        setShowModal(true);
        setLastModalShowTime(now);
        
        console.log('SubscriptionContext: Modal state updated - showModal should be true, isUsageLimitModal = true');
        return true;
      }
      
      // For subscription expired errors, handle based on subscription status
      if (isSubscriptionExpired) {
        // If we have subscription data and it's active, this shouldn't happen but suppress anyway
        if (subscription && subscription.active) {
          console.log('SubscriptionContext: Active subscription but got expired error, suppressing modal');
          return true;
        }

        // If we don't have subscription data yet, defer the decision
        if (!subscription) {
          console.log('SubscriptionContext: No subscription data yet, deferring modal decision');
          setDeferredError(error);
          return true; // Handle the error but don't show modal yet
        }

        // If subscription is not active, show modal immediately
        if (!subscription.active) {
          console.log('SubscriptionContext: Inactive subscription, showing modal immediately');
          setIsUsageLimitModal(false);
          setModalErrorData({
            provider: errorData.provider,
            usage_info: errorData.usage_info,
            message: errorData.message || errorData.error
          });
          setShowModal(true);
          setLastModalShowTime(now);
          return true;
        }
      }
    }
    
    return false; // Not a subscription error
  }, [subscription]);

  // Register the global error handler with the API client
  // Use a ref to ensure the latest handler is always used
  const handlerRef = useRef(globalSubscriptionErrorHandler);
  useEffect(() => {
    handlerRef.current = globalSubscriptionErrorHandler;
  }, [globalSubscriptionErrorHandler]);

  useEffect(() => {
    console.log('SubscriptionContext: Registering global subscription error handler');
    setGlobalSubscriptionErrorHandler((error: any) => {
      // Always use the latest handler from ref
      return handlerRef.current(error);
    });
    
    // Cleanup: Don't remove the handler on unmount - it should persist
    // This ensures errors can still be caught even during component transitions
  }, []); // Empty deps - only register once, but handler ref updates automatically

  useEffect(() => {
    const eventHandler = (event: Event) => {
      const customEvent = event as CustomEvent;
      console.log('SubscriptionContext: Received subscription-error event fallback', customEvent.detail);
      handlerRef.current(customEvent.detail);
    };

    window.addEventListener('subscription-error', eventHandler as EventListener);
    return () => {
      window.removeEventListener('subscription-error', eventHandler as EventListener);
    };
  }, []);

  useEffect(() => {
    // Check subscription on mount
    checkSubscription();

    // Set up periodic refresh (every 5 minutes)
    const interval = setInterval(checkSubscription, 5 * 60 * 1000);

    // Listen for subscription updates
    const handleSubscriptionUpdate = () => {
      console.log('Subscription updated, refreshing...');
      checkSubscription();
    };

    // Listen for user authentication changes
    const handleUserAuth = () => {
      console.log('User authenticated, checking subscription...');
      checkSubscription();
    };

    window.addEventListener('subscription-updated', handleSubscriptionUpdate);
    window.addEventListener('user-authenticated', handleUserAuth);

    return () => {
      clearInterval(interval);
      window.removeEventListener('subscription-updated', handleSubscriptionUpdate);
      window.removeEventListener('user-authenticated', handleUserAuth);
    };
  }, []); // Remove checkSubscription dependency to prevent loop

  const value: SubscriptionContextType = {
    subscription,
    loading,
    error,
    checkSubscription,
    refreshSubscription,
    showExpiredModal,
    hideExpiredModal,
  };

  return (
    <SubscriptionContext.Provider value={value}>
      {children}
      <SubscriptionExpiredModal
        open={showModal}
        onClose={hideExpiredModal}
        onRenewSubscription={handleRenewSubscription}
        subscriptionData={subscription}
        errorData={modalErrorData}
      />
    </SubscriptionContext.Provider>
  );
};
