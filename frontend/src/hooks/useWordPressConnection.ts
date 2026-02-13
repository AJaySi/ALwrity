/**
 * WordPress Connection Hook
 * Manages WordPress site connections and publishing state.
 */

import { useState, useEffect, useCallback } from 'react';
import { wordpressAPI, WordPressSite, WordPressStatusResponse } from '../api/wordpress';
import { useAuth } from '@clerk/clerk-react';

export interface UseWordPressConnectionReturn {
  // Connection state
  connected: boolean;
  sites: WordPressSite[];
  totalSites: number;
  isLoading: boolean;
  
  // Connection actions
  addSite: (siteData: {
    site_url: string;
    site_name: string;
    username: string;
    app_password: string;
  }) => Promise<boolean>;
  disconnectSite: (siteId: number) => Promise<boolean>;
  testConnection: (siteData: {
    site_url: string;
    site_name: string;
    username: string;
    app_password: string;
  }) => Promise<boolean>;
  
  // Publishing actions
  publishContent: (publishData: {
    site_id: number;
    title: string;
    content: string;
    excerpt?: string;
    featured_image_path?: string;
    categories?: string[];
    tags?: string[];
    status?: 'draft' | 'publish' | 'private';
    meta_description?: string;
  }) => Promise<{ success: boolean; post_id?: number; error?: string }>;
  
  // Utility functions
  validateSiteUrl: (url: string) => boolean;
  formatSiteUrl: (url: string) => string;
  refreshStatus: () => Promise<void>;
}

export const useWordPressConnection = (): UseWordPressConnectionReturn => {
  const { getToken } = useAuth();
  const [connected, setConnected] = useState(false);
  const [sites, setSites] = useState<WordPressSite[]>([]);
  const [totalSites, setTotalSites] = useState(0);
  const [isLoading, setIsLoading] = useState(false);

  // Set up authentication
  useEffect(() => {
    const setupAuth = async () => {
      try {
        wordpressAPI.setAuthTokenGetter(async () => {
          try {
            return await getToken();
          } catch (e) {
            return null;
          }
        });
      } catch (error) {
        console.error('Error setting up WordPress API auth:', error);
      }
    };

    setupAuth();
  }, [getToken]);

  // Check connection status on mount
  useEffect(() => {
    checkStatus();
  }, []);

  const checkStatus = async () => {
    try {
      setIsLoading(true);
      const status: WordPressStatusResponse = await wordpressAPI.getStatus();
      
      setConnected(status.connected);
      setSites(status.sites || []);
      setTotalSites(status.total_sites);
    } catch (error) {
      console.error('Error checking WordPress status:', error);
      setConnected(false);
      setSites([]);
      setTotalSites(0);
    } finally {
      setIsLoading(false);
    }
  };

  const addSite = async (siteData: {
    site_url: string;
    site_name: string;
    username: string;
    app_password: string;
  }): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // Format the site URL
      const formattedUrl = wordpressAPI.formatSiteUrl(siteData.site_url);
      
      const site = await wordpressAPI.addSite({
        ...siteData,
        site_url: formattedUrl
      });
      
      // Update local state
      setSites(prev => [site, ...prev]);
      setTotalSites(prev => prev + 1);
      setConnected(true);
      
      console.log('WordPress site added successfully:', site);
      return true;
    } catch (error) {
      console.error('Error adding WordPress site:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const disconnectSite = async (siteId: number): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      const result = await wordpressAPI.disconnectSite(siteId);
      
      if (result.success) {
        // Update local state
        setSites(prev => prev.filter(site => site.id !== siteId));
        setTotalSites(prev => Math.max(0, prev - 1));
        
        // Check if we still have any connected sites
        const remainingSites = sites.filter(site => site.id !== siteId);
        setConnected(remainingSites.length > 0);
        
        console.log('WordPress site disconnected successfully');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Error disconnecting WordPress site:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const testConnection = async (siteData: {
    site_url: string;
    site_name: string;
    username: string;
    app_password: string;
  }): Promise<boolean> => {
    try {
      setIsLoading(true);
      
      // Format the site URL
      const formattedUrl = wordpressAPI.formatSiteUrl(siteData.site_url);
      
      const success = await wordpressAPI.testConnection({
        ...siteData,
        site_url: formattedUrl
      });
      
      return success;
    } catch (error) {
      console.error('Error testing WordPress connection:', error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const publishContent = async (publishData: {
    site_id: number;
    title: string;
    content: string;
    excerpt?: string;
    featured_image_path?: string;
    categories?: string[];
    tags?: string[];
    status?: 'draft' | 'publish' | 'private';
    meta_description?: string;
  }): Promise<{ success: boolean; post_id?: number; error?: string }> => {
    try {
      setIsLoading(true);
      
      const result = await wordpressAPI.publishContent(publishData);
      
      console.log('WordPress content published:', result);
      return result;
    } catch (error) {
      console.error('Error publishing WordPress content:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    } finally {
      setIsLoading(false);
    }
  };

  const validateSiteUrl = useCallback((url: string): boolean => {
    return wordpressAPI.validateSiteUrl(url);
  }, []);

  const formatSiteUrl = useCallback((url: string): string => {
    return wordpressAPI.formatSiteUrl(url);
  }, []);

  const refreshStatus = useCallback(async (): Promise<void> => {
    await checkStatus();
  }, []);

  return {
    // Connection state
    connected,
    sites,
    totalSites,
    isLoading,
    
    // Connection actions
    addSite,
    disconnectSite,
    testConnection,
    
    // Publishing actions
    publishContent,
    
    // Utility functions
    validateSiteUrl,
    formatSiteUrl,
    refreshStatus
  };
};
