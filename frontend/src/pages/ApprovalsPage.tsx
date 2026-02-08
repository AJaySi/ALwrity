import React from 'react';
import { Box, Typography, Paper, Stack, Button, Chip, CircularProgress } from '@mui/material';
import { apiClient } from '../api/client';

type Approval = {
  id: number;
  status: string;
  decision?: string | null;
  action_id: string;
  action_type: string;
  agent_type?: string | null;
  target_resource?: string | null;
  risk_level: number;
  payload?: any;
  created_at?: string | null;
};

export default function ApprovalsPage() {
  const [loading, setLoading] = React.useState(false);
  const [approvals, setApprovals] = React.useState<Approval[]>([]);
  const [error, setError] = React.useState<string | null>(null);

  const loadApprovals = React.useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await apiClient.get('/api/agents/approvals', { params: { status: 'pending', limit: 50 } });
      const items = resp?.data?.data?.approvals || [];
      setApprovals(items);
    } catch (e: any) {
      setError(e?.message || 'Failed to load approvals');
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    loadApprovals();
  }, [loadApprovals]);

  const decide = async (approvalId: number, decision: 'approved' | 'rejected') => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.post(`/api/agents/approvals/${approvalId}/decision`, { decision });
      await loadApprovals();
    } catch (e: any) {
      setError(e?.message || 'Failed to submit decision');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 2 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>Agent Approvals</Typography>
        <Button variant="outlined" onClick={loadApprovals} disabled={loading}>Refresh</Button>
      </Stack>

      {error && (
        <Paper sx={{ p: 2, mb: 2, border: '1px solid #fecaca', bgcolor: '#fef2f2' }}>
          <Typography sx={{ color: '#991b1b', fontWeight: 600 }}>{error}</Typography>
        </Paper>
      )}

      {loading && approvals.length === 0 && (
        <Stack alignItems="center" sx={{ py: 6 }}>
          <CircularProgress />
        </Stack>
      )}

      {approvals.length === 0 && !loading && (
        <Paper sx={{ p: 3 }}>
          <Typography sx={{ color: '#6b7280' }}>No pending approvals.</Typography>
        </Paper>
      )}

      <Stack spacing={2}>
        {approvals.map((a) => (
          <Paper key={a.id} sx={{ p: 2 }}>
            <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
              <Chip label={a.agent_type || 'Agent'} size="small" />
              <Chip label={`Risk ${a.risk_level.toFixed(2)}`} size="small" color={a.risk_level >= 0.8 ? 'error' : a.risk_level >= 0.6 ? 'warning' : 'default'} />
              <Chip label={a.status} size="small" />
            </Stack>

            <Typography sx={{ fontWeight: 700, mb: 0.5 }}>{a.action_type}</Typography>
            {a.target_resource && (
              <Typography sx={{ color: '#6b7280', mb: 1 }}>{a.target_resource}</Typography>
            )}

            <Stack direction="row" spacing={1}>
              <Button variant="contained" onClick={() => decide(a.id, 'approved')} disabled={loading}>Approve</Button>
              <Button variant="outlined" color="error" onClick={() => decide(a.id, 'rejected')} disabled={loading}>Reject</Button>
            </Stack>
          </Paper>
        ))}
      </Stack>
    </Box>
  );
}

