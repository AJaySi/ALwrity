/**
 * Wix Connection Hook
 * Manages Wix connection state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/clerk-react';
import { wixAPI, WixStatus } from '../api/wix';

export const useWixConnection = () => {
  const { getToken } = useAuth();
  const [status, setStatus] = useState<WixStatus>({
    connected: false,
    sites: [],
    total_sites: 0
  });
  const [isLoading, setIsLoading] = useState(false);

  // Set up auth token getter for Wix API
  useEffect(() => {
    wixAPI.setAuthTokenGetter(async () => {
      try {
        const template = process.env.REACT_APP_CLERK_JWT_TEMPLATE;
        if (template) {
          // @ts-ignore Clerk types allow options object
          return await getToken({ template });
        }
        return await getToken();
      } catch {
        return null;
      }
    });
  }, [getToken]);

  const checkStatus = useCallback(async () => {
    setIsLoading(true);
    try {
      // Check sessionStorage for Wix tokens and site info
      const connectedFlag = sessionStorage.getItem('wix_connected') === 'true';
      const tokensRaw = sessionStorage.getItem('wix_tokens');
      const siteInfoRaw = sessionStorage.getItem('wix_site_info');
      
      if (connectedFlag && tokensRaw) {
        let siteInfo: any = {};
        try {
          if (siteInfoRaw) {
            siteInfo = JSON.parse(siteInfoRaw);
          }
        } catch (e) {
          // Ignore parse errors
        }

        // Set connected status with site information
        setStatus({
          connected: true,
          sites: [{ 
            id: siteInfo.siteId || siteInfo.site_id || 'wix-site-1', 
            blog_url: siteInfo.url || siteInfo.viewUrl || 'Connected Wix Site', 
            blog_id: 'wix-blog', 
            created_at: siteInfo.createdAt || new Date().toISOString(), 
            scope: 'BLOG.CREATE-DRAFT,BLOG.PUBLISH,MEDIA.MANAGE' 
          }],
          total_sites: 1
        });
        
      } else {
        setStatus({
          connected: false,
          sites: [],
          total_sites: 0,
          error: 'No Wix connection found'
        });
      }
    } catch (error) {
      setStatus({
        connected: false,
        sites: [],
        total_sites: 0,
        error: 'Error checking connection status'
      });
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Check status on mount
  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  return {
    connected: status.connected,
    sites: status.sites,
    totalSites: status.total_sites,
    isLoading,
    checkStatus
  };
};
