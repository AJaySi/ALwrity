import React, { useEffect, useMemo } from 'react';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotReadable, useCopilotAction, useCopilotContext } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import './styles/alwrity-copilot.css';
import RegisterLinkedInActions from './RegisterLinkedInActions';
import RegisterLinkedInEditActions from './RegisterLinkedInEditActions';
import RegisterLinkedInActionsEnhanced from './RegisterLinkedInActionsEnhanced';
import { Header, ContentEditor, LoadingIndicator, WelcomeMessage, ProgressTracker, CopilotActions } from './components';
import { useLinkedInWriter } from './hooks/useLinkedInWriter';
import { useCopilotPersistence } from './utils/enhancedPersistence';
import { PlatformPersonaProvider, usePlatformPersonaContext } from '../shared/PersonaContext/PlatformPersonaProvider';

const useCopilotActionTyped = useCopilotAction as any;

// Optional debug flag: set to true to enable verbose logs locally
const DEBUG_LINKEDIN = false;

interface LinkedInWriterProps {
  className?: string;
}

const LinkedInWriter: React.FC<LinkedInWriterProps> = ({ className = '' }) => {
  return (
    <PlatformPersonaProvider platform="linkedin">
      <LinkedInWriterContent className={className} />
    </PlatformPersonaProvider>
  );
};

// Main LinkedIn Writer Content Component
const LinkedInWriterContent: React.FC<LinkedInWriterProps> = ({ className = '' }) => {
  const {
    // State
    draft,
    context,
    isGenerating,
    isPreviewing,
    livePreviewHtml,
    pendingEdit,
    loadingMessage,
    currentAction,
    chatHistory,
    userPreferences,
    currentSuggestions,
    showPreferencesModal,
    showContextModal,
    showPreview,
    justGeneratedContent,
    
    // Grounding data
    researchSources,
    citations,
    qualityMetrics,
    groundingEnabled,
    searchQueries,
    progressSteps,
    progressActive,
    
    // Setters
    setDraft,
    setIsPreviewing,
    setLivePreviewHtml,
    setPendingEdit,
    setUserPreferences,
    setShowPreferencesModal,
    setShowContextModal,
    setShowPreview,
    
    // Handlers
    handleDraftChange,
    handleContextChange,
    handleClear,
    handleCopy,
    handleClearHistory,
    
    // Utilities
    getHistoryLength,
    savePreferences,
    summarizeHistory
  } = useLinkedInWriter();

  // Get persona context for enhanced AI assistance
  const { corePersona, platformPersona, loading: personaLoading } = usePlatformPersonaContext();

  // Get enhanced persistence functionality
  const {
    persistenceManager,
    saveChatHistory,
    loadChatHistory,
    addChatMessage,
    saveUserPreferences: savePersistedPreferences,
    loadUserPreferences: loadPersistedPreferences,
    saveConversationContext,
    loadConversationContext,
    saveDraftContent,
    loadDraftContent,
    saveLastSession,
    loadLastSession,
    getStorageStats
  } = useCopilotPersistence();
  
  // Sync component state with enhanced persistence
  useEffect(() => {
    console.log('[LinkedIn Writer] Component mounted, enhanced persistence enabled');
    
    // Load persisted data on component mount
    const loadPersistedData = () => {
      try {
        // Load chat history
        const chatHistory = loadChatHistory();
        console.log(`📖 Loaded ${chatHistory.length} persisted chat messages`);
        
        // Load user preferences
        const persistedPrefs = loadPersistedPreferences();
        console.log('📖 Loaded persisted user preferences:', persistedPrefs);
        
        // Load conversation context
        const conversationContext = loadConversationContext();
        console.log('📖 Loaded persisted conversation context:', conversationContext);
        
        // Load draft content
        const persistedDraft = loadDraftContent();
        if (persistedDraft && !draft) {
          console.log('📖 Restoring persisted draft content');
          // Note: We'll need to integrate this with the useLinkedInWriter hook
        }
        
        // Load last session
        const lastSession = loadLastSession();
        if (lastSession) {
          console.log('📖 Last session:', lastSession);
        }
        
        // Get storage statistics
        const stats = getStorageStats();
        console.log('📊 Persistence stats:', stats);
        
      } catch (error) {
        console.error('❌ Error loading persisted data:', error);
      }
    };
    
    // Load data after a short delay to allow CopilotKit to initialize
    setTimeout(loadPersistedData, 1000);
    
    // Save session data when component unmounts
    return () => {
      saveLastSession();
    };
  }, []);

  // Handle preview changes
  const handleConfirmChanges = () => {
    if (pendingEdit) {
      setDraft(pendingEdit.target);
    }
    setIsPreviewing(false);
    setPendingEdit(null);
    setLivePreviewHtml('');
  };

  const handleDiscardChanges = () => {
    setIsPreviewing(false);
    setPendingEdit(null);
    setLivePreviewHtml('');
  };

  const handlePreviewToggle = () => {
    setShowPreview(!showPreview);
  };

  const handlePreferencesChange = (prefs: Partial<typeof userPreferences>) => {
    const updated = { ...userPreferences, ...prefs };
    setUserPreferences(updated);
    savePreferences(prefs);
    
    // Also save to enhanced persistence
    savePersistedPreferences(prefs);
  };

  // Share current draft and context with CopilotKit for better context awareness
  useCopilotReadable({
    description: 'Current LinkedIn content draft the user is editing',
    value: draft,
    categories: ['social', 'linkedin', 'draft']
  });
  
  // Auto-save draft content when it changes
  useEffect(() => {
    if (draft && draft.trim().length > 0) {
      saveDraftContent(draft);
    }
  }, [draft, saveDraftContent]);

  useCopilotReadable({
    description: 'User context and notes for LinkedIn content',
    value: context,
    categories: ['social', 'linkedin', 'context']
  });

  // Allow Copilot to update the draft directly
  useCopilotActionTyped({
    name: 'updateLinkedInDraft',
    description: 'Replace the LinkedIn content draft with provided content',
    parameters: [
      { name: 'content', type: 'string', description: 'The full content to set', required: true }
    ],
    handler: async ({ content }: { content: string }) => {
      setDraft(content);
      return { success: true, message: 'Draft updated' };
    }
  });

  // Let Copilot append text to the draft
  useCopilotActionTyped({
    name: 'appendToLinkedInDraft',
    description: 'Append text to the current LinkedIn content draft',
    parameters: [
      { name: 'content', type: 'string', description: 'The text to append', required: true }
    ],
    handler: async ({ content }: { content: string }) => {
      setDraft(prev => (prev ? `${prev}\n\n${content}` : content));
      return { success: true, message: 'Text appended' };
    }
  });


  // Initialize CopilotActions component to handle all copilot-related functionality
  const getIntelligentSuggestions = CopilotActions({
    draft,
    context,
    userPreferences,
    justGeneratedContent,
    handleContextChange,
    setDraft
  });

  return (
    <div className={`linkedin-writer ${className}`} style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Header
        userPreferences={userPreferences}
        chatHistory={chatHistory}
        showPreferencesModal={showPreferencesModal}
        onPreferencesModalChange={setShowPreferencesModal}
        onPreferencesChange={handlePreferencesChange}
        onClearHistory={handleClearHistory}
        getHistoryLength={getHistoryLength}
      />

      {/* Lightweight progress tracker under header */}
      <div style={{ 
        padding: '6px 16px',
        transition: 'all 300ms ease',
        opacity: progressActive || progressSteps.length > 0 ? 1 : 0,
        transform: progressActive || progressSteps.length > 0 ? 'translateY(0)' : 'translateY(-10px)',
        height: progressActive || progressSteps.length > 0 ? 'auto' : 0,
        overflow: 'hidden'
      }}>
        <ProgressTracker steps={progressSteps as any} active={progressActive} />
      </div>



      {/* Debug: Enhanced Persistence Test Buttons (remove in production) */}


      {/* Main Content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Loading Indicator */}
        <LoadingIndicator
          isGenerating={isGenerating}
          loadingMessage={loadingMessage}
          currentAction={currentAction}
        />

         {/* Content Area */}
        {draft || isGenerating ? (<>
          {/* Editor Panel - Show when there's content or generating */}
          <ContentEditor
            isPreviewing={isPreviewing}
            pendingEdit={pendingEdit}
            livePreviewHtml={livePreviewHtml}
            draft={draft}
            showPreview={showPreview}
            isGenerating={isGenerating}
            loadingMessage={loadingMessage}
            // Grounding data
            researchSources={researchSources}
            citations={citations}
            qualityMetrics={qualityMetrics}
            groundingEnabled={groundingEnabled}
            searchQueries={searchQueries}
            onConfirmChanges={handleConfirmChanges}
            onDiscardChanges={handleDiscardChanges}
            onDraftChange={handleDraftChange}
            onPreviewToggle={handlePreviewToggle}
            topic={context ? context.split('\n')[0].substring(0, 50) : undefined}
          />
 
          
        </>) : (
          /* Welcome Message - Show when no content */
          <WelcomeMessage
            draft={draft}
            isGenerating={isGenerating}
          />
        )}
      </div>

      {/* Register CopilotKit Actions */}
      <RegisterLinkedInActions />
      <RegisterLinkedInEditActions />
      {/* Enhanced Persona-Aware Actions */}
      <RegisterLinkedInActionsEnhanced />


      {/* CopilotKit Sidebar */}
      <CopilotSidebar 
        className="alwrity-copilot-sidebar linkedin-writer"
        labels={{
          title: 'ALwrity Co-Pilot',
          initial: draft ? 
            'Great! I can see you have content to work with. Use the quick edit suggestions below to refine your post in real-time, or ask me to make specific changes.' : 
            `Hi! I'm your ALwrity Co-Pilot, your LinkedIn writing assistant${corePersona ? ` with ${corePersona.persona_name} persona optimization` : ''}. I can help you create professional posts, articles, carousels, video scripts, and comment responses. Try the new persona-aware actions for enhanced content generation!`
        }}
        suggestions={getIntelligentSuggestions}
        makeSystemMessage={(context: string, additional?: string) => {
          const prefs = userPreferences;
          const prefsLine = Object.keys(prefs).length ? `User preferences (remember and respect unless changed): ${JSON.stringify(prefs)}` : '';
          const history = summarizeHistory();
          const historyLine = history ? `Recent conversation (last 15 messages):\n${history}` : '';
          const currentDraft = draft ? `Current draft content:\n${draft}` : 'No current draft content.';
          const tone = prefs.tone || 'professional';
          const industry = prefs.industry || 'Technology';
          const audience = prefs.target_audience || 'professionals';
          
          // Enhanced persona-aware guidance
          const personaGuidance = corePersona && platformPersona ? `
PERSONA-AWARE WRITING GUIDANCE:
- PERSONA: ${corePersona.persona_name} (${corePersona.archetype})
- CORE BELIEF: ${corePersona.core_belief}
- CONFIDENCE SCORE: ${corePersona.confidence_score}%
- LINGUISTIC STYLE: ${corePersona.linguistic_fingerprint?.sentence_metrics?.average_sentence_length_words || 'Unknown'} words average, ${corePersona.linguistic_fingerprint?.sentence_metrics?.active_to_passive_ratio || 'Unknown'} active/passive ratio
- GO-TO WORDS: ${corePersona.linguistic_fingerprint?.lexical_features?.go_to_words?.join(', ') || 'None specified'}
- AVOID WORDS: ${corePersona.linguistic_fingerprint?.lexical_features?.avoid_words?.join(', ') || 'None specified'}

PLATFORM OPTIMIZATION (LinkedIn):
- CHARACTER LIMIT: ${platformPersona.content_format_rules?.character_limit || '3000'} characters
- OPTIMAL LENGTH: ${platformPersona.content_format_rules?.optimal_length || '150-300 words'}
- ENGAGEMENT PATTERN: ${platformPersona.engagement_patterns?.posting_frequency || '2-3 times per week'}
- HASHTAG STRATEGY: ${platformPersona.lexical_features?.hashtag_strategy || '3-5 relevant hashtags'}

ALWAYS generate content that matches this persona's linguistic fingerprint and platform optimization rules.` : '';

          const guidance = `
 You are ALwrity's LinkedIn Writing Assistant specializing in ${industry} content.
 
 CRITICAL CONSTRAINTS:
 - TONE: Always maintain a ${tone} tone throughout all content
 - INDUSTRY: Focus specifically on ${industry} industry context and terminology  
 - AUDIENCE: Target content specifically for ${audience}
 - QUALITY: Ensure all content meets LinkedIn professional standards
 ${personaGuidance ? `\n${personaGuidance}` : ''}
 
 CURRENT CONTEXT:
 ${currentDraft}
 
       Available LinkedIn content tools:
      - generateLinkedInPost: Create ${tone} LinkedIn posts for ${industry} ${audience}
      - generateLinkedInArticle: Write ${tone} thought leadership articles about ${industry}
      - generateLinkedInCarousel: Design ${tone} multi-slide carousels for ${industry} insights
      - generateLinkedInVideoScript: Create ${tone} video scripts for ${industry} topics
      - generateLinkedInCommentResponse: Draft ${tone} responses appropriate for ${industry}
      
      🎭 ENHANCED PERSONA-AWARE ACTIONS (Recommended):
      - generateLinkedInPostWithPersona: Create posts optimized for your writing style and platform constraints
      - generateLinkedInArticleWithPersona: Write articles with persona-aware optimization
      - validateContentAgainstPersona: Validate existing content against your persona
      - getPersonaWritingSuggestions: Get personalized writing recommendations
 
 DIRECT DRAFT ACTIONS:
 - updateLinkedInDraft: Replace the entire draft with new content
 - appendToLinkedInDraft: Add text to the existing draft
 - editLinkedInDraft: Apply quick edits (Casual, Professional, TightenHook, AddCTA, Shorten, Lengthen) to the current draft
 
 IMPORTANT: When refining or editing content, always reference the current draft above. If the user asks to refine their post, use the current draft content as the starting point. Never ask for content that already exists in the draft.
 
 For quick edits, use editLinkedInDraft with the appropriate operation. This will show a live preview of changes before applying them.
 
 Use user preferences, context, conversation history, and persona data to personalize all content.
 Always respect the user's preferred ${tone} tone, ${industry} industry focus, and writing persona style.
 Always use the most appropriate tool for the user's request.`.trim();
          return [prefsLine, historyLine, currentDraft, guidance, additional].filter(Boolean).join('\n\n');
        }}
        observabilityHooks={{
          onChatExpanded: () => {
            console.log('[LinkedIn Writer] Sidebar opened');
          },
          onMessageSent: (message: any) => {
            const text = typeof message === 'string' ? message : (message?.content ?? '');
            if (text) {
              console.log('[LinkedIn Writer] User message tracked:', { content_length: text.length });
            }
          },
          onFeedbackGiven: (id: string, type: string) => {
            console.log('[LinkedIn Writer] Feedback given:', { id, type });
          }
        }}
      />
    </div>
  );
};

export default LinkedInWriter;
