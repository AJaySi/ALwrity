import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from "react";
import { Script, Knobs, Scene, PodcastMode } from "../types";
import { podcastApi } from "../../../services/podcastApi";

interface ScriptEditorContextType {
  // State
  script: Script | null;
  loading: boolean;
  error: string | null;
  podcastMode: PodcastMode;
  approvingSceneId: string | null;
  generatingAudioId: string | null;
  showScriptFormatInfo: boolean;
  combiningAudio: boolean;
  scriptTab: "audio" | "video";
  combinedAudioResult: { url: string; filename: string; duration: number; sceneCount: number } | null;
  generatingBatchAudio: boolean;
  batchAudioProgress: { completed: number; total: number } | null;
  generatingChartId: string | null; // B-roll: generating chart preview
  
  // Computed
  activeScript: Script | null;
  allApproved: boolean | null;
  approvedCount: number;
  totalScenes: number;
  allScenesHaveAudio: boolean | null;
  scenesWithAudio: number;
  allScenesHaveAudioAndImages: boolean | null;
  needsAudioGeneration: boolean | null;
  scenesWithCharts: number; // B-roll: count of scenes with chart data
  
  // Setters for UI state
  setScript: React.Dispatch<React.SetStateAction<Script | null>>;
  setLoading: React.Dispatch<React.SetStateAction<boolean>>;
  setError: React.Dispatch<React.SetStateAction<string | null>>;
  setApprovingSceneId: React.Dispatch<React.SetStateAction<string | null>>;
  setGeneratingAudioId: React.Dispatch<React.SetStateAction<string | null>>;
  setShowScriptFormatInfo: React.Dispatch<React.SetStateAction<boolean>>;
  setCombiningAudio: React.Dispatch<React.SetStateAction<boolean>>;
  setScriptTab: React.Dispatch<React.SetStateAction<"audio" | "video">>;
  setCombinedAudioResult: React.Dispatch<React.SetStateAction<{ url: string; filename: string; duration: number; sceneCount: number } | null>>;
  setGeneratingBatchAudio: React.Dispatch<React.SetStateAction<boolean>>;
  setBatchAudioProgress: React.Dispatch<React.SetStateAction<{ completed: number; total: number } | null>>;
  setGeneratingChartId: React.Dispatch<React.SetStateAction<string | null>>;
  
  // Actions
  updateScene: (updated: Scene) => void;
  approveScene: (sceneId: string) => Promise<void>;
  deleteScene: (sceneId: string) => void;
  generateAllAudio: () => Promise<void>;
  combineAudio: () => Promise<void>;
  emitScriptChange: (next: Script) => void;
  // B-roll actions
  generateChartPreviews: () => Promise<void>;
  regenerateChart: (sceneId: string) => Promise<void>;
  removeChart: (sceneId: string) => void;
}

const ScriptEditorContext = createContext<ScriptEditorContextType | undefined>(undefined);

interface ScriptEditorProviderProps {
  children: ReactNode;
  projectId: string;
  idea: string;
  rawResearch: any;
  knobs: Knobs;
  speakers: number;
  durationMinutes: number;
  initialScript: Script | null;
  initialAudioScript?: Script | null;
  initialVideoScript?: Script | null;
  podcastMode?: PodcastMode;
  analysis?: any;
  outline?: any;
  onScriptChange: (script: Script) => void;
  onError: (message: string) => void;
}

export const ScriptEditorProvider: React.FC<ScriptEditorProviderProps> = ({
  children,
  projectId,
  idea,
  rawResearch,
  knobs,
  speakers,
  durationMinutes,
  initialScript,
  initialAudioScript,
  initialVideoScript,
  podcastMode = "video_only",
  analysis,
  outline,
  onScriptChange,
  onError,
}) => {
  // Core state
  const [script, setScript] = useState<Script | null>(initialScript);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // UI state
  const [approvingSceneId, setApprovingSceneId] = useState<string | null>(null);
  const [generatingAudioId, setGeneratingAudioId] = useState<string | null>(null);
  const [showScriptFormatInfo, setShowScriptFormatInfo] = useState(false);
  const [combiningAudio, setCombiningAudio] = useState(false);
  const [scriptTab, setScriptTab] = useState<"audio" | "video">("video");
  const [combinedAudioResult, setCombinedAudioResult] = useState<{
    url: string;
    filename: string;
    duration: number;
    sceneCount: number;
  } | null>(null);
  const [generatingBatchAudio, setGeneratingBatchAudio] = useState(false);
  const [batchAudioProgress, setBatchAudioProgress] = useState<{ completed: number; total: number } | null>(null);
  const [generatingChartId, setGeneratingChartId] = useState<string | null>(null);

  // Emit script changes to parent (deferred to avoid setState during render)
  const emitScriptChange = useCallback(
    (next: Script) => {
      Promise.resolve().then(() => onScriptChange(next));
    },
    [onScriptChange]
  );

  // Determine which script to display based on mode and tab
  const getActiveScript = (): Script | null => {
    const currentScript = script || null;
    
    if (podcastMode === "audio_only") {
      if (currentScript?.audioScript) {
        return { scenes: currentScript.audioScript };
      }
      return initialAudioScript || null;
    }
    
    if (podcastMode === "video_only") {
      return currentScript || initialVideoScript || null;
    }
    
    if (podcastMode === "audio_video") {
      if (scriptTab === "audio") {
        if (currentScript?.audioScript) {
          return { scenes: currentScript.audioScript };
        }
        return initialAudioScript || null;
      } else {
        if (currentScript?.videoScript) {
          return { scenes: currentScript.videoScript };
        }
        return currentScript || initialVideoScript || null;
      }
    }
    
    return currentScript || initialVideoScript || null;
  };

  const activeScript = getActiveScript();

  // Computed values
  const allApproved = activeScript && activeScript.scenes.every((s) => s.approved);
  const approvedCount = activeScript ? activeScript.scenes.filter((s) => s.approved).length : 0;
  const totalScenes = activeScript ? activeScript.scenes.length : 0;
  const allScenesHaveAudio = activeScript && activeScript.scenes.every((s) => s.audioUrl);
  const scenesWithAudio = activeScript ? activeScript.scenes.filter((s) => s.audioUrl).length : 0;
  const allScenesHaveAudioAndImages = activeScript && (
    podcastMode === "audio_only" 
      ? activeScript.scenes.every((s) => s.audioUrl)
      : activeScript.scenes.every((s) => s.audioUrl && s.imageUrl)
  );
  const needsAudioGeneration = activeScript && !allScenesHaveAudio && activeScript.scenes.some((s) => !s.audioUrl);
  
  // B-roll computed
  const scenesWithCharts = activeScript ? activeScript.scenes.filter((s) => s.chart_data && Object.keys(s.chart_data).length > 0).length : 0;

  // Sync with parent state
  useEffect(() => {
    if (initialScript) {
      setScript(initialScript);
    }
  }, [initialScript]);

  // Generate script effect - only if not already generated by parent
  // This prevents duplicate API calls when both parent workflow and this component try to generate
  useEffect(() => {
    // Skip if parent already provided script via props
    if (script || initialScript) {
      return;
    }

    if (!rawResearch) {
      return;
    }
    
    // Skip if podcastMode is audio_only (script should be passed from parent for audio_only)
    // Parent workflow already generates the script, we just display it here
    if (podcastMode === "audio_only") {
      return;
    }

    let mounted = true;
    setLoading(true);
    setError(null);
    podcastApi
      .generateScript({
        projectId,
        idea,
        research: rawResearch,
        knobs,
        speakers,
        durationMinutes,
        podcastMode,
        analysis,
        outline,
      })
      .then((res) => {
        if (mounted) {
          setScript(res);
          emitScriptChange(res);
          setError(null);
        }
      })
      .catch((err) => {
        const message = err instanceof Error ? err.message : "Failed to generate script";
        setError(message);
        onError(message);
      })
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [projectId, rawResearch, idea, knobs, speakers, durationMinutes, analysis, outline, emitScriptChange, onError, script]);

  const updateScene = (updated: Scene) => {
    setScript((currentScript) => {
      if (!currentScript) return currentScript;
      const updatedScript = { 
        ...currentScript, 
        scenes: currentScript.scenes.map((s) => (s.id === updated.id ? { ...s, ...updated } : s)) 
      };
      emitScriptChange(updatedScript);
      return updatedScript;
    });
  };

  const approveScene = async (sceneId: string) => {
    try {
      setApprovingSceneId(sceneId);
      await podcastApi.approveScene({ projectId, sceneId });
      setScript((currentScript) => {
        if (!currentScript) return currentScript;
        const updatedScript = {
          ...currentScript,
          scenes: currentScript.scenes.map((s) => (s.id === sceneId ? { ...s, approved: true } : s)),
        };
        emitScriptChange(updatedScript);
        return updatedScript;
      });
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to approve scene";
      setError(message);
      onError(message);
      throw err;
    } finally {
      setApprovingSceneId((current) => (current === sceneId ? null : current));
    }
  };

  const deleteScene = useCallback((sceneId: string) => {
    if (!activeScript) return;

    if (activeScript.scenes.length <= 1) {
      onError("Cannot delete the last scene. At least one scene is required.");
      return;
    }

    const sceneToDelete = activeScript.scenes.find(s => s.id === sceneId);
    if (!sceneToDelete) return;

    const confirmDelete = window.confirm(
      `Are you sure you want to delete "${sceneToDelete.title}"? This action cannot be undone.`
    );

    if (!confirmDelete) return;

    const updatedScenes = activeScript.scenes.filter(s => s.id !== sceneId);
    const updatedScript = { ...activeScript, scenes: updatedScenes };
    
    emitScriptChange(updatedScript);
    setScript(updatedScript);
  }, [activeScript, emitScriptChange, onError]);

  const generateAllAudio = useCallback(async () => {
    if (!activeScript || !projectId || !knobs) return;
    
    const scenesNeedingAudio = activeScript.scenes.filter((s) => !s.audioUrl);
    if (scenesNeedingAudio.length === 0) {
      onError("All scenes already have audio generated.");
      return;
    }

    try {
      setGeneratingBatchAudio(true);
      setBatchAudioProgress({ completed: 0, total: scenesNeedingAudio.length });

      const sceneData = scenesNeedingAudio.map((scene) => ({
        id: scene.id,
        title: scene.title,
        lines: scene.lines.map((line) => ({ text: line.text })),
      }));

      const result = await podcastApi.generateBatchAudio({
        scenes: sceneData,
        voiceId: knobs.voice_id,
        customVoiceId: knobs.custom_voice_id,
        speed: knobs.voice_speed,
        emotion: knobs.voice_emotion,
        englishNormalization: true,
      });

      const updatedScenes = activeScript.scenes.map((scene) => {
        const batchResult = result.results.find((r: any) => r.sceneId === scene.id);
        if (batchResult) {
          return { ...scene, audioUrl: batchResult.audioUrl };
        }
        return scene;
      });

      await emitScriptChange({ ...activeScript, scenes: updatedScenes });
      setBatchAudioProgress({ completed: scenesNeedingAudio.length, total: scenesNeedingAudio.length });
    } catch (error: any) {
      console.error("Batch audio generation failed:", error);
      onError(`Failed to generate audio: ${error.message || error}`);
    } finally {
      setGeneratingBatchAudio(false);
      setBatchAudioProgress(null);
    }
  }, [activeScript, projectId, knobs, emitScriptChange, onError]);

  const combineAudio = useCallback(async () => {
    if (!activeScript || !projectId) return;
    
    try {
      setCombiningAudio(true);

      const sceneIds: string[] = [];
      const sceneAudioUrls: string[] = [];

      activeScript.scenes.forEach((scene) => {
        if (scene.audioUrl) {
          const audioUrl = scene.audioUrl.startsWith('blob:') ? '' : scene.audioUrl;
          if (audioUrl) {
            sceneIds.push(scene.id);
            sceneAudioUrls.push(audioUrl);
          }
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

      setCombinedAudioResult({
        url: result.combined_audio_url,
        filename: result.combined_audio_filename,
        duration: result.total_duration,
        sceneCount: result.scene_count,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to combine audio";
      onError(`Failed to combine audio: ${message}`);
    } finally {
      setCombiningAudio(false);
    }
  }, [activeScript, projectId, onError]);

  // =====================
  // B-Roll Actions
  // =====================
  
  const generateChartPreviews = useCallback(async () => {
    if (!activeScript) return;
    
    const scenesWithData = activeScript.scenes.filter(
      (s) => s.chart_data && Object.keys(s.chart_data).length > 0
    );
    
    if (scenesWithData.length === 0) {
      onError("No scenes have chart data to generate previews.");
      return;
    }

    try {
      setGeneratingChartId("all");
      
      const updatedScenes = await Promise.all(
        activeScript.scenes.map(async (scene) => {
          if (!scene.chart_data || Object.keys(scene.chart_data).length === 0) {
            return scene;
          }
          
          try {
            const result = await podcastApi.generateChartPreview({
              chart_data: scene.chart_data,
              chart_type: scene.chart_data.type || "bar_comparison",
              title: scene.title,
            });
            
            return {
              ...scene,
              broll_preview_url: result.preview_url,
              chart_id: result.chart_id,
            };
          } catch (err) {
            console.error(`Failed to generate chart for scene ${scene.id}:`, err);
            return scene;
          }
        })
      );
      
      const updatedScript = { ...activeScript, scenes: updatedScenes };
      setScript(updatedScript);
      emitScriptChange(updatedScript);
    } catch (error: any) {
      console.error("Chart preview generation failed:", error);
      onError(`Failed to generate chart previews: ${error.message || error}`);
    } finally {
      setGeneratingChartId(null);
    }
  }, [activeScript, emitScriptChange, onError]);

  const regenerateChart = useCallback(async (sceneId: string) => {
    if (!activeScript) return;
    
    const scene = activeScript.scenes.find((s) => s.id === sceneId);
    if (!scene || !scene.chart_data) return;
    
    try {
      setGeneratingChartId(sceneId);
      
      const result = await podcastApi.generateChartPreview({
        chart_data: scene.chart_data,
        chart_type: scene.chart_data.type || "bar_comparison",
        title: scene.title,
      });
      
      const updatedScenes = activeScript.scenes.map((s) =>
        s.id === sceneId
          ? { ...s, broll_preview_url: result.preview_url, chart_id: result.chart_id }
          : s
      );
      
      const updatedScript = { ...activeScript, scenes: updatedScenes };
      setScript(updatedScript);
      emitScriptChange(updatedScript);
    } catch (error: any) {
      console.error("Chart regeneration failed:", error);
      onError(`Failed to regenerate chart: ${error.message || error}`);
    } finally {
      setGeneratingChartId(null);
    }
  }, [activeScript, emitScriptChange, onError]);

  const removeChart = useCallback((sceneId: string) => {
    if (!activeScript) return;
    
    const updatedScenes = activeScript.scenes.map((s) =>
      s.id === sceneId
        ? { ...s, chart_data: undefined, broll_preview_url: undefined, broll_video_url: undefined }
        : s
    );
    
    const updatedScript = { ...activeScript, scenes: updatedScenes };
    setScript(updatedScript);
    emitScriptChange(updatedScript);
  }, [activeScript, emitScriptChange]);

const value: ScriptEditorContextType = {
    // State
    script,
    loading,
    error,
    podcastMode,
    approvingSceneId,
    generatingAudioId,
    showScriptFormatInfo,
    combiningAudio,
    scriptTab,
    combinedAudioResult,
    generatingBatchAudio,
    batchAudioProgress,
    generatingChartId,
    
    // Computed
    activeScript,
    allApproved,
    approvedCount,
    totalScenes,
    allScenesHaveAudio,
    scenesWithAudio,
    allScenesHaveAudioAndImages,
    needsAudioGeneration,
    scenesWithCharts,
    
    // Setters for UI state
    setScript,
    setLoading,
    setError,
    setApprovingSceneId,
    setGeneratingAudioId,
    setShowScriptFormatInfo,
    setCombiningAudio,
    setScriptTab,
    setCombinedAudioResult,
    setGeneratingBatchAudio,
    setBatchAudioProgress,
    setGeneratingChartId,
    
    // Actions
    updateScene,
    approveScene,
    deleteScene,
    generateAllAudio,
    combineAudio,
    emitScriptChange,
    // B-roll actions
    generateChartPreviews,
    regenerateChart,
    removeChart,
  };

  return (
    <ScriptEditorContext.Provider value={value}>
      {children}
    </ScriptEditorContext.Provider>
  );
};

export const useScriptEditor = (): ScriptEditorContextType => {
  const context = useContext(ScriptEditorContext);
  if (!context) {
    throw new Error("useScriptEditor must be used within ScriptEditorProvider");
  }
  return context;
};
