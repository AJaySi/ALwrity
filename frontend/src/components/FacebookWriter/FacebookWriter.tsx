import React from 'react';
import { Box, Container, Typography, TextField, Paper, Button } from '@mui/material';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotReadable, useCopilotAction } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import RegisterFacebookActions from './RegisterFacebookActions';
import RegisterFacebookEditActions from './RegisterFacebookEditActions';
import RegisterFacebookActionsEnhanced from './RegisterFacebookActionsEnhanced';
import { PlatformPersonaProvider, usePlatformPersonaContext } from '../shared/PersonaContext/PlatformPersonaProvider';

const useCopilotActionTyped = useCopilotAction as any;

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
  return (
    <PlatformPersonaProvider platform="facebook">
      <FacebookWriterContent className={className} />
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
      if (content) {
        pushHistory('assistant', String(content));
        setHistoryVersion(v => v + 1);
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
    return () => {
      window.removeEventListener('fbwriter:updateDraft', onUpdate as any);
      window.removeEventListener('fbwriter:appendDraft', onAppend as any);
      window.removeEventListener('fbwriter:assistantMessage', onAssistantMessage as any);
      window.removeEventListener('fbwriter:applyEdit', onApplyEdit as any);
      window.removeEventListener('fbwriter:adVariations', onAdVariations as any);
      window.removeEventListener('fbwriter:storyImages', onStoryImages as any);
    };
  }, [postDraft]);

  // Share current draft and notes with Copilot
  useCopilotReadable({
    description: 'Current Facebook post draft text the user is editing',
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

  const startSuggestions = [
    { title: '🎉 Launch teaser', message: 'Use tool generateFacebookPost to write a short Facebook post announcing our new feature launch.' },
    { title: '💡 Benefit-first', message: 'Use tool generateFacebookPost to draft a benefit-first Facebook post with a strong CTA.' },
    { title: '🏷️ Hashtags', message: 'Use tool generateFacebookHashtags to suggest 5 relevant hashtags for this post.' },
    { title: '📢 Ad copy (primary text)', message: 'Use tool generateFacebookAdCopy to create ad copy tailored for conversions.' },
    { title: '📚 Story', message: 'Use tool generateFacebookStory to create a Facebook Story script with tone and visuals.' },
    { title: '🎬 Reel script', message: 'Use tool generateFacebookReel to draft a 30-60 seconds fast-paced product demo reel with hook, scenes, and CTA.' },
    { title: '🖼️ Carousel', message: 'Use tool generateFacebookCarousel to create a 5-slide Product showcase carousel with a main caption and CTA.' },
    { title: '📅 Event', message: 'Use tool generateFacebookEvent to create a Virtual Webinar event description with title, highlights, and CTA.' },
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
          color: 'rgba(255,255,255,0.92)',
          background:
            'radial-gradient(1200px 600px at -10% -20%, rgba(24,119,242,0.25) 0%, transparent 60%),' +
            'radial-gradient(900px 500px at 110% 10%, rgba(11, 88, 195, 0.25) 0%, transparent 60%),' +
            'linear-gradient(135deg, #0b1a3a 0%, #0f2559 35%, #0f3a7a 70%, #0b4da6 100%)',
        }}
      >
        <Container maxWidth="md" sx={{ position: 'relative', zIndex: 1, py: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h4" sx={{ fontWeight: 800, letterSpacing: 0.3 }}>
              Facebook Writer (Preview)
            </Typography>
          </Box>
          
          {/* Persona Integration Indicator */}
          {corePersona && !personaLoading && (
            <div 
              style={{
                padding: '8px 16px',
                backgroundColor: 'rgba(24, 119, 242, 0.1)',
                borderBottom: '1px solid rgba(24, 119, 242, 0.3)',
                fontSize: '12px',
                color: 'rgba(255, 255, 255, 0.8)',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'help',
                position: 'relative',
                marginBottom: '16px',
                borderRadius: '8px',
                border: '1px solid rgba(24, 119, 242, 0.2)'
              }}
              title={`🎭 YOUR PERSONALIZED WRITING ASSISTANT

🤔 WHAT IS A PERSONA?
A persona is your unique writing style profile that AI uses to create content that sounds exactly like you. It's like having a digital twin of your writing voice!

🎯 HOW DOES IT HELP YOU?
✅ Generates content that matches your natural writing style
✅ Maintains consistent voice across all your Facebook posts
✅ Saves time by understanding your preferences automatically
✅ Optimizes content for Facebook's algorithm and your audience
✅ Provides personalized suggestions based on your industry

🧠 HOW WAS IT CREATED?
Your persona was built by analyzing:
• Your website content and writing patterns
• Your research preferences and content goals
• Your target audience and industry focus
• Your communication style and tone preferences
• Facebook-specific optimization requirements

🤖 HOW DOES COPILOTKIT USE IT?
The AI assistant now knows:
• Your preferred sentence length and structure
• Your go-to words and phrases to use/avoid
• Your professional tone and communication style
• Facebook-specific optimization strategies
• Your engagement patterns and posting preferences

🚀 HYPER-PERSONALIZATION ACHIEVED!
Instead of generic content, you get:
• Content that sounds authentically like you
• Industry-specific insights and terminology
• Facebook algorithm-optimized posts
• Community engagement strategies
• Personalized conversion tactics

📊 YOUR PERSONA DETAILS:
🎭 Name: ${corePersona.persona_name}
📋 Style: ${corePersona.archetype}
💭 Philosophy: ${corePersona.core_belief}
📈 Confidence: ${corePersona.confidence_score}% accuracy

🎯 FACEBOOK OPTIMIZATION:
• Optimal length: ${platformPersona?.content_format_rules?.optimal_length || '40-80 words'}
• Posting frequency: ${platformPersona?.engagement_patterns?.posting_frequency || '1-2 times per day'}
• Hashtag strategy: ${platformPersona?.lexical_features?.hashtag_strategy || '1-2 relevant hashtags'}
• Engagement style: ${platformPersona?.engagement_patterns?.interaction_style || 'community-focused'}

💡 TRY THIS: Ask the AI to "generate a Facebook post about [your topic]" and watch how it automatically applies your persona to create content that sounds like you!`}
            >
              <span style={{ color: '#1877f2' }}>🎭</span>
              <span><strong>🎭 Your Writing Assistant:</strong> {corePersona.persona_name} ({corePersona.archetype})</span>
              <span style={{ marginLeft: 'auto', fontSize: '11px' }}>
                {corePersona.confidence_score}% accuracy | 
                Platform: Facebook Optimized
              </span>
              <span style={{ fontSize: '10px', color: 'rgba(255, 255, 255, 0.6)', marginLeft: '8px' }}>
                (Hover for details)
              </span>
            </div>
          )}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Button size="small" variant="outlined" disabled sx={{ color: 'rgba(255,255,255,0.7)', borderColor: 'rgba(255,255,255,0.25)' }}>
                DashBoard
              </Button>
            <Button size="small" variant="outlined" onClick={() => { clearHistory(); setHistoryVersion(v => v + 1); }}
              sx={{ color: 'rgba(255,255,255,0.9)', borderColor: 'rgba(255,255,255,0.35)' }}>
              Clear chat memory
            </Button>
            </Box>
          <Typography variant="body1" sx={{ color: 'rgba(255,255,255,0.85)', mb: 3 }}>
            {stage === 'start' ? 'Collaborate with the Copilot to craft your post. The assistant can update the draft directly.' : 'Use the edit suggestions to see real-time changes applied to your post.'}
          </Typography>

          <Paper
            sx={{
              p: 2,
              mb: 3,
              background: 'linear-gradient(180deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.08) 100%)',
              backdropFilter: 'blur(22px)',
              WebkitBackdropFilter: 'blur(22px)',
              border: '1px solid rgba(255, 255, 255, 0.16)',
              borderRadius: 3,
              boxShadow: '0 18px 50px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.25)',
            }}
          >
            <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
              Context/Notes (optional)
            </Typography>
            <TextField
              fullWidth
              multiline
              minRows={2}
              value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Audience, campaign, tone, key points..."
              sx={{
                mb: 2,
                '& .MuiInputBase-root': { color: 'white' },
                '& .MuiOutlinedInput-notchedOutline': { borderColor: 'rgba(255,255,255,0.35)' },
                '& .MuiInputBase-input::placeholder': { color: 'rgba(255,255,255,0.7)' }
              }}
            />
          </Paper>

          <Paper
            sx={{
              p: 2,
              background: 'linear-gradient(180deg, rgba(255,255,255,0.14) 0%, rgba(255,255,255,0.08) 100%)',
              backdropFilter: 'blur(22px)',
              WebkitBackdropFilter: 'blur(22px)',
              border: '1px solid rgba(255, 255, 255, 0.16)',
              borderRadius: 3,
              boxShadow: '0 18px 50px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.25)'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                Post Draft (rendered)
              </Typography>
            </Box>

            {isPreviewing && (
              <Paper
                sx={{
                  p: 2,
                  mb: 2,
                  background: 'rgba(255,255,255,0.09)',
                  border: '1px solid rgba(255,255,255,0.25)'
                }}
              >
                <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                  Live changes preview
                </Typography>
                <div
                  style={{ color: 'white', fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace' }}
                  dangerouslySetInnerHTML={{ __html: livePreviewHtml }}
                />
                <style>{`
                  .fbw-add { color: #4CAF50; font-style: normal; background: rgba(76,175,80,0.12); border-radius: 3px; }
                  .fbw-del { color: #EF9A9A; text-decoration: line-through; }
                  .fbw-more { opacity: 0.7; }
                `}</style>
                {pendingEdit && (
                  <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    <Button size="small" variant="contained" color="primary"
                      onClick={() => {
                        setPostDraft(pendingEdit.target);
                        setIsPreviewing(false);
                        setPendingEdit(null);
                        setLivePreviewHtml('');
                      }}>
                      Confirm changes
                    </Button>
                    <Button size="small" variant="outlined" color="inherit"
                      onClick={() => {
                        setIsPreviewing(false);
                        setPendingEdit(null);
                        setLivePreviewHtml('');
                      }}>
                      Discard
                    </Button>
                  </Box>
                )}
              </Paper>
            )}

            <Box
              ref={renderRef}
              onMouseUp={() => {
                try {
                  const sel = window.getSelection();
                  if (!sel || sel.rangeCount === 0) { setSelectionMenu(null); return; }
                  const text = (sel.toString() || '').trim();
                  if (!text) { setSelectionMenu(null); return; }
                  const range = sel.getRangeAt(0);
                  const rect = range.getBoundingClientRect();
                  const container = renderRef.current?.getBoundingClientRect();
                  if (!container) { setSelectionMenu(null); return; }
                  const x = Math.max(8, rect.left - container.left + (rect.width / 2));
                  const y = Math.max(8, rect.top - container.top);
                  setSelectionMenu({ x, y, text });
                } catch {
                  setSelectionMenu(null);
                }
              }}
              sx={{
              p: 2,
              border: '1px solid rgba(255,255,255,0.25)',
              borderRadius: 2,
              color: 'rgba(255,255,255,0.95)',
              position: 'relative',
              '& h1, & h2, & h3': { margin: '8px 0' },
              '& p': { margin: '6px 0' },
              '& ul': { paddingLeft: '1.2rem', margin: '6px 0' }
            }}>
              <div dangerouslySetInnerHTML={{ __html: simpleMarkdownToHtml(postDraft) }} />
              {selectionMenu && (
                <Box
                  role="menu"
                  sx={{
                    position: 'absolute',
                    top: selectionMenu.y - 36,
                    left: selectionMenu.x - 80,
                    background: 'rgba(20,22,35,0.92)',
                    border: '1px solid rgba(255,255,255,0.25)',
                    borderRadius: 2,
                    display: 'flex',
                    gap: 0.5,
                    px: 1,
                    py: 0.5,
                    boxShadow: '0 10px 24px rgba(0,0,0,0.35)'
                  }}
                >
                  <Button size="small" variant="text" sx={{ color: 'white', textTransform: 'none' }} onClick={() => console.log('Casual:', selectionMenu.text)}>Casual</Button>
                  <Button size="small" variant="text" sx={{ color: 'white', textTransform: 'none' }} onClick={() => console.log('Shorten:', selectionMenu.text)}>Shorten</Button>
                  <Button size="small" variant="text" sx={{ color: 'white', textTransform: 'none' }} onClick={() => console.log('Professional:', selectionMenu.text)}>Professional</Button>
                  <Button size="small" variant="text" sx={{ color: 'rgba(255,255,255,0.8)', textTransform: 'none' }} onClick={() => setSelectionMenu(null)}>Close</Button>
                </Box>
              )}
            </Box>
          </Paper>

          {Array.isArray(storyImages) && storyImages.length > 0 && (
            <Paper
              sx={{
                p: 2,
                mt: 3,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.16)',
                borderRadius: 3
              }}
            >
              <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                Story Images
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
                {storyImages.map((b64, idx) => (
                  <img key={idx} src={`data:image/png;base64,${b64}`} alt={`story-${idx}`} style={{ maxWidth: 220, borderRadius: 8, border: '1px solid rgba(255,255,255,0.2)' }} />
                ))}
              </Box>
            </Paper>
          )}

          {adVariations && (
            <Paper
              sx={{
                p: 2,
                mt: 3,
                background: 'linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.06) 100%)',
                border: '1px solid rgba(255, 255, 255, 0.16)',
                borderRadius: 3
              }}
            >
              <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>
                Ad Variations
              </Typography>
              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                <VariationList title="Headlines" items={adVariations.headline_variations} onInsert={(t)=>setPostDraft(prev => prev ? `${t}\n\n${prev}` : t)} onReplace={(t)=>setPostDraft(t)} />
                <VariationList title="Primary Text" items={adVariations.primary_text_variations} onInsert={(t)=>setPostDraft(prev => prev ? `${prev}\n\n${t}` : t)} onReplace={(t)=>setPostDraft(t)} />
                <VariationList title="Descriptions" items={adVariations.description_variations} onInsert={(t)=>setPostDraft(prev => prev ? `${prev}\n\n${t}` : t)} onReplace={(t)=>setPostDraft(t)} />
                <VariationList title="CTAs" items={adVariations.cta_variations} onInsert={(t)=>setPostDraft(prev => prev ? `${prev}\n\n${t}` : t)} onReplace={(t)=>setPostDraft(t)} />
              </Box>
            </Paper>
          )}
        </Container>
      </Box>
    </CopilotSidebar>
  );
};

const VariationList: React.FC<{ title: string; items: string[]; onInsert: (t: string) => void; onReplace: (t: string) => void }> = ({ title, items, onInsert, onReplace }) => {
  if (!Array.isArray(items) || items.length === 0) return null;
  return (
    <Box>
      <Typography variant="subtitle2" sx={{ color: 'rgba(255,255,255,0.85)', mb: 1 }}>{title}</Typography>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {items.slice(0, 5).map((t, idx) => (
          <Box key={idx} sx={{ border: '1px solid rgba(255,255,255,0.18)', borderRadius: 2, p: 1.2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 1 }}>{t}</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Button size="small" variant="contained" onClick={() => onInsert(t)}>Insert</Button>
              <Button size="small" variant="outlined" onClick={() => onReplace(t)}>Replace</Button>
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default FacebookWriter;


