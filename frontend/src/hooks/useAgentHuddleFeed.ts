import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { apiClient, getApiUrl, getAuthTokenGetter } from '../api/client';

export interface AgentRunItem { id: number; agent_type?: string; status?: string; success?: boolean | null; result_summary?: string | null; error_message?: string | null; finished_at?: string | null; started_at?: string | null; }
export interface AgentEventItem { id: number; run_id?: number; agent_type?: string; event_type?: string; message?: string | null; created_at?: string | null; payload?: any; }
export interface AgentAlertItem { id: number; title?: string; message?: string; severity?: string; read_at?: string | null; payload?: any; }
export interface AgentApprovalItem { id: number; action_type?: string; status?: string; risk_level?: number; created_at?: string | null; }

interface Cursor { run_id: number; event_id: number; alert_id: number; approval_id: number; }
interface FeedPayload {
  runs: AgentRunItem[];
  events: AgentEventItem[];
  alerts: AgentAlertItem[];
  approvals: AgentApprovalItem[];
  cursor: Cursor;
}

const DEFAULT_CURSOR: Cursor = { run_id: 0, event_id: 0, alert_id: 0, approval_id: 0 };
const BASE_BACKOFF_MS = 1500;
const MAX_BACKOFF_MS = 20000;

const mergeById = <T extends { id: number }>(prev: T[], incoming: T[], limit = 100): T[] => {
  if (!incoming.length) return prev;
  const byId = new Map<number, T>();
  [...prev, ...incoming].forEach((item) => byId.set(item.id, item));
  return Array.from(byId.values()).sort((a, b) => b.id - a.id).slice(0, limit);
};

const parseSseLines = (raw: string): Array<{ event: string; data: string }> => {
  return raw
    .split('\n\n')
    .map((block) => block.trim())
    .filter(Boolean)
    .map((block) => {
      const lines = block.split('\n');
      const event = (lines.find((line) => line.startsWith('event:')) || 'event: message').replace('event:', '').trim();
      const data = lines
        .filter((line) => line.startsWith('data:'))
        .map((line) => line.replace('data:', '').trim())
        .join('');
      return { event, data };
    });
};

export const useAgentHuddleFeed = (options?: { detailTier?: 'summary' | 'detailed' | 'debug' }) => {
  const [feed, setFeed] = useState<FeedPayload>({ runs: [], events: [], alerts: [], approvals: [], cursor: DEFAULT_CURSOR });
  const [connectionMode, setConnectionMode] = useState<'connecting' | 'sse' | 'polling'>('connecting');
  const [lastHeartbeatAt, setLastHeartbeatAt] = useState<number | null>(null);
  const stopRef = useRef(false);
  const reconnectAttemptRef = useRef(0);
  const cursorRef = useRef<Cursor>(DEFAULT_CURSOR);
  const detailTier = options?.detailTier || 'summary';

  const applyPayload = useCallback((payload: Partial<FeedPayload>, replace = false) => {
    setFeed((prev) => ({
      runs: replace ? (payload.runs || []) : mergeById(prev.runs, payload.runs || []),
      events: replace ? (payload.events || []) : mergeById(prev.events, payload.events || []),
      alerts: replace ? (payload.alerts || []) : mergeById(prev.alerts, payload.alerts || []),
      approvals: replace ? (payload.approvals || []) : mergeById(prev.approvals, payload.approvals || []),
      cursor: {
        run_id: payload.cursor?.run_id ?? prev.cursor.run_id,
        event_id: payload.cursor?.event_id ?? prev.cursor.event_id,
        alert_id: payload.cursor?.alert_id ?? prev.cursor.alert_id,
        approval_id: payload.cursor?.approval_id ?? prev.cursor.approval_id,
      },
    }));
    if (payload.cursor) {
      cursorRef.current = {
        run_id: payload.cursor.run_id ?? cursorRef.current.run_id,
        event_id: payload.cursor.event_id ?? cursorRef.current.event_id,
        alert_id: payload.cursor.alert_id ?? cursorRef.current.alert_id,
        approval_id: payload.cursor.approval_id ?? cursorRef.current.approval_id,
      };
    }
  }, []);

  const loadSnapshot = useCallback(async (cursor?: Cursor) => {
    const params = { ...(cursor || {}), detail_tier: detailTier };
    const resp = await apiClient.get('/api/agents/huddle/feed', { params });
    const data = resp?.data?.data as FeedPayload;
    applyPayload(data, !cursor);
    return data;
  }, [applyPayload, detailTier]);

  useEffect(() => {
    stopRef.current = false;
    let pollingTimer: ReturnType<typeof setInterval> | null = null;

    const startPolling = () => {
      setConnectionMode('polling');
      if (pollingTimer) clearInterval(pollingTimer);
      pollingTimer = setInterval(async () => {
        try {
          await loadSnapshot(cursorRef.current);
        } catch {
          // no-op
        }
      }, 7000);
    };

    const connect = async () => {
      try {
        setConnectionMode('connecting');
        await loadSnapshot();
        const tokenGetter = getAuthTokenGetter();
        const token = tokenGetter ? await tokenGetter() : null;
        if (!token) throw new Error('No auth token available for SSE stream');

        const streamUrl = `${getApiUrl()}/api/agents/huddle/stream?detail_tier=${detailTier}`;
        const response = await fetch(streamUrl, {
          headers: { Authorization: `Bearer ${token}`, Accept: 'text/event-stream' },
        });

        if (!response.ok || !response.body) {
          throw new Error(`SSE stream unavailable (${response.status})`);
        }

        reconnectAttemptRef.current = 0;
        setConnectionMode('sse');

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (!stopRef.current) {
          const { done, value } = await reader.read();
          if (done) {
            throw new Error('SSE stream ended');
          }
          buffer += decoder.decode(value, { stream: true });
          const chunks = buffer.split('\n\n');
          buffer = chunks.pop() || '';

          for (const packet of parseSseLines(chunks.join('\n\n'))) {
            if (!packet.data) continue;
            if (packet.event === 'heartbeat') {
              setLastHeartbeatAt(Date.now());
              continue;
            }
            const payload = JSON.parse(packet.data);
            if (packet.event === 'snapshot') {
              applyPayload(payload, true);
            }
            if (packet.event === 'delta') {
              applyPayload(payload, false);
            }
          }
        }
      } catch {
        reconnectAttemptRef.current += 1;
        if (reconnectAttemptRef.current >= 3) {
          startPolling();
          return;
        }
        const sleepMs = Math.min(MAX_BACKOFF_MS, BASE_BACKOFF_MS * (2 ** reconnectAttemptRef.current));
        await new Promise((resolve) => setTimeout(resolve, sleepMs));
        if (!stopRef.current) connect();
      }
    };

    connect();

    return () => {
      stopRef.current = true;
      if (pollingTimer) clearInterval(pollingTimer);
    };
  }, [applyPayload, loadSnapshot]);

  return useMemo(() => ({ ...feed, connectionMode, lastHeartbeatAt }), [feed, connectionMode, lastHeartbeatAt]);
};
