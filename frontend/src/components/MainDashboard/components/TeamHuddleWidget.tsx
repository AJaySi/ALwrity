import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Chip,
  List,
  ListItem,
  Divider,
  IconButton,
  Tooltip,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { apiClient } from '../../../api/client';

type EventPayload = {
  phase?: string | null;
  step?: string | null;
  tool_name?: string | null;
  progress_percent?: number | null;
  input_summary?: string | null;
  output_summary?: string | null;
  decision_reason?: string | null;
  evidence_refs?: string[] | null;
  safe_debug?: boolean;
  metadata?: Record<string, unknown>;
};

type TeamActivityEvent = {
  id: number;
  event_type: string;
  severity: string;
  message?: string | null;
  created_at?: string | null;
  payload?: EventPayload | null;
};

type AgentRun = {
  id: number;
  agent_type: string;
  status: string;
  started_at?: string | null;
};

const TeamHuddleWidget: React.FC = () => {
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [timeline, setTimeline] = React.useState<Array<{ run: AgentRun; events: TeamActivityEvent[] }>>([]);

  const loadTimeline = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const runsResp = await apiClient.get('/api/agents/runs', { params: { limit: 5 } });
      const runs: AgentRun[] = runsResp?.data?.data?.runs || [];

      const eventResponses = await Promise.all(
        runs.slice(0, 3).map(async (run) => {
          const eventsResp = await apiClient.get(`/api/agents/runs/${run.id}/events`, { params: { limit: 25 } });
          return {
            run,
            events: (eventsResp?.data?.data?.events || []) as TeamActivityEvent[],
          };
        }),
      );

      setTimeline(eventResponses);
    } catch (e: any) {
      setError(e?.message || 'Failed to load team activity');
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadTimeline();
  }, [loadTimeline]);

  return (
    <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="h6" fontWeight={700}>Team Activity</Typography>
          <Chip label="Live" size="small" color="success" sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700 }} />
        </Box>
        <Tooltip title="Refresh Team Activity">
          <IconButton size="small" onClick={loadTimeline}>
            <RefreshIcon fontSize="small" />
          </IconButton>
        </Tooltip>
      </Box>

      {loading && (
        <Box py={4} textAlign="center">
          <CircularProgress size={24} />
        </Box>
      )}

      {!loading && error && (
        <Typography variant="body2" color="error">{error}</Typography>
      )}

      {!loading && !error && timeline.length === 0 && (
        <Typography variant="body2" color="text.secondary">No team activity yet.</Typography>
      )}

      {!loading && !error && timeline.length > 0 && (
        <List disablePadding>
          {timeline.map(({ run, events }, index) => (
            <React.Fragment key={run.id}>
              {index > 0 && <Divider sx={{ my: 1 }} />}
              <ListItem disableGutters sx={{ display: 'block' }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                  <Chip size="small" label={run.agent_type || 'Agent'} />
                  <Chip size="small" color={run.status === 'completed' ? 'success' : 'warning'} label={run.status} />
                  <Typography variant="caption" color="text.secondary">
                    {run.started_at ? new Date(run.started_at).toLocaleString() : ''}
                  </Typography>
                </Stack>

                {events.map((event) => {
                  const payload = event.payload || {};
                  return (
                    <Accordion key={event.id} disableGutters elevation={0} sx={{ border: '1px solid #e5e7eb', mb: 1 }}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Stack direction="row" spacing={1} alignItems="center" sx={{ width: '100%' }}>
                          <Chip size="small" label={payload.phase || event.event_type} />
                          {payload.step && <Chip size="small" variant="outlined" label={payload.step} />}
                          <Typography variant="body2" sx={{ flexGrow: 1 }}>
                            {event.message || payload.output_summary || 'Activity update'}
                          </Typography>
                          {typeof payload.progress_percent === 'number' && (
                            <Typography variant="caption" color="text.secondary">{payload.progress_percent}%</Typography>
                          )}
                        </Stack>
                      </AccordionSummary>
                      <AccordionDetails>
                        <Typography variant="caption" display="block">Tool: {payload.tool_name || '—'}</Typography>
                        <Typography variant="caption" display="block">Input: {payload.input_summary || '—'}</Typography>
                        <Typography variant="caption" display="block">Output: {payload.output_summary || '—'}</Typography>
                        <Typography variant="caption" display="block">Decision: {payload.decision_reason || '—'}</Typography>
                        <Typography variant="caption" display="block">Evidence: {(payload.evidence_refs || []).join(', ') || '—'}</Typography>
                        <Typography variant="caption" display="block">Safe debug: {String(payload.safe_debug ?? true)}</Typography>
                      </AccordionDetails>
                    </Accordion>
                  );
                })}
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}
    </Paper>
  );
};

export default TeamHuddleWidget;
