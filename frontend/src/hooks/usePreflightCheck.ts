import { useState, useCallback } from 'react';
import { checkPreflight, PreflightOperation, PreflightCheckResponse } from '../services/billingService';

export interface UsePreflightCheckOptions {
  onBlocked?: (response: PreflightCheckResponse) => void;
  onAllowed?: (response: PreflightCheckResponse) => void;
}

export const usePreflightCheck = (options?: UsePreflightCheckOptions) => {
  const [isChecking, setIsChecking] = useState(false);
  const [lastCheck, setLastCheck] = useState<PreflightCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const check = useCallback(async (operation: PreflightOperation): Promise<PreflightCheckResponse> => {
    setIsChecking(true);
    setError(null);
    
    try {
      const response = await checkPreflight(operation);
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
