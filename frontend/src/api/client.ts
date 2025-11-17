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

// Optional token getter installed from within the app after Clerk is available
let authTokenGetter: (() => Promise<string | null>) | null = null;

// Optional Clerk sign-out function - set by App.tsx when Clerk is available
let clerkSignOut: (() => Promise<void>) | null = null;

export const setClerkSignOut = (signOutFn: () => Promise<void>) => {
  clerkSignOut = signOutFn;
};

export const setAuthTokenGetter = (getter: () => Promise<string | null>) => {
  authTokenGetter = getter;
};

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

// Add request interceptor for logging (optional)
apiClient.interceptors.request.use(
  async (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    try {
      if (!authTokenGetter) {
        console.warn(`[apiClient] ⚠️ authTokenGetter not set for ${config.url} - request may fail authentication`);
        console.warn(`[apiClient] This usually means TokenInstaller hasn't run yet. Request will likely fail with 401.`);
      } else {
        try {
          const token = await authTokenGetter();
      if (token) {
        config.headers = config.headers || {};
        (config.headers as any)['Authorization'] = `Bearer ${token}`;
            console.log(`[apiClient] ✅ Added auth token to request: ${config.url}`);
          } else {
            console.warn(`[apiClient] ⚠️ authTokenGetter returned null for ${config.url} - user may not be signed in`);
            console.warn(`[apiClient] User ID from localStorage: ${localStorage.getItem('user_id') || 'none'}`);
          }
        } catch (tokenError) {
          console.error(`[apiClient] ❌ Error getting auth token for ${config.url}:`, tokenError);
        }
      }
    } catch (e) {
      console.error(`[apiClient] ❌ Unexpected error in request interceptor for ${config.url}:`, e);
      // non-fatal - let the request proceed, backend will return 401 if needed
    }
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

// Add response interceptor with automatic token refresh on 401
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

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

    // If 401 and we haven't retried yet, try to refresh token and retry
    if (error?.response?.status === 401 && !originalRequest._retry && authTokenGetter) {
      originalRequest._retry = true;

      try {
        // Get fresh token
        const newToken = await authTokenGetter();
        if (newToken) {
          // Update the request with new token
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          // Retry the request
          return apiClient(originalRequest);
        }
      } catch (retryError) {
        console.error('Token refresh failed:', retryError);
      }

      // If retry failed, token is expired - sign out user and redirect to sign in
      const isOnboardingRoute = window.location.pathname.includes('/onboarding');
      const isRootRoute = window.location.pathname === '/';
      
      // Don't redirect from root route during app initialization - allow InitialRouteHandler to work
      if (!isRootRoute && !isOnboardingRoute) {
        // Token expired - sign out user and redirect to landing/sign-in
        console.warn('401 Unauthorized - token expired, signing out user');
        
        // Clear any cached auth data
        localStorage.removeItem('user_id');
        localStorage.removeItem('auth_token');
        
        // Use Clerk signOut if available, otherwise just redirect
        if (clerkSignOut) {
          clerkSignOut()
            .then(() => {
              // Redirect to landing page after sign out
              window.location.assign('/');
            })
            .catch((err) => {
              console.error('Error during Clerk sign out:', err);
              // Fallback: redirect anyway
              window.location.assign('/');
            });
        } else {
          // Fallback: redirect to landing (will show sign-in if Clerk handles it)
          window.location.assign('/');
        }
      } else {
        console.warn('401 Unauthorized - token refresh failed (during initialization, not redirecting)');
      }
    }

    // Handle 401 errors that weren't retried (e.g., no authTokenGetter, already retried, etc.)
    if (error?.response?.status === 401 && (originalRequest._retry || !authTokenGetter)) {
      const isOnboardingRoute = window.location.pathname.includes('/onboarding');
      const isRootRoute = window.location.pathname === '/';
      
      if (!isRootRoute && !isOnboardingRoute) {
        // Token expired - sign out user and redirect
        console.warn('401 Unauthorized - token expired (not retried), signing out user');
        localStorage.removeItem('user_id');
        localStorage.removeItem('auth_token');
        
        if (clerkSignOut) {
          clerkSignOut()
            .then(() => window.location.assign('/'))
            .catch(() => window.location.assign('/'));
        } else {
          window.location.assign('/');
        }
      }
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
    try {
      const token = authTokenGetter ? await authTokenGetter() : null;
      if (token) {
        config.headers = config.headers || {};
        (config.headers as any)['Authorization'] = `Bearer ${token}`;
      }
    } catch (e) {}
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
    const originalRequest = error.config;
    
    // If 401 and we haven't retried yet, try to refresh token and retry
    if (error?.response?.status === 401 && !originalRequest._retry && authTokenGetter) {
      originalRequest._retry = true;
      
      try {
        const newToken = await authTokenGetter();
        if (newToken) {
          originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
          return aiApiClient(originalRequest);
        }
      } catch (retryError) {
        console.error('Token refresh failed:', retryError);
      }
      
      const isOnboardingRoute = window.location.pathname.includes('/onboarding');
      const isRootRoute = window.location.pathname === '/';
      
      // Don't redirect from root route during app initialization
      if (!isRootRoute && !isOnboardingRoute) {
        // Token expired - sign out user and redirect
        console.warn('401 Unauthorized - token expired, signing out user');
        localStorage.removeItem('user_id');
        localStorage.removeItem('auth_token');
        
        if (clerkSignOut) {
          clerkSignOut()
            .then(() => window.location.assign('/'))
            .catch(() => window.location.assign('/'));
        } else {
          window.location.assign('/');
        }
      } else {
        console.warn('401 Unauthorized - token refresh failed (during initialization, not redirecting)');
      }
    }
    
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
    try {
      const token = authTokenGetter ? await authTokenGetter() : null;
      if (token) {
        config.headers = config.headers || {};
        (config.headers as any)['Authorization'] = `Bearer ${token}`;
      }
    } catch (e) {}
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
    if (error?.response?.status === 401) {
      // Only redirect on 401 if we're not in onboarding flow or root route
      const isOnboardingRoute = window.location.pathname.includes('/onboarding');
      const isRootRoute = window.location.pathname === '/';
      
      // Don't redirect from root route during app initialization
      if (!isRootRoute && !isOnboardingRoute) {
        try { window.location.assign('/'); } catch {}
      } else {
        console.warn('401 Unauthorized during initialization - token may need refresh (not redirecting)');
      }
    }
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
    try {
      const token = authTokenGetter ? await authTokenGetter() : null;
      if (token) {
        config.headers = config.headers || {};
        (config.headers as any)['Authorization'] = `Bearer ${token}`;
      }
    } catch (e) {}
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
    if (error?.response?.status === 401) {
      // Only redirect on 401 if we're not in onboarding flow or root route
      const isOnboardingRoute = window.location.pathname.includes('/onboarding');
      const isRootRoute = window.location.pathname === '/';
      
      // Don't redirect from root route during app initialization
      if (!isRootRoute && !isOnboardingRoute) {
        try { window.location.assign('/'); } catch {}
      } else {
        console.warn('401 Unauthorized during initialization - token may need refresh (not redirecting)');
      }
    }
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