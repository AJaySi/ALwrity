import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Grid,
  Card,
  CardMedia,
  CardContent,
} from '@mui/material';
import GlobalStyles from '@mui/material/GlobalStyles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ImageIcon from '@mui/icons-material/Image';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import { motion, AnimatePresence } from 'framer-motion';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi, StoryScene } from '../../../services/storyWriterApi';
import { aiApiClient } from '../../../api/client';

const MotionBox = motion(Box);

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

interface StoryOutlineProps {
  state: ReturnType<typeof useStoryWriterState>;
  onNext: () => void;
}

const StoryOutline: React.FC<StoryOutlineProps> = ({ state, onNext }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [isGeneratingImages, setIsGeneratingImages] = useState(false);
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSceneIndex, setCurrentSceneIndex] = useState(0);
  const [pageDirection, setPageDirection] = useState(0);
  const [imageLoadError, setImageLoadError] = useState<Set<number>>(new Set());
  const [imageBlobUrls, setImageBlobUrls] = useState<Map<number, string>>(new Map());
  
  // Use state from hook instead of local state
  const sceneImages = state.sceneImages || new Map<number, string>();
  const sceneAudio = state.sceneAudio || new Map<number, string>();

  const scenes = state.outlineScenes || [];
  const hasScenes = state.isOutlineStructured && scenes.length > 0;

  useEffect(() => {
    if (hasScenes) {
      setCurrentSceneIndex(0);
      setPageDirection(0);
    }
  }, [hasScenes]);

  const currentScene = hasScenes ? scenes[currentSceneIndex] : null;
  const canGoPrev = currentSceneIndex > 0;
  const canGoNext = hasScenes ? currentSceneIndex < scenes.length - 1 : false;
  
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
  }, [currentSceneNumber, currentSceneImageUrl, hasImageLoadError]);
  
  // Cleanup blob URLs when component unmounts or scenes change
  useEffect(() => {
    return () => {
      // Revoke all blob URLs on unmount
      imageBlobUrls.forEach((blobUrl) => {
        URL.revokeObjectURL(blobUrl);
      });
    };
  }, []);
  
  const currentSceneImageFullUrl = imageBlobUrls.get(currentSceneNumber) || null;
  
  // Reset image load error when scene changes
  useEffect(() => {
    setImageLoadError((prev) => {
      const next = new Set(prev);
      next.delete(currentSceneNumber);
      return next;
    });
  }, [currentSceneNumber]);

  const handlePrevScene = () => {
    if (canGoPrev) {
      setPageDirection(-1);
      setCurrentSceneIndex((prev) => prev - 1);
    }
  };

  const handleNextScene = () => {
    if (canGoNext) {
      setPageDirection(1);
      setCurrentSceneIndex((prev) => prev + 1);
    }
  };

  const handleGenerateOutline = async () => {
    if (!state.premise) {
      setError('Please generate a premise first');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const request = state.getRequest();
      const response = await storyWriterApi.generateOutline(state.premise, request);
      
      if (response.success && response.outline) {
        // Handle structured outline (scenes) or plain text outline
        if (response.is_structured && Array.isArray(response.outline)) {
          // Structured outline with scenes
          const scenes = response.outline as StoryScene[];
          state.setOutlineScenes(scenes);
          state.setIsOutlineStructured(true);
          // Also store as formatted text for backward compatibility
          const formattedOutline = scenes.map((scene, idx) => 
            `Scene ${scene.scene_number || idx + 1}: ${scene.title}\n${scene.description}`
          ).join('\n\n');
          state.setOutline(formattedOutline);
        } else {
          // Plain text outline
          state.setOutline(typeof response.outline === 'string' ? response.outline : String(response.outline));
          state.setOutlineScenes(null);
          state.setIsOutlineStructured(false);
        }
        state.setError(null);
      } else {
        throw new Error(typeof response.outline === 'string' ? response.outline : 'Failed to generate outline');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate outline';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleContinue = () => {
    if (state.outline || state.outlineScenes) {
      onNext();
    }
  };

  const handleGenerateImages = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }

    setIsGeneratingImages(true);
    setError(null);

    try {
      const response = await storyWriterApi.generateSceneImages({
        scenes: state.outlineScenes,
        provider: state.imageProvider || undefined,
        width: state.imageWidth,
        height: state.imageHeight,
        model: state.imageModel || undefined,
      });
      
      if (response.success && response.images) {
        // Store image URLs by scene number
        const imagesMap = new Map<number, string>();
        response.images.forEach((image) => {
          if (image.image_url && !image.error) {
            imagesMap.set(image.scene_number, image.image_url);
          }
        });
        state.setSceneImages(imagesMap);
        state.setError(null);
      } else {
        throw new Error('Failed to generate images');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate images';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingImages(false);
    }
  };

  const handleGenerateAudio = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }

    setIsGeneratingAudio(true);
    setError(null);

    try {
      const response = await storyWriterApi.generateSceneAudio({
        scenes: state.outlineScenes,
        provider: state.audioProvider,
        lang: state.audioLang,
        slow: state.audioSlow,
        rate: state.audioRate,
      });
      
      if (response.success && response.audio_files) {
        // Store audio URLs by scene number
        const audioMap = new Map<number, string>();
        response.audio_files.forEach((audio) => {
          if (audio.audio_url && !audio.error) {
            audioMap.set(audio.scene_number, audio.audio_url);
          }
        });
        state.setSceneAudio(audioMap);
        state.setError(null);
      } else {
        throw new Error('Failed to generate audio');
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate audio';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  // Render structured scenes
  const renderStructuredScenes = () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      return null;
    }

    return (
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ mb: 2, color: '#1A1611' }}>
          Story Scenes ({state.outlineScenes.length} scenes)
        </Typography>
        {state.outlineScenes.map((scene: StoryScene, index: number) => (
          <Accordion 
            key={index} 
            sx={{ 
              mb: 2,
              backgroundColor: '#FAF9F6', // Slightly lighter cream for accordions
              '&:before': {
                display: 'none', // Remove default border
              },
            }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1A1611' }}>
                Scene {scene.scene_number || index + 1}: {scene.title}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="body2" sx={{ color: '#5D4037' }} gutterBottom>
                    <strong>Description:</strong>
                  </Typography>
                  <Typography variant="body1" sx={{ mb: 2, color: '#2C2416' }}>
                    {scene.description}
                  </Typography>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" sx={{ color: '#5D4037' }} gutterBottom>
                    <strong>Image Prompt:</strong>
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    value={scene.image_prompt}
                    disabled
                    variant="outlined"
                    size="small"
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#FFFFFF',
                        color: '#1A1611',
                        '& fieldset': {
                          borderColor: '#8D6E63',
                          borderWidth: '1.5px',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: '#1A1611',
                      },
                    }}
                  />
                  {sceneImages && sceneImages.has(scene.scene_number || index + 1) && (
                    <Card 
                      sx={{ 
                        mt: 2,
                        backgroundColor: '#FAF9F6', // Slightly lighter cream for cards
                        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.08)',
                      }}
                    >
                      <CardMedia
                        component="img"
                        height="200"
                        image={storyWriterApi.getImageUrl(sceneImages.get(scene.scene_number || index + 1) || '')}
                        alt={`Scene ${scene.scene_number || index + 1}: ${scene.title}`}
                        sx={{ objectFit: 'contain' }}
                      />
                      <CardContent>
                        <Typography variant="caption" sx={{ color: '#5D4037' }}>
                          Generated image for Scene {scene.scene_number || index + 1}
                        </Typography>
                      </CardContent>
                    </Card>
                  )}
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" sx={{ color: '#5D4037' }} gutterBottom>
                    <strong>Audio Narration:</strong>
                  </Typography>
                  <TextField
                    fullWidth
                    multiline
                    rows={3}
                    value={scene.audio_narration}
                    disabled
                    variant="outlined"
                    size="small"
                    sx={{
                      mb: 2,
                      '& .MuiOutlinedInput-root': {
                        backgroundColor: '#FFFFFF',
                        color: '#1A1611',
                        '& fieldset': {
                          borderColor: '#8D6E63',
                          borderWidth: '1.5px',
                        },
                      },
                      '& .MuiInputBase-input': {
                        color: '#1A1611',
                      },
                    }}
                  />
                  {sceneAudio && sceneAudio.has(scene.scene_number || index + 1) && (
                    <Box sx={{ mt: 2 }}>
                      <audio
                        controls
                        src={storyWriterApi.getAudioUrl(sceneAudio.get(scene.scene_number || index + 1) || '')}
                        style={{ width: '100%' }}
                      >
                        Your browser does not support the audio element.
                      </audio>
                      <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#5D4037' }}>
                        Generated audio for Scene {scene.scene_number || index + 1}
                      </Typography>
                    </Box>
                  )}
                </Grid>
                
                {scene.character_descriptions && scene.character_descriptions.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="body2" sx={{ color: '#5D4037' }} gutterBottom>
                      <strong>Characters:</strong>
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {scene.character_descriptions.map((char, idx) => (
                        <Chip key={idx} label={char} size="small" />
                      ))}
                    </Box>
                  </Grid>
                )}
                
                {scene.key_events && scene.key_events.length > 0 && (
                  <Grid item xs={12}>
                    <Typography variant="body2" sx={{ color: '#5D4037' }} gutterBottom>
                      <strong>Key Events:</strong>
                    </Typography>
                    <Box component="ul" sx={{ pl: 2, mb: 0 }}>
                      {scene.key_events.map((event, idx) => (
                        <li key={idx}>
                          <Typography variant="body2" sx={{ color: '#2C2416' }}>{event}</Typography>
                        </li>
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    );
  };

  return (
    <Paper 
      sx={{ 
        p: 4, 
        mt: 2,
        backgroundColor: '#F7F3E9', // Warm cream/parchment color
        color: '#2C2416', // Dark brown text for readability
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
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600, color: '#1A1611' }}>
        Story Outline
      </Typography>
      <Typography variant="body2" sx={{ mb: 4, color: '#5D4037' }}>
        Generate and review your story outline based on the premise. You can regenerate it or proceed to writing.
      </Typography>
      
      {state.isOutlineStructured && (
        <Alert severity="info" sx={{ mb: 3 }}>
          Structured outline with {state.outlineScenes?.length || 0} scenes generated. Each scene includes image prompts and audio narration.
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!state.premise && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Please generate a premise first in the Setup phase.
        </Alert>
      )}

      {(state.outline || state.outlineScenes) ? (
        <>
          {hasScenes ? (
            <>
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
                    border: '1px solid rgba(120, 90, 60, 0.28)',
                    transform: 'perspective(2200px) rotateX(2deg)',
                    mx: 'auto',
                    '&::after': {
                      content: '""',
                      position: 'absolute',
                      inset: '-10px -24px 28px',
                      background:
                        'radial-gradient(circle at 25% 20%, rgba(255,255,255,0.45) 0%, rgba(255,255,255,0) 42%), radial-gradient(circle at 75% 82%, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 46%)',
                      filter: 'blur(20px)',
                      zIndex: -2,
                    },
                  }}
                >
                  {/* Book spine */}
                  <Box
                    sx={{
                      position: 'absolute',
                      top: 0,
                      bottom: 0,
                      left: '50%',
                      width: '2px',
                      background: 'linear-gradient(180deg, rgba(120, 90, 60, 0.5) 0%, rgba(120, 90, 60, 0.08) 100%)',
                      transform: 'translateX(-50%)',
                      zIndex: 2,
                    }}
                  />

                  <AnimatePresence initial={false} custom={pageDirection}>
                    {/* Single container wrapping both pages for page turn animation */}
                    <MotionBox
                      key={`pages-${currentSceneIndex}`}
                      custom={pageDirection}
                      variants={{
                        enter: () => ({
                          opacity: 0,
                        }),
                        center: {
                          opacity: 1,
                        },
                        exit: () => ({
                          opacity: 0,
                        }),
                      }}
                      initial="enter"
                      animate="center"
                      exit="exit"
                      sx={{
                        display: 'flex',
                        width: '100%',
                        height: '100%',
                      }}
                    >
                    {/* Left page */}
                    <MotionBox
                      key={`meta-${currentSceneIndex}`}
                      role="button"
                      aria-label="Previous scene"
                      onClick={handlePrevScene}
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
                      <Box sx={{ flex: '0 0 auto' }}>
                        <Typography
                          variant="overline"
                          sx={{ color: '#7a5335', letterSpacing: 4, fontWeight: 600, display: 'block' }}
                        >
                          Scene {currentScene?.scene_number || currentSceneIndex + 1} of {scenes.length}
                        </Typography>
                        <Typography
                          variant="h4"
                          sx={{
                            mt: 1,
                            color: '#2C2416',
                            fontFamily: `'Playfair Display', serif`,
                            fontWeight: 600,
                            lineHeight: 1.2,
                            pr: 2,
                          }}
                        >
                          {currentScene?.title}
                        </Typography>
                      </Box>

                      <Box
                        sx={{
                          flex: '1 1 auto',
                          overflowY: 'auto',
                          mt: 3,
                          display: 'grid',
                          gridTemplateRows: currentSceneImageFullUrl ? 'auto 1fr auto auto' : 'auto auto auto 1fr',
                          alignContent: 'start',
                          gap: 3,
                        }}
                      >
                        <Box>
                          {currentSceneImageFullUrl ? (
                            <>
                              <Typography
                                variant="subtitle2"
                                sx={{ color: '#7a5335', textTransform: 'uppercase', letterSpacing: 1, mb: 1.5 }}
                              >
                                Scene Illustration
                              </Typography>
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
                                    // Mark this scene's image as failed to load
                                    setImageLoadError((prev) => new Set(prev).add(currentSceneNumber));
                                  }}
                                />
                              </Box>
                            </>
                          ) : (
                            <>
                              <Typography
                                variant="subtitle2"
                                sx={{ color: '#7a5335', textTransform: 'uppercase', letterSpacing: 1, mb: 1 }}
                              >
                                Image Prompt
                              </Typography>
                              <Typography variant="body2" sx={{ color: '#3f3224', lineHeight: 1.7 }}>
                                {currentScene?.image_prompt}
                              </Typography>
                            </>
                          )}
                        </Box>

                        <Box>
                          <Typography
                            variant="subtitle2"
                            sx={{ color: '#7a5335', textTransform: 'uppercase', letterSpacing: 1, mb: 1 }}
                          >
                            Audio Narration
                          </Typography>
                          <Typography variant="body2" sx={{ color: '#3f3224', lineHeight: 1.7 }}>
                            {currentScene?.audio_narration}
                          </Typography>
                        </Box>

                        {currentScene?.character_descriptions && currentScene?.character_descriptions.length > 0 && (
                          <Box>
                            <Typography
                              variant="subtitle2"
                              sx={{ color: '#7a5335', textTransform: 'uppercase', letterSpacing: 1, mb: 1 }}
                            >
                              Characters
                            </Typography>
                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
                              {currentScene.character_descriptions.map((char: string, idx: number) => (
                                <Chip
                                  key={idx}
                                  label={char}
                                  size="small"
                                  sx={{
                                    background: 'linear-gradient(120deg, #f9e6c8, #f2d8b4)',
                                    color: '#5a3922',
                                    fontWeight: 500,
                                    border: '1px solid rgba(120, 90, 60, 0.35)',
                                  }}
                                />
                              ))}
                            </Box>
                          </Box>
                        )}

                        {currentScene?.key_events && currentScene?.key_events.length > 0 && (
                          <Box>
                            <Typography
                              variant="subtitle2"
                              sx={{ color: '#7a5335', textTransform: 'uppercase', letterSpacing: 1, mb: 1 }}
                            >
                              Key Events
                            </Typography>
                            <Box component="ul" sx={{ pl: 2.5, color: '#3f3224', mb: 0, lineHeight: 1.7 }}>
                              {currentScene.key_events.map((event: string, idx: number) => (
                                <li key={idx}>
                                  <Typography variant="body2">{event}</Typography>
                                </li>
                              ))}
                            </Box>
                          </Box>
                        )}
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                        <Typography variant="caption" sx={{ color: '#7a5335' }}>
                          Click to turn back
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#a37b55' }}>
                          {canGoPrev ? '← Previous scene' : 'Start of outline'}
                        </Typography>
                      </Box>
                    </MotionBox>

                    {/* Right page */}
                    <MotionBox
                      key={`story-${currentSceneIndex}`}
                      role="button"
                      aria-label="Next scene"
                      onClick={handleNextScene}
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
                            fontSize: '1.08rem',
                            lineHeight: 1.9,
                            fontFamily: `'Merriweather', serif`,
                            whiteSpace: 'pre-line',
                            textAlign: 'justify',
                            textJustify: 'inter-word',
                            textIndent: '2em',
                            hyphens: 'auto',
                            pr: { xs: 0, md: 1.5 },
                          }}
                        >
                          {currentScene?.description}
                        </Typography>
                      </Box>

                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
                        <Typography variant="caption" sx={{ color: '#7a5335' }}>
                          Click to turn page
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#a37b55' }}>
                          {canGoNext ? 'Next scene →' : 'End of outline'}
                        </Typography>
                      </Box>
                    </MotionBox>
                    </MotionBox>
                  </AnimatePresence>
                </Box>
              </Box>

              <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
                <Typography variant="caption" sx={{ color: '#7a5335' }}>
                  Page {currentSceneIndex + 1} of {scenes.length}
                </Typography>
              </Box>
            </>
          ) : (
            <TextField
              fullWidth
              multiline
              rows={12}
              value={state.outline || ''}
              onChange={(e) => state.setOutline(e.target.value)}
              label="Story Outline"
              sx={{ mb: 3 }}
            />
          )}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
            <Button
              variant="outlined"
              onClick={handleGenerateOutline}
              disabled={isGenerating || !state.premise}
            >
              {isGenerating ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Regenerating...
                </>
              ) : (
                'Regenerate Outline'
              )}
            </Button>
            {state.isOutlineStructured && state.outlineScenes && (
              <>
                <Button
                  variant="outlined"
                  startIcon={<ImageIcon />}
                  onClick={handleGenerateImages}
                  disabled={isGeneratingImages || !state.outlineScenes || state.outlineScenes.length === 0}
                >
                  {isGeneratingImages ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Generating Images...
                    </>
                  ) : (
                    'Generate Images'
                  )}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<VolumeUpIcon />}
                  onClick={handleGenerateAudio}
                  disabled={isGeneratingAudio || !state.outlineScenes || state.outlineScenes.length === 0}
                >
                  {isGeneratingAudio ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Generating Audio...
                    </>
                  ) : (
                    'Generate Audio'
                  )}
                </Button>
              </>
            )}
            <Button
              variant="contained"
              onClick={handleContinue}
              disabled={(!state.outline && !state.outlineScenes) || isGenerating || isGeneratingImages || isGeneratingAudio}
            >
              Continue to Writing
            </Button>
          </Box>
        </>
      ) : (
        <Box>
          <Alert severity="info" sx={{ mb: 3 }}>
            {state.premise
              ? 'Generating outline... If this message persists, please return to Setup and try again.'
              : 'Please generate a premise first.'}
          </Alert>
        </Box>
      )}
    </Paper>
  );
};

export default StoryOutline;
