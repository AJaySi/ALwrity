import { useState, useCallback, useEffect, useRef } from 'react';
import {
  PodcastAnalysis,
  PodcastEstimate,
  Query,
  Research,
  Script,
  Knobs,
  Job,
  CreateProjectPayload,
} from '../components/PodcastMaker/types';
import { BlogResearchResponse, ResearchProvider } from '../services/blogWriterApi';
import { podcastApi } from '../services/podcastApi';

export interface PodcastProjectState {
  // Project metadata
  project: {
    id: string;
    idea: string;
    duration: number;
    speakers: number;
    avatarUrl?: string | null;
    avatarPrompt?: string | null;
    avatarPersonaId?: string | null;
  } | null;
  
  // Step results
  analysis: PodcastAnalysis | null;
  queries: Query[];
  selectedQueries: Set<string>;
  research: Research | null;
  rawResearch: BlogResearchResponse | null;
  estimate: PodcastEstimate | null;
  scriptData: Script | null;
  
  // Render jobs
  renderJobs: Job[];
  
  // Settings
  knobs: Knobs;
  researchProvider: ResearchProvider;
  budgetCap: number;
  
  // UI state
  showScriptEditor: boolean;
  showRenderQueue: boolean;
  
  // Current step tracking
  currentStep: 'create' | 'analysis' | 'research' | 'script' | 'render' | null;
  
  // Final combined video
  finalVideoUrl?: string | null;
  
  // Timestamps
  createdAt?: string;
  updatedAt?: string;
}

const DEFAULT_KNOBS: Knobs = {
  voice_emotion: "neutral",
  voice_speed: 1,
  resolution: "720p",
  scene_length_target: 45,
  sample_rate: 24000,
  bitrate: "standard",
};

const DEFAULT_STATE: PodcastProjectState = {
  project: null,
  analysis: null,
  queries: [],
  selectedQueries: new Set(),
  research: null,
  rawResearch: null,
  estimate: null,
  scriptData: null,
  renderJobs: [],
  knobs: DEFAULT_KNOBS,
  researchProvider: "exa",
  budgetCap: 50,
  showScriptEditor: false,
  showRenderQueue: false,
  currentStep: null,
};

const STORAGE_KEY = 'podcast_project_state';

export const usePodcastProjectState = () => {
  const [state, setState] = useState<PodcastProjectState>(() => {
    // Initialize from localStorage if available
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        
        // Restore Sets from arrays
        const restoredState: PodcastProjectState = {
          ...DEFAULT_STATE,
          ...parsed,
          selectedQueries: parsed.selectedQueries ? new Set(parsed.selectedQueries) : new Set(),
          renderJobs: parsed.renderJobs || [],
        };
        
        return restoredState;
      }
    } catch (error) {
      console.error('Error loading podcast project state from localStorage:', error);
    }
    return DEFAULT_STATE;
  });

  // Debounce ref for database sync
  const syncTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Persist state to localStorage on every change
  useEffect(() => {
    try {
      // Convert Sets to arrays for JSON serialization
      const serializableState = {
        ...state,
        selectedQueries: Array.from(state.selectedQueries),
      };
      
      localStorage.setItem(STORAGE_KEY, JSON.stringify(serializableState));
    } catch (error) {
      console.error('Error saving podcast project state to localStorage:', error);
    }
  }, [state]);

  // Sync to database after major steps (debounced)
  useEffect(() => {
    if (!state.project || !state.project.id) return;

    // Capture project ID to avoid closure issues
    const projectId = state.project.id;

    // Clear existing timeout
    if (syncTimeoutRef.current) {
      clearTimeout(syncTimeoutRef.current);
    }

    // Debounce database sync (wait 2 seconds after last change)
    syncTimeoutRef.current = setTimeout(async () => {
      try {
        const dbState = {
          analysis: state.analysis,
          queries: state.queries,
          selected_queries: Array.from(state.selectedQueries),
          research: state.research,
          raw_research: state.rawResearch,
          estimate: state.estimate,
          script_data: state.scriptData,
          render_jobs: state.renderJobs,
          knobs: state.knobs,
          research_provider: state.researchProvider,
          show_script_editor: state.showScriptEditor,
          show_render_queue: state.showRenderQueue,
          current_step: state.currentStep,
          status: state.currentStep === 'render' && state.renderJobs.every(j => j.status === 'completed') ? 'completed' : 'in_progress',
        };

        await podcastApi.saveProject(projectId, dbState);
      } catch (error) {
        console.error('Error syncing project to database:', error);
        // Don't throw - localStorage is still working
      }
    }, 2000);

    return () => {
      if (syncTimeoutRef.current) {
        clearTimeout(syncTimeoutRef.current);
      }
    };
  }, [
    state.project,
    state.analysis,
    state.queries,
    state.selectedQueries,
    state.research,
    state.rawResearch,
    state.estimate,
    state.scriptData,
    state.renderJobs,
    state.knobs,
    state.researchProvider,
    state.showScriptEditor,
    state.showRenderQueue,
    state.currentStep,
  ]);

  // Setters
  const setProject = useCallback((project: PodcastProjectState['project']) => {
    setState((prev) => ({ ...prev, project, currentStep: project ? 'analysis' : null, updatedAt: new Date().toISOString() }));
  }, []);

  const setAnalysis = useCallback((analysis: PodcastProjectState['analysis']) => {
    setState((prev) => ({ 
      ...prev, 
      analysis, 
      currentStep: analysis ? 'research' : prev.currentStep,
      updatedAt: new Date().toISOString() 
    }));
  }, []);

  const setQueries = useCallback((queries: Query[]) => {
    setState((prev) => ({ ...prev, queries, updatedAt: new Date().toISOString() }));
  }, []);

  const setSelectedQueries = useCallback((selectedQueries: Set<string> | ((prev: Set<string>) => Set<string>)) => {
    setState((prev) => {
      const newQueries = typeof selectedQueries === 'function' ? selectedQueries(prev.selectedQueries) : selectedQueries;
      return { ...prev, selectedQueries: newQueries, updatedAt: new Date().toISOString() };
    });
  }, []);

  const setResearch = useCallback((research: PodcastProjectState['research']) => {
    setState((prev) => ({ 
      ...prev, 
      research, 
      currentStep: research ? 'script' : prev.currentStep,
      updatedAt: new Date().toISOString() 
    }));
  }, []);

  const setRawResearch = useCallback((rawResearch: PodcastProjectState['rawResearch']) => {
    setState((prev) => ({ ...prev, rawResearch, updatedAt: new Date().toISOString() }));
  }, []);

  const setEstimate = useCallback((estimate: PodcastProjectState['estimate']) => {
    setState((prev) => ({ ...prev, estimate, updatedAt: new Date().toISOString() }));
  }, []);

  const setScriptData = useCallback((scriptData: PodcastProjectState['scriptData']) => {
    setState((prev) => ({ 
      ...prev, 
      scriptData, 
      currentStep: scriptData ? 'render' : prev.currentStep,
      updatedAt: new Date().toISOString() 
    }));
  }, []);

  const setRenderJobs = useCallback((renderJobs: Job[]) => {
    setState((prev) => ({ ...prev, renderJobs, updatedAt: new Date().toISOString() }));
  }, []);

  const updateRenderJob = useCallback((sceneId: string, updates: Partial<Job>) => {
    setState((prev) => {
      const existingJob = prev.renderJobs.find((job) => job.sceneId === sceneId);
      
      if (existingJob) {
        // Update existing job
        return {
          ...prev,
          renderJobs: prev.renderJobs.map((job) =>
            job.sceneId === sceneId ? { ...job, ...updates } : job
          ),
          updatedAt: new Date().toISOString(),
        };
      } else {
        // Create new job if it doesn't exist
        const newJob: Job = {
          sceneId,
          title: updates.title || sceneId,
          status: updates.status || "idle",
          progress: updates.progress || 0,
          previewUrl: updates.previewUrl || null,
          finalUrl: updates.finalUrl || null,
          videoUrl: updates.videoUrl || null,
          imageUrl: updates.imageUrl || null,
          jobId: updates.jobId || null,
          taskId: updates.taskId || null,
          cost: updates.cost || null,
          provider: updates.provider || null,
          voiceId: updates.voiceId || null,
          fileSize: updates.fileSize || null,
          avatarImageUrl: updates.avatarImageUrl || null,
        };
        return {
          ...prev,
          renderJobs: [...prev.renderJobs, newJob],
          updatedAt: new Date().toISOString(),
        };
      }
    });
  }, []);

  const setKnobs = useCallback((knobs: Knobs) => {
    setState((prev) => ({ ...prev, knobs, updatedAt: new Date().toISOString() }));
  }, []);

  const setResearchProvider = useCallback((provider: ResearchProvider) => {
    setState((prev) => ({ ...prev, researchProvider: provider, updatedAt: new Date().toISOString() }));
  }, []);

  const setBudgetCap = useCallback((cap: number) => {
    setState((prev) => ({ ...prev, budgetCap: cap, updatedAt: new Date().toISOString() }));
  }, []);

  const setShowScriptEditor = useCallback((show: boolean) => {
    setState((prev) => ({ ...prev, showScriptEditor: show, updatedAt: new Date().toISOString() }));
  }, []);

  const setShowRenderQueue = useCallback((show: boolean) => {
    setState((prev) => ({ ...prev, showRenderQueue: show, updatedAt: new Date().toISOString() }));
  }, []);

  const setCurrentStep = useCallback((step: PodcastProjectState['currentStep']) => {
    setState((prev) => ({ ...prev, currentStep: step, updatedAt: new Date().toISOString() }));
  }, []);

  // Reset state
  const resetState = useCallback(() => {
    setState(DEFAULT_STATE);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  // Initialize project from payload
  const initializeProject = useCallback(async (payload: CreateProjectPayload, projectId: string) => {
    // Create project in database
    try {
      await podcastApi.createProjectInDb({
        project_id: projectId,
        idea: payload.ideaOrUrl,
        duration: payload.duration,
        speakers: payload.speakers,
        budget_cap: payload.budgetCap,
      });
    } catch (error) {
      console.error('Error creating project in database:', error);
      // Continue anyway - localStorage fallback
    }

    setState((prev) => ({
      ...prev,
      project: {
        id: projectId,
        idea: payload.ideaOrUrl,
        duration: payload.duration,
        speakers: payload.speakers,
        avatarUrl: payload.avatarUrl || null,
        avatarPrompt: null, // Will be set when avatar is generated
        avatarPersonaId: null,
      },
      knobs: payload.knobs,
      budgetCap: payload.budgetCap,
      currentStep: 'analysis',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }));
  }, []);

  // Load project from database
  const loadProjectFromDb = useCallback(async (projectId: string) => {
    try {
      const dbProject = await podcastApi.loadProject(projectId);
      
      // Restore state from database
      setState((prev) => ({
        ...prev,
        project: {
          id: dbProject.project_id,
          idea: dbProject.idea,
          duration: dbProject.duration,
          speakers: dbProject.speakers,
          avatarUrl: dbProject.avatar_url || null,
          avatarPrompt: dbProject.avatar_prompt || null,
          avatarPersonaId: dbProject.avatar_persona_id || null,
        },
        analysis: dbProject.analysis,
        queries: dbProject.queries || [],
        selectedQueries: new Set(dbProject.selected_queries || []),
        research: dbProject.research,
        rawResearch: dbProject.raw_research,
        estimate: dbProject.estimate,
        scriptData: dbProject.script_data,
        renderJobs: dbProject.render_jobs || [],
        knobs: dbProject.knobs || DEFAULT_KNOBS,
        researchProvider: dbProject.research_provider || 'exa',
        budgetCap: dbProject.budget_cap || 50,
        showScriptEditor: dbProject.show_script_editor || false,
        showRenderQueue: dbProject.show_render_queue || false,
        currentStep: dbProject.current_step || null,
        finalVideoUrl: dbProject.final_video_url || null,
        createdAt: dbProject.created_at,
        updatedAt: dbProject.updated_at,
      }));
    } catch (error) {
      console.error('Error loading project from database:', error);
      throw error;
    }
  }, []);

  return {
    // State
    ...state,

    // Setters
    setProject,
    setAnalysis,
    setQueries,
    setSelectedQueries,
    setResearch,
    setRawResearch,
    setEstimate,
    setScriptData,
    setRenderJobs,
    updateRenderJob,
    setKnobs,
    setResearchProvider,
    setBudgetCap,
    setShowScriptEditor,
    setShowRenderQueue,
    setCurrentStep,

    // Helpers
    resetState,
    initializeProject,
    loadProjectFromDb,
  };
};

