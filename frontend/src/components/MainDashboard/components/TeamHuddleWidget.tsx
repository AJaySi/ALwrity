import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Avatar,
  AvatarGroup,
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
  Refresh as RefreshIcon,
  MoreVert as MoreVertIcon
} from '@mui/icons-material';

interface AgentStatus {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'thinking' | 'idle' | 'offline';
  current_activity: string;
  icon: React.ElementType;
  color: string;
}

// Mock data - In real implementation, this would come from a backend endpoint
// /api/agents/status or similar
const AGENT_TEAM: AgentStatus[] = [
  {
    id: 'strategy_architect',
    name: 'Strategy Architect',
    role: 'Team Lead',
    status: 'active',
    current_activity: 'Analyzing content pillar performance',
    icon: StrategyIcon,
    color: '#6366f1' // Indigo
  },
  {
    id: 'content_strategist',
    name: 'Content Strategist',
    role: 'Creative',
    status: 'thinking',
    current_activity: 'Identifying semantic gaps in "AI Tools"',
    icon: ContentIcon,
    color: '#10b981' // Emerald
  },
  {
    id: 'seo_specialist',
    name: 'SEO Specialist',
    role: 'Technical',
    status: 'idle',
    current_activity: 'Monitoring SERP rankings',
    icon: SeoIcon,
    color: '#f59e0b' // Amber
  },
  {
    id: 'social_manager',
    name: 'Social Manager',
    role: 'Engagement',
    status: 'idle',
    current_activity: 'Waiting for new content to schedule',
    icon: SocialIcon,
    color: '#ec4899' // Pink
  },
   {
    id: 'competitor_analyst',
    name: 'Competitor Analyst',
    role: 'Intelligence',
    status: 'active',
    current_activity: 'Scanning competitor X for new posts',
    icon: CompetitorIcon,
    color: '#ef4444' // Red
  }
];

const TeamHuddleWidget: React.FC = () => {
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
        </Box>
        <Box>
           <Tooltip title="Refresh Team Status">
            <IconButton size="small">
              <RefreshIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <List disablePadding>
        {AGENT_TEAM.map((agent, index) => (
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
      
      <Box mt={2} pt={2} borderTop="1px solid #eee" display="flex" justifyContent="center">
        <Typography variant="caption" color="primary" sx={{ fontWeight: 600, cursor: 'pointer', '&:hover': { textDecoration: 'underline' } }}>
          View Full Team Activity
        </Typography>
      </Box>
    </Paper>
  );
};

export default TeamHuddleWidget;
