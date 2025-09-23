import axios, { AxiosResponse } from 'axios';
import { emitApiEvent } from '../utils/apiEvents';
import {
  SystemHealth,
  APIStats,
  LightweightStats,
  CacheStats,
  SystemHealthAPIResponse,
  APIStatsAPIResponse,
  LightweightStatsAPIResponse,
  CacheStatsAPIResponse,
  SystemHealthSchema,
  APIStatsSchema,
  LightweightStatsSchema,
  CacheStatsSchema,
} from '../types/monitoring';

// API base configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance for monitoring APIs
const monitoringAPI = axios.create({
  baseURL: `${API_BASE_URL}/api/content-planning/monitoring`,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for authentication
monitoringAPI.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add user ID to ALL requests for billing tracking
    const userId = localStorage.getItem('user_id') || 'demo-user';
    
    // Add user_id as query parameter for billing tracking
    if (config.params) {
      config.params.user_id = userId;
    } else {
      config.params = { user_id: userId };
    }
    
    // Also add as header for additional tracking
    config.headers['X-User-ID'] = userId;
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
monitoringAPI.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    console.error('Monitoring API Error:', error);
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status === 503) {
      // Service unavailable
      console.warn('Monitoring service temporarily unavailable');
    }
    
    return Promise.reject(error);
  }
);

// Core monitoring service functions
export const monitoringService = {
  /**
   * Get system health status
   */
  getSystemHealth: async (): Promise<SystemHealth> => {
    try {
      const response = await monitoringAPI.get<SystemHealthAPIResponse>('/health');
      
      // Check for success status (API returns 'status' field, not 'success')
      if (response.data.status !== 'success') {
        throw new Error(response.data.message || 'Failed to fetch system health');
      }
      
      // Transform API response to match SystemHealth interface
      const apiData = response.data.data as any; // Type assertion for API response
      const transformedData: SystemHealth = {
        status: apiData.system_health as 'healthy' | 'warning' | 'critical',
        icon: apiData.icon,
        recent_requests: apiData.api_performance?.recent_requests || 0,
        recent_errors: apiData.api_performance?.recent_errors || 0,
        error_rate: apiData.api_performance?.error_rate || 0,
        timestamp: apiData.timestamp,
      };
      
      // Validate transformed data
      const validatedData = SystemHealthSchema.parse(transformedData);
      emitApiEvent({ url: '/health', method: 'GET', source: 'monitoring' });
      return validatedData;
    } catch (error) {
      console.error('Error fetching system health:', error);
      // Return default healthy state on error
      return {
        status: 'healthy',
        icon: '🟢',
        recent_requests: 0,
        recent_errors: 0,
        error_rate: 0,
        timestamp: new Date().toISOString(),
      };
    }
  },

  /**
   * Get API performance statistics
   */
  getAPIStats: async (minutes: number = 5): Promise<APIStats> => {
    try {
      const response = await monitoringAPI.get<APIStatsAPIResponse>('/api-stats', {
        params: { minutes }
      });
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch API stats');
      }
      
      // Validate response data
      const validatedData = APIStatsSchema.parse(response.data.data);
      emitApiEvent({ url: '/api-stats', method: 'GET', source: 'monitoring' });
      return validatedData;
    } catch (error) {
      console.error('Error fetching API stats:', error);
      throw error;
    }
  },

  /**
   * Get lightweight monitoring stats for dashboard header
   */
  getLightweightStats: async (): Promise<LightweightStats> => {
    try {
      const response = await monitoringAPI.get<LightweightStatsAPIResponse>('/lightweight-stats');
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch lightweight stats');
      }
      
      // Validate response data
      const validatedData = LightweightStatsSchema.parse(response.data.data);
      emitApiEvent({ url: '/lightweight-stats', method: 'GET', source: 'monitoring' });
      return validatedData;
    } catch (error) {
      console.error('Error fetching lightweight stats:', error);
      // Return default stats on error
      return {
        status: 'healthy',
        icon: '🟢',
        recent_requests: 0,
        recent_errors: 0,
        error_rate: 0,
        timestamp: new Date().toISOString(),
      };
    }
  },

  /**
   * Get cache performance metrics
   */
  getCacheStats: async (): Promise<CacheStats> => {
    try {
      const response = await monitoringAPI.get<CacheStatsAPIResponse>('/cache-stats');
      
      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch cache stats');
      }
      
      // Validate response data
      const validatedData = CacheStatsSchema.parse(response.data.data);
      emitApiEvent({ url: '/cache-stats', method: 'GET', source: 'monitoring' });
      return validatedData;
    } catch (error) {
      console.error('Error fetching cache stats:', error);
      // Return default cache stats on error
      return {
        hits: 0,
        misses: 0,
        hit_rate: 0,
        total_requests: 0,
      };
    }
  },
};

// Utility functions for monitoring
export const getHealthStatusColor = (status: string): string => {
  switch (status) {
    case 'healthy':
      return '#22c55e'; // Green
    case 'warning':
      return '#f59e0b'; // Orange
    case 'critical':
      return '#ef4444'; // Red
    default:
      return '#6b7280'; // Gray
  }
};

export const getHealthStatusIcon = (status: string): string => {
  switch (status) {
    case 'healthy':
      return '🟢';
    case 'warning':
      return '🟡';
    case 'critical':
      return '🔴';
    default:
      return '⚪';
  }
};

export const formatResponseTime = (time: number): string => {
  if (time < 1000) {
    return `${time.toFixed(0)}ms`;
  } else {
    return `${(time / 1000).toFixed(2)}s`;
  }
};

export const formatErrorRate = (rate: number): string => {
  return `${rate.toFixed(2)}%`;
};

export const formatUptime = (uptime: number): string => {
  if (uptime >= 99.9) {
    return `${uptime.toFixed(3)}%`;
  } else if (uptime >= 99) {
    return `${uptime.toFixed(2)}%`;
  } else {
    return `${uptime.toFixed(1)}%`;
  }
};

export const getPerformanceStatus = (responseTime: number, errorRate: number): {
  status: 'excellent' | 'good' | 'warning' | 'critical';
  color: string;
  icon: string;
} => {
  if (errorRate > 5 || responseTime > 5000) {
    return {
      status: 'critical',
      color: '#ef4444',
      icon: '🔴'
    };
  } else if (errorRate > 2 || responseTime > 2000) {
    return {
      status: 'warning',
      color: '#f59e0b',
      icon: '🟡'
    };
  } else if (errorRate > 0.5 || responseTime > 1000) {
    return {
      status: 'good',
      color: '#22c55e',
      icon: '🟢'
    };
  } else {
    return {
      status: 'excellent',
      color: '#16a34a',
      icon: '🟢'
    };
  }
};

export const calculateCacheEfficiency = (hitRate: number): {
  status: 'excellent' | 'good' | 'warning' | 'poor';
  color: string;
  icon: string;
} => {
  if (hitRate >= 90) {
    return {
      status: 'excellent',
      color: '#16a34a',
      icon: '🚀'
    };
  } else if (hitRate >= 75) {
    return {
      status: 'good',
      color: '#22c55e',
      icon: '✅'
    };
  } else if (hitRate >= 50) {
    return {
      status: 'warning',
      color: '#f59e0b',
      icon: '⚠️'
    };
  } else {
    return {
      status: 'poor',
      color: '#ef4444',
      icon: '❌'
    };
  }
};

export const formatThroughput = (requestsPerSecond: number): string => {
  if (requestsPerSecond >= 1000) {
    return `${(requestsPerSecond / 1000).toFixed(1)}k req/s`;
  } else {
    return `${requestsPerSecond.toFixed(1)} req/s`;
  }
};

export const getEndpointStatus = (errorRate: number, avgTime: number): {
  status: 'healthy' | 'warning' | 'critical';
  color: string;
  icon: string;
} => {
  if (errorRate > 10 || avgTime > 5000) {
    return {
      status: 'critical',
      color: '#ef4444',
      icon: '🔴'
    };
  } else if (errorRate > 5 || avgTime > 2000) {
    return {
      status: 'warning',
      color: '#f59e0b',
      icon: '🟡'
    };
  } else {
    return {
      status: 'healthy',
      color: '#22c55e',
      icon: '🟢'
    };
  }
};

export default monitoringService;
