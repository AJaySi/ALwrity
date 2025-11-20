import React from 'react';
import { Box, Skeleton, type BoxProps } from '@mui/material';
import { motion } from 'framer-motion';
import { shimmerVariants } from './motionPresets';

interface LoadingSkeletonProps extends BoxProps {
  lines?: number;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  lines = 3,
  sx,
  ...rest
}) => (
  <Box
    component={motion.div}
    variants={shimmerVariants}
    initial="initial"
    animate="animate"
    sx={{ width: '100%', ...sx }}
    {...rest}
  >
    {Array.from({ length: lines }).map((_, idx) => (
      <Skeleton
        key={idx}
        variant="rectangular"
        height={16}
        animation="wave"
        sx={{
          my: 1,
          borderRadius: 1,
          bgcolor: 'rgba(148,163,184,0.15)',
        }}
      />
    ))}
  </Box>
);

