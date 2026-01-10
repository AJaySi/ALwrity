import React, { Suspense, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Tooltip as MuiTooltip,
} from '@mui/material';
import { motion } from 'framer-motion';
import { Calendar } from 'lucide-react';
import { formatCurrency } from '../../services/billingService';
import { UsageLog } from '../../types/billing';

interface DailyCostHeatmapProps {
  usageLogs: UsageLog[];
  currentMonth: number;
  currentYear: number;
}

/**
 * DailyCostHeatmap - Calendar-style heatmap showing cost patterns by day
 * 
 * Visualizes daily spending patterns to identify high-cost days
 */
const DailyCostHeatmap: React.FC<DailyCostHeatmapProps> = ({ 
  usageLogs,
  currentMonth,
  currentYear
}) => {
  // Aggregate logs by day
  const dailyCosts = useMemo(() => {
    const costs: Record<number, number> = {};
    
    usageLogs.forEach(log => {
      const logDate = new Date(log.timestamp);
      if (logDate.getMonth() === currentMonth && logDate.getFullYear() === currentYear) {
        const day = logDate.getDate();
        costs[day] = (costs[day] || 0) + (log.cost_total || 0);
      }
    });
    
    return costs;
  }, [usageLogs, currentMonth, currentYear]);

  // Get days in month
  const daysInMonth = useMemo(() => {
    return new Date(currentYear, currentMonth + 1, 0).getDate();
  }, [currentMonth, currentYear]);

  // Calculate max cost for color scaling
  const maxCost = useMemo(() => {
    return Math.max(...Object.values(dailyCosts), 0.01);
  }, [dailyCosts]);

  // Get color intensity based on cost
  const getColorIntensity = (cost: number) => {
    if (cost === 0) return 'rgba(255,255,255,0.05)';
    const intensity = Math.min(cost / maxCost, 1);
    // Green (low) to Red (high)
    if (intensity < 0.3) {
      return `rgba(34, 197, 94, ${0.3 + intensity * 0.4})`; // Green
    } else if (intensity < 0.7) {
      return `rgba(234, 179, 8, ${0.5 + (intensity - 0.3) * 0.3})`; // Yellow
    } else {
      return `rgba(239, 68, 68, ${0.6 + (intensity - 0.7) * 0.4})`; // Red
    }
  };

  // Generate calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const days: Array<{ day: number; cost: number; date: Date | null }> = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      days.push({ day: 0, cost: 0, date: null });
    }
    
    // Add days of month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(currentYear, currentMonth, day);
      days.push({
        day,
        cost: dailyCosts[day] || 0,
        date
      });
    }
    
    return days;
  }, [currentMonth, currentYear, daysInMonth, dailyCosts]);

  if (usageLogs.length === 0) {
    return null;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
        }}
      >
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Calendar size={20} color="#4ade80" />
            <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
              Daily Cost Heatmap
            </Typography>
          </Box>

          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)', mb: 1 }}>
              Cost intensity by day of month
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', fontSize: '0.75rem' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 12, height: 12, backgroundColor: 'rgba(34, 197, 94, 0.5)', borderRadius: 1 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>Low</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 12, height: 12, backgroundColor: 'rgba(234, 179, 8, 0.7)', borderRadius: 1 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>Medium</Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                <Box sx={{ width: 12, height: 12, backgroundColor: 'rgba(239, 68, 68, 0.8)', borderRadius: 1 }} />
                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>High</Typography>
              </Box>
            </Box>
          </Box>

          <Box 
            sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(7, 1fr)', 
              gap: 1,
              mb: 1
            }}
          >
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <Typography 
                key={day}
                variant="caption" 
                sx={{ 
                  textAlign: 'center', 
                  color: 'rgba(255,255,255,0.6)',
                  fontWeight: 600,
                  fontSize: '0.7rem'
                }}
              >
                {day}
              </Typography>
            ))}
          </Box>

          <Box 
            sx={{ 
              display: 'grid', 
              gridTemplateColumns: 'repeat(7, 1fr)', 
              gap: 1
            }}
          >
            {calendarDays.map((item, index) => (
              <MuiTooltip
                key={index}
                title={
                  item.date ? (
                    <Box>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                        {item.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                      </Typography>
                      <Typography variant="body2">
                        Cost: {formatCurrency(item.cost)}
                      </Typography>
                    </Box>
                  ) : (
                    'No data'
                  )
                }
                arrow
                placement="top"
              >
                <Box
                  sx={{
                    aspectRatio: '1',
                    backgroundColor: getColorIntensity(item.cost),
                    borderRadius: 1,
                    border: item.cost > 0 ? '1px solid rgba(255,255,255,0.2)' : '1px solid rgba(255,255,255,0.05)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: item.date ? 'pointer' : 'default',
                    transition: 'all 0.2s ease',
                    '&:hover': item.date ? {
                      transform: 'scale(1.1)',
                      zIndex: 1,
                      boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
                    } : {},
                    position: 'relative'
                  }}
                >
                  {item.day > 0 && (
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        color: item.cost > maxCost * 0.5 ? '#ffffff' : 'rgba(255,255,255,0.8)',
                        fontSize: '0.65rem',
                        fontWeight: item.cost > 0 ? 600 : 400
                      }}
                    >
                      {item.day}
                    </Typography>
                  )}
                </Box>
              </MuiTooltip>
            ))}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DailyCostHeatmap;
