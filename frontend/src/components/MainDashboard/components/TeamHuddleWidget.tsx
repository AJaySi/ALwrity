import React from 'react';
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
  Tooltip
} from '@mui/material';
import {
  Psychology as StrategyIcon,
  Article as ContentIcon,
  Search as SeoIcon,
  Campaign as SocialIcon,
  CompareArrows as CompetitorIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { Link as RouterLink } from 'react-router-dom';
import { useAgentHuddleFeed } from '../../../hooks/useAgentHuddleFeed';

const ICON_BY_AGENT: Record<string, React.ElementType> = {
  strategy: StrategyIcon,
  content: ContentIcon,
  seo: SeoIcon,
  social: SocialIcon,
  competitor: CompetitorIcon,
};

const TeamHuddleWidget: React.FC = () => {
  const { runs, connectionMode, lastHeartbeatAt } = useAgentHuddleFeed();

  // Create rows for the widget from the feed runs
  // Note: events are not directly used in the simple widget view, but available if needed
  const rows = React.useMemo(() => {
    return runs.slice(0, 5).map((run) => {
      const agentType = String(run.agent_type || 'strategy');
      // Simple heuristic for icon mapping
      let IconComponent = StrategyIcon;
      for (const key in ICON_BY_AGENT) {
        if (agentType.toLowerCase().includes(key)) {
          IconComponent = ICON_BY_AGENT[key];
          break;
        }
      }
      
      const status = run.status === 'running' ? 'thinking' : run.success === false ? 'offline' : 'active';
      return {
        id: run.id,
        name: agentType.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
        role: run.status || 'active',
        status,
        current_activity: run.result_summary || run.error_message || 'Awaiting next update',
        icon: IconComponent,
      };
    });
  }, [runs]);

  return (
    <Paper elevation={0} sx={{ p: 2, borderRadius: 3, border: '1px solid', borderColor: 'divider', height: '100%', background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)' }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box display="flex" alignItems="center" gap={1}>
          <Typography variant="h6" fontWeight={700} color="text.primary">Team Huddle</Typography>
          <Chip label={connectionMode === 'sse' ? 'Live' : connectionMode === 'polling' ? 'Polling' : 'Connecting'} size="small" color={connectionMode === 'sse' ? 'success' : 'warning'} sx={{ height: 20, fontSize: '0.65rem', fontWeight: 700 }} />
        </Box>
        <Tooltip title={lastHeartbeatAt ? `Heartbeat ${new Date(lastHeartbeatAt).toLocaleTimeString()}` : 'Waiting for heartbeat'}>
          <IconButton size="small"><RefreshIcon fontSize="small" /></IconButton>
        </Tooltip>
      </Box>

      {rows.length === 0 ? (
        <Box display="flex" justifyContent="center" alignItems="center" minHeight={180}>
          <Typography variant="body2" color="text.secondary" textAlign="center">
            No active agent activity right now.
          </Typography>
        </Box>
      ) : (
        <List disablePadding>
          {rows.map((agent, index) => (
            <React.Fragment key={agent.id}>
              {index > 0 && <Divider variant="inset" component="li" sx={{ my: 1, ml: 7 }} />}
              <ListItem alignItems="flex-start" disableGutters sx={{ py: 0.5 }}>
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: '#eef2ff', color: '#6366f1', width: 40, height: 40 }}><agent.icon fontSize="small" /></Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={<Box display="flex" alignItems="center" gap={1}><Typography variant="subtitle2" fontWeight={600}>{agent.name}</Typography><Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem', border: '1px solid #e2e8f0', px: 0.5, borderRadius: 1 }}>{agent.role}</Typography></Box>}
                  secondary={<Typography variant="body2" color="text.secondary" sx={{ display: '-webkit-box', WebkitLineClamp: 1, WebkitBoxOrient: 'vertical', overflow: 'hidden', fontSize: '0.75rem', mt: 0.25 }}>{agent.current_activity}</Typography>}
                />
              </ListItem>
            </React.Fragment>
          ))}
        </List>
      )}

      <Box mt={2} pt={2} borderTop="1px solid #eee" display="flex" justifyContent="center">
        <Typography component={RouterLink} to="/team-activity" variant="caption" color="primary" sx={{ fontWeight: 600, textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}>
          View Full Team Activity
        </Typography>
      </Box>
    </Paper>
  );
};

export default TeamHuddleWidget;
