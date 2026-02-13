import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
} from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';
import { motion, AnimatePresence } from 'framer-motion';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../api/client';
import { aiApiClient } from '../../../api/client';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';
import { MultimediaSection } from '../components/MultimediaSection';

const MotionBox = motion.create(Box);

// Define cubic bezier easing arrays as const to preserve tuple types
const easeInOut = [0.22, 0.61, 0.36, 1] as const;
const easeOut = [0.4, 0, 1, 1] as const;

const leftPageVariants = {
  enter: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? -20 : 20,
    x: direction === 0 ? 0 : direction > 0 ? -80 : 80,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: 'center',
  }),
  center: {
    rotateY: 0,
    x: 0,
    opacity: 1,
    transformOrigin: 'center',
    transition: { duration: 0.55, ease: easeInOut },
  },
  exit: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? 15 : -15,
    x: direction === 0 ? 0 : direction > 0 ? 60 : -60,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: 'center',
    transition: { duration: 0.4, ease: easeOut },
  }),
};

const rightPageVariants = {
  enter: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? 25 : -25,
    x: direction === 0 ? 0 : direction > 0 ? 110 : -110,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: direction >= 0 ? 'right center' : 'left center',
  }),
  center: {
    rotateY: 0,
    x: 0,
    opacity: 1,
    transformOrigin: 'center',
    transition: { duration: 0.55, ease: easeInOut },
  },
  exit: (direction: number) => ({
    rotateY: direction === 0 ? 0 : direction > 0 ? -25 : 25,
    x: direction === 0 ? 0 : direction > 0 ? -90 : 90,
    opacity: direction === 0 ? 1 : 0,
    transformOrigin: direction >= 0 ? 'left center' : 'right center',
    transition: { duration: 0.4, ease: easeOut },
  }),
};

interface StoryWritingProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

// Helper function to check if story is short
const isShortStory = (storyLength: string | null | undefined): boolean => {
  if (!storyLength) return false;
  const storyLengthLower = storyLength.toLowerCase();
  return storyLengthLower.includes('short') || storyLengthLower.includes('1000');
};

// Split story content into sections based on the number of scenes
const splitStoryContent = (content: string, numSections: number): string[] => {
  if (!content || numSections <= 1) {
    return [content || ''];
  }

  // Split by paragraphs (double newlines)
  const paragraphs = content.split(/\n\s*\n/).filter(p => p.trim().length > 0);
  
  if (paragraphs.length === 0) {
    return [content];
  }

  // If we have fewer paragraphs than sections, use paragraphs as sections
  if (paragraphs.length <= numSections) {
    // Pad with empty sections if needed
    const sections = [...paragraphs];
    while (sections.length < numSections) {
      sections.push('');
    }
    return sections;
  }

  // Divide paragraphs into roughly equal sections
  const sections: string[] = [];
  const paragraphsPerSection = Math.ceil(paragraphs.length / numSections);

  for (let i = 0; i < numSections; i++) {
    const start = i * paragraphsPerSection;
    const end = Math.min(start + paragraphsPerSection, paragraphs.length);
    sections.push(paragraphs.slice(start, end).join('\n\n'));
  }

  return sections;
};

const StoryWriting: React.FC<StoryWritingProps> = ({ state, onNext }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isContinuing, setIsContinuing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentPageIndex, setCurrentPageIndex] = useState(0);
  const [pageDirection, setPageDirection] = useState(0);
  const [imageLoadError, setImageLoadError] = useState<Set<number>>(new Set());
  const [imageBlobUrls, setImageBlobUrls] = useState<Map<number, string>>(new Map());
  const [videoBlobUrls, setVideoBlobUrls] = useState<Map<number, string>>(new Map());
  const [videoLoadError, setVideoLoadError] = useState<Set<number>>(new Set());

  // Get scenes and images from state
  const scenes = state.outlineScenes || [];
  const sceneImages = state.sceneImages || new Map<number, string>();
  const sceneAnimatedVideos = state.sceneAnimatedVideos || new Map<number, string>();
  const hasScenes = state.isOutlineStructured && scenes.length > 0;
  
  // Split story content into sections mapped to scenes
  const storySections = useMemo(() => {
    if (!state.storyContent) {
      return [];
    }
    
    if (hasScenes && scenes.length > 0) {
      // Split story content into sections based on number of scenes
      return splitStoryContent(state.storyContent, scenes.length);
    }
    
    // If no scenes, treat entire story as one section
    return [state.storyContent];
  }, [state.storyContent, hasScenes, scenes.length]);

  const numPages = Math.max(storySections.length, hasScenes ? scenes.length : 1);
  const currentPage = currentPageIndex < storySections.length ? storySections[currentPageIndex] : '';
  const currentSceneIndex = hasScenes ? Math.min(currentPageIndex, scenes.length - 1) : 0;
  const currentScene = hasScenes ? scenes[currentSceneIndex] : null;
  const canGoPrev = currentPageIndex > 0;
  const canGoNext = currentPageIndex < numPages - 1;

  // Get the current scene's image URL
  const currentSceneNumber = currentScene?.scene_number || currentSceneIndex + 1;
  const currentSceneImageUrl = sceneImages.get(currentSceneNumber);
  const hasImageLoadError = imageLoadError.has(currentSceneNumber);

  // Fetch image as blob with authentication
  useEffect(() => {
    if (!currentSceneImageUrl || hasImageLoadError || imageBlobUrls.has(currentSceneNumber)) {
      return;
    }
    
    const loadImage = async () => {
      try {
        // Use relative URL path directly (aiApiClient will add base URL and auth)
        const imageUrl = currentSceneImageUrl.startsWith('/') 
          ? currentSceneImageUrl 
          : `/${currentSceneImageUrl}`;
        // Use aiApiClient to get authenticated response with blob
        const response = await aiApiClient.get(imageUrl, {
          responseType: 'blob',
        });
        
        const blob = response.data;
        const blobUrl = URL.createObjectURL(blob);
        
        setImageBlobUrls((prev) => {
          const next = new Map(prev);
          next.set(currentSceneNumber, blobUrl);
          return next;
        });
      } catch (err) {
        console.error('Failed to load image:', err);
        setImageLoadError((prev) => new Set(prev).add(currentSceneNumber));
      }
    };
    
    loadImage();
  }, [currentSceneNumber, currentSceneImageUrl, hasImageLoadError, imageBlobUrls]);

  // Cleanup blob URLs when component unmounts
  const imageBlobUrlsRef = React.useRef(imageBlobUrls);
  useEffect(() => {
    imageBlobUrlsRef.current = imageBlobUrls;
  }, [imageBlobUrls]);

  useEffect(() => {
    return () => {
      // Revoke all blob URLs on unmount using the ref
      imageBlobUrlsRef.current.forEach((blobUrl) => {
        URL.revokeObjectURL(blobUrl);
      });
    };
  }, []);

  const currentSceneImageFullUrl = imageBlobUrls.get(currentSceneNumber) || null;
  const currentSceneAnimatedVideoUrl = sceneAnimatedVideos.get(currentSceneNumber) || null;
  const currentSceneAnimatedVideoBlobUrl = videoBlobUrls.get(currentSceneNumber) || null;
  const hasVideoLoadError = videoLoadError.has(currentSceneNumber);
  const showAnimatedVideo = Boolean(currentSceneAnimatedVideoBlobUrl);

  // Reset image load error when page changes
  useEffect(() => {
    setImageLoadError((prev) => {
      const next = new Set(prev);
      next.delete(currentSceneNumber);
      return next;
    });
  }, [currentSceneNumber]);

  useEffect(() => {
    if (!currentSceneAnimatedVideoUrl || hasVideoLoadError || currentSceneAnimatedVideoBlobUrl) {
      return;
    }

    let cancelled = false;

    const loadVideo = async () => {
      try {
        const videoPath = currentSceneAnimatedVideoUrl.startsWith('/')
          ? currentSceneAnimatedVideoUrl
          : `/${currentSceneAnimatedVideoUrl}`;
        const blobUrl = await fetchMediaBlobUrl(videoPath);
        if (!blobUrl || cancelled) {
          if (!blobUrl) {
            setVideoLoadError((prev) => new Set(prev).add(currentSceneNumber));
          }
          return;
        }

        setVideoBlobUrls((prev) => {
          const next = new Map(prev);
          const existing = next.get(currentSceneNumber);
          if (existing) {
            URL.revokeObjectURL(existing);
          }
          next.set(currentSceneNumber, blobUrl);
          return next;
        });
      } catch (err) {
        console.warn('Failed to load animated video:', err);
        setVideoLoadError((prev) => {
          const next = new Set(prev);
          next.add(currentSceneNumber);
          return next;
        });
      }
    };

    loadVideo();

    return () => {
      cancelled = true;
    };
  }, [currentSceneNumber, currentSceneAnimatedVideoUrl, currentSceneAnimatedVideoBlobUrl, hasVideoLoadError]);

  // Cleanup video blob URLs when component unmounts
  const videoBlobUrlsRef = React.useRef(videoBlobUrls);
  useEffect(() => {
    videoBlobUrlsRef.current = videoBlobUrls;
  }, [videoBlobUrls]);

  useEffect(() => {
    return () => {
      videoBlobUrlsRef.current.forEach((blob) => {
        URL.revokeObjectURL(blob);
      });
    };
  }, []);

  useEffect(() => {
    if (storySections.length > 0) {
      setCurrentPageIndex(0);
      setPageDirection(0);
    }
  }, [storySections.length]);

  const handlePrevPage = () => {
    if (canGoPrev) {
      setPageDirection(-1);
      setCurrentPageIndex((prev) => prev - 1);
    }
  };

  const handleNextPage = () => {
    if (canGoNext) {
      setPageDirection(1);
      setCurrentPageIndex((prev) => prev + 1);
    }
  };

  const handleGenerateStart = async () => {
    if (!state.premise || (!state.outline && !state.outlineScenes)) {
      setError('Please generate a premise and outline first');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request = state.getRequest();
      // Use structured scenes if available, otherwise use text outline
      const outline = state.isOutlineStructured && state.outlineScenes 
        ? state.outlineScenes 
        : (state.outline || '');
      
      const response = await storyWriterApi.generateStoryStart(
        state.premise,
        outline,
        request
      );
      
      if (response.success && response.story) {
        state.setStoryContent(response.story);
        state.setIsComplete(response.is_complete);
        state.setError(null);
      } else {
        throw new Error(response.story || 'Failed to generate story');
      }
    } catch (err: any) {
      console.error('Story start generation failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('StoryWriting: Detected subscription error, triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StoryWriting: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsGenerating(false);
          return;
        } else {
          console.warn('StoryWriting: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate story';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = async () => {
    if (!state.premise || (!state.outline && !state.outlineScenes) || !state.storyContent) {
      setError('Please generate story content first');
      return;
    }

    setIsContinuing(true);
    setError(null);

    try {
      const request = state.getRequest();
      // Use structured scenes if available, otherwise use text outline
      const outline = state.isOutlineStructured && state.outlineScenes 
        ? state.outlineScenes 
        : (state.outline || '');
      
      const continueRequest = {
        ...request,
        premise: state.premise,
        outline: outline,
        story_text: state.storyContent,
      };
      
      const response = await storyWriterApi.continueStory(continueRequest);
      
      if (response.success && response.continuation) {
        // Check if continuation is IAMDONE marker
        const isDone = response.is_complete || /IAMDONE/i.test(response.continuation);
        
        // Strip IAMDONE marker if present for cleaner display
        const cleanContinuation = response.continuation.replace(/IAMDONE/gi, '').trim();
        
        // Only append continuation if it's not just IAMDONE or empty
        if (cleanContinuation) {
          state.setStoryContent((state.storyContent || '') + '\n\n' + cleanContinuation);
        }
        
        // Set completion status
        state.setIsComplete(isDone);
        
        // If story is complete, show success message
        if (isDone) {
          console.log('Story is complete. Word count target reached.');
        }
        
        state.setError(null);
      } else {
        throw new Error(response.continuation || 'Failed to continue story');
      }
    } catch (err: any) {
      console.error('Story continuation failed:', err);
      
      // Check if this is a subscription error (429/402) and trigger global subscription modal
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        console.log('StoryWriting: Detected subscription error in continuation, triggering global handler', {
          status,
          data: err?.response?.data
        });
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          console.log('StoryWriting: Global subscription error handler triggered successfully');
          // Don't set local error - let the global modal handle it
          setIsContinuing(false);
          return;
        } else {
          console.warn('StoryWriting: Global subscription error handler did not handle the error');
        }
      }
      
      // For non-subscription errors, show local error message
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to continue story';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsContinuing(false);
    }
  };

  const handleContinueToExport = () => {
    if (state.storyContent && state.isComplete) {
      onNext();
    }
  };

  return (
    <Paper 
      sx={{ 
        p: 4, 
        mt: 2,
        backgroundColor: '#F7F3E9',
        color: '#2C2416',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08)',
      }}
    >
      <GlobalStyles
        styles={{
          '.tw-shadow-book': {
            boxShadow: '0 36px 80px rgba(45, 30, 15, 0.35)',
          },
          '.tw-rounded-book': {
            borderRadius: '20px',
          },
          '.tw-page-accent': {
            background: 'linear-gradient(120deg, #f9e6c8, #f2d8b4)',
          },
        }}
      />
      {state.storyContent && (
        <Typography variant="body2" sx={{ mb: 3, color: '#5D4037', fontStyle: 'italic' }}>
          Current word count: {state.storyContent.split(/\s+/).filter(word => word.length > 0).length} words
          {state.storyLength && (
            <> (Target: {state.storyLength.includes('1000') ? '>1000' : state.storyLength.includes('5000') ? '>5000' : '>10000'} words)</>
          )}
        </Typography>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {(!state.premise || (!state.outline && !state.outlineScenes)) && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please generate a premise and outline first.
        </Alert>
      )}

      {state.storyContent ? (
        <>
          {hasScenes && numPages > 1 ? (
            // Book-like UI with images
            <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
              <Box
                className="tw-shadow-book tw-rounded-book"
                sx={{
                  position: 'relative',
                  width: '100%',
                  maxWidth: '100%',
                  minHeight: 520,
                  display: 'flex',
                  flexDirection: { xs: 'column', md: 'row' },
                  borderRadius: '20px',
                  overflow: 'hidden',
                  boxShadow: '0 36px 80px rgba(45, 30, 15, 0.35)',
                  background: 'linear-gradient(120deg, #fff9ef 0%, #f5e1c7 45%, #fff9ef 100%)',
                }}
              >
                <AnimatePresence mode="wait" custom={pageDirection}>
                  <MotionBox
                    key={`book-pages-${currentPageIndex}`}
                    custom={pageDirection}
                    variants={{}}
                    initial="enter"
                    animate="center"
                    exit="exit"
                    sx={{
                      width: '100%',
                      display: 'flex',
                      flexDirection: { xs: 'column', md: 'row' },
                      position: 'relative',
                      height: '100%',
                    }}
                  >
                    {/* Left page - Image */}
                    <MotionBox
                      key={`image-${currentPageIndex}`}
                      role="button"
                      aria-label="Previous page"
                      onClick={handlePrevPage}
                      custom={pageDirection}
                      variants={leftPageVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      sx={{
                        flexBasis: { xs: '100%', md: '48%' },
                        maxWidth: { xs: '100%', md: '48%' },
                        padding: { xs: 3, md: 4, lg: 5 },
                        pr: { xs: 3, md: 5, lg: 6 },
                        borderRight: '1px solid rgba(120, 90, 60, 0.18)',
                        cursor: canGoPrev ? 'pointer' : 'default',
                        background:
                          'linear-gradient(100deg, rgba(255,255,255,0.82) 0%, rgba(250,240,225,0.95) 50%, rgba(242,226,204,0.9) 100%)',
                        boxShadow: 'inset -18px 0 30px rgba(160, 120, 90, 0.18)',
                        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        '&:hover': canGoPrev
                          ? {
                              transform: 'translateX(-4px) rotate(-0.3deg)',
                              boxShadow: 'inset -24px 0 50px rgba(145, 110, 72, 0.25)',
                            }
                          : undefined,
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 18,
                          bottom: 18,
                          right: '-12px',
                          width: 24,
                          background:
                            'linear-gradient(180deg, rgba(220,190,150,0.25) 0%, rgba(200,160,120,0) 50%, rgba(220,190,150,0.25) 100%)',
                          filter: 'blur(5px)',
                          opacity: 0.8,
                        },
                      }}
                    >
                      {showAnimatedVideo ? (
                        <Box
                          sx={{
                            width: '100%',
                            borderRadius: '12px',
                            overflow: 'hidden',
                            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.18), 0 4px 8px rgba(0, 0, 0, 0.12)',
                            border: '3px solid rgba(120, 90, 60, 0.25)',
                            backgroundColor: '#000',
                          }}
                        >
                          <Box
                            component="video"
                            src={currentSceneAnimatedVideoBlobUrl ?? undefined}
                            poster={currentSceneImageFullUrl ?? undefined}
                            autoPlay
                            muted
                            loop
                            controls
                            playsInline
                            sx={{
                              width: '100%',
                              height: 'auto',
                              display: 'block',
                              minHeight: '300px',
                              maxHeight: '500px',
                              objectFit: 'cover',
                            }}
                          />
                        </Box>
                      ) : currentSceneImageFullUrl ? (
                        <Box
                          sx={{
                            width: '100%',
                            borderRadius: '12px',
                            overflow: 'hidden',
                            boxShadow: '0 8px 20px rgba(0, 0, 0, 0.18), 0 4px 8px rgba(0, 0, 0, 0.12)',
                            border: '3px solid rgba(120, 90, 60, 0.25)',
                            backgroundColor: '#fff',
                            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                            '&:hover': {
                              transform: 'translateY(-4px) scale(1.01)',
                              boxShadow: '0 12px 28px rgba(0, 0, 0, 0.25), 0 6px 12px rgba(0, 0, 0, 0.18)',
                            },
                          }}
                        >
                          <Box
                            component="img"
                            src={currentSceneImageFullUrl}
                            alt={currentScene?.title || `Scene ${currentSceneNumber} illustration`}
                            sx={{
                              width: '100%',
                              height: 'auto',
                              display: 'block',
                              objectFit: 'contain',
                              minHeight: '300px',
                              maxHeight: '500px',
                            }}
                            onError={() => {
                              setImageLoadError((prev) => new Set(prev).add(currentSceneNumber));
                            }}
                          />
                        </Box>
                      ) : (
                        <Box
                          sx={{
                            width: '100%',
                            minHeight: '300px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#7a5335',
                          }}
                        >
                          <Typography variant="body2" sx={{ textAlign: 'center' }}>
                            {currentScene?.image_prompt || 'No image available for this scene'}
                          </Typography>
                        </Box>
                      )}
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, width: '100%' }}>
                        <Typography variant="caption" sx={{ color: '#7a5335' }}>
                          Click to turn back
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#a37b55' }}>
                          {canGoPrev ? '← Previous page' : 'Start of story'}
                        </Typography>
                      </Box>
                    </MotionBox>

                    {/* Right page - Story text */}
                    <MotionBox
                      key={`story-${currentPageIndex}`}
                      role="button"
                      aria-label="Next page"
                      onClick={handleNextPage}
                      custom={pageDirection}
                      variants={rightPageVariants}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      sx={{
                        flexBasis: { xs: '100%', md: '52%' },
                        maxWidth: { xs: '100%', md: '52%' },
                        padding: { xs: 3, md: 4, lg: 5 },
                        pl: { xs: 3, md: 5, lg: 6 },
                        cursor: canGoNext ? 'pointer' : 'default',
                        background:
                          'linear-gradient(260deg, rgba(255,255,255,0.88) 0%, rgba(249,236,215,0.96) 45%, rgba(243,226,206,0.92) 100%)',
                        boxShadow: 'inset 18px 0 30px rgba(160, 120, 90, 0.18)',
                        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                        display: 'flex',
                        flexDirection: 'column',
                        '&:hover': canGoNext
                          ? {
                              transform: 'translateX(4px) rotate(0.3deg)',
                              boxShadow: 'inset 24px 0 50px rgba(145, 110, 72, 0.25)',
                            }
                          : undefined,
                        '&::before': {
                          content: '""',
                          position: 'absolute',
                          top: 18,
                          bottom: 18,
                          left: '-12px',
                          width: 24,
                          background:
                            'linear-gradient(180deg, rgba(220,190,150,0.25) 0%, rgba(200,160,120,0) 50%, rgba(220,190,150,0.25) 100%)',
                          filter: 'blur(5px)',
                          opacity: 0.8,
                        },
                      }}
                    >
                      <Box sx={{ flex: 1, overflowY: 'auto' }}>
                        <Typography
                          variant="body1"
                          sx={{
                            color: '#2C2416',
                            lineHeight: 1.8,
                            fontFamily: `'Georgia', 'Times New Roman', serif`,
                            fontSize: '1.1rem',
                            whiteSpace: 'pre-wrap',
                            wordBreak: 'break-word',
                          }}
                        >
                          {currentPage || 'Loading...'}
                        </Typography>
                      </Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2 }}>
                        <Typography variant="caption" sx={{ color: '#a37b55' }}>
                          {canGoNext ? 'Next page →' : 'End of story'}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#7a5335' }}>
                          Page {currentPageIndex + 1} of {numPages}
                        </Typography>
                      </Box>
                    </MotionBox>
                  </MotionBox>
                </AnimatePresence>
              </Box>
            </Box>
          ) : (
            // Simple text display if no scenes
            <Box sx={{ mb: 3 }}>
              <Paper
                sx={{
                  p: 3,
                  backgroundColor: '#FAF9F6',
                  minHeight: '400px',
                }}
              >
                <Typography
                  variant="body1"
                  sx={{
                    color: '#2C2416',
                    lineHeight: 1.8,
                    fontFamily: `'Georgia', 'Times New Roman', serif`,
                    fontSize: '1.1rem',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {state.storyContent}
                </Typography>
              </Paper>
            </Box>
          )}

          {/* Multimedia Generation Section */}
          {state.isOutlineStructured && state.outlineScenes && state.outlineScenes.length > 0 && (
            <MultimediaSection state={state} />
          )}

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap', alignItems: 'center' }}>
            {/* Only show Continue Writing button for medium/long stories that are not complete */}
            {!state.isComplete && !isShortStory(state.storyLength) && (
              <Button
                variant="outlined"
                onClick={handleContinue}
                disabled={isContinuing || !state.storyContent}
              >
                {isContinuing ? (
                  <>
                    <CircularProgress size={20} sx={{ mr: 1 }} />
                    Continuing...
                  </>
                ) : (
                  'Continue Writing'
                )}
              </Button>
            )}
            {/* Show completion message if story is complete */}
            {state.isComplete && (
              <Alert severity="success" sx={{ flex: 1, minWidth: '200px' }}>
                Story is complete! You can proceed to export.
              </Alert>
            )}
            {/* Show info message for short stories that are not complete yet */}
            {!state.isComplete && isShortStory(state.storyLength) && (
              <Alert severity="info" sx={{ flex: 1, minWidth: '200px' }}>
                Short stories are generated in one call. If the story is incomplete, please regenerate it.
              </Alert>
            )}
            <Button
              variant="contained"
              onClick={handleContinueToExport}
              disabled={!state.storyContent || !state.isComplete}
            >
              Continue to Export
            </Button>
          </Box>
        </>
      ) : (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            {state.premise && (state.outline || state.outlineScenes)
              ? 'Click "Generate Story" to start writing your story.'
              : 'Please generate a premise and outline first.'}
          </Alert>
          <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="contained"
              onClick={handleGenerateStart}
              disabled={isGenerating || !state.premise || (!state.outline && !state.outlineScenes)}
            >
              {isGenerating ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Generating...
                </>
              ) : (
                'Generate Story'
              )}
            </Button>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default StoryWriting;
