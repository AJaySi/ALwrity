import React, { useEffect } from 'react';
import { CopilotSidebar } from '@copilotkit/react-ui';
import { useCopilotReadable, useCopilotAction, useCopilotContext } from '@copilotkit/react-core';
import '@copilotkit/react-ui/styles.css';
import './styles/alwrity-copilot.css';
import RegisterLinkedInActions from './RegisterLinkedInActions';
import RegisterLinkedInEditActions from './RegisterLinkedInEditActions';
import RegisterLinkedInActionsEnhanced from './RegisterLinkedInActionsEnhanced';
import { Header, ContentEditor, LoadingIndicator, WelcomeMessage, ProgressTracker } from './components';
import { useLinkedInWriter } from './hooks/useLinkedInWriter';
import { useCopilotPersistence } from './utils/enhancedPersistence';
import { PlatformPersonaProvider, usePlatformPersonaContext } from '../shared/PersonaContext/PlatformPersonaProvider';

const useCopilotActionTyped = useCopilotAction as any;



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
    copilotContext,
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

  // Allow Copilot to edit the draft with specific operations
  useCopilotActionTyped({
    name: 'editLinkedInDraft',
    description: 'Apply a quick style or structural edit to the current LinkedIn draft',
    parameters: [
      { name: 'operation', type: 'string', description: 'The edit operation to perform', required: true, enum: ['Casual', 'Professional', 'TightenHook', 'AddCTA', 'Shorten', 'Lengthen'] }
    ],
    handler: async ({ operation }: { operation: string }) => {
      const currentDraft = draft || '';
      if (!currentDraft) {
        return { success: false, message: 'No draft content to edit' };
      }

      let editedContent = currentDraft;
      
      switch (operation) {
        case 'Casual':
          editedContent = currentDraft.replace(/\b(utilize|implement|facilitate|leverage)\b/gi, (match) => {
            const casual = { utilize: 'use', implement: 'put in place', facilitate: 'help', leverage: 'use' };
            return casual[match.toLowerCase() as keyof typeof casual] || match;
          });
          editedContent = editedContent.replace(/\./g, '! 😊');
          break;
          
        case 'Professional':
          editedContent = currentDraft.replace(/\b(use|put in place|help)\b/gi, (match) => {
            const professional = { use: 'utilize', 'put in place': 'implement', help: 'facilitate' };
            return professional[match.toLowerCase() as keyof typeof professional] || match;
          });
          editedContent = editedContent.replace(/! 😊/g, '.');
          break;
          
        case 'TightenHook':
          const lines = currentDraft.split('\n');
          if (lines.length > 0) {
            const firstLine = lines[0];
            const tightened = firstLine.length > 100 ? firstLine.substring(0, 100) + '...' : firstLine;
            lines[0] = tightened;
            editedContent = lines.join('\n');
          }
          break;
          
        case 'AddCTA':
          if (!/\b(call now|sign up|join|try|learn more|cta|comment|share|connect|message|dm|reach out)\b/i.test(currentDraft)) {
            editedContent = currentDraft + '\n\nWhat are your thoughts on this? Share your experience in the comments below!';
          }
          break;
          
        case 'Shorten':
          if (currentDraft.length > 200) {
            editedContent = currentDraft.substring(0, 200) + '...';
          }
          break;
          
        case 'Lengthen':
          if (currentDraft.length < 500) {
            editedContent = currentDraft + '\n\nThis approach has shown remarkable results in our industry. The key is to maintain consistency while adapting to changing market conditions.';
          }
          break;
          
        default:
          return { success: false, message: 'Unknown operation' };
      }

      // Use the edit action to show the diff preview
      window.dispatchEvent(new CustomEvent('linkedinwriter:applyEdit', { 
        detail: { target: editedContent } 
      }));
      
      return { success: true, message: `Draft ${operation.toLowerCase()} applied`, content: editedContent };
    }
  });

  // Intelligent, stage-aware suggestions
  const getIntelligentSuggestions = () => {
    const hasContent = draft && draft.trim().length > 0;
    const hasCTA = /\b(call now|sign up|join|try|learn more|cta|comment|share|connect|message|dm|reach out)\b/i.test(draft || '');
    const hasHashtags = /#[A-Za-z0-9_]+/.test(draft || '');
    const isLong = (draft || '').length > 500;
    
    // Debug logging for suggestions
    console.log('[LinkedIn Writer] Generating suggestions:', {
      hasContent,
      justGeneratedContent,
      draftLength: draft?.length || 0
    });

    if (!hasContent) {
      // Initial suggestions for content creation
      const initialSuggestions = [
        { title: '📝 LinkedIn Post', message: 'Use tool generateLinkedInPost to create a professional LinkedIn post for your industry.' },
        { title: '📄 Article', message: 'Use tool generateLinkedInArticle to write a thought leadership article.' },
        { title: '🎠 Carousel', message: 'Use tool generateLinkedInCarousel to create a multi-slide carousel presentation.' },
        { title: '🎬 Video Script', message: 'Use tool generateLinkedInVideoScript to draft a video script for LinkedIn.' },
        { title: '💬 Comment Response', message: 'Use tool generateLinkedInCommentResponse to craft a professional comment reply.' },
        { title: '🖼️ Generate Post Image', message: 'Use tool generateLinkedInImagePrompts to create professional images for your LinkedIn content.' },
        { title: '🎨 Visual Content', message: 'Create engaging visual content with AI-generated images optimized for LinkedIn.' }
      ];
      console.log('[LinkedIn Writer] Initial suggestions:', initialSuggestions);
      return initialSuggestions;
    } else {
        // Refinement suggestions for existing content - use direct edit actions
      const refinementSuggestions = [
        { title: '🙂 Make it casual', message: 'Use tool editLinkedInDraft with operation Casual' },
        { title: '💼 Make it professional', message: 'Use tool editLinkedInDraft with operation Professional' },
        { title: '✨ Tighten hook', message: 'Use tool editLinkedInDraft with operation TightenHook' },
        { title: '📣 Add a CTA', message: 'Use tool editLinkedInDraft with operation AddCTA' },
        { title: '✂️ Shorten', message: 'Use tool editLinkedInDraft with operation Shorten' },
        { title: '➕ Lengthen', message: 'Use tool editLinkedInDraft with operation Lengthen' }
      ];
      
      // Add special suggestions when content was just generated
      if (justGeneratedContent) {
        console.log('[LinkedIn Writer] Adding post-generation suggestions');
        refinementSuggestions.unshift(
          { 
            title: '🎉 Content Generated! Next Steps:', 
            message: 'Great! Your content is ready. Now let\'s enhance it with images and make it perfect for LinkedIn.' 
          },
          { 
            title: '🖼️ Generate Post Image', 
            message: 'Use tool generateLinkedInImagePrompts to create professional images for this LinkedIn post' 
          }
        );
      }

      // Add contextual suggestions based on content analysis
      if (!hasCTA) {
        refinementSuggestions.push({ title: '📣 Add CTA', message: 'Use tool editLinkedInDraft with operation AddCTA' });
      }
      if (!hasHashtags) {
        refinementSuggestions.push({ title: '🏷️ Add hashtags', message: 'Use tool addLinkedInHashtags' });
      }
      if (isLong) {
        refinementSuggestions.push({ title: '📝 Summarize intro', message: 'Use tool editLinkedInDraft with operation Shorten' });
      }
      
      // Add image generation suggestion when there's content
      if (draft && draft.trim().length > 0) {
        console.log('[LinkedIn Writer] Adding image generation suggestion');
        // Make image generation suggestion more prominent
        refinementSuggestions.push({ 
          title: '🖼️ Generate Post Image', 
          message: 'Use tool generateLinkedInImagePrompts to create professional images for this LinkedIn post'
        });
        
        // Add contextual image suggestions based on content type
        if (draft.includes('digital transformation') || draft.includes('technology') || draft.includes('innovation')) {
          refinementSuggestions.push({ 
            title: '🚀 Tech-Focused Image', 
            message: 'Use tool generateLinkedInImagePrompts to create technology-themed professional images for this post' 
          });
        } else if (draft.includes('business') || draft.includes('strategy') || draft.includes('growth')) {
          refinementSuggestions.push({ 
            title: '💼 Business Image', 
            message: 'Use tool generateLinkedInImagePrompts to create business-focused professional images for this post' 
          });
        }
      }

      console.log('[LinkedIn Writer] Final suggestions:', refinementSuggestions);
      return refinementSuggestions;
    }
  };

  return (
    <div className={`linkedin-writer ${className}`} style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Header
        userPreferences={userPreferences}
        chatHistory={chatHistory}
        showPreferencesModal={showPreferencesModal}
        showContextModal={showContextModal}
        context={context}
        onPreferencesModalChange={setShowPreferencesModal}
        onContextModalChange={setShowContextModal}
        onContextChange={handleContextChange}
        onPreferencesChange={handlePreferencesChange}
        onCopy={handleCopy}
        onClear={handleClear}
        onClearHistory={handleClearHistory}
        draft={draft}
        getHistoryLength={getHistoryLength}
      />
                  {/* Persona Integration Indicator */}
            {corePersona && !personaLoading && (
              <div 
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#f0f8ff',
                  borderBottom: '1px solid #e1e8ed',
                  fontSize: '12px',
                  color: '#666',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  cursor: 'help',
                  position: 'relative'
                }}
                title={`🎭 YOUR PERSONALIZED WRITING ASSISTANT

🤔 WHAT IS A PERSONA?
A persona is your unique writing style profile that AI uses to create content that sounds exactly like you. It's like having a digital twin of your writing voice!

🎯 HOW DOES IT HELP YOU?
✅ Generates content that matches your natural writing style
✅ Maintains consistent voice across all your LinkedIn posts
✅ Saves time by understanding your preferences automatically
✅ Optimizes content for LinkedIn's algorithm and your audience
✅ Provides personalized suggestions based on your industry

🧠 HOW WAS IT CREATED?
Your persona was built by analyzing:
• Your website content and writing patterns
• Your research preferences and content goals
• Your target audience and industry focus
• Your communication style and tone preferences
• LinkedIn-specific optimization requirements

🤖 HOW DOES COPILOTKIT USE IT?
The AI assistant now knows:
• Your preferred sentence length and structure
• Your go-to words and phrases to use/avoid
• Your professional tone and communication style
• LinkedIn-specific optimization strategies
• Your engagement patterns and posting preferences

🚀 HYPER-PERSONALIZATION ACHIEVED!
Instead of generic content, you get:
• Content that sounds authentically like you
• Industry-specific insights and terminology
• LinkedIn algorithm-optimized posts
• Professional networking strategies
• Personalized engagement tactics

📊 YOUR PERSONA DETAILS:
🎭 Name: ${corePersona.persona_name}
📋 Style: ${corePersona.archetype}
💭 Philosophy: ${corePersona.core_belief}
📈 Confidence: ${corePersona.confidence_score}% accuracy

🎯 LINKEDIN OPTIMIZATION:
• Optimal length: ${platformPersona?.content_format_rules?.optimal_length || '150-300 words'}
• Posting frequency: ${platformPersona?.engagement_patterns?.posting_frequency || '2-3 times per week'}
• Hashtag strategy: ${platformPersona?.lexical_features?.hashtag_strategy || '3-5 relevant hashtags'}
• Engagement style: ${platformPersona?.engagement_patterns?.interaction_style || 'conversational'}

💡 TRY THIS: Ask the AI to "generate a LinkedIn post about [your topic]" and watch how it automatically applies your persona to create content that sounds like you!`}
              >
                <span style={{ color: '#0073b1' }}>🎭</span>
                <span><strong>🎭 Your Writing Assistant:</strong> {corePersona.persona_name} ({corePersona.archetype})</span>
                <span style={{ marginLeft: 'auto', fontSize: '11px' }}>
                  {corePersona.confidence_score}% accuracy | 
                  Platform: LinkedIn Optimized
                </span>
                <span style={{ fontSize: '10px', color: '#999', marginLeft: '8px' }}>
                  (Hover for details)
                </span>
              </div>
            )}

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
        suggestions={getIntelligentSuggestions()}
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
