import React from 'react';
import { Box, Card, CardContent, Chip, Divider, Grid, List, ListItem, ListItemText, Typography } from '@mui/material';
import { useAgentHuddleFeed } from '../hooks/useAgentHuddleFeed';

const TeamActivityPage: React.FC = () => {
  const { runs, events, alerts, approvals, connectionMode } = useAgentHuddleFeed();

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Team Activity</Typography>
        <Chip label={connectionMode === 'sse' ? 'Live stream' : 'Polling fallback'} color={connectionMode === 'sse' ? 'success' : 'warning'} />
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Run lifecycle updates</Typography>
            <List dense>
              {runs.slice(0, 20).map((run) => (
                <ListItem key={run.id}><ListItemText primary={`${run.agent_type || 'agent'} · ${run.status}`} secondary={run.result_summary || run.finished_at || 'In progress'} /></ListItem>
              ))}
            </List>
          </CardContent></Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>New events</Typography>
            <List dense>
              {events.slice(0, 20).map((event) => (
                <ListItem key={event.id}><ListItemText primary={`${event.agent_type || 'agent'} · ${event.event_type}`} secondary={event.message || event.created_at} /></ListItem>
              ))}
            </List>
          </CardContent></Card>
        </Grid>

        <Grid item xs={12}><Divider /></Grid>

        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Alert deltas</Typography>
            <List dense>
              {alerts.slice(0, 20).map((alert) => (
                <ListItem key={alert.id}><ListItemText primary={alert.title || 'Alert'} secondary={alert.message} /></ListItem>
              ))}
            </List>
          </CardContent></Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card><CardContent>
            <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Approval deltas</Typography>
            <List dense>
              {approvals.slice(0, 20).map((approval) => (
                <ListItem key={approval.id}><ListItemText primary={`${approval.action_type || 'Action'} · ${approval.status}`} secondary={approval.created_at} /></ListItem>
              ))}
            </List>
          </CardContent></Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TeamActivityPage;
