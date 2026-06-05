import React from 'react';
import {
  Box,
  Grid,
  Typography,
  Chip,
  Tooltip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableRow,
} from '@mui/material';
import {
  Topic as TopicIcon,
  HealthAndSafety as HealthIcon,
  Update as UpdateIcon,
  Timeline as VelocityIcon,
  Warning as WarningIcon,
  Link as LinkIcon,
  AltRoute as RedirectIcon,
  Image as ImageIcon,
  Language as UrlIcon,
  Dns as RobotsIcon,
  AccountTree as BudgetIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp as TrendUpIcon,
  TrendingDown as TrendDownIcon,
  TrendingFlat as TrendFlatIcon,
} from '@mui/icons-material';
import { GlassCard } from '../../shared/styled';

interface AdvertoolsInsightsProps {
  data: any;
}

const SeverityChip: React.FC<{ severity: string }> = ({ severity }) => {
  const config: Record<string, { color: any; icon: any }> = {
    critical: { color: 'error', icon: <ErrorIcon sx={{ fontSize: 14 }} /> },
    warning: { color: 'warning', icon: <WarningIcon sx={{ fontSize: 14 }} /> },
    info: { color: 'info', icon: <InfoIcon sx={{ fontSize: 14 }} /> },
  };
  const c = config[severity] || config.info;
  return (
    <Chip
      label={severity}
      size="small"
      color={c.color}
      icon={c.icon as any}
      sx={{ height: 20, fontSize: '0.65rem', textTransform: 'capitalize' }}
    />
  );
};

const TrendBadge: React.FC<{ trend: string }> = ({ trend }) => {
  if (trend === 'increasing') return <TrendUpIcon sx={{ fontSize: 16, color: '#10b981' }} />;
  if (trend === 'decreasing') return <TrendDownIcon sx={{ fontSize: 16, color: '#ef4444' }} />;
  return <TrendFlatIcon sx={{ fontSize: 16, color: '#f59e0b' }} />;
};

const ScoreBar: React.FC<{ value: number; label: string; max?: number }> = ({ value, label, max = 100 }) => {
  const pct = Math.min((value / max) * 100, 100);
  const color = pct >= 80 ? '#10b981' : pct >= 50 ? '#f59e0b' : '#ef4444';
  return (
    <Box sx={{ mb: 1.5 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>{label}</Typography>
        <Typography variant="caption" sx={{ color: 'white', fontWeight: 600 }}>{value}</Typography>
      </Box>
      <LinearProgress
        variant="determinate"
        value={pct}
        sx={{
          height: 6,
          borderRadius: 3,
          bgcolor: 'rgba(255,255,255,0.06)',
          '& .MuiLinearProgress-bar': { bgcolor: color, borderRadius: 3 },
        }}
      />
    </Box>
  );
};

export const AdvertoolsInsights: React.FC<AdvertoolsInsightsProps> = ({ data }) => {
  if (!data || (!data.augmented_themes?.length && !data.site_health?.total_urls && !data.freshness?.freshness_score && !data.link_health?.total_links_found)) {
    return null;
  }

  const { augmented_themes, site_health, last_audit, last_health_check, tasks, avg_word_count,
    freshness, link_health, redirect_audit, image_seo, url_structure, page_status,
    robots_txt, crawl_budget } = data;

  const getStatusDisplay = (taskType: string) => {
    const status = tasks?.[taskType];
    switch (status) {
      case 'running':
        return { label: 'Running...', color: 'secondary' as const, icon: <UpdateIcon sx={{ fontSize: 14 }} /> };
      case 'failed':
        return { label: 'Failed', color: 'error' as const, icon: <WarningIcon sx={{ fontSize: 14 }} /> };
      case 'pending':
        return { label: 'Scheduled', color: 'default' as const, icon: <UpdateIcon sx={{ fontSize: 14 }} /> };
      default:
        return { label: 'Active', color: 'success' as const, icon: null };
    }
  };

  const auditStatus = getStatusDisplay('content_audit');
  const healthStatus = getStatusDisplay('site_health');

  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
          Data-Driven Content Intelligence (Advertools)
        </Typography>
        <Tooltip title="Deep insights extracted from your actual site content and structure.">
          <InfoIcon sx={{ color: 'rgba(255, 255, 255, 0.5)', fontSize: 18 }} />
        </Tooltip>
      </Box>

      <Grid container spacing={3}>
        {/* 1. Content Themes & Persona Augmentation */}
        <Grid item xs={12} md={6}>
          <GlassCard sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TopicIcon sx={{ color: '#8b5cf6' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>
                  Augmented Content Themes
                </Typography>
              </Box>
              <Chip label={auditStatus.label} size="small" color={auditStatus.color} variant="outlined" icon={auditStatus.icon as any} sx={{ height: 20, fontSize: '0.65rem' }} />
            </Box>
            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
              Actual themes discovered from your content crawl.
            </Typography>
            {augmented_themes && augmented_themes.length > 0 ? (
              <>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {augmented_themes.slice(0, 15).map((theme: any, idx: number) => (
                    <Tooltip key={idx} title={`Frequency: ${theme.abs_freq}`}>
                      <Chip label={theme.word} size="small" sx={{ bgcolor: 'rgba(139, 92, 246, 0.1)', color: '#a78bfa', border: '1px solid rgba(139, 92, 246, 0.2)', '&:hover': { bgcolor: 'rgba(139, 92, 246, 0.2)' } }} />
                    </Tooltip>
                  ))}
                </Box>
                <Grid container spacing={1}>
                  {avg_word_count && (
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Avg. Content Length</Typography>
                        <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{avg_word_count} words</Typography>
                      </Box>
                    </Grid>
                  )}
                  {site_health?.top_pillars && (
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Primary Structure</Typography>
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

        {/* 2. Site Health & Freshness */}
        <Grid item xs={12} md={6}>
          <GlassCard sx={{ p: 3, height: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <HealthIcon sx={{ color: '#10b981' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Site Health & Freshness</Typography>
              </Box>
              <Chip label={healthStatus.label} size="small" color={healthStatus.color} variant="outlined" icon={healthStatus.icon as any} sx={{ height: 20, fontSize: '0.65rem' }} />
            </Box>

            {site_health && site_health.total_urls ? (
              <>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Total Pages</Typography>
                      <Typography variant="h6" sx={{ color: 'white' }}>{site_health.total_urls}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <VelocityIcon sx={{ fontSize: 14, color: '#3b82f6' }} />
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Velocity</Typography>
                      </Box>
                      <Typography variant="h6" sx={{ color: 'white' }}>
                        {site_health.publishing_velocity} <Typography component="span" variant="caption">/ wk</Typography>
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <TrendBadge trend={site_health.publishing_trend || freshness?.publishing_trend} />
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Trend</Typography>
                      </Box>
                      <Typography variant="h6" sx={{ color: 'white', textTransform: 'capitalize' }}>
                        {site_health.publishing_trend || freshness?.publishing_trend || 'unknown'}
                      </Typography>
                    </Box>
                  </Grid>
                </Grid>

                {/* Freshness Score */}
                {(freshness?.freshness_score || site_health?.freshness_score) && (
                  <Box sx={{ mt: 2 }}>
                    <ScoreBar value={freshness?.freshness_score ?? site_health?.freshness_score} label="Content Freshness Score" />
                  </Box>
                )}

                {/* Stale Content */}
                <Box sx={{ mt: 1.5, p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2, border: (site_health.stale_content_percentage || 0) > 30 ? '1px solid rgba(239, 68, 68, 0.2)' : 'none' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <WarningIcon sx={{ fontSize: 14, color: (site_health.stale_content_percentage || 0) > 30 ? '#ef4444' : '#f59e0b' }} />
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)' }}>Stale Content (6+ months)</Typography>
                      </Box>
                      <Typography variant="h6" sx={{ color: (site_health.stale_content_percentage || 0) > 30 ? '#f87171' : 'white' }}>
                        {site_health.stale_content_count} pages ({site_health.stale_content_percentage}%)
                      </Typography>
                    </Box>
                    {(site_health.stale_content_percentage || 0) > 30 && (
                      <Chip label="High Risk" size="small" color="error" variant="outlined" sx={{ height: 20, fontSize: '0.65rem' }} />
                    )}
                  </Box>
                </Box>

                {/* Publishing Recency */}
                {freshness?.publishing_recency && (
                  <Box sx={{ mt: 1.5, p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 1 }}>Publishing Recency</Typography>
                    <Grid container spacing={1}>
                      {Object.entries(freshness.publishing_recency).map(([period, count]) => (
                        <Grid item xs={3} key={period}>
                          <Box sx={{ textAlign: 'center' }}>
                            <Typography variant="subtitle2" sx={{ color: 'white', fontWeight: 600 }}>{count as number}</Typography>
                            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.4)' }}>{period.replace('last_', '').replace('d', 'd')}</Typography>
                          </Box>
                        </Grid>
                      ))}
                    </Grid>
                  </Box>
                )}
              </>
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

        {/* 3. URL Structure Analysis */}
        {url_structure && url_structure.total_urls_analyzed > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <UrlIcon sx={{ color: '#3b82f6' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>URL Structure Analysis</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>URLs Analyzed</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{url_structure.total_urls_analyzed}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Avg Depth</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{url_structure.directory_depth?.average_depth || 0}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Max Depth</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{url_structure.directory_depth?.max_depth || 0}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>URLs with Parameters</Typography>
                    <Typography variant="subtitle1" sx={{ color: url_structure.parameter_usage?.percentage_with_params > 20 ? '#f87171' : 'white', fontWeight: 600 }}>
                      {url_structure.parameter_usage?.percentage_with_params || 0}%
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Subdomains</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{url_structure.subdomains?.unique_count || 0}</Typography>
                  </Box>
                </Grid>
              </Grid>
              {url_structure.directory_depth?.distribution && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Depth Distribution</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Object.entries(url_structure.directory_depth.distribution).slice(0, 8).map(([depth, count]) => (
                      <Tooltip key={depth} title={`Depth ${depth}: ${count} pages`}>
                        <Chip label={`L${depth}: ${count as number}`} size="small" sx={{ bgcolor: 'rgba(59, 130, 246, 0.1)', color: '#93c5fd', border: '1px solid rgba(59, 130, 246, 0.2)', fontSize: '0.65rem' }} />
                      </Tooltip>
                    ))}
                  </Box>
                </Box>
              )}
            </GlassCard>
          </Grid>
        )}

        {/* 4. Link Health */}
        {link_health && link_health.total_links_found > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <LinkIcon sx={{ color: '#10b981' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Internal Link Health</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Total Links</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{link_health.total_links_found}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Internal</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{link_health.internal_link_count} ({link_health.internal_link_percentage}%)</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>External</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{link_health.external_link_count}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Nofollow</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{link_health.nofollow_link_count}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={6}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Avg Links/Page</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{link_health.avg_links_per_page}</Typography>
                  </Box>
                </Grid>
              </Grid>
              {link_health.top_anchor_words && Object.keys(link_health.top_anchor_words).length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Top Anchor Text</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Object.entries(link_health.top_anchor_words).slice(0, 10).map(([word, count]) => (
                      <Chip key={word} label={`${word} (${count})`} size="small" sx={{ bgcolor: 'rgba(16, 185, 129, 0.1)', color: '#6ee7b7', border: '1px solid rgba(16, 185, 129, 0.2)', fontSize: '0.65rem' }} />
                    ))}
                  </Box>
                </Box>
              )}
            </GlassCard>
          </Grid>
        )}

        {/* 5. Redirect Audit */}
        {redirect_audit && redirect_audit.total_redirects > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <RedirectIcon sx={{ color: '#f59e0b' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Redirect Audit</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Total Redirects</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{redirect_audit.total_redirects}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Unique Chains</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{redirect_audit.unique_chains}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Multi-Hop</Typography>
                    <Typography variant="subtitle1" sx={{ color: redirect_audit.multi_hop_chains > 0 ? '#f87171' : 'white', fontWeight: 600 }}>{redirect_audit.multi_hop_chains}</Typography>
                  </Box>
                </Grid>
              </Grid>
              {redirect_audit.status_distribution && Object.keys(redirect_audit.status_distribution).length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Status Distribution</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Object.entries(redirect_audit.status_distribution).map(([code, count]) => (
                      <Chip key={code} label={`${code}: ${count}`} size="small" sx={{ bgcolor: 'rgba(245, 158, 11, 0.1)', color: '#fcd34d', border: '1px solid rgba(245, 158, 11, 0.2)', fontSize: '0.65rem' }} />
                    ))}
                  </Box>
                </Box>
              )}
            </GlassCard>
          </Grid>
        )}

        {/* 6. Image SEO */}
        {image_seo && image_seo.total_images > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ImageIcon sx={{ color: '#8b5cf6' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Image SEO</Typography>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Total Images</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{image_seo.total_images}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Missing Alt</Typography>
                    <Typography variant="subtitle1" sx={{ color: (image_seo.missing_alt_count || 0) > 0 ? '#f87171' : 'white', fontWeight: 600 }}>{image_seo.missing_alt_count || 0}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Alt Coverage</Typography>
                    <Typography variant="subtitle1" sx={{ color: (image_seo.alt_coverage_percentage || 0) >= 80 ? '#10b981' : '#f59e0b', fontWeight: 600 }}>
                      {image_seo.alt_coverage_percentage || 0}%
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              <Box sx={{ mt: 1 }}>
                <ScoreBar value={image_seo.alt_coverage_percentage || 0} label="Alt Text Coverage" />
              </Box>
            </GlassCard>
          </Grid>
        )}

        {/* 7. Robots.txt Compliance */}
        {robots_txt && robots_txt.success && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <RobotsIcon sx={{ color: '#6366f1' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Robots.txt Compliance</Typography>
              </Box>
              <ScoreBar value={robots_txt.compliance_score || 0} label="Compliance Score" />
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Directives</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{robots_txt.total_directives}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Sitemap</Typography>
                    <Typography variant="subtitle1" sx={{ color: robots_txt.has_sitemap_directive ? '#10b981' : '#f87171', fontWeight: 600 }}>
                      {robots_txt.has_sitemap_directive ? 'Declared' : 'Missing'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Crawl-Delay</Typography>
                    <Typography variant="subtitle1" sx={{ color: robots_txt.has_crawl_delay ? '#10b981' : 'rgba(255,255,255,0.5)', fontWeight: 600 }}>
                      {robots_txt.has_crawl_delay ? 'Set' : 'Not set'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              {robots_txt.issues && robots_txt.issues.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Issues</Typography>
                  {robots_txt.issues.map((issue: any, idx: number) => (
                    <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <SeverityChip severity={issue.severity} />
                      <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>{issue.detail}</Typography>
                    </Box>
                  ))}
                </Box>
              )}
              {robots_txt.user_agents_found && robots_txt.user_agents_found.length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>User Agents</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {robots_txt.user_agents_found.map((ua: string, idx: number) => (
                      <Chip key={idx} label={ua} size="small" sx={{ bgcolor: 'rgba(99, 102, 241, 0.1)', color: '#a5b4fc', border: '1px solid rgba(99, 102, 241, 0.2)', fontSize: '0.65rem' }} />
                    ))}
                  </Box>
                </Box>
              )}
            </GlassCard>
          </Grid>
        )}

        {/* 8. Crawl Budget Analysis */}
        {crawl_budget && crawl_budget.success && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <BudgetIcon sx={{ color: '#f59e0b' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Crawl Budget Analysis</Typography>
              </Box>
              <ScoreBar value={crawl_budget.optimization_score || 0} label="Optimization Score" />
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Sitemap URLs</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{crawl_budget.sitemap_total_urls}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Pages Crawled</Typography>
                    <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 600 }}>{crawl_budget.pages_crawled}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={4}>
                  <Box sx={{ p: 1.5, bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 }}>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block' }}>Wasted</Typography>
                    <Typography variant="subtitle1" sx={{ color: (crawl_budget.waste_percentage || 0) > 20 ? '#f87171' : 'white', fontWeight: 600 }}>
                      {crawl_budget.waste_percentage || 0}%
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
              {crawl_budget.depth_distribution && Object.keys(crawl_budget.depth_distribution).length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Crawl Depth Distribution</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Object.entries(crawl_budget.depth_distribution).slice(0, 6).map(([depth, count]) => (
                      <Chip key={depth} label={`Depth ${depth}: ${count}`} size="small" sx={{ bgcolor: 'rgba(245, 158, 11, 0.1)', color: '#fcd34d', border: '1px solid rgba(245, 158, 11, 0.2)', fontSize: '0.65rem' }} />
                    ))}
                  </Box>
                </Box>
              )}
              {crawl_budget.status_distribution && Object.keys(crawl_budget.status_distribution).length > 0 && (
                <Box sx={{ mt: 1.5 }}>
                  <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.5)', display: 'block', mb: 0.5 }}>Status Distribution</Typography>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {Object.entries(crawl_budget.status_distribution).slice(0, 6).map(([code, count]) => (
                      <Chip key={code} label={`${code}: ${count}`} size="small" sx={{
                        bgcolor: code.startsWith('2') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        color: code.startsWith('2') ? '#6ee7b7' : '#fca5a5',
                        border: `1px solid ${code.startsWith('2') ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                        fontSize: '0.65rem',
                      }} />
                    ))}
                  </Box>
                </Box>
              )}
            </GlassCard>
          </Grid>
        )}

        {/* 9. Page Status Overview (from site structure) */}
        {page_status && Object.keys(page_status).length > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <CheckIcon sx={{ color: '#10b981' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Page Status Distribution</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                {Object.entries(page_status).map(([code, count]) => (
                  <Chip key={code} label={`HTTP ${code}: ${count}`} size="small" sx={{
                    bgcolor: code.startsWith('2') ? 'rgba(16, 185, 129, 0.1)' : code.startsWith('3') ? 'rgba(59, 130, 246, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                    color: code.startsWith('2') ? '#6ee7b7' : code.startsWith('3') ? '#93c5fd' : '#fca5a5',
                    border: `1px solid ${code.startsWith('2') ? 'rgba(16, 185, 129, 0.2)' : code.startsWith('3') ? 'rgba(59, 130, 246, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`,
                    fontSize: '0.7rem',
                  }} />
                ))}
              </Box>
            </GlassCard>
          </Grid>
        )}

        {/* 10. Sitemap URLs (from robots.txt) */}
        {robots_txt?.sitemap_urls && robots_txt.sitemap_urls.length > 0 && (
          <Grid item xs={12} md={6}>
            <GlassCard sx={{ p: 3, height: '100%' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <UrlIcon sx={{ color: '#6366f1' }} />
                <Typography variant="subtitle1" sx={{ color: 'white', fontWeight: 700 }}>Sitemaps Found</Typography>
              </Box>
              <Table size="small">
                <TableBody>
                  {robots_txt.sitemap_urls.map((url: string, idx: number) => (
                    <TableRow key={idx} sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' } }}>
                      <TableCell sx={{ borderBottom: '1px solid rgba(255,255,255,0.05)', py: 0.75 }}>
                        <Typography variant="caption" sx={{ color: '#a5b4fc', wordBreak: 'break-all', fontFamily: 'monospace', fontSize: '0.65rem' }}>
                          {url}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </GlassCard>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};