import React from 'react';
import { Paper, PaperProps } from '@mui/material';
import { motion } from 'framer-motion';
import { cardLiftVariants } from './motionPresets';

export interface GlassyCardProps extends PaperProps {
  animateOnMount?: boolean;
}

export const GlassyCard: React.FC<GlassyCardProps> = ({
  children,
  animateOnMount = true,
  sx,
  ...rest
}) => (
  <Paper
    component={motion.div}
    variants={cardLiftVariants}
    initial={animateOnMount ? 'hidden' : false}
    animate={animateOnMount ? 'visible' : false}
    whileHover="hover"
    elevation={0}
    sx={{
      borderRadius: 4,
      border: '1px solid rgba(255,255,255,0.08)',
      background: 'rgba(15,23,42,0.72)',
      backdropFilter: 'blur(24px)',
      ...sx,
    }}
    {...rest}
  >
    {children}
  </Paper>
);

