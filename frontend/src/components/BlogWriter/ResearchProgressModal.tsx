import React, { useEffect, useMemo, useRef } from 'react';
import CircularProgress from '@mui/material/CircularProgress';

interface ResearchProgressModalProps {
  open: boolean;
  title?: string;
  status?: string;
  messages: Array<{ timestamp: string; message: string }>;
  error?: string | null;
  onClose: () => void;
}

type Tone = 'info' | 'active' | 'success' | 'warning' | 'error';
type StageState = 'upcoming' | 'active' | 'done' | 'error';

const statusThemes: Record<
  string,
  { label: string; description: string; color: string; background: string }
> = {
  pending: {
    label: 'Queued',
    description: 'Preparing the research workflow…',
    color: '#1f2937',
    background: '#e5e7eb'
  },
  running: {
    label: 'In Progress',
    description: 'Gathering sources and extracting insights.',
    color: '#1d4ed8',
    background: '#dbeafe'
  },
  completed: {
    label: 'Completed',
    description: 'Research results are ready to review.',
    color: '#047857',
    background: '#d1fae5'
  },
  success: {
    label: 'Completed',
    description: 'Research results are ready to review.',
    color: '#047857',
    background: '#d1fae5'
  },
  succeeded: {
    label: 'Completed',
    description: 'Research results are ready to review.',
    color: '#047857',
    background: '#d1fae5'
  },
  finished: {
    label: 'Completed',
    description: 'Research results are ready to review.',
    color: '#047857',
    background: '#d1fae5'
  },
  failed: {
    label: 'Needs Attention',
    description: 'We hit an issue while running research.',
    color: '#b91c1c',
    background: '#fee2e2'
  }
};

const toneStyles: Record<Tone, { bg: string; border: string; text: string }> = {
  info: { bg: '#f8fafc', border: '#e2e8f0', text: '#0f172a' },
  active: { bg: '#eff6ff', border: '#bfdbfe', text: '#1d4ed8' },
  success: { bg: '#ecfdf5', border: '#bbf7d0', text: '#047857' },
  warning: { bg: '#fff7ed', border: '#fed7aa', text: '#c2410c' },
  error: { bg: '#fef2f2', border: '#fecaca', text: '#b91c1c' }
};

const stageDefinitions = [
  {
    id: 'cache',
    label: 'Cache Check',
    description: 'Looking for saved research results to speed things up.',
    icon: '🗂️',
    keywords: ['cache', 'cached', 'stored']
  },
  {
    id: 'validation',
    label: 'Request Validation',
    description: 'Verifying your topic and preparing the research pipeline.',
    icon: '✅',
    keywords: ['starting', 'launching', 'bootstrap', 'validat']
  },
  {
    id: 'exa',
    label: 'Deep Web Search (Exa)',
    description: 'Searching academic databases, research papers, and structured content.',
    icon: '🌐',
    keywords: ['exa', 'neural search']
  },
  {
    id: 'tavily',
    label: 'AI Web Search (Tavily)',
    description: 'Scanning news, blogs, and real-time web content.',
    icon: '🔍',
    keywords: ['tavily', 'ai search']
  },
  {
    id: 'analysis',
    label: 'Content Analysis',
    description: 'Extracting key data points, statistics, and actionable insights.',
    icon: '🧠',
    keywords: ['analyz', 'analyz', 'extract', 'insight', 'keywords', 'angles', 'filter']
  },
  {
    id: 'assembly',
    label: 'Structuring Results',
    description: 'Packaging findings into a ready-to-use research brief.',
    icon: '📦',
    keywords: ['caching', 'assembling', 'structuring', 'post-processing', 'completed', 'ready']
  }
] as const;

type StageId = (typeof stageDefinitions)[number]['id'];

interface MessageMeta {
  timestamp: string;
  timeLabel: string;
  raw: string;
  title: string;
  subtitle?: string;
  icon: string;
  tone: Tone;
  stage: StageId | null;
}

const completionStatuses = new Set(['completed', 'success', 'succeeded', 'finished']);

const formatTime = (timestamp: string) => {
  try {
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit'
    }).format(new Date(timestamp));
  } catch {
    return timestamp;
  }
};

const inferStage = (text: string): StageId | null => {
  const lower = text.toLowerCase();
  for (const stage of stageDefinitions) {
    if (stage.keywords.some(keyword => lower.includes(keyword))) {
      return stage.id;
    }
  }
  return null;
};

const friendlyMappings: Array<{
  keywords: string[];
  title: string;
  subtitle?: string;
  icon: string;
  tone: Tone;
  stage?: StageId;
}> = [
  // ── Cache stage ─────────────────────────────────────────────────
  {
    keywords: ['checking cache', 'looking for saved'],
    title: 'Checking for saved research results',
    subtitle: 'If you have run this topic before, we skip straight to the cached results — saving 30–50 seconds.',
    icon: '🗂️',
    tone: 'info',
    stage: 'cache'
  },
  {
    keywords: ['found cached research', 'found cached', 'loading cached', 'returning instantly'],
    title: 'Using cached research — no fresh search needed',
    subtitle: 'Previous results loaded instantly. You can review them and proceed directly to the Outline phase.',
    icon: '⚡',
    tone: 'success',
    stage: 'cache'
  },
  {
    keywords: ['cache miss', 'no cached'],
    title: 'No cached results found — starting fresh research',
    subtitle: 'This will take 40–60 seconds as we search multiple sources, extract insights, and build your research brief.',
    icon: '🔍',
    tone: 'active',
    stage: 'cache'
  },

  // ── Validation / Start stage ──────────────────────────────────
  {
    keywords: ['starting research', 'starting research operation', 'launching fresh'],
    title: 'Launching research pipeline',
    subtitle: 'We validate your topic, then fan out across multiple search engines (Exa, Tavily) to gather diverse perspectives. This runs in parallel so you get results faster.',
    icon: '🚀',
    tone: 'active',
    stage: 'validation'
  },
  {
    keywords: ['user id is required', 'validation error'],
    title: 'Validation check in progress',
    subtitle: 'Ensuring your account and request parameters are properly configured before the search begins.',
    icon: '🔐',
    tone: 'info',
    stage: 'validation'
  },

  // ── Exa neural search stage ──────────────────────────────────
  {
    keywords: ['connecting to exa', 'exa neural search'],
    title: 'Connecting to deep-web search engine (Exa)',
    subtitle: 'Exa searches academic databases, technical documentation, and structured content repositories. This is the most thorough search layer and typically takes 10–15 seconds.',
    icon: '🌐',
    tone: 'active',
    stage: 'exa'
  },
  {
    keywords: ['executing exa neural search', 'exa research'],
    title: 'Running deep-web search via Exa AI',
    subtitle: 'Exa scans millions of indexed pages for authoritative, high-signal content. Results feed into your research brief with source citations and relevance scores.',
    icon: '🤖',
    tone: 'active',
    stage: 'exa'
  },
  {
    keywords: ['exa research failed', 'exa research did not return'],
    title: 'Exa search completed with limited results',
    subtitle: 'This is normal for niche topics. We fall back to Tavily for broader web coverage. Your research will still be comprehensive.',
    icon: '⚠️',
    tone: 'warning',
    stage: 'exa'
  },

  // ── Tavily AI search stage ────────────────────────────────────
  {
    keywords: ['connecting to tavily', 'tavily ai search'],
    title: 'Connecting to real-time web search (Tavily)',
    subtitle: 'Tavily searches news articles, blog posts, and current web content. It provides up-to-date information from a broader range of sources than traditional search.',
    icon: '🔍',
    tone: 'active',
    stage: 'tavily'
  },
  {
    keywords: ['executing tavily ai search', 'tavily research'],
    title: 'Running real-time web search via Tavily AI',
    subtitle: 'Tavily fetches and ranks results based on relevance, authority, and recency. Combined with Exa results, this gives you both depth and breadth of coverage.',
    icon: '🤖',
    tone: 'active',
    stage: 'tavily'
  },
  {
    keywords: ['tavily research failed', 'tavily api call limit'],
    title: 'Tavily search hit a rate limit',
    subtitle: 'We already have results from Exa. Continuing with what we have — your research will still contain valuable data.',
    icon: '⚠️',
    tone: 'warning',
    stage: 'tavily'
  },
  {
    keywords: ['tavily research did not return'],
    title: 'Tavily returned minimal results for this topic',
    subtitle: 'Combining available Exa and Tavily data to build a complete picture. Niche or emerging topics sometimes have sparse web coverage.',
    icon: 'ℹ️',
    tone: 'info',
    stage: 'tavily'
  },

  // ── Analysis / Processing stage ───────────────────────────────
  {
    keywords: ['analyz', 'analyz', 'keywords and content angles'],
    title: 'Analyzing keywords and content angles',
    subtitle: 'We cross-reference your search results to identify the strongest angles, key statistics, trending subtopics, and gaps in existing coverage. This shapes the strategic direction of your blog.',
    icon: '🧠',
    tone: 'active',
    stage: 'analysis'
  },
  {
    keywords: ['filtering', 'cleaning research data'],
    title: 'Filtering and ranking research data',
    subtitle: 'Removing duplicates, low-authority sources, and irrelevant content. Every source gets a quality score so the Outline phase can prioritize the best material.',
    icon: '🔬',
    tone: 'active',
    stage: 'analysis'
  },
  {
    keywords: ['extracting', 'insight'],
    title: 'Extracting key insights and statistics',
    subtitle: 'Pulling out data points, quotes, statistics, and authoritative references. Your outline will use these to build credible, well-supported content.',
    icon: '📊',
    tone: 'active',
    stage: 'analysis'
  },

  // ── Assembly / Caching stage ─────────────────────────────────
  {
    keywords: ['caching results', 'caching for future'],
    title: 'Saving results to cache for next time',
    subtitle: 'Your research is being cached so revisiting or regenerating this topic will be instant next time.',
    icon: '💾',
    tone: 'info',
    stage: 'assembly'
  },
  {
    keywords: ['post-processing', 'assembling', 'structuring'],
    title: 'Assembling the final research brief',
    subtitle: 'Organizing all findings into a structured brief with source mappings, competitor analysis, and suggested angles — ready for the Outline phase.',
    icon: '🧩',
    tone: 'info',
    stage: 'assembly'
  },

  // ── Completion ────────────────────────────────────────────────
  {
    keywords: ['completed successfully', 'research completed', 'found', 'sources'],
    title: 'Research complete! Ready for Outline phase.',
    subtitle: 'Your research brief is ready. Next up: the Outline phase turns this research into a structured blog outline. Click the Outline chip or navigate to it to continue.',
    icon: '✅',
    tone: 'success',
    stage: 'assembly'
  },
  {
    keywords: ['subscription limit exceeded', '429'],
    title: 'Search provider rate limit hit',
    subtitle: 'One of our search providers is temporarily rate-limited. The system will retry automatically. If it persists, try again in a few minutes.',
    icon: '⏳',
    tone: 'warning'
  },

  // ── Errors ────────────────────────────────────────────────────
  {
    keywords: ['failed with error', 'research failed'],
    title: 'Research encountered an error',
    subtitle: 'Something went wrong during the research process. Review the error details below and try again. Common causes: network issues, API timeouts, or invalid keywords.',
    icon: '❌',
    tone: 'error'
  },
  {
    keywords: ['failed', 'error', 'unknown status'],
    title: 'Research operation reported an issue',
    subtitle: 'The research pipeline encountered a problem. Please check the error details below and consider refining your keywords before trying again.',
    icon: '⚠️',
    tone: 'error'
  }
];

const sanitizeTitle = (text: string) => {
  // Strip leading emoji/whitespace, capitalize first letter
  const cleaned = text.replace(/^[^\w\s]+/, '').trim();
  if (!cleaned) return '';
  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
};

// Fallback icons based on message content
const inferFallbackIcon = (text: string): string => {
  const lower = text.toLowerCase();
  if (/error|fail|timeout|limit/i.test(lower)) return '⚠️';
  if (/done|complete|success|finish|ready/i.test(lower)) return '✅';
  if (/fetch|load|retriev|download/i.test(lower)) return '📥';
  if (/writ|generat|creat|build/i.test(lower)) return '✍️';
  if (/check|validat|verif/i.test(lower)) return '🔍';
  return '📝';
};

const mapMessageToMeta = (message: { timestamp: string; message: string }): MessageMeta => {
  const raw = message.message || '';
  const lower = raw.toLowerCase();

  const mapping = friendlyMappings.find(entry =>
    entry.keywords.some(keyword => lower.includes(keyword))
  );

  if (mapping) {
    return {
      timestamp: message.timestamp,
      timeLabel: formatTime(message.timestamp),
      raw,
      title: mapping.title,
      subtitle: mapping.subtitle,
      icon: mapping.icon,
      tone: mapping.tone,
      stage: mapping.stage ?? inferStage(raw)
    };
  }

  const stage = inferStage(raw);
  const fallbackTitle = sanitizeTitle(raw);

  return {
    timestamp: message.timestamp,
    timeLabel: formatTime(message.timestamp),
    raw,
    title: fallbackTitle || 'Processing research data…',
    subtitle: 'Your research is being assembled. This may take a moment as we process multiple data sources in parallel.',
    icon: inferFallbackIcon(raw),
    tone: 'info',
    stage
  };
};

const stageStateCopy: Record<StageState, { label: string; color: string; background: string; border: string }> = {
  upcoming: {
    label: 'Pending',
    color: '#9ca3af',
    background: '#f9fafb',
    border: '#e5e7eb'
  },
  active: {
    label: 'In Progress',
    color: '#1d4ed8',
    background: '#dbeafe',
    border: '#93c5fd'
  },
  done: {
    label: 'Completed',
    color: '#047857',
    background: '#d1fae5',
    border: '#86efac'
  },
  error: {
    label: 'Needs Attention',
    color: '#b91c1c',
    background: '#fee2e2',
    border: '#fca5a5'
  }
};

const ResearchProgressModal: React.FC<ResearchProgressModalProps> = ({
  open,
  title = 'Research in progress',
  status,
  messages,
  error,
  onClose
}) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);
  const normalizedStatus = (status || '').toLowerCase();
  const statusKey = error ? 'failed' : normalizedStatus;
  const statusInfo = statusThemes[statusKey] || statusThemes.pending;

  const processedMessages = useMemo(() => {
    if (!messages || messages.length === 0) {
      return [] as MessageMeta[];
    }
    return messages.map(mapMessageToMeta);
  }, [messages]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [processedMessages.length]);

  const latestMessage = processedMessages.length > 0 ? processedMessages[processedMessages.length - 1] : null;

  const stagesWithState = useMemo(() => {
    const states: StageState[] = stageDefinitions.map(() => 'upcoming');
    let highestCompletedIndex = -1;

    processedMessages.forEach(meta => {
      if (!meta.stage) {
        return;
      }
      const idx = stageDefinitions.findIndex(stage => stage.id === meta.stage);
      if (idx === -1) {
        return;
      }

      if (meta.tone === 'error' || /error|failed/i.test(meta.raw)) {
        states[idx] = 'error';
      } else {
        states[idx] = 'done';
        if (idx > highestCompletedIndex) {
          highestCompletedIndex = idx;
        }
      }
    });

    if (!error) {
      const firstPending = states.findIndex(state => state === 'upcoming');
      if (firstPending !== -1 && !completionStatuses.has(normalizedStatus)) {
        states[firstPending] = 'active';
      } else if (completionStatuses.has(normalizedStatus)) {
        for (let i = 0; i < states.length; i += 1) {
          if (states[i] !== 'error') {
            states[i] = 'done';
          }
        }
      }
    } else if (highestCompletedIndex >= 0) {
      states[highestCompletedIndex] = 'error';
    }

    return stageDefinitions.map((stage, index) => ({
      ...stage,
      state: states[index]
    }));
  }, [error, normalizedStatus, processedMessages]);

  const isRunning = !error && !completionStatuses.has(normalizedStatus);

  if (!open) {
    return null;
  }

  return (
    <>
      <style>{`
        @keyframes researchPulse {
          0%, 100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.15); }
          50% { box-shadow: 0 0 0 8px rgba(37, 99, 235, 0); }
        }
        @keyframes researchShimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="research-progress-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.55)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 2000,
        padding: '24px'
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: 700,
          maxHeight: '85vh',
          background: '#ffffff',
          borderRadius: 16,
          boxShadow: '0 20px 60px rgba(15, 23, 42, 0.2)',
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        {/* Compact header */}
        <div
          style={{
            padding: '16px 20px',
            background: '#f8fafc',
            borderBottom: '1px solid #e2e8f0',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flex: 1, minWidth: 0 }}>
            {isRunning && <CircularProgress size={18} thickness={4} sx={{ color: '#2563eb', flexShrink: 0 }} />}
            <div style={{ minWidth: 0 }}>
              <h3 id="research-progress-title" style={{ margin: 0, fontSize: 16, color: '#0f172a' }}>
                {title}
              </h3>
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 6,
                  marginTop: 4,
                  padding: '2px 8px',
                  borderRadius: 999,
                  background: statusInfo.background,
                  color: statusInfo.color,
                  fontSize: 12,
                  fontWeight: 600,
                }}
              >
                {statusInfo.label}
                {statusInfo.description && <span style={{ fontWeight: 400, fontSize: 11, color: '#64748b' }}>— {statusInfo.description}</span>}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{
              background: '#fff',
              border: '1px solid #e2e8f0',
              borderRadius: 8,
              padding: '6px 12px',
              cursor: 'pointer',
              fontSize: 13,
              fontWeight: 500,
              color: '#475569',
              flexShrink: 0
            }}
          >
            Close
          </button>
        </div>

        <div style={{ padding: '12px 20px', overflow: 'auto', flex: 1 }}>
          {/* Progress bar */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <div style={{ flex: 1, height: 4, borderRadius: 2, background: '#e5e7eb', overflow: 'hidden' }}>
              <div
                style={{
                  width: `${Math.round((stagesWithState.filter(s => s.state === 'done').length / stagesWithState.length) * 100)}%`,
                  height: '100%',
                  borderRadius: 2,
                  background: 'linear-gradient(90deg, #3b82f6, #2563eb)',
                  transition: 'width 0.5s ease'
                }}
              />
            </div>
            <span style={{ fontSize: 11, fontWeight: 600, color: '#64748b' }}>
              {stagesWithState.filter(s => s.state === 'done').length}/{stagesWithState.length}
            </span>
          </div>

          {/* Compact stage indicators */}
          <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
            {stagesWithState.map(stage => {
              const copy = stageStateCopy[stage.state];
              return (
                <div
                  key={stage.id}
                  style={{
                    flex: 1,
                    padding: '6px 4px',
                    borderRadius: 8,
                    background: copy.background,
                    border: `1px solid ${copy.border}`,
                    textAlign: 'center',
                    animation: stage.state === 'active' ? 'researchPulse 2s ease-in-out infinite' : undefined,
                    transition: 'all 0.3s ease'
                  }}
                >
                  <div style={{ fontSize: 16, lineHeight: 1 }}>{stage.icon}</div>
                  <div style={{ fontSize: 10, fontWeight: 600, color: copy.color, marginTop: 2, lineHeight: 1.2 }}>
                    {stage.state === 'active' ? 'Working…' : stage.state === 'done' ? 'Done' : stage.state === 'error' ? 'Error' : stage.label.split('(')[0].trim()}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Latest message card — compact */}
          {latestMessage && (
            <div
              style={{
                borderRadius: 10,
                padding: '10px 14px',
                border: `1px solid ${toneStyles[latestMessage.tone].border}`,
                background: toneStyles[latestMessage.tone].bg,
                marginBottom: 10,
                display: 'flex',
                alignItems: 'center',
                gap: 10
              }}
            >
              <div style={{ fontSize: 20, flexShrink: 0 }}>{latestMessage.icon}</div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 8 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', display: 'flex', alignItems: 'center', gap: 6 }}>
                    {latestMessage.tone === 'active' && isRunning && (
                      <CircularProgress size={12} thickness={5} sx={{ color: '#1d4ed8', flexShrink: 0 }} />
                    )}
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{latestMessage.title}</span>
                  </div>
                  <div style={{ fontSize: 11, color: '#94a3b8', flexShrink: 0 }}>{latestMessage.timeLabel}</div>
                </div>
                {latestMessage.subtitle && (
                  <div style={{ marginTop: 2, fontSize: 12, color: '#64748b', lineHeight: 1.3 }}>{latestMessage.subtitle}</div>
                )}
              </div>
            </div>
          )}

          {/* Scrollable message log — compact rows */}
          <div
            style={{
              border: '1px solid #e5e7eb',
              borderRadius: 10,
              maxHeight: '28vh',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div
              ref={scrollRef}
              style={{
                overflowY: 'auto',
                padding: '6px 10px',
                display: 'flex',
                flexDirection: 'column',
                gap: 4
              }}
            >
              {processedMessages.length === 0 && (
                <div style={{ padding: '8px 0', color: '#9ca3af', fontSize: 13, display: 'flex', alignItems: 'center', gap: 6 }}>
                  {isRunning && <CircularProgress size={10} thickness={5} sx={{ color: '#9ca3af' }} />}
                  Awaiting progress updates…
                </div>
              )}
              {processedMessages.map((meta, index) => {
                const styles = toneStyles[meta.tone];
                return (
                  <div
                    key={`${meta.timestamp}-${index}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      padding: '4px 8px',
                      borderRadius: 6,
                      background: styles.bg,
                      border: `1px solid ${styles.border}`,
                      fontSize: 12
                    }}
                  >
                    <span style={{ fontSize: 14, flexShrink: 0 }}>{meta.icon}</span>
                    <span style={{ fontWeight: 600, color: styles.text, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{meta.title}</span>
                    <span style={{ color: '#94a3b8', fontSize: 10, flexShrink: 0 }}>{meta.timeLabel}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: 10,
                padding: '8px 12px',
                borderRadius: 8,
                border: '1px solid #fecaca',
                background: '#fef2f2',
                color: '#b91c1c',
                fontSize: 13
              }}
            >
              Error: {error}
            </div>
          )}
        </div>
      </div>
    </div>
    </>
  );
};

export default ResearchProgressModal;

