import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  Divider,
  LinearProgress,
  CircularProgress,
  Chip,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Collapse,
  IconButton,
} from '@mui/material';
import VolumeUpIcon from '@mui/icons-material/VolumeUp';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { triggerSubscriptionError, aiApiClient } from '../../../api/client';

interface MultimediaSectionProps {
  state: ReturnType<typeof useStoryWriterState>;
}

export const MultimediaSection: React.FC<MultimediaSectionProps> = ({ state }) => {
  const [isGeneratingAudio, setIsGeneratingAudio] = useState(false);
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [audioProgress, setAudioProgress] = useState(0);
  const [videoProgress, setVideoProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedScenes, setSelectedScenes] = useState<Set<number>>(new Set());
  const [showSceneSelection, setShowSceneSelection] = useState(false);
  const [audioBlobUrls, setAudioBlobUrls] = useState<Map<number, string>>(new Map());

  const hasScenes = state.isOutlineStructured && state.outlineScenes && state.outlineScenes.length > 0;
  const narrationEnabled = state.enableNarration;
  const videoEnabled = state.enableVideoNarration;
  const hasAudio = narrationEnabled && state.sceneAudio && state.sceneAudio.size > 0;
  const hasVideo = videoEnabled && !!state.storyVideo;
  const hasImages = state.sceneImages && state.sceneImages.size > 0;

  // Initialize selected scenes to all scenes by default
  useEffect(() => {
    if (!narrationEnabled || !state.outlineScenes) {
      setSelectedScenes(new Set());
      return;
    }
    setSelectedScenes((prev) => {
      if (prev.size > 0) return prev;
      const scenes = state.outlineScenes ?? [];
      const allSceneNumbers = new Set(
        scenes.map((scene: any, index: number) => scene.scene_number || index + 1),
      );
      return allSceneNumbers;
    });
  }, [narrationEnabled, state.outlineScenes]);

  const canGenerateAudio = hasScenes && selectedScenes.size > 0 && !isGeneratingAudio;
  const canGenerateVideo = hasScenes && hasImages && hasAudio && !isGeneratingVideo;

  const handleSceneSelectionToggle = (sceneNumber: number) => {
    setSelectedScenes((prev) => {
      const next = new Set(prev);
      if (next.has(sceneNumber)) {
        next.delete(sceneNumber);
      } else {
        next.add(sceneNumber);
      }
      return next;
    });
  };

  const handleSelectAllScenes = () => {
    if (hasScenes && state.outlineScenes) {
      const allSceneNumbers = new Set(
        state.outlineScenes.map((scene: any, index: number) => 
          scene.scene_number || index + 1
        )
      );
      setSelectedScenes(allSceneNumbers);
    }
  };

  const handleDeselectAllScenes = () => {
    setSelectedScenes(new Set());
  };

  // Fetch authenticated audio blobs for playback
  useEffect(() => {
    const sceneAudioMap = state.sceneAudio;
    if (!narrationEnabled || !sceneAudioMap || sceneAudioMap.size === 0) {
      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map();
      });
      return;
    }

    let isMounted = true;

    const loadAudioBlobs = async () => {
      const entries = Array.from(sceneAudioMap.entries());
      const blobEntries: Array<[number, string]> = [];

      for (const [sceneNumber, audioPath] of entries) {
        if (!audioPath) continue;
        try {
          const normalizedPath = audioPath.startsWith('/') ? audioPath : `/${audioPath}`;
          const response = await aiApiClient.get(normalizedPath, {
            responseType: 'blob',
          });
          const blobUrl = URL.createObjectURL(response.data);
          blobEntries.push([sceneNumber, blobUrl]);
        } catch (err) {
          console.error('Failed to load audio blob:', err);
        }
      }

      if (!isMounted) {
        blobEntries.forEach(([, url]) => URL.revokeObjectURL(url));
        return;
      }

      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map(blobEntries);
      });
    };

    loadAudioBlobs();

    return () => {
      isMounted = false;
      setAudioBlobUrls((prev) => {
        prev.forEach((url) => URL.revokeObjectURL(url));
        return new Map();
      });
    };
  }, [state.sceneAudio, narrationEnabled]);

  const handleGenerateAudio = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }
    if (!narrationEnabled) {
      setError('Narration feature is disabled in Story Setup.');
      return;
    }

    if (selectedScenes.size === 0) {
      setError('Please select at least one scene to generate audio for');
      return;
    }

    setIsGeneratingAudio(true);
    setError(null);
    setAudioProgress(0);

    try {
      // Filter scenes to only selected ones
      const scenesToGenerate = state.outlineScenes.filter((scene: any, index: number) => {
        const sceneNumber = scene.scene_number || index + 1;
        return selectedScenes.has(sceneNumber);
      });

      const response = await storyWriterApi.generateSceneAudio({
        scenes: scenesToGenerate,
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
        setAudioProgress(100);
      } else {
        throw new Error('Failed to generate audio');
      }
    } catch (err: any) {
      console.error('Audio generation failed:', err);

      // Check if this is a subscription error (429/402)
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          setIsGeneratingAudio(false);
          return;
        }
      }

      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate audio';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingAudio(false);
    }
  };

  const handleGenerateVideo = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }
    if (!videoEnabled) {
      setError('Story video feature is disabled in Story Setup.');
      return;
    }

    if (!hasImages) {
      setError('Please generate images for scenes first');
      return;
    }

    if (!hasAudio) {
      setError('Please generate audio for scenes first');
      return;
    }

    setIsGeneratingVideo(true);
    setError(null);
    setVideoProgress(0);

    try {
      // Prepare image and audio URLs in scene order
      const imageUrls: string[] = [];
      const audioUrls: string[] = [];
      const scenes = state.outlineScenes;

      for (const scene of scenes) {
        const sceneNumber = scene.scene_number || scenes.indexOf(scene) + 1;
        const imageUrl = state.sceneImages?.get(sceneNumber);
        const audioUrl = state.sceneAudio?.get(sceneNumber);

        if (imageUrl && audioUrl) {
          imageUrls.push(imageUrl);
          audioUrls.push(audioUrl);
        } else {
          throw new Error(`Missing image or audio for scene ${sceneNumber}`);
        }
      }

      if (imageUrls.length !== scenes.length || audioUrls.length !== scenes.length) {
        throw new Error('Number of images and audio files must match number of scenes');
      }

      setVideoProgress(30);

      // Generate video
      const response = await storyWriterApi.generateStoryVideo({
        scenes: scenes,
        image_urls: imageUrls,
        audio_urls: audioUrls,
        story_title: state.storySetting || 'Story',
        fps: state.videoFps,
        transition_duration: state.videoTransitionDuration,
      });

      if (response.success && response.video) {
        state.setStoryVideo(response.video.video_url);
        state.setError(null);
        setVideoProgress(100);
      } else {
        throw new Error('Failed to generate video');
      }
    } catch (err: any) {
      console.error('Video generation failed:', err);

      // Check if this is a subscription error (429/402)
      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          setIsGeneratingVideo(false);
          return;
        }
      }

      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate video';
      setError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = () => {
    if (state.storyVideo) {
      const videoUrl = storyWriterApi.getVideoUrl(state.storyVideo);
      const a = document.createElement('a');
      a.href = videoUrl;
      a.download = `story-video-${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  };

  if (!hasScenes) {
    return null; // Don't show if no scenes available
  }

  return (
    <Paper
      sx={{
        p: 3,
        mb: 3,
        backgroundColor: '#FAF9F6',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ mb: 2, fontWeight: 600, color: '#1A1611' }}>
        Multimedia Generation
      </Typography>
      <Typography variant="body2" sx={{ mb: 3, color: '#5D4037' }}>
        Generate audio narration and video for your story scenes.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Audio Section */}
      {narrationEnabled ? (
        <Box sx={{ mb: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <VolumeUpIcon sx={{ color: hasAudio ? '#4caf50' : '#5D4037' }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1A1611' }}>
                Audio Narration
              </Typography>
              {hasAudio && (
                <Chip
                  icon={<CheckCircleIcon />}
                  label="Generated"
                  size="small"
                  color="success"
                  sx={{ ml: 1 }}
                />
              )}
            </Box>
            <Button
              variant={hasAudio ? 'outlined' : 'contained'}
              startIcon={isGeneratingAudio ? <CircularProgress size={16} /> : <VolumeUpIcon />}
              onClick={handleGenerateAudio}
              disabled={!canGenerateAudio || isGeneratingAudio}
            >
              {hasAudio
                ? 'Regenerate Selected'
                : `Generate Audio (${selectedScenes.size} scene${selectedScenes.size !== 1 ? 's' : ''})`}
            </Button>
          </Box>

          {hasScenes && state.outlineScenes && (
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2" sx={{ color: '#5D4037', fontWeight: 500 }}>
                  Select scenes to generate audio for:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    size="small"
                    variant="text"
                    onClick={handleSelectAllScenes}
                    sx={{ minWidth: 'auto', px: 1, fontSize: '0.75rem' }}
                  >
                    Select All
                  </Button>
                  <Button
                    size="small"
                    variant="text"
                    onClick={handleDeselectAllScenes}
                    sx={{ minWidth: 'auto', px: 1, fontSize: '0.75rem' }}
                  >
                    Deselect All
                  </Button>
                  <IconButton
                    size="small"
                    onClick={() => setShowSceneSelection(!showSceneSelection)}
                    sx={{ p: 0.5 }}
                  >
                    {showSceneSelection ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>
              </Box>
              <Collapse in={showSceneSelection}>
                <FormGroup sx={{ pl: 1 }}>
                  {state.outlineScenes.map((scene: any, index: number) => {
                    const sceneNumber = scene.scene_number || index + 1;
                    const hasAudioForScene = state.sceneAudio?.has(sceneNumber);
                    return (
                      <FormControlLabel
                        key={sceneNumber}
                        control={
                          <Checkbox
                            checked={selectedScenes.has(sceneNumber)}
                            onChange={() => handleSceneSelectionToggle(sceneNumber)}
                            size="small"
                          />
                        }
                        label={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              Scene {sceneNumber}: {scene.title || `Scene ${sceneNumber}`}
                            </Typography>
                            {hasAudioForScene && (
                              <CheckCircleIcon sx={{ fontSize: 16, color: '#4caf50' }} />
                            )}
                          </Box>
                        }
                      />
                    );
                  })}
                </FormGroup>
              </Collapse>
            </Box>
          )}

          {isGeneratingAudio && (
            <Box sx={{ mt: 1 }}>
              <LinearProgress variant="indeterminate" />
              <Typography variant="caption" sx={{ mt: 0.5, color: '#5D4037', display: 'block' }}>
                Generating audio for {selectedScenes.size} selected scene
                {selectedScenes.size !== 1 ? 's' : ''}...
              </Typography>
            </Box>
          )}

          {hasAudio && state.sceneAudio && state.outlineScenes && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ color: '#5D4037', fontSize: '0.875rem', mb: 2 }}>
                Audio narration generated for {state.sceneAudio.size} scene(s). Listen to audio for each scene:
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {state.outlineScenes.map((scene: any, index: number) => {
                  const sceneNumber = scene.scene_number || index + 1;
                  const audioUrl = state.sceneAudio?.get(sceneNumber);
                  if (!audioUrl) return null;
                  const blobUrl = audioBlobUrls.get(sceneNumber);

                  return (
                    <Box
                      key={sceneNumber}
                      sx={{
                        p: 2,
                        backgroundColor: '#FFFFFF',
                        borderRadius: '8px',
                        border: '1px solid rgba(120, 90, 60, 0.2)',
                      }}
                    >
                      <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600, color: '#1A1611' }}>
                        Scene {sceneNumber}: {scene.title || `Scene ${sceneNumber}`}
                      </Typography>
                      <audio
                        controls
                        src={blobUrl ? blobUrl : storyWriterApi.getAudioUrl(audioUrl)}
                        style={{ width: '100%' }}
                      >
                        Your browser does not support the audio element.
                      </audio>
                    </Box>
                  );
                })}
              </Box>
            </Box>
          )}
        </Box>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          Narration is disabled in Story Setup. Enable it to generate or listen to audio narration.
        </Alert>
      )}

      <Divider sx={{ my: 3 }} />

      {/* Video Section */}
      {videoEnabled ? (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <VideoLibraryIcon sx={{ color: hasVideo ? '#4caf50' : '#5D4037' }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#1A1611' }}>
                Story Video
              </Typography>
              {hasVideo && (
                <Chip
                  icon={<CheckCircleIcon />}
                  label="Generated"
                  size="small"
                  color="success"
                  sx={{ ml: 1 }}
                />
              )}
              {!hasVideo && !hasImages && (
                <Chip label="Images required" size="small" color="warning" sx={{ ml: 1 }} />
              )}
              {!hasVideo && hasImages && !hasAudio && (
                <Chip label="Audio required" size="small" color="warning" sx={{ ml: 1 }} />
              )}
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {hasVideo && (
                <Button variant="outlined" startIcon={<DownloadIcon />} onClick={handleDownloadVideo}>
                  Download
                </Button>
              )}
              <Button
                variant={hasVideo ? 'outlined' : 'contained'}
                startIcon={isGeneratingVideo ? <CircularProgress size={16} /> : <VideoLibraryIcon />}
                onClick={handleGenerateVideo}
                disabled={!canGenerateVideo || isGeneratingVideo}
              >
                {hasVideo ? 'Regenerate Video' : 'Generate Video'}
              </Button>
            </Box>
          </Box>

          {isGeneratingVideo && (
            <Box sx={{ mt: 1 }}>
              <LinearProgress
                variant={videoProgress > 0 ? 'determinate' : 'indeterminate'}
                value={videoProgress}
              />
              <Typography variant="caption" sx={{ mt: 0.5, color: '#5D4037', display: 'block' }}>
                Generating video... This may take a few minutes.
              </Typography>
            </Box>
          )}

          {hasVideo && state.storyVideo && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" sx={{ color: '#5D4037', mb: 1, fontSize: '0.875rem' }}>
                Video ready! Preview and download below.
              </Typography>
              <Box
                component="video"
                controls
                src={storyWriterApi.getVideoUrl(state.storyVideo)}
                sx={{
                  width: '100%',
                  maxWidth: '600px',
                  borderRadius: '8px',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                }}
              >
                Your browser does not support the video tag.
              </Box>
            </Box>
          )}
        </Box>
      ) : (
        <Alert severity="info">
          Story video generation is disabled in Story Setup. Enable it to create narrative videos.
        </Alert>
      )}
    </Paper>
  );
};

