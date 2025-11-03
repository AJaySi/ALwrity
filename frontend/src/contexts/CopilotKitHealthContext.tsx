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
  const [state, setState] = useState<CopilotKitHealthState>({
    isHealthy: initialHealthStatus,
    isChecking: false,
    lastChecked: null,
    errorMessage: null,
    retryCount: 0,
    isAvailable: initialHealthStatus,
  });

  const markHealthy = useCallback(() => {
    setState((prev) => ({
      ...prev,
      isHealthy: true,
      isAvailable: true,
      errorMessage: null,
      retryCount: 0,
      lastChecked: new Date(),
    }));
  }, []);

  const markUnhealthy = useCallback((errorMessage?: string) => {
    setState((prev) => ({
      ...prev,
      isHealthy: false,
      isAvailable: false,
      errorMessage: errorMessage || 'CopilotKit is unavailable',
      lastChecked: new Date(),
      retryCount: prev.retryCount + 1,
    }));
  }, []);

  // Listen for CopilotKit error events from App.tsx
  React.useEffect(() => {
    const handleCopilotKitError = (event: Event) => {
      const customEvent = event as CustomEvent;
      const { errorMessage, isFatal } = customEvent.detail || {};
      
      if (isFatal) {
        markUnhealthy(errorMessage || 'CopilotKit fatal error');
      } else {
        // For transient errors, just log but don't mark as unhealthy immediately
        // Let the health check determine if it's truly down
        console.warn('CopilotKit transient error:', errorMessage);
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
      // Try to check CopilotKit status endpoint
      // This is a lightweight check that doesn't require full CopilotKit initialization
      const response = await fetch('https://api.cloud.copilotkit.ai/ciu', {
        method: 'GET',
        headers: {
          'x-copilotcloud-public-api-key': process.env.REACT_APP_COPILOTKIT_PUBLIC_API_KEY || '',
        },
        // Use a short timeout to avoid blocking
        signal: AbortSignal.timeout(3000),
      });

      if (response.ok) {
        markHealthy();
      } else {
        markUnhealthy(`CopilotKit status check failed: ${response.status}`);
      }
    } catch (error: any) {
      // Handle various error types
      let errorMsg = 'CopilotKit health check failed';
      
      if (error.name === 'AbortError' || error.name === 'TimeoutError') {
        errorMsg = 'CopilotKit health check timed out';
      } else if (error.message?.includes('CORS')) {
        errorMsg = 'CopilotKit CORS error - service may be unavailable';
      } else if (error.message?.includes('certificate') || error.message?.includes('SSL')) {
        errorMsg = 'CopilotKit SSL certificate error';
      } else if (error.message?.includes('network') || error.message?.includes('Failed to fetch')) {
        errorMsg = 'CopilotKit network error - service may be down';
      } else {
        errorMsg = error.message || 'Unknown error checking CopilotKit health';
      }

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

