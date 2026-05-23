import React, { useState, useEffect } from 'react';
import { useCopilotAction } from '@copilotkit/react-core';
import { BlogSEOMetadataResponse } from '../../services/blogWriterApi';
import { apiClient } from '../../api/client';
import { wordpressAPI, WordPressSite, WordPressPublishRequest } from '../../api/wordpress';
import WixConnectModal from './BlogWriterUtils/WixConnectModal';
import { useWixPublish } from '../../hooks/useWixPublish';

interface PublisherProps {
  buildFullMarkdown: () => string;
  convertMarkdownToHTML: (md: string) => string;
  seoMetadata: BlogSEOMetadataResponse | null;
  onPublishComplete?: () => void;
}

const saveCompleteBlogAsset = async (
  title: string,
  content: string,
  seoMetadata: BlogSEOMetadataResponse | null
) => {
  try {
    await apiClient.post('/api/blog/save-complete-asset', {
      title,
      content,
      seo_title: seoMetadata?.seo_title,
      meta_description: seoMetadata?.meta_description,
      focus_keyword: seoMetadata?.focus_keyword,
      tags: seoMetadata?.blog_tags || [],
      categories: seoMetadata?.blog_categories || [],
    });
  } catch (error) {
    console.error('Failed to save complete blog asset:', error);
  }
};

const useCopilotActionTyped = useCopilotAction as any;

export const Publisher: React.FC<PublisherProps> = ({
  buildFullMarkdown,
  convertMarkdownToHTML,
  seoMetadata,
  onPublishComplete,
}) => {
  const {
    publishToWix,
    showWixConnectModal,
    closeWixConnectModal,
    handleWixConnectionSuccess,
  } = useWixPublish();

  const [wordpressSites, setWordpressSites] = useState<WordPressSite[]>([]);
  const [checkingWordPressStatus, setCheckingWordPressStatus] = useState(false);

  useEffect(() => {
    checkWordPressConnectionStatus();
  }, []);

  const checkWordPressConnectionStatus = async () => {
    setCheckingWordPressStatus(true);
    try {
      const status = await wordpressAPI.getStatus();
      setWordpressSites(status.sites || []);
    } catch (error: any) {
      if (error?.response?.status !== 404) {
        console.error('Failed to check WordPress connection status:', error);
      }
      setWordpressSites([]);
    } finally {
      setCheckingWordPressStatus(false);
    }
  };

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
        const wixResult = await publishToWix(md, seoMetadata);
        if (wixResult.success) {
          saveCompleteBlogAsset(
            seoMetadata?.seo_title || 'Blog Post',
            md,
            seoMetadata
          );
          onPublishComplete?.();
        }
        return wixResult;
      } else if (platform === 'wordpress') {
        if (!seoMetadata) {
          return { 
            success: false, 
            message: 'Generate SEO metadata first. Use the "Next: Generate SEO Metadata" suggestion to create metadata before publishing.' 
          };
        }

        if (wordpressSites.length === 0) {
          return {
            success: false,
            message: 'No WordPress sites connected. Please connect a WordPress site first. Go to Settings > Integrations to add your WordPress site.',
            action_required: 'connect_wordpress'
          };
        }

        const activeSite = wordpressSites.find(site => site.is_active) || wordpressSites[0];
        if (!activeSite) {
          return {
            success: false,
            message: 'No active WordPress sites found. Please activate a WordPress site connection.',
            action_required: 'activate_wordpress'
          };
        }

        const title = seoMetadata.seo_title || (() => {
          const titleMatch = md.match(/^#\s+(.+)$/m);
          return titleMatch ? titleMatch[1] : 'Blog Post from ALwrity';
        })();

        const excerpt = seoMetadata.meta_description || '';

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
            saveCompleteBlogAsset(title, md, seoMetadata);
            onPublishComplete?.();
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
        onClose={closeWixConnectModal}
        onConnectionSuccess={handleWixConnectionSuccess}
      />
    </>
  );
};

export default Publisher;
