import React from 'react';
import {
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Chip,
  IconButton,
  Tooltip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider
} from '@mui/material';
import {
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { type GSCSite } from '../../../api/gsc';
import type { GSCDataQualityResponse, GSCCachedOpportunitiesResponse } from '../../../api/gsc';

interface GSCPlatformCardProps {
  platform: {
    id: string;
    name: string;
    description: string;
    icon: React.ReactNode;
    status: string;
  };
  gscSites: GSCSite[] | null;
  isLoading: boolean;
  onConnect: (platformId: string) => void;
  getStatusIcon: (status: string) => React.ReactElement;
  getStatusText: (status: string) => string;
  getStatusColor: (status: string) => string;
  onRefresh?: () => void;
  primarySite: string;
  onPrimarySiteChange: (siteUrl: string) => void;
  dataQuality: GSCDataQualityResponse | null;
  opportunities: GSCCachedOpportunitiesResponse | null;
}

const GSCPlatformCard: React.FC<GSCPlatformCardProps> = ({
  platform,
  gscSites,
  isLoading,
  onConnect,
  getStatusIcon,
  getStatusText,
  getStatusColor,
  onRefresh,
  primarySite,
  onPrimarySiteChange,
  dataQuality,
  opportunities
}) => {
  const handleRefresh = () => {
    if (onRefresh) {
      onRefresh();
    }
  };

  return (
    <Card 
      sx={{
        height: '100%',
        border: '1px solid #e2e8f0',
        backgroundColor: '#ffffff',
        transition: 'all 0.2s ease',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          transform: 'translateY(-2px)'
        }
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        {/* Header */}
        <Box display="flex" alignItems="center" mb={2}>
          <Box sx={{ color: '#64748b', mr: 1 }}>
            {platform.icon}
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1e293b' }}>
              {platform.name}
            </Typography>
            <Typography variant="body2" sx={{ color: '#64748b', fontSize: '0.875rem' }}>
              {platform.description}
            </Typography>
          </Box>
          <Chip
            icon={getStatusIcon(platform.status)}
            label={getStatusText(platform.status)}
            color={getStatusColor(platform.status) as any}
            size="small"
          />
        </Box>

        {/* Connected Sites Display */}
        {platform.status === 'connected' && gscSites && gscSites.length > 0 && (
          <Box mb={2}>
            <Typography variant="body2" sx={{ fontWeight: 500, color: '#1e293b', mb: 1 }}>
              Connected Sites:
            </Typography>
            {gscSites.map((site, index) => (
              <Box
                key={index}
                sx={{
                  p: 1.5,
                  border: '1px solid #e2e8f0',
                  borderRadius: 1,
                  backgroundColor: '#f8fafc',
                  fontSize: '0.875rem',
                  color: '#475569',
                  fontFamily: 'monospace',
                  mb: 1
                }}
              >
                {site.siteUrl}
              </Box>
            ))}

            <FormControl fullWidth size="small" sx={{ mt: 1 }}>
              <InputLabel id="gsc-primary-site-label">Primary Site</InputLabel>
              <Select
                labelId="gsc-primary-site-label"
                value={primarySite || ''}
                label="Primary Site"
                onChange={(e) => onPrimarySiteChange(e.target.value)}
              >
                {gscSites.map((site) => (
                  <MenuItem key={site.siteUrl} value={site.siteUrl}>
                    {site.siteUrl}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Box>
        )}

        {dataQuality && (
          <Box mb={2}>
            <Alert severity={dataQuality.has_sufficient_permission ? 'success' : 'warning'} sx={{ mb: 1 }}>
              Permission: {dataQuality.permission_level || 'unknown'}
            </Alert>
            <Typography variant="caption" sx={{ color: '#475569', display: 'block' }}>
              Data window: {dataQuality.data_window_start || 'n/a'} → {dataQuality.data_window_end || 'n/a'} ({dataQuality.data_days_available} days)
            </Typography>
            <Typography variant="caption" sx={{ color: '#475569', display: 'block' }}>
              Indexing health: {dataQuality.indexing_health.indexed_urls}/{dataQuality.indexing_health.submitted_urls} indexed
              {typeof dataQuality.indexing_health.indexing_ratio === 'number' ? ` (${dataQuality.indexing_health.indexing_ratio}%)` : ''}
            </Typography>
          </Box>
        )}

        {opportunities && opportunities.opportunities.length > 0 && (
          <Box mb={2}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: '#1e293b', mb: 1 }}>
              Guided opportunities
            </Typography>
            <List dense sx={{ p: 0, border: '1px solid #e2e8f0', borderRadius: 1 }}>
              {opportunities.opportunities.slice(0, 3).map((op, idx) => (
                <React.Fragment key={op.query}>
                  <ListItem>
                    <ListItemText
                      primary={op.query}
                      secondary={`${op.impressions} impressions • ${op.ctr}% CTR • ${op.recommended_action}`}
                    />
                  </ListItem>
                  {idx < Math.min(opportunities.opportunities.length, 3) - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Box>
        )}

        {/* Features as Chips */}
        <Box mb={2} sx={{ minHeight: '32px' }}>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            <Chip 
              label="SEO analytics" 
              size="small" 
              variant="outlined" 
              sx={{ 
                color: '#475569',
                borderColor: '#e2e8f0',
                '&:hover': {
                  backgroundColor: '#f8fafc'
                }
              }} 
            />
            <Chip 
              label="Search performance" 
              size="small" 
              variant="outlined" 
              sx={{ 
                color: '#475569',
                borderColor: '#e2e8f0',
                '&:hover': {
                  backgroundColor: '#f8fafc'
                }
              }} 
            />
            <Chip 
              label="Content optimization" 
              size="small" 
              variant="outlined" 
              sx={{ 
                color: '#475569',
                borderColor: '#e2e8f0',
                '&:hover': {
                  backgroundColor: '#f8fafc'
                }
              }} 
            />
          </Box>
        </Box>

        {/* Actions */}
        <Box display="flex" gap={1}>
          {platform.status === 'connected' ? (
            <>
              <Button
                variant="outlined"
                size="small"
                onClick={() => onConnect(platform.id)}
                sx={{
                  textTransform: 'none',
                  fontWeight: 600,
                  borderColor: '#e2e8f0',
                  color: '#64748b',
                  flex: 1
                }}
              >
                Reconnect
              </Button>
              <Tooltip title="Refresh status">
                <IconButton 
                  onClick={handleRefresh} 
                  disabled={isLoading}
                  size="small"
                  sx={{ color: '#64748b' }}
                >
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </>
          ) : (
            <Button
              variant="contained"
              size="small"
              onClick={() => onConnect(platform.id)}
              disabled={isLoading}
              sx={{
                textTransform: 'none',
                fontWeight: 600,
                flex: 1
              }}
            >
              Connect GSC
            </Button>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default GSCPlatformCard;
