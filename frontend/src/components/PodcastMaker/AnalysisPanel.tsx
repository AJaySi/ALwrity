import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, Divider, Chip, Paper, alpha, CircularProgress, Button, Checkbox } from "@mui/material";
import { Psychology as PsychologyIcon, Insights as InsightsIcon, Search as SearchIcon, Person as PersonIcon, AutoAwesome as AutoAwesomeIcon, Edit as EditIcon, Save as SaveIcon, Close as CloseIcon, Add as AddIcon, EditNote as EditNoteIcon, Input as InputIcon, Groups as GroupsIcon, ListAlt as ListAltIcon, RecordVoiceOver as VoiceIcon, Lightbulb as TipsIcon, Quiz as TalkIcon } from "@mui/icons-material";
import { PodcastAnalysis, PodcastEstimate } from "./types";
import { GlassyCard, glassyCardSx, SecondaryButton } from "./ui";
import { Refresh as RefreshIcon } from "@mui/icons-material";
import { aiApiClient } from "../../api/client";
import { InputsTab, AudienceTab, OutlineTab, TitlesTab, HookTab, TakeawaysTab, GuestTab, CTATab } from "./AnalysisPanel/tabs";

interface AnalysisPanelProps {
  analysis: PodcastAnalysis | null;
  estimate: PodcastEstimate | null;
  idea?: string;
  duration?: number;
  speakers?: number;
  avatarUrl?: string | null;
  avatarPrompt?: string | null;
  onRegenerate?: () => void;
  onUpdateAnalysis?: (updatedAnalysis: PodcastAnalysis) => void;
  onRunResearch?: () => void;
  isResearchRunning?: boolean;
  selectedQueries?: Set<string>;
  onToggleQuery?: (queryId: string) => void;
  queries?: { id: string; query: string; rationale: string }[];
}

type TabId = 'inputs' | 'audience' | 'content' | 'outline' | 'titles' | 'hook' | 'takeaways' | 'cta' | 'guest';

interface TabConfig {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const inputStyles = {
  '& .MuiInputBase-input': { 
    color: '#111827 !important', 
    fontWeight: 500,
    WebkitTextFillColor: '#111827 !important', // Fix for some browsers
  },
  '& .MuiInputLabel-root': { 
    color: '#4b5563 !important',
  },
  '& .MuiOutlinedInput-root': {
    bgcolor: '#ffffff !important',
    '& fieldset': {
      borderColor: '#d1d5db !important',
    },
    '&:hover fieldset': {
      borderColor: '#4f46e5 !important',
    },
    '&.Mui-focused fieldset': {
      borderColor: '#4f46e5 !important',
    }
  },
  '& .MuiSelect-select': {
    color: '#111827 !important',
    WebkitTextFillColor: '#111827 !important',
  }
};

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ 
  analysis, 
  estimate,
  idea, 
  duration, 
  speakers, 
  avatarUrl, 
  avatarPrompt, 
  onRegenerate,
  onUpdateAnalysis,
  onRunResearch,
  isResearchRunning,
  selectedQueries,
  onToggleQuery,
  queries
}) => {
  const [activeTab, setActiveTab] = useState<TabId>('inputs');
  const [avatarBlobUrl, setAvatarBlobUrl] = useState<string | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  
  // Edit states
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnalysis, setEditedAnalysis] = useState<PodcastAnalysis | null>(null);

  const tabs: TabConfig[] = [
    { id: 'inputs', label: 'Your Inputs', icon: <InputIcon /> },
    { id: 'audience', label: 'Audience', icon: <GroupsIcon /> },
    { id: 'content', label: 'Content', icon: <ListAltIcon /> },
    { id: 'outline', label: 'Outline', icon: <ListAltIcon /> },
    { id: 'titles', label: 'Titles', icon: <EditNoteIcon /> },
    { id: 'hook', label: 'Hook', icon: <AutoAwesomeIcon /> },
    { id: 'takeaways', label: 'Takeaways', icon: <TipsIcon /> },
    { id: 'guest', label: 'Guest', icon: <PersonIcon /> },
    { id: 'cta', label: 'CTA', icon: <VoiceIcon /> },
  ];

  const tabButtonStyles = (isActive: boolean) => ({
    background: isActive 
      ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
      : "transparent",
    color: isActive ? "#fff" : "#64748b",
    border: isActive ? "none" : "1px solid rgba(0,0,0,0.1)",
    borderRadius: 2,
    px: 2,
    py: 1,
    fontSize: "0.75rem",
    fontWeight: 600,
    textTransform: "none" as const,
    transition: "all 0.2s ease",
    "&:hover": {
      background: isActive 
        ? "linear-gradient(135deg, #764ba2 0%, #667eea 100%)" 
        : "rgba(102,126,234,0.08)",
    },
  });

  // Sync editedAnalysis with analysis initially
  useEffect(() => {
    if (analysis && !editedAnalysis) {
      setEditedAnalysis(JSON.parse(JSON.stringify(analysis)));
    }
  }, [analysis, editedAnalysis]);

  const handleSave = () => {
    if (editedAnalysis && onUpdateAnalysis) {
      console.log('[AnalysisPanel] Saving updated analysis:', editedAnalysis);
      onUpdateAnalysis(JSON.parse(JSON.stringify(editedAnalysis)));
    }
    setIsEditing(false);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditedAnalysis(JSON.parse(JSON.stringify(analysis)));
  };

  const updateExaConfig = (field: string, value: any) => {
    if (!editedAnalysis) return;
    setEditedAnalysis({
      ...editedAnalysis,
      exaSuggestedConfig: {
        ...(editedAnalysis.exaSuggestedConfig || {}),
        [field]: value
      }
    });
  };

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

  // Load avatar image as blob for authenticated URLs
  useEffect(() => {
    if (!avatarUrl) {
      setAvatarBlobUrl(null);
      setAvatarError(false);
      return;
    }

    // Check if it's already a blob URL
    if (avatarUrl.startsWith('blob:')) {
      setAvatarBlobUrl(avatarUrl);
      return;
    }

    // Check if it's an authenticated endpoint
    const isAuthenticatedEndpoint = avatarUrl.includes('/api/podcast/images/') || avatarUrl.includes('/api/podcast/avatar/');
    
    let currentBlobUrl: string | null = null;
    
    if (isAuthenticatedEndpoint) {
      setAvatarLoading(true);
      setAvatarError(false);
      
      const loadAvatarBlob = async () => {
        try {
          const response = await aiApiClient.get(avatarUrl, { responseType: 'blob' });
          const blobUrl = URL.createObjectURL(response.data);
          currentBlobUrl = blobUrl;
          setAvatarBlobUrl(blobUrl);
          setAvatarError(false);
        } catch (error) {
          console.error('[AnalysisPanel] Failed to load avatar as blob:', error);
          // Fallback: try with query token
          try {
            const token = localStorage.getItem('clerk_dashboard_token') || '';
            if (token) {
              const urlWithToken = `${avatarUrl}?token=${encodeURIComponent(token)}`;
              setAvatarBlobUrl(urlWithToken);
            } else {
              setAvatarError(true);
            }
          } catch (fallbackError) {
            console.error('[AnalysisPanel] Fallback avatar loading failed:', fallbackError);
            setAvatarError(true);
          }
        } finally {
          setAvatarLoading(false);
        }
      };

      loadAvatarBlob();

      // Cleanup blob URL on unmount or when avatarUrl changes
      return () => {
        if (currentBlobUrl && currentBlobUrl.startsWith('blob:')) {
          URL.revokeObjectURL(currentBlobUrl);
        }
        // Also cleanup any previous blob URL from state
        setAvatarBlobUrl((prev) => {
          if (prev && prev.startsWith('blob:') && prev !== currentBlobUrl) {
            URL.revokeObjectURL(prev);
          }
          return null;
        });
      };
    } else {
      // Direct URL, use as-is
      setAvatarBlobUrl(avatarUrl);
    }
  }, [avatarUrl]);

  if (!analysis) return null;
  const currentAnalysis = isEditing && editedAnalysis ? editedAnalysis : analysis;

  console.log('[AnalysisPanel] Rendering:', { isEditing, hasEditedAnalysis: !!editedAnalysis });

  return (
    <GlassyCard
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className="light-theme-container"
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#111827",
      }}
      aria-label="analysis-panel"
    >
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="center">
          <Stack direction="row" alignItems="center" spacing={2} flex={1}>
            <Typography
              variant="h6"
              sx={{
                color: "#1e293b",
                fontWeight: 800,
                display: "flex",
                alignItems: "center",
                gap: 1,
                whiteSpace: "nowrap"
              }}
            >
              <PsychologyIcon sx={{ color: "#4f46e5" }} />
              AI Analysis
            </Typography>
            
            {estimate && (
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ ml: 2, flex: 1, overflow: 'hidden' }}>
                <Divider orientation="vertical" flexItem sx={{ height: 24, alignSelf: 'center', borderColor: "rgba(0,0,0,0.1)" }} />
                <Typography variant="subtitle2" fontWeight={700} sx={{ color: "#4f46e5" }}>
                  Est. Cost: ${estimate.total.toFixed(2)}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ display: { xs: 'none', lg: 'flex' } }}>
                  <Chip 
                    label={`Voice: $${estimate.ttsCost.toFixed(2)}`} 
                    size="small" 
                    variant="outlined" 
                    sx={{ height: 20, fontSize: '0.7rem', color: "#64748b", borderColor: "rgba(0,0,0,0.15)", bgcolor: "rgba(0,0,0,0.02)" }} 
                  />
                  <Chip 
                    label={`Visuals: $${estimate.avatarCost.toFixed(2)}`} 
                    size="small" 
                    variant="outlined" 
                    sx={{ height: 20, fontSize: '0.7rem', color: "#64748b", borderColor: "rgba(0,0,0,0.15)", bgcolor: "rgba(0,0,0,0.02)" }} 
                  />
                  <Chip 
                    label={`Research: $${estimate.researchCost.toFixed(2)}`} 
                    size="small" 
                    variant="outlined" 
                    sx={{ height: 20, fontSize: '0.7rem', color: "#64748b", borderColor: "rgba(0,0,0,0.15)", bgcolor: "rgba(0,0,0,0.02)" }} 
                  />
                </Stack>
              </Stack>
            )}
          </Stack>

          <Stack direction="row" spacing={1}>
            {isEditing ? (
              <>
                <SecondaryButton 
                  onClick={handleSave} 
                  startIcon={<SaveIcon />} 
                  sx={{ 
                    color: '#059669', 
                    borderColor: '#10b981', 
                    bgcolor: 'white',
                    fontWeight: 600,
                    '&:hover': { bgcolor: alpha('#10b981', 0.05) } 
                  }}
                >
                  Save Changes
                </SecondaryButton>
                <SecondaryButton 
                  onClick={handleCancel} 
                  startIcon={<CloseIcon />}
                  sx={{ color: '#4b5563', borderColor: '#d1d5db', bgcolor: 'white' }}
                >
                  Cancel
                </SecondaryButton>
              </>
            ) : (
              <>
                <SecondaryButton 
                  onClick={() => setIsEditing(true)} 
                  startIcon={<EditIcon />}
                  sx={{ color: '#4f46e5', borderColor: '#4f46e5', bgcolor: 'white', fontWeight: 600 }}
                >
                  Edit Analysis
                </SecondaryButton>
                <SecondaryButton 
                  onClick={onRegenerate} 
                  startIcon={<RefreshIcon />} 
                  tooltip="Regenerate analysis with different parameters"
                  sx={{ color: '#4b5563', borderColor: '#d1d5db', bgcolor: 'white' }}
                >
                  Regenerate
                </SecondaryButton>
              </>
            )}
          </Stack>
        </Stack>

        <Divider sx={{ borderColor: "rgba(0,0,0,0.06)" }} />

        {/* AI Futuristic Tab Navigation */}
        <Stack direction="row" flexWrap="wrap" gap={1} sx={{ mb: 2 }}>
          {tabs.map((tab) => (
            <Button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              startIcon={tab.icon}
              sx={tabButtonStyles(activeTab === tab.id)}
            >
              {tab.label}
            </Button>
          ))}
        </Stack>

        {/* Tab Content */}
        <Box sx={{ minHeight: 300 }}>
          {activeTab === 'inputs' && (
            <InputsTab 
              idea={idea} 
              duration={duration} 
              speakers={speakers} 
              avatarUrl={avatarUrl} 
              avatarPrompt={avatarPrompt}
              avatarBlobUrl={avatarBlobUrl}
              avatarLoading={avatarLoading}
              avatarError={avatarError}
            />
          )}

          {activeTab === 'audience' && (
            <AudienceTab 
              analysis={currentAnalysis} 
              isEditing={isEditing}
              editedAnalysis={editedAnalysis}
              setEditedAnalysis={setEditedAnalysis}
              handleRemoveKeyword={handleRemoveKeyword}
              handleAddKeyword={handleAddKeyword}
              handleRemoveTitle={handleRemoveTitle}
              handleAddTitle={handleAddTitle}
              handleUpdateOutline={handleUpdateOutline}
              updateExaConfig={updateExaConfig}
            />
          )}

          {activeTab === 'outline' && (
            <OutlineTab 
              analysis={currentAnalysis} 
              isEditing={isEditing}
              onUpdateOutline={handleUpdateOutline}
            />
          )}

          {activeTab === 'titles' && (
            <TitlesTab 
              analysis={currentAnalysis} 
              isEditing={isEditing}
              handleRemoveTitle={handleRemoveTitle}
              handleAddTitle={handleAddTitle}
            />
          )}

          {activeTab === 'hook' && (
            <HookTab analysis={currentAnalysis} />
          )}

          {activeTab === 'takeaways' && (
            <TakeawaysTab analysis={currentAnalysis} />
          )}

          {activeTab === 'guest' && (
            <GuestTab analysis={currentAnalysis} />
          )}

          {activeTab === 'cta' && (
            <CTATab analysis={currentAnalysis} />
          )}
        </Box>

        {/* Research Section - Separate from tabs */}
        <Divider sx={{ borderColor: "rgba(0,0,0,0.06)", my: 2 }} />
        
        <Box>
          <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
            <Typography variant="subtitle1" sx={{ color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
              <SearchIcon sx={{ color: "#4f46e5" }} />
              Research Queries
              {selectedQueries && selectedQueries.size > 0 && (
                <Chip 
                  label={`${selectedQueries.size} selected`} 
                  size="small" 
                  sx={{ ml: 1, height: 20, fontSize: "0.65rem", bgcolor: "#4f46e5", color: "#fff" }} 
                />
              )}
            </Typography>
            {onRunResearch && (
              <Button
                variant="contained"
                size="small"
                onClick={onRunResearch}
                disabled={isResearchRunning || !selectedQueries || selectedQueries.size === 0}
                startIcon={isResearchRunning ? <CircularProgress size={16} color="inherit" /> : <SearchIcon />}
                sx={{
                  background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                  color: "#fff",
                  fontWeight: 600,
                  fontSize: "0.75rem",
                  px: 2,
                  py: 0.75,
                  borderRadius: 2,
                  textTransform: "none",
                  "&:hover": {
                    background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
                  },
                  "&:disabled": {
                    background: "#94a3b8",
                  }
                }}
              >
                {isResearchRunning ? "Running..." : "Run Research"}
              </Button>
            )}
          </Stack>

          {!analysis?.research_queries || analysis.research_queries.length === 0 ? (
            <Typography variant="body2" sx={{ color: "#64748b", fontStyle: "italic" }}>
              No research queries yet. Click "Regenerate Analysis" to generate research queries based on your podcast idea.
            </Typography>
          ) : (
            <Stack spacing={1.5}>
              {(queries || analysis.research_queries?.map((rq, idx) => ({ id: `query-${idx}`, ...rq }))).map((rq: { id: string; query: string; rationale: string }, idx: number) => {
                const queryId = rq.id;
                const isSelected = selectedQueries?.has(queryId) || false;
                return (
                  <Paper 
                    key={idx} 
                    elevation={0} 
                    sx={{ 
                      p: 2, 
                      bgcolor: isSelected ? "#f0f9ff" : "#f8fafc", 
                      border: `1px solid ${isSelected ? 'rgba(79,70,229,0.4)' : 'rgba(0,0,0,0.08)'}`,
                      borderRadius: 2,
                      transition: "all 0.2s ease",
                      cursor: onToggleQuery ? "pointer" : "default",
                      "&:hover": onToggleQuery ? {
                        borderColor: "rgba(79,70,229,0.3)",
                        bgcolor: "#f8fafc"
                      } : {}
                    }}
                    onClick={() => onToggleQuery?.(queryId)}
                  >
                    <Stack direction="row" alignItems="flex-start" gap={1.5}>
                      <Checkbox
                        checked={isSelected}
                        onChange={() => onToggleQuery?.(queryId)}
                        sx={{
                          color: "#64748b",
                          "&.Mui-checked": {
                            color: "#4f46e5",
                          },
                          padding: 0.5,
                        }}
                      />
                      <Chip label={idx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#4f46e5", color: "#fff" }} />
                      <Box>
                        <Typography variant="body2" sx={{ color: "#0f172a", fontWeight: 600, mb: 0.5 }}>
                          {rq.query}
                        </Typography>
                        <Typography variant="caption" sx={{ color: "#64748b" }}>
                          Rationale: {rq.rationale}
                        </Typography>
                      </Box>
                    </Stack>
                  </Paper>
                );
              })}
            </Stack>
          )}
        </Box>
      </Stack>
    </GlassyCard>
  );
};

