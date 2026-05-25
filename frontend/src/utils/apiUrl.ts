/**
 * Shared API URL resolution utility.
 *
 * Determines the correct backend URL based on:
 *  1. Explicit REACT_APP_API_URL env var (production)
 *  2. Browser origin when accessed via localhost (development)
 *  3. Fallback to http://localhost:8000
 *
 * This ensures that when a developer accesses the app via
 * `http://localhost:3000`, the API calls go to `http://localhost:8000`
 * regardless of what REACT_APP_API_URL (e.g. an ngrok URL) is set to.
 * Conversely, when accessed via an ngrok URL, the API calls go to that
 * same ngrok URL.
 */

const LOCALHOST_PORTS = [3000, 3001, 5173, 5174, 8080, 4173];

function isLocalhostAccess(): boolean {
  try {
    if (typeof window === 'undefined') return false;
    const { hostname } = window.location;
    return hostname === 'localhost' || hostname === '127.0.0.1';
  } catch {
    return false;
  }
}

function getLocalhostApiUrl(): string {
  try {
    if (typeof window === 'undefined') return 'http://localhost:8000';
    const { port } = window.location;
    const numericPort = parseInt(port, 10);
    // If the frontend is running on a common dev port, assume backend is on 8000
    if (LOCALHOST_PORTS.includes(numericPort) || isNaN(numericPort)) {
      return 'http://localhost:8000';
    }
    // If on port 8000 itself (served by backend), use same origin
    if (numericPort === 8000) {
      return `${window.location.origin}`;
    }
    return 'http://localhost:8000';
  } catch {
    return 'http://localhost:8000';
  }
}

/**
 * Returns the appropriate API base URL.
 *
 * In production: always uses REACT_APP_API_URL (required).
 * In development, when the browser is on localhost: uses http://localhost:8000
 * In development, when the browser is NOT on localhost (e.g. ngrok):
 *   uses REACT_APP_API_URL if set, otherwise http://localhost:8000.
 */
export const getApiBaseUrl = (): string => {
  const envUrl = process.env.REACT_APP_API_URL;
  const isProduction = process.env.NODE_ENV === 'production';

  if (isProduction) {
    if (!envUrl) {
      console.error('[getApiBaseUrl] REACT_APP_API_URL is not set for production!');
      throw new Error('REACT_APP_API_URL environment variable is required for production.');
    }
    return envUrl;
  }

  // Development: if accessing from localhost, always use localhost backend
  if (isLocalhostAccess()) {
    const localUrl = getLocalhostApiUrl();
    if (envUrl && envUrl !== localUrl) {
      console.info(`[getApiBaseUrl] Browser on localhost — using local backend ${localUrl} instead of env URL ${envUrl}`);
    }
    return localUrl;
  }

  // Development: not on localhost (e.g. ngrok) — use env URL if set
  if (envUrl) {
    return envUrl;
  }

  return 'http://localhost:8000';
};

export default getApiBaseUrl;