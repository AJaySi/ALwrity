import React, { useEffect, useMemo, useRef } from 'react';

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
    color: '#6b7280',
    background: '#f3f4f6',
    border: '#e5e7eb'
  },
  active: {
    label: 'In Progress',
    color: '#2563eb',
    background: '#eff6ff',
    border: '#bfdbfe'
  },
  done: {
    label: 'Completed',
    color: '#047857',
    background: '#ecfdf5',
    border: '#bbf7d0'
  },
  error: {
    label: 'Needs Attention',
    color: '#b91c1c',
    background: '#fee2e2',
    border: '#fecaca'
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

  if (!open) {
    return null;
  }

  return (
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
          maxWidth: 940,
          maxHeight: '82vh',
          background: '#ffffff',
          borderRadius: 18,
          boxShadow: '0 28px 80px rgba(15, 23, 42, 0.25)',
          border: '1px solid #e2e8f0',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}
      >
        <div
          style={{
            padding: '28px 32px 24px 32px',
            background: '#f8fafc',
            borderBottom: '1px solid #e2e8f0',
            position: 'relative'
          }}
        >
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundImage: 'url(/blog-writer-bg.png)',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'left center',
              backgroundSize: '35% auto',
              opacity: 0.12,
              pointerEvents: 'none'
            }}
          />
          <div
            style={{
              position: 'relative',
              zIndex: 1,
              display: 'flex',
              alignItems: 'flex-start',
              justifyContent: 'space-between',
              gap: 16
            }}
          >
            <div>
              <h3 id="research-progress-title" style={{ margin: 0, fontSize: 22, color: '#0f172a' }}>
                {title}
              </h3>
              <p style={{ margin: '8px 0 0 0', color: '#475569', fontSize: 14 }}>
                Research takes 40–60 seconds. We search multiple engines (Exa, Tavily), extract key insights, 
                and assemble a structured research brief. After this, you will move to the <strong>Outline phase</strong> 
                where AI generates a blog structure, then <strong>Content</strong> writes each section, followed by 
                <strong> SEO</strong> optimization and <strong>Publish</strong>.
              </p>
              <div
                style={{
                  marginTop: 14,
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 12,
                  padding: '8px 14px',
                  borderRadius: 999,
                  background: statusInfo.background,
                  color: statusInfo.color,
                  fontSize: 13,
                  fontWeight: 600,
                  border: `1px solid ${statusInfo.color}1A`
                }}
              >
                <span>{statusInfo.label}</span>
                <span style={{ fontSize: 12, color: '#475569', fontWeight: 500 }}>{statusInfo.description}</span>
              </div>
            </div>
            <button
              onClick={onClose}
              style={{
                background: '#ffffff',
                border: '1px solid #cbd5f5',
                borderRadius: 12,
                padding: '10px 14px',
                cursor: 'pointer',
                fontSize: 13,
                fontWeight: 600,
                color: '#1f2937',
                boxShadow: '0 1px 2px rgba(15, 23, 42, 0.08)',
                transition: 'all 0.2s ease'
              }}
            >
              Close
            </button>
          </div>
        </div>

        <div style={{ padding: '24px 32px', overflow: 'auto' }}>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 12,
              marginBottom: 20
            }}
          >
            {stagesWithState.map(stage => {
              const copy = stageStateCopy[stage.state];
              return (
                <div
                  key={stage.id}
                  style={{
                    flex: '1 1 180px',
                    minWidth: 180,
                    borderRadius: 14,
                    padding: '14px 16px',
                    background: copy.background,
                    border: `1px solid ${copy.border}`,
                    boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.6)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontWeight: 600, color: '#0f172a' }}>
                    <span style={{ fontSize: 22 }}>{stage.icon}</span>
                    <span>{stage.label}</span>
                  </div>
                  <div style={{ marginTop: 6, fontSize: 12.5, color: '#475569' }}>{stage.description}</div>
                  <div style={{ marginTop: 12, fontSize: 12, fontWeight: 600, color: copy.color }}>{copy.label}</div>
                </div>
              );
            })}
          </div>

          {latestMessage && (
            <div
              style={{
                borderRadius: 16,
                padding: '18px 20px',
                border: `1px solid ${toneStyles[latestMessage.tone].border}`,
                background: toneStyles[latestMessage.tone].bg,
                marginBottom: 20,
                boxShadow: '0 4px 16px rgba(15, 23, 42, 0.08)'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14 }}>
                <div style={{ fontSize: 28 }}>{latestMessage.icon}</div>
                <div style={{ flex: 1 }}>
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'baseline',
                      gap: 16
                    }}
                  >
                    <div style={{ fontSize: 17, fontWeight: 600, color: '#0f172a' }}>{latestMessage.title}</div>
                    <div style={{ fontSize: 12, color: '#64748b' }}>{latestMessage.timeLabel}</div>
                  </div>
                  {latestMessage.subtitle && (
                    <div style={{ marginTop: 6, fontSize: 13.5, color: '#334155' }}>{latestMessage.subtitle}</div>
                  )}
                  {latestMessage.raw && (
                    <div style={{ marginTop: 10, fontSize: 12.5, color: '#64748b' }}>{latestMessage.raw}</div>
                  )}
                </div>
              </div>
            </div>
          )}

          <div
            style={{
              border: '1px solid #e2e8f0',
              borderRadius: 16,
              padding: '18px 0',
              maxHeight: '32vh',
              overflow: 'hidden',
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <div
              ref={scrollRef}
              style={{
                overflowY: 'auto',
                padding: '0 20px',
                display: 'flex',
                flexDirection: 'column',
                gap: 12
              }}
            >
              {processedMessages.length === 0 && (
                <div style={{ padding: '10px 0', color: '#6b7280', fontSize: 14 }}>
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
                      gap: 14,
                      padding: '12px 14px',
                      borderRadius: 12,
                      background: styles.bg,
                      border: `1px solid ${styles.border}`
                    }}
                  >
                    <div style={{ fontSize: 22 }}>{meta.icon}</div>
                    <div style={{ flex: 1 }}>
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'baseline',
                          gap: 12
                        }}
                      >
                        <div style={{ fontWeight: 600, color: styles.text, fontSize: 14 }}>{meta.title}</div>
                        <div style={{ fontSize: 12, color: '#64748b' }}>{meta.timeLabel}</div>
                      </div>
                      {meta.subtitle && (
                        <div style={{ marginTop: 4, fontSize: 13, color: '#475569' }}>{meta.subtitle}</div>
                      )}
                      {meta.raw && (
                        <div style={{ marginTop: 6, fontSize: 12.5, color: '#6b7280' }}>{meta.raw}</div>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: 18,
                padding: '12px 16px',
                borderRadius: 12,
                border: '1px solid #fecaca',
                background: '#fef2f2',
                color: '#b91c1c',
                fontSize: 13.5
              }}
            >
              Error: {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResearchProgressModal;

