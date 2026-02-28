import React from 'react';
import { Card, CardContent, Box, Typography, Tooltip, Chip, Button, List, ListItem, ListItemText, Paper, IconButton } from '@mui/material';
import { Info, MouseOutlined, Visibility, TrendingUp, OpenInNew } from '@mui/icons-material';
import ChipLegend from './ChipLegend';

type Query = { query: string; clicks: number; impressions: number; ctr: number };

interface TopPagesInsightsPanelProps {
  pages: Array<{ page: string; clicks: number; impressions: number; ctr: number; queries?: Query[] }>;
  risingQueries: Array<{ query: string }>;
  onOpenPage: (url: string) => void;
  onCreateBrief: (page: string, queries: Query[]) => void;
  formatNumber: (n: number) => string;
}

const TopPagesInsightsPanel: React.FC<TopPagesInsightsPanelProps> = ({ pages, risingQueries, onOpenPage, onCreateBrief, formatNumber }) => {
  const risingSet = React.useMemo(() => new Set(risingQueries.map(r => String(r.query || '').toLowerCase())), [risingQueries]);

  return (
    <Card sx={{ mt: 2, bgcolor: '#ffffff !important', color: '#1f2937 !important', border: '1px solid #e5e7eb !important', boxShadow: '0 1px 3px 0 rgba(0,0,0,0.1) !important' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle1">Top Pages Insights</Typography>
            <Tooltip title="Your pages with the most traffic from Google in this window. Improve winners and link to related pages to spread authority.">
              <Info fontSize="small" color="action" />
            </Tooltip>
          </Box>
          <Typography variant="caption" color="text.secondary">Sorted by clicks</Typography>
        </Box>
        <ChipLegend
          items={[
            { label: 'Clicks', icon: <MouseOutlined fontSize="small" />, tooltip: 'Total clicks in the selected date range', sx: { backgroundImage: 'linear-gradient(135deg, #dbeafe 0%, #eef2ff 100%)', color: '#1e3a8a', border: '1px solid #c7d2fe', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'Impressions', icon: <Visibility fontSize="small" />, tooltip: 'Total impressions in the selected date range', sx: { backgroundImage: 'linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%)', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'CTR', tooltip: 'Click-through rate', sx: { backgroundImage: 'linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%)', color: '#065f46', border: '1px solid #86efac', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
            { label: 'Trending', icon: <TrendingUp fontSize="small" />, tooltip: 'Appears in Rising Queries', sx: { backgroundImage: 'linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%)', color: '#065f46', border: '1px solid #a7f3d0', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 } },
          ]}
        />
        {(!pages || pages.length === 0) ? (
          <Typography variant="body2" color="text.secondary">No top pages for this window.</Typography>
        ) : (
          <List dense>
            {pages.slice(0, 10).map((p, idx) => {
              const clicks = Number(p.clicks || 0);
              const impressions = Number(p.impressions || 0);
              const ctr = Number(p.ctr || 0);
              const ctrColor = ctr >= 3 ? '#065f46' : ctr >= 1 ? '#92400e' : '#7f1d1d';
              const ctrBg = ctr >= 3 ? 'linear-gradient(135deg, #d1fae5 0%, #ecfdf5 100%)' : ctr >= 1 ? 'linear-gradient(135deg, #fef3c7 0%, #fffbeb 100%)' : 'linear-gradient(135deg, #fee2e2 0%, #fff1f2 100%)';
              const hasTrending = Array.isArray(p.queries) && p.queries!.some(q => risingSet.has(String(q.query || '').toLowerCase()));
              return (
                <ListItem key={`${p.page || 'page'}-${idx}`} sx={{ px: 0, py: 0.75 }}>
                  <Paper elevation={0} sx={{ px: 1.25, py: 1, width: '100%', borderRadius: 2, border: '1px solid #e5e7eb', background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)', transition: 'all .2s', '&:hover': { boxShadow: '0 6px 12px rgba(17,24,39,0.06)', transform: 'translateY(-1px)' } }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%', justifyContent: 'space-between' }}>
                      <Box sx={{ minWidth: 0, flex: 1 }}>
                        <Tooltip title={`Total clicks ${clicks}, total impressions ${impressions}, CTR ${ctr.toFixed(1)}% for the selected range`}>
                          <ListItemText
                            primary={p.page || '(unknown page)'}
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
                        {hasTrending && <Chip icon={<TrendingUp fontSize="small" />} label="Trending" size="small" sx={{ mt: 0.5, backgroundImage: 'linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%)', color: '#065f46', border: '1px solid #a7f3d0', boxShadow: '0 1px 2px rgba(0,0,0,0.04)', fontWeight: 700 }} />}
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.2, mr: 1, flexShrink: 0 }}>
                        <Tooltip title="Total clicks across the selected date range. Higher is better.">
                          <Chip icon={<MouseOutlined fontSize="small" />} label={`${formatNumber(clicks)} clicks`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #dbeafe 0%, #eef2ff 100%)', color: '#1e3a8a', border: '1px solid #c7d2fe', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 }} />
                        </Tooltip>
                        <Tooltip title="Total impressions across the selected date range. Indicates visibility in search results.">
                          <Chip icon={<Visibility fontSize="small" />} label={`${formatNumber(impressions)} imp`} size="small" sx={{ backgroundImage: 'linear-gradient(135deg, #e2e8f0 0%, #f8fafc 100%)', color: '#0f172a', border: '1px solid #cbd5e1', boxShadow: '0 1px 2px rgba(0,0,0,0.05)', fontWeight: 700 }} />
                        </Tooltip>
                        <Tooltip title="Click-through rate. Higher indicates titles/meta attract clicks for given impressions.">
                          <Chip label={`${ctr.toFixed(1)}% CTR`} size="small" sx={{ backgroundImage: ctrBg, color: ctrColor, border: '1px solid rgba(0,0,0,0.06)', boxShadow: '0 1px 2px rgba(0,0,0,0.04)', fontWeight: 700 }} />
                        </Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexShrink: 0 }}>
                        <Tooltip title="Open page in new tab">
                          <IconButton
                            size="small"
                            onClick={() => onOpenPage(p.page)}
                            sx={{ color: '#4f46e5' }}
                          >
                            <OpenInNew fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Button size="small" variant="contained" sx={{ textTransform: 'none' }} onClick={() => onCreateBrief(p.page, p.queries || [])}>Create Brief</Button>
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

export default TopPagesInsightsPanel;
