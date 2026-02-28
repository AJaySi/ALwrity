import React from 'react';
import { Card, CardContent, Box, Typography, Tooltip, Chip, Button, Grid, List, ListItem, Paper } from '@mui/material';
import { Info, MouseOutlined, Visibility } from '@mui/icons-material';
import ChipLegend from './ChipLegend';

interface DeltaQuery {
  query: string;
  deltaClicks: number;
  deltaImpressions: number;
}

interface RefreshQueuePanelProps {
  risingQueries: DeltaQuery[];
  decliningQueries: DeltaQuery[];
  loading: boolean;
  onRecompute: () => void;
  formatNumber: (n: number) => string;
}

const RefreshQueuePanel: React.FC<RefreshQueuePanelProps> = ({ risingQueries, decliningQueries, loading, onRecompute, formatNumber }) => {
  const hasNoData = risingQueries.length === 0 && decliningQueries.length === 0;

  return (
    <Card sx={{ mt: 2, bgcolor: '#ffffff !important', color: '#1f2937 !important', border: '1px solid #e5e7eb !important', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1) !important' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle1">Refresh Queue (Current vs Previous)</Typography>
            <Tooltip title="Highlights topics gaining or losing traction compared to the previous window. Rising = more clicks or impressions; declining = fewer. Use this to refresh content.">
              <Info fontSize="small" color="action" />
            </Tooltip>
          </Box>
          <Button onClick={onRecompute} disabled={loading} variant="outlined" size="small" sx={{ textTransform: 'none' }}>
            {loading ? 'Computing…' : 'Recompute'}
          </Button>
        </Box>

        <ChipLegend
          items={[
            { label: 'Δ Clicks', icon: <MouseOutlined fontSize="small" />, tooltip: 'Change in clicks vs previous period', sx: { backgroundImage: 'linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%)', color: '#1e40af', border: '1px solid #bfdbfe', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'Δ Impr', icon: <Visibility fontSize="small" />, tooltip: 'Change in impressions vs previous period', sx: { backgroundImage: 'linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%)', color: '#065f46', border: '1px solid #a7f3d0', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
          ]}
        />

        {hasNoData ? (
          <Typography variant="body2" color="text.secondary">No rising or declining queries detected.</Typography>
        ) : (
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>Rising Queries</Typography>
              <List dense>
                {risingQueries.map((q, i) => (
                  <ListItem key={`rise-${i}`} sx={{ px: 0, py: 0.5 }}>
                    <Paper elevation={0} sx={{ px: 1, py: 0.75, width: '100%', borderRadius: 2, border: '1px solid #e5e7eb', background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, width: '100%', justifyContent: 'space-between' }}>
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              color: '#111827',
                              fontWeight: 500,
                            }}
                          >
                            {q.query}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, flexShrink: 0 }}>
                          <Tooltip title="Additional clicks compared to previous window">
                            <Chip icon={<MouseOutlined fontSize="small" />} label={`+${formatNumber(Math.max(0, q.deltaClicks))}`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%)', color: '#065f46', border: '1px solid #a7f3d0', fontWeight: 700 }} />
                          </Tooltip>
                          <Tooltip title="Additional impressions compared to previous window">
                            <Chip icon={<Visibility fontSize="small" />} label={`+${formatNumber(Math.max(0, q.deltaImpressions))}`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #dbeafe 0%, #eff6ff 100%)', color: '#1e40af', border: '1px solid #bfdbfe', fontWeight: 700 }} />
                          </Tooltip>
                        </Box>
                        <Button size="small" variant="outlined" sx={{ textTransform: 'none' }}>Open in Writer</Button>
                      </Box>
                    </Paper>
                  </ListItem>
                ))}
              </List>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" gutterBottom>Declining Queries</Typography>
              <List dense>
                {decliningQueries.map((q, i) => (
                  <ListItem key={`decl-${i}`} sx={{ px: 0, py: 0.5 }}>
                    <Paper elevation={0} sx={{ px: 1, py: 0.75, width: '100%', borderRadius: 2, border: '1px solid #e5e7eb', background: 'linear-gradient(180deg, #ffffff 0%, #fff7ed 100%)' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, width: '100%', justifyContent: 'space-between' }}>
                        <Box sx={{ minWidth: 0, flex: 1 }}>
                          <Typography
                            variant="body2"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                              color: '#111827',
                              fontWeight: 500,
                            }}
                          >
                            {q.query}
                          </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, flexShrink: 0 }}>
                          <Tooltip title="Lost clicks compared to previous window">
                            <Chip icon={<MouseOutlined fontSize="small" />} label={`${formatNumber(q.deltaClicks)}`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #fee2e2 0%, #fff1f2 100%)', color: '#991b1b', border: '1px solid #fecaca', fontWeight: 700 }} />
                          </Tooltip>
                          <Tooltip title="Lost impressions compared to previous window">
                            <Chip icon={<Visibility fontSize="small" />} label={`${formatNumber(q.deltaImpressions)}`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #ffedd5 0%, #fff7ed 100%)', color: '#9a3412', border: '1px solid #fed7aa', fontWeight: 700 }} />
                          </Tooltip>
                        </Box>
                        <Button size="small" variant="outlined" color="warning" sx={{ textTransform: 'none' }}>Create Brief</Button>
                      </Box>
                    </Paper>
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>
        )}
      </CardContent>
    </Card>
  );
};

export default RefreshQueuePanel;
