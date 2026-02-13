import React from 'react';
import { Box, Typography, Tooltip, Chip, CircularProgress } from '@mui/material';
import { motion, AnimatePresence } from 'framer-motion';
import OutlineHoverActions from './OutlineHoverActions';
import EditNoteIcon from '@mui/icons-material/EditNote';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import GraphicEqIcon from '@mui/icons-material/GraphicEq';
import ReplayIcon from '@mui/icons-material/Replay';
import { OperationButton } from '../../../shared/OperationButton';
import { leftPageVariants, rightPageVariants } from './pageVariants';
import { StoryScene } from '../../../../services/storyWriterApi';
import type { SceneAnimationResume } from '../../../../hooks/useStoryWriterState';

const MotionBox = motion.create(Box);

interface BookPagesProps {
  currentScene: StoryScene | null;
  currentSceneIndex: number;
  scenesLength: number;
  canGoPrev: boolean;
  canGoNext: boolean;
  pageDirection: number;
  onPrev: () => void;
  onNext: () => void;

  imageUrl: string | null;
  onImageError: () => void;

  narrationEnabled: boolean;
  audioUrl: string | null;
  hasAudio: boolean;
  onOpenImageModal: () => void;
  onOpenAudioModal: () => void;
  onOpenCharactersModal: () => void;
  onOpenKeyEventsModal: () => void;
  onOpenTitleModal: () => void;
  onOpenEditModal: () => void;
  onAnimateScene?: () => void;
  onResumeScene?: () => void;
  onAnimateWithVoiceover?: () => void;
  isAnimatingScene?: boolean;
  animatedVideoUrl?: string | null;
  resumeInfo?: SceneAnimationResume | null;
}

const BookPages: React.FC<BookPagesProps> = ({
  currentScene,
  currentSceneIndex,
  scenesLength,
  canGoPrev,
  canGoNext,
  pageDirection,
  onPrev,
  onNext,
  imageUrl,
  onImageError,
  narrationEnabled,
  onOpenImageModal,
  onOpenAudioModal,
  audioUrl,
  hasAudio,
  onOpenCharactersModal,
  onOpenKeyEventsModal,
  onOpenTitleModal,
  onOpenEditModal,
  onAnimateScene,
  onResumeScene,
  onAnimateWithVoiceover,
  isAnimatingScene,
  animatedVideoUrl,
  resumeInfo,
}) => {
  const currentSceneNumber = currentScene?.scene_number || currentSceneIndex + 1;
  const showAnimatedVideo = Boolean(animatedVideoUrl);
  const hasImage = Boolean(imageUrl);
  const hasMedia = showAnimatedVideo || hasImage;

  return (
    <Box sx={{ mb: 4, display: 'flex', justifyContent: 'center' }}>
      <Box
        className="tw-shadow-book tw-rounded-book"
        sx={{
          position: 'relative',
          width: { xs: '100%', lg: '90vw' },
          maxWidth: '1800px',
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
          <MotionBox
            key={`pages-${currentSceneIndex}`}
            custom={pageDirection}
            variants={{
              enter: () => ({ opacity: 0 }),
              center: { opacity: 1 },
              exit: () => ({ opacity: 0 }),
            }}
            initial="enter"
            animate="center"
            exit="exit"
            sx={{ display: 'flex', width: '100%', height: '100%' }}
          >
            {/* Left page */}
            <MotionBox
              key={`meta-${currentSceneIndex}`}
              role="button"
              aria-label="Previous scene"
              onClick={onPrev}
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
                <Typography variant="overline" sx={{ color: '#7a5335', letterSpacing: 4, fontWeight: 600, display: 'block' }}>
                  Scene {currentSceneNumber} of {scenesLength}
                </Typography>
                <Box sx={{ position: 'relative', display: 'inline-flex', alignItems: 'center', gap: 1, '&:hover .title-edit': { opacity: 1, pointerEvents: 'auto' } }}>
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
                  <Box
                    className="title-edit"
                    role="button"
                    aria-label="Edit title"
                    onClick={(e) => { e.stopPropagation(); onOpenTitleModal(); }}
                    sx={{
                      width: 32,
                      height: 32,
                      borderRadius: '50%',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
                      color: '#fff',
                      boxShadow: '0 6px 12px rgba(127,90,240,0.25)',
                      cursor: 'pointer',
                      opacity: 0,
                      pointerEvents: 'none',
                    }}
                  >
                    <EditNoteIcon fontSize="small" />
                  </Box>
                </Box>
              </Box>

              <Box
                sx={{
                  flex: '1 1 auto',
                  overflowY: 'auto',
                  mt: 3,
                  display: 'grid',
                  gridTemplateRows: hasMedia ? 'auto 1fr auto auto' : 'auto auto auto 1fr',
                  alignContent: 'start',
                  gap: 3,
                }}
              >
                <Box sx={{ position: 'relative', '&:hover .left-image-actions': { opacity: 1, pointerEvents: 'auto' } }}>
                  {showAnimatedVideo ? (
                    <Box
                      sx={{
                        width: '100%',
                        borderRadius: '12px',
                        overflow: 'hidden',
                        boxShadow: '0 12px 24px rgba(0, 0, 0, 0.2)',
                        border: '3px solid rgba(120, 90, 60, 0.25)',
                        backgroundColor: '#000',
                      }}
                    >
                      <Box
                        component="video"
                        src={animatedVideoUrl ?? undefined}
                        poster={imageUrl ?? undefined}
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
                  ) : hasImage ? (
                    <>
                       {/* Removed 'Scene Illustration' heading for cleaner look */}
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
                          src={imageUrl || undefined}
                          alt={currentScene?.title || `Scene ${currentSceneNumber} illustration`}
                          sx={{
                            width: '100%',
                            height: 'auto',
                            display: 'block',
                            objectFit: 'contain',
                            minHeight: '300px',
                            maxHeight: '500px',
                          }}
                          onError={onImageError}
                        />
                        <Box
                          className="left-image-actions"
                          sx={{
                            position: 'absolute',
                            top: 8,
                            right: 8,
                            display: 'flex',
                            flexDirection: 'column',
                            gap: 1,
                            opacity: 0,
                            pointerEvents: 'none',
                            transition: 'opacity 0.2s ease',
                            zIndex: 5,
                            alignItems: 'flex-end',
                          }}
                        >
                          <Tooltip title="Edit scene image prompt">
                            <Box
                              role="button"
                              aria-label="Edit scene image"
                              onClick={(e) => { e.stopPropagation(); onOpenImageModal(); }}
                              sx={{
                                width: 40,
                                height: 40,
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
                                boxShadow: '0 8px 16px rgba(127,90,240,0.3)',
                                color: 'white',
                                cursor: 'pointer',
                              }}
                            >
                              <EditNoteIcon />
                            </Box>
                          </Tooltip>

                          {hasImage && onAnimateScene && (
                            <Box
                              onClick={(e) => {
                                e.stopPropagation();
                              }}
                              sx={{ display: 'inline-flex', pointerEvents: 'auto' }}
                            >
                              <OperationButton
                                operation={{
                                  provider: 'video',
                                  model: 'kling-v2.5-turbo-std-5s',
                                  operation_type: 'scene_animation',
                                  actual_provider_name: 'wavespeed',
                                }}
                                label="Animate Scene"
                                variant="contained"
                                size="small"
                                startIcon={<PlayArrowIcon />}
                                showCost
                                checkOnHover
                                checkOnMount={false}
                                onClick={onAnimateScene}
                                disabled={isAnimatingScene}
                                sx={{
                                  minWidth: 'auto',
                                  padding: '8px',
                                  width: 40,
                                  height: 40,
                                  borderRadius: '50%',
                                  background: 'linear-gradient(135deg, #1f8a70 0%, #32d9c8 100%)',
                                  boxShadow: '0 8px 16px rgba(31,138,112,0.35)',
                                  color: 'white',
                                  '&:hover': {
                                    background: 'linear-gradient(135deg, #1a7a60 0%, #2dc9b8 100%)',
                                  },
                                  '& .MuiButton-startIcon': {
                                    margin: 0,
                                  },
                                  '& .MuiButton-label': {
                                    display: 'none',
                                  },
                                }}
                                tooltipPlacement="left"
                              />
                            </Box>
                          )}

                          {hasImage && hasAudio && onAnimateWithVoiceover && (
                            <Box
                              onClick={(e) => {
                                e.stopPropagation();
                              }}
                              sx={{ display: 'inline-flex', pointerEvents: 'auto' }}
                            >
                              <OperationButton
                                operation={{
                                  provider: 'video',
                                  model: 'wavespeed-ai/infinitetalk',
                                  operation_type: 'scene_animation_voiceover',
                                  actual_provider_name: 'wavespeed',
                                }}
                                label="Animate with Voiceover"
                                variant="contained"
                                size="small"
                                startIcon={<GraphicEqIcon />}
                                showCost
                                checkOnHover
                                checkOnMount={false}
                                onClick={onAnimateWithVoiceover}
                                disabled={isAnimatingScene}
                                sx={{
                                  minWidth: 'auto',
                                  padding: '8px',
                                  width: 40,
                                  height: 40,
                                  borderRadius: '50%',
                                  background: 'linear-gradient(135deg, #733dd9 0%, #bb86fc 100%)',
                                  boxShadow: '0 8px 16px rgba(115,61,217,0.35)',
                                  color: 'white',
                                  '&:hover': {
                                    background: 'linear-gradient(135deg, #6030ba 0%, #a974f1 100%)',
                                  },
                                  '& .MuiButton-startIcon': {
                                    margin: 0,
                                  },
                                  '& .MuiButton-label': {
                                    display: 'none',
                                  },
                                }}
                                tooltipPlacement="left"
                              />
                            </Box>
                          )}

                          {resumeInfo && onResumeScene && (
                            <Tooltip
                              title={resumeInfo.message || 'Resume animation download (no extra cost)'}
                              placement="left"
                            >
                              <Box
                                onClick={(e) => {
                                  e.stopPropagation();
                                }}
                                sx={{ display: 'inline-flex', pointerEvents: 'auto' }}
                              >
                                <OperationButton
                                  operation={{
                                    provider: 'video',
                                    model: 'kling-v2.5-turbo-std-resume',
                                    operation_type: 'scene_animation_resume',
                                    actual_provider_name: 'wavespeed',
                                  }}
                                  label="Resume Animation"
                                  variant="contained"
                                  size="small"
                                  startIcon={<ReplayIcon />}
                                  showCost={false}
                                  checkOnHover={false}
                                  checkOnMount={false}
                                  onClick={onResumeScene}
                                  disabled={isAnimatingScene}
                                  sx={{
                                    minWidth: 'auto',
                                    padding: '8px',
                                    width: 40,
                                    height: 40,
                                    borderRadius: '50%',
                                    background: 'linear-gradient(135deg, #b35c1e 0%, #f5a623 100%)',
                                    boxShadow: '0 8px 16px rgba(179,92,30,0.35)',
                                    color: 'white',
                                    '&:hover': {
                                      background: 'linear-gradient(135deg, #9c511a 0%, #e1911c 100%)',
                                    },
                                    '& .MuiButton-startIcon': {
                                      margin: 0,
                                    },
                                    '& .MuiButton-label': {
                                      display: 'none',
                                    },
                                  }}
                                  tooltipPlacement="left"
                                />
                              </Box>
                            </Tooltip>
                          )}
                        </Box>
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
                      <Box sx={{ mt: 1 }}>
                        <Tooltip title="Edit scene image prompt">
                          <Box
                            role="button"
                            aria-label="Edit scene image"
                            onClick={(e) => { e.stopPropagation(); onOpenImageModal(); }}
                            sx={{
                              width: 40,
                              height: 40,
                              borderRadius: '50%',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
                              boxShadow: '0 8px 16px rgba(127,90,240,0.3)',
                              color: 'white',
                              cursor: 'pointer',
                            }}
                          >
                            <EditNoteIcon />
                          </Box>
                        </Tooltip>
                      </Box>
                    </>
                  )}
                  {isAnimatingScene && (
                    <Box
                      sx={{
                        position: 'absolute',
                        inset: 0,
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        backdropFilter: 'blur(2px)',
                        backgroundColor: 'rgba(0,0,0,0.35)',
                        borderRadius: '12px',
                        color: '#fff',
                        gap: 1,
                        zIndex: 6,
                      }}
                    >
                      <CircularProgress color="inherit" size={36} />
                      <Typography variant="body2">Animating scene...</Typography>
                    </Box>
                  )}
                </Box>

                {/* Audio chip moved to right page */}

                 {/* Characters */}
                {currentScene?.character_descriptions && currentScene.character_descriptions.length > 0 && (
                  <></>
                )}

                 {/* Key Events */}
                {currentScene?.key_events && currentScene.key_events.length > 0 && (<></>)}
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
              role="button"
              aria-label="Next scene"
              onClick={onNext}
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
                position: 'relative',
                '&:hover .outline-actions': { opacity: 1, pointerEvents: 'auto' },
                '&:hover .chip-actions': { opacity: 1, pointerEvents: 'auto' },
              }}
            >
              <OutlineHoverActions
                onEdit={onOpenEditModal}
                onImprove={onOpenEditModal}
              />
              <Box sx={{ flex: 1, overflowY: 'auto', pt: { xs: 1, md: 2 } }}>
                <Box className="chip-actions" sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1.5, opacity: 0, pointerEvents: 'none', transition: 'opacity 0.2s ease' }}>
                  <Chip
                    size="medium"
                    variant="filled"
                    icon={<TipsAndUpdatesIcon sx={{ color: '#2CB67D !important' }} />}
                    label={audioUrl ? 'Audio' : 'Audio'}
                    onClick={(e) => { e.stopPropagation(); onOpenAudioModal(); }}
                    sx={{
                      px: 1.6,
                      py: 0.6,
                      fontWeight: 700,
                      letterSpacing: 0.2,
                      color: '#2C2416',
                      background: 'linear-gradient(135deg, #fffefc 0%, #f7efe1 100%)',
                      boxShadow: '0 8px 20px rgba(93,59,36,0.15)',
                      border: '1px solid rgba(120,90,60,0.25)',
                      cursor: 'pointer',
                    }}
                  />
                  {currentScene?.character_descriptions && currentScene.character_descriptions.length > 0 && (
                    <Chip
                      size="medium"
                      variant="filled"
                      label={`Characters (${currentScene.character_descriptions.length})`}
                      onClick={(e) => { e.stopPropagation(); onOpenCharactersModal(); }}
                      sx={{
                        px: 1.6,
                        py: 0.6,
                        fontWeight: 700,
                        color: '#2C2416',
                        background: 'linear-gradient(135deg, #fffefc 0%, #f5ecd8 100%)',
                        boxShadow: '0 8px 20px rgba(93,59,36,0.15)',
                        border: '1px solid rgba(120,90,60,0.25)',
                        cursor: 'pointer',
                      }}
                    />
                  )}
                  {currentScene?.key_events && currentScene.key_events.length > 0 && (
                    <Chip
                      size="medium"
                      variant="filled"
                      label={`Key events (${currentScene.key_events.length})`}
                      onClick={(e) => { e.stopPropagation(); onOpenKeyEventsModal(); }}
                      sx={{
                        px: 1.6,
                        py: 0.6,
                        fontWeight: 700,
                        color: '#2C2416',
                        background: 'linear-gradient(135deg, #fffefc 0%, #f5ecd8 100%)',
                        boxShadow: '0 8px 20px rgba(93,59,36,0.15)',
                        border: '1px solid rgba(120,90,60,0.25)',
                        cursor: 'pointer',
                      }}
                    />
                  )}
                </Box>
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
  );
};

export default BookPages;

