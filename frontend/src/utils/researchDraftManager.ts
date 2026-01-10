/**
 * Research Draft Manager
 * 
 * Handles saving and restoring research drafts at each stage of the research process.
 * Drafts are saved to localStorage for quick access and to the database for persistence.
 */

import { WizardState } from '../components/Research/types/research.types';
import { AnalyzeIntentResponse, ResearchIntent, IntentDrivenResearchResponse } from '../components/Research/types/intent.types';
import { BlogResearchResponse } from '../services/blogWriterApi';
import { intentResearchApi } from '../api/intentResearchApi';

const DRAFT_STORAGE_KEY = 'alwrity_research_draft';
const DRAFT_ID_KEY = 'alwrity_research_draft_id';

export interface ResearchDraft {
  id?: string; // Database draft ID (database primary key)
  project_id?: string; // Project UUID (for lookups)
  keywords: string[];
  industry: string;
  target_audience: string;
  research_mode: string;
  config: any;
  current_step: number;
  intent_analysis?: AnalyzeIntentResponse | null;
  confirmed_intent?: ResearchIntent | null;
  intent_result?: IntentDrivenResearchResponse | null;
  legacy_result?: BlogResearchResponse | null;
  trends_config?: any;
  created_at: string;
  updated_at: string;
  is_complete: boolean;
}

/**
 * Save draft to localStorage
 */
export const saveDraftToStorage = (draft: Partial<ResearchDraft>): void => {
  try {
    const existingDraft = getDraftFromStorage();
    const now = new Date().toISOString();
    const mergedDraft: Partial<ResearchDraft> = {
      ...existingDraft,
      ...draft,
      updated_at: now,
      // Preserve project_id if it exists
      project_id: draft.project_id || existingDraft?.project_id,
      // Ensure required fields have defaults
      keywords: draft.keywords || existingDraft?.keywords || [],
      industry: draft.industry || existingDraft?.industry || 'General',
      target_audience: draft.target_audience || existingDraft?.target_audience || 'General',
      research_mode: draft.research_mode || existingDraft?.research_mode || 'comprehensive',
      config: draft.config || existingDraft?.config || {},
      current_step: draft.current_step || existingDraft?.current_step || 1,
      created_at: draft.created_at || existingDraft?.created_at || now,
      is_complete: draft.is_complete ?? existingDraft?.is_complete ?? false,
    };
    
    localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(mergedDraft));
    console.log('[ResearchDraftManager] ✅ Draft saved to localStorage:', {
      step: mergedDraft.current_step,
      hasKeywords: (mergedDraft.keywords?.length || 0) > 0,
      hasIntentAnalysis: !!mergedDraft.intent_analysis,
      hasConfirmedIntent: !!mergedDraft.confirmed_intent,
      hasResults: !!mergedDraft.intent_result || !!mergedDraft.legacy_result,
    });
  } catch (error) {
    console.error('[ResearchDraftManager] ❌ Failed to save draft to localStorage:', error);
  }
};

/**
 * Get draft from localStorage
 */
export const getDraftFromStorage = (): Partial<ResearchDraft> | null => {
  try {
    const draftJson = localStorage.getItem(DRAFT_STORAGE_KEY);
    if (!draftJson) return null;
    
    const draft = JSON.parse(draftJson);
    return draft;
  } catch (error) {
    console.error('[ResearchDraftManager] ❌ Failed to load draft from localStorage:', error);
    return null;
  }
};

/**
 * Clear draft from localStorage
 */
export const clearDraftFromStorage = (): void => {
  localStorage.removeItem(DRAFT_STORAGE_KEY);
  localStorage.removeItem(DRAFT_ID_KEY);
  console.log('[ResearchDraftManager] ✅ Draft cleared from localStorage');
};

/**
 * Create draft from wizard state
 */
export const createDraftFromState = (
  state: WizardState,
  options?: {
    intentAnalysis?: AnalyzeIntentResponse | null;
    confirmedIntent?: ResearchIntent | null;
    intentResult?: IntentDrivenResearchResponse | null;
    legacyResult?: BlogResearchResponse | null;
    trendsConfig?: any;
  }
): Partial<ResearchDraft> => {
  const now = new Date().toISOString();
  const existingDraft = getDraftFromStorage();
  
  return {
    id: existingDraft?.id,
    project_id: existingDraft?.project_id,
    keywords: state.keywords || [],
    industry: state.industry || 'General',
    target_audience: state.targetAudience || 'General',
    research_mode: state.researchMode || 'comprehensive',
    config: state.config || {},
    current_step: state.currentStep || 1,
    intent_analysis: options?.intentAnalysis || existingDraft?.intent_analysis,
    confirmed_intent: options?.confirmedIntent || existingDraft?.confirmed_intent,
    intent_result: options?.intentResult || existingDraft?.intent_result,
    legacy_result: options?.legacyResult || existingDraft?.legacy_result,
    trends_config: options?.trendsConfig || existingDraft?.trends_config,
    created_at: existingDraft?.created_at || now,
    updated_at: now,
    is_complete: !!(options?.intentResult || options?.legacyResult),
  };
};

/**
 * Save draft to database (Asset Library)
 * This creates/updates a draft in the database
 */
export const saveDraftToDatabase = async (
  draft: Partial<ResearchDraft>
): Promise<{ success: boolean; draft_id?: string; message: string }> => {
  try {
    const keywords = draft.keywords || [];
    const industry = draft.industry || 'General';
    const targetAudience = draft.target_audience || 'General';
    const currentStep = draft.current_step || 1;
    
    // Generate title from keywords
    const title = keywords.length > 0
      ? `Draft: ${keywords.slice(0, 3).join(', ')}`
      : 'Research Draft';
    
    // Generate description
    const description = draft.is_complete
      ? `Completed research on ${keywords.join(', ')}`
      : `Research draft - Step ${currentStep} of 3. ` +
        `Industry: ${industry}, Target Audience: ${targetAudience}`;
    
    // Convert draft to wizard state format for API
    const wizardState: WizardState = {
      currentStep,
      keywords,
      industry,
      targetAudience,
      researchMode: (draft.research_mode as any) || 'comprehensive',
      config: draft.config || {},
      results: draft.legacy_result || null, // Only use legacy_result for WizardState.results
    };
    
    // Save using existing API (pass project_id if we have one for updates)
    const existingProjectId = localStorage.getItem(DRAFT_ID_KEY) || draft.project_id;
    const response = await intentResearchApi.saveResearchProject(wizardState, {
      intentAnalysis: draft.intent_analysis || undefined,
      confirmedIntent: draft.confirmed_intent || undefined,
      intentResult: draft.intent_result || undefined,
      legacyResult: draft.legacy_result || undefined,
      title,
      description,
      projectId: existingProjectId || undefined, // Pass existing project_id (UUID) for updates
    });
    
    if (response.success && response.project_id) {
      // Store project_id (UUID) for future updates - this is what we use for lookups
      localStorage.setItem(DRAFT_ID_KEY, response.project_id);
      console.log('[ResearchDraftManager] ✅ Draft saved to database:', {
        project_id: response.project_id,
        db_id: response.asset_id
      });
    }
    
    return {
      success: response.success,
      draft_id: response.project_id || (response.asset_id ? String(response.asset_id) : undefined),
      message: response.message || (response.success ? 'Draft saved successfully' : 'Failed to save draft'),
    };
  } catch (error) {
    console.error('[ResearchDraftManager] ❌ Failed to save draft to database:', error);
    return {
      success: false,
      message: error instanceof Error ? error.message : 'Failed to save draft',
    };
  }
};

/**
 * Auto-save draft (saves to both localStorage and database)
 */
export const autoSaveDraft = async (
  state: WizardState,
  options?: {
    intentAnalysis?: AnalyzeIntentResponse | null;
    confirmedIntent?: ResearchIntent | null;
    intentResult?: IntentDrivenResearchResponse | null;
    legacyResult?: BlogResearchResponse | null;
    trendsConfig?: any;
  }
): Promise<void> => {
  // Always save to localStorage immediately
  const draft = createDraftFromState(state, options);
  saveDraftToStorage(draft);
  
  // Save to database if we have meaningful content
  // Only save to DB if:
  // 1. Intent analysis is complete (user clicked "intent and options"), OR
  // 2. Research is complete
  // NOTE: We do NOT save to DB just for keywords - only after user clicks "intent and options"
  const shouldSaveToDB = 
    !!options?.intentAnalysis || 
    !!options?.intentResult || 
    !!options?.legacyResult;
  
  if (shouldSaveToDB) {
    // For intent analysis completion, save immediately (no debounce)
    // For other saves (research completion), debounce to avoid excessive saves
    const isIntentAnalysisSave = !!options?.intentAnalysis && !options?.intentResult && !options?.legacyResult;
    
    if (isIntentAnalysisSave) {
      // Immediate save for intent analysis (user clicked "Intent and Options")
      try {
        await saveDraftToDatabase(draft);
        console.log('[ResearchDraftManager] ✅ Draft saved immediately after intent analysis');
      } catch (error) {
        // Don't block UI if database save fails - localStorage is already saved
        console.warn('[ResearchDraftManager] ⚠️ Database save failed, but localStorage is saved:', error);
      }
    } else {
      // Debounce database saves for other operations - only save every 5 seconds max
      const lastSaveTime = localStorage.getItem('alwrity_last_draft_db_save');
      const now = Date.now();
      const shouldSaveNow = !lastSaveTime || (now - parseInt(lastSaveTime)) > 5000;
      
      if (shouldSaveNow) {
        try {
          await saveDraftToDatabase(draft);
          localStorage.setItem('alwrity_last_draft_db_save', String(now));
        } catch (error) {
          // Don't block UI if database save fails - localStorage is already saved
          console.warn('[ResearchDraftManager] ⚠️ Database save failed, but localStorage is saved:', error);
        }
      }
    }
  }
};

/**
 * Restore draft from storage
 */
export const restoreDraft = (): Partial<ResearchDraft> | null => {
  return getDraftFromStorage();
};
