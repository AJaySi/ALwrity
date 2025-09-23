import { z } from 'zod';

// System health and monitoring types
export interface SystemHealth {
  status: 'healthy' | 'warning' | 'critical';
  icon: string;
  recent_requests: number;
  recent_errors: number;
  error_rate: number;
  timestamp: string;
}

export interface APIStats {
  timestamp: string;
  overview: {
    total_requests: number;
    total_errors: number;
    recent_requests: number;
    recent_errors: number;
  };
  cache_performance: {
    hits: number;
    misses: number;
    hit_rate: number;
  };
  top_endpoints: APIEndpointStats[];
  recent_errors: APIError[];
  system_health: {
    status: 'healthy' | 'warning' | 'critical';
    error_rate: number;
  };
}

export interface APIEndpointStats {
  endpoint: string;
  count: number;
  avg_time: number;
  errors: number;
  last_called: string | null;
  cache_hit_rate: number;
}

export interface APIError {
  timestamp: string;
  path: string;
  method: string;
  status_code: number;
  duration: number;
}

export interface LightweightStats {
  status: 'healthy' | 'warning' | 'critical';
  icon: string;
  recent_requests: number;
  recent_errors: number;
  error_rate: number;
  timestamp: string;
}

export interface CacheStats {
  hits: number;
  misses: number;
  hit_rate: number;
  total_requests: number;
}

// Performance metrics
export interface PerformanceMetrics {
  response_time: {
    average: number;
    p95: number;
    p99: number;
  };
  throughput: {
    requests_per_second: number;
    requests_per_minute: number;
  };
  error_rate: number;
  uptime: number;
}

// External API monitoring
export interface ExternalAPIMetrics {
  provider: string;
  calls: number;
  cost: number;
  avg_response_time: number;
  error_rate: number;
  last_updated: string;
}

// Zod validation schemas
export const SystemHealthSchema = z.object({
  status: z.enum(['healthy', 'warning', 'critical']),
  icon: z.string(),
  recent_requests: z.number(),
  recent_errors: z.number(),
  error_rate: z.number(),
  timestamp: z.string(),
});

export const APIEndpointStatsSchema = z.object({
  endpoint: z.string(),
  count: z.number(),
  avg_time: z.number(),
  errors: z.number(),
  last_called: z.string().nullable(),
  cache_hit_rate: z.number(),
});

export const APIErrorSchema = z.object({
  timestamp: z.string(),
  path: z.string(),
  method: z.string(),
  status_code: z.number(),
  duration: z.number(),
});

export const APIStatsSchema = z.object({
  timestamp: z.string(),
  overview: z.object({
    total_requests: z.number(),
    total_errors: z.number(),
    recent_requests: z.number(),
    recent_errors: z.number(),
  }),
  cache_performance: z.object({
    hits: z.number(),
    misses: z.number(),
    hit_rate: z.number(),
  }),
  top_endpoints: z.array(APIEndpointStatsSchema),
  recent_errors: z.array(APIErrorSchema),
  system_health: z.object({
    status: z.enum(['healthy', 'warning', 'critical']),
    error_rate: z.number(),
  }),
});

export const LightweightStatsSchema = z.object({
  status: z.enum(['healthy', 'warning', 'critical']),
  icon: z.string(),
  recent_requests: z.number(),
  recent_errors: z.number(),
  error_rate: z.number(),
  timestamp: z.string(),
});

export const CacheStatsSchema = z.object({
  hits: z.number(),
  misses: z.number(),
  hit_rate: z.number(),
  total_requests: z.number(),
});

export const PerformanceMetricsSchema = z.object({
  response_time: z.object({
    average: z.number(),
    p95: z.number(),
    p99: z.number(),
  }),
  throughput: z.object({
    requests_per_second: z.number(),
    requests_per_minute: z.number(),
  }),
  error_rate: z.number(),
  uptime: z.number(),
});

export const ExternalAPIMetricsSchema = z.object({
  provider: z.string(),
  calls: z.number(),
  cost: z.number(),
  avg_response_time: z.number(),
  error_rate: z.number(),
  last_updated: z.string(),
});

// API Response types
export interface MonitoringAPIResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

export interface SystemHealthAPIResponse {
  status: string;
  data: SystemHealth;
  message?: string;
}
export interface APIStatsAPIResponse extends MonitoringAPIResponse<APIStats> {}
export interface LightweightStatsAPIResponse extends MonitoringAPIResponse<LightweightStats> {}
export interface CacheStatsAPIResponse extends MonitoringAPIResponse<CacheStats> {}
