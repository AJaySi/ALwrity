// SEO CopilotKit Provider Component
// Main provider that wraps all SEO CopilotKit functionality

import React, { useEffect, useMemo, useState } from 'react';
import { CopilotKit } from '@copilotkit/react-core';
import { CopilotSidebar } from '@copilotkit/react-ui';
import '@copilotkit/react-ui/styles.css';
import SEOCopilotContext from './SEOCopilotContext';
import SEOCopilotActions from './SEOCopilotActions';
import { useSEOCopilotStore } from '../../stores/seoCopilotStore';

interface SEOCopilotKitProviderProps {
  children: React.ReactNode;
  enableDebugMode?: boolean;
}

const SEOCopilotKitProvider: React.FC<SEOCopilotKitProviderProps> = ({ 
  children, 
  enableDebugMode = false 
}) => {
  const { analysisData } = useSEOCopilotStore();

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
      console.warn('SEOCopilotKitProvider: CopilotKit API key format invalid - must start with ck_pub_');
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
  const backChip = useMemo(() => ({ title: '← Back to categories', message: 'back' }), []);
  const displayedSuggestions = useMemo(() => {
    // Always show a back chip when not on top-level
    const isTop = chatSuggestions === topLevelGroups;
    return isTop ? chatSuggestions : [...chatSuggestions, backChip];
  }, [chatSuggestions, topLevelGroups, backChip]);

  // Initialize the provider
  useEffect(() => {
    if (enableDebugMode) {
      console.log('🔧 SEO CopilotKit Provider initialized successfully');
      console.log('🔑 CopilotKit API Key:', publicApiKey ? 'Configured' : 'Missing');
    }
  }, [enableDebugMode, publicApiKey]);

  return (
    <CopilotKit publicApiKey={publicApiKey}>
      <CopilotSidebar
        className="alwrity-copilot-sidebar"
        labels={{
          title: domainRootName ? `ALwrity SEO • ${domainRootName}` : "ALwrity SEO Assistant",
          initial: domainRootName
            ? `Hi! 👋 I'm your SEO assistant for ${domainRootName}. I can analyze your site, generate meta descriptions, check page speed, and more. What would you like to work on today?`
            : "Hi! 👋 I'm your SEO expert assistant. I can help you analyze your website, generate meta descriptions, check page speed, and much more. What would you like to work on today?",
        }}
        suggestions={displayedSuggestions}
        makeSystemMessage={(context: string, additionalInstructions?: string) => {
          const websiteUrl = analysisData?.url;
          const urlLine = websiteUrl ? `The user's current website URL is ${websiteUrl}. If the user does not provide a URL explicitly, default to this URL.` : '';
          const guidance = `
You are ALwrity's SEO Expert Assistant. ${urlLine}
When greeting the user, personalize messages${domainRootName ? ` for ${domainRootName}` : ''} and keep a professional, friendly tone.
Never ask for the URL if you already have it in context unless the user wants to switch URLs.
Focus on actionable recommendations and use the registered tools.
          `.trim();
          return [guidance, additionalInstructions].filter(Boolean).join('\n\n');
        }}
        onSubmitMessage={(message: string) => {
          const text = (message || '').trim();
          const match = Object.keys(subSuggestionsByGroup).find(key => key.toLowerCase() === text.toLowerCase());
          if (match) {
            setChatSuggestions(subSuggestionsByGroup[match as keyof typeof subSuggestionsByGroup]);
          } else if (text.toLowerCase() === 'back' || text.toLowerCase() === 'categories') {
            setChatSuggestions(topLevelGroups);
          }
        }}
        observabilityHooks={{
          onChatExpanded: () => {
            if (enableDebugMode) {
              console.log('🔧 SEO CopilotKit Sidebar opened');
            }
          },
          onChatMinimized: () => {
            if (enableDebugMode) {
              console.log('🔧 SEO CopilotKit Sidebar closed');
            }
          },
        }}
      >
        <div className="seo-copilotkit-provider">
          {/* Suggestions controller sets progressive suggestions */}
          {/* SEOSuggestionsController */}
          {/* SEO CopilotKit Context - Provides data and instructions */}
          <SEOCopilotContext>
            {/* SEO CopilotKit Actions - Defines available actions */}
            <SEOCopilotActions />
            
            {/* Main content */}
            <div className="seo-copilotkit-content">
              {children}
            </div>
          </SEOCopilotContext>

          {/* Copilot debug info removed */}

          <style>{`
            .seo-copilotkit-provider {
              position: relative;
              width: 100%;
              height: 100%;
            }

            /* ALwrity Compact Copilot Styling - 60% Smaller & More Efficient */
            .alwrity-copilot-sidebar {
              --alwrity-bg: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(255,255,255,0.08));
              --alwrity-border: rgba(255,255,255,0.22);
              --alwrity-shadow: 0 8px 24px rgba(0,0,0,0.25); /* Reduced from 18px 50px */
              --alwrity-accent: #667eea;
              --alwrity-accent2: #764ba2;
              --alwrity-text: rgba(255,255,255,0.92);
              --alwrity-subtext: rgba(255,255,255,0.7);
            }
            
            .alwrity-copilot-sidebar * {
              font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, 'Helvetica Neue', Arial, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
            }
            
            /* Compact sidebar container */
            .alwrity-copilot-sidebar .copilot-sidebar-container,
            .alwrity-copilot-sidebar .copilotkit-sidebar,
            .alwrity-copilot-sidebar .copilotkit-chat-container {
              background: var(--alwrity-bg) !important;
              backdrop-filter: blur(16px) !important; /* Reduced from 22px */
              -webkit-backdrop-filter: blur(16px) !important;
              border: 1px solid var(--alwrity-border) !important;
              box-shadow: var(--alwrity-shadow) !important;
              color: var(--alwrity-text) !important;
              
              /* Compact dimensions */
              width: 40% !important; /* Reduced from 100% */
              max-width: 320px !important;
              min-width: 280px !important;
              height: 85vh !important;
              max-height: 600px !important;
              
              /* Compact spacing */
              padding: 8px !important;
              margin: 8px !important;
              border-radius: 8px !important;
            }
            
            .alwrity-copilot-sidebar .copilotkit-title,
            .alwrity-copilot-sidebar .copilot-title {
              color: var(--alwrity-text) !important;
              font-weight: 600 !important; /* Reduced from 700 */
              letter-spacing: 0.1px !important; /* Reduced from 0.2px */
              font-size: 14px !important; /* Reduced from 18px+ */
            }
            
            .alwrity-copilot-sidebar .copilotkit-sidebar,
            .alwrity-copilot-sidebar .copilot-sidebar-container {
              z-index: 1200 !important;
            }
            
            .alwrity-copilot-sidebar .copilotkit-subtitle,
            .alwrity-copilot-sidebar .copilot-subtitle,
            .alwrity-copilot-sidebar .copilotkit-initial-message {
              color: var(--alwrity-subtext) !important;
              font-size: 12px !important; /* Reduced from 14px+ */
              line-height: 1.3 !important; /* Reduced from 1.5 */
              margin: 4px 0 8px 0 !important;
            }
            
            /* Compact Suggestions - 60% smaller */
            .alwrity-copilot-sidebar .copilot-suggestion,
            .alwrity-copilot-sidebar .copilotkit-suggestion,
            .alwrity-copilot-sidebar .copilotkit-suggestions button,
            .alwrity-copilot-sidebar .copilot-suggestions button {
              position: relative;
              background: linear-gradient(180deg, rgba(255,255,255,0.16), rgba(255,255,255,0.08)) !important;
              border: 1px solid rgba(255,255,255,0.32) !important; /* Reduced from 1.5px */
              color: var(--alwrity-text) !important;
              box-shadow: 0 4px 12px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.2) !important; /* Reduced from 10px 28px */
              transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease; /* Reduced from 0.25s */
              border-radius: 8px !important; /* Reduced from 12px */
              overflow: hidden;
              backdrop-filter: blur(12px); /* Reduced from 16px */
              -webkit-backdrop-filter: blur(12px);
              
              /* Compact padding and margins */
              padding: 6px 10px !important; /* Reduced from 12px+ */
              margin: 3px !important; /* Reduced from 6px+ */
              font-size: 12px !important; /* Reduced from 14px+ */
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion::before,
            .alwrity-copilot-sidebar .copilotkit-suggestion::before,
            .alwrity-copilot-sidebar .copilotkit-suggestions button::before,
            .alwrity-copilot-sidebar .copilot-suggestions button::before {
              content: "";
              position: absolute;
              top: 0;
              left: -120%;
              width: 120%;
              height: 100%;
              background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent); /* Reduced from 0.18 */
              transition: left 0.4s ease; /* Reduced from 0.6s */
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion:hover::before,
            .alwrity-copilot-sidebar .copilotkit-suggestion:hover::before,
            .alwrity-copilot-sidebar .copilotkit-suggestions button:hover::before,
            .alwrity-copilot-sidebar .copilot-suggestions button:hover::before {
              left: 120%;
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion:hover,
            .alwrity-copilot-sidebar .copilotkit-suggestion:hover,
            .alwrity-copilot-sidebar .copilotkit-suggestions button:hover,
            .alwrity-copilot-sidebar .copilot-suggestions button:hover {
              transform: translateY(-2px) scale(1.01); /* Reduced from -4px 1.015 */
              box-shadow: 0 8px 20px rgba(0,0,0,0.25), 0 0 0 1px rgba(255,255,255,0.15) inset !important; /* Reduced from 18px 44px */
              border-color: rgba(255,255,255,0.4) !important; /* Reduced from 0.45 */
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion:active,
            .alwrity-copilot-sidebar .copilotkit-suggestion:active,
            .alwrity-copilot-sidebar .copilotkit-suggestions button:active,
            .alwrity-copilot-sidebar .copilot-suggestions button:active {
              transform: translateY(-1px) scale(0.995);
              box-shadow: 0 4px 12px rgba(0,0,0,0.25) !important; /* Reduced from 8px 20px */
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion:focus-visible,
            .alwrity-copilot-sidebar .copilotkit-suggestion:focus-visible,
            .alwrity-copilot-sidebar .copilotkit-suggestions button:focus-visible,
            .alwrity-copilot-sidebar .copilot-suggestions button:focus-visible {
              outline: none !important;
              box-shadow: 0 0 0 2px rgba(255,255,255,0.35), 0 0 0 3px rgba(102,126,234,0.3) !important; /* Reduced from 4px */
            }
            
            .alwrity-copilot-sidebar .copilot-suggestion .icon, 
            .alwrity-copilot-sidebar .copilotkit-suggestion .icon, 
            .alwrity-copilot-sidebar .copilotkit-suggestions button .icon {
              filter: drop-shadow(0 1px 3px rgba(0,0,0,0.2)); /* Reduced from 2px 6px */
              width: 14px !important; /* Reduced from 18px+ */
              height: 14px !important; /* Reduced from 18px+ */
              margin-right: 6px !important; /* Reduced from 8px+ */
            }
            
            /* Compact suggestions grid */
            .alwrity-copilot-sidebar .copilotkit-suggestions,
            .alwrity-copilot-sidebar .copilot-suggestions {
              display: grid;
              grid-template-columns: 1fr;
              gap: 6px; /* Reduced from 10px */
              margin: 8px 0; /* Reduced from 16px+ */
            }
            
            @media (min-width: 420px) {
              .alwrity-copilot-sidebar .copilotkit-suggestions,
              .alwrity-copilot-sidebar .copilot-suggestions {
                grid-template-columns: 1fr 1fr;
                gap: 8px; /* Reduced from 12px */
              }
            }

            /* Compact motion for users who prefer it */
            @media (prefers-reduced-motion: reduce) {
              .alwrity-copilot-sidebar .copilot-suggestion,
              .alwrity-copilot-sidebar .copilotkit-suggestion,
              .alwrity-copilot-sidebar .copilotkit-suggestions button,
              .alwrity-copilot-sidebar .copilot-suggestions button {
                transition: none !important;
              }
              .alwrity-copilot-sidebar .copilot-suggestion::before,
              .alwrity-copilot-sidebar .copilotkit-suggestion::before,
              .alwrity-copilot-sidebar .copilotkit-suggestions button::before,
              .alwrity-copilot-sidebar .copilot-suggestions button::before {
                display: none !important;
              }
            }

            /* Compact scrollbar styling */
            .alwrity-copilot-sidebar ::-webkit-scrollbar {
              width: 6px; /* Reduced from 10px */
              height: 6px; /* Reduced from 10px */
            }
            
            .alwrity-copilot-sidebar ::-webkit-scrollbar-thumb {
              background: rgba(255,255,255,0.2); /* Reduced from 0.25 */
              border: 1px solid rgba(0,0,0,0.1);
              border-radius: 6px; /* Reduced from 10px */
            }
            
            .alwrity-copilot-sidebar ::-webkit-scrollbar-track {
              background: rgba(255,255,255,0.05); /* Reduced from 0.08 */
              border-radius: 6px; /* Reduced from 10px */
            }
            
            /* Compact primary buttons */
            .alwrity-copilot-sidebar .copilot-primary,
            .alwrity-copilot-sidebar .copilotkit-primary-button,
            .alwrity-copilot-sidebar button[type="submit"] {
              background: linear-gradient(90deg, var(--alwrity-accent), var(--alwrity-accent2)) !important;
              border: 1px solid rgba(255,255,255,0.3) !important; /* Reduced from 0.35 */
              color: white !important;
              padding: 6px 12px !important; /* Reduced from 10px 20px */
              font-size: 12px !important; /* Reduced from 14px+ */
              border-radius: 6px !important; /* Reduced from 8px+ */
            }
            
            /* Compact input styling */
            .alwrity-copilot-sidebar .copilot-input,
            .alwrity-copilot-sidebar .copilotkit-input {
              background: rgba(255,255,255,0.12) !important; /* Reduced from 0.14 */
              color: var(--alwrity-text) !important;
              border: 1px solid rgba(255,255,255,0.2) !important; /* Reduced from 0.22 */
              padding: 8px 12px !important; /* Reduced from 14px 18px */
              font-size: 13px !important; /* Reduced from 14px+ */
              border-radius: 6px !important; /* Reduced from 8px+ */
            }

            /* Compact chat messages container */
            .alwrity-copilot-sidebar .copilotkit-messages,
            .alwrity-copilot-sidebar .copilot-messages,
            .alwrity-copilot-sidebar .chat-messages {
              padding: 8px !important; /* Reduced from 16px+ */
              margin: 0 !important;
              max-height: 70vh !important; /* Ensure chat takes most space */
              overflow-y: auto !important;
            }

            /* Compact chat input area */
            .alwrity-copilot-sidebar .copilotkit-input-container,
            .alwrity-copilot-sidebar .copilot-input-container {
              padding: 8px !important; /* Reduced from 16px+ */
              margin: 8px 0 !important; /* Reduced from 16px+ */
              border-top: 1px solid rgba(255,255,255,0.1) !important;
            }

            /* Compact close button */
            .alwrity-copilot-sidebar .copilotkit-close,
            .alwrity-copilot-sidebar .copilot-close,
            .alwrity-copilot-sidebar button[aria-label*="close"],
            .alwrity-copilot-sidebar button[aria-label*="Close"] {
              width: 24px !important; /* Reduced from 32px+ */
              height: 24px !important; /* Reduced from 32px+ */
              border-radius: 50% !important;
              padding: 0 !important;
              font-size: 12px !important; /* Reduced from 16px+ */
            }

            /* Compact responsive design */
            @media (max-width: 768px) {
              .alwrity-copilot-sidebar .copilot-sidebar-container,
              .alwrity-copilot-sidebar .copilotkit-sidebar,
              .alwrity-copilot-sidebar .copilotkit-chat-container {
                width: 90% !important; /* Mobile: take more width */
                max-width: none !important;
                min-width: 280px !important;
                height: 80vh !important;
              }
              
              .alwrity-copilot-sidebar .copilotkit-suggestions,
              .alwrity-copilot-sidebar .copilot-suggestions {
                grid-template-columns: 1fr !important; /* Single column on mobile */
                gap: 4px !important; /* Even more compact on mobile */
              }
            }

            .seo-copilotkit-loading {
              position: fixed;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background: rgba(255, 255, 255, 0.9);
              display: flex;
              align-items: center;
              justify-content: center;
              z-index: 1000;
            }

            .loading-spinner {
              text-align: center;
              padding: 20px;
              background: white;
              border-radius: 8px;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            .spinner {
              width: 40px;
              height: 40px;
              border: 4px solid #f3f3f3;
              border-top: 4px solid #3498db;
              border-radius: 50%;
              animation: spin 1s linear infinite;
              margin: 0 auto 10px;
            }

            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }

            .seo-copilotkit-error {
              position: fixed;
              top: 20px;
              right: 20px;
              z-index: 1001;
              max-width: 400px;
            }

            .error-message {
              background: #fee;
              border: 1px solid #fcc;
              border-radius: 6px;
              padding: 12px 16px;
              display: flex;
              align-items: center;
              gap: 8px;
              box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }

            .error-icon {
              font-size: 16px;
              flex-shrink: 0;
            }

            .error-text {
              flex: 1;
              color: #c33;
              font-size: 14px;
            }

            .error-dismiss {
              background: none;
              border: none;
              color: #c33;
              font-size: 18px;
              cursor: pointer;
              padding: 0;
              width: 20px;
              height: 20px;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: 50%;
              transition: background-color 0.2s;
            }

            .error-dismiss:hover {
              background: rgba(204, 51, 51, 0.1);
            }

            .seo-copilotkit-content {
              width: 100%;
              height: 100%;
            }

            .seo-copilotkit-debug {
              position: fixed;
              bottom: 20px;
              left: 20px;
              z-index: 999;
              background: rgba(0, 0, 0, 0.8);
              color: white;
              border-radius: 6px;
              padding: 8px;
              font-size: 12px;
            }

            .seo-copilotkit-debug summary {
              cursor: pointer;
              padding: 4px 8px;
              border-radius: 4px;
              transition: background-color 0.2s;
            }

            .seo-copilotkit-debug summary:hover {
              background: rgba(255, 255, 255, 0.1);
            }

            .debug-content {
              padding: 8px;
              border-top: 1px solid rgba(255, 255, 255, 0.2);
              margin-top: 4px;
            }

            .debug-content p {
              margin: 4px 0;
              font-size: 11px;
            }
          `}</style>
        </div>
      </CopilotSidebar>
    </CopilotKit>
  );
};

export default SEOCopilotKitProvider;
