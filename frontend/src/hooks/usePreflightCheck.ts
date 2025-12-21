import { useState, useCallback, useRef } from 'react';
import { checkPreflight, PreflightOperation, PreflightCheckResponse } from '../services/billingService';

export interface UsePreflightCheckOptions {
  onBlocked?: (response: PreflightCheckResponse) => void;
  onAllowed?: (response: PreflightCheckResponse) => void;
}

// Global cache for preflight checks to prevent duplicate API calls
const preflightCache = new Map<string, { response: PreflightCheckResponse; timestamp: number }>();
const CACHE_TTL = 30000; // 30 seconds cache TTL

// Generate cache key from operation
const getCacheKey = (operation: PreflightOperation): string => {
  return `${operation.provider}_${operation.operation_type}_${operation.tokens_requested || 0}`;
};

// Check if cached response is still valid
const isCacheValid = (timestamp: number): boolean => {
  return Date.now() - timestamp < CACHE_TTL;
};

export const usePreflightCheck = (options?: UsePreflightCheckOptions) => {
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState<PreflightCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const checkingRef = useRef<Set<string>>(new Set()); // Track ongoing checks to prevent duplicates

  const check = useCallback(async (operation: PreflightOperation): Promise<PreflightCheckResponse> => {
    const cacheKey = getCacheKey(operation);
    
    // Check cache first
    const cached = preflightCache.get(cacheKey);
    if (cached && isCacheValid(cached.timestamp)) {
      setLastCheck(cached.response);
      return cached.response;
    }
    
    // Prevent duplicate concurrent checks for the same operation
    if (checkingRef.current.has(cacheKey)) {
      // Wait for existing check to complete
      return new Promise((resolve) => {
        const checkInterval = setInterval(() => {
          const cached = preflightCache.get(cacheKey);
          if (cached && isCacheValid(cached.timestamp)) {
            clearInterval(checkInterval);
            setLastCheck(cached.response);
            resolve(cached.response);
          }
        }, 100);
        
        // Timeout after 5 seconds
        setTimeout(() => {
          clearInterval(checkInterval);
          resolve({
            can_proceed: true,
            estimated_cost: 0,
            operations: [],
            total_cost: 0,
            usage_summary: null,
            cached: false,
          } as PreflightCheckResponse);
        }, 5000);
      });
    }
    
    checkingRef.current.add(cacheKey);
    setIsChecking(true);
    setError(null);
    
    try {
      const response = await checkPreflight(operation);
      
      // Cache the response
      preflightCache.set(cacheKey, {
        response,
        timestamp: Date.now(),
      });
      
      setLastCheck(response);
      
      if (!response.can_proceed) {
        setError(response.operations[0]?.message || 'Operation blocked by subscription limits');
        options?.onBlocked?.(response);
      } else {
        options?.onAllowed?.(response);
      }
      
      return response;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err?.message || 'Preflight check failed';
      setError(errorMessage);
      
      // Return blocked response on error
      const blockedResponse: PreflightCheckResponse = {
        can_proceed: false,
        estimated_cost: 0,
        operations: [{
          provider: operation.provider,
          operation_type: operation.operation_type,
          cost: 0,
          allowed: false,
          limit_info: null,
          message: errorMessage,
        }],
        total_cost: 0,
        usage_summary: null,
        cached: false,
      };
      
      setLastCheck(blockedResponse);
      options?.onBlocked?.(blockedResponse);
      return blockedResponse;
    } finally {
      setIsChecking(false);
      checkingRef.current.delete(cacheKey);
    }
  }, [options]);

  // Extract useful properties from lastCheck
  const estimatedCost = lastCheck?.estimated_cost ?? 0;
  const limitInfo = lastCheck?.operations?.[0]?.limit_info ?? null;

  return {
    check,
    isChecking,
    lastCheck,
    error,
    canProceed: lastCheck?.can_proceed ?? null,
    estimatedCost,
    limitInfo,
    loading: isChecking,
    // For backward compatibility with OperationButton
    checkOnHover: () => {}, // No-op for now, can be implemented if needed
    checkNow: () => check(lastCheck?.operations?.[0] ? {
      provider: lastCheck.operations[0].provider,
      operation_type: lastCheck.operations[0].operation_type,
    } as PreflightOperation : {
      provider: 'gemini',
      operation_type: 'unknown',
    }),
  };
};
