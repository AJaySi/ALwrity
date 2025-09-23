import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  Collapse,
  Alert,
} from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  AlertTriangle, 
  Info, 
  XCircle,
  ChevronDown,
  ChevronUp,
  Bell,
  BellOff,
  CheckCircle
} from 'lucide-react';

// Types
import { UsageAlert } from '../../types/billing';

interface UsageAlertsProps {
  alerts: UsageAlert[];
  onMarkRead: (alertId: number) => Promise<void>;
}

const UsageAlerts: React.FC<UsageAlertsProps> = ({ 
  alerts, 
  onMarkRead 
}) => {
  const [expanded, setExpanded] = useState(false);
  const [processing, setProcessing] = useState<number | null>(null);

  // Separate alerts by read status
  const unreadAlerts = alerts.filter(alert => !alert.is_read);
  const readAlerts = alerts.filter(alert => alert.is_read);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <XCircle size={16} color="#ef4444" />;
      case 'warning':
        return <AlertTriangle size={16} color="#f59e0b" />;
      case 'info':
        return <Info size={16} color="#3b82f6" />;
      default:
        return <Info size={16} color="#6b7280" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return '#ef4444';
      case 'warning':
        return '#f59e0b';
      case 'info':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const handleMarkAsRead = async (alertId: number) => {
    try {
      setProcessing(alertId);
      await onMarkRead(alertId);
    } catch (error) {
      console.error('Error marking alert as read:', error);
    } finally {
      setProcessing(null);
    }
  };

  const formatAlertTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const renderAlertItem = (alert: UsageAlert, index: number) => (
    <motion.div
      key={alert.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <ListItem
        sx={{
          backgroundColor: alert.is_read ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.05)',
          borderRadius: 2,
          mb: 1,
          border: `1px solid ${getSeverityColor(alert.severity)}20`,
          position: 'relative',
          '&:hover': {
            backgroundColor: 'rgba(255,255,255,0.08)',
          }
        }}
      >
        <ListItemIcon sx={{ minWidth: 40 }}>
          {getSeverityIcon(alert.severity)}
        </ListItemIcon>
        
        <ListItemText
          primary={
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 'bold', flex: 1 }}>
                {alert.title}
              </Typography>
              {!alert.is_read && (
                <Chip
                  label="New"
                  size="small"
                  sx={{
                    backgroundColor: '#ef4444',
                    color: 'white',
                    fontSize: '0.7rem',
                    height: 20
                  }}
                />
              )}
            </Box>
          }
          secondary={
            <Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {alert.message}
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Typography variant="caption" color="text.secondary">
                  {formatAlertTime(alert.created_at)}
                </Typography>
                {alert.provider && (
                  <Chip
                    label={alert.provider}
                    size="small"
                    variant="outlined"
                    sx={{ fontSize: '0.7rem', height: 20 }}
                  />
                )}
                <Chip
                  label={`${alert.threshold_percentage}% threshold`}
                  size="small"
                  variant="outlined"
                  sx={{ fontSize: '0.7rem', height: 20 }}
                />
              </Box>
            </Box>
          }
        />
        
        {!alert.is_read && (
          <Tooltip title="Mark as read">
            <IconButton
              size="small"
              onClick={() => handleMarkAsRead(alert.id)}
              disabled={processing === alert.id}
              sx={{
                color: getSeverityColor(alert.severity),
                '&:hover': {
                  backgroundColor: `${getSeverityColor(alert.severity)}20`
                }
              }}
            >
              {processing === alert.id ? (
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                >
                  <CheckCircle size={16} />
                </motion.div>
              ) : (
                <CheckCircle size={16} />
              )}
            </IconButton>
          </Tooltip>
        )}
      </ListItem>
    </motion.div>
  );

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
              <Bell size={20} />
              Usage Alerts
            </Typography>
            {unreadAlerts.length > 0 && (
              <Chip
                label={unreadAlerts.length}
                size="small"
                sx={{
                  backgroundColor: '#ef4444',
                  color: 'white',
                  fontWeight: 'bold'
                }}
              />
            )}
          </Box>
        </CardContent>

        <CardContent sx={{ pt: 0 }}>
          {/* No alerts state */}
          {alerts.length === 0 && (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <BellOff size={48} color="#6b7280" />
              <Typography variant="body2" sx={{ mt: 2, color: 'rgba(255,255,255,0.8)' }}>
                No alerts at this time
              </Typography>
              <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                You'll be notified when usage thresholds are reached
              </Typography>
            </Box>
          )}

          {/* Unread alerts */}
          {unreadAlerts.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 'bold', color: 'error.main' }}>
                Unread Alerts ({unreadAlerts.length})
              </Typography>
              <List sx={{ p: 0 }}>
                <AnimatePresence>
                  {unreadAlerts.slice(0, 3).map((alert, index) => renderAlertItem(alert, index))}
                </AnimatePresence>
              </List>
            </Box>
          )}

          {/* Read alerts (collapsible) */}
          {readAlerts.length > 0 && (
            <Box>
              <Box 
                sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1, 
                  cursor: 'pointer',
                  p: 1,
                  borderRadius: 1,
                  '&:hover': { backgroundColor: 'rgba(255,255,255,0.05)' }
                }}
                onClick={() => setExpanded(!expanded)}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: 'text.secondary' }}>
                  Read Alerts ({readAlerts.length})
                </Typography>
                {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </Box>
              
              <Collapse in={expanded}>
                <List sx={{ p: 0, mt: 1 }}>
                  <AnimatePresence>
                    {readAlerts.map((alert, index) => renderAlertItem(alert, index))}
                  </AnimatePresence>
                </List>
              </Collapse>
            </Box>
          )}

          {/* Alert summary */}
          {alerts.length > 0 && (
            <Box 
              sx={{ 
                mt: 3,
                p: 2, 
                backgroundColor: 'rgba(255,255,255,0.05)',
                borderRadius: 2,
                border: '1px solid rgba(255,255,255,0.1)'
              }}
            >
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                Alert Summary
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {['error', 'warning', 'info'].map(severity => {
                  const count = alerts.filter(alert => alert.severity === severity).length;
                  if (count === 0) return null;
                  
                  return (
                    <Chip
                      key={severity}
                      label={`${count} ${severity}`}
                      size="small"
                      sx={{
                        backgroundColor: `${getSeverityColor(severity)}20`,
                        color: getSeverityColor(severity),
                        fontSize: '0.7rem',
                        height: 24
                      }}
                    />
                  );
                })}
              </Box>
            </Box>
          )}
        </CardContent>

        {/* Decorative Elements */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 100,
            height: 100,
            background: 'radial-gradient(circle, rgba(239, 68, 68, 0.1) 0%, transparent 70%)',
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
            background: 'radial-gradient(circle, rgba(245, 158, 11, 0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}
        />
      </Card>
    </motion.div>
  );
};

export default UsageAlerts;
