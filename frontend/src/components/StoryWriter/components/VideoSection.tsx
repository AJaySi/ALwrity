import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  LinearProgress,
  CircularProgress,
  Chip,
  Alert,
} from '@mui/material';
import VideoLibraryIcon from '@mui/icons-material/VideoLibrary';
import DownloadIcon from '@mui/icons-material/Download';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { useStoryWriterState } from '../../../hooks/useStoryWriterState';
import { storyWriterApi } from '../../../services/storyWriterApi';
import { triggerSubscriptionError } from '../../../api/client';
import { fetchMediaBlobUrl } from '../../../utils/fetchMediaBlobUrl';
import { HdVideoSection } from './HdVideoSection';

interface VideoSectionProps {
  state: ReturnType<typeof useStoryWriterState>;
  error: string | null;
  onError: (error: string | null) => void;
}

export const VideoSection: React.FC<VideoSectionProps> = ({ state, error, onError }) => {
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false);
  const [videoProgress, setVideoProgress] = useState(0);
  const [videoMessage, setVideoMessage] = useState<string>('');
  const [videoBlobUrl, setVideoBlobUrl] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const hasScenes = state.isOutlineStructured && state.outlineScenes && state.outlineScenes.length > 0;
  const videoEnabled = state.enableVideoNarration;
  const hasVideo = videoEnabled && !!state.storyVideo;
  const hasImages = state.sceneImages && state.sceneImages.size > 0;
  const hasAudio = state.enableNarration && state.sceneAudio && state.sceneAudio.size > 0;
  const canGenerateVideo = hasScenes && hasImages && hasAudio && !isGeneratingVideo;

  // Load video blob URL when storyVideo changes
  useEffect(() => {
    if (state.storyVideo) {
      fetchMediaBlobUrl(state.storyVideo).then(setVideoBlobUrl);
    } else {
      if (videoBlobUrl) {
        URL.revokeObjectURL(videoBlobUrl);
        setVideoBlobUrl(null);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.storyVideo]);

  const handleGenerateVideo = async () => {
    if (!state.outlineScenes || state.outlineScenes.length === 0) {
      onError('Please generate a structured outline first');
      return;
    }
    if (!videoEnabled) {
      onError('Story video feature is disabled in Story Setup.');
      return;
    }

    if (!hasImages) {
      onError('Please generate images for scenes first');
      return;
    }

    if (!hasAudio) {
      onError('Please generate audio for scenes first');
      return;
    }

    setIsGeneratingVideo(true);
    onError(null);
    setVideoProgress(0);
    setVideoMessage('');

    try {
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

      const start = await storyWriterApi.generateStoryVideoAsync({
        scenes: scenes,
        image_urls: imageUrls,
        audio_urls: audioUrls,
        story_title: state.storySetting || 'Story',
        fps: state.videoFps,
        transition_duration: state.videoTransitionDuration,
      });
      setVideoMessage(start.message || 'Starting video generation...');

      const taskId = start.task_id;
      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, 1200));
        const status = await storyWriterApi.getTaskStatus(taskId);
        setVideoProgress(Math.round(status.progress ?? 0));
        if (status.message) setVideoMessage(status.message);
        if (status.status === 'completed') {
          done = true;
          const result = await storyWriterApi.getTaskResult(taskId);
          const video = (result as any).video || (result as any)?.result?.video;
          const finalUrl: string | undefined = video?.video_url;
          if (!finalUrl) throw new Error('Video URL not found in result');
          state.setStoryVideo(finalUrl);
          const blobUrl = await fetchMediaBlobUrl(finalUrl);
          setVideoBlobUrl(blobUrl);
          setVideoProgress(100);
          setVideoMessage('Video generation complete');
          state.setError(null);
          setTimeout(() => {
            const v = videoRef.current;
            if (v) {
              try { v.play().catch(() => {}); } catch {}
              try { if (v.requestFullscreen) v.requestFullscreen(); } catch {}
            }
          }, 300);
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Video generation failed');
        }
      }
    } catch (err: any) {
      console.error('Video generation failed:', err);

      const status = err?.response?.status;
      if (status === 429 || status === 402) {
        const handled = await triggerSubscriptionError(err);
        if (handled) {
          setIsGeneratingVideo(false);
          return;
        }
      }

      const errorMessage = err.response?.data?.detail || err.message || 'Failed to generate video';
      onError(errorMessage);
      state.setError(errorMessage);
    } finally {
      setIsGeneratingVideo(false);
    }
  };

  const handleDownloadVideo = async () => {
    if (state.storyVideo) {
      const blobUrl = await fetchMediaBlobUrl(state.storyVideo);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `story-video-${Date.now()}.mp4`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    }
  };

  if (!videoEnabled) {
    return (
      <Alert severity="info">
        Story video generation is disabled in Story Setup. Enable it to create narrative videos.
      </Alert>
    );
  }

  return (
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
            {videoMessage || 'Generating video... This may take a few minutes.'}
          </Typography>
        </Box>
      )}

      {hasVideo && state.storyVideo && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="body2" sx={{ color: '#5D4037', mb: 1, fontSize: '0.875rem' }}>
            Video ready! Preview and download below.
          </Typography>
          <Box sx={{ mt: 0 }}>
            <video
              ref={videoRef}
              controls
              src={videoBlobUrl ?? undefined}
              style={{
                width: '100%',
                maxWidth: '600px',
                borderRadius: 8,
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              }}
            >
              Your browser does not support the video tag.
            </video>
            <HdVideoSection state={state} error={error} onError={onError} />
          </Box>
        </Box>
      )}
    </Box>
  );
};

