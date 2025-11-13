/**
 * SEO Metadata Modal Component
 * 
 * Comprehensive SEO metadata generation and editing interface with:
 * - Tabbed interface for different metadata types
 * - Live preview of social media cards
 * - Character counters and validation
 * - Copy-to-clipboard functionality
 * - Integration with backend metadata generation
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
  IconButton,
  Chip,
  Tooltip
} from '@mui/material';
import {
  Close as CloseIcon,
  Check as CheckIcon,
  Preview as PreviewIcon,
  Search as SearchIcon,
  Share as ShareIcon,
  Code as CodeIcon,
  Tag as TagIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { apiClient, triggerSubscriptionError } from '../../api/client';

// Import metadata display components
import { CoreMetadataTab } from './SEO/MetadataDisplay/CoreMetadataTab';
import { SocialMediaTab } from './SEO/MetadataDisplay/SocialMediaTab';
import { StructuredDataTab } from './SEO/MetadataDisplay/StructuredDataTab';
import { PreviewCard } from './SEO/MetadataDisplay/PreviewCard';
import { subscribeImage } from '../../utils/imageBus';

interface SEOMetadataModalProps {
  isOpen: boolean;
  onClose: () => void;
  blogContent: string;
  blogTitle: string;
  researchData: any;
  outline?: any[]; // Add outline structure
  seoAnalysis?: any; // Add SEO analysis results
  onMetadataGenerated: (metadata: any) => void;
}

interface SEOMetadataResult {
  success: boolean;
  seo_title?: string;
  meta_description?: string;
  url_slug?: string;
  blog_tags?: string[];
  blog_categories?: string[];
  social_hashtags?: string[];
  open_graph?: any;
  twitter_card?: any;
  json_ld_schema?: any;
  canonical_url?: string;
  reading_time?: number;
  focus_keyword?: string;
  generated_at?: string;
  optimization_score?: number;
  error?: string;
}

// Cache helper functions (similar to SEOAnalysisModal)
async function hashContent(text: string): Promise<string> {
  try {
    const enc = new TextEncoder().encode(text);
    const digest = await crypto.subtle.digest('SHA-256', enc);
    const bytes = Array.from(new Uint8Array(digest));
    return bytes.map(b => b.toString(16).padStart(2, '0')).join('');
  } catch {
    // Fallback hash
    let h = 0;
    for (let i = 0; i < text.length; i++) h = (h * 31 + text.charCodeAt(i)) | 0;
    return String(h);
  }
}

function getMetadataCacheKey(contentHash: string, title?: string): string {
  return `seo_metadata_cache:${contentHash}:${title || ''}`;
}

export const SEOMetadataModal: React.FC<SEOMetadataModalProps> = ({
  isOpen,
  onClose,
  blogContent,
  blogTitle,
  researchData,
  outline,
  seoAnalysis,
  onMetadataGenerated
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [metadataResult, setMetadataResult] = useState<SEOMetadataResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tabValue, setTabValue] = useState('preview'); // Start with preview tab first
  const [previewTabValue, setPreviewTabValue] = useState('google'); // Sub-tab for preview platforms
  const [copiedItems, setCopiedItems] = useState<Set<string>>(new Set());
  const [editableMetadata, setEditableMetadata] = useState<SEOMetadataResult | null>(null);
  const [contentHash, setContentHash] = useState<string>('');
  // Subscribe to image generation bus to auto-fill OG/Twitter image fields
  useEffect(() => {
    const unsub = subscribeImage(({ base64 }: { base64: string }) => {
      setEditableMetadata(prev => {
        const next = { ...(prev || metadataResult || {}) } as any;
        next.open_graph = { ...(next.open_graph || {}), image: `data:image/png;base64,${base64}` };
        next.twitter_card = { ...(next.twitter_card || {}), image: `data:image/png;base64,${base64}` };
        return next;
      });
    });
    return unsub;
  }, [metadataResult]);

  // Debug logging only in development and when modal state changes meaningfully
  useEffect(() => {
    if (process.env.NODE_ENV === 'development' && isOpen) {
      console.log('🔍 SEOMetadataModal render:', {
        isOpen,
        blogContent: blogContent?.length,
        blogTitle,
        researchData: !!researchData
      });
    }
  }, [isOpen, blogContent?.length, blogTitle, researchData]);

  // Reset state when modal closes
  useEffect(() => {
    if (!isOpen) {
      // Reset state when modal closes (but keep result for next time)
      setError(null);
      setIsGenerating(false);
    }
  }, [isOpen]);

  const generateMetadata = useCallback(async (forceRefresh = false) => {
    try {
      setIsGenerating(true);
      setError(null);
      if (forceRefresh) {
        setMetadataResult(null);
      }

      console.log('🚀 Starting SEO metadata generation...', { forceRefresh });

      // Calculate content hash for caching - use existing hash if available
      let hash = contentHash;
      if (!hash) {
        hash = await hashContent(`${blogTitle || ''}\n${blogContent}`);
        // Update state for future use
        setContentHash(hash);
      }
      const cacheKey = getMetadataCacheKey(hash, blogTitle);
      console.log('🔍 Checking SEO metadata cache', { cacheKey, hasHash: !!hash, forceRefresh });

      // Check cache first (unless force refresh)
      if (!forceRefresh && typeof window !== 'undefined') {
        const cached = window.localStorage.getItem(cacheKey);
        if (cached) {
          try {
            const parsed = JSON.parse(cached) as SEOMetadataResult;
            // Validate cached data has required fields
            if (parsed && parsed.success !== undefined) {
              console.log('✅ Using cached SEO metadata', { cacheKey, success: parsed.success });
              setMetadataResult(parsed);
              setEditableMetadata(parsed);
              setIsGenerating(false);
              // Notify parent that metadata is available
              if (onMetadataGenerated) {
                onMetadataGenerated(parsed);
              }
              return;
            } else {
              console.warn('⚠️ Cached SEO metadata data is invalid, will fetch fresh metadata');
            }
          } catch (e) {
            console.warn('⚠️ Failed to parse cached SEO metadata, will fetch fresh metadata', e);
            // Remove invalid cache entry
            if (typeof window !== 'undefined') {
              window.localStorage.removeItem(cacheKey);
            }
          }
        } else {
          console.log('ℹ️ No cached SEO metadata found, will fetch from API', { cacheKey });
        }
      } else {
        console.log('🔄 Force refresh requested, skipping cache check');
      }

      // Make API call to generate metadata
      const response = await apiClient.post('/api/blog/seo/metadata', {
        content: blogContent,
        title: blogTitle,
        research_data: researchData,
        outline: outline || null,
        seo_analysis: seoAnalysis || null
      });

      const result = response.data;
      console.log('✅ SEO metadata generation response:', result);

      // Check if the response indicates a subscription error (even if HTTP status is 200)
      if (!result.success && result.error) {
        const errorMessage = result.error;
        // Check if error message indicates subscription limit (429/402)
        if (errorMessage.includes('Token limit') || 
            errorMessage.includes('limit would be exceeded') ||
            errorMessage.includes('usage limit') ||
            errorMessage.includes('subscription')) {
          console.log('SEOMetadataModal: Detected subscription error in response data', {
            error: errorMessage,
            data: result
          });
          
          // Create a mock error object with subscription error data
          const mockError = {
            response: {
              status: 429, // Treat as 429 for subscription error
              data: {
                error: errorMessage,
                message: result.message || errorMessage,
                provider: result.provider || 'unknown',
                usage_info: result.usage_info || {}
              }
            }
          };
          
          const handled = await triggerSubscriptionError(mockError);
          if (handled) {
            console.log('SEOMetadataModal: Global subscription error handler triggered successfully');
            setIsGenerating(false);
            return;
          } else {
            console.warn('SEOMetadataModal: Global subscription error handler did not handle the error');
          }
        }
        
        // If not a subscription error, throw the error normally
        throw new Error(result.error || 'Metadata generation failed');
      }

      // Cache the result
      if (typeof window !== 'undefined') {
        try {
          window.localStorage.setItem(cacheKey, JSON.stringify(result));
          console.log('💾 SEO metadata cached');
        } catch (e) {
          console.warn('Failed to cache metadata:', e);
        }
      }

      setMetadataResult(result);
      setEditableMetadata(result);
      console.log('📊 Metadata result set:', result);

    } catch (err: any) {
      console.error('❌ SEO metadata generation failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      const errorMessage = err?.message || err?.response?.data?.error || '';
      
      // Check HTTP status code first
      if (status === 429 || status === 402) {
        console.log('SEOMetadataModal: Detected subscription error (HTTP status), triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('SEOMetadataModal: Global subscription error handler triggered successfully');
          setIsGenerating(false);
          return;
        } else {
          console.warn('SEOMetadataModal: Global subscription error handler did not handle the error');
        }
      }
      
      // Also check error message for subscription-related errors (in case API returns 200 with error in body)
      if (errorMessage.includes('Token limit') || 
          errorMessage.includes('limit would be exceeded') ||
          errorMessage.includes('usage limit') ||
          errorMessage.includes('subscription') ||
          errorMessage.includes('429')) {
        console.log('SEOMetadataModal: Detected subscription error (error message), triggering global handler', {
          errorMessage,
          err
        });
        
        // Create a mock error object with subscription error data
        const mockError = {
          response: {
            status: 429,
            data: {
              error: errorMessage,
              message: errorMessage,
              provider: err?.response?.data?.provider || 'unknown',
              usage_info: err?.response?.data?.usage_info || {}
            }
          }
        };
        
        const handled = await triggerSubscriptionError(mockError);
        if (handled) {
          console.log('SEOMetadataModal: Global subscription error handler triggered successfully (from error message)');
          setIsGenerating(false);
          return;
        } else {
          console.warn('SEOMetadataModal: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      setError(err instanceof Error ? err.message : 'Failed to generate SEO metadata');
    } finally {
      setIsGenerating(false);
    }
  }, [blogContent, blogTitle, researchData, outline, seoAnalysis, contentHash, onMetadataGenerated]);

  // Precompute hash when modal opens and trigger cache check
  useEffect(() => {
    if (isOpen) {
      (async () => {
        const h = await hashContent(`${blogTitle || ''}\n${blogContent}`);
        setContentHash(h);
        // After hash is computed, check cache if we don't have metadata result yet
        if (!metadataResult) {
          // Small delay to ensure hash is set in state
          setTimeout(() => {
            generateMetadata(false);
          }, 100);
        }
      })();
    } else {
      // Reset hash when modal closes
      setContentHash('');
    }
  }, [isOpen, blogContent, blogTitle, metadataResult, generateMetadata]);

  // Fallback: if modal opens and hash is already computed, check cache immediately
  useEffect(() => {
    if (isOpen && !metadataResult && contentHash) {
      generateMetadata(false);
    }
  }, [isOpen, metadataResult, contentHash, generateMetadata]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: string) => {
    setTabValue(newValue);
  };

  const handleCopyToClipboard = async (text: string, itemId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedItems(prev => new Set([...prev, itemId]));
      setTimeout(() => {
        setCopiedItems(prev => {
          const newSet = new Set(prev);
          newSet.delete(itemId);
          return newSet;
        });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const handleMetadataEdit = (field: string, value: any) => {
    if (editableMetadata) {
      setEditableMetadata(prev => ({
        ...prev!,
        [field]: value
      }));
    }
  };

  /**
   * Handle Apply Metadata button click
   * 
   * This saves the generated/edited metadata to the parent component's state.
   * The metadata is then used when publishing to platforms:
   * - WordPress: Requires SEO metadata for proper post creation with SEO fields
   * - Wix: Currently doesn't require metadata, but could be added in future
   * 
   * The metadata includes:
   * - SEO title, meta description, URL slug
   * - Blog tags, categories, focus keyword
   * - Open Graph tags (Facebook/LinkedIn)
   * - Twitter Card tags
   * - JSON-LD structured data (Schema.org Article)
   * 
   * All of these will be passed to the platform's API when publishing.
   */
  const handleApplyMetadata = () => {
    if (editableMetadata) {
      onMetadataGenerated(editableMetadata);
      onClose();
    }
  };

  const getTabIcon = (tabValue: string) => {
    switch (tabValue) {
      case 'core': return <SearchIcon />;
      case 'social': return <ShareIcon />;
      case 'structured': return <CodeIcon />;
      case 'preview': return <PreviewIcon />;
      default: return <TagIcon />;
    }
  };

  const getTabLabel = (tabValue: string) => {
    switch (tabValue) {
      case 'core': return 'Core SEO';
      case 'social': return 'Social Media';
      case 'structured': return 'Structured Data';
      case 'preview': return 'Preview';
      default: return 'Metadata';
    }
  };

  return (
    <Dialog
      open={isOpen}
      onClose={onClose}
      maxWidth="lg"
      fullWidth
      PaperProps={{
        sx: {
          background: 'rgba(255, 255, 255, 0.98)',
          backdropFilter: 'blur(10px)',
          borderRadius: 3,
          minHeight: '80vh'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        pb: 1,
        borderBottom: '1px solid rgba(0,0,0,0.1)'
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <TagIcon sx={{ color: 'primary.main' }} />
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            SEO Metadata Generator
          </Typography>
          {metadataResult && (
            <Chip 
              label={`${metadataResult.optimization_score || 0}% Optimized`}
              color={metadataResult.optimization_score && metadataResult.optimization_score >= 80 ? 'success' : 
                     metadataResult.optimization_score && metadataResult.optimization_score >= 60 ? 'warning' : 'error'}
              size="small"
            />
          )}
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {metadataResult && (
            <Tooltip title="Regenerate SEO metadata">
              <IconButton 
                onClick={() => generateMetadata(true)} 
                size="small"
                disabled={isGenerating}
                color="primary"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          )}
          <IconButton onClick={onClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ p: 0 }}>
        {isGenerating && (
          <Box sx={{ p: 4, textAlign: 'center' }}>
            <CircularProgress size={60} sx={{ mb: 2 }} />
            <Typography variant="h6" sx={{ mb: 1 }}>
              Generating SEO Metadata...
            </Typography>
            <Typography variant="body2" sx={{ color: 'text.secondary' }}>
              Creating optimized titles, descriptions, and social media tags
            </Typography>
          </Box>
        )}

        {error && (
          <Box sx={{ p: 3 }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
            <Button
              variant="outlined"
              onClick={() => generateMetadata(true)}
              startIcon={<RefreshIcon />}
            >
              Try Again
            </Button>
          </Box>
        )}

        {metadataResult && (
          <Box>
            {/* Tabs */}
            <Box sx={{ borderBottom: 1, borderColor: 'divider', px: 3 }}>
              <Tabs
                value={tabValue}
                onChange={handleTabChange}
                variant="scrollable"
                scrollButtons="auto"
                sx={{ minHeight: 48 }}
              >
                {['preview', 'core', 'social', 'structured'].map((tab) => (
                  <Tab
                    key={tab}
                    value={tab}
                    label={getTabLabel(tab)}
                    icon={getTabIcon(tab)}
                    iconPosition="start"
                    sx={{ minHeight: 48, textTransform: 'none' }}
                  />
                ))}
              </Tabs>
            </Box>

            {/* Tab Content */}
            <Box sx={{ p: 3 }}>
              {tabValue === 'core' && (
                <CoreMetadataTab
                  metadata={editableMetadata || metadataResult}
                  onMetadataEdit={handleMetadataEdit}
                  onCopyToClipboard={handleCopyToClipboard}
                  copiedItems={copiedItems}
                />
              )}

              {tabValue === 'social' && (
                <SocialMediaTab
                  metadata={editableMetadata || metadataResult}
                  onMetadataEdit={handleMetadataEdit}
                  onCopyToClipboard={handleCopyToClipboard}
                  copiedItems={copiedItems}
                />
              )}

              {tabValue === 'structured' && (
                <StructuredDataTab
                  metadata={editableMetadata || metadataResult}
                  onMetadataEdit={handleMetadataEdit}
                  onCopyToClipboard={handleCopyToClipboard}
                  copiedItems={copiedItems}
                />
              )}

              {tabValue === 'preview' && (
                <PreviewCard
                  metadata={editableMetadata || metadataResult}
                  blogTitle={blogTitle}
                  previewTabValue={previewTabValue}
                  onPreviewTabChange={setPreviewTabValue}
                />
              )}
            </Box>
          </Box>
        )}
      </DialogContent>

      {metadataResult && (
        <DialogActions sx={{ p: 3, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
          <Button onClick={onClose} color="inherit">
            Cancel
          </Button>
          <Button
            variant="contained"
            onClick={handleApplyMetadata}
            startIcon={<CheckIcon />}
            sx={{ px: 3 }}
          >
            Apply Metadata
          </Button>
        </DialogActions>
      )}
    </Dialog>
  );
};
