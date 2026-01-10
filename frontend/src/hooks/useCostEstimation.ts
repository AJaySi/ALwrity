import { useState, useCallback } from 'react';
import { PreflightOperation } from '../services/billingService';

interface UseCostEstimationReturn {
  showEstimation: (operations: PreflightOperation[]) => void;
  estimationOperations: PreflightOperation[];
  isEstimationOpen: boolean;
  closeEstimation: () => void;
}

/**
 * Hook for cost estimation before operations.
 * 
 * Usage:
 * ```tsx
 * const { showEstimation, estimationOperations, isEstimationOpen, closeEstimation } = useCostEstimation();
 * 
 * const handleGenerate = () => {
 *   showEstimation([
 *     {
 *       provider: 'gemini',
 *       model: 'gemini-2.5-flash',
 *       operation_type: 'text_generation',
 *       tokens_requested: 2000
 *     }
 *   ]);
 * };
 * 
 * <CostEstimationModal
 *   open={isEstimationOpen}
 *   onClose={closeEstimation}
 *   onConfirm={() => {
 *     // Proceed with actual operation
 *     performOperation();
 *   }}
 *   operations={estimationOperations}
 * />
 * ```
 */
export const useCostEstimation = (): UseCostEstimationReturn => {
  const [isEstimationOpen, setIsEstimationOpen] = useState(false);
  const [estimationOperations, setEstimationOperations] = useState<PreflightOperation[]>([]);

  const showEstimation = useCallback((operations: PreflightOperation[]) => {
    setEstimationOperations(operations);
    setIsEstimationOpen(true);
  }, []);

  const closeEstimation = useCallback(() => {
    setIsEstimationOpen(false);
    setEstimationOperations([]);
  }, []);

  return {
    showEstimation,
    estimationOperations,
    isEstimationOpen,
    closeEstimation,
  };
};

export default useCostEstimation;
