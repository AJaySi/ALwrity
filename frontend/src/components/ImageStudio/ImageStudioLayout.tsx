import React from 'react';
import { Box } from '@mui/material';
import { motion } from 'framer-motion';
import type { Variants } from 'framer-motion';

import DashboardHeader from '../shared/DashboardHeader';
import type { DashboardHeaderProps } from '../shared/types';

const MotionBox = motion(Box);

const sparkleVariants: Variants = {
  initial: { scale: 0, rotate: 0 },
  animate: {
    scale: [0, 1, 0],
    rotate: [0, 180, 360],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut',
    },
  },
};

interface ImageStudioLayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  headerProps?: DashboardHeaderProps;
}

const defaultHeaderProps: DashboardHeaderProps = {
  title: 'AI Image Studio',
  subtitle:
    'One hub for every visual workflow: generate, edit, upscale, transform, optimize, and manage assets built for content and marketing teams.',
};

export const ImageStudioLayout: React.FC<ImageStudioLayoutProps> = ({
  children,
  showHeader = true,
  headerProps,
}) => {
  const mergedHeaderProps = {
    ...defaultHeaderProps,
    ...headerProps,
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
        py: 4,
        px: 2,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'fixed',
          inset: 0,
          pointerEvents: 'none',
          zIndex: 0,
        }}
      >
        {[...Array(20)].map((_, i) => (
          <MotionBox
            key={i}
            variants={sparkleVariants}
            initial="initial"
            animate="animate"
            transition={{ delay: i * 0.1 }}
            sx={{
              position: 'absolute',
              width: 4,
              height: 4,
              borderRadius: '50%',
              background: 'rgba(255, 255, 255, 0.6)',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </Box>

      <Box
        sx={{
          maxWidth: 1400,
          mx: 'auto',
          position: 'relative',
          zIndex: 1,
        }}
      >
        {showHeader && (
          <Box sx={{ mb: 3 }}>
            <DashboardHeader {...mergedHeaderProps} />
          </Box>
        )}
        {children}
      </Box>
    </Box>
  );
};

