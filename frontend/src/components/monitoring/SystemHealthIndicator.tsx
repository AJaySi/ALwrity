import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  Activity, 
  RefreshCw,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Zap
} from 'lucide-react';

// Types
import { SystemHealth } from '../../types/monitoring';

// Utils
import { 
  getHealthStatusColor,
  getHealthStatusIcon,
  formatResponseTime,
  formatErrorRate,
  getPerformanceStatus
} from '../../services/monitoringService';

interface SystemHealthIndicatorProps {
  systemHealth: SystemHealth | null;
  onRefresh: () => void;
}

const SystemHealthIndicator: React.FC<SystemHealthIndicatorProps> = ({ 
  systemHealth, 
  onRefresh 
}) => {
  if (!systemHealth) {
    return (
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        <Typography sx={{ color: 'rgba(255,255,255,0.8)' }}>Loading system health...</Typography>
      </Card>
    );
  }

  const performanceStatus = getPerformanceStatus(0, systemHealth.error_rate);
  const healthColor = getHealthStatusColor(systemHealth.status);
  const healthIcon = getHealthStatusIcon(systemHealth.status);

  const getStatusChip = () => {
    let chipColor: 'default' | 'primary' | 'secondary' | 'error' | 'info' | 'success' | 'warning' = 'default';
    if (systemHealth.status === 'healthy') chipColor = 'success';
    else if (systemHealth.status === 'warning') chipColor = 'warning';
    else if (systemHealth.status === 'critical') chipColor = 'error';

    return (
      <Chip
        icon={<span>{healthIcon}</span>}
        label={systemHealth.status.charAt(0).toUpperCase() + systemHealth.status.slice(1)}
        color={chipColor}
        size="small"
        sx={{ fontWeight: 'bold' }}
      />
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 'bold' }}>
              <Activity size={20} />
              System Health
            </Typography>
            <Tooltip title="Refresh data">
              <IconButton 
                size="small" 
                onClick={onRefresh}
                sx={{ 
                  color: 'text.secondary',
                  '&:hover': { color: 'primary.main' }
                }}
              >
                <RefreshCw size={16} />
              </IconButton>
            </Tooltip>
          </Box>

          {/* Status Chip */}
          <Box sx={{ mb: 3 }}>
            {getStatusChip()}
          </Box>
        </CardContent>

        <CardContent sx={{ pt: 0 }}>
          {/* Main Health Indicator */}
          <Box sx={{ mb: 3, textAlign: 'center' }}>
            <motion.div
              initial={{ scale: 0.8 }}
              animate={{ scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <Box
                sx={{
                  width: 80,
                  height: 80,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${healthColor}20 0%, ${healthColor}10 100%)`,
                  border: `3px solid ${healthColor}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 16px',
                  position: 'relative'
                }}
              >
                <Typography variant="h4" sx={{ color: healthColor }}>
                  {healthIcon}
                </Typography>
                
                {/* Pulse animation for critical status */}
                {systemHealth.status === 'critical' && (
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                    style={{
                      position: 'absolute',
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      border: `2px solid ${healthColor}`,
                      opacity: 0.3
                    }}
                  />
                )}
              </Box>
              
              <Typography variant="h6" sx={{ fontWeight: 'bold', color: healthColor }}>
                {systemHealth.status.charAt(0).toUpperCase() + systemHealth.status.slice(1)}
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)' }}>
                System Status
              </Typography>
            </motion.div>
          </Box>

          {/* Metrics */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                Recent Requests
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                {systemHealth.recent_requests.toLocaleString()}
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                Recent Errors
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 'bold',
                  color: systemHealth.recent_errors > 0 ? '#ff6b6b' : '#ffffff'
                }}
              >
                {systemHealth.recent_errors}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                Error Rate
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  fontWeight: 'bold',
                  color: systemHealth.error_rate > 5 ? '#ff6b6b' : '#ffffff'
                }}
              >
                {formatErrorRate(systemHealth.error_rate)}
              </Typography>
            </Box>
          </Box>

          {/* Error Rate Progress */}
          <Box sx={{ mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Error Rate
              </Typography>
              <Typography variant="body2" fontWeight="bold">
                {formatErrorRate(systemHealth.error_rate)}
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(systemHealth.error_rate, 100)}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'rgba(255,255,255,0.1)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: systemHealth.error_rate > 10 ? '#ef4444' : 
                                 systemHealth.error_rate > 5 ? '#f59e0b' : '#22c55e',
                  borderRadius: 4,
                }
              }}
            />
            <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
              {systemHealth.error_rate > 10 ? 'High error rate detected' : 
               systemHealth.error_rate > 5 ? 'Moderate error rate' : 'Normal error rate'}
            </Typography>
          </Box>

          {/* Performance Indicators */}
          <Box 
            sx={{ 
              p: 2, 
              backgroundColor: 'rgba(255,255,255,0.05)',
              borderRadius: 2,
              border: '1px solid rgba(255,255,255,0.1)'
            }}
          >
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              Performance Status
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <span style={{ color: performanceStatus.color }}>
                {performanceStatus.icon}
              </span>
              <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                {performanceStatus.status.charAt(0).toUpperCase() + performanceStatus.status.slice(1)}
              </Typography>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Last updated: {new Date(systemHealth.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>

          {/* Quick Actions */}
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-around' }}>
            <Tooltip title="View detailed logs">
              <Box sx={{ textAlign: 'center', cursor: 'pointer' }}>
                <Clock size={20} color={healthColor} />
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                  Logs
                </Typography>
              </Box>
            </Tooltip>
            <Tooltip title="Performance metrics">
              <Box sx={{ textAlign: 'center', cursor: 'pointer' }}>
                <Zap size={20} color={healthColor} />
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                  Metrics
                </Typography>
              </Box>
            </Tooltip>
          </Box>
        </CardContent>

        {/* Decorative Elements */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 100,
            height: 100,
            background: `radial-gradient(circle, ${healthColor}10 0%, transparent 70%)`,
            borderRadius: '50%',
            pointerEvents: 'none'
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 60,
            height: 60,
            background: `radial-gradient(circle, ${healthColor}05 0%, transparent 70%)`,
            borderRadius: '50%',
            pointerEvents: 'none'
          }}
        />
      </Card>
    </motion.div>
  );
};

export default SystemHealthIndicator;
