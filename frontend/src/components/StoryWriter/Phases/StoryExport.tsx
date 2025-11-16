import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Alert,
  Divider,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import DownloadIcon from '@mui/icons-material/Download';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';

interface StoryExportProps {
  state: ReturnType<typeof useStoryWriterState>;
}

const StoryExport: React.FC<StoryExportProps> = ({ state }) => {
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleCopyToClipboard = () => {
    if (state.storyContent) {
      navigator.clipboard.writeText(state.storyContent);
    }
  };

  const handleDownload = () => {
    if (state.storyContent) {
      const blob = new Blob([state.storyContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `story-${Date.now()}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  };

  const handleGenerateVideo = async () => {
    if (!state.enableVideoNarration) {
      setError('Story video generation is disabled in Story Setup.');
      return;
    }
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      setError('Please generate a structured outline first');
      return;
    }

    if (!state.sceneImages || state.sceneImages.size === 0) {
      setError('Please generate images for scenes first');
      return;
    }

    if (!state.sceneAudio || state.sceneAudio.size === 0) {
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
      <Typography variant="h5" gutterBottom sx={{ mb: 3, fontWeight: 600, color: '#1A1611' }}>
        Export Story
      </Typography>
      <Typography variant="body2" sx={{ mb: 4, color: '#5D4037' }}>
        Your story is complete! You can copy it to clipboard or download it as a text file.
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {!state.storyContent ? (
        <Alert severity="info">
          No story content available. Please complete the writing phase first.
        </Alert>
      ) : (
        <>
          {/* Story Summary */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
              Story Summary
            </Typography>
            <Box 
              sx={{ 
                p: 2, 
                borderRadius: 1,
                backgroundColor: '#FAF9F6', // Slightly lighter cream for summary box
              }}
            >
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Setting:</strong> {state.storySetting || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Characters:</strong> {state.characters || 'N/A'}
              </Typography>
              <Typography variant="body2" sx={{ mb: 1, color: '#2C2416' }}>
                <strong>Style:</strong> {state.writingStyle} | <strong>Tone:</strong> {state.storyTone}
              </Typography>
              <Typography variant="body2" sx={{ color: '#2C2416' }}>
                <strong>POV:</strong> {state.narrativePOV} | <strong>Audience:</strong> {state.audienceAgeGroup}
              </Typography>
            </Box>
          </Box>

          <Divider sx={{ my: 3 }} />

          {/* Premise */}
          {state.premise && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Premise
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={state.premise}
                InputProps={{ readOnly: true }}
                sx={{
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
            </Box>
          )}

          {/* Outline */}
          {state.outline && (
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Outline
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={6}
                value={state.outline}
                InputProps={{ readOnly: true }}
                sx={{
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
            </Box>
          )}

          {/* Story Content */}
          <Box sx={{ mb: 4 }}>
            <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
              Complete Story
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={20}
              value={state.storyContent}
              InputProps={{ readOnly: true }}
              sx={{
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
          </Box>

          {/* Video Generation */}
          {state.isOutlineStructured && state.outlineScenes && (
            state.enableVideoNarration ? (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" gutterBottom sx={{ color: '#1A1611' }}>
                Video Generation
              </Typography>
              <Alert severity="info" sx={{ mb: 2 }}>
                Generate a video from your story scenes with images and audio narration.
                {(!state.sceneImages || state.sceneImages.size === 0) && ' Generate images first.'}
                {(!state.sceneAudio || state.sceneAudio.size === 0) && ' Generate audio first.'}
              </Alert>
              
              {isGeneratingVideo && (
                <Box sx={{ mb: 2 }}>
                  <LinearProgress variant="determinate" value={videoProgress} sx={{ mb: 1 }} />
                  <Typography variant="body2" sx={{ color: '#5D4037' }}>
                    Generating video... {videoProgress}%
                  </Typography>
                </Box>
              )}

              {state.storyVideo && (
                <Box sx={{ mb: 2 }}>
                  <video
                    controls
                    src={storyWriterApi.getVideoUrl(state.storyVideo)}
                    style={{ width: '100%', maxHeight: '500px' }}
                  >
                    Your browser does not support the video element.
                  </video>
                  <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#5D4037' }}>
                    Generated story video
                  </Typography>
                </Box>
              )}

              <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
                <Button
                  variant="outlined"
                  startIcon={<VideoLibraryIcon />}
                  onClick={handleGenerateVideo}
                  disabled={
                    isGeneratingVideo ||
                    !state.outlineScenes ||
                    !state.sceneImages ||
                    state.sceneImages.size === 0 ||
                    !state.sceneAudio ||
                    state.sceneAudio.size === 0
                  }
                >
                  {isGeneratingVideo ? (
                    <>
                      <CircularProgress size={20} sx={{ mr: 1 }} />
                      Generating Video...
                    </>
                  ) : (
                    'Generate Video'
                  )}
                </Button>
                {state.storyVideo && (
                  <Button
                    variant="outlined"
                    startIcon={<DownloadIcon />}
                    onClick={handleDownloadVideo}
                  >
                    Download Video
                  </Button>
                )}
              </Box>
            </Box>
            ) : (
              <Alert severity="info" sx={{ mb: 4 }}>
                Story video generation is disabled in Story Setup. Enable it to create narrated videos.
              </Alert>
            )
          )}

          <Divider sx={{ my: 3 }} />

          {/* Export Actions */}
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end', flexWrap: 'wrap' }}>
            <Button variant="outlined" onClick={handleCopyToClipboard}>
              Copy to Clipboard
            </Button>
            <Button variant="contained" onClick={handleDownload}>
              Download as Text File
            </Button>
          </Box>
        </>
      )}
    </Paper>
  );
};

export default StoryExport;
