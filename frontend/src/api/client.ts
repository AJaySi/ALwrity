import axios from 'axios';

// Global subscription error handler - will be set by the app
// Can be async to support subscription status refresh
let globalSubscriptionErrorHandler: ((error: any) => boolean | Promise<boolean>) | null = null;

export const setGlobalSubscriptionErrorHandler = (handler: (error: any) => boolean | Promise<boolean>) => {
  globalSubscriptionErrorHandler = handler;
};

// Export a function to trigger subscription error handler from outside axios interceptors
export const triggerSubscriptionError = async (error: any) => {
  const status = error?.response?.status;
  console.log('triggerSubscriptionError: Received error', {
    hasHandler: !!globalSubscriptionErrorHandler,
    status,
    dataKeys: error?.response?.data ? Object.keys(error.response.data) : null
  });

  if (globalSubscriptionErrorHandler) {
    console.log('triggerSubscriptionError: Calling global subscription error handler');
    const result = globalSubscriptionErrorHandler(error);
    // Handle both sync and async handlers
    return result instanceof Promise ? await result : result;
  }

  console.warn('triggerSubscriptionError: No global subscription error handler registered');
  return false;
};

// Authentication disabled for personal use - no token management needed

// Get API URL from environment variables
export const getApiUrl = () => {
  if (process.env.NODE_ENV === 'production') {
    // In production, use the environment variable or fallback
    return process.env.REACT_APP_API_URL || process.env.REACT_APP_BACKEND_URL;
  }
  return ''; // Use proxy in development
};

// Create a shared axios instance for all API calls
const apiBaseUrl = getApiUrl();

export const apiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 60000, // Increased to 60 seconds for regular API calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for AI operations with extended timeout
export const aiApiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 180000, // 3 minutes timeout for AI operations (matching 20-25 second responses)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for long-running operations like SEO analysis
export const longRunningApiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 300000, // 5 minutes timeout for SEO analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for polling operations with reasonable timeout
export const pollingApiClient = axios.create({
  baseURL: apiBaseUrl,
  timeout: 60000, // 60 seconds timeout for polling status checks
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  async (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Custom error types for better error handling
export class ConnectionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConnectionError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Handle network errors and timeouts (backend not available)
    if (!error.response) {
      // Network error, timeout, or backend not reachable
      const connectionError = new NetworkError(
        'Unable to connect to the backend server. Please check if the server is running.'
      );
      console.error('Network/Connection Error:', error.message || error);
      return Promise.reject(connectionError);
    }

    // Handle server errors (5xx)
    if (error.response.status >= 500) {
      const connectionError = new ConnectionError(
        'Backend server is experiencing issues. Please try again later.'
      );
      console.error('Server Error:', error.response.status, error.response.data);
      return Promise.reject(connectionError);
    }

    // Check if it's a subscription-related error and handle it globally
    if (error.response?.status === 429 || error.response?.status === 402) {
      console.log('API Client: Detected subscription error, triggering global handler');
      if (globalSubscriptionErrorHandler) {
        const result = globalSubscriptionErrorHandler(error);
        const wasHandled = result instanceof Promise ? await result : result;
        if (wasHandled) {
          console.log('API Client: Subscription error handled by global handler');
          return Promise.reject(error);
        }
      }
    }

    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for AI client
aiApiClient.interceptors.request.use(
  async (config) => {
    console.log(`Making AI ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

aiApiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Check if it's a subscription-related error and handle it globally
    if (error.response?.status === 429 || error.response?.status === 402) {
      console.log('AI API Client: Detected subscription error, triggering global handler');
      if (globalSubscriptionErrorHandler) {
        const result = globalSubscriptionErrorHandler(error);
        const wasHandled = result instanceof Promise ? await result : result;
        if (wasHandled) {
          console.log('AI API Client: Subscription error handled by global handler');
          return Promise.reject(error);
        }
      }
    }

    console.error('AI API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for long-running client
longRunningApiClient.interceptors.request.use(
  async (config) => {
    console.log(`Making long-running ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

longRunningApiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Check if it's a subscription-related error and handle it globally
    if (error.response?.status === 429 || error.response?.status === 402) {
      console.log('Long-running API Client: Detected subscription error, triggering global handler');
      if (globalSubscriptionErrorHandler) {
        const result = globalSubscriptionErrorHandler(error);
        const wasHandled = result instanceof Promise ? await result : result;
        if (wasHandled) {
          console.log('Long-running API Client: Subscription error handled by global handler');
          return Promise.reject(error);
        }
      }
    }

    console.error('Long-running API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for polling client
pollingApiClient.interceptors.request.use(
  async (config) => {
    console.log(`Making polling ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

pollingApiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    // Check if it's a subscription-related error and handle it globally
    if (error.response?.status === 429 || error.response?.status === 402) {
      if (globalSubscriptionErrorHandler) {
        const result = globalSubscriptionErrorHandler(error);
        const wasHandled = result instanceof Promise ? await result : result;
        if (!wasHandled) {
          console.warn('Polling API Client: Subscription error not handled by global handler');
        }
        // Always reject so the polling hook can also handle it
        return Promise.reject(error);
      } else {
        console.warn('Polling API Client: No global subscription error handler registered');
      }
    }

    console.error('Polling API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
); 