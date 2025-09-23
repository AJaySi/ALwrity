import { z } from 'zod';

// Core data structures for billing and usage tracking
export interface DashboardData {
  current_usage: UsageStats;
  trends: UsageTrends;
  limits: SubscriptionLimits;
  alerts: UsageAlert[];
  projections: CostProjections;
  summary: UsageSummary;
}

export interface UsageStats {
  billing_period: string;
  usage_status: 'active' | 'warning' | 'limit_reached';
  total_calls: number;
  total_tokens: number;
  total_cost: number;
  avg_response_time: number;
  error_rate: number;
  limits: SubscriptionLimits;
  provider_breakdown: ProviderBreakdown;
  alerts: UsageAlert[];
  usage_percentages: UsagePercentages;
  last_updated: string;
}

export interface ProviderBreakdown {
  gemini: ProviderUsage;
  openai: ProviderUsage;
  anthropic: ProviderUsage;
  mistral: ProviderUsage;
  tavily: ProviderUsage;
  serper: ProviderUsage;
  metaphor: ProviderUsage;
  firecrawl: ProviderUsage;
  stability: ProviderUsage;
}

export interface ProviderUsage {
  calls: number;
  tokens: number;
  cost: number;
}

export interface SubscriptionLimits {
  plan_name: string;
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  limits: {
    gemini_calls: number;
    openai_calls: number;
    anthropic_calls: number;
    mistral_calls: number;
    tavily_calls: number;
    serper_calls: number;
    metaphor_calls: number;
    firecrawl_calls: number;
    stability_calls: number;
    gemini_tokens: number;
    openai_tokens: number;
    anthropic_tokens: number;
    mistral_tokens: number;
    monthly_cost: number;
  };
  features: string[];
}

export interface UsageTrends {
  periods: string[];
  total_calls: number[];
  total_cost: number[];
  total_tokens: number[];
  provider_trends: {
    [key: string]: {
      calls: number[];
      cost: number[];
      tokens: number[];
    };
  };
}

export interface UsageAlert {
  id: number;
  type: string;
  threshold_percentage: number;
  provider?: string;
  title: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
  is_sent: boolean;
  sent_at?: string;
  is_read: boolean;
  read_at?: string;
  billing_period: string;
  created_at: string;
}

export interface CostProjections {
  projected_monthly_cost: number;
  cost_limit: number;
  projected_usage_percentage: number;
}

export interface UsageSummary {
  total_api_calls_this_month: number;
  total_cost_this_month: number;
  usage_status: string;
  unread_alerts: number;
}

export interface SubscriptionPlan {
  id: number;
  name: string;
  tier: 'free' | 'basic' | 'pro' | 'enterprise';
  price_monthly: number;
  price_yearly: number;
  description: string;
  features: string[];
  limits: {
    gemini_calls: number;
    openai_calls: number;
    anthropic_calls: number;
    mistral_calls: number;
    tavily_calls: number;
    serper_calls: number;
    metaphor_calls: number;
    firecrawl_calls: number;
    stability_calls: number;
    gemini_tokens: number;
    openai_tokens: number;
    anthropic_tokens: number;
    mistral_tokens: number;
    monthly_cost: number;
  };
}

export interface APIPricing {
  provider: string;
  model_name: string;
  cost_per_input_token: number;
  cost_per_output_token: number;
  cost_per_request: number;
  cost_per_search: number;
  cost_per_image: number;
  cost_per_page: number;
  description: string;
  effective_date: string;
}

export interface UsagePercentages {
  gemini_calls: number;
  openai_calls: number;
  anthropic_calls: number;
  mistral_calls: number;
  tavily_calls: number;
  serper_calls: number;
  metaphor_calls: number;
  firecrawl_calls: number;
  stability_calls: number;
  cost: number;
}

// Zod validation schemas
export const UsagePercentagesSchema = z.object({
  gemini_calls: z.number(),
  openai_calls: z.number(),
  anthropic_calls: z.number(),
  mistral_calls: z.number(),
  tavily_calls: z.number(),
  serper_calls: z.number(),
  metaphor_calls: z.number(),
  firecrawl_calls: z.number(),
  stability_calls: z.number(),
  cost: z.number(),
});

export const ProviderUsageSchema = z.object({
  calls: z.number(),
  tokens: z.number(),
  cost: z.number(),
});

export const ProviderBreakdownSchema = z.object({
  gemini: ProviderUsageSchema,
  openai: ProviderUsageSchema,
  anthropic: ProviderUsageSchema,
  mistral: ProviderUsageSchema,
  tavily: ProviderUsageSchema,
  serper: ProviderUsageSchema,
  metaphor: ProviderUsageSchema,
  firecrawl: ProviderUsageSchema,
  stability: ProviderUsageSchema,
});

export const SubscriptionLimitsSchema = z.object({
  plan_name: z.string(),
  tier: z.enum(['free', 'basic', 'pro', 'enterprise']),
  limits: z.object({
    gemini_calls: z.number(),
    openai_calls: z.number(),
    anthropic_calls: z.number(),
    mistral_calls: z.number(),
    tavily_calls: z.number(),
    serper_calls: z.number(),
    metaphor_calls: z.number(),
    firecrawl_calls: z.number(),
    stability_calls: z.number(),
    gemini_tokens: z.number(),
    openai_tokens: z.number(),
    anthropic_tokens: z.number(),
    mistral_tokens: z.number(),
    monthly_cost: z.number(),
  }),
  features: z.array(z.string()),
});

export const UsageAlertSchema = z.object({
  id: z.number(),
  type: z.string(),
  threshold_percentage: z.number(),
  provider: z.string().optional(),
  title: z.string(),
  message: z.string(),
  severity: z.enum(['info', 'warning', 'error']),
  is_sent: z.boolean(),
  sent_at: z.string().optional(),
  is_read: z.boolean(),
  read_at: z.string().optional(),
  billing_period: z.string(),
  created_at: z.string(),
});

export const UsageStatsSchema = z.object({
  billing_period: z.string(),
  usage_status: z.enum(['active', 'warning', 'limit_reached']),
  total_calls: z.number(),
  total_tokens: z.number(),
  total_cost: z.number(),
  avg_response_time: z.number(),
  error_rate: z.number(),
  limits: SubscriptionLimitsSchema,
  provider_breakdown: ProviderBreakdownSchema,
  alerts: z.array(UsageAlertSchema),
  usage_percentages: UsagePercentagesSchema,
  last_updated: z.string(),
});

export const DashboardDataSchema = z.object({
  current_usage: UsageStatsSchema,
  trends: z.object({
    periods: z.array(z.string()),
    total_calls: z.array(z.number()),
    total_cost: z.array(z.number()),
    total_tokens: z.array(z.number()),
    provider_trends: z.record(z.object({
      calls: z.array(z.number()),
      cost: z.array(z.number()),
      tokens: z.array(z.number()),
    })),
  }),
  limits: SubscriptionLimitsSchema,
  alerts: z.array(UsageAlertSchema),
  projections: z.object({
    projected_monthly_cost: z.number(),
    cost_limit: z.number(),
    projected_usage_percentage: z.number(),
  }),
  summary: z.object({
    total_api_calls_this_month: z.number(),
    total_cost_this_month: z.number(),
    usage_status: z.string(),
    unread_alerts: z.number(),
  }),
});

// API Response types
export interface BillingAPIResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface UsageAPIResponse extends BillingAPIResponse<UsageStats> {}
export interface DashboardAPIResponse extends BillingAPIResponse<DashboardData> {}
export interface PlansAPIResponse extends BillingAPIResponse<{ plans: SubscriptionPlan[]; total: number }> {}
export interface PricingAPIResponse extends BillingAPIResponse<{ pricing: APIPricing[]; total: number }> {}
export interface AlertsAPIResponse extends BillingAPIResponse<{ alerts: UsageAlert[]; total: number; unread_count: number }> {}
