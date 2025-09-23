import axios from 'axios';

// Create a shared axios instance for all API calls
export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // Increased to 60 seconds for regular API calls
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for AI operations with extended timeout
export const aiApiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 180000, // 3 minutes timeout for AI operations (matching 20-25 second responses)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for long-running operations like SEO analysis
export const longRunningApiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 300000, // 5 minutes timeout for SEO analysis
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create a specialized client for polling operations with reasonable timeout
export const pollingApiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 60000, // 60 seconds timeout for polling status checks
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging (optional)
apiClient.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling (optional)
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for AI client
aiApiClient.interceptors.request.use(
  (config) => {
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
  (error) => {
    console.error('AI API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for long-running client
longRunningApiClient.interceptors.request.use(
  (config) => {
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
  (error) => {
    console.error('Long-running API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
);

// Add interceptors for polling client
pollingApiClient.interceptors.request.use(
  (config) => {
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
  (error) => {
    console.error('Polling API Error:', error.response?.status, error.response?.data);
    return Promise.reject(error);
  }
); 