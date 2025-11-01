import React, { useState, useEffect } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { BlogSEOMetadataResponse } from '../../services/blogWriterApi';
import { apiClient } from '../../api/client';
import { wordpressAPI, WordPressSite, WordPressPublishRequest } from '../../api/wordpress';
import { validateAndRefreshWixTokens } from '../../utils/wixTokenUtils';
import WixConnectModal from './BlogWriterUtils/WixConnectModal';

interface PublisherProps {
  buildFullMarkdown: () => string;
  convertMarkdownToHTML: (md: string) => string;
  seoMetadata: BlogSEOMetadataResponse | null;
}

const useCopilotActionTyped = useCopilotAction as any;

interface WixConnectionStatus {
  connected: boolean;
  has_permissions: boolean;
  site_info?: any;
  permissions?: any;
  error?: string;
}

export const Publisher: React.FC<PublisherProps> = ({
  buildFullMarkdown,
  convertMarkdownToHTML,
  seoMetadata
}) => {
  const [wixConnectionStatus, setWixConnectionStatus] = useState<WixConnectionStatus | null>(null);
  const [checkingWixStatus, setCheckingWixStatus] = useState(false);
  const [wordpressSites, setWordpressSites] = useState<WordPressSite[]>([]);
  const [checkingWordPressStatus, setCheckingWordPressStatus] = useState(false);
  const [showWixConnectModal, setShowWixConnectModal] = useState(false);
  const [pendingWixPublish, setPendingWixPublish] = useState<(() => Promise<any>) | null>(null);

  // Check platform connection statuses on component mount
  useEffect(() => {
    checkWixConnectionStatus();
    checkWordPressConnectionStatus();
  }, []);

  const checkWixConnectionStatus = async () => {
    setCheckingWixStatus(true);
    try {
      const response = await apiClient.get('/api/wix/connection/status');
      setWixConnectionStatus(response.data);
    } catch (error) {
      console.error('Failed to check Wix connection status:', error);
      setWixConnectionStatus({
        connected: false,
        has_permissions: false,
        error: 'Failed to check connection status'
      });
    } finally {
      setCheckingWixStatus(false);
    }
  };

  const checkWordPressConnectionStatus = async () => {
    setCheckingWordPressStatus(true);
    try {
      const status = await wordpressAPI.getStatus();
      setWordpressSites(status.sites || []);
    } catch (error) {
      console.error('Failed to check WordPress connection status:', error);
      setWordpressSites([]);
    } finally {
      setCheckingWordPressStatus(false);
    }
  };

  // Helper function to publish to Wix
  const publishToWix = async (md: string, metadata: BlogSEOMetadataResponse | null, accessToken?: string): Promise<any> => {
    // Get access token if not provided
    if (!accessToken) {
      const tokenResult = await validateAndRefreshWixTokens();
      if (!tokenResult.accessToken) {
        return {
          success: false,
          message: 'Wix tokens not available. Please connect your Wix account.',
          action_required: 'connect_wix'
        };
      }
      accessToken = tokenResult.accessToken;
    }

    // Extract title from SEO metadata or markdown
    const title = metadata?.seo_title || (() => {
      const titleMatch = md.match(/^#\s+(.+)$/m);
      return titleMatch ? titleMatch[1] : 'Blog Post from ALwrity';
    })();

    // Extract cover image URL, skip if base64 (Wix needs HTTP URL)
    let coverImageUrl: string | undefined = undefined;
    if (metadata?.open_graph?.image) {
      const imageUrl = metadata.open_graph.image;
      // Skip base64 images - Wix import_image needs HTTP/HTTPS URL
      if (typeof imageUrl === 'string' && (imageUrl.startsWith('http://') || imageUrl.startsWith('https://'))) {
        coverImageUrl = imageUrl;
      } else {
        console.warn('Skipping cover image - Wix requires HTTP/HTTPS URL, received:', imageUrl?.substring(0, 50));
      }
    }

    try {
      // Publish using same endpoint as WixTestPage
      // Note: Wix requires category/tag IDs (UUIDs), not names
      // For now, skip categories/tags until we implement ID lookup/creation
      const response = await apiClient.post('/api/wix/test/publish/real', {
        title: title,
        content: md, // Use markdown, backend converts it
        cover_image_url: coverImageUrl,
        // TODO: Lookup/create category IDs from metadata?.blog_categories
        // TODO: Lookup/create tag IDs from metadata?.blog_tags
        category_ids: undefined,
        tag_ids: undefined,
        publish: true,
        access_token: accessToken,
        member_id: undefined // Let backend derive from token
      });

      if (response.data.success) {
        return {
          success: true,
          url: response.data.url,
          post_id: response.data.post_id,
          message: 'Blog post published successfully to Wix!'
        };
      } else {
        return {
          success: false,
          message: response.data.error || 'Failed to publish to Wix'
        };
      }
    } catch (error: any) {
      // If auth error, token may be invalid - try refreshing or reconnect
      if (error.response?.status === 401 || error.response?.status === 403) {
        // Try to refresh one more time
        const tokenResult = await validateAndRefreshWixTokens();
        if (tokenResult.needsReconnect) {
          const publishFunction = async () => {
            return await publishToWix(md, metadata);
          };
          setPendingWixPublish(() => publishFunction);
          setShowWixConnectModal(true);
          return {
            success: false,
            message: 'Wix tokens expired. Please reconnect your Wix account.',
            action_required: 'reconnect_wix'
          };
        }
        // If refresh worked, retry once
        if (tokenResult.accessToken) {
          return await publishToWix(md, metadata, tokenResult.accessToken);
        }
      }
      
      return {
        success: false,
        message: `Failed to publish to Wix: ${error.response?.data?.detail || error.message}`
      };
    }
  };

  // Handle Wix connection success - retry publish
  const handleWixConnectionSuccess = async () => {
    if (pendingWixPublish) {
      const publishFn = pendingWixPublish;
      setPendingWixPublish(null);
      // Small delay to ensure tokens are saved in sessionStorage
      setTimeout(async () => {
        try {
          // Retry the publish - this will be executed and return result
          // Note: The result won't show in CopilotKit UI since we're outside the action handler
          // But the publish will succeed and user will see their blog on Wix
          const result = await publishFn();
          console.log('Wix publish after connection:', result);
          // Optionally show a success notification
          if (result.success) {
            // Publish succeeded - user's blog is now on Wix
            console.log('Blog published to Wix successfully after connection');
          }
        } catch (error) {
          console.error('Error retrying publish after connection:', error);
        }
      }, 500);
    }
  };
  // Enhanced publish action with Wix support
  useCopilotActionTyped({
    name: 'publishToPlatform',
    description: 'Publish the blog to Wix or WordPress',
    parameters: [
      { name: 'platform', type: 'string', description: 'wix|wordpress', required: true },
      { name: 'schedule_time', type: 'string', description: 'Optional ISO datetime', required: false }
    ],
    handler: async ({ platform, schedule_time }: { platform: 'wix' | 'wordpress'; schedule_time?: string }) => {
      const md = buildFullMarkdown();
      const html = convertMarkdownToHTML(md);
      
      if (platform === 'wix') {
        // Proactively validate and refresh tokens
        const tokenResult = await validateAndRefreshWixTokens();
        
        if (tokenResult.needsReconnect || !tokenResult.accessToken) {
          // Store the publish function to retry after connection
          const publishFunction = async () => {
            return await publishToWix(md, seoMetadata);
          };
          setPendingWixPublish(() => publishFunction);
          setShowWixConnectModal(true);
          return {
            success: false,
            message: 'Wix account not connected. Please connect your Wix account to publish.',
            action_required: 'connect_wix'
          };
        }

        // We have a valid access token, proceed with publishing
        return await publishToWix(md, seoMetadata, tokenResult.accessToken);
      } else if (platform === 'wordpress') {
        // WordPress publishing
        if (!seoMetadata) {
          return { 
            success: false, 
            message: 'Generate SEO metadata first. Use the "Next: Generate SEO Metadata" suggestion to create metadata before publishing.' 
          };
        }

        // Check if user has connected WordPress sites
        if (wordpressSites.length === 0) {
          return {
            success: false,
            message: 'No WordPress sites connected. Please connect a WordPress site first. Go to Settings > Integrations to add your WordPress site.',
            action_required: 'connect_wordpress'
          };
        }

        // Find first active site, or use first site if none are active
        const activeSite = wordpressSites.find(site => site.is_active) || wordpressSites[0];
        if (!activeSite) {
          return {
            success: false,
            message: 'No active WordPress sites found. Please activate a WordPress site connection.',
            action_required: 'activate_wordpress'
          };
        }

        // Extract title from SEO metadata or markdown
        const title = seoMetadata.seo_title || (() => {
          const titleMatch = md.match(/^#\s+(.+)$/m);
          return titleMatch ? titleMatch[1] : 'Blog Post from ALwrity';
        })();

        // Extract excerpt from SEO metadata
        const excerpt = seoMetadata.meta_description || '';

        // Build WordPress publish request
        const publishRequest: WordPressPublishRequest = {
          site_id: activeSite.id,
          title: title,
          content: html,
          excerpt: excerpt,
          status: 'publish',
          meta_description: seoMetadata.meta_description || excerpt,
          tags: seoMetadata.blog_tags || [],
          categories: seoMetadata.blog_categories || []
        };

        try {
          const result = await wordpressAPI.publishContent(publishRequest);
          
          if (result.success) {
            return {
              success: true,
              url: result.post_url || `${activeSite.site_url}/?p=${result.post_id}`,
              post_id: result.post_id,
              message: `Blog post published successfully to WordPress site "${activeSite.site_name}"!`
            };
          } else {
            return {
              success: false,
              message: result.error || 'Failed to publish to WordPress'
            };
          }
        } catch (error: any) {
          return {
            success: false,
            message: `Failed to publish to WordPress: ${error.response?.data?.detail || error.message || 'Unknown error'}`
          };
        }
      } else {
        return {
          success: false,
          message: `Unsupported platform: ${platform}. Supported platforms are 'wix' and 'wordpress'.`
        };
      }
    },
    render: ({ status, result }: any) => {
      if (status === 'complete') {
        if (result?.success) {
          return (
            <div style={{ padding: 12 }}>
              <div style={{ color: 'green', fontWeight: 'bold' }}>
                ✅ Published Successfully!
              </div>
              {result.url && (
                <div style={{ marginTop: 8 }}>
                  <a href={result.url} target="_blank" rel="noopener noreferrer">
                    View Published Post
                  </a>
                </div>
              )}
              {result.post_id && (
                <div style={{ fontSize: '0.9em', color: '#666', marginTop: 4 }}>
                  Post ID: {result.post_id}
                </div>
              )}
            </div>
          );
        } else {
          return (
            <div style={{ padding: 12 }}>
              <div style={{ color: 'red', fontWeight: 'bold' }}>
                ❌ Publishing Failed
              </div>
              <div style={{ marginTop: 8, color: '#666' }}>
                {result?.message}
              </div>
              {result?.action_required === 'connect_wix' && (
                <div style={{ marginTop: 8 }}>
                  <a href="/wix-test" target="_blank" rel="noopener noreferrer">
                    Connect Wix Account
                  </a>
                </div>
              )}
              {(result?.action_required === 'connect_wordpress' || result?.action_required === 'activate_wordpress') && (
                <div style={{ marginTop: 8 }}>
                  <a href="/settings/integrations" target="_blank" rel="noopener noreferrer">
                    Manage WordPress Connections
                  </a>
                </div>
              )}
            </div>
          );
        }
      }
      return null;
    }
  });

  return (
    <>
      <WixConnectModal
        isOpen={showWixConnectModal}
        onClose={() => {
          setShowWixConnectModal(false);
          setPendingWixPublish(null);
        }}
        onConnectionSuccess={handleWixConnectionSuccess}
      />
    </>
  );
};

export default Publisher;
