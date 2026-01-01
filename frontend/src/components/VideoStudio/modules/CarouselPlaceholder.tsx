import React, { useEffect, useState, useRef } from 'react';
import { Box, Typography } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';

interface CarouselPlaceholderProps {
  examples: string[];
  interval?: number;
  onExampleChange?: (example: string, index: number) => void;
  paused?: boolean;
}

export const CarouselPlaceholder: React.FC<CarouselPlaceholderProps> = ({
  examples,
  interval = 4000,
  onExampleChange,
  paused = false,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (examples.length <= 1 || paused) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }

    intervalRef.current = setInterval(() => {
      setCurrentIndex(prev => {
        const next = (prev + 1) % examples.length;
        if (onExampleChange) {
          onExampleChange(examples[next], next);
        }
        return next;
      });
    }, interval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [examples.length, interval, onExampleChange, paused]);

  if (examples.length === 0) return null;

  return (
    <Box
      sx={{
        position: 'relative',
        minHeight: 24,
        display: 'flex',
        alignItems: 'center',
        width: '100%',
      }}
    >
      <AnimatePresence mode="wait">
        <motion.div
          key={currentIndex}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.3 }}
          style={{ width: '100%' }}
        >
          <Typography
            variant="body2"
            sx={{
              color: 'rgba(255,255,255,0.5)',
              fontStyle: 'italic',
              pointerEvents: 'none',
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {examples[currentIndex]}
          </Typography>
        </motion.div>
      </AnimatePresence>
      {examples.length > 1 && (
        <Box
          sx={{
            position: 'absolute',
            bottom: -24,
            right: 0,
            display: 'flex',
            gap: 0.5,
          }}
        >
          {examples.map((_, idx) => (
            <Box
              key={idx}
              sx={{
                width: 6,
                height: 6,
                borderRadius: '50%',
                background: idx === currentIndex ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.2)',
                transition: 'background 0.3s ease',
              }}
            />
          ))}
        </Box>
      )}
    </Box>
  );
};
