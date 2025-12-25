import { useCallback, useEffect, useRef, useState } from 'react';
import {
  youtubeApi,
  Scene,
  SceneVideoRenderRequest,
  TaskStatus,
  VideoPlan,
} from '../../../services/youtubeApi';

type SceneStatus = 'idle' | 'running' | 'completed' | 'failed';

interface SceneVideoState {
  status: SceneStatus;
  progress: number;
  taskId?: string;
  error?: string;
  videoUrl?: string;
}

interface UseYouTubeRenderQueueParams {
  scenes: Scene[];
  videoPlan: VideoPlan | null;
  resolution: '480p' | '720p' | '1080p';
  onScenesUpdate: (updated: Scene[]) => void;
  onError?: (msg: string) => void;
  onInfo?: (msg: string) => void;
  onSuccess?: (msg: string) => void;
}

interface UseYouTubeRenderQueueResult {
  sceneStatuses: Record<number, SceneVideoState>;
  finalVideoUrl: string | null;
  combining: boolean;
  combiningProgress: number;
  combiningMessage: string;
  runSceneVideo: (scene: Scene) => Promise<void>;
  combineVideos: () => Promise<void>;
}

const POLL_MS = 3000;

export function useYouTubeRenderQueue({
  scenes,
  videoPlan,
  resolution,
  onScenesUpdate,
  onError,
  onInfo,
  onSuccess,
}: UseYouTubeRenderQueueParams): UseYouTubeRenderQueueResult {
  const [sceneStatuses, setSceneStatuses] = useState<Record<number, SceneVideoState>>({});
  const [finalVideoUrl, setFinalVideoUrl] = useState<string | null>(null);
  const [combining, setCombining] = useState(false);
  const [combiningProgress, setCombiningProgress] = useState(0);
  const [combiningMessage, setCombiningMessage] = useState('Combining videos...');
  const pollingRefs = useRef<Map<string, NodeJS.Timeout>>(new Map());

  const updateSceneStatus = useCallback((sceneNumber: number, updates: Partial<SceneVideoState>) => {
    setSceneStatuses((prev) => ({
      ...prev,
      [sceneNumber]: {
        ...prev[sceneNumber],
        status: prev[sceneNumber]?.status || 'idle',
        progress: prev[sceneNumber]?.progress || 0,
        ...updates,
      },
    }));
  }, []);

  const clearPolling = useCallback((taskId: string) => {
    const timers = pollingRefs.current;
    timers.forEach((interval, key) => {
      if (key === taskId) {
        clearInterval(interval);
        timers.delete(key);
      }
    });
  }, []);

  useEffect(() => {
    return () => {
      pollingRefs.current.forEach((interval) => clearInterval(interval));
      pollingRefs.current.clear();
    };
  }, []);

  const pollTask = useCallback(
    (taskId: string, sceneNumber: number) => {
      const interval = setInterval(async () => {
        try {
          const status: TaskStatus = await youtubeApi.getRenderStatus(taskId);
          const progress = status.progress ?? 0;

          if (status.status === 'completed') {
            const videoUrl =
              status.result?.video_url ||
              status.result?.final_video_url ||
              status.result?.scene_results?.[0]?.video_url ||
              null;

            updateSceneStatus(sceneNumber, {
              status: 'completed',
              progress: 100,
              videoUrl: videoUrl || undefined,
              taskId,
              error: undefined,
            });

            if (videoUrl) {
              const updatedScenes = scenes.map((s) =>
                s.scene_number === sceneNumber ? { ...s, videoUrl } : s
              );
              onScenesUpdate(updatedScenes);
            }

            clearPolling(taskId);
          } else if (status.status === 'failed') {
            const errorMessage =
              status.error ||
              status.message ||
              status.result?.error ||
              'Video generation failed';
            updateSceneStatus(sceneNumber, {
              status: 'failed',
              progress,
              error: errorMessage,
              taskId,
            });
            clearPolling(taskId);
            onError?.(errorMessage);
          } else {
            updateSceneStatus(sceneNumber, {
              status: 'running',
              progress,
              taskId,
            });
          }
        } catch (err: any) {
          const msg = err?.message || 'Failed to poll render status';
          updateSceneStatus(sceneNumber, {
            status: 'failed',
            progress: 0,
            error: msg,
            taskId,
          });
          clearPolling(taskId);
          onError?.(msg);
        }
      }, POLL_MS);

      pollingRefs.current.set(taskId, interval);
    },
    [clearPolling, onError, onScenesUpdate, scenes, updateSceneStatus]
  );

  const runSceneVideo = useCallback(
    async (scene: Scene) => {
      if (!videoPlan) {
        onError?.('Video plan is missing');
        return;
      }
      const sn = scene.scene_number;
      const existing = sceneStatuses[sn];
      if (existing?.status === 'running') return;

      updateSceneStatus(sn, { status: 'running', progress: 5, error: undefined });

      const payload: SceneVideoRenderRequest = {
        scene,
        video_plan: videoPlan,
        resolution,
        generate_audio_enabled: false,
        voice_id: 'Wise_Woman',
      };

      try {
        const resp = await youtubeApi.generateSceneVideo(payload);
        if (resp.success && resp.task_id) {
          updateSceneStatus(sn, { status: 'running', progress: 5, taskId: resp.task_id });
          pollTask(resp.task_id, sn);
        } else {
          const msg = resp.message || 'Failed to start scene render';
          updateSceneStatus(sn, { status: 'failed', progress: 0, error: msg });
          onError?.(msg);
        }
      } catch (err: any) {
        const msg = err?.message || 'Failed to start scene render';
        updateSceneStatus(sn, { status: 'failed', progress: 0, error: msg });
        onError?.(msg);
      }
    },
    [pollTask, resolution, sceneStatuses, updateSceneStatus, videoPlan, onError]
  );

  const combineVideos = useCallback(async () => {
    const readyVideos = scenes
      .filter((s) => s.enabled !== false && s.videoUrl)
      .map((s) => s.videoUrl as string);

    if (readyVideos.length < 2) {
      onError?.('Need at least two scene videos to combine.');
      return;
    }

    setCombining(true);
    setCombiningProgress(5);
    setCombiningMessage('Starting combination...');

    try {
      const resp = await youtubeApi.combineVideos({
        scene_video_urls: readyVideos,
        video_plan: videoPlan || undefined,
        resolution,
      });

      if (!resp.success || !resp.task_id) {
        const msg = resp.message || 'Failed to start video combine';
        setCombining(false);
        setCombiningProgress(0);
        setCombiningMessage(msg);
        onError?.(msg);
        return;
      }

      const taskId = resp.task_id;
      let done = false;
      while (!done) {
        await new Promise((r) => setTimeout(r, POLL_MS));
        const status = await youtubeApi.getRenderStatus(taskId);
        const progress = status.progress ?? 0;
        setCombiningProgress(progress);
        setCombiningMessage(status.message || 'Combining...');

        if (status.status === 'completed') {
          const url = status.result?.video_url || status.result?.final_video_url;
          setFinalVideoUrl(url || null);
          setCombining(false);
          setCombiningProgress(100);
          setCombiningMessage('Combined successfully');
          onSuccess?.('Final video combined successfully');
          done = true;
        } else if (status.status === 'failed') {
          const msg = status.error || status.message || 'Combine failed';
          setCombining(false);
          setCombiningMessage(msg);
          onError?.(msg);
          done = true;
        }
      }
    } catch (err: any) {
      const msg = err?.message || 'Combine failed';
      setCombining(false);
      setCombiningMessage(msg);
      onError?.(msg);
    }
  }, [onError, resolution, scenes, videoPlan]);

  return {
    sceneStatuses,
    finalVideoUrl,
    combining,
    combiningProgress,
    combiningMessage,
    runSceneVideo,
    combineVideos,
  };
}

