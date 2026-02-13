import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  LinearProgress,
  Alert,
  CircularProgress,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Visibility,
  MouseOutlined,
  Search,
  Web,
  Refresh,
  Info,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
} from '@mui/icons-material';
import { Button } from '@mui/material';
import { PlatformAnalytics as PlatformAnalyticsType, AnalyticsSummary, PlatformConnectionStatus } from '../../api/analytics';
import { cachedAnalyticsAPI } from '../../api/cachedAnalytics';
import BingInsightsCard from './BingInsightsCard';
import BackgroundJobManager from './BackgroundJobManager';

interface PlatformAnalyticsComponentProps {
  platforms?: string[];
  showSummary?: boolean;
  refreshInterval?: number; // in milliseconds, 0 = no auto-refresh
  onDataLoaded?: (data: any) => void;
  onRefreshReady?: (refreshFn: () => Promise<void>) => void; // Expose refresh function to parent
  onReconnect?: (platform: string) => void; // Reconnect handler for individual platforms
  showBackgroundJobs?: boolean; // Only render background jobs when user triggers
}

const PlatformAnalytics: React.FC<PlatformAnalyticsComponentProps> = ({
  platforms,
  showSummary = true,
  refreshInterval = 0,
  onDataLoaded,
  onRefreshReady,
  onReconnect,
  showBackgroundJobs = false,
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyticsData, setAnalyticsData] = useState<Record<string, PlatformAnalyticsType>>({});
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [, setPlatformStatus] = useState<Record<string, PlatformConnectionStatus>>({});
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load platform connection status
      const statusResponse = await cachedAnalyticsAPI.getPlatformStatus();
      setPlatformStatus(statusResponse.platforms);

      // Load analytics data
      const analyticsResponse = await cachedAnalyticsAPI.getAnalyticsData(platforms);
      setAnalyticsData(analyticsResponse.data as Record<string, PlatformAnalyticsType>);
      setSummary(analyticsResponse.summary);
      setLastUpdated(new Date());

      if (onDataLoaded) {
        onDataLoaded({
          analytics: analyticsResponse.data,
          summary: analyticsResponse.summary,
          status: statusResponse.platforms,
        });
      }
    } catch (err: unknown) {
      console.error('Error loading analytics data:', err);
      let errorMessage = 'Failed to load analytics data';
      if (err instanceof Error) {
        errorMessage = (err as Error).message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [platforms, onDataLoaded]);

  // Method to force refresh (bypass cache)
  const forceRefresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Clear cache and force fresh data
      await cachedAnalyticsAPI.forceRefreshAnalyticsData(platforms);
      
      // Reload data
      await loadData();
      
    } catch (err) {
      console.error('PlatformAnalytics: Force refresh failed:', err);
      setError(err instanceof Error ? err.message : 'Failed to refresh data');
    } finally {
      setLoading(false);
    }
  }, [platforms, loadData]);

  // One-run guard to prevent duplicate calls in StrictMode
  const dataLoadedRef = useRef(false);

  useEffect(() => {
    if (dataLoadedRef.current) return;
    dataLoadedRef.current = true;
    
    loadData();

    // Set up auto-refresh if interval is specified
    let interval: NodeJS.Timeout | null = null;
    if (refreshInterval > 0) {
      interval = setInterval(loadData, refreshInterval);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [platforms, refreshInterval, loadData]);

  // Expose refresh function to parent component
  useEffect(() => {
    if (onRefreshReady) {
      onRefreshReady(forceRefresh);
    }
  }, [onRefreshReady, forceRefresh]);

  const getPlatformIcon = (platform: string) => {
    switch (platform.toLowerCase()) {
      case 'gsc':
        return <Search color="primary" />;
      case 'wix':
        return <Web color="secondary" />;
      case 'wordpress':
        return <Web color="info" />;
      case 'bing':
        return <Search color="primary" />;
      default:
        return <Web />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'partial':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle color="success" fontSize="small" />;
      case 'error':
        return <ErrorIcon color="error" fontSize="small" />;
      case 'partial':
        return <Warning color="warning" fontSize="small" />;
      default:
        return <Info fontSize="small" />;
    }
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  const renderMetricsCard = (platform: string, data: PlatformAnalyticsType) => {
    const metrics = data.metrics;
    
    return (
      <Card key={platform} sx={{ height: '100%' }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getPlatformIcon(platform)}
              <Typography variant="h6" component="div">
                {platform.toUpperCase()}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              {getStatusIcon(data.status)}
              <Chip 
                label={data.status} 
                color={getStatusColor(data.status) as any}
                size="small"
              />
            </Box>
          </Box>

          {data.status === 'success' && (
            <>
              <Grid container spacing={2}>
                {metrics.total_clicks !== undefined && (
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <MouseOutlined color="primary" sx={{ fontSize: 32, mb: 1 }} />
                      <Typography variant="h4" color="primary">
                        {formatNumber(metrics.total_clicks)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Clicks
                      </Typography>
                    </Box>
                  </Grid>
                )}
                
                {metrics.total_impressions !== undefined && (
                  <Grid item xs={6}>
                    <Box sx={{ textAlign: 'center' }}>
                      <Visibility color="secondary" sx={{ fontSize: 32, mb: 1 }} />
                      <Typography variant="h4" color="secondary">
                        {formatNumber(metrics.total_impressions)}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Impressions
                      </Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>

              {metrics.avg_ctr !== undefined && (
                <Box sx={{ mt: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">CTR</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {metrics.avg_ctr}%
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.min(metrics.avg_ctr * 10, 100)} 
                    sx={{ height: 8, borderRadius: 4 }}
                  />
                </Box>
              )}

              {metrics.avg_position !== undefined && (
                <Box sx={{ mt: 1 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Avg Position</Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {metrics.avg_position.toFixed(1)}
                    </Typography>
                  </Box>
                  <LinearProgress 
                    variant="determinate" 
                    value={Math.max(0, 100 - (metrics.avg_position - 1) * 5)} 
                    color="secondary"
                    sx={{ height: 6, borderRadius: 4 }}
                  />
                </Box>
              )}

              {metrics.top_queries && metrics.top_queries.length > 0 && (
                <Box sx={{ mt: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Top Queries
                  </Typography>
                  <List dense>
                    {metrics.top_queries.slice(0, 3).map((query, index) => (
                      <ListItem key={index} sx={{ px: 0 }}>
                        <ListItemIcon sx={{ minWidth: 32 }}>
                          <Typography variant="caption" color="text.secondary">
                            {index + 1}
                          </Typography>
                        </ListItemIcon>
                        <ListItemText
                          primary={query.query}
                          secondary={`${query.clicks} clicks • ${query.ctr.toFixed(1)}% CTR`}
                          primaryTypographyProps={{ variant: 'body2' }}
                          secondaryTypographyProps={{ variant: 'caption' }}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </>
          )}

          {data.status === 'error' && (
            <Box sx={{ mt: 1 }}>
              <Alert severity="error" sx={{ mb: 2 }}>
                {data.error_message || 'Failed to load analytics data'}
              </Alert>
              {onReconnect && (
                <Button
                  variant="outlined"
                  color="error"
                  size="small"
                  onClick={() => onReconnect(platform)}
                  sx={{ 
                    textTransform: 'none',
                    fontWeight: 600,
                    borderColor: '#f44336',
                    color: '#f44336',
                    '&:hover': {
                      borderColor: '#d32f2f',
                      backgroundColor: 'rgba(244, 67, 54, 0.04)'
                    }
                  }}
                >
                  Reconnect {platform.toUpperCase()}
                </Button>
              )}
            </Box>
          )}

          {data.status === 'partial' && (
            <Alert severity="warning" sx={{ mt: 1 }}>
              {data.error_message || 'Limited analytics data available'}
            </Alert>
          )}

          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1 }}>
            Last updated: {data.last_updated ? new Date(data.last_updated).toLocaleString() : 'Never'}
          </Typography>
        </CardContent>
      </Card>
    );
  };

  const renderSummaryCard = () => {
    if (!summary) return null;

    return (
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              Analytics Summary
            </Typography>
            <IconButton onClick={forceRefresh} disabled={loading} title="Force refresh (bypass cache)">
              <Refresh />
            </IconButton>
          </Box>

          <Grid container spacing={3}>
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="primary">
                  {summary.connected_platforms}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Connected Platforms
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="secondary">
                  {formatNumber(summary.total_clicks)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Clicks
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="info">
                  {formatNumber(summary.total_impressions)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Impressions
                </Typography>
              </Box>
            </Grid>
            
            <Grid item xs={6} sm={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" color="success">
                  {summary.overall_ctr}%
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Overall CTR
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {lastUpdated && (
            <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2, textAlign: 'center' }}>
              Last refreshed: {lastUpdated.toLocaleString()}
            </Typography>
          )}
        </CardContent>
      </Card>
    );
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 200 }}>
        <CircularProgress />
        <Typography variant="body2" sx={{ ml: 2 }}>
          Loading analytics data...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      {showSummary && renderSummaryCard()}
      
      <Grid container spacing={3}>
        {Object.entries(analyticsData)
          .filter(([platform]) => platform.toLowerCase() !== 'wordpress') // Exclude WordPress analytics
          .map(([platform, data]) => (
            <Grid item xs={12} sm={6} lg={4} key={platform}>
              {renderMetricsCard(platform, data)}
            </Grid>
          ))}
      </Grid>

      {/* Background Job Manager - render only when explicitly enabled */}
      {showBackgroundJobs && (
        <Box sx={{ mt: 3 }}>
          <BackgroundJobManager
            siteUrl="https://www.alwrity.com/"
            days={30}
            onJobCompleted={(job) => {
              console.log('🎉 Background job completed:', job);
              // Refresh analytics data when job completes
              forceRefresh();
            }}
          />
        </Box>
      )}

      {/* Debug Section - Show data structure for all platforms */}
      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Debug: Platform Data Structures
        </Typography>
        {Object.entries(analyticsData).map(([platform, data]) => (
          <Box key={platform} sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              {platform.toUpperCase()} Data:
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ 
              fontFamily: 'monospace', 
              fontSize: '0.75rem',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-all',
              maxHeight: '200px',
              overflow: 'auto',
              border: '1px solid #e0e0e0',
              padding: '8px',
              borderRadius: '4px',
              backgroundColor: '#f5f5f5'
            }}>
              {JSON.stringify(data, null, 2)}
            </Typography>
          </Box>
        ))}
      </Box>

      {/* Bing Insights Card - Show when Bing is connected */}
      {analyticsData.bing && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Debug: Bing data structure: {JSON.stringify(analyticsData.bing, null, 2)}
          </Typography>
          {analyticsData.bing.metrics?.connection_status === 'connected' && (
            <BingInsightsCard
              siteUrl={
                analyticsData.bing.metrics?.sites?.[0]?.Url ||
                analyticsData.bing.metrics?.sites?.[0]?.url ||
                'https://www.alwrity.com/'
              }
              days={30}
              insights={analyticsData.bing.metrics?.insights}
              loading={loading}
              error={error}
              onInsightsLoaded={(insights) => {
                console.log('Bing insights loaded:', insights);
              }}
            />
          )}
        </Box>
      )}

      {Object.keys(analyticsData).length === 0 && (
        <Alert severity="info">
          No analytics data available. Connect your platforms to see analytics insights.
        </Alert>
      )}
    </Box>
  );
};

export default PlatformAnalytics;
