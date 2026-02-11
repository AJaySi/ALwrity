import React, { useEffect, useState } from 'react';
import { Box, Typography } from '@mui/material';
import { motion } from 'framer-motion';
import { DollarSign, TrendingUp, TrendingDown } from 'lucide-react';
import { AnimatedNumber } from '../shared/AnimatedNumber';
import { formatCurrency } from '../../services/billingService';

interface LiveCostCounterProps {
  currentCost: number;
  previousCost?: number;
  velocity?: number; // Daily spending rate
  terminalTheme?: boolean;
  terminalColors?: any;
  TypographyComponent?: React.ComponentType<any>;
}

/**
 * LiveCostCounter - Animated counter showing real-time cost accumulation
 * 
 * Features:
 * - Smooth number animation
 * - Velocity indicator (trending up/down)
 * - Pulse animation on cost increase
 * - Color changes based on velocity
 */
const LiveCostCounter: React.FC<LiveCostCounterProps> = ({
  currentCost,
  previousCost,
  velocity = 0,
  terminalTheme = false,
  terminalColors,
  TypographyComponent = Typography
}) => {
  const [hasIncreased, setHasIncreased] = useState(false);
  const [pulseKey, setPulseKey] = useState(0);

  // Detect cost increase
  useEffect(() => {
    if (previousCost !== undefined && currentCost > previousCost) {
      setHasIncreased(true);
      setPulseKey(prev => prev + 1);
      const timer = setTimeout(() => setHasIncreased(false), 1000);
      return () => clearTimeout(timer);
    }
  }, [currentCost, previousCost]);

  // Calculate velocity trend
  const isIncreasing = velocity > 0;
  const velocityPercent = Math.abs(velocity);

  // Color based on velocity
  const getColor = () => {
    if (terminalTheme) {
      if (velocityPercent > 20) return terminalColors?.error || '#ef4444';
      if (velocityPercent > 10) return terminalColors?.warning || '#f59e0b';
      return terminalColors?.success || '#22c55e';
    }
    if (velocityPercent > 20) return '#ef4444';
    if (velocityPercent > 10) return '#f59e0b';
    return '#22c55e';
  };

  return (
    <motion.div
      key={pulseKey}
      animate={hasIncreased ? {
        scale: [1, 1.05, 1],
      } : {}}
      transition={{ duration: 0.5 }}
    >
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
          ...(terminalTheme ? {
            backgroundColor: terminalColors?.backgroundLight,
            borderRadius: 3,
            border: `1px solid ${terminalColors?.border || 'rgba(255,255,255,0.1)'}`
          } : {
            background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(79, 70, 229, 0.1) 100%)',
            borderRadius: 3,
            border: '1px solid rgba(102, 126, 234, 0.3)'
          })
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
          <DollarSign 
            size={24} 
            color={terminalTheme ? (terminalColors?.text || '#ffffff') : '#667eea'} 
          />
          <TypographyComponent 
            variant="caption" 
            sx={{ 
              color: terminalTheme 
                ? (terminalColors?.textSecondary || 'rgba(255,255,255,0.7)')
                : 'rgba(255,255,255,0.7)',
              textTransform: 'uppercase',
              letterSpacing: '1px',
              fontSize: '0.7rem',
              fontWeight: 600
            }}
          >
            Live Cost
          </TypographyComponent>
        </Box>

        <TypographyComponent
          variant="h3"
          sx={{
            fontWeight: 800,
            color: getColor(),
            mb: 1,
            textShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.3)',
            display: 'flex',
            alignItems: 'baseline',
            gap: 0.5
          }}
        >
          <AnimatedNumber
            value={currentCost}
            format={formatCurrency}
            decimals={4}
            duration={0.8}
          />
        </TypographyComponent>

        {previousCost !== undefined && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {isIncreasing ? (
              <TrendingUp size={14} color={getColor()} />
            ) : (
              <TrendingDown size={14} color={getColor()} />
            )}
            <TypographyComponent
              variant="caption"
              sx={{
                color: getColor(),
                fontWeight: 600,
                fontSize: '0.75rem'
              }}
            >
              {isIncreasing ? '+' : ''}{velocityPercent.toFixed(1)}% daily rate
            </TypographyComponent>
          </Box>
        )}
      </Box>
    </motion.div>
  );
};

export default LiveCostCounter;
