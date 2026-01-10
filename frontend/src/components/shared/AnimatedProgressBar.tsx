import React from 'react';
import { Box, LinearProgress, Typography } from '@mui/material';
import { motion } from 'framer-motion';

interface AnimatedProgressBarProps {
  value: number; // 0-100
  maxValue?: number; // Optional max value for display
  label?: string;
  color?: string;
  height?: number;
  showLabel?: boolean;
  showPercentage?: boolean;
  variant?: 'determinate' | 'indeterminate' | 'buffer' | 'query';
}

/**
 * AnimatedProgressBar - Progress bar with smooth fill animation
 * 
 * Usage:
 *   <AnimatedProgressBar value={75} label="Usage" showPercentage />
 *   <AnimatedProgressBar value={50} color="#4ade80" height={8} />
 */
export const AnimatedProgressBar: React.FC<AnimatedProgressBarProps> = ({
  value,
  maxValue,
  label,
  color,
  height = 8,
  showLabel = false,
  showPercentage = false,
  variant = 'determinate'
}) => {
  // Clamp value between 0 and 100
  const clampedValue = Math.min(Math.max(value, 0), 100);
  
  // Get color based on value if not provided
  const getColor = () => {
    if (color) return color;
    if (clampedValue >= 90) return '#ef4444'; // Red
    if (clampedValue >= 75) return '#f59e0b'; // Orange
    if (clampedValue >= 50) return '#eab308'; // Yellow
    return '#22c55e'; // Green
  };

  const displayValue = maxValue 
    ? `${Math.round(clampedValue)} / ${maxValue}`
    : `${Math.round(clampedValue)}%`;

  return (
    <Box sx={{ width: '100%' }}>
      {(showLabel || showPercentage) && (
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          {showLabel && label && (
            <Typography variant="caption" sx={{ fontSize: '0.75rem', opacity: 0.8 }}>
              {label}
            </Typography>
          )}
          {showPercentage && (
            <Typography variant="caption" sx={{ fontSize: '0.75rem', fontWeight: 'bold' }}>
              {displayValue}
            </Typography>
          )}
        </Box>
      )}
      <Box sx={{ position: 'relative', width: '100%', height }}>
        <LinearProgress
          variant={variant}
          value={clampedValue}
          sx={{
            height,
            borderRadius: height / 2,
            backgroundColor: 'rgba(255,255,255,0.1)',
            '& .MuiLinearProgress-bar': {
              borderRadius: height / 2,
              backgroundColor: getColor(),
            }
          }}
        />
        {/* Animated overlay for smoother animation */}
        <motion.div
          initial={{ scaleX: 0 }}
          animate={{ scaleX: clampedValue / 100 }}
          transition={{ 
            duration: 1,
            ease: "easeOut",
            delay: 0.2
          }}
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            height: '100%',
            width: '100%',
            transformOrigin: 'left',
            backgroundColor: getColor(),
            borderRadius: height / 2,
            opacity: 0.3,
            pointerEvents: 'none'
          }}
        />
      </Box>
    </Box>
  );
};

export default AnimatedProgressBar;
