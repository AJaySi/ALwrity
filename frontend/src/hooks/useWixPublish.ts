import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from '../api/client';
import { BlogSEOMetadataResponse } from '../services/blogWriterApi';

export interface WixStatus {
  connected: boolean;
  has_permissions: boolean;
  site_info?: any;
}

export interface WixPublishResult {
  success: boolean;
  url?: string;
  post_id?: string;
  message: string;
  action_required?: string;
}

export function useWixPublish() {
  const [wixStatus, setWixStatus] = useState<WixStatus | null>(null);
  const [checkingWix, setCheckingWix] = useState(false);
  const [publishingWix, setPublishingWix] = useState(false);
  const [showWixConnectModal, setShowWixConnectModal] = useState(false);
  const pendingPublishRef = useRef<(() => Promise<WixPublishResult>) | null>(null);

  const checkWixStatus = useCallback(async () => {
    setCheckingWix(true);
    try {
      if (typeof window.name === 'string' && window.name.startsWith('WIX_RESULT::')) {
        try {
          const payload = JSON.parse(atob(window.name.replace('WIX_RESULT::', '')));
          if (payload.access_token) {
            localStorage.setItem('wix_access_token', payload.access_token);
          }
          localStorage.setItem('wix_connected', 'true');
          sessionStorage.setItem('wix_connected', 'true');
          window.name = '';
          setWixStatus({ connected: true, has_permissions: true, site_info: payload.site_info });
          return;
        } catch {}
      }

      try {
        const resp = await apiClient.get('/api/wix/connection/status');
        if (resp.data?.connected) {
          setWixStatus({
            connected: true,
            has_permissions: resp.data.has_permissions ?? true,
            site_info: resp.data.site_info,
          });
          return;
        }
      } catch {}

      if (localStorage.getItem('wix_connected') === 'true') {
        setWixStatus({ connected: true, has_permissions: true });
        return;
      }

      if (sessionStorage.getItem('wix_connected') === 'true') {
        setWixStatus({ connected: true, has_permissions: true });
        return;
      }

      const params = new URLSearchParams(window.location.search);
      if (params.get('wix_connected') === 'true') {
        localStorage.setItem('wix_connected', 'true');
        sessionStorage.setItem('wix_connected', 'true');
        setWixStatus({ connected: true, has_permissions: true });
        window.history.replaceState({}, document.title, window.location.pathname + window.location.hash);
        return;
      }

      setWixStatus({ connected: false, has_permissions: false });
    } catch {
      setWixStatus({ connected: false, has_permissions: false });
    } finally {
      setCheckingWix(false);
    }
  }, []);

  useEffect(() => {
    checkWixStatus();
  }, [checkWixStatus]);

  useEffect(() => {
    const handler = (e: StorageEvent) => {
      if (e.key === 'wix_connected' && e.newValue === 'true') {
        setWixStatus({ connected: true, has_permissions: true });
        setShowWixConnectModal(false);
      }
      if (e.key === 'wix_access_token' && e.newValue) {
        setWixStatus(prev => prev ? prev : { connected: true, has_permissions: true });
      }
    };
    window.addEventListener('storage', handler);

    const msgHandler = (e: MessageEvent) => {
      if (e.data?.type === 'WIX_OAUTH_SUCCESS' && e.data?.success) {
        if (e.data.access_token) localStorage.setItem('wix_access_token', e.data.access_token);
        localStorage.setItem('wix_connected', 'true');
        sessionStorage.setItem('wix_connected', 'true');
        setWixStatus({ connected: true, has_permissions: true, site_info: e.data.site_info });
        setShowWixConnectModal(false);
      }
    };
    window.addEventListener('message', msgHandler);

    return () => {
      window.removeEventListener('storage', handler);
      window.removeEventListener('message', msgHandler);
    };
  }, []);

  const publishToWix = useCallback(async (
    content: string,
    metadata: BlogSEOMetadataResponse | null,
    explicitTitle?: string,
  ): Promise<WixPublishResult> => {
    const title = explicitTitle
      || metadata?.seo_title
      || content.match(/^#\s+(.+)$/m)?.[1]
      || content.match(/^##\s+(.+)$/m)?.[1]?.replace(/^\d+[\.\)]\s*/, '')
      || 'Blog Post';

    let coverImageUrl: string | undefined;
    if (metadata?.open_graph?.image) {
      const img = metadata.open_graph.image;
      if (typeof img === 'string' && (img.startsWith('http://') || img.startsWith('https://'))) {
        coverImageUrl = img;
      }
    }

    try {
      // Include access_token as fallback. The backend DB may not have tokens
      // if the OAuth callback ran in a new tab where Clerk wasn't initialized.
      // Tokens may be in sessionStorage (same-tab) or localStorage (cross-tab).
      let accessToken: string | undefined;
      try {
        if (typeof window.name === 'string' && window.name.startsWith('WIX_RESULT::')) {
          const payload = JSON.parse(atob(window.name.replace('WIX_RESULT::', '')));
          accessToken = payload.access_token || undefined;
          if (payload.access_token) localStorage.setItem('wix_access_token', payload.access_token);
          window.name = '';
        }
      } catch {}
      if (!accessToken) {
        try {
          const raw = sessionStorage.getItem('wix_tokens');
          if (raw) {
            const parsed = JSON.parse(raw);
            accessToken = parsed.accessToken?.value || parsed.access_token || undefined;
          }
        } catch {}
      }
      if (!accessToken) {
        try {
          accessToken = localStorage.getItem('wix_access_token') || undefined;
        } catch {}
      }

      const response = await apiClient.post('/api/wix/publish', {
        title,
        content,
        cover_image_url: coverImageUrl,
        category_names: metadata?.blog_categories || [],
        tag_names: metadata?.blog_tags || [],
        publish: true,
        ...(accessToken ? { access_token: accessToken } : {}),
        seo_metadata: metadata ? {
          seo_title: metadata.seo_title,
          meta_description: metadata.meta_description,
          focus_keyword: metadata.focus_keyword,
          blog_tags: metadata.blog_tags || [],
          social_hashtags: metadata.social_hashtags || [],
          open_graph: metadata.open_graph || {},
          twitter_card: metadata.twitter_card || {},
          canonical_url: metadata.canonical_url,
        } : undefined,
      });

      if (response.data.success) {
        const url = response.data.url;
        return {
          success: true,
          url,
          post_id: response.data.post_id,
          message: url
            ? `Blog post published to Wix! View it here: ${url}`
            : 'Blog post published successfully to Wix!',
        };
      }
      return {
        success: false,
        message: response.data.error || 'Failed to publish to Wix',
      };
    } catch (error: any) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        pendingPublishRef.current = async () => publishToWix(content, metadata);
        setShowWixConnectModal(true);
        return {
          success: false,
          message: 'Wix tokens expired. Please reconnect your Wix account.',
          action_required: 'reconnect_wix',
        };
      }
      return {
        success: false,
        message: `Failed to publish to Wix: ${error.response?.data?.detail || error.message}`,
      };
    }
  }, []);

  const handleWixConnectionSuccess = useCallback(async () => {
    await checkWixStatus();
    const fn = pendingPublishRef.current;
    if (fn) {
      pendingPublishRef.current = null;
      setTimeout(async () => {
        try {
          setPublishingWix(true);
          await fn();
        } catch {} finally {
          setPublishingWix(false);
        }
      }, 500);
    }
  }, [checkWixStatus]);

  const closeWixConnectModal = useCallback(() => {
    setShowWixConnectModal(false);
    pendingPublishRef.current = null;
  }, []);

  return {
    wixStatus,
    checkingWix,
    publishingWix,
    setPublishingWix,
    checkWixStatus,
    publishToWix,
    showWixConnectModal,
    setShowWixConnectModal,
    closeWixConnectModal,
    handleWixConnectionSuccess,
  };
}
