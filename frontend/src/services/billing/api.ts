/**
 * Billing API Client
 * HTTP client for billing API requests with authentication and error handling
 */

import axios, { AxiosResponse } from 'axios';
import { getApiUrl } from '../../api/client';

// Create axios instance with default config
const BILLING_BASE_URL = getApiUrl()
  ? `${getApiUrl().replace(/\/+$/, '')}/api/subscription`
  : '/api/subscription';

// Create axios instance with security configurations
const billingAPI = axios.create({
  baseURL: BILLING_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
  // Security: Limit request size to 1MB
  maxContentLength: 1024 * 1024, // 1MB
  maxBodyLength: 1024 * 1024, // 1MB
});

// Optional token getter - will be set by App.tsx when Clerk is available
let authTokenGetter: (() => Promise<string | null>) | null = null;

// Export function to set auth token getter (called from App.tsx)
export const setBillingAuthTokenGetter = (getter: (() => Promise<string | null>)) => {
  authTokenGetter = getter;
};

// Request interceptor for authentication
billingAPI.interceptors.request.use(
  async (config) => {
    if (authTokenGetter) {
      try {
        const token = await authTokenGetter();
        if (token) {
          config.headers = {
            ...config.headers,
            Authorization: `Bearer ${token}`,
          } as any;
        }
      } catch (tokenError) {
        console.error('Billing API: Error getting auth token:', tokenError);
      }
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for enhanced error handling and sanitization
billingAPI.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle network errors
    if (!error.response) {
      console.error('Billing API Network Error:', error.message);
      return Promise.reject(new Error('Network connection failed. Please check your internet connection.'));
    }
    
    // Handle 401 errors - try to refresh token
    if (error?.response?.status === 401 && !originalRequest._retry && authTokenGetter) {
      originalRequest._retry = true;
      
      try {
        const newToken = await authTokenGetter();
        if (newToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return billingAPI(originalRequest);
        }
      } catch (retryError) {
        console.error('Billing API: Token refresh failed:', retryError);
      }
    }
    
    // Enhanced error sanitization
    let sanitizedError = error;
    
    switch (error?.response?.status) {
      case 400:
        sanitizedError = new Error('Invalid request. Please check your input and try again.');
        break;
      case 401:
        sanitizedError = new Error('Authentication required. Please log in again.');
        break;
      case 403:
        sanitizedError = new Error('Access denied. You do not have permission to perform this action.');
        break;
      case 404:
        sanitizedError = new Error('Resource not found. Please check your request and try again.');
        break;
      case 429:
        sanitizedError = new Error('Too many requests. Please wait a moment and try again.');
        break;
      case 500:
        sanitizedError = new Error('Server error. Please try again later.');
        break;
      case 502:
      case 503:
      case 504:
        sanitizedError = new Error('Service temporarily unavailable. Please try again later.');
        break;
      default:
        sanitizedError = new Error(error.response?.data?.detail || error.message || 'An unexpected error occurred.');
    }
    
    console.error('Billing API Error:', {
      status: error?.response?.status,
      message: error.message,
      url: originalRequest?.url,
      method: originalRequest?.method
    });
    
    return Promise.reject(sanitizedError);
  }
);

// Export the configured API instance
export { billingAPI };
