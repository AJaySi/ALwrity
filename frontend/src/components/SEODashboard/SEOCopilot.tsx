
import React, { useEffect, useMemo, useState } from 'react';
import { useSEOCopilotStore } from '../../stores/seoCopilotStore';
import SEOCopilotActions from './SEOCopilotActions';

const SEOCopilot: React.FC = () => {
  const { 
    loadPersonalizationData, 
    error, 
    clearError,
    isLoading 
  } = useSEOCopilotStore();
  const { analysisData } = useSEOCopilotStore();

  // Handle data loading and error states
  useEffect(() => {
    const initializeCopilot = async () => {
      try {
        await loadPersonalizationData();
      } catch (error) {
        console.error('Failed to initialize SEO Copilot:', error);
      }
    };

    initializeCopilot();
  }, [loadPersonalizationData]);

  // Auto-clear errors after 5 seconds
  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => {
        clearError();
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [error, clearError]);

  // Get the CopilotKit API key from the same sources as App.tsx
  // Check localStorage first, then fall back to environment variable
  const publicApiKey = useMemo(() => {
    const savedKey = typeof window !== 'undefined' 
      ? localStorage.getItem('copilotkit_api_key') 
      : null;
    const envKey = process.env.REACT_APP_COPILOTKIT_API_KEY || '';
    const key = (savedKey || envKey).trim();
    
    // Validate key format if present
    if (key && !key.startsWith('ck_pub_')) {
      console.warn('SEOCopilot: CopilotKit API key format invalid - must start with ck_pub_');
    }
    
    return key;
  }, []);

  // Derive a friendly site/brand name from the URL for personalization
  const domainRootName = useMemo(() => {
    const url = analysisData?.url;
    if (!url) return '';
    try {
      const withProto = url.startsWith('http') ? url : `https://${url}`;
      const host = new URL(withProto).hostname;
      const parts = host.split('.').filter(Boolean);
      const root = parts.length >= 2 ? parts[parts.length - 2] : parts[0] || '';
      if (!root) return '';
      return root.charAt(0).toUpperCase() + root.slice(1);
    } catch {
      return '';
    }
  }, [analysisData?.url]);

  // Suggestions model: progressive disclosure
  const topLevelGroups = useMemo(() => ([
    { title: 'Content analysis', message: 'Content analysis' },
    { title: 'Website/URL analysis', message: 'Web URL analysis' },
    { title: 'Technical SEO', message: 'Technical SEO' },
    { title: 'Strategy & planning', message: 'Strategy and planning' },
    { title: 'Monitoring & health', message: 'Monitoring and health' }
  ]), []);

  const subSuggestionsByGroup = useMemo(() => ({
    'Content analysis': [
      { title: 'Comprehensive content analysis', message: 'Analyze content comprehensively for my site' },
      { title: 'Optimize page content', message: 'Optimize page content for SEO' },
      { title: 'Generate meta descriptions', message: 'Generate meta descriptions for key pages' }
    ],
    'Web URL analysis': [
      { title: 'Comprehensive SEO analysis', message: 'Run comprehensive SEO analysis for a URL' },
      { title: 'Analyze page speed', message: 'Analyze page speed for a URL' },
      { title: 'Analyze sitemap', message: 'Analyze sitemap for my site' },
      { title: 'Generate OpenGraph tags', message: 'Generate OpenGraph tags for a URL' }
    ],
    'Technical SEO': [
      { title: 'Technical SEO audit', message: 'Run a technical SEO audit' },
      { title: 'Check SEO health', message: 'Check overall SEO health' },
      { title: 'Image alt text', message: 'Generate image alt text for pages' }
    ],
    'Strategy and planning': [
      { title: 'Enterprise SEO analysis', message: 'Run enterprise SEO analysis' },
      { title: 'Content strategy', message: 'Analyze content strategy and recommendations' },
      { title: 'Customize SEO dashboard', message: 'Customize the SEO dashboard' }
    ],
    'Monitoring and health': [
      { title: 'Website audit', message: 'Perform a website audit' },
      { title: 'Update SEO charts', message: 'Update SEO charts and visualizations' },
      { title: 'Explain an SEO concept', message: 'Explain an SEO concept in simple terms' }
    ]
  }), []);

  const [chatSuggestions, setChatSuggestions] = useState(topLevelGroups);

  useEffect(() => {
    loadPersonalizationData();
  }, [loadPersonalizationData]);

  return (
    <>
      {/* Loading indicator */}
      {isLoading && (
        <div className="seo-copilot-loading">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <p>Loading SEO Assistant...</p>
          </div>
        </div>
      )}
      
      {/* Error display */}
      {error && (
        <div className="seo-copilot-error">
          <div className="error-message">
            <span className="error-icon">⚠️</span>
            <span className="error-text">{error}</span>
            <button 
              className="error-dismiss"
              onClick={clearError}
              aria-label="Dismiss error"
            >
              ×
            </button>
          </div>
        </div>
      )}
      
      <SEOCopilotActions />
      
      <style>{`
        .seo-copilot-loading {
          position: fixed;
          top: 20px;
          right: 20px;
          background: rgba(0, 0, 0, 0.8);
          color: white;
          padding: 12px 16px;
          border-radius: 8px;
          z-index: 1300;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .seo-copilot-error {
          position: fixed;
          top: 20px;
          right: 20px;
          background: #f44336;
          color: white;
          padding: 12px 16px;
          border-radius: 8px;
          z-index: 1300;
          display: flex;
          align-items: center;
          gap: 8px;
          max-width: 300px;
        }
        
        .error-message {
          display: flex;
          align-items: center;
          gap: 8px;
          flex: 1;
        }
        
        .error-dismiss {
          background: none;
          border: none;
          color: white;
          font-size: 18px;
          cursor: pointer;
          padding: 0;
          margin-left: 8px;
        }
        
        .spinner {
          width: 16px;
          height: 16px;
          border: 2px solid #ffffff40;
          border-top: 2px solid #ffffff;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </>
  );
};

export default SEOCopilot;
