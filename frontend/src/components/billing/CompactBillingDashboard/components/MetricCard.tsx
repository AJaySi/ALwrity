import React from 'react';
import { Box, Tooltip } from '@mui/material';
import { motion } from 'framer-motion';
import { TerminalTypography } from '../../../SchedulerDashboard/terminalTheme';
import { terminalColors } from '../../../SchedulerDashboard/terminalTheme';
import { AnimatedNumber } from '../../../shared/AnimatedNumber';
import { MiniSparkline } from '../../../shared/MiniSparkline';

interface MetricCardProps {
  title: string;
  value: number;
  formatValue: (n: number) => string;
  decimals?: number;
  tooltip: React.ReactNode;
  sparklineData?: Array<{ date: string; value: number }>;
  sparklineColor?: string;
  sparklineFormatValue?: (n: number) => string;
  sparklineLabel?: string;
  gradientColors: {
    start: string;
    end: string;
    border: string;
    hoverBorder: string;
    topBar: string;
  };
  animationDelay?: number;
  terminalTheme?: boolean;
  TypographyComponent: typeof TerminalTypography | React.ComponentType<any>;
}

/**
 * MetricCard - Reusable metric card component for displaying key metrics
 */
export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  formatValue,
  decimals = 0,
  tooltip,
  sparklineData,
  sparklineColor,
  sparklineFormatValue,
  sparklineLabel,
  gradientColors,
  animationDelay = 0,
  terminalTheme = false,
  TypographyComponent
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: animationDelay, duration: 0.4, ease: "easeOut" }}
    >
      <Tooltip 
        title={tooltip}
        arrow
        placement="top"
      >
        <Box sx={{ 
          textAlign: 'center', 
          p: 2.5, 
          ...(terminalTheme ? {
            backgroundColor: terminalColors.backgroundLight,
            borderRadius: 3,
            border: `1px solid ${terminalColors.border}`,
            position: 'relative',
            overflow: 'hidden',
            cursor: 'help',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 0 15px ${terminalColors.border}40`,
              borderColor: terminalColors.secondary
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '3px',
              background: terminalColors.border,
              zIndex: 1
            }
          } : {
            background: `linear-gradient(135deg, ${gradientColors.start} 0%, ${gradientColors.end} 100%)`,
            borderRadius: 3,
            border: `1px solid ${gradientColors.border}`,
            position: 'relative',
            overflow: 'hidden',
            cursor: 'help',
            transition: 'all 0.3s ease',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 8px 25px ${gradientColors.start.replace('0.12', '0.2')}`,
              border: `1px solid ${gradientColors.hoverBorder}`
            },
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '3px',
              background: gradientColors.topBar,
              zIndex: 1
            }
          })
        }}>
          <TypographyComponent variant="h5" sx={{ 
            fontWeight: 800, 
            color: terminalTheme ? terminalColors.text : '#ffffff', 
            textShadow: terminalTheme ? 'none' : '0 2px 8px rgba(0,0,0,0.4)',
            mb: 0.5
          }}>
            <AnimatedNumber 
              value={value}
              format={formatValue}
              decimals={decimals}
            />
          </TypographyComponent>
          <TypographyComponent variant="body2" sx={{ 
            color: terminalTheme ? terminalColors.textSecondary : 'rgba(255,255,255,0.9)',
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: '0.5px',
            fontSize: '0.75rem'
          }}>
            {title}
          </TypographyComponent>
          {sparklineData && sparklineData.length > 0 && sparklineColor && (
            <MiniSparkline 
              data={sparklineData}
              color={sparklineColor}
              height={50}
              formatValue={sparklineFormatValue || formatValue}
              label={sparklineLabel || title}
            />
          )}
        </Box>
      </Tooltip>
    </motion.div>
  );
};
