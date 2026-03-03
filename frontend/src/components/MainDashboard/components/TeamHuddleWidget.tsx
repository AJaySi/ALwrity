import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  Chip,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Divider,
  IconButton,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Psychology as StrategyIcon,
  Article as ContentIcon,
  Search as SeoIcon,
  Campaign as SocialIcon,
  CompareArrows as CompetitorIcon,
  SmartToy as AgentIcon,
  Refresh as RefreshIcon,
  WarningAmber as WarningIcon
} from '@mui/icons-material';
import { apiClient } from '../../../api/client';

interface AgentCard {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'thinking' | 'idle' | 'offline';
  current_activity: string;
  icon: React.ElementType;
  color: string;
}

interface AgentMeta {
  name: string;
  role: string;
  icon: React.ElementType;
  color: string;
}

const AGENT_META: Record<string, AgentMeta> = {
  strategy: {
    name: 'Strategy Architect',
    role: 'Team Lead',
    icon: StrategyIcon,
    color: '#6366f1'
  },
  content: {
    name: 'Content Strategist',
    role: 'Creative',
    icon: ContentIcon,
    color: '#10b981'
  },
  seo: {
    name: 'SEO Specialist',
    role: 'Technical',
    icon: SeoIcon,
    color: '#f59e0b'
  },
  social: {
    name: 'Social Manager',
    role: 'Engagement',
    icon: SocialIcon,
    color: '#ec4899'
  },
  competitor: {
    name: 'Competitor Analyst',
    role: 'Intelligence',
    icon: CompetitorIcon,
    color: '#ef4444'
  }
};

const normalizeAgentKey = (rawKey: string): string => {
  const key = (rawKey || '').toLowerCase();

  if (key.includes('strategy')) return 'strategy';
  if (key.includes('content')) return 'content';
  if (key.includes('seo') || key.includes('search')) return 'seo';
  if (key.includes('social')) return 'social';
  if (key.includes('competitor') || key.includes('competition')) return 'competitor';

  return key;
};

const normalizeStatus = (status: string): AgentCard['status'] => {
  const value = (status || '').toLowerCase();

  if (value === 'active' || value === 'thinking' || value === 'idle' || value === 'offline') {
    return value;
  }

  if (value === 'running' || value === 'busy') return 'active';
  if (value === 'processing' || value === 'analyzing') return 'thinking';
  if (value === 'inactive' || value === 'stopped') return 'offline';

  return 'idle';
};

const TeamHuddleWidget: React.FC = () => {
  const navigate = useNavigate();
  const [agents, setAgents] = React.useState<AgentCard[]>([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);
  const [refreshing, setRefreshing] = React.useState(false);
  const [alertCount, setAlertCount] = React.useState(0);

  const fetchTeamData = React.useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }

    setError(null);

    try {
      const [statusResp, runsResp, alertsResp] = await Promise.allSettled([
        apiClient.get('/api/agents/status'),
        apiClient.get('/api/agents/runs', { params: { limit: 20 } }),
        apiClient.get('/api/agents/alerts', { params: { unread_only: true, limit: 20 } })
      ]);

      if (statusResp.status !== 'fulfilled') {
        throw new Error('Unable to load team status');
      }

      const statusPayload = statusResp.value?.data?.data?.agents || statusResp.value?.data?.agents || [];
      const runsPayload = runsResp.status === 'fulfilled'
        ? (runsResp.value?.data?.data?.runs || runsResp.value?.data?.runs || [])
        : [];
      const alertsPayload = alertsResp.status === 'fulfilled'
        ? (alertsResp.value?.data?.data?.alerts || alertsResp.value?.data?.alerts || [])
        : [];

      const runByAgent = new Map<string, string>();
      runsPayload.forEach((run: Record<string, unknown>) => {
        const key = normalizeAgentKey((run.agent_key || run.agent || run.agent_id || '') as string);
        if (!key || runByAgent.has(key)) return;

        runByAgent.set(
          key,
          (run.summary || run.context || run.activity || run.status_message || 'Working on recent tasks') as string
        );
      });

      const normalizedAgents: AgentCard[] = statusPayload.map((agent: Record<string, unknown>, index: number) => {
        const rawKey = (agent.key || agent.agent_key || agent.id || agent.name || `agent-${index}`) as string;
        const normalizedKey = normalizeAgentKey(rawKey);
        const meta = AGENT_META[normalizedKey] || {
          name: (agent.display_name || agent.name || rawKey) as string,
          role: 'AI Agent',
          icon: AgentIcon,
          color: '#64748b'
        };

        return {
          id: String(rawKey),
          name: (agent.display_name || meta.name) as string,
          role: (agent.role || meta.role) as string,
          status: normalizeStatus((agent.status || agent.operational_status || '') as string),
          current_activity:
            (agent.current_activity ||
            runByAgent.get(normalizedKey) ||
            agent.last_message ||
            'Waiting for next instruction') as string,
          icon: meta.icon,
          color: meta.color
        };
      });

      setAgents(normalizedAgents);
      setAlertCount(Array.isArray(alertsPayload) ? alertsPayload.length : 0);
    } catch (err) {
      console.error('Failed to load team huddle data:', err);
      setError('Could not load team huddle data. Please try again.');
      setAgents([]);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  React.useEffect(() => {
    fetchTeamData();
  }, [fetchTeamData]);

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        borderRadius: 3,
        border: '1px solid',
        borderColor: 'divider',
        height: '100%',
        background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)'
      }}
    >
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="h6" fontWeight={700} color="text.primary">
            Team Huddle
          </Typography>
          <Chip
            label="Live"
            size="small"
            color="success"
            sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700 }}
          />
          {alertCount > 0 && (
            <Chip
              icon={<WarningIcon fontSize="small" />}
              label={`${alertCount} alert${alertCount > 1 ? 's' : ''}`}
              size="small"
              color="warning"
              sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700 }}
            />
          )}
        </Box>
        <Box>
          <Tooltip title="Refresh Team Status">
            <span>
              <IconButton size="small" onClick={() => fetchTeamData(true)} disabled={loading || refreshing}>
                {refreshing ? <CircularProgress size={16} /> : <RefreshIcon fontSize="small" />}
              </IconButton>
            </span>
          </Tooltip>
        </Box>
      </Box>

      {loading ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={180}>
          <CircularProgress size={24} />
        </Box>
      ) : error ? (
        <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight={180} gap={1}>
          <Typography variant="body2" color="error.main" textAlign="center">
            {error}
          </Typography>
          <Typography
            variant="caption"
            color="primary"
            sx={{ fontWeight: 600, cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}
            onClick={() => fetchTeamData(true)}
          >
            Retry
          </Typography>
        </Box>
      ) : agents.length === 0 ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={180}>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No active agent activity right now.
          </Typography>
        </Box>
      ) : (
        <List disablePadding>
          {agents.map((agent, index) => (
            <React.Fragment key={agent.id}>
              {index > 0 && <Divider variant="inset" component="li" sx={{ my: 1, ml: 7 }} />}
              <ListItem
                alignItems="flex-start"
                disableGutters
                sx={{ py: 0.5 }}
                secondaryAction={
                  <Tooltip title={agent.status}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor:
                          agent.status === 'active' ? '#22c55e' :
                          agent.status === 'thinking' ? '#3b82f6' :
                          agent.status === 'offline' ? '#cbd5e1' :
                          '#94a3b8',
                        boxShadow: agent.status === 'active' ? '0 0 0 2px rgba(34, 197, 94, 0.2)' : 'none',
                        animation: agent.status === 'thinking' ? 'pulse 1.5s infinite' : 'none',
                        '@keyframes pulse': {
                          '0%': { opacity: 1, transform: 'scale(1)' },
                          '50%': { opacity: 0.6, transform: 'scale(1.2)' },
                          '100%': { opacity: 1, transform: 'scale(1)' }
                        }
                      }}
                    />
                  </Tooltip>
                }
              >
                <ListItemAvatar>
                  <Avatar
                    sx={{
                      bgcolor: `${agent.color}15`,
                      color: agent.color,
                      width: 40,
                      height: 40
                    }}
                  >
                    <agent.icon fontSize="small" />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {agent.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem', border: '1px solid #e2e8f0', px: 0.5, borderRadius: 1 }}>
                        {agent.role}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Typography
                      variant="body2"
                      color="text.secondary"
                      sx={{
                        display: '-webkit-box',
                        WebkitLineClamp: 1,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        fontSize: '0.75rem',
                        mt: 0.25
                      }}
                    >
                      {agent.current_activity}
                    </Typography>
                  }
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}

      <Box mt={2} pt={2} borderTop="1px solid #eee" display="flex" justifyContent="center">
        <Typography
          component="button"
          type="button"
          variant="caption"
          color="primary"
          onClick={() => navigate('/team-activity')}
          sx={{
            border: 0,
            bgcolor: 'transparent',
            p: 0,
            fontWeight: 600,
            cursor: 'pointer',
            '&:hover': { textDecoration: 'underline' }
          }}
        >
          View Full Team Activity
        </Typography>
      </Box>
    </Paper>
  );
};

export default TeamHuddleWidget;
