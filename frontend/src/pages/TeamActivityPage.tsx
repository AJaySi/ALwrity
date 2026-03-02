import React from 'react';
import {
  Box,
  Chip,
  Divider,
  Paper,
  Stack,
  Typography,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';

const activeRuns = [
  { id: 'run-9142', title: 'Q4 SEO Pillar Refresh', owner: 'SEO Specialist', progress: '67%' },
  { id: 'run-9143', title: 'LinkedIn Carousel Draft', owner: 'Content Strategist', progress: '42%' },
  { id: 'run-9144', title: 'Competitor Monitoring Sweep', owner: 'Competitor Analyst', progress: '88%' },
];

const timelineEvents = [
  { time: '09:20', detail: 'Strategy Architect approved updated campaign goals.' },
  { time: '09:35', detail: 'Social Manager queued 6 posts for review.' },
  { time: '10:05', detail: 'SEO Specialist flagged ranking drop on "AI copy tools".' },
  { time: '10:24', detail: 'Content Strategist generated new briefing packet.' },
];

const alerts = [
  { severity: 'high', label: '2 content briefs are blocked on missing references.' },
  { severity: 'medium', label: 'SERP volatility increased for 3 tracked keywords.' },
];

const approvals = [
  { id: 'ap-112', action: 'Publish LinkedIn thread for Campaign Alpha', requestedBy: 'Social Manager' },
  { id: 'ap-113', action: 'Approve budget reallocation to ad creatives', requestedBy: 'Strategy Architect' },
];

export default function TeamActivityPage() {
  return (
    <Box sx={{ p: { xs: 2, md: 3 } }}>
      <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
        Team Activity
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Real-time view of active agent workstreams, timelines, alerts, and pending approvals.
      </Typography>

      <Stack spacing={2.5}>
        <Paper sx={{ p: 2.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Active Runs</Typography>
          <Stack spacing={1}>
            {activeRuns.map((run) => (
              <Stack key={run.id} direction="row" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography sx={{ fontWeight: 600 }}>{run.title}</Typography>
                  <Typography variant="caption" color="text.secondary">{run.owner}</Typography>
                </Box>
                <Chip size="small" label={run.progress} color="primary" variant="outlined" />
              </Stack>
            ))}
          </Stack>
        </Paper>

        <Paper sx={{ p: 2.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Event Timeline</Typography>
          <List disablePadding>
            {timelineEvents.map((event, index) => (
              <React.Fragment key={`${event.time}-${event.detail}`}>
                {index > 0 && <Divider sx={{ my: 1 }} />}
                <ListItem disableGutters sx={{ py: 0 }}>
                  <ListItemText
                    primary={<Typography sx={{ fontWeight: 600 }}>{event.detail}</Typography>}
                    secondary={<Typography variant="caption">{event.time}</Typography>}
                  />
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        </Paper>

        <Paper sx={{ p: 2.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Alerts</Typography>
          <Stack spacing={1}>
            {alerts.map((alert) => (
              <Chip
                key={alert.label}
                label={alert.label}
                color={alert.severity === 'high' ? 'error' : 'warning'}
                variant="outlined"
                sx={{ justifyContent: 'flex-start' }}
              />
            ))}
          </Stack>
        </Paper>

        <Paper sx={{ p: 2.5 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, mb: 1.5 }}>Approvals Requiring Action</Typography>
          <Stack spacing={1}>
            {approvals.map((approval) => (
              <Box key={approval.id}>
                <Typography sx={{ fontWeight: 600 }}>{approval.action}</Typography>
                <Typography variant="caption" color="text.secondary">Requested by {approval.requestedBy}</Typography>
              </Box>
            ))}
          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
}
