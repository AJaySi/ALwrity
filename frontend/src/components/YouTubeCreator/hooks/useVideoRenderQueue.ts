import { useCallback, useEffect, useRef, useState } from 'react';
import { youtubeApi, Scene, VideoPlan, TaskStatus } from '../../../services/youtubeApi';

export type VideoJobStatus = 'idle' | 'running' | 'completed' | 'failed';

export interface SceneVideoJob {
  scene_number: number;
  status: VideoJobStatus;
  progress: number;
  taskId?: string;
  videoUrl?: string;
  error?: string;
}

interface UseVideoRenderQueueOptions {
  scenes: Scene[];
  videoPlan: VideoPlan | null;
  resolution: '480p' | '720p' | '1080p';
  onSceneVideoReady?: (sceneNumber: number, videoUrl: string) => void;
  onCombineReady?: (videoUrl: string) => void;
}

export const useVideoRenderQueue = ({
  scenes,
  videoPlan,
  resolution,
  onSceneVideoReady,
  onCombineReady,
}: UseVideoRenderQueueOptions) => {
  const [jobs, setJobs] = useState<Record<number, SceneVideoJob>>({});
  const [combineTaskId, setCombineTaskId] = useState<string | null>(null);
  const [combineProgress, setCombineProgress] = useState<number>(0);
  const [combineStatus, setCombineStatus] = useState<VideoJobStatus>('idle');
  const pollingRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Initialize jobs for current scenes
  useEffect(() => {
    setJobs((prev) => {
      const next = { ...prev };
      scenes.forEach((scene) => {
        const sn = scene.scene_number;
        if (!next[sn]) {
          next[sn] = {
            scene_number: sn,
            status: scene.videoUrl ? 'completed' : 'idle',
            progress: scene.videoUrl ? 100 : 0,
            videoUrl: scene.videoUrl,
          };
        } else if (scene.videoUrl && next[sn].videoUrl !== scene.videoUrl) {
          next[sn] = { ...next[sn], videoUrl: scene.videoUrl, status: 'completed', progress: 100 };
        }
      });
      return next;
    });
  }, [scenes]);

  const stopPolling = useCallback((taskId: string) => {
    const timer = pollingRef.current.get(taskId);
    if (timer) {
      clearInterval(timer);
      pollingRef.current.delete(taskId);
    }
  }, []);

  const pollTask = useCallback(
    (taskId: string, sceneNumber?: number, isCombine?: boolean) => {
      const timer = setInterval(async () => {
        try {
          const status: TaskStatus | null = await youtubeApi.getRenderStatus(taskId);
          
          // Handle null response (task not found) - matches podcast pattern
          if (!status) {
            console.debug(`[VideoRenderQueue] Task ${taskId} not found, stopping poll`);
            stopPolling(taskId);
            if (sceneNumber !== undefined) {
              setJobs((prev) => ({
                ...prev,
                [sceneNumber]: {
                  ...(prev[sceneNumber] || { scene_number: sceneNumber }),
                  status: 'failed',
                  progress: 0,
                  error: 'Task expired or not found. Please try again.',
                },
              }));
            } else {
              setCombineStatus('failed');
            }
            return; // Don't process further for null responses
          }
          
          const progress = status.progress ?? 0;

          if (isCombine) {
            setCombineProgress(progress);
          } else if (sceneNumber !== undefined) {
            setJobs((prev) => ({
              ...prev,
              [sceneNumber]: {
                ...(prev[sceneNumber] || { scene_number: sceneNumber, status: 'running', progress }),
                status: status.status === 'failed' ? 'failed' : status.status === 'completed' ? 'completed' : 'running',
                progress,
              },
            }));
          }

          if (status.status === 'completed') {
            stopPolling(taskId);
            const result = status.result || {};

            if (isCombine) {
              const finalUrl = result.final_video_url || result.video_url;
              if (finalUrl && onCombineReady) {
                onCombineReady(finalUrl);
              }
              setCombineStatus('completed');
            } else if (sceneNumber !== undefined) {
              const videoUrl =
                result.final_video_url ||
                result.video_url ||
                (Array.isArray(result.scene_results) && result.scene_results[0]?.video_url);
              if (videoUrl && onSceneVideoReady) {
                onSceneVideoReady(sceneNumber, videoUrl);
              }
              setJobs((prev) => ({
                ...prev,
                [sceneNumber]: {
                  ...(prev[sceneNumber] || { scene_number: sceneNumber }),
                  status: 'completed',
                  progress: 100,
                  videoUrl,
                },
              }));
            }
          } else if (status.status === 'failed') {
            stopPolling(taskId);
            const errorMsg = status.error || status.message || 'Video render failed';
            if (isCombine) {
              setCombineStatus('failed');
            } else if (sceneNumber !== undefined) {
              setJobs((prev) => ({
                ...prev,
                [sceneNumber]: {
                  ...(prev[sceneNumber] || { scene_number: sceneNumber }),
                  status: 'failed',
                  progress: 0,
                  error: errorMsg,
                },
              }));
            }
          }
        } catch (err: any) {
          // Check if this is a 404 (task not found) - stop polling silently
          const isNotFound = err?.response?.status === 404 || err?.status === 404 || 
                             err?.message?.toLowerCase().includes('not found') ||
                             err?.response?.data?.error === 'Task not found';
          
          if (isNotFound) {
            // Task not found (expired/cleaned up) - stop polling silently
            console.debug(`[VideoRenderQueue] Task ${taskId} not found, stopping poll`);
            stopPolling(taskId);
            if (sceneNumber !== undefined) {
              setJobs((prev) => ({
                ...prev,
                [sceneNumber]: {
                  ...(prev[sceneNumber] || { scene_number: sceneNumber }),
                  status: 'failed',
                  progress: 0,
                  error: 'Task expired or not found. Please try again.',
                },
              }));
            } else {
              setCombineStatus('failed');
            }
            return; // Don't process further for expected 404s
          }
          
          // Other errors - handle normally
          stopPolling(taskId);
          if (sceneNumber !== undefined) {
            setJobs((prev) => ({
              ...prev,
              [sceneNumber]: {
                ...(prev[sceneNumber] || { scene_number: sceneNumber }),
                status: 'failed',
                progress: 0,
                error: err instanceof Error ? err.message : 'Video render failed',
              },
            }));
          } else {
            setCombineStatus('failed');
          }
        }
      }, 3000);

      pollingRef.current.set(taskId, timer);
    },
    [onCombineReady, onSceneVideoReady, stopPolling]
  );

  const runSceneVideo = useCallback(
    async (scene: Scene, opts?: { generateAudio?: boolean }) => {
      if (!videoPlan) {
        throw new Error('Video plan is missing');
      }
      if (!scene.imageUrl) throw new Error('Scene image is required before video generation.');
      if (!scene.audioUrl && !opts?.generateAudio) throw new Error('Scene audio is required before video generation.');

      const sn = scene.scene_number;
      setJobs((prev) => ({
        ...prev,
        [sn]: { scene_number: sn, status: 'running', progress: 5 },
      }));

      const resp = await youtubeApi.generateSceneVideo({
        scene,
        video_plan: videoPlan,
        resolution,
        generate_audio_enabled: Boolean(opts?.generateAudio),
      });

      if (resp.success && resp.task_id) {
        setJobs((prev) => ({
          ...prev,
          [sn]: { ...(prev[sn] || { scene_number: sn }), status: 'running', taskId: resp.task_id, progress: 5 },
        }));
        pollTask(resp.task_id, sn, false);
      } else {
        setJobs((prev) => ({
          ...prev,
          [sn]: { scene_number: sn, status: 'failed', progress: 0, error: resp.message },
        }));
        throw new Error(resp.message || 'Failed to start scene video render');
      }
    },
    [videoPlan, resolution, pollTask]
  );

  const combineVideos = useCallback(
    async (videoUrls: string[], title?: string) => {
      if (!videoUrls || videoUrls.length < 2) {
        throw new Error('At least two scene videos are required to combine.');
      }
      setCombineStatus('running');
      setCombineProgress(5);
      const resp = await youtubeApi.combineVideos({
        scene_video_urls: videoUrls,
        resolution,
        title,
      });
      if (resp.success && resp.task_id) {
        setCombineTaskId(resp.task_id);
        setCombineProgress(10);
        pollTask(resp.task_id, undefined, true);
      } else {
        setCombineStatus('failed');
        throw new Error(resp.message || 'Failed to start combine task');
      }
    },
    [pollTask, resolution]
  );

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      pollingRef.current.forEach((timer) => clearInterval(timer));
      pollingRef.current.clear();
    };
  }, []);

  return {
    jobs,
    runSceneVideo,
    combineVideos,
    combineTaskId,
    combineProgress,
    combineStatus,
  };
};

