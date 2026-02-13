/**
 * Priority 2 Alert Banner Component
 * 
 * Displays Priority 2 alerts (cost trends, pricing changes, OSS recommendations)
 * in a prominent banner format for the main dashboard.
 */

import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  IconButton,
  Collapse,
  Chip,
} from '@mui/material';
import {
  AlertTriangle,
  Info,
  XCircle,
  TrendingUp,
  DollarSign,
  X,
  Lightbulb,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Priority2Alert } from '../../hooks/usePriority2Alerts';

interface Priority2AlertBannerProps {
  alerts: Priority2Alert[];
  onDismiss: (alertId: string) => void;
  maxAlerts?: number;
}

const Priority2AlertBanner: React.FC<Priority2AlertBannerProps> = ({
  alerts,
  onDismiss,
  maxAlerts = 3
}) => {
  const [expanded] = React.useState(true);
  const [dismissedIds, setDismissedIds] = React.useState<Set<string>>(new Set());

  // Filter out dismissed alerts
  const visibleAlerts = alerts.filter(alert => !dismissedIds.has(alert.id));
  const displayAlerts = visibleAlerts.slice(0, maxAlerts);
  const remainingCount = visibleAlerts.length - maxAlerts;

  const getSeverityIcon = (severity: string, type: string) => {
    if (type === 'cost_trend') return <TrendingUp size={20} />;
    if (type === 'oss_recommendation') return <Lightbulb size={20} />;
    if (type === 'pricing_change') return <DollarSign size={20} />;
    
    switch (severity) {
      case 'error':
        return <XCircle size={20} />;
      case 'warning':
        return <AlertTriangle size={20} />;
      default:
        return <Info size={20} />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
    }
  };

  const handleDismiss = (alertId: string) => {
    setDismissedIds(prev => new Set([...prev, alertId]));
    onDismiss(alertId);
  };

  if (displayAlerts.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <AnimatePresence>
        {displayAlerts.map((alert, index) => (
          <motion.div
            key={alert.id}
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Alert
              severity={getSeverityColor(alert.severity)}
              icon={getSeverityIcon(alert.severity, alert.type)}
              action={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  {alert.action && (
                    <Button
                      size="small"
                      onClick={alert.action.onClick}
                      sx={{ textTransform: 'none' }}
                    >
                      {alert.action.label}
                    </Button>
                  )}
                  {alert.dismissible && (
                    <IconButton
                      size="small"
                      onClick={() => handleDismiss(alert.id)}
                      sx={{ ml: 1 }}
                    >
                      <X size={16} />
                    </IconButton>
                  )}
                </Box>
              }
              sx={{
                mb: 2,
                '& .MuiAlert-icon': {
                  alignItems: 'center'
                }
              }}
            >
              <AlertTitle sx={{ fontWeight: 'bold', mb: 0.5 }}>
                {alert.title}
              </AlertTitle>
              {alert.message}
              {alert.type && (
                <Chip
                  label={alert.type.replace('_', ' ')}
                  size="small"
                  sx={{ mt: 1, ml: 1 }}
                />
              )}
            </Alert>
          </motion.div>
        ))}
      </AnimatePresence>

      {remainingCount > 0 && (
        <Collapse in={expanded}>
          <Alert severity="info" sx={{ mt: 1 }}>
            <AlertTitle>
              {remainingCount} more alert{remainingCount > 1 ? 's' : ''} available
            </AlertTitle>
            View all alerts in the{' '}
            <Button
              size="small"
              onClick={() => window.location.href = '/billing'}
              sx={{ textTransform: 'none' }}
            >
              Billing Dashboard
            </Button>
          </Alert>
        </Collapse>
      )}
    </Box>
  );
};

export default Priority2AlertBanner;
