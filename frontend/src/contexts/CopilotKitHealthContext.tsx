import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

interface CopilotKitHealthState {
  isHealthy: boolean;
  isChecking: boolean;
  lastChecked: Date | null;
  errorMessage: string | null;
  retryCount: number;
  isAvailable: boolean; // Alias for isHealthy, for clearer semantics
}

interface CopilotKitHealthContextType extends CopilotKitHealthState {
  checkHealth: () => Promise<void>;
  markUnhealthy: (errorMessage?: string) => void;
  markHealthy: () => void;
  resetHealth: () => void;
}

const CopilotKitHealthContext = createContext<CopilotKitHealthContextType | undefined>(undefined);

export const useCopilotKitHealthContext = () => {
  const context = useContext(CopilotKitHealthContext);
  if (!context) {
    throw new Error('useCopilotKitHealthContext must be used within CopilotKitHealthProvider');
  }
  return context;
};

interface CopilotKitHealthProviderProps {
  children: ReactNode;
  initialHealthStatus?: boolean;
}

export const CopilotKitHealthProvider: React.FC<CopilotKitHealthProviderProps> = ({
  children,
  initialHealthStatus = true,
}) => {
  // Persist health status across page reloads to prevent manual form from disappearing
  const getInitialHealthStatus = (): boolean => {
    if (typeof window === 'undefined') return initialHealthStatus;
    try {
      const saved = localStorage.getItem('copilotkit_health_status');
      if (saved !== null) {
        return saved === 'true';
      }
    } catch (e) {
      console.warn('[CopilotKitHealthContext] Failed to read persisted health status:', e);
    }
    return initialHealthStatus;
  };

  const [state, setState] = useState<CopilotKitHealthState>({
    isHealthy: getInitialHealthStatus(),
    isChecking: false,
    lastChecked: null,
    errorMessage: null,
    retryCount: 0,
    isAvailable: getInitialHealthStatus(),
  });

  const markHealthy = useCallback(() => {
    setState((prev) => {
      const newState = {
        ...prev,
        isHealthy: true,
        isAvailable: true,
        errorMessage: null,
        retryCount: 0,
        lastChecked: new Date(),
      };
      // Persist health status to localStorage
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem('copilotkit_health_status', 'true');
        }
      } catch (e) {
        console.warn('[CopilotKitHealthContext] Failed to persist health status:', e);
      }
      return newState;
    });
  }, []);

  const markUnhealthy = useCallback((errorMessage?: string) => {
    setState((prev) => {
      const newState = {
        ...prev,
        isHealthy: false,
        isAvailable: false,
        errorMessage: errorMessage || 'CopilotKit is unavailable',
        lastChecked: new Date(),
        retryCount: prev.retryCount + 1,
      };
      // Persist health status to localStorage
      try {
        if (typeof window !== 'undefined') {
          localStorage.setItem('copilotkit_health_status', 'false');
        }
      } catch (e) {
        console.warn('[CopilotKitHealthContext] Failed to persist health status:', e);
      }
      return newState;
    });
  }, []);

  // Listen for CopilotKit error events from App.tsx
  React.useEffect(() => {
    const handleCopilotKitError = (event: Event) => {
      const customEvent = event as CustomEvent;
      const { errorMessage, isFatal, error } = customEvent.detail || {};
      
      // Always mark as unhealthy for fatal errors (CORS, SSL, 403, etc.)
      if (isFatal) {
        console.warn('[CopilotKitHealthContext] Fatal CopilotKit error detected:', errorMessage);
        markUnhealthy(errorMessage || 'CopilotKit fatal error');
      } else {
        // Check error details for CORS/network errors even if not marked as fatal
        // Safely check error strings to avoid "Cannot read properties of undefined" errors
        const errorMsg = error?.message || '';
        const errorMsgStr = typeof errorMsg === 'string' ? errorMsg.toLowerCase() : String(errorMsg || '').toLowerCase();
        const messageStr = typeof errorMessage === 'string' ? errorMessage.toLowerCase() : String(errorMessage || '').toLowerCase();
        const errorStr = errorMsgStr || messageStr || '';
        
        if (errorStr && (
          errorStr.includes('cors') || 
          errorStr.includes('failed to fetch') || 
          errorStr.includes('networkerror') ||
          errorStr.includes('network') ||
          errorStr.includes('cannot read properties')
        )) {
          console.warn('[CopilotKitHealthContext] CORS/network error detected:', errorMessage);
          markUnhealthy(errorMessage || 'CopilotKit network error');
        } else if (error?.response?.status === 504 || error?.response?.status === 502 || error?.response?.status === 500) {
          // Gateway timeout, bad gateway, or server error - mark as unavailable
          console.warn('[CopilotKitHealthContext] Gateway/server error detected:', errorMessage);
          markUnhealthy(errorMessage || 'CopilotKit gateway error');
        } else if (error?.error?.statusCode === 500 || error?.error?.code === 'UNKNOWN') {
          // Internal CopilotKit errors - mark as unavailable
          console.warn('[CopilotKitHealthContext] CopilotKit internal error detected:', errorMessage);
          markUnhealthy(errorMessage || 'CopilotKit internal error');
        } else {
          // For other transient errors, just log but don't mark as unhealthy immediately
          // Let the health check determine if it's truly down
          console.warn('[CopilotKitHealthContext] Transient CopilotKit error:', errorMessage);
        }
      }
    };

    window.addEventListener('copilotkit-error', handleCopilotKitError as EventListener);
    return () => {
      window.removeEventListener('copilotkit-error', handleCopilotKitError as EventListener);
    };
  }, [markUnhealthy]);

  const checkHealth = useCallback(async () => {
    setState((prev) => ({ ...prev, isChecking: true }));

    try {
      // Get CopilotKit API key from the same sources as App.tsx
      // Check localStorage first, then fall back to environment variable
      const savedKey = typeof window !== 'undefined' 
        ? localStorage.getItem('copilotkit_api_key') 
        : null;
      const apiKey = savedKey || process.env.REACT_APP_COPILOTKIT_API_KEY || '';
      
      // If no API key is available, mark as unhealthy and skip the check
      if (!apiKey || !apiKey.trim()) {
        markUnhealthy('CopilotKit API key not configured');
        return;
      }

      // Validate key format (must start with ck_pub_)
      if (!apiKey.startsWith('ck_pub_')) {
        markUnhealthy('CopilotKit API key format invalid (must start with ck_pub_)');
        return;
      }

      // Try to check CopilotKit status endpoint
      // This is a lightweight check that doesn't require full CopilotKit initialization
      // Use AbortController for timeout (more compatible than AbortSignal.timeout)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);
      
      try {
        const response = await fetch('https://api.cloud.copilotkit.ai/ciu', {
          method: 'GET',
          headers: {
            'x-copilotcloud-public-api-key': apiKey.trim(),
          },
          signal: controller.signal,
        });
        
        clearTimeout(timeoutId);

        if (response.ok) {
          markHealthy();
        } else {
          // Provide more specific error messages based on status code
          if (response.status === 401) {
            markUnhealthy('CopilotKit API key is invalid or unauthorized');
          } else if (response.status === 429) {
            markUnhealthy('CopilotKit rate limit exceeded');
          } else if (response.status >= 500) {
            markUnhealthy(`CopilotKit server error: ${response.status}`);
          } else {
            markUnhealthy(`CopilotKit status check failed: ${response.status}`);
          }
        }
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (error: any) {
      // Handle various error types
      let errorMsg = 'CopilotKit health check failed';
      let isCorsError = false;
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMsg = 'CopilotKit health check timed out';
      } else if (error.message?.includes('CORS') || error.message?.includes('cors')) {
        errorMsg = 'CopilotKit CORS error - service may be unavailable';
        isCorsError = true;
      } else if (error.message?.includes('Failed to fetch') || error.message?.includes('NetworkError')) {
        // Failed to fetch often indicates CORS or network issues
        errorMsg = 'CopilotKit network error - service may be down or blocked';
        isCorsError = true; // Treat as potentially unavailable
      } else if (error.message?.includes('certificate') || error.message?.includes('SSL')) {
        errorMsg = 'CopilotKit SSL certificate error';
      } else if (error.message?.includes('network') || error.message?.includes('Network')) {
        errorMsg = 'CopilotKit network error - service may be down';
      } else {
        errorMsg = error.message || 'Unknown error checking CopilotKit health';
      }

      console.warn('[CopilotKitHealthContext] Health check failed:', errorMsg, error);
      markUnhealthy(errorMsg);
    } finally {
      setState((prev) => ({ ...prev, isChecking: false }));
    }
  }, [markHealthy, markUnhealthy]);

  const resetHealth = useCallback(() => {
    setState({
      isHealthy: initialHealthStatus,
      isChecking: false,
      lastChecked: null,
      errorMessage: null,
      retryCount: 0,
      isAvailable: initialHealthStatus,
    });
  }, [initialHealthStatus]);

  const value: CopilotKitHealthContextType = {
    ...state,
    checkHealth,
    markUnhealthy,
    markHealthy,
    resetHealth,
  };

  return (
    <CopilotKitHealthContext.Provider value={value}>
      {children}
    </CopilotKitHealthContext.Provider>
  );
};

