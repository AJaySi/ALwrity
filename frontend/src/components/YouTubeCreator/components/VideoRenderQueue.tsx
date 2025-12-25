import React, { useMemo } from 'react';
import { Box, Paper, Stack, Typography, Button, LinearProgress, Alert, Chip } from '@mui/material';
import { PlayArrow, VideoLibrary, CheckCircle, ErrorOutline } from '@mui/icons-material';
import { Scene, VideoPlan } from '../../../services/youtubeApi';
import { useVideoRenderQueue, SceneVideoJob } from '../hooks/useVideoRenderQueue';

interface VideoRenderQueueProps {
  scenes: Scene[];
  videoPlan: VideoPlan | null;
  resolution: '480p' | '720p' | '1080p';
  onSceneVideoReady: (sceneNumber: number, videoUrl: string) => void;
  onFinalVideoReady?: (videoUrl: string) => void;
}

const statusColor = (job?: SceneVideoJob) => {
  if (!job) return 'default';
  if (job.status === 'completed') return 'success';
  if (job.status === 'failed') return 'error';
  if (job.status === 'running') return 'info';
  return 'default';
};

export const VideoRenderQueue: React.FC<VideoRenderQueueProps> = ({
  scenes,
  videoPlan,
  resolution,
  onSceneVideoReady,
  onFinalVideoReady,
}) => {
  const {
    jobs,
    runSceneVideo,
    combineVideos,
    combineStatus,
    combineProgress,
  } = useVideoRenderQueue({
    scenes,
    videoPlan,
    resolution,
    onSceneVideoReady,
    onCombineReady: onFinalVideoReady,
  });

  const allVideosReady = useMemo(() => {
    const enabled = scenes.filter((s) => s.enabled !== false);
    if (enabled.length === 0) return false;
    return enabled.every((s) => jobs[s.scene_number]?.videoUrl);
  }, [jobs, scenes]);

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>
        Scene-wise Video Generation
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Generate videos per scene to save costs and retry only failing scenes. Once all scene videos are ready, combine them into a final video.
      </Typography>

      <Stack spacing={2}>
        {scenes.map((scene) => {
          const job = jobs[scene.scene_number];
          return (
            <Paper key={scene.scene_number} variant="outlined" sx={{ p: 2 }}>
              <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2} flexWrap="wrap">
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                    Scene {scene.scene_number}: {scene.title}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {scene.imageUrl ? '✅ Image ready' : '⚠️ Image missing'} · {scene.audioUrl ? '✅ Audio ready' : '⚠️ Audio missing'}
                  </Typography>
                  {job?.error && (
                    <Alert severity="error" sx={{ mt: 1 }}>
                      {job.error}
                    </Alert>
                  )}
                </Box>
                <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                  <Chip
                    label={job?.status ?? 'idle'}
                    color={statusColor(job) as any}
                    size="small"
                    variant="outlined"
                  />
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<PlayArrow />}
                    disabled={job?.status === 'running'}
                    onClick={() => runSceneVideo(scene, { generateAudio: false }).catch(() => {})}
                  >
                    {job?.status === 'running'
                      ? 'Generating...'
                      : job?.status === 'completed'
                      ? 'Regenerate Video'
                      : 'Generate Video'}
                  </Button>
                  {job?.videoUrl && (
                    <Button
                      variant="outlined"
                      size="small"
                      href={job.videoUrl}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Preview
                    </Button>
                  )}
                </Stack>
              </Stack>
              {job?.status === 'running' && (
                <Box sx={{ mt: 1.5 }}>
                  <LinearProgress variant="determinate" value={job.progress || 0} sx={{ height: 6, borderRadius: 2 }} />
                  <Typography variant="caption" color="text.secondary">
                    {Math.round(job.progress || 0)}%
                  </Typography>
                </Box>
              )}
            </Paper>
          );
        })}
      </Stack>

      <Box sx={{ mt: 3, p: 2, border: '1px solid #e5e7eb', borderRadius: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
          Final Video
        </Typography>
        {!allVideosReady && (
          <Alert severity="info" icon={<VideoLibrary />}>
            Generate videos for all enabled scenes to combine them into a single final video.
          </Alert>
        )}
        {allVideosReady && (
          <Stack spacing={1}>
            <Typography variant="body2" color="text.secondary">
              All scene videos are ready. Combine into a final video.
            </Typography>
            {combineStatus === 'running' && (
              <Box>
                <LinearProgress
                  variant="determinate"
                  value={combineProgress || 0}
                  sx={{ height: 6, borderRadius: 2, mb: 0.5 }}
                />
                <Typography variant="caption" color="text.secondary">
                  {Math.round(combineProgress || 0)}%
                </Typography>
              </Box>
            )}
            <Stack direction="row" spacing={1} alignItems="center">
              <Button
                variant="contained"
                color="secondary"
                startIcon={<VideoLibrary />}
                disabled={combineStatus === 'running'}
                onClick={() =>
                  combineVideos(
                    scenes
                      .filter((s) => s.enabled !== false)
                      .map((s) => jobs[s.scene_number]?.videoUrl)
                      .filter(Boolean) as string[],
                    videoPlan?.video_summary
                  ).catch(() => {})
                }
              >
                {combineStatus === 'running' ? 'Combining...' : 'Combine Scenes'}
              </Button>
              {combineStatus === 'completed' && <Chip icon={<CheckCircle />} color="success" label="Final video ready" />}
              {combineStatus === 'failed' && (
                <Chip icon={<ErrorOutline />} color="error" label="Combine failed, retry" />
              )}
            </Stack>
          </Stack>
        )}
      </Box>
    </Paper>
  );
};

