/** Authentication utilities for ALwrity frontend. */

import { useAuth } from '@clerk/clerk-react';

/**
 * Hook to get the current authentication token
 */
export const useAuthToken = () => {
  const { getToken } = useAuth();
  
  const getAuthToken = async (): Promise<string | null> => {
    try {
      const token = await getToken();
      return token;
    } catch (error) {
      console.error('Error getting auth token:', error);
      return null;
    }
  };
  
  return { getAuthToken };
};

/**
 * Get auth token without using hooks (for use in non-React contexts)
 * This requires the Clerk instance to be available globally
 */
export const getAuthTokenSync = async (): Promise<string | null> => {
  try {
    // This is a fallback method - in practice, we'll use the hook version
    return null;
  } catch (error) {
    console.error('Error getting auth token sync:', error);
    return null;
  }
};
