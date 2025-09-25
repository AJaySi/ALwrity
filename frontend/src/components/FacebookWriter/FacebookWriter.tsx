import React from 'react';
import { Box, Container, Typography, TextField, Paper, Button, Tooltip, Select, MenuItem, FormControl, InputLabel, CircularProgress } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotReadable, useCopilotAction } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import RegisterFacebookActions from './RegisterFacebookActions';
import RegisterFacebookEditActions from './RegisterFacebookEditActions';
import RegisterFacebookActionsEnhanced from './RegisterFacebookActionsEnhanced';
import { PlatformPersonaProvider, usePlatformPersonaContext } from '../shared/PersonaContext/PlatformPersonaProvider';
import { facebookWriterApi } from '../../services/facebookWriterApi';
import ContentGenerationProgress from './components/ContentGenerationProgress';

const useCopilotActionTyped = useCopilotAction as any;

// --- Facebook Post Button Component ---
interface FacebookPostButtonProps {
  postContent: string;
}

const FacebookPostButton: React.FC<FacebookPostButtonProps> = ({ postContent }) => {
  const [connectionStatus, setConnectionStatus] = React.useState<any>(null);
  const [pages, setPages] = React.useState<any[]>([]);
  const [selectedPageId, setSelectedPageId] = React.useState<string>('');
  const [isLoading, setIsLoading] = React.useState(false);
  const [isConnecting, setIsConnecting] = React.useState(false);

  // Check connection status on mount
  React.useEffect(() => {
    checkConnectionStatus();
  }, []);

  const checkConnectionStatus = async () => {
    try {
      const status = await facebookWriterApi.getFacebookConnectionStatus();
      setConnectionStatus(status);
      
      if (status.connected) {
        loadPages();
      }
    } catch (error: any) {
      console.error('Failed to check Facebook connection:', error);
      
      // Handle token expiration
      if (error.response?.status === 401 && error.response?.headers?.['x-reauth-required']) {
        setConnectionStatus({ connected: false, user_id: null, pages_count: 0 });
        window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
          detail: { 
            message: 'Facebook connection expired. Please reconnect.', 
            type: 'warning' 
          }
        }));
      }
    }
  };

  const loadPages = async () => {
    try {
      const pagesData = await facebookWriterApi.getFacebookPages();
      setPages(pagesData);
      
      // Auto-select first page if none selected
      if (pagesData.length > 0 && !selectedPageId) {
        setSelectedPageId(pagesData[0].id);
      }
    } catch (error: any) {
      console.error('Failed to load Facebook pages:', error);
      
      // Handle token expiration
      if (error.response?.status === 401 && error.response?.headers?.['x-reauth-required']) {
        setConnectionStatus({ connected: false, user_id: null, pages_count: 0 });
        setPages([]);
        window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
          detail: { 
            message: 'Facebook connection expired. Please reconnect.', 
            type: 'warning' 
          }
        }));
      }
    }
  };

  const handleConnectFacebook = async () => {
    setIsConnecting(true);
    try {
      const oauthUrl = await facebookWriterApi.startFacebookOAuth();
      window.open(oauthUrl, '_blank', 'width=600,height=600');
      
      // Poll for connection status
      const pollInterval = setInterval(async () => {
        try {
          const status = await facebookWriterApi.getFacebookConnectionStatus();
          if (status.connected) {
            setConnectionStatus(status);
            await loadPages();
            clearInterval(pollInterval);
            setIsConnecting(false);
          }
        } catch (error) {
          console.error('Polling error:', error);
        }
      }, 2000);
      
      // Stop polling after 2 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        setIsConnecting(false);
      }, 120000);
      
    } catch (error) {
      console.error('Failed to start Facebook OAuth:', error);
      setIsConnecting(false);
    }
  };

  const handlePublish = async () => {
    if (!selectedPageId || !postContent.trim()) return;
    
    setIsLoading(true);
    try {
      const result = await facebookWriterApi.publishFacebookPost({
        page_id: selectedPageId,
        message: postContent.trim()
      });
      
      if (result.success) {
        window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
          detail: { 
            message: `Posted successfully! ${result.permalink_url ? 'View post' : ''}`, 
            type: 'success',
            action: result.permalink_url ? { label: 'View', url: result.permalink_url } : undefined
          }
        }));
      } else {
        // Handle token expiration
        if (result.details?.reauth_required) {
          setConnectionStatus({ connected: false, user_id: null, pages_count: 0 });
          setPages([]);
          window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
            detail: { 
              message: 'Facebook connection expired. Please reconnect to continue publishing.', 
              type: 'warning' 
            }
          }));
        } else {
          throw new Error(result.error || 'Failed to publish post');
        }
      }
    } catch (error: any) {
      console.error('Failed to publish to Facebook:', error);
      
      // Handle API errors
      if (error.response?.status === 401) {
        setConnectionStatus({ connected: false, user_id: null, pages_count: 0 });
        setPages([]);
        window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
          detail: { 
            message: 'Facebook connection expired. Please reconnect.', 
            type: 'warning' 
          }
        }));
      } else {
        window.dispatchEvent(new CustomEvent('fbwriter:toast', { 
          detail: { message: `Publish failed: ${error.message}`, type: 'error' }
        }));
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Not connected state
  if (!connectionStatus?.connected) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button
          variant="outlined"
          startIcon={<span>📘</span>}
          onClick={handleConnectFacebook}
          disabled={isConnecting}
          sx={{
            borderColor: '#1877F2',
            color: '#1877F2',
            '&:hover': {
              borderColor: '#166FE5',
              backgroundColor: 'rgba(24, 119, 242, 0.04)',
            },
            borderRadius: 2,
            px: 3,
            py: 1,
            textTransform: 'none',
            fontWeight: 600
          }}
        >
          {isConnecting ? 'Connecting...' : 'Connect Facebook'}
        </Button>
      </Box>
    );
  }

  // Connected but no pages
  if (pages.length === 0) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
        <Button
          variant="outlined"
          disabled
          sx={{
            borderColor: '#666',
            color: '#666',
            borderRadius: 2,
            px: 3,
            py: 1,
            textTransform: 'none'
          }}
        >
          No Facebook Pages Found
        </Button>
      </Box>
    );
  }

  // Connected with pages - show publish UI
  return (
    <Box sx={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: 2, mt: 2 }}>
      <FormControl size="small" sx={{ minWidth: 200 }}>
        <InputLabel sx={{ color: 'rgba(255,255,255,0.7)' }}>Select Page</InputLabel>
        <Select
          value={selectedPageId}
          onChange={(e) => setSelectedPageId(e.target.value)}
          sx={{
            color: 'white',
            '& .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255,255,255,0.3)',
            },
            '&:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: 'rgba(255,255,255,0.5)',
            },
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#1877F2',
            }
          }}
        >
          {pages.map((page) => (
            <MenuItem key={page.id} value={page.id}>
              {page.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      
      <Button
        variant="contained"
        startIcon={isLoading ? <CircularProgress size={16} color="inherit" /> : <span>📘</span>}
        onClick={handlePublish}
        disabled={isLoading || !selectedPageId}
        sx={{
          backgroundColor: '#1877F2',
          '&:hover': {
            backgroundColor: '#166FE5',
          },
          borderRadius: 2,
          px: 3,
          py: 1,
          textTransform: 'none',
          fontWeight: 600
        }}
      >
        {isLoading ? 'Publishing...' : 'Post to Facebook'}
      </Button>
    </Box>
  );
};

// --- Simple localStorage-backed chat memory ---
const HISTORY_KEY = 'fbwriter:chatHistory';
const PREFS_KEY = 'fbwriter:preferences';

type ChatMsg = { role: 'user' | 'assistant'; content: string; ts: number };

function loadHistory(): ChatMsg[] {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    if (!raw) return [];
    const arr = JSON.parse(raw);
    if (!Array.isArray(arr)) return [];
    return arr.filter((m: any) => m && typeof m.content === 'string' && (m.role === 'user' || m.role === 'assistant'));
  } catch { return []; }
}

function saveHistory(msgs: ChatMsg[]) {
  try { localStorage.setItem(HISTORY_KEY, JSON.stringify(msgs.slice(-50))); } catch {}
}

function pushHistory(role: 'user' | 'assistant', content: string) {
  const msgs = loadHistory();
  msgs.push({ role, content: String(content || '').slice(0, 4000), ts: Date.now() });
  saveHistory(msgs);
}

function clearHistory() {
  try { localStorage.removeItem(HISTORY_KEY); } catch {}
}

function getPreferences(): Record<string, any> {
  try { return JSON.parse(localStorage.getItem(PREFS_KEY) || '{}') || {}; } catch { return {}; }
}

function summarizeHistory(maxChars = 1000): string {
  const msgs = loadHistory();
  if (!msgs.length) return '';
  const recent = msgs.slice(-10).map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`);
  const joined = recent.join('\n');
  return joined.length > maxChars ? `${joined.slice(0, maxChars)}…` : joined;
}

function computeEditedText(op: string, src: string): string {
  const opL = (op || '').toLowerCase();
  if (opL === 'shorten') return src.length > 240 ? src.slice(0, 220) + '…' : src;
  if (opL === 'lengthen') return src + '\n\nLearn more at our page!';
  if (opL === 'tightenhook') {
    const lines = src.split('\n');
    if (lines.length) lines[0] = '🔥 ' + lines[0].replace(/^\W+/, '');
    return lines.join('\n');
  }
  if (opL === 'addcta') return src + '\n\n👉 Tell us your thoughts in the comments!';
  if (opL === 'casual') return src.replace(/\b(you will|you should)\b/gi, "you'll").replace(/\bdo not\b/gi, "don't");
  if (opL === 'professional') return src.replace(/\bcan't\b/gi, 'cannot').replace(/\bwon't\b/gi, 'will not');
  if (opL === 'upbeat') return src + ' 🎉';
  return src;
}

function diffMarkup(oldText: string, newText: string): string {
  const MAX = 4000;
  const a = (oldText || '').slice(0, MAX);
  const b = (newText || '').slice(0, MAX);
  const n = a.length, m = b.length;
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(m + 1).fill(0));
  for (let i = n - 1; i >= 0; i--) {
    for (let j = m - 1; j >= 0; j--) {
      if (a[i] === b[j]) dp[i][j] = dp[i + 1][j + 1] + 1;
      else dp[i][j] = Math.max(dp[i + 1][j], dp[i][j + 1]);
    }
  }
  let i = 0, j = 0;
  let out = '';
  while (i < n && j < m) {
    if (a[i] === b[j]) {
      out += a[i];
      i++; j++;
    } else if (dp[i + 1][j] >= dp[i][j + 1]) {
      out += `<s class=\"fbw-del\">${escapeHtml(a[i])}</s>`;
      i++;
    } else {
      out += `<em class=\"fbw-add\">${escapeHtml(b[j])}</em>`;
      j++;
    }
  }
  while (i < n) { out += `<s class=\"fbw-del\">${escapeHtml(a[i++])}</s>`; }
  while (j < m) { out += `<em class=\"fbw-add\">${escapeHtml(b[j++])}</em>`; }
  if (oldText.length > MAX || newText.length > MAX) out += '<span class=\"fbw-more\"> …</span>';
  return out;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function simpleMarkdownToHtml(markdown: string): string {
  // Very small, safe-ish markdown renderer for bold, italics, lists, headings, paragraphs
  // 1) Escape HTML first
  let html = escapeHtml(markdown || '');
  // 2) Headings (##, # at line start)
  html = html.replace(/^###\s+(.*)$/gm, '<h3>$1</h3>');
  html = html.replace(/^##\s+(.*)$/gm, '<h2>$1</h2>');
  html = html.replace(/^#\s+(.*)$/gm, '<h1>$1</h1>');
  // 3) Bold and italics
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
  // 4) Lists: lines starting with * or -
  html = html.replace(/^(?:\*|-)\s+(.+)$/gm, '<li>$1</li>');
  // Wrap consecutive <li> into <ul>
  html = html.replace(/(<li>.*<\/li>)(\s*(<li>.*<\/li>))+/gms, (m) => `<ul>${m}</ul>`);
  // 5) Line breaks → paragraphs
  html = html.replace(/^(?!<h\d>|<ul>|<li>)(.+)$/gm, '<p>$1</p>');
  // Remove paragraphs around list items
  html = html.replace(/<p>(<li>.*?<\/li>)<\/p>/gms, '$1');
  html = html.replace(/<p>(<ul>.*?<\/ul>)<\/p>/gms, '$1');
  return html;
}

interface FacebookWriterProps {
  className?: string;
}

// Enhanced Facebook Writer with Persona Integration
const FacebookWriter: React.FC<FacebookWriterProps> = ({ className = '' }) => {
  // Minimal Facebook-themed palette for local scope
  const fbTheme = React.useMemo(() => createTheme({
    palette: {
      mode: 'dark',
      primary: { 
        main: '#1877f2',
        light: '#42a5f5',
        dark: '#1565c0',
        contrastText: '#ffffff'
      },
      secondary: { 
        main: '#1b74e4',
        light: '#5c9eff',
        dark: '#0d47a1'
      },
      background: {
        default: '#0a0e1a',
        paper: 'rgba(255,255,255,0.05)'
      },
      text: {
        primary: 'rgba(255,255,255,0.95)',
        secondary: 'rgba(255,255,255,0.7)'
      }
    },
    typography: {
      fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
      h1: { fontWeight: 700, fontSize: '2.5rem', lineHeight: 1.2 },
      h2: { fontWeight: 600, fontSize: '2rem', lineHeight: 1.3 },
      h3: { fontWeight: 600, fontSize: '1.5rem', lineHeight: 1.4 },
      h4: { fontWeight: 600, fontSize: '1.25rem', lineHeight: 1.4 },
      h5: { fontWeight: 500, fontSize: '1.125rem', lineHeight: 1.5 },
      h6: { fontWeight: 500, fontSize: '1rem', lineHeight: 1.5 },
      body1: { fontSize: '1rem', lineHeight: 1.6 },
      body2: { fontSize: '0.875rem', lineHeight: 1.5 },
      button: { fontWeight: 600, textTransform: 'none', letterSpacing: 0.5 }
    },
    shape: { borderRadius: 12 },
    components: {
      MuiButton: {
        styleOverrides: {
          root: { 
            borderRadius: 12, 
            textTransform: 'none', 
            letterSpacing: 0.5, 
            fontWeight: 600,
            padding: '12px 24px',
            fontSize: '0.95rem',
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
            '&:hover': {
              transform: 'translateY(-1px)',
              boxShadow: '0 8px 25px rgba(0,0,0,0.15)'
            }
          },
          containedPrimary: { 
            backgroundColor: '#1877f2',
            boxShadow: '0 4px 14px 0 rgba(24,119,242,0.39)',
            '&:hover': {
              backgroundColor: '#166fe5',
              boxShadow: '0 6px 20px 0 rgba(24,119,242,0.5)'
            }
          },
          outlinedPrimary: { 
            borderColor: 'rgba(24,119,242,0.5)', 
            color: '#dbe7ff',
            borderWidth: '1.5px',
            '&:hover': {
              borderColor: '#1877f2',
              backgroundColor: 'rgba(24,119,242,0.08)',
              borderWidth: '1.5px'
            }
          },
          containedSecondary: {
            backgroundColor: 'rgba(255,255,255,0.1)',
            color: 'rgba(255,255,255,0.9)',
            backdropFilter: 'blur(10px)',
            '&:hover': {
              backgroundColor: 'rgba(255,255,255,0.15)'
            }
          }
        }
      },
      MuiPaper: {
        styleOverrides: {
          root: { 
            borderRadius: 16,
            background: 'rgba(255,255,255,0.03)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.1)',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)'
          }
        }
      },
      MuiTypography: {
        styleOverrides: {
          h1: { fontWeight: 700, letterSpacing: '-0.02em' },
          h2: { fontWeight: 600, letterSpacing: '-0.01em' },
          h3: { fontWeight: 600, letterSpacing: '0em' },
          h4: { fontWeight: 600, letterSpacing: '0em' },
          h5: { fontWeight: 500, letterSpacing: '0em' },
          h6: { fontWeight: 500, letterSpacing: '0em' }
        }
      },
      MuiContainer: {
        styleOverrides: {
          root: {
            paddingLeft: '24px',
            paddingRight: '24px'
          }
        }
      },
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            backgroundColor: 'rgba(0,0,0,0.9)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 8,
            fontSize: '0.875rem',
            padding: '8px 12px'
          }
        }
      }
    }
  }), []);

  return (
    <PlatformPersonaProvider platform="facebook">
      <ThemeProvider theme={fbTheme}>
      <FacebookWriterContent className={className} />
      </ThemeProvider>
    </PlatformPersonaProvider>
  );
};

// Main Facebook Writer Content Component
const FacebookWriterContent: React.FC<FacebookWriterProps> = ({ className = '' }) => {
  const [postDraft, setPostDraft] = React.useState<string>('');
  const [notes, setNotes] = React.useState<string>('');
  const [stage, setStage] = React.useState<'start' | 'edit'>('start');
  const [livePreviewHtml, setLivePreviewHtml] = React.useState<string>('');
  const [isPreviewing, setIsPreviewing] = React.useState<boolean>(false);
  const [pendingEdit, setPendingEdit] = React.useState<{ src: string; target: string } | null>(null);
  const [historyVersion, setHistoryVersion] = React.useState<number>(0);
  const [adVariations, setAdVariations] = React.useState<{
    headline_variations: string[];
    primary_text_variations: string[];
    description_variations: string[];
    cta_variations: string[];
  } | null>(null);
  const [storyImages, setStoryImages] = React.useState<string[] | null>(null);
  const renderRef = React.useRef<HTMLDivElement | null>(null);
  const [selectionMenu, setSelectionMenu] = React.useState<{ x: number; y: number; text: string } | null>(null);

  // Get persona context for enhanced AI assistance
  const { corePersona, platformPersona, loading: personaLoading } = usePlatformPersonaContext();
  const [isGenerating, setIsGenerating] = React.useState<boolean>(false);
  const [health, setHealth] = React.useState<any>(null);
  const [busyCount, setBusyCount] = React.useState<number>(0);
  const [showProgress, setShowProgress] = React.useState<boolean>(false);
  const [generationType, setGenerationType] = React.useState<'post' | 'hashtags' | 'ad_copy' | 'story' | 'reel' | 'carousel' | 'event' | 'page_about'>('post');

  React.useEffect(() => {
    const onUpdate = (e: any) => {
      setPostDraft(String(e.detail || ''));
      setStage('edit');
    };
    const onAppend = (e: any) => {
      setPostDraft(prev => (prev || '') + String(e.detail || ''));
      setStage('edit');
    };
    const onAssistantMessage = (e: any) => {
      const content = e?.detail?.content ?? e?.detail ?? '';
      if (!content) return;
        pushHistory('assistant', String(content));
        setHistoryVersion(v => v + 1);
      
      // Enhanced content extraction and synchronization
      try {
        const raw = String(content || '');
        console.log('[Facebook Writer] Assistant message received:', raw.substring(0, 100) + '...');
        
        // More comprehensive content extraction patterns
        let clean = raw
          // Remove common prefixes
          .replace(/^Here\'s a[^:]*:\s*/i, '')
          .replace(/^Here is a[^:]*:\s*/i, '')
          .replace(/^Facebook post[:\s]*/i, '')
          .replace(/^Here\'s your[^:]*:\s*/i, '')
          .replace(/^Your[^:]*:\s*/i, '')
          .replace(/^Generated[^:]*:\s*/i, '')
          .replace(/^Content[^:]*:\s*/i, '')
          // Remove code blocks and markdown
          .replace(/```[\s\S]*?```/g, '')
          .replace(/`[^`]*`/g, '')
          // Remove action results and tool calls
          .replace(/\[Action[^\]]*\]/g, '')
          .replace(/\[Tool[^\]]*\]/g, '')
          .replace(/Success: true[^\n]*/g, '')
          .replace(/Generated successfully[^\n]*/g, '')
          .trim();
        
        console.log('[Facebook Writer] Cleaned content:', clean.substring(0, 100) + '...');
        
        // Enhanced post detection patterns
        const hasHashtags = /#[A-Za-z0-9_]+/.test(clean);
        const hasEmojis = /[🚀🎉✅✨💡📢📚🎬🖼️📅ℹ️]/.test(clean);
        const hasMultipleLines = clean.split('\n').length >= 2;
        const hasCallToAction = /(visit|check|learn|discover|explore|try|get|start|join|follow|share|comment|like)/i.test(clean);
        const hasEngagementWords = /(challenge|solution|benefit|feature|launch|announce|excited|thrilled)/i.test(clean);
        
        const looksLikePost = hasHashtags || hasEmojis || hasMultipleLines || hasCallToAction || hasEngagementWords;
        const isSubstantialContent = clean.length > 30;
        
        console.log('[Facebook Writer] Post detection:', {
          hasHashtags,
          hasEmojis,
          hasMultipleLines,
          hasCallToAction,
          hasEngagementWords,
          looksLikePost,
          isSubstantialContent,
          contentLength: clean.length
        });
        
        if (looksLikePost && isSubstantialContent) {
          console.log('[Facebook Writer] Syncing content to draft');
          setPostDraft(clean);
          setStage('edit');
        } else {
          console.log('[Facebook Writer] Content does not match post pattern, not syncing');
        }
      } catch (error) {
        console.error('[Facebook Writer] Error processing assistant message:', error);
      }
    };
    const onApplyEdit = (e: any) => {
      const op = (e?.detail?.operation || '').toLowerCase();
      const src = postDraft || '';
      const target = computeEditedText(op, src);
      setIsPreviewing(true);
      setStage('edit');
      setPendingEdit({ src, target });
      let idx = 0;
      const total = target.length;
      const intervalMs = 20;
      const step = Math.max(1, Math.floor(total / 120)); // ~2 seconds
      const interval = setInterval(() => {
        idx += step;
        if (idx >= total) idx = total;
        const partial = target.slice(0, idx);
        setLivePreviewHtml(diffMarkup(src, partial));
        if (idx === total) {
          clearInterval(interval);
          // Keep preview open and wait for user to confirm or discard.
        }
      }, intervalMs);
    };
    window.addEventListener('fbwriter:updateDraft', onUpdate as any);
    window.addEventListener('fbwriter:appendDraft', onAppend as any);
    window.addEventListener('fbwriter:assistantMessage', onAssistantMessage as any);
    const onAdVariations = (e: any) => {
      const v = e?.detail;
      if (v) setAdVariations(v);
    };
    const onStoryImages = (e: any) => {
      const imgs = e?.detail;
      if (Array.isArray(imgs) && imgs.length) setStoryImages(imgs);
    };
    window.addEventListener('fbwriter:applyEdit', onApplyEdit as any);
    window.addEventListener('fbwriter:adVariations', onAdVariations as any);
    window.addEventListener('fbwriter:storyImages', onStoryImages as any);
    const onGenStart = () => {
      setIsGenerating(true);
      setShowProgress(true);
    };
    const onGenEnd = () => {
      setIsGenerating(false);
      setShowProgress(false);
    };
    const onSyncContent = () => {
      console.log('[Facebook Writer] Manual sync triggered');
      // Force a re-evaluation of the current content
      if (postDraft) {
        console.log('[Facebook Writer] Current draft content:', postDraft.substring(0, 100) + '...');
      }
    };
    const onSetGenerationType = (e: any) => {
      const type = e.detail || 'post';
      if (['post', 'hashtags', 'ad_copy', 'story', 'reel', 'carousel', 'event', 'page_about'].includes(type)) {
        setGenerationType(type as 'post' | 'hashtags' | 'ad_copy' | 'story' | 'reel' | 'carousel' | 'event' | 'page_about');
      }
    };
    window.addEventListener('fbwriter:generatingStart', onGenStart as any);
    window.addEventListener('fbwriter:generatingEnd', onGenEnd as any);
    window.addEventListener('fbwriter:syncContent', onSyncContent as any);
    window.addEventListener('fbwriter:setGenerationType', onSetGenerationType as any);
    return () => {
      window.removeEventListener('fbwriter:updateDraft', onUpdate as any);
      window.removeEventListener('fbwriter:appendDraft', onAppend as any);
      window.removeEventListener('fbwriter:assistantMessage', onAssistantMessage as any);
      window.removeEventListener('fbwriter:applyEdit', onApplyEdit as any);
      window.removeEventListener('fbwriter:adVariations', onAdVariations as any);
      window.removeEventListener('fbwriter:storyImages', onStoryImages as any);
      window.removeEventListener('fbwriter:generatingStart', onGenStart as any);
      window.removeEventListener('fbwriter:generatingEnd', onGenEnd as any);
      window.removeEventListener('fbwriter:syncContent', onSyncContent as any);
      window.removeEventListener('fbwriter:setGenerationType', onSetGenerationType as any);
    };
  }, [postDraft]);

  // Health check effect
  React.useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await fetch('/api/facebook-writer/health');
        const data = await response.json();
        setHealth(data);
      } catch (error) {
        console.error('Health check failed:', error);
        setHealth({ status: 'unhealthy' });
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Busy state tracking
  React.useEffect(() => {
    const onBusy = () => setBusyCount(prev => prev + 1);
    const onIdle = () => setBusyCount(prev => Math.max(0, prev - 1));
    
    window.addEventListener('fbwriter:busy', onBusy);
    window.addEventListener('fbwriter:idle', onIdle);
    
    return () => {
      window.removeEventListener('fbwriter:busy', onBusy);
      window.removeEventListener('fbwriter:idle', onIdle);
    };
  }, []);

  // Share current draft and notes with Copilot
  useCopilotReadable({
    description: 'Current Facebook post draft text the user is editing - this is the main content that should be used for all operations',
    value: postDraft,
    categories: ['social', 'facebook', 'draft']
  });
  useCopilotReadable({
    description: 'User notes/context for the next Facebook post',
    value: notes,
    categories: ['social', 'facebook', 'context']
  });

  // Allow Copilot to update the draft directly (predictive state-like edit)
  useCopilotActionTyped({
    name: 'updateFacebookPostDraft',
    description: 'Replace the Facebook post draft with provided content',
    parameters: [
      { name: 'content', type: 'string', description: 'The full post content to set', required: true }
    ],
    handler: async ({ content }: { content: string }) => {
      setPostDraft(content);
      setStage('edit');
      return { success: true, message: 'Draft updated' };
    }
  });

  // Let Copilot append text to the draft (collaborative editing)
  useCopilotActionTyped({
    name: 'appendToFacebookPostDraft',
    description: 'Append text to the current Facebook post draft',
    parameters: [
      { name: 'content', type: 'string', description: 'The text to append', required: true }
    ],
    handler: async ({ content }: { content: string }) => {
      setPostDraft(prev => (prev ? `${prev}\n\n${content}` : content));
      setStage('edit');
      return { success: true, message: 'Text appended' };
    }
  });

  // Ensure Copilot always works with the current draft content
  useCopilotActionTyped({
    name: 'getCurrentFacebookDraft',
    description: 'Get the current Facebook post draft content for reference',
    parameters: [],
    handler: async () => {
      return { 
        success: true, 
        content: postDraft,
        message: 'Current draft content retrieved',
        length: postDraft.length
      };
    }
  });

  // Sync content between draft and Copilot
  useCopilotActionTyped({
    name: 'syncFacebookContent',
    description: 'Ensure the Copilot content matches the current draft content',
    parameters: [],
    handler: async () => {
      // This action ensures that any content generated by Copilot
      // is immediately synced to the draft
      return { 
        success: true, 
        content: postDraft,
        message: 'Content synchronized between draft and Copilot',
        draft_content: postDraft
      };
    }
  });

  const startSuggestions = [
    { title: '🎉 Launch teaser', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookPost to write a short Facebook post announcing our new feature launch.' },
    { title: '💡 Benefit-first', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookPost to draft a benefit-first Facebook post with a strong CTA.' },
    { title: '🏷️ Hashtags', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookHashtags to suggest 5 relevant hashtags for this post.' },
    { title: '📢 Ad copy (primary text)', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookAdCopy to create ad copy tailored for conversions.' },
    { title: '📚 Story', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookStory to create a Facebook Story script with tone and visuals.' },
    { title: '🎬 Reel script', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookReel to draft a 30-60 seconds fast-paced product demo reel with hook, scenes, and CTA.' },
    { title: '🖼️ Carousel', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookCarousel to create a 5-slide Product showcase carousel with a main caption and CTA.' },
    { title: '📅 Event', message: 'First, use tool getCurrentFacebookDraft to see the current content, then use tool generateFacebookEvent to create a Virtual Webinar event description with title, highlights, and CTA.' },
    { title: 'ℹ️ Page About', message: 'Use tool generateFacebookPageAbout to create a comprehensive Facebook Page About section with business details and contact information.' }
  ];
  const editSuggestions = [
    { title: '🙂 Make it casual', message: 'Use tool editFacebookDraft with operation Casual' },
    { title: '💼 Make it professional', message: 'Use tool editFacebookDraft with operation Professional' },
    { title: '✨ Tighten hook', message: 'Use tool editFacebookDraft with operation TightenHook' },
    { title: '📣 Add a CTA', message: 'Use tool editFacebookDraft with operation AddCTA' },
    { title: '✂️ Shorten', message: 'Use tool editFacebookDraft with operation Shorten' },
    { title: '➕ Lengthen', message: 'Use tool editFacebookDraft with operation Lengthen' }
  ];

  // Stage-aware suggestion refinement
  const hasCTA = /\b(call now|sign up|join|try|learn more|cta|comment|share|buy|shop)\b/i.test(postDraft);
  const hasHashtags = /#[A-Za-z0-9_]+/.test(postDraft);
  const isLong = (postDraft || '').length > 500;
  const refinedEdit = [
    ...editSuggestions,
    ...(isLong ? [{ title: '📝 Summarize intro', message: 'Use tool editFacebookDraft with operation Shorten' }] : []),
    ...(!hasCTA ? [{ title: '📣 Add a CTA', message: 'Use tool editFacebookDraft with operation AddCTA' }] : []),
    ...(!hasHashtags ? [{ title: '🏷️ Add hashtags', message: 'Use tool generateFacebookHashtags' }] : [])
  ];
  const suggestions = stage === 'start' ? startSuggestions : refinedEdit;

  return (
    <CopilotSidebar
      className="alwrity-copilot-sidebar"
      labels={{
        title: 'ALwrity • Facebook Writer',
        initial: stage === 'start' ? 
          `Tell me what you want to post. I can draft, refine, and generate variants${corePersona ? ` with ${corePersona.persona_name} persona optimization` : ''}.` : 
          `Great! Try quick edits below to refine your post in real-time${corePersona ? ` using your ${corePersona.persona_name} persona` : ''}.`
      }}
      suggestions={suggestions}
      makeSystemMessage={(_context: string, additional?: string) => {
        const prefs = getPreferences();
        const prefsLine = Object.keys(prefs).length ? `User preferences (remember and respect unless changed): ${JSON.stringify(prefs)}` : '';
        const history = summarizeHistory();
        const historyLine = history ? `Recent conversation (last 10 messages):\n${history}` : '';
        const currentDraft = postDraft ? `Current draft content:\n${postDraft}` : 'No current draft content.';
        
        // Enhanced persona-aware guidance
        const personaGuidance = corePersona && platformPersona ? `
PERSONA-AWARE WRITING GUIDANCE:
- PERSONA: ${corePersona.persona_name} (${corePersona.archetype})
- CORE BELIEF: ${corePersona.core_belief}
- CONFIDENCE SCORE: ${corePersona.confidence_score}%
- LINGUISTIC STYLE: ${corePersona.linguistic_fingerprint?.sentence_metrics?.average_sentence_length_words || 'Unknown'} words average, ${corePersona.linguistic_fingerprint?.sentence_metrics?.active_to_passive_ratio || 'Unknown'} active/passive ratio
- GO-TO WORDS: ${corePersona.linguistic_fingerprint?.lexical_features?.go_to_words?.join(', ') || 'None specified'}
- AVOID WORDS: ${corePersona.linguistic_fingerprint?.lexical_features?.avoid_words?.join(', ') || 'None specified'}

PLATFORM OPTIMIZATION (Facebook):
- CHARACTER LIMIT: ${platformPersona.content_format_rules?.character_limit || '63206'} characters
- OPTIMAL LENGTH: ${platformPersona.content_format_rules?.optimal_length || '40-80 characters'}
- ENGAGEMENT PATTERN: ${platformPersona.engagement_patterns?.posting_frequency || '1-2 times per day'}
- HASHTAG STRATEGY: ${platformPersona.lexical_features?.hashtag_strategy || '1-2 relevant hashtags'}

ALWAYS generate content that matches this persona's linguistic fingerprint and platform optimization rules.` : '';

        const guidance = `
You are ALwrity's Facebook Writing Assistant specializing in engaging social media content.

CRITICAL CONSTRAINTS:
- TONE: Always maintain an engaging, community-focused tone
- PLATFORM: Focus specifically on Facebook's unique characteristics and audience
- QUALITY: Ensure all content meets Facebook's community standards
${personaGuidance ? `\n${personaGuidance}` : ''}

CURRENT CONTEXT:
${currentDraft}

Available Facebook content tools:
- generateFacebookPost: Create engaging Facebook posts with persona optimization
- generateFacebookHashtags: Generate relevant hashtags for Facebook content
- generateFacebookAdCopy: Create conversion-focused ad copy
- generateFacebookStory: Create Facebook Story scripts
- generateFacebookReel: Create Facebook Reel scripts
- generateFacebookCarousel: Create multi-slide carousel content
- generateFacebookEvent: Create event descriptions
- generateFacebookPageAbout: Create page about sections

🎭 ENHANCED PERSONA-AWARE ACTIONS (Recommended):
- generateFacebookPostWithPersona: Create posts optimized for your writing style and platform constraints
- validateContentAgainstPersona: Validate existing content against your persona
- getPersonaWritingSuggestions: Get personalized writing recommendations

DIRECT DRAFT ACTIONS:
- updateFacebookPostDraft: Replace the entire draft with new content
- appendToFacebookPostDraft: Add text to the existing draft
- editFacebookDraft: Apply quick edits (Casual, Professional, Upbeat, Shorten, Lengthen, TightenHook, AddCTA) to the current draft

IMPORTANT: When refining or editing content, always reference the current draft above. If the user asks to refine their post, use the current draft content as the starting point. Never ask for content that already exists in the draft.

For quick edits, use editFacebookDraft with the appropriate operation. This will show a live preview of changes before applying them.

Use user preferences, context, conversation history, and persona data to personalize all content.
Always respect the user's preferred tone, platform focus, and writing persona style.
Always use the most appropriate tool for the user's request.`.trim();
        return [prefsLine, historyLine, currentDraft, guidance, additional].filter(Boolean).join('\n\n');
      }}
      observabilityHooks={{
        onChatExpanded: () => console.log('[FB Writer] Sidebar opened'),
        onMessageSent: (m: any) => { console.log('[FB Writer] Message sent', m); try { const text = typeof m === 'string' ? m : (m?.content ?? ''); if (text) { pushHistory('user', String(text)); setHistoryVersion(v => v + 1); } } catch {} },
        onFeedbackGiven: (id: string, type: string) => console.log('[FB Writer] Feedback', { id, type })
      }}
    >
      <RegisterFacebookActions />
      <RegisterFacebookEditActions />
      {/* Enhanced Persona-Aware Actions */}
      <RegisterFacebookActionsEnhanced />
      <Box
        sx={{
          minHeight: '100vh',
          position: 'relative',
          color: 'rgba(255,255,255,0.95)',
          background: `
            radial-gradient(1400px 800px at -20% -30%, rgba(24,119,242,0.15) 0%, transparent 50%),
            radial-gradient(1000px 600px at 120% 20%, rgba(11, 88, 195,0.12) 0%, transparent 50%),
            radial-gradient(800px 400px at 50% 100%, rgba(24,119,242,0.08) 0%, transparent 60%),
            linear-gradient(135deg, #0a0e1a 0%, #0f1a2e 25%, #1a2332 50%, #0f2559 75%, #0b4da6 100%)
          `,
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: `
              radial-gradient(circle at 20% 80%, rgba(24,119,242,0.1) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(11, 88, 195,0.08) 0%, transparent 50%),
              radial-gradient(circle at 40% 40%, rgba(24,119,242,0.05) 0%, transparent 50%)
            `,
            pointerEvents: 'none'
          }
        }}
      >
        {/* Back to Dashboard Button - Top Left */}
        <Button
          variant="contained"
          component="a"
          href="/"
          startIcon={<span style={{ fontSize: '16px' }}>←</span>}
          sx={{
            position: 'fixed',
            top: 20,
            left: 20,
            zIndex: 2000,
            background: 'linear-gradient(135deg, #1877f2 0%, #1b74e4 100%)',
            color: 'white',
            fontWeight: 600,
            borderRadius: 2,
            px: 3,
            py: 1.5,
            boxShadow: '0 4px 20px rgba(24,119,242,0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #166fe5 0%, #1557c0 100%)',
              boxShadow: '0 6px 25px rgba(24,119,242,0.4)',
              transform: 'translateY(-1px)'
            },
            transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          Back to Dashboard
        </Button>
        <Container maxWidth="lg" sx={{ position: 'relative', zIndex: 1, pt: 4, pb: 6 }}>
          {/* Enterprise Hero Section */}
          <Box sx={{ textAlign: 'center', mb: 6 }}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h2" sx={{ 
                fontWeight: 700,
                background: 'linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                mb: 2
              }}>
                Facebook Content Studio
              </Typography>
              <Typography variant="h5" sx={{ 
                color: 'rgba(255,255,255,0.8)',
                fontWeight: 400,
                mb: 3
              }}>
                Create compelling Facebook posts with AI-powered assistance
            </Typography>
          </Box>
          
            {/* Professional Stats Cards */}
            <Box sx={{ 
                display: 'flex',
              justifyContent: 'center', 
              gap: 3, 
              mb: 4,
              flexWrap: 'wrap'
            }}>
              <Paper sx={{ 
                p: 2, 
                minWidth: 140,
                textAlign: 'center',
                background: 'rgba(24,119,242,0.1)',
                border: '1px solid rgba(24,119,242,0.2)'
              }}>
                <Typography variant="h6" sx={{ color: '#1877f2', fontWeight: 600 }}>
                  AI-Powered
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  Smart Content Generation
                </Typography>
              </Paper>
              <Paper sx={{ 
                p: 2, 
                minWidth: 140,
                textAlign: 'center',
                background: 'rgba(76,175,80,0.1)',
                border: '1px solid rgba(76,175,80,0.2)'
              }}>
                <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 600 }}>
                  Optimized
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  For Maximum Engagement
                </Typography>
              </Paper>
              <Paper sx={{ 
                p: 2, 
                minWidth: 140,
                textAlign: 'center',
                background: 'rgba(255,193,7,0.1)',
                border: '1px solid rgba(255,193,7,0.2)'
              }}>
                <Typography variant="h6" sx={{ color: '#ffc107', fontWeight: 600 }}>
                  Professional
                </Typography>
                <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                  Enterprise-Grade Tools
                </Typography>
              </Paper>
            </Box>
          </Box>
          

          {/* Professional Action Center */}
          <Paper sx={{ 
            p: 4, 
            mb: 4,
            background: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: 3
          }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ 
                color: 'rgba(255,255,255,0.95)', 
                fontWeight: 600,
                mb: 1
              }}>
                {postDraft || isGenerating ? 'Content Management' : 'Start Creating Your Content'}
              </Typography>
              <Typography variant="body1" sx={{ 
                color: 'rgba(255,255,255,0.7)',
                maxWidth: 600,
                mx: 'auto'
              }}>
                {postDraft || isGenerating 
                  ? 'Your content is ready for review and publishing'
                  : 'Collaborate with our AI assistant to craft engaging Facebook posts that resonate with your audience'
                }
              </Typography>
            </Box>
            
            {/* Professional Action Buttons */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'center',
              mb: 3
            }}>
              <Button 
                variant="contained" 
                size="large"
                onClick={() => {
                  try {
                    window.dispatchEvent(new CustomEvent('copilot:open'));
                    window.dispatchEvent(new CustomEvent('openCopilot'));
                    const selectors = [
                      '[data-copilot-toggle]',
                      '.copilotkit-toggle',
                      '.copilotkit-chat-toggle',
                      '.alwrity-copilot-sidebar button',
                      '.copilot-sidebar button',
                    ];
                    for (const sel of selectors) {
                      const el = document.querySelector(sel) as HTMLButtonElement | null;
                      if (el) { el.click(); return; }
                    }
                    const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
                    const target = buttons.find(b => (b.textContent || '').match(/open|assistant|copilot|chat/i));
                    if (target) { target.click(); }
                  } catch {}
                }} 
                sx={{ 
                  px: 4, 
                  py: 2, 
                  fontSize: '1.1rem',
                  minWidth: 200,
                  background: 'linear-gradient(135deg, #1877f2 0%, #1b74e4 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #166fe5 0%, #1565c0 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: '0 8px 25px rgba(24,119,242,0.4)'
                  }
                }}
              >
                {postDraft || isGenerating ? '🤖 Continue with AI' : '🤖 Start with AI Assistant'}
              </Button>
            </Box>
            
             {/* Professional Features Grid */}
             <Box sx={{ 
               display: 'grid', 
               gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(3, 1fr)' },
               gap: 2,
               mt: 3
             }}>
               <Box sx={{ textAlign: 'center', p: 2 }}>
                 <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 500 }}>
                   Optimal Length
          </Typography>
                 <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                   {platformPersona?.content_format_rules?.optimal_length || '40-80 words'}
                 </Typography>
               </Box>
               <Box sx={{ textAlign: 'center', p: 2 }}>
                 <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 500 }}>
                   Posting Frequency
                 </Typography>
                 <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                   {platformPersona?.engagement_patterns?.posting_frequency || '1-2 times per day'}
                 </Typography>
               </Box>
               <Box sx={{ textAlign: 'center', p: 2 }}>
                 <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', fontWeight: 500 }}>
                   Hashtag Strategy
                 </Typography>
                 <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                   {platformPersona?.lexical_features?.hashtag_strategy || '1-2 relevant hashtags'}
                 </Typography>
               </Box>
             </Box>
          </Paper>

          {/* Professional Draft Section - Progressive Disclosure */}
          {(postDraft || isGenerating) && (
            <Paper sx={{ 
              p: 4,
              background: 'linear-gradient(135deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.03) 100%)',
              border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: 3,
              position: 'relative'
            }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
              <Typography variant="h5" sx={{ 
                color: 'rgba(255,255,255,0.95)', 
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 1
              }}>
                📝 Content Draft
                {isGenerating && (
                  <Box sx={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 1,
                    ml: 2,
                    px: 2,
                    py: 0.5,
                    background: 'rgba(24,119,242,0.1)',
                    borderRadius: 2,
                    border: '1px solid rgba(24,119,242,0.2)'
                  }}>
                    <Box sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: '#1877f2',
                      animation: 'pulse 1.5s ease-in-out infinite'
                    }} />
                    <Typography variant="caption" sx={{ color: '#1877f2', fontWeight: 500 }}>
                      Generating content...
            </Typography>
                  </Box>
                )}
              </Typography>
              
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <Button 
                  size="small" 
                  variant="outlined" 
                  onClick={() => { clearHistory(); setHistoryVersion(v => v + 1); }}
            sx={{
                    color: 'rgba(255,255,255,0.7)',
                    borderColor: 'rgba(255,255,255,0.2)',
                    fontSize: '0.875rem',
                    '&:hover': {
                      borderColor: 'rgba(255,255,255,0.4)',
                      backgroundColor: 'rgba(255,255,255,0.05)'
                    }
                  }}
                >
                  Clear Memory
                </Button>
            </Box>
            </Box>
            {/* Professional Draft Content Area */}
            <Box data-testid="post-draft"
              ref={renderRef}
                sx={{
                minHeight: 200,
                p: 3,
                background: 'rgba(255,255,255,0.02)',
                border: '2px dashed rgba(255,255,255,0.1)',
                borderRadius: 2,
                position: 'relative',
                '&:hover': {
                  borderColor: 'rgba(255,255,255,0.2)',
                  background: 'rgba(255,255,255,0.03)'
                }
              }}
            >
              {postDraft ? (
                <Box sx={{ 
                  whiteSpace: 'pre-wrap',
                  lineHeight: 1.6,
                  color: 'rgba(255,255,255,0.9)',
                  fontSize: '1rem'
                }}>
                  {postDraft}
                </Box>
              ) : isGenerating ? (
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  minHeight: 120,
                  flexDirection: 'column',
                  gap: 2
                }}>
                  <Box sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    border: '3px solid rgba(24,119,242,0.3)',
                    borderTop: '3px solid #1877f2',
                    animation: 'spin 1s linear infinite'
                  }} />
                  <Typography variant="body1" sx={{ 
                    color: 'rgba(255,255,255,0.7)',
                    fontWeight: 500
                  }}>
                    Generating your content...
                </Typography>
                </Box>
              ) : (
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  minHeight: 120,
                  flexDirection: 'column',
                  gap: 2,
                  textAlign: 'center'
                }}>
                  <Box sx={{
                    width: 48,
                    height: 48,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, rgba(24,119,242,0.1) 0%, rgba(11,88,195,0.05) 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '24px'
                  }}>
                    📝
                  </Box>
                  <Typography variant="h6" sx={{ 
                    color: 'rgba(255,255,255,0.8)',
                    fontWeight: 500
                  }}>
                    Your content will appear here
                  </Typography>
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.6)',
                    maxWidth: 400
                  }}>
                    Use the AI assistant above to generate engaging Facebook posts, or start typing to create your own content
                  </Typography>
                  </Box>
                )}
            </Box>
            
            {/* Professional Action Bar */}
            <Box sx={{ 
              display: 'flex', 
              justifyContent: 'space-between', 
              alignItems: 'center',
              mt: 3,
              pt: 3,
              borderTop: '1px solid rgba(255,255,255,0.1)'
            }}>
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Button 
                  variant="outlined" 
                  size="small"
                  onClick={() => {
                    try {
                      window.dispatchEvent(new CustomEvent('copilot:open'));
                      window.dispatchEvent(new CustomEvent('openCopilot'));
                      const selectors = [
                        '[data-copilot-toggle]',
                        '.copilotkit-toggle',
                        '.copilotkit-chat-toggle',
                        '.alwrity-copilot-sidebar button',
                        '.copilot-sidebar button',
                      ];
                      for (const sel of selectors) {
                        const el = document.querySelector(sel) as HTMLButtonElement | null;
                        if (el) { el.click(); return; }
                      }
                      const buttons = Array.from(document.querySelectorAll('button')) as HTMLButtonElement[];
                      const target = buttons.find(b => (b.textContent || '').match(/open|assistant|copilot|chat/i));
                      if (target) { target.click(); }
                    } catch {}
              }}
              sx={{
                    fontSize: '0.875rem',
                    px: 3,
                    py: 1
                  }}
                >
                  🤖 Open AI Assistant
                </Button>
              </Box>
              
              {/* Post to Facebook Button */}
              <FacebookPostButton postContent={postDraft || ''} />
              </Box>
            </Paper>
          )}

          {/* Professional Status Indicators */}
          {health && (
            <Box sx={{ 
              position: 'fixed', 
              top: 80, 
              right: 24, 
              zIndex: 1500 
            }}>
              <Paper sx={{ 
                p: 2, 
                background: health.status === 'healthy' 
                  ? 'linear-gradient(135deg, rgba(76,175,80,0.15) 0%, rgba(76,175,80,0.08) 100%)'
                  : 'linear-gradient(135deg, rgba(244,67,54,0.15) 0%, rgba(244,67,54,0.08) 100%)',
                border: `1px solid ${health.status === 'healthy' ? 'rgba(76,175,80,0.3)' : 'rgba(244,67,54,0.3)'}`,
                borderRadius: 2,
                backdropFilter: 'blur(10px)'
              }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{
                    width: 8,
                    height: 8,
                    borderRadius: '50%',
                    backgroundColor: health.status === 'healthy' ? '#4caf50' : '#f44336',
                    boxShadow: `0 0 8px ${health.status === 'healthy' ? 'rgba(76,175,80,0.5)' : 'rgba(244,67,54,0.5)'}`
                  }} />
                  <Typography variant="body2" sx={{ 
                    color: 'rgba(255,255,255,0.9)',
                    fontWeight: 500
                  }}>
                    {health.status === 'healthy' ? 'System Online' : 'System Issues'}
              </Typography>
                  {busyCount > 0 && (
                    <Typography variant="caption" sx={{ 
                      color: 'rgba(255,255,255,0.7)',
                      ml: 1
                    }}>
                      ({busyCount} active)
                    </Typography>
                  )}
              </Box>
            </Paper>
            </Box>
          )}
          
          {/* CSS Animations */}
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
            @keyframes pulse {
              0%, 100% { opacity: 1; }
              50% { opacity: 0.5; }
            }
          `}</style>
        </Container>
        
        {/* Content Generation Progress */}
        <ContentGenerationProgress
          isVisible={showProgress}
          onClose={() => setShowProgress(false)}
          onComplete={(result) => {
            console.log('Content generation completed:', result);
            setShowProgress(false);
            setIsGenerating(false);
          }}
          onError={(error) => {
            console.error('Content generation error:', error);
            setShowProgress(false);
            setIsGenerating(false);
          }}
          generationType={generationType}
        />
      </Box>
    </CopilotSidebar>
  );
};

export default FacebookWriter;


