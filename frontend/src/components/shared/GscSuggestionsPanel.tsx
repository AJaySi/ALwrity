import React from 'react';
import { Card, CardContent, Box, Typography, Tooltip, Chip, Button, List, ListItem, ListItemText, Paper } from '@mui/material';
import { Info, Visibility, TrendingDown, BarChart } from '@mui/icons-material';
import ChipLegend from './ChipLegend';

interface Suggestion {
  query: string;
  impressions: number;
  ctr: number;
  position: number;
}

interface GscSuggestionsPanelProps {
  suggestions: Suggestion[];
  rangeDays: number;
  onUseInWriter?: (s: Suggestion) => void;
  onProposeMeta?: (s: Suggestion) => void;
  formatNumber: (n: number) => string;
}

const GscSuggestionsPanel: React.FC<GscSuggestionsPanelProps> = ({ suggestions, rangeDays, onUseInWriter, onProposeMeta, formatNumber }) => {
  const impTh = rangeDays <= 7 ? 100 : rangeDays <= 30 ? 500 : 1500;
  const ctrTh = 2.5;

  return (
    <Card sx={{ mt: 2, bgcolor: '#ffffff !important', color: '#1f2937 !important', border: '1px solid #e5e7eb !important', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1) !important' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle1">GSC Suggestions (High Impressions • Low CTR)</Typography>
            <Tooltip title="Opportunities where many people saw your result but few clicked. Focus on improving titles and descriptions for these queries. CTR means click‑through rate.">
              <Info fontSize="small" color="action" />
            </Tooltip>
          </Box>
          <Typography variant="caption" color="text.secondary">Top {suggestions.length} opportunities</Typography>
        </Box>
        <ChipLegend
          items={[
            { label: 'Impressions', icon: <Visibility fontSize="small" />, tooltip: `Impressions ≥ ${impTh} are considered high visibility for this window.`, sx: { backgroundImage: 'linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%)', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'Low CTR', icon: <TrendingDown fontSize="small" />, tooltip: `CTR ≤ ${ctrTh}% indicates low click‑through. Improve titles/meta.`, sx: { backgroundImage: 'linear-gradient(135deg, #fee2e2 0%, #fff1f2 100%)', color: '#991b1b', border: '1px solid #fecaca', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'Avg Pos', icon: <BarChart fontSize="small" />, tooltip: 'Average position gives ranking context.', sx: { backgroundImage: 'linear-gradient(135deg, #ede9fe 0%, #eff6ff 100%)', color: '#4c1d95', border: '1px solid #ddd6fe', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
          ]}
        />
        {suggestions.length === 0 ? (
          <Typography variant="body2" color="text.secondary">No low‑CTR queries found for this window.</Typography>
        ) : (
          <List dense>
            {suggestions.map((s, idx) => {
              const ctrColor = s.ctr >= 3 ? '#065f46' : s.ctr >= 1 ? '#92400e' : '#7f1d1d';
              const ctrBg = s.ctr >= 3 ? 'linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%)' : s.ctr >= 1 ? 'linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%)' : 'linear-gradient(135deg, #fee2e2 0%, #fff1f2 100%)';
              return (
                <ListItem key={`${s.query}-${idx}`} sx={{ px: 0, py: 0.5 }}>
                  <Paper elevation={0} sx={{ px: 1.25, py: 1, width: '100%', borderRadius: 2, border: '1px solid #e5e7eb', background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, width: '100%', justifyContent: 'space-between' }}>
                      <Box sx={{ minWidth: 0, flex: 1 }}>
                        <Tooltip title={`Impressions ≥ ${impTh}, CTR ≤ ${ctrTh}% • This: ${formatNumber(s.impressions)} impressions, ${s.ctr.toFixed(1)}% CTR, position ${s.position.toFixed(1)}`}>
                          <ListItemText
                            primary={s.query}
                            primaryTypographyProps={{
                              variant: 'body2',
                              sx: {
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                color: '#111827',
                                fontWeight: 500,
                              },
                            }}
                          />
                        </Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, flexShrink: 0 }}>
                        <Tooltip title="Impressions">
                          <Chip label={`${formatNumber(s.impressions)} imp`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%)', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 }} />
                        </Tooltip>
                        <Tooltip title="CTR">
                          <Chip label={`${s.ctr.toFixed(1)}% CTR`} size="small" sx={{ backgroundImage: ctrBg, color: ctrColor, border: '1px solid rgba(0,0,0,0.06)', boxShadow: '0 1px 2px rgba(0,0,0,0.04)', fontWeight: 700 }} />
                        </Tooltip>
                        <Tooltip title="Average position">
                          <Chip label={`pos ${s.position.toFixed(1)}`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #ede9fe 0%, #eff6ff 100%)', color: '#4c1d95', border: '1px solid #ddd6fe', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 }} />
                        </Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Button size="small" variant="outlined" sx={{ textTransform: 'none' }} onClick={() => onUseInWriter && onUseInWriter(s)}>Use in Writer</Button>
                        <Button size="small" variant="contained" sx={{ textTransform: 'none' }} onClick={() => onProposeMeta && onProposeMeta(s)}>Propose Title/Meta</Button>
                      </Box>
                    </Box>
                  </Paper>
                </ListItem>
              );
            })}
          </List>
        )}
      </CardContent>
    </Card>
  );
};

export default GscSuggestionsPanel;
