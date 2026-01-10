/**
 * Utility functions for restoring research projects from localStorage and database
 */

import { intentResearchApi } from '../../../api/intentResearchApi';

export interface RestoredProject {
  keywords?: string[];
  industry?: string;
  target_audience?: string;
  research_mode?: any;
  config?: any;
  intent_result?: any;
  legacy_result?: any;
  intent_analysis?: any;
  confirmed_intent?: any;
  current_step?: number;
  title?: string;
}

/**
 * Restore research project from localStorage
 */
export const restoreProjectFromStorage = (): RestoredProject | null => {
  const restoredProjectJson = localStorage.getItem('restored_research_project');
  if (!restoredProjectJson) {
    return null;
  }

  try {
    const project = JSON.parse(restoredProjectJson);
    console.log('[ResearchDashboard] 🔄 Restoring research project:', project);
    
    // Clear restored project from localStorage after reading
    localStorage.removeItem('restored_research_project');
    
    return project;
  } catch (error) {
    console.error('[ResearchDashboard] ❌ Error restoring research project:', error);
    localStorage.removeItem('restored_research_project');
    return null;
  }
};

/**
 * Load research project from database by project ID
 */
export const loadProjectFromDatabase = async (projectId: string): Promise<RestoredProject | null> => {
  try {
    console.log('[ResearchDashboard] 🔄 Loading research project from database:', projectId);
    const project = await intentResearchApi.getResearchProject(projectId);
    
    if (!project) {
      console.error('[ResearchDashboard] ❌ Project not found:', projectId);
      return null;
    }

    // Convert database project to RestoredProject format
    const restoredProject: RestoredProject = {
      keywords: project.keywords || [],
      industry: project.industry || undefined,
      target_audience: project.target_audience || undefined,
      research_mode: project.research_mode || undefined,
      config: project.config || undefined,
      intent_result: project.intent_result || undefined,
      legacy_result: project.legacy_result || undefined,
      intent_analysis: project.intent_analysis || undefined,
      confirmed_intent: project.confirmed_intent || undefined,
      current_step: project.current_step || 1,
      title: project.title || undefined,
    };

    // Store in localStorage for restoration
    localStorage.setItem('restored_research_project', JSON.stringify(restoredProject));
    localStorage.setItem('alwrity_research_draft_id', project.project_id);
    
    // Also update the draft manager with the project data
    if (project.intent_analysis) {
      const draftData = {
        keywords: project.keywords,
        industry: project.industry,
        targetAudience: project.target_audience,
        researchMode: project.research_mode,
        config: project.config,
        intentAnalysis: project.intent_analysis,
        confirmedIntent: project.confirmed_intent,
        currentStep: project.current_step,
      };
      localStorage.setItem('alwrity_research_draft', JSON.stringify(draftData));
    }

    console.log('[ResearchDashboard] ✅ Research project loaded from database');
    return restoredProject;
  } catch (error) {
    console.error('[ResearchDashboard] ❌ Error loading research project from database:', error);
    return null;
  }
};
