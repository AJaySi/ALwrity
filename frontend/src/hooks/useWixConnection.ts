import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/client';

export interface WixSite {
  id: string;
  blog_url: string;
  blog_id: string;
  created_at: string;
  scope: string;
}

export interface WixStatus {
  connected: boolean;
  sites: WixSite[];
  total_sites: number;
  error?: string;
}

export const useWixConnection = () => {
  const [status, setStatus] = useState<WixStatus>({
    connected: false,
    sites: [],
    total_sites: 0
  });
  const [isLoading, setIsLoading] = useState(false);

  const checkStatus = useCallback(async () => {
    setIsLoading(true);
    try {
      try {
        const resp = await apiClient.get('/api/wix/connection/status');
        if (resp.data?.connected) {
          const siteInfo = resp.data.site_info;
          const sites: WixSite[] = siteInfo ? [{
            id: siteInfo.siteId || siteInfo.site_id || 'wix-site-1',
            blog_url: siteInfo.url || siteInfo.viewUrl || 'Connected Wix Site',
            blog_id: 'wix-blog',
            created_at: siteInfo.createdAt || new Date().toISOString(),
            scope: 'BLOG.CREATE-DRAFT,BLOG.PUBLISH,MEDIA.MANAGE'
          }] : [];
          setStatus({ connected: true, sites, total_sites: sites.length });
          return;
        }
      } catch {}

      const connectedFlag = sessionStorage.getItem('wix_connected') === 'true'
        || localStorage.getItem('wix_connected') === 'true';

      if (connectedFlag) {
        const siteInfoRaw = sessionStorage.getItem('wix_site_info');
        let siteInfo: any = {};
        try { if (siteInfoRaw) siteInfo = JSON.parse(siteInfoRaw); } catch {}
        const sites: WixSite[] = [{
          id: siteInfo.siteId || siteInfo.site_id || 'wix-site-1',
          blog_url: siteInfo.url || siteInfo.viewUrl || 'Connected Wix Site',
          blog_id: 'wix-blog',
          created_at: siteInfo.createdAt || new Date().toISOString(),
          scope: 'BLOG.CREATE-DRAFT,BLOG.PUBLISH,MEDIA.MANAGE'
        }];
        setStatus({ connected: true, sites, total_sites: 1 });
      } else {
        setStatus({ connected: false, sites: [], total_sites: 0 });
      }
    } catch {
      setStatus({ connected: false, sites: [], total_sites: 0, error: 'Error checking connection status' });
    } finally {
      setIsLoading(false);
    }
  }, []);

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
