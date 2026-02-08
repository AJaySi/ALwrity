import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Chip,
  Tooltip,
  Divider,
  LinearProgress,
} from '@mui/material';
import {
  Topic as TopicIcon,
  HealthAndSafety as HealthIcon,
  Update as UpdateIcon,
  Timeline as VelocityIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { GlassCard } from '../../shared/styled';

interface AdvertoolsInsightsProps {
  data: any;
}

export const AdvertoolsInsights: React.FC<AdvertoolsInsightsProps> = ({ data }) => {
  if (!data || (!data.augmented_themes?.length && !data.site_health?.total_urls)) {
    return null;
  }

  const { augmented_themes, site_health, last_audit, last_health_check, tasks, avg_word_count } = data;

  const getStatusDisplay = (taskType: string) => {
    const status = tasks?.[taskType];
    switch (status) {
      case 'running':
        return { label: 'Running...', color: 'secondary', icon: <UpdateIcon sx={{ fontSize: 14 }} /> };
      case 'failed':
        return { label: 'Failed', color: 'error', icon: <WarningIcon sx={{ fontSize: 14 }} /> };
      case 'pending':
        return { label: 'Scheduled', color: 'default', icon: <UpdateIcon sx={{ fontSize: 14 }} /> };
      default:
        return { label: 'Active', color: 'success', icon: null };
    }
  };

  const auditStatus = getStatusDisplay('content_audit');
  const healthStatus = getStatusDisplay('site_health');

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
          🚀 Data-Driven Content Intelligence (Advertools)
        </Typography>
        <Tooltip title="Deep insights extracted from your actual site content and structure.">
          <UpdateIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 18 }} />
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* Content Themes & Persona Augmentation */}
        <Grid item xs={12} md={6}>
          <GlassCard sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TopicIcon sx={{ color: '#8b5cf6' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>
                  Augmented Content Themes
                </Typography>
              </Box>
              <Chip 
                label={auditStatus.label} 
                size="small" 
                color={auditStatus.color as any} 
                variant="outlined" 
                icon={auditStatus.icon as any}
                sx={{ height: 20, fontSize: '0.65rem' }}
              />
            </Box>
            
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
              Actual themes discovered from your content crawl. These are used to refine your brand persona.
            </Typography>

            {augmented_themes && augmented_themes.length > 0 ? (
              <>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {augmented_themes.slice(0, 15).map((theme: any, idx: number) => (
                    <Tooltip key={idx} title={`Frequency: ${theme.abs_freq}`}>
                      <Chip
                        label={theme.word}
                        size="small"
                        sx={{
                          bgcolor: 'rgba(139, 92, 246, 0.1)',
                          color: '#a78bfa',
                          border: '1px solid rgba(139, 92, 246, 0.2)',
                          '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.2)' }
                        }}
                      />
                    </Tooltip>
                  ))}
                </Box>
                <Grid container spacing={1}>
                  {avg_word_count && (
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>
                          Avg. Content Length
                        </Typography>
                        <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>
                          {avg_word_count} words
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                  {site_health?.top_pillars && (
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>
                          Primary Structure
                        </Typography>
                        <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          /{Object.keys(site_health.top_pillars)[0] || 'root'}
                        </Typography>
                      </Box>
                    </Grid>
                  )}
                </Grid>
              </>
            ) : (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                  {tasks?.content_audit === 'running' ? 'Crawl in progress...' : (tasks?.content_audit === 'failed' ? 'Audit failed. Check sitemap.' : 'No themes discovered yet.')}
                </Typography>
                {tasks?.content_audit === 'running' && <LinearProgress sx={{ mt: 1, borderRadius: 1 }} color="secondary" />}
              </Box>
            )}
            
            {last_audit && (
              <Typography variant="caption" sx={{ display: 'block', mt: 2, color: 'rgba(255, 255, 255, 0.4)' }}>
                Last updated: {new Date(last_audit).toLocaleDateString()}
              </Typography>
            )}
          </GlassCard>
        </Grid>

        {/* Site Health & Freshness */}
        <Grid item xs={12} md={6}>
          <GlassCard sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HealthIcon sx={{ color: '#10b981' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>
                  Site Health & Freshness
                </Typography>
              </Box>
              <Chip 
                label={healthStatus.label} 
                size="small" 
                color={healthStatus.color as any} 
                variant="outlined" 
                icon={healthStatus.icon as any}
                sx={{ height: 20, fontSize: '0.65rem' }}
              />
            </Box>

            {site_health && site_health.total_urls ? (
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>
                      Total Pages
                    </Typography>
                    <Typography variant="h6" sx={{ color: 'white' }}>
                      {site_health.total_urls}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <VelocityIcon sx={{ fontSize: 14, color: '#3b82f6' }} />
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                        Publishing Velocity
                      </Typography>
                    </Box>
                    <Typography variant="h6" sx={{ color: 'white' }}>
                      {site_health.publishing_velocity} <Typography component="span" variant="caption">/ week</Typography>
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2, border: site_health.stale_content_percentage > 30 ? '1px solid rgba(239, 68, 68, 0.2)' : 'none' }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                          <WarningIcon sx={{ fontSize: 14, color: site_health.stale_content_percentage > 30 ? '#ef4444' : '#f59e0b' }} />
                          <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>
                            Stale Content (6+ months)
                          </Typography>
                        </Box>
                        <Typography variant="h6" sx={{ color: site_health.stale_content_percentage > 30 ? '#f87171' : 'white' }}>
                          {site_health.stale_content_count} pages ({site_health.stale_content_percentage}%)
                        </Typography>
                      </Box>
                      {site_health.stale_content_percentage > 30 && (
                        <Chip label="High Risk" size="small" color="error" variant="outlined" sx={{ height: 20, fontSize: '0.65rem' }} />
                      )}
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            ) : (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.5)' }}>
                  {tasks?.site_health === 'running' ? 'Analyzing sitemap...' : (tasks?.site_health === 'failed' ? 'Sitemap analysis failed.' : 'Sitemap analysis pending.')}
                </Typography>
                {tasks?.site_health === 'running' && <LinearProgress sx={{ mt: 1, borderRadius: 1 }} color="primary" />}
              </Box>
            )}

            {last_health_check && (
              <Typography variant="caption" sx={{ display: 'block', mt: 2, color: 'rgba(255, 255, 255, 0.4)' }}>
                Last checked: {new Date(last_health_check).toLocaleDateString()}
              </Typography>
            )}
          </GlassCard>
        </Grid>
      </Grid>
    </Box>
  );
};
