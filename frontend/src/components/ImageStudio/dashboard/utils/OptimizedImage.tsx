import React, { useState, useRef, useEffect } from 'react';
import { Box, Skeleton } from '@mui/material';

interface OptimizedImageProps {
  src: string;
  alt: string;
  sx?: any;
  loading?: 'lazy' | 'eager';
  placeholder?: 'blur' | 'empty';
  sizes?: string;
  width?: number | string;
  height?: number | string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  sx = {},
  loading = 'lazy',
  placeholder = 'blur',
  sizes,
  width,
  height,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [isInView, setIsInView] = useState(loading === 'eager');
  const [hasError, setHasError] = useState(false);
  const imgRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (loading === 'eager') {
      setIsInView(true);
      return;
    }

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
        threshold: 0.01,
      }
    );

    if (imgRef.current) {
      observer.observe(imgRef.current);
    }

    return () => {
      observer.disconnect();
    };
  }, [loading]);

  const handleLoad = () => {
    setIsLoaded(true);
  };

  const handleError = () => {
    setHasError(true);
    setIsLoaded(true);
  };

  // Extract clip-path and other advanced CSS from sx to apply to wrapper
  const {
    clipPath,
    gridArea,
    '--progress': progress,
    ...imgSx
  } = sx || {};

  return (
    <Box
      ref={imgRef}
      sx={{
        position: 'relative',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        clipPath,
        gridArea,
        '--progress': progress,
        ...(clipPath ? {} : sx),
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
            borderRadius: imgSx.borderRadius || 0,
          }}
        />
      )}
      {isInView && (
        <Box
          component="img"
          src={src}
          alt={alt}
          onLoad={handleLoad}
          onError={handleError}
          loading={loading}
          sizes={sizes}
          width={width}
          height={height}
          sx={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            opacity: isLoaded ? 1 : 0,
            transition: 'opacity 0.3s ease-in-out',
            ...imgSx,
          }}
        />
      )}
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
          }}
        >
          Failed to load image
        </Box>
      )}
    </Box>
  );
};

