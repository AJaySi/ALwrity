import { useState, useCallback, useEffect } from 'react';
import { useCopilotReadable } from '@copilotkit/react-core';
import { 
  loadHistory, 
  clearHistory, 
  getHistoryLength, 
  getPreferences, 
  savePreferences, 
  getCurrentContext, 
  saveCurrentContext, 
  summarizeHistory,
  type ChatMsg,
  type LinkedInPreferences
} from '../utils/storageUtils';
import { getContextAwareSuggestions } from '../utils/linkedInWriterUtils';

export function useLinkedInWriter() {
  // Core state
  const [draft, setDraft] = useState('');
  const [context, setContext] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [livePreviewHtml, setLivePreviewHtml] = useState('');
  const [pendingEdit, setPendingEdit] = useState<{ src: string; target: string } | null>(null);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [currentAction, setCurrentAction] = useState<string | null>(null);
  
  // Grounding data state
  const [researchSources, setResearchSources] = useState<any[]>([]);
  const [citations, setCitations] = useState<any[]>([]);
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [groundingEnabled, setGroundingEnabled] = useState(false);
  const [searchQueries, setSearchQueries] = useState<string[]>([]);

  // Progress state (lightweight custom system)
  type ProgressStatus = 'pending' | 'active' | 'completed' | 'error';
  type ProgressStep = { 
    id: string; 
    label: string; 
    status: ProgressStatus; 
    message?: string;
    details?: any;
    timestamp?: string;
  };
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([]);
  const [progressActive, setProgressActive] = useState<boolean>(false);

  // Chat history state
  const [historyVersion, setHistoryVersion] = useState<number>(0);
  const [chatHistory, setChatHistory] = useState<ChatMsg[]>([]);
  const [userPreferences, setUserPreferences] = useState<LinkedInPreferences>(getPreferences());
  
  // UI state
  const [currentSuggestions, setCurrentSuggestions] = useState<Array<{title: string, message: string, priority?: string}>>([]);
  const [showContextPanel, setShowContextPanel] = useState(false);
  const [showPreferencesModal, setShowPreferencesModal] = useState(false);
  const [showContextModal, setShowContextModal] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [justGeneratedContent, setJustGeneratedContent] = useState(false);

  // Update suggestions when context changes
  const updateSuggestions = useCallback(() => {
    const newSuggestions = getContextAwareSuggestions(
      userPreferences,
      draft,
      chatHistory.slice(-5),
      userPreferences.last_used_actions || []
    );
    setCurrentSuggestions(newSuggestions);
  }, [userPreferences, draft, chatHistory]);

  // Track action usage and update preferences
  const trackActionUsage = useCallback((actionName: string) => {
    const currentPrefs = getPreferences();
    const updatedActions = [...(currentPrefs.last_used_actions || []), actionName].slice(-5);
    savePreferences({ last_used_actions: updatedActions });
    setUserPreferences(prev => ({ ...prev, last_used_actions: updatedActions }));
    
    // Mark content as just generated for content creation actions
    if (['generateLinkedInPost', 'generateLinkedInArticle', 'generateLinkedInCarousel', 'generateLinkedInVideoScript'].includes(actionName)) {
      setJustGeneratedContent(true);
      // Reset the flag after 30 seconds
      setTimeout(() => setJustGeneratedContent(false), 30000);
    }
    
    // Update suggestions after action usage
    setTimeout(() => updateSuggestions(), 100);
  }, [updateSuggestions]);

  // Initialize chat history and preferences from localStorage
  useEffect(() => {
    const loadInitialData = () => {
      try {
        const history = loadHistory();
        const prefs = getPreferences();
        const savedContext = getCurrentContext();
        
        setChatHistory(history);
        setUserPreferences(prefs);
        if (savedContext && !context) {
          setContext(savedContext);
        }
        
        console.log('[LinkedIn Writer] Initialized with:', {
          historyCount: history.length,
          preferences: prefs,
          hasContext: !!savedContext
        });
      } catch (error) {
        console.warn('[LinkedIn Writer] Failed to initialize from localStorage:', error);
      }
    };

    loadInitialData();
  }, []);

  // Listen for lightweight progress events
  useEffect(() => {
    const handleProgressInit = (event: CustomEvent) => {
      const steps: Array<{ id: string; label: string; message?: string }> = event.detail?.steps || [];
      const initialized: ProgressStep[] = steps.map((s, index) => ({
        id: s.id,
        label: s.label,
        message: s.message,
        status: index === 0 ? 'active' : 'pending',
        timestamp: new Date().toISOString()
      }));
      setProgressSteps(initialized);
      setProgressActive(true);
    };

    const handleProgressStep = (event: CustomEvent) => {
      const { id, status, details, message } = event.detail || {};
      if (!id) return;
      setProgressSteps(prev => {
        const updated = prev.map(step => step.id === id ? { 
          ...step, 
          status: (status || 'completed') as ProgressStatus, 
          details, 
          message,
          timestamp: new Date().toISOString() 
        } : step);
        // Mark next pending as active if current completed
        if ((status || 'completed') === 'completed') {
          const nextIdx = updated.findIndex(s => s.status === 'pending');
          if (nextIdx !== -1) {
            updated[nextIdx] = { 
              ...updated[nextIdx], 
              status: 'active', 
              timestamp: new Date().toISOString() 
            };
          }
        }
        return updated;
      });
    };

    const handleProgressComplete = () => {
      console.log('[LinkedIn Writer] Progress completed - hiding progress tracker');
      setProgressSteps(prev => prev.map(s => s.status === 'completed' ? s : { ...s, status: 'completed', timestamp: new Date().toISOString() }));
      setProgressActive(false);
      // Keep progress visible for a moment to show completion, then hide
      setTimeout(() => {
        console.log('[LinkedIn Writer] Hiding progress steps after delay');
        setProgressSteps([]);
      }, 1500);
    };

    const handleProgressError = (event: CustomEvent) => {
      const { id, details } = event.detail || {};
      setProgressSteps(prev => prev.map(s => (id ? (s.id === id) : (s.status === 'active')) ? { ...s, status: 'error', details, timestamp: new Date().toISOString() } : s));
      setProgressActive(false);
    };

    window.addEventListener('linkedinwriter:progressInit', handleProgressInit as EventListener);
    window.addEventListener('linkedinwriter:progressStep', handleProgressStep as EventListener);
    window.addEventListener('linkedinwriter:progressComplete', handleProgressComplete as EventListener);
    window.addEventListener('linkedinwriter:progressError', handleProgressError as EventListener);

    return () => {
      window.removeEventListener('linkedinwriter:progressInit', handleProgressInit as EventListener);
      window.removeEventListener('linkedinwriter:progressStep', handleProgressStep as EventListener);
      window.removeEventListener('linkedinwriter:progressComplete', handleProgressComplete as EventListener);
      window.removeEventListener('linkedinwriter:progressError', handleProgressError as EventListener);
    };
  }, []);

  // Listen for grounding data updates from CopilotKit actions
  useEffect(() => {
    const handleGroundingDataUpdate = (event: CustomEvent) => {
      console.log('[LinkedIn Writer] Received grounding data event:', event.detail);
      
      const { researchSources, citations, qualityMetrics, groundingEnabled, searchQueries } = event.detail;
      
      console.log('[LinkedIn Writer] Extracted data:', {
        researchSources: researchSources?.length || 0,
        citations: citations?.length || 0,
        qualityMetrics: !!qualityMetrics,
        groundingEnabled,
        searchQueries: searchQueries?.length || 0
      });
      
      setResearchSources(researchSources || []);
      setCitations(citations || []);
      setQualityMetrics(qualityMetrics || null);
      setGroundingEnabled(groundingEnabled || false);
      setSearchQueries(searchQueries || []);
      
      console.log('[LinkedIn Writer] Grounding data updated:', {
        sourcesCount: researchSources?.length || 0,
        citationsCount: citations?.length || 0,
        hasQualityMetrics: !!qualityMetrics,
        groundingEnabled
      });
    };

    window.addEventListener('linkedinwriter:updateGroundingData', handleGroundingDataUpdate as EventListener);
    
    return () => {
      window.removeEventListener('linkedinwriter:updateGroundingData', handleGroundingDataUpdate as EventListener);
    };
  }, []);

  // Save context changes to localStorage
  useEffect(() => {
    if (context) {
      saveCurrentContext(context);
    }
  }, [context]);
  
  // Update suggestions when relevant state changes
  useEffect(() => {
    updateSuggestions();
  }, [updateSuggestions]);

  // Handle draft updates from CopilotKit actions
  useEffect(() => {
    const handleUpdateDraft = (event: CustomEvent) => {
      console.log('[LinkedIn Writer] Draft updated:', event.detail?.substring(0, 100) + '...');
      console.log('[LinkedIn Writer] Draft length:', event.detail?.length);
      console.log('[LinkedIn Writer] Setting draft and clearing loading state...');
      setDraft(event.detail);
      setIsGenerating(false);
      setLoadingMessage('');
      setCurrentAction(null);
      // Auto-show preview when new content is generated
      setShowPreview(true);
      // Hide progress tracker when content is generated
      setProgressActive(false);
      setProgressSteps([]);
      console.log('[LinkedIn Writer] Draft update complete');
    };

    const handleAppendDraft = (event: CustomEvent) => {
      setDraft(prev => prev + event.detail);
    };

    const handleAssistantMessage = (event: CustomEvent) => {
      console.log('LinkedIn Assistant:', event.detail);
    };

    const handleLoadingStart = (event: CustomEvent) => {
      const { action, message } = event.detail;
      console.log('[LinkedIn Writer] Loading started:', { action, message });
      setCurrentAction(action);
      setLoadingMessage(message);
      setIsGenerating(true);
    };

    const handleLoadingEnd = (event: CustomEvent) => {
      console.log('[LinkedIn Writer] Loading ended - clearing all loading states');
      setIsGenerating(false);
      setLoadingMessage('');
      setCurrentAction(null);
      console.log('[LinkedIn Writer] Loading state cleared');
    };

    const handleApplyEdit = (event: CustomEvent) => {
      const target: string = typeof event.detail === 'string' ? event.detail : (event.detail?.target ?? '');
      const src = draft || '';
      if (!target) return;
      setPendingEdit({ src, target });
      setIsPreviewing(true);
      
      // Use diff highlighting for professional content changes
      try {
        const { diffMarkup } = require('../utils/contentFormatters');
        setLivePreviewHtml(diffMarkup(src, target));
      } catch (error) {
        // Fallback to simple text if diffMarkup fails to load
        console.warn('Failed to load diffMarkup, using fallback:', error);
        setLivePreviewHtml(target);
      }
    };

    window.addEventListener('linkedinwriter:updateDraft', handleUpdateDraft as EventListener);
    window.addEventListener('linkedinwriter:appendDraft', handleAppendDraft as EventListener);
    window.addEventListener('linkedinwriter:assistantMessage', handleAssistantMessage as EventListener);
    window.addEventListener('linkedinwriter:applyEdit', handleApplyEdit as EventListener);
    window.addEventListener('linkedinwriter:loadingStart', handleLoadingStart as EventListener);
    window.addEventListener('linkedinwriter:loadingEnd', handleLoadingEnd as EventListener);

    return () => {
      window.removeEventListener('linkedinwriter:updateDraft', handleUpdateDraft as EventListener);
      window.removeEventListener('linkedinwriter:appendDraft', handleAppendDraft as EventListener);
      window.removeEventListener('linkedinwriter:assistantMessage', handleAssistantMessage as EventListener);
      window.removeEventListener('linkedinwriter:applyEdit', handleApplyEdit as EventListener);
      window.removeEventListener('linkedinwriter:loadingStart', handleLoadingStart as EventListener);
      window.removeEventListener('linkedinwriter:loadingEnd', handleLoadingEnd as EventListener);
    };
  }, [draft]);

  // Event handlers
  const handleDraftChange = useCallback((value: string) => {
    setDraft(value);
  }, []);

  const handleContextChange = useCallback((value: string) => {
    setContext(value);
  }, []);

  const handleClear = useCallback(() => {
    setDraft('');
    setContext('');
  }, []);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(draft);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  }, [draft]);

  const handleClearHistory = useCallback(() => {
    clearHistory(); 
    setHistoryVersion(v => v + 1);
    setChatHistory([]);
    console.log('[LinkedIn Writer] Chat memory cleared by user');
  }, []);

  // Make content available to CopilotKit
  useCopilotReadable({
    description: 'Current LinkedIn content draft',
    value: draft
  });

  useCopilotReadable({
    description: 'Context and notes for LinkedIn content',
    value: context
  });

  useCopilotReadable({
    description: 'User preferences for LinkedIn content (tone, industry, audience, style, options)',
    value: userPreferences
  });

  return {
    // State
    draft,
    context,
    isGenerating,
    isPreviewing,
    livePreviewHtml,
    pendingEdit,
    loadingMessage,
    currentAction,
    historyVersion,
    chatHistory,
    userPreferences,
    currentSuggestions,
    showContextPanel,
    showPreferencesModal,
    showContextModal,
    showPreview,
    justGeneratedContent,
    
    // Setters
    setDraft,
    setContext,
    setIsGenerating,
    setIsPreviewing,
    setLivePreviewHtml,
    setPendingEdit,
    setLoadingMessage,
    setCurrentAction,
    setHistoryVersion,
    setChatHistory,
    setUserPreferences,
    setShowContextPanel,
    setShowPreferencesModal,
    setShowContextModal,
    setShowPreview,
    setJustGeneratedContent: setJustGeneratedContent,
    
    // Handlers
    handleDraftChange,
    handleContextChange,
    handleClear,
    handleCopy,
    handleClearHistory,
    
    // Utilities
    trackActionUsage,
    updateSuggestions,
    getHistoryLength,
    savePreferences,
    summarizeHistory,
    
    // Grounding data
    researchSources,
    citations,
    qualityMetrics,
    groundingEnabled,
    searchQueries,
    setResearchSources,
    setCitations,
    setQualityMetrics,
    setGroundingEnabled,
    setSearchQueries,

    // Progress (exposed to UI)
    progressSteps,
    progressActive
  };
}
