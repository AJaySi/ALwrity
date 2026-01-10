import { useState, useEffect } from 'react';
import { BlogResearchResponse } from '../../../services/blogWriterApi';
import { restoreProjectFromStorage, loadProjectFromDatabase, RestoredProject } from '../utils/projectRestoration';

/**
 * Hook to handle restoration of research projects from localStorage and database
 */
export const useProjectRestoration = () => {
  const [restoredProject, setRestoredProject] = useState<RestoredProject | null>(null);
  const [presetKeywords, setPresetKeywords] = useState<string[] | undefined>();
  const [presetIndustry, setPresetIndustry] = useState<string | undefined>();
  const [presetTargetAudience, setPresetTargetAudience] = useState<string | undefined>();
  const [presetMode, setPresetMode] = useState<any>();
  const [presetConfig, setPresetConfig] = useState<any>();
  const [results, setResults] = useState<BlogResearchResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadProject = async () => {
      // First check if there's a project ID in localStorage (from project list selection)
      const projectId = localStorage.getItem('alwrity_research_project_id');
      
      if (projectId) {
        // Load from database
        console.log('[ResearchDashboard] Loading project from database:', projectId);
        const project = await loadProjectFromDatabase(projectId);
        localStorage.removeItem('alwrity_research_project_id'); // Clear after loading
        
        if (project) {
          setRestoredProject(project);
          restoreProjectState(project);
          setLoading(false);
          return;
        }
      }

      // Fallback to localStorage restoration
      const project = restoreProjectFromStorage();
      if (project) {
        setRestoredProject(project);
        restoreProjectState(project);
      }
      
      setLoading(false);
    };

    const restoreProjectState = (project: RestoredProject) => {
      // Restore wizard state
      if (project.keywords) {
        setPresetKeywords(project.keywords);
      }
      if (project.industry) {
        setPresetIndustry(project.industry);
      }
      if (project.target_audience) {
        setPresetTargetAudience(project.target_audience);
      }
      if (project.research_mode) {
        setPresetMode(project.research_mode);
      }
      if (project.config) {
        setPresetConfig(project.config);
      }

      // Restore results if they exist
      if (project.intent_result) {
        setResults(project.intent_result as any);
      } else if (project.legacy_result) {
        setResults(project.legacy_result);
      }

      console.log('[ResearchDashboard] ✅ Research project restored successfully');
    };

    loadProject();
  }, []);

  const handleReset = () => {
    setPresetKeywords(undefined);
    setPresetIndustry(undefined);
    setPresetTargetAudience(undefined);
    setPresetMode(undefined);
    setPresetConfig(undefined);
    setResults(null);
    setRestoredProject(null);
  };

  return {
    restoredProject,
    presetKeywords,
    presetIndustry,
    presetTargetAudience,
    presetMode,
    presetConfig,
    results,
    loading,
    setPresetKeywords,
    setPresetIndustry,
    setPresetTargetAudience,
    setPresetMode,
    setPresetConfig,
    setResults,
    handleReset,
  };
};
