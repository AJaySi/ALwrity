import { useState, useCallback } from 'react';

interface BudgetTrackingState {
  totalSpent: number;
  budgetCap: number;
  operations: Array<{ id: string; cost: number; timestamp: string; description: string }>;
}

export const useBudgetTracking = (initialBudgetCap: number = 50) => {
  const [budget, setBudget] = useState<BudgetTrackingState>({
    totalSpent: 0,
    budgetCap: initialBudgetCap,
    operations: [],
  });

  const addCost = useCallback((cost: number, description: string) => {
    setBudget((prev) => {
      const newTotal = prev.totalSpent + cost;
      const operation = {
        id: `${Date.now()}_${Math.random()}`,
        cost,
        timestamp: new Date().toISOString(),
        description,
      };
      
      return {
        ...prev,
        totalSpent: newTotal,
        operations: [...prev.operations, operation],
      };
    });
  }, []);

  const setBudgetCap = useCallback((cap: number) => {
    setBudget((prev) => ({ ...prev, budgetCap: cap }));
  }, []);

  const reset = useCallback(() => {
    setBudget({
      totalSpent: 0,
      budgetCap: initialBudgetCap,
      operations: [],
    });
  }, [initialBudgetCap]);

  const canAfford = useCallback((estimatedCost: number): boolean => {
    return budget.totalSpent + estimatedCost <= budget.budgetCap;
  }, [budget.totalSpent, budget.budgetCap]);

  const getRemaining = useCallback((): number => {
    return Math.max(0, budget.budgetCap - budget.totalSpent);
  }, [budget.budgetCap, budget.totalSpent]);

  const getUsagePercentage = useCallback((): number => {
    if (budget.budgetCap === 0) return 0;
    return Math.min(100, (budget.totalSpent / budget.budgetCap) * 100);
  }, [budget.totalSpent, budget.budgetCap]);

  return {
    totalSpent: budget.totalSpent,
    budgetCap: budget.budgetCap,
    remaining: getRemaining(),
    usagePercentage: getUsagePercentage(),
    operations: budget.operations,
    addCost,
    setBudgetCap,
    canAfford,
    reset,
  };
};

