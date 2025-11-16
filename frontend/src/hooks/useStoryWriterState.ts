import { useState, useCallback, useEffect } from 'react';
import {
  StoryGenerationRequest,
  StoryPremiseResponse,
  StoryOutlineResponse,
  StoryContentResponse,
  StoryFullGenerationResponse,
} from '../services/storyWriterApi';

export interface StoryWriterState {
  // Story parameters (Setup phase)
  persona: string;
  storySetting: string;
  characters: string;
  plotElements: string;
  writingStyle: string;
  storyTone: string;
  narrativePOV: string;
  audienceAgeGroup: string;
  contentRating: string;
  endingPreference: string;
  storyLength: string;
  enableExplainer: boolean;
  enableIllustration: boolean;
  enableNarration: boolean;
  enableVideoNarration: boolean;

  // Image generation settings
  imageProvider: string | null;
  imageWidth: number;
  imageHeight: number;
  imageModel: string | null;

  // Video generation settings
  videoFps: number;
  videoTransitionDuration: number;

  // Audio generation settings
  audioProvider: string;
  audioLang: string;
  audioSlow: boolean;
  audioRate: number;

  // Generated content
  premise: string | null;
  outline: string | null;
  outlineScenes: any[] | null; // Structured scenes from outline
  isOutlineStructured: boolean;
  storyContent: string | null;
  isComplete: boolean;
  sceneImages: Map<number, string> | null; // Generated image URLs by scene number
  sceneAudio: Map<number, string> | null; // Generated audio URLs by scene number
  storyVideo: string | null; // Generated video URL

  // Task management
  currentTaskId: string | null;
  generationProgress: number;
  generationMessage: string | null;

  // UI state
  isLoading: boolean;
  error: string | null;
}

const DEFAULT_STATE: Partial<StoryWriterState> = {
  persona: '',
  storySetting: '',
  characters: '',
  plotElements: '',
  writingStyle: 'Formal',
  storyTone: 'Suspenseful',
  narrativePOV: 'Third Person Limited',
  audienceAgeGroup: 'Adults (18+)',
  contentRating: 'PG-13',
  endingPreference: 'Happy',
  storyLength: 'Medium',
  enableExplainer: true,
  enableIllustration: true,
  enableNarration: true,
  enableVideoNarration: true,
  // Image generation settings
  imageProvider: null,
  imageWidth: 1024,
  imageHeight: 1024,
  imageModel: null,
  // Video generation settings
  videoFps: 24,
  videoTransitionDuration: 0.5,
  // Audio generation settings
  audioProvider: 'gtts',
  audioLang: 'en',
  audioSlow: false,
  audioRate: 150,
  premise: null,
  outline: null,
  outlineScenes: null,
  isOutlineStructured: false,
  storyContent: null,
  isComplete: false,
  sceneImages: null,
  sceneAudio: null,
  storyVideo: null,
  currentTaskId: null,
  generationProgress: 0,
  generationMessage: null,
  isLoading: false,
  error: null,
};

// Mapping for old values to new values (for migration)
const AUDIENCE_AGE_GROUP_MIGRATION: Record<string, string> = {
  'Adults': 'Adults (18+)',
  'Children': 'Children (5-12)',
  'Young Adults': 'Young Adults (13-17)',
};

// Valid audience age groups
const VALID_AUDIENCE_AGE_GROUPS = ['Children (5-12)', 'Young Adults (13-17)', 'Adults (18+)', 'All Ages'];

export const useStoryWriterState = () => {
  const [state, setState] = useState<StoryWriterState>(() => {
    // Initialize from localStorage if available
    try {
      const saved = localStorage.getItem('story_writer_state');
      if (saved) {
        const parsed = JSON.parse(saved);
        
        // Migrate old audienceAgeGroup values to new format
        if (parsed.audienceAgeGroup && AUDIENCE_AGE_GROUP_MIGRATION[parsed.audienceAgeGroup]) {
          parsed.audienceAgeGroup = AUDIENCE_AGE_GROUP_MIGRATION[parsed.audienceAgeGroup];
        }
        // Validate audienceAgeGroup is in valid list, if not, use default
        if (parsed.audienceAgeGroup && !VALID_AUDIENCE_AGE_GROUPS.includes(parsed.audienceAgeGroup)) {
          console.warn(`Invalid audienceAgeGroup value: ${parsed.audienceAgeGroup}, using default`);
          parsed.audienceAgeGroup = DEFAULT_STATE.audienceAgeGroup;
        }
        
        // Convert arrays back to Maps
        const restoredState = {
          ...DEFAULT_STATE,
          ...parsed,
          sceneImages: parsed.sceneImages ? new Map(parsed.sceneImages) : null,
          sceneAudio: parsed.sceneAudio ? new Map(parsed.sceneAudio) : null,
        };
        
        return restoredState as StoryWriterState;
      }
    } catch (error) {
      console.error('Error loading story writer state from localStorage:', error);
    }
    return DEFAULT_STATE as StoryWriterState;
  });

  // Fix invalid audienceAgeGroup values whenever state changes
  useEffect(() => {
    if (state.audienceAgeGroup && !VALID_AUDIENCE_AGE_GROUPS.includes(state.audienceAgeGroup)) {
      // Migrate old values to new format
      const migratedValue = AUDIENCE_AGE_GROUP_MIGRATION[state.audienceAgeGroup] || (DEFAULT_STATE.audienceAgeGroup as string);
      if (migratedValue !== state.audienceAgeGroup) {
        console.log(`Migrating audienceAgeGroup from '${state.audienceAgeGroup}' to '${migratedValue}'`);
        setState((prev) => ({ ...prev, audienceAgeGroup: migratedValue }));
      }
    }
  }, [state.audienceAgeGroup]);

  // Persist state to localStorage
  useEffect(() => {
    try {
      // Don't persist loading/error states
      const { isLoading, error, ...persistableState } = state;
      
      // Ensure audienceAgeGroup is valid before persisting
      let validAudienceAgeGroup = persistableState.audienceAgeGroup;
      if (!VALID_AUDIENCE_AGE_GROUPS.includes(validAudienceAgeGroup)) {
        validAudienceAgeGroup = AUDIENCE_AGE_GROUP_MIGRATION[validAudienceAgeGroup] || (DEFAULT_STATE.audienceAgeGroup as string);
        // Update state if corrected
        if (validAudienceAgeGroup !== persistableState.audienceAgeGroup) {
          setState((prev) => ({ ...prev, audienceAgeGroup: validAudienceAgeGroup }));
        }
      }
      
      // Convert Maps to arrays for JSON serialization
      const serializableState = {
        ...persistableState,
        audienceAgeGroup: validAudienceAgeGroup,
        sceneImages: persistableState.sceneImages ? Array.from(persistableState.sceneImages.entries()) : null,
        sceneAudio: persistableState.sceneAudio ? Array.from(persistableState.sceneAudio.entries()) : null,
      };
      
      localStorage.setItem('story_writer_state', JSON.stringify(serializableState));
    } catch (error) {
      console.error('Error saving story writer state to localStorage:', error);
    }
  }, [state]);

  // Setters
  const setPersona = useCallback((persona: string) => {
    setState((prev) => ({ ...prev, persona }));
  }, []);

  const setStorySetting = useCallback((setting: string) => {
    setState((prev) => ({ ...prev, storySetting: setting }));
  }, []);

  const setCharacters = useCallback((characters: string) => {
    setState((prev) => ({ ...prev, characters }));
  }, []);

  const setPlotElements = useCallback((plotElements: string) => {
    setState((prev) => ({ ...prev, plotElements }));
  }, []);

  const setWritingStyle = useCallback((style: string) => {
    setState((prev) => ({ ...prev, writingStyle: style }));
  }, []);

  const setStoryTone = useCallback((tone: string) => {
    setState((prev) => ({ ...prev, storyTone: tone }));
  }, []);

  const setNarrativePOV = useCallback((pov: string) => {
    setState((prev) => ({ ...prev, narrativePOV: pov }));
  }, []);

  const setAudienceAgeGroup = useCallback((ageGroup: string) => {
    // Migrate old values to new format
    const migratedAgeGroup = AUDIENCE_AGE_GROUP_MIGRATION[ageGroup] || ageGroup;
    // Validate the value is in the valid list
    if (VALID_AUDIENCE_AGE_GROUPS.includes(migratedAgeGroup)) {
      setState((prev) => ({ ...prev, audienceAgeGroup: migratedAgeGroup }));
    } else {
      console.warn(`Invalid audienceAgeGroup value: ${ageGroup}, using default`);
      setState((prev) => ({ ...prev, audienceAgeGroup: DEFAULT_STATE.audienceAgeGroup as string }));
    }
  }, []);

  const setContentRating = useCallback((rating: string) => {
    setState((prev) => ({ ...prev, contentRating: rating }));
  }, []);

  const setEndingPreference = useCallback((ending: string) => {
    setState((prev) => ({ ...prev, endingPreference: ending }));
  }, []);

  const setStoryLength = useCallback((length: string) => {
    setState((prev) => ({ ...prev, storyLength: length }));
  }, []);

  const setEnableExplainer = useCallback((enabled: boolean) => {
    setState((prev) => ({ ...prev, enableExplainer: enabled }));
  }, []);

  const setEnableIllustration = useCallback((enabled: boolean) => {
    setState((prev) => ({ ...prev, enableIllustration: enabled }));
  }, []);

  const setEnableNarration = useCallback((enabled: boolean) => {
    setState((prev) => ({ ...prev, enableNarration: enabled }));
  }, []);

  const setEnableVideoNarration = useCallback((enabled: boolean) => {
    setState((prev) => ({ ...prev, enableVideoNarration: enabled }));
  }, []);

  // Image generation setters
  const setImageProvider = useCallback((provider: string | null) => {
    setState((prev) => ({ ...prev, imageProvider: provider }));
  }, []);

  const setImageWidth = useCallback((width: number) => {
    setState((prev) => ({ ...prev, imageWidth: width }));
  }, []);

  const setImageHeight = useCallback((height: number) => {
    setState((prev) => ({ ...prev, imageHeight: height }));
  }, []);

  const setImageModel = useCallback((model: string | null) => {
    setState((prev) => ({ ...prev, imageModel: model }));
  }, []);

  // Video generation setters
  const setVideoFps = useCallback((fps: number) => {
    setState((prev) => ({ ...prev, videoFps: fps }));
  }, []);

  const setVideoTransitionDuration = useCallback((duration: number) => {
    setState((prev) => ({ ...prev, videoTransitionDuration: duration }));
  }, []);

  // Audio generation setters
  const setAudioProvider = useCallback((provider: string) => {
    setState((prev) => ({ ...prev, audioProvider: provider }));
  }, []);

  const setAudioLang = useCallback((lang: string) => {
    setState((prev) => ({ ...prev, audioLang: lang }));
  }, []);

  const setAudioSlow = useCallback((slow: boolean) => {
    setState((prev) => ({ ...prev, audioSlow: slow }));
  }, []);

  const setAudioRate = useCallback((rate: number) => {
    setState((prev) => ({ ...prev, audioRate: rate }));
  }, []);

  const setPremise = useCallback((premise: string | null) => {
    setState((prev) => ({ ...prev, premise }));
  }, []);

  const setOutline = useCallback((outline: string | null) => {
    setState((prev) => ({ ...prev, outline }));
  }, []);

  const setOutlineScenes = useCallback((scenes: any[] | null) => {
    setState((prev) => ({ ...prev, outlineScenes: scenes, isOutlineStructured: scenes !== null && scenes.length > 0 }));
  }, []);

  const setIsOutlineStructured = useCallback((isStructured: boolean) => {
    setState((prev) => ({ ...prev, isOutlineStructured: isStructured }));
  }, []);

  const setStoryContent = useCallback((content: string | null) => {
    setState((prev) => ({ ...prev, storyContent: content }));
  }, []);

  const setSceneImages = useCallback((images: Map<number, string> | null) => {
    setState((prev) => ({ ...prev, sceneImages: images }));
  }, []);

  const setSceneAudio = useCallback((audio: Map<number, string> | null) => {
    setState((prev) => ({ ...prev, sceneAudio: audio }));
  }, []);

  const setStoryVideo = useCallback((video: string | null) => {
    setState((prev) => ({ ...prev, storyVideo: video }));
  }, []);

  const setIsComplete = useCallback((complete: boolean) => {
    setState((prev) => ({ ...prev, isComplete: complete }));
  }, []);

  const setCurrentTaskId = useCallback((taskId: string | null) => {
    setState((prev) => ({ ...prev, currentTaskId: taskId }));
  }, []);

  const setGenerationProgress = useCallback((progress: number) => {
    setState((prev) => ({ ...prev, generationProgress: progress }));
  }, []);

  const setGenerationMessage = useCallback((message: string | null) => {
    setState((prev) => ({ ...prev, generationMessage: message }));
  }, []);

  const setIsLoading = useCallback((loading: boolean) => {
    setState((prev) => ({ ...prev, isLoading: loading }));
  }, []);

  const setError = useCallback((error: string | null) => {
    setState((prev) => ({ ...prev, error }));
  }, []);

  // Helper to get request object
  const getRequest = useCallback((): StoryGenerationRequest => {
    return {
      persona: state.persona,
      story_setting: state.storySetting,
      character_input: state.characters,
      plot_elements: state.plotElements,
      writing_style: state.writingStyle,
      story_tone: state.storyTone,
      narrative_pov: state.narrativePOV,
      audience_age_group: state.audienceAgeGroup,
      content_rating: state.contentRating,
      ending_preference: state.endingPreference,
      story_length: state.storyLength,
      enable_explainer: state.enableExplainer,
      enable_illustration: state.enableIllustration,
      enable_narration: state.enableNarration,
      enable_video_narration: state.enableVideoNarration,
      // Image generation settings
      image_provider: state.imageProvider || undefined,
      image_width: state.imageWidth,
      image_height: state.imageHeight,
      image_model: state.imageModel || undefined,
      // Video generation settings
      video_fps: state.videoFps,
      video_transition_duration: state.videoTransitionDuration,
      // Audio generation settings
      audio_provider: state.audioProvider,
      audio_lang: state.audioLang,
      audio_slow: state.audioSlow,
      audio_rate: state.audioRate,
    };
  }, [state]);

  // Reset state
  const resetState = useCallback(() => {
    setState(DEFAULT_STATE as StoryWriterState);
    // Clear story writer state from localStorage
    localStorage.removeItem('story_writer_state');
    // Clear phase navigation from localStorage
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('storywriter_current_phase');
        localStorage.removeItem('storywriter_user_selected_phase');
      }
    } catch (error) {
      console.error('Error clearing phase navigation from localStorage:', error);
    }
  }, []);

  return {
    // State
    ...state,

    // Setters
    setPersona,
    setStorySetting,
    setCharacters,
    setPlotElements,
    setWritingStyle,
    setStoryTone,
    setNarrativePOV,
    setAudienceAgeGroup,
    setContentRating,
    setEndingPreference,
    setStoryLength,
    setEnableExplainer,
    setEnableIllustration,
    setEnableNarration,
    setEnableVideoNarration,
    setImageProvider,
    setImageWidth,
    setImageHeight,
    setImageModel,
    setVideoFps,
    setVideoTransitionDuration,
    setAudioProvider,
    setAudioLang,
    setAudioSlow,
    setAudioRate,
    setPremise,
    setOutline,
    setOutlineScenes,
    setIsOutlineStructured,
    setStoryContent,
    setIsComplete,
    setSceneImages,
    setSceneAudio,
    setStoryVideo,
    setCurrentTaskId,
    setGenerationProgress,
    setGenerationMessage,
    setIsLoading,
    setError,

    // Helpers
    getRequest,
    resetState,
  };
};
