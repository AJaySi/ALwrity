import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Stack,
  Divider
} from '@mui/material';
import { gscAPI } from '../../api/gsc';

interface Props {
  siteUrl?: string;
  compact?: boolean;
  title?: string;
}

const GSCTaskReportsPanel: React.FC<Props> = ({ siteUrl, compact = false, title = 'GSC Task Reports (Issues 1-4)' }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<any>(null);
  const [runningTask, setRunningTask] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await gscAPI.getTaskReports(siteUrl);
      setData(response);
    } catch (e: any) {
      setError(e?.message || 'Failed to load task reports');
    } finally {
      setLoading(false);
    }
  };

  const runTask = async (taskKey: string) => {
    setRunningTask(taskKey);
    try {
      await gscAPI.runTaskReport(taskKey, siteUrl);
      await load();
    } catch (e) {
      console.error('Failed to run task:', e);
    } finally {
      setRunningTask(null);
    }
  };

  useEffect(() => {
    load();
  }, [siteUrl]);

  return (
    <Paper elevation={2} sx={{ p: 2, mt: 2, borderRadius: 2 }}>
      <Stack direction="row" alignItems="center" justifyContent="space-between" mb={1}>
        <Typography variant={compact ? 'subtitle1' : 'h6'} fontWeight={700}>{title}</Typography>
        <Button variant="outlined" size="small" onClick={load}>Refresh</Button>
      </Stack>

      {loading && <CircularProgress size={22} />}
      {error && <Alert severity="error">{error}</Alert>}
      {data?.connected === false && <Alert severity="info">Connect GSC and choose a property to preview these tasks.</Alert>}

      {data?.sections?.map((section: any) => (
        <Box key={section.issue_key} sx={{ py: 1.2 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={1}>
            <Box>
              <Typography variant="subtitle2" fontWeight={700}>{section.title}</Typography>
              <Typography variant="body2" color="text.secondary">{section.description}</Typography>
            </Box>
            <Button
              size="small"
              variant="contained"
              onClick={() => runTask(section.issue_key)}
              disabled={runningTask === section.issue_key}
            >
              {runningTask === section.issue_key ? 'Running…' : 'Run once'}
            </Button>
          </Stack>

          <Stack direction="row" spacing={1} mt={1} flexWrap="wrap" useFlexGap>
            {Object.entries(section.metrics || {}).map(([k, v]) => (
              <Chip key={k} label={`${k}: ${Array.isArray(v) ? v.join(', ') : String(v)}`} size="small" />
            ))}
          </Stack>

          {!compact && Array.isArray(section.items) && section.items.slice(0, 3).map((item: any, idx: number) => (
            <Typography key={idx} variant="caption" display="block" color="text.secondary" mt={0.5}>
              • {item.query || item.query_template || JSON.stringify(item)}
            </Typography>
          ))}
          <Divider sx={{ mt: 1.2 }} />
        </Box>
      ))}
    </Paper>
  );
};

export default GSCTaskReportsPanel;
