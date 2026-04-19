import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { PodcastAnalysis, PodcastEstimate, PodcastBible } from "../types";

export type TabId = "inputs" | "audience" | "outline" | "details" | "takeaways" | "guest";

interface AnalysisPanelContextType {
  activeTab: TabId;
  setActiveTab: (tab: TabId) => void;
  analysis: PodcastAnalysis | null;
  estimate: PodcastEstimate | null;
  idea?: string;
  duration?: number;
  speakers?: number;
  avatarUrl?: string | null;
  avatarPrompt?: string | null;
  bible?: PodcastBible | null;
  isEditing: boolean;
  setIsEditing: (editing: boolean) => void;
  editedAnalysis: PodcastAnalysis | null;
  setEditedAnalysis: React.Dispatch<React.SetStateAction<PodcastAnalysis | null>>;
  currentAnalysis: PodcastAnalysis | null;
  handleRemoveKeyword: (keyword: string) => void;
  handleAddKeyword: (keyword: string) => void;
  handleRemoveTitle: (title: string) => void;
  handleAddTitle: (title: string) => void;
  handleUpdateOutline: (id: string | number, field: 'title' | 'segments', value: any) => void;
  onRegenerate?: () => void;
  onUpdateAnalysis?: (updatedAnalysis: PodcastAnalysis) => void;
  onUpdateBible?: (updatedBible: PodcastBible) => void;
}

const AnalysisPanelContext = createContext<AnalysisPanelContextType | undefined>(undefined);

interface AnalysisPanelProviderProps {
  children: ReactNode;
  analysis: PodcastAnalysis | null;
  estimate: PodcastEstimate | null;
  idea?: string;
  duration?: number;
  speakers?: number;
  avatarUrl?: string | null;
  avatarPrompt?: string | null;
  bible?: PodcastBible | null;
  onRegenerate?: () => void;
  onUpdateAnalysis?: (updatedAnalysis: PodcastAnalysis) => void;
  onUpdateBible?: (updatedBible: PodcastBible) => void;
}

export const AnalysisPanelProvider: React.FC<AnalysisPanelProviderProps> = ({
  children,
  analysis,
  estimate,
  idea,
  duration,
  speakers,
  avatarUrl,
  avatarPrompt,
  bible,
  onRegenerate,
  onUpdateAnalysis,
  onUpdateBible,
}) => {
  const [activeTab, setActiveTab] = useState<TabId>("inputs");
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnalysis, setEditedAnalysis] = useState<PodcastAnalysis | null>(null);

  useEffect(() => {
    if (analysis && !editedAnalysis) {
      setEditedAnalysis(JSON.parse(JSON.stringify(analysis)));
    }
  }, [analysis, editedAnalysis]);

  const currentAnalysis = isEditing && editedAnalysis ? editedAnalysis : analysis;

  const handleAddKeyword = (keyword: string) => {
    if (!editedAnalysis || !keyword.trim()) return;
    if (editedAnalysis.topKeywords.includes(keyword.trim())) return;
    setEditedAnalysis({
      ...editedAnalysis,
      topKeywords: [...editedAnalysis.topKeywords, keyword.trim()]
    });
  };

  const handleRemoveKeyword = (keyword: string) => {
    if (!editedAnalysis) return;
    setEditedAnalysis({
      ...editedAnalysis,
      topKeywords: editedAnalysis.topKeywords.filter(k => k !== keyword)
    });
  };

  const handleAddTitle = (title: string) => {
    if (!editedAnalysis || !title.trim()) return;
    setEditedAnalysis({
      ...editedAnalysis,
      titleSuggestions: [...editedAnalysis.titleSuggestions, title.trim()]
    });
  };

  const handleRemoveTitle = (title: string) => {
    if (!editedAnalysis) return;
    setEditedAnalysis({
      ...editedAnalysis,
      titleSuggestions: editedAnalysis.titleSuggestions.filter(t => t !== title)
    });
  };

  const handleUpdateOutline = (id: string | number, field: 'title' | 'segments', value: any) => {
    if (!editedAnalysis) return;
    setEditedAnalysis({
      ...editedAnalysis,
      suggestedOutlines: editedAnalysis.suggestedOutlines.map(o => 
        o.id === id ? { ...o, [field]: value } : o
      )
    });
  };

  const value: AnalysisPanelContextType = {
    activeTab,
    setActiveTab,
    analysis,
    estimate,
    idea,
    duration,
    speakers,
    avatarUrl,
    avatarPrompt,
    bible,
    isEditing,
    setIsEditing,
    editedAnalysis,
    setEditedAnalysis,
    currentAnalysis,
    handleRemoveKeyword,
    handleAddKeyword,
    handleRemoveTitle,
    handleAddTitle,
    handleUpdateOutline,
    onRegenerate,
    onUpdateAnalysis,
    onUpdateBible,
  };

  return (
    <AnalysisPanelContext.Provider value={value}>
      {children}
    </AnalysisPanelContext.Provider>
  );
};

export const useAnalysisPanel = (): AnalysisPanelContextType => {
  const context = useContext(AnalysisPanelContext);
  if (!context) {
    throw new Error("useAnalysisPanel must be used within AnalysisPanelProvider");
  }
  return context;
};