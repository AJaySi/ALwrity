import { useState, useCallback, useRef, useEffect } from 'react';
import {
  checkPreflight,
  PreflightOperation,
  PreflightCheckResponse,
  PreflightLimitInfo,
} from '../services/billingService';

export interface UsePreflightCheckOptions {
  operation: PreflightOperation;
  enabled?: boolean; // Whether to perform check on hover
  debounceMs?: number; // Debounce delay (default: 300ms)
  cacheTtl?: number; // Cache TTL in ms (default: 5000ms)
}

export interface UsePreflightCheckResult {
  canProceed: boolean;
  estimatedCost: number;
  limitInfo: PreflightLimitInfo | null;
  loading: boolean;
  error: string | null;
  checkOnHover: () => void;
  checkNow: () => void; // Immediate check
  reset: () => void;
}

interface CacheEntry {
  data: PreflightCheckResponse;
  timestamp: number;
}

/**
 * React hook for pre-flight checking operations with cost estimation.
 * 
 * Features:
 * - Debounced hover checks (300ms default)
 * - In-memory caching (5s default TTL)
 * - Request cancellation on unmount
 */
export const usePreflightCheck = (
  options: UsePreflightCheckOptions
): UsePreflightCheckResult => {
  const {
    operation,
    enabled = true,
    debounceMs = 300,
    cacheTtl = 5000,
  } = options;

  const [canProceed, setCanProceed] = useState<boolean>(true);
  const [estimatedCost, setEstimatedCost] = useState<number>(0);
  const [limitInfo, setLimitInfo] = useState<PreflightLimitInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Cache for pre-flight check results
  const cacheRef = useRef<Map<string, CacheEntry>>(new Map());
  
  // Debounce timer ref
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Abort controller for request cancellation
  const abortControllerRef = useRef<AbortController | null>(null);

  // Generate cache key from operation
  const getCacheKey = useCallback(() => {
    return JSON.stringify(operation);
  }, [operation]);

  // Check if cached result is still valid
  const getCachedResult = useCallback((): PreflightCheckResponse | null => {
    const cacheKey = getCacheKey();
    const cached = cacheRef.current.get(cacheKey);
    
    if (cached) {
      const age = Date.now() - cached.timestamp;
      if (age < cacheTtl) {
        return cached.data;
      }
      // Cache expired, remove it
      cacheRef.current.delete(cacheKey);
    }
    
    return null;
  }, [getCacheKey, cacheTtl]);

  // Store result in cache
  const setCache = useCallback((data: PreflightCheckResponse) => {
    const cacheKey = getCacheKey();
    cacheRef.current.set(cacheKey, {
      data,
      timestamp: Date.now(),
    });
  }, [getCacheKey]);

  // Perform actual pre-flight check
  const performCheck = useCallback(async (): Promise<void> => {
    if (!enabled) {
      return;
    }

    // Check cache first
    const cached = getCachedResult();
    if (cached) {
      updateState(cached);
      return;
    }

    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();
    const currentAbortController = abortControllerRef.current;

    setLoading(true);
    setError(null);

    try {
      const response = await checkPreflight(operation);
      
      // Check if request was cancelled
      if (currentAbortController.signal.aborted) {
        return;
      }

      // Cache the result
      setCache(response);

      // Update state
      updateState(response);
    } catch (err: any) {
      // Check if request was cancelled
      if (currentAbortController.signal.aborted) {
        return;
      }

      const errorMessage = err?.message || 'Pre-flight check failed';
      setError(errorMessage);
      setCanProceed(false);
      setEstimatedCost(0);
      setLimitInfo(null);
    } finally {
      if (!currentAbortController.signal.aborted) {
        setLoading(false);
      }
    }
  }, [operation, enabled, getCachedResult, setCache]);

  // Update state from response
  const updateState = useCallback((response: PreflightCheckResponse) => {
    setCanProceed(response.can_proceed);
    setEstimatedCost(response.estimated_cost);
    
    // Get limit info from first operation (for single operation checks)
    const firstOp = response.operations[0];
    if (firstOp) {
      setLimitInfo(firstOp.limit_info);
      if (!response.can_proceed && firstOp.message) {
        setError(firstOp.message);
      } else {
        setError(null);
      }
    } else {
      setLimitInfo(null);
    }
  }, []);

  // Debounced check for hover events
  const checkOnHover = useCallback(() => {
    if (!enabled) {
      return;
    }

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Check cache first (no debounce for cache hits)
    const cached = getCachedResult();
    if (cached) {
      updateState(cached);
      return;
    }

    // Debounce the actual API call
    debounceTimerRef.current = setTimeout(() => {
      performCheck();
    }, debounceMs);
  }, [enabled, debounceMs, getCachedResult, updateState, performCheck]);

  // Immediate check (no debounce)
  const checkNow = useCallback(() => {
    if (!enabled) {
      return;
    }

    // Clear any pending debounced check
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }

    performCheck();
  }, [enabled, performCheck]);

  // Reset state
  const reset = useCallback(() => {
    setCanProceed(true);
    setEstimatedCost(0);
    setLimitInfo(null);
    setLoading(false);
    setError(null);

    // Clear debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
      debounceTimerRef.current = null;
    }

    // Cancel any in-flight request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      // Clear debounce timer
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }

      // Cancel any in-flight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    canProceed,
    estimatedCost,
    limitInfo,
    loading,
    error,
    checkOnHover,
    checkNow,
    reset,
  };
};

