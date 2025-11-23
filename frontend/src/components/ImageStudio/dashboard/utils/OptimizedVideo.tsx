import React, { useState, useRef, useEffect } from 'react';
import { Box, Skeleton } from '@mui/material';

interface OptimizedVideoProps {
  src: string;
  poster?: string;
  alt?: string;
  sx?: any;
  controls?: boolean;
  preload?: 'none' | 'metadata' | 'auto';
  muted?: boolean;
  loop?: boolean;
  playsInline?: boolean;
}

export const OptimizedVideo: React.FC<OptimizedVideoProps> = ({
  src,
  poster,
  alt,
  sx = {},
  controls = true,
  preload = 'metadata',
  muted = false,
  loop = false,
  playsInline = true,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(false);
  const [hasError, setHasError] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Less aggressive: load when element is visible or about to be visible
    const observer = new IntersectionObserver(
      entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.01, // Trigger as soon as any part is visible
      }
    );

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, []);

  const handleLoadedData = () => {
    setIsLoaded(true);
  };

  const handleCanPlay = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoaded(true);
  };

  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        width: '100%',
        overflow: 'hidden',
        ...sx,
      }}
    >
      {!isLoaded && !hasError && (
        <Skeleton
          variant="rectangular"
          width="100%"
          height="100%"
          sx={{
            position: 'absolute',
            inset: 0,
            bgcolor: 'rgba(15,23,42,0.5)',
            borderRadius: sx.borderRadius || 0,
            zIndex: 1,
          }}
        />
      )}
      {/* Always render video element, but use lazy loading attribute */}
      <Box
        component="video"
        ref={videoRef}
        src={isInView ? src : undefined}
        poster={poster}
        controls={controls}
        preload={isInView ? preload : 'none'}
        muted={muted}
        loop={loop}
        playsInline={playsInline}
        onLoadedData={handleLoadedData}
        onCanPlay={handleCanPlay}
        onError={handleError}
        sx={{
          width: '100%',
          height: '100%',
          display: 'block',
          position: 'relative',
          zIndex: 2,
          opacity: isLoaded ? 1 : poster ? 0.7 : 0,
          transition: 'opacity 0.3s ease-in-out',
          ...sx,
        }}
      />
      {hasError && (
        <Box
          sx={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            bgcolor: 'rgba(15,23,42,0.8)',
            color: 'rgba(255,255,255,0.5)',
            fontSize: '0.875rem',
            zIndex: 3,
          }}
        >
          Failed to load video
        </Box>
      )}
    </Box>
  );
};

