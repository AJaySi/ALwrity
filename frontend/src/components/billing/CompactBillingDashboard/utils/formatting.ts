/**
 * Formatting utilities for CompactBillingDashboard
 */

export const formatCurrency = (amount: number): string => `$${amount.toFixed(4)}`;

export const formatNumber = (num: number): string => num.toLocaleString();
