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
    id: 'discovery',
    label: 'Source Discovery',
    description: 'Exploring trusted sources across the web.',
    icon: '🔎',
    keywords: ['search', 'source', 'gather', 'google', 'discover']
  },
  {
    id: 'analysis',
    label: 'Insight Extraction',
    description: 'Extracting data points, statistics, and quotes.',
    icon: '🧠',
    keywords: ['analysis', 'analyz', 'extract', 'insight', 'processing']
  },
  {
    id: 'assembly',
    label: 'Structuring Findings',
    description: 'Packaging insights and preparing summaries.',
    icon: '📝',
    keywords: ['assembling', 'structuring', 'summary', 'completed', 'ready', 'post-processing']
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
  {
    keywords: ['checking cache', 'cache'],
    title: 'Checking existing research cache',
    subtitle: 'Looking for previously generated insights so we can respond instantly.',
    icon: '🗂️',
    tone: 'info',
    stage: 'cache'
  },
  {
    keywords: ['found cached research', 'loading cached'],
    title: 'Loaded cached research results',
    subtitle: 'Serving saved insights to keep things fast.',
    icon: '⚡',
    tone: 'success',
    stage: 'cache'
  },
  {
    keywords: ['starting research'],
    title: 'Launching fresh research',
    subtitle: 'Bootstrapping the workflow and validating your request.',
    icon: '🚀',
    tone: 'active',
    stage: 'discovery'
  },
  {
    keywords: ['search', 'query', 'sources', 'web'],
    title: 'Collecting authoritative sources',
    subtitle: 'Evaluating top-ranked pages, studies, and reports.',
    icon: '🔎',
    tone: 'active',
    stage: 'discovery'
  },
  {
    keywords: ['extracting', 'analyzing', 'analysis', 'insight'],
    title: 'Extracting key insights',
    subtitle: 'Summarising statistics, trends, and quotes that matter.',
    icon: '🧠',
    tone: 'active',
    stage: 'analysis'
  },
  {
    keywords: ['assembling', 'compiling', 'structuring', 'post-processing'],
    title: 'Structuring the research package',
    subtitle: 'Organising findings into ready-to-use sections.',
    icon: '🧩',
    tone: 'info',
    stage: 'assembly'
  },
  {
    keywords: ['completed successfully', 'research completed', 'ready'],
    title: 'Research completed successfully',
    subtitle: 'All insights are ready for the outline phase.',
    icon: '✅',
    tone: 'success',
    stage: 'assembly'
  },
  {
    keywords: ['failed', 'error', 'limit exceeded'],
    title: 'Research encountered an issue',
    subtitle: 'Review the error message below and try again.',
    icon: '⚠️',
    tone: 'error'
  }
];

const sanitizeTitle = (text: string) => text.replace(/^[^a-zA-Z0-9]+/, '').trim();

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

  return {
    timestamp: message.timestamp,
    timeLabel: formatTime(message.timestamp),
    raw,
    title: sanitizeTitle(raw) || 'Update received',
    icon: '📝',
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
                We are gathering sources, extracting insights, and assembling a research brief tailored to your topic.
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

