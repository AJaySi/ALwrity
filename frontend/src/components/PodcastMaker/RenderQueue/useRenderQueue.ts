import { useState, useEffect, useRef, useCallback } from "react";
import { Script, Knobs, Job, RenderJobResult, TaskStatus } from "../types";
import { podcastApi } from "../../../services/podcastApi";

interface UseRenderQueueProps {
  script: Script;
  jobs: Job[];
  knobs: Knobs;
  projectId: string;
  budgetCap?: number;
  avatarImageUrl?: string | null;
  onUpdateJob: (sceneId: string, updates: Partial<Job>) => void;
  onUpdateScript?: (script: Script) => void;
  onError: (message: string) => void;
}

const getSceneVoiceEmotion = (knobs: Knobs) => knobs.voice_emotion || "neutral";

export const useRenderQueue = ({
  script,
  jobs,
  knobs,
  projectId,
  budgetCap,
  avatarImageUrl,
  onUpdateJob,
  onUpdateScript,
  onError,
}: UseRenderQueueProps) => {
  const [rendering, setRendering] = useState<string | null>(null);
  const [generatingImage, setGeneratingImage] = useState<string | null>(null);
  const [combiningAudio, setCombiningAudio] = useState(false);
  const [combinedAudioResult, setCombinedAudioResult] = useState<{
    url: string;
    filename: string;
    duration: number;
    sceneCount: number;
  } | null>(null);
  const pollingIntervals = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Cleanup polling intervals on unmount
  useEffect(() => {
    const intervals = pollingIntervals.current;
    return () => {
      intervals.forEach((interval) => clearInterval(interval));
      intervals.clear();
    };
  }, []);

  // Initialize jobs if empty
  useEffect(() => {
    if (jobs.length === 0 && script.scenes.length > 0) {
      const initialJobs: Job[] = script.scenes.map((s) => {
        const hasExistingAudio = Boolean(s.audioUrl);
        return {
          sceneId: s.id,
          title: s.title,
          status: hasExistingAudio ? ("completed" as const) : ("idle" as const),
          progress: hasExistingAudio ? 100 : 0,
          previewUrl: null,
          finalUrl: hasExistingAudio ? s.audioUrl || null : null,
          imageUrl: s.imageUrl || null, // Include existing imageUrl from scene
          jobId: null,
        };
      });
      initialJobs.forEach((job) => {
        onUpdateJob(job.sceneId, job);
      });
    }
  }, [script.scenes.length, jobs.length, onUpdateJob, script.scenes]);

  const getScene = useCallback((sceneId: string) => script.scenes.find((s) => s.id === sceneId), [script.scenes]);

  const pollTaskStatus = useCallback(async (taskId: string, sceneId: string) => {
    try {
      const status: TaskStatus = await podcastApi.pollTaskStatus(taskId);

      onUpdateJob(sceneId, {
        progress: status.progress ?? 0,
        status: status.status === "completed" ? "completed" : status.status === "failed" ? "failed" : "running",
      });

      if (status.status === "completed" && status.result) {
        const result = status.result;
        onUpdateJob(sceneId, {
          status: "completed",
          progress: 100,
          videoUrl: result.video_url,
          cost: result.cost,
        });

        const interval = pollingIntervals.current.get(sceneId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(sceneId);
        }
      } else if (status.status === "failed") {
        onUpdateJob(sceneId, { status: "failed", progress: 0 });
        const interval = pollingIntervals.current.get(sceneId);
        if (interval) {
          clearInterval(interval);
          pollingIntervals.current.delete(sceneId);
        }
        onError(status.error || "Video generation failed");
      }

      return status.status === "completed" || status.status === "failed";
    } catch (error) {
      console.error("Error polling task status:", error);
      return false;
    }
  }, [onUpdateJob, onError]);

  const startPolling = useCallback((taskId: string, sceneId: string) => {
    const existingInterval = pollingIntervals.current.get(sceneId);
    if (existingInterval) {
      clearInterval(existingInterval);
    }

    const interval = setInterval(async () => {
      const isComplete = await pollTaskStatus(taskId, sceneId);
      if (isComplete) {
        clearInterval(interval);
        pollingIntervals.current.delete(sceneId);
      }
    }, 3000);

    pollingIntervals.current.set(sceneId, interval);
  }, [pollTaskStatus]);

  const runRender = useCallback(async (sceneId: string, mode: "preview" | "full") => {
    if (rendering && rendering !== sceneId) return;
    const job = jobs.find((j) => j.sceneId === sceneId);
    if (job && job.status !== "idle") return;
    const scene = getScene(sceneId);
    if (!scene) return;

    const textLength = scene.lines.map((l) => l.text).join(" ").length;
    const estimatedCost = (textLength / 1000) * 0.05;

    if (budgetCap && budgetCap > 0) {
      const currentSpent = jobs
        .filter((j) => j.status === "completed" && j.cost)
        .reduce((sum, j) => sum + (j.cost || 0), 0);

      if (currentSpent + estimatedCost > budgetCap) {
        onError(`Budget cap exceeded. Estimated cost: $${estimatedCost.toFixed(4)}, Budget remaining: $${(budgetCap - currentSpent).toFixed(2)}`);
        return;
      }
    }

    setRendering(sceneId);
    onUpdateJob(sceneId, {
      status: mode === "preview" ? "previewing" : "running",
      progress: mode === "preview" ? 25 : 40,
    });

    try {
      const result: RenderJobResult = await podcastApi.renderSceneAudio({
        scene,
        voiceId: "Wise_Woman",
        emotion: scene.emotion || getSceneVoiceEmotion(knobs),
        speed: knobs.voice_speed,
      });

      const updates: Partial<Job> = {
        status: "completed",
        progress: 100,
        cost: result.cost,
        provider: result.provider,
        voiceId: result.voiceId,
        fileSize: result.fileSize,
      };

      if (mode === "preview") {
        updates.previewUrl = result.audioUrl;
        window.open(result.audioUrl, "_blank");
      } else {
        updates.finalUrl = result.audioUrl;
        try {
          await podcastApi.saveAudioToAssetLibrary({
            audioUrl: result.audioUrl,
            filename: result.audioFilename,
            title: `${scene.title} - ${projectId}`,
            description: `Podcast episode scene audio: ${scene.title}`,
            projectId,
            sceneId,
            cost: result.cost,
            provider: result.provider,
            model: result.model,
            fileSize: result.fileSize,
          });
        } catch (assetError) {
          console.error("Failed to save to asset library:", assetError);
        }
      }

      onUpdateJob(sceneId, updates);
    } catch (error) {
      onUpdateJob(sceneId, { status: "failed", progress: 0 });
      const message = error instanceof Error ? error.message : "Render failed";
      onError(message);
    } finally {
      setRendering(null);
    }
  }, [rendering, jobs, getScene, knobs, budgetCap, projectId, onUpdateJob, onError]);

  const runImageGeneration = useCallback(async (sceneId: string) => {
    if (generatingImage && generatingImage !== sceneId) return;
    const scene = getScene(sceneId);
    if (!scene) return;

    setGeneratingImage(sceneId);
    try {
      const sceneContent = scene.lines.map((line) => line.text).join(" ");
      const result = await podcastApi.generateSceneImage({
        sceneId: scene.id,
        sceneTitle: scene.title,
        sceneContent: sceneContent,
        width: 1024,
        height: 1024,
      });

      // Update job with image URL
      onUpdateJob(sceneId, {
        imageUrl: result.image_url,
      });

      // Also update the scene's imageUrl so it persists
      if (onUpdateScript) {
        const updatedScenes = script.scenes.map((s) =>
          s.id === sceneId ? { ...s, imageUrl: result.image_url } : s
        );
        onUpdateScript({ ...script, scenes: updatedScenes });
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Image generation failed";
      onError(message);
    } finally {
      setGeneratingImage(null);
    }
  }, [generatingImage, getScene, onUpdateJob, onError]);

  const runVideoRender = useCallback(async (sceneId: string) => {
    if (rendering && rendering !== sceneId) return;
    const scene = getScene(sceneId);
    if (!scene) return;

    const sceneImageUrl = scene.imageUrl || avatarImageUrl;
    if (!sceneImageUrl) {
      onError("Scene image is required for video generation. Please generate images for scenes first.");
      return;
    }

    const job = jobs.find((j) => j.sceneId === sceneId);
    if (!job?.finalUrl) {
      onError("Please generate audio first before creating video.");
      return;
    }

    const estimatedCost = 0.30;
    if (budgetCap && budgetCap > 0) {
      const currentSpent = jobs
        .filter((j) => j.status === "completed" && j.cost)
        .reduce((sum, j) => sum + (j.cost || 0), 0);

      if (currentSpent + estimatedCost > budgetCap) {
        onError(`Budget cap exceeded. Estimated cost: $${estimatedCost.toFixed(2)}, Budget remaining: $${(budgetCap - currentSpent).toFixed(2)}`);
        return;
      }
    }

    setRendering(sceneId);
    onUpdateJob(sceneId, {
      status: "running",
      progress: 5,
    });

    try {
      const result = await podcastApi.generateVideo({
        projectId,
        sceneId,
        sceneTitle: scene.title,
        audioUrl: job.finalUrl,
        avatarImageUrl: sceneImageUrl,
        resolution: knobs.resolution || "720p",
      });

      onUpdateJob(sceneId, {
        taskId: result.taskId,
        status: "running",
        progress: 5,
      });

      startPolling(result.taskId, sceneId);
    } catch (error) {
      onUpdateJob(sceneId, { status: "failed", progress: 0 });
      const message = error instanceof Error ? error.message : "Video generation failed";
      onError(message);
    } finally {
      setRendering(null);
    }
  }, [rendering, getScene, avatarImageUrl, jobs, budgetCap, projectId, knobs, onUpdateJob, onError, startPolling]);

  const combineAudio = useCallback(async () => {
    try {
      setCombiningAudio(true);

      const sceneIds: string[] = [];
      const sceneAudioUrls: string[] = [];

      script.scenes.forEach((scene) => {
        if (scene.audioUrl) {
          // Ensure we're using the correct URL format (not blob URLs)
          const audioUrl = scene.audioUrl.startsWith('blob:') ? '' : scene.audioUrl;
          if (audioUrl) {
            sceneIds.push(scene.id);
            sceneAudioUrls.push(audioUrl);
          }
        }
      });

      jobs.forEach((job) => {
        // Prefer finalUrl over previewUrl, and ensure it's not a blob URL
        const audioUrl = job.finalUrl || job.previewUrl;
        if (audioUrl && !audioUrl.startsWith('blob:') && !sceneAudioUrls.includes(audioUrl)) {
          sceneIds.push(job.sceneId);
          sceneAudioUrls.push(audioUrl);
        }
      });

      if (sceneIds.length === 0) {
        onError("No audio files found to combine.");
        return;
      }

      const result = await podcastApi.combineAudio({
        projectId,
        sceneIds,
        sceneAudioUrls,
      });

      // Store combined audio result for preview
      setCombinedAudioResult({
        url: result.combined_audio_url,
        filename: result.combined_audio_filename,
        duration: result.total_duration,
        sceneCount: result.scene_count,
      });

      // Auto-download the combined audio
      const link = document.createElement("a");
      link.href = result.combined_audio_url;
      link.download = `podcast-episode-${projectId.slice(-8)}.mp3`;
      link.click();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to combine audio";
      onError(`Failed to combine audio: ${message}`);
    } finally {
      setCombiningAudio(false);
    }
  }, [script.scenes, jobs, projectId, onError]);

  return {
    rendering,
    generatingImage,
    combiningAudio,
    combinedAudioResult,
    isBusy: Boolean(rendering),
    runRender,
    runImageGeneration,
    runVideoRender,
    combineAudio,
  };
};

