// Shared cache utility for API calls
// Reduces redundant API calls and improves performance

const apiCache = new Map<string, { data: any; timestamp: number; ttl: number }>();

export const getCachedApiCall = async (
  key: string,
  apiCall: () => Promise<any>,
  ttlSeconds: number = 300
): Promise<any> => {
  const now = Date.now();
  const cached = apiCache.get(key);

  if (cached && (now - cached.timestamp) < (cached.ttl * 1000)) {
    return cached.data;
  }

  try {
    const data = await apiCall();
    apiCache.set(key, { data, timestamp: now, ttl: ttlSeconds });
    return data;
  } catch (error) {
    // If API call fails, return cached data if available (stale data better than no data)
    if (cached) {
      return cached.data;
    }
    throw error;
  }
};

// Clear cache for a specific key
export const clearCache = (key: string): void => {
  apiCache.delete(key);
};

// Clear all cache
export const clearAllCache = (): void => {
  apiCache.clear();
};

// Get cache stats for debugging
export const getCacheStats = (): { size: number; keys: string[] } => {
  return {
    size: apiCache.size,
    keys: Array.from(apiCache.keys())
  };
};