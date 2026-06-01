import React, { useState, useEffect } from 'react';
import { apiClient } from '../../../api/client';
import { wordpressAPI, WordPressSite, WordPressPublishRequest } from '../../../api/wordpress';
import { BlogSEOMetadataResponse } from '../../../services/blogWriterApi';
import WixConnectModal from './WixConnectModal';
import { useWixPublish } from '../../../hooks/useWixPublish';
import { useTextToSpeech } from '../../../hooks/useTextToSpeech';

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

interface PublishContentProps {
  buildFullMarkdown: () => string;
  convertMarkdownToHTML: (md: string) => string;
  seoMetadata: BlogSEOMetadataResponse | null;
  seoAnalysis?: any;
  blogTitle?: string;
}

export const PublishContent: React.FC<PublishContentProps> = ({
  buildFullMarkdown,
  convertMarkdownToHTML,
  seoMetadata,
  blogTitle,
}) => {
  const {
    wixStatus,
    checkingWix,
    publishingWix,
    publishToWix,
    showWixConnectModal,
    setShowWixConnectModal,
    closeWixConnectModal,
    handleWixConnectionSuccess,
    validateWixContent,
  } = useWixPublish();

  const [wordpressSites, setWordpressSites] = useState<WordPressSite[]>([]);
  const [checkingWP, setCheckingWP] = useState(false);
  const [publishing, setPublishing] = useState<string | null>(null);
  const [publishResult, setPublishResult] = useState<{ platform: string; success: boolean; message: string; url?: string } | null>(null);
  const [copyDone, setCopyDone] = useState(false);
  const [wixContentWarning, setWixContentWarning] = useState<string | null>(null);

  // Audio / TTS
  const { speak, stop, isSpeaking, isSupported } = useTextToSpeech();
  const [isListening, setIsListening] = useState(false);

  const stripMarkdown = (md: string) => {
    return md
      .replace(/[#*_~`]/g, '')
      .replace(/\[(.*?)\]\(.*\)/g, '$1')
      .replace(/!\[.*?\]\(.*?\)/g, '')
      .replace(/\n{2,}/g, '\n')
      .trim();
  };

  const handleListen = () => {
    if (isSpeaking) {
      stop();
      setIsListening(false);
      return;
    }
    const md = buildFullMarkdown();
    const plainText = stripMarkdown(md);
    if (!plainText) return;
    setIsListening(true);
    speak(plainText, { rate: 1 });
  };

  useEffect(() => {
    if (isListening && !isSpeaking) {
      setIsListening(false);
    }
  }, [isSpeaking, isListening]);

  useEffect(() => {
    checkWPStatus();
  }, []);

  const checkWPStatus = async () => {
    setCheckingWP(true);
    try {
      const status = await wordpressAPI.getStatus();
      setWordpressSites(status.sites || []);
    } catch {
      setWordpressSites([]);
    } finally {
      setCheckingWP(false);
    }
  };

  const publishToWordPress = async () => {
    const md = buildFullMarkdown();
    const html = convertMarkdownToHTML(md);
    setPublishing('wordpress');
    setPublishResult(null);

    try {
      if (!seoMetadata) {
        setPublishResult({ platform: 'wordpress', success: false, message: 'Generate SEO metadata first before publishing.' });
        return;
      }

      const activeSite = wordpressSites.find(s => s.is_active) || wordpressSites[0];
      if (!activeSite) {
        setPublishResult({ platform: 'wordpress', success: false, message: 'No WordPress sites connected. Go to Settings > Integrations to add one.' });
        return;
      }

      const title = seoMetadata.seo_title || md.match(/^#\s+(.+)$/m)?.[1] || 'Blog Post';
      const request: WordPressPublishRequest = {
        site_id: activeSite.id,
        title,
        content: html,
        excerpt: seoMetadata.meta_description || '',
        status: 'publish',
        meta_description: seoMetadata.meta_description || '',
        tags: seoMetadata.blog_tags || [],
        categories: seoMetadata.blog_categories || [],
      };

      const result = await wordpressAPI.publishContent(request);
      if (result.success) {
        setPublishResult({ platform: 'wordpress', success: true, message: `Published to "${activeSite.site_name}"!`, url: result.post_url });
        try { localStorage.setItem('blog_publish_completed', 'true'); } catch {}
      } else {
        setPublishResult({ platform: 'wordpress', success: false, message: result.error || 'Publish failed' });
      }
    } catch (err: any) {
      setPublishResult({ platform: 'wordpress', success: false, message: err?.response?.data?.detail || err.message || 'Publish failed' });
    } finally {
      setPublishing(null);
    }
  };

  const handlePublishToWix = async () => {
    const md = buildFullMarkdown();
    setPublishResult(null);
    setWixContentWarning(null);
    const validation = validateWixContent(md);
    if (!validation.valid) {
      setPublishResult({ platform: 'wix', success: false, message: validation.warning || 'Content validation failed.' });
      return;
    }
    if (validation.warning) {
      setWixContentWarning(validation.warning);
    }
    const result = await publishToWix(md, seoMetadata, blogTitle);
    setPublishResult({ platform: 'wix', success: result.success, message: result.message, url: result.url });
    if (result.warning && result.success) {
      setWixContentWarning(result.warning);
    }
    setPublishResult({ platform: 'wix', success: result.success, message: result.message, url: result.url });
    if (result.success) {
      saveCompleteBlogAsset(blogTitle || seoMetadata?.seo_title || 'Blog Post', md, seoMetadata);
      try { localStorage.setItem('blog_publish_completed', 'true'); } catch {}
    }
  };

  const handleWixClick = () => {
    if (wixStatus?.connected) {
      handlePublishToWix();
    } else {
      setShowWixConnectModal(true);
    }
  };

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(buildFullMarkdown());
    setCopyDone(true);
    setTimeout(() => setCopyDone(false), 2000);
  };

  const handleCopyHTML = () => {
    navigator.clipboard.writeText(convertMarkdownToHTML(buildFullMarkdown()));
    setCopyDone(true);
    setTimeout(() => setCopyDone(false), 2000);
  };

  const cardStyle: React.CSSProperties = {
    background: '#ffffff',
    borderRadius: 12,
    border: '1px solid #e2e8f0',
    padding: 24,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  };

  const btnStyle: React.CSSProperties = {
    padding: '10px 20px',
    borderRadius: 8,
    border: 'none',
    fontWeight: 600,
    cursor: 'pointer',
    fontSize: '0.875rem',
    transition: 'all 0.2s',
  };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <h2 style={{ margin: '0 0 8px 0', color: '#0f172a' }}>Publish Your Blog</h2>
      <p style={{ margin: '0 0 24px 0', color: '#64748b', fontSize: '0.9rem' }}>
        Your blog is ready to publish. Choose a platform below.
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* WordPress card */}
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f172a' }}>WordPress</h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                {checkingWP ? 'Checking connection...' : wordpressSites.length > 0 ? `${wordpressSites.length} site(s) connected` : 'No sites connected'}
              </p>
            </div>
            <button
              onClick={publishToWordPress}
              disabled={publishing === 'wordpress' || wordpressSites.length === 0}
              style={{
                ...btnStyle,
                background: wordpressSites.length > 0 ? 'linear-gradient(135deg, #21759b, #1a6a8a)' : '#e2e8f0',
                color: wordpressSites.length > 0 ? '#fff' : '#94a3b8',
                cursor: wordpressSites.length > 0 && publishing !== 'wordpress' ? 'pointer' : 'not-allowed',
              }}
            >
              {publishing === 'wordpress' ? 'Publishing...' : 'Publish to WordPress'}
            </button>
          </div>
          {wordpressSites.length > 0 && wordpressSites[0] && (
            <div style={{ marginTop: 8, fontSize: '0.8rem', color: '#64748b' }}>
              Target: {wordpressSites[0].site_name} ({wordpressSites[0].site_url})
            </div>
          )}
        </div>

        {/* Wix card */}
        <div style={cardStyle}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f172a' }}>Wix</h3>
              <p style={{ margin: '4px 0 0 0', fontSize: '0.85rem', color: '#64748b' }}>
                {checkingWix ? 'Checking connection...' : wixStatus?.connected ? 'Connected' : 'Not connected'}
              </p>
            </div>
            <button
              onClick={handleWixClick}
              disabled={publishingWix}
              style={{
                ...btnStyle,
                background: wixStatus?.connected ? 'linear-gradient(135deg, #0a6eff, #0052cc)' : '#6366f1',
                color: '#fff',
                cursor: !publishingWix ? 'pointer' : 'not-allowed',
              }}
            >
              {publishingWix ? 'Publishing...' : wixStatus?.connected ? 'Publish to Wix' : 'Connect Wix'}
            </button>
          </div>
          {wixStatus?.connected && wixStatus.site_info && (
            <div style={{ marginTop: 8, fontSize: '0.8rem', color: '#64748b' }}>
              Site: {wixStatus.site_info.name || wixStatus.site_info.displayName}
            </div>
          )}
          {wixContentWarning && (
            <div style={{ marginTop: 8, padding: '6px 10px', fontSize: '0.8rem', color: '#92400e', background: '#fef3c7', borderRadius: 6, border: '1px solid #fcd34d' }}>
              {wixContentWarning}
            </div>
          )}
        </div>

        {/* Export card */}
        <div style={cardStyle}>
          <h3 style={{ margin: 0, fontSize: '1.1rem', color: '#0f172a' }}>Export</h3>
          <p style={{ margin: '4px 0 12px 0', fontSize: '0.85rem', color: '#64748b' }}>
            Copy your blog content for use elsewhere
          </p>
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
            <button
              onClick={handleCopyMarkdown}
              style={{ ...btnStyle, background: '#f1f5f9', color: '#334155', border: '1px solid #e2e8f0' }}
            >
              {copyDone ? 'Copied!' : 'Copy Markdown'}
            </button>
            <button
              onClick={handleCopyHTML}
              style={{ ...btnStyle, background: '#f1f5f9', color: '#334155', border: '1px solid #e2e8f0' }}
            >
              {copyDone ? 'Copied!' : 'Copy HTML'}
            </button>
            {isSupported && (
              <button
                onClick={handleListen}
                style={{
                  ...btnStyle,
                  background: isListening ? '#fef2f2' : '#f1f5f9',
                  color: isListening ? '#991b1b' : '#334155',
                  border: `1px solid ${isListening ? '#fecaca' : '#e2e8f0'}`,
                }}
              >
                {isListening ? '🔊 Stop Listening' : '🔈 Listen to Blog'}
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Publish result */}
      {publishResult && (
        <div style={{
          marginTop: 16,
          padding: 16,
          borderRadius: 8,
          background: publishResult.success ? '#f0fdf4' : '#fef2f2',
          border: `1px solid ${publishResult.success ? '#86efac' : '#fecaca'}`,
          color: publishResult.success ? '#166534' : '#991b1b',
        }}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>
            {publishResult.success ? '✅ Published!' : '❌ Publish failed'}
          </div>
          <div style={{ fontSize: '0.9rem' }}>{publishResult.message}</div>
          {publishResult.url && (
            <a href={publishResult.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '0.85rem', marginTop: 4, display: 'inline-block' }}>
              View published post
            </a>
          )}
        </div>
      )}

      <WixConnectModal
        isOpen={showWixConnectModal}
        onClose={closeWixConnectModal}
        onConnectionSuccess={handleWixConnectionSuccess}
      />
    </div>
  );
};

export default PublishContent;
