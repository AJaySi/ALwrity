import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, Divider, Chip, alpha, Button, IconButton, Popover, TextField, Tooltip } from "@mui/material";
import { Psychology as PsychologyIcon, Person as PersonIcon, Edit as EditIcon, Save as SaveIcon, Close as CloseIcon, Input as InputIcon, Groups as GroupsIcon, ListAlt as ListAltIcon, Lightbulb as TipsIcon, Article as ArticleIcon, AutoFixHigh as BibleIcon } from "@mui/icons-material";
import { PodcastAnalysis, PodcastEstimate, PodcastBible } from "./types";
import { GlassyCard, glassyCardSx, SecondaryButton } from "./ui";
import { Refresh as RefreshIcon } from "@mui/icons-material";
import { aiApiClient } from "../../api/client";
import { InputsTab, AudienceTab, OutlineTab, EpisodeDetailsTab, TakeawaysTab, GuestTab } from "./AnalysisPanel/tabs";

interface AnalysisPanelProps {
  analysis: PodcastAnalysis | null;
  estimate: PodcastEstimate | null;
  idea?: string;
  duration?: number;
  speakers?: number;
  voiceName?: string;
  podcastMode?: "audio_only" | "video_only" | "audio_video";
  avatarUrl?: string | null;
  avatarPrompt?: string | null;
  bible?: PodcastBible | null;
  onRegenerate?: () => void;
  onUpdateAnalysis?: (updatedAnalysis: PodcastAnalysis) => void;
  onUpdateBible?: (updatedBible: PodcastBible) => void;
}

type TabId = 'inputs' | 'audience' | 'outline' | 'details' | 'takeaways' | 'guest';

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
  voiceName,
  podcastMode,
  avatarUrl, 
  avatarPrompt, 
  bible,
  onRegenerate,
  onUpdateAnalysis,
  onUpdateBible
}) => {
  const [activeTab, setActiveTab] = useState<TabId>('inputs');
  const [avatarBlobUrl, setAvatarBlobUrl] = useState<string | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  const [bibleAnchorEl, setBibleAnchorEl] = useState<HTMLElement | null>(null);
  
  // Edit states
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnalysis, setEditedAnalysis] = useState<PodcastAnalysis | null>(null);
  const [editedBible, setEditedBible] = useState<PodcastBible | null>(null);

  const tabs: TabConfig[] = [
    { id: 'inputs', label: 'Your Inputs', icon: <InputIcon /> },
    { id: 'audience', label: 'Audience & Keywords', icon: <GroupsIcon /> },
    { id: 'outline', label: 'Outline', icon: <ListAltIcon /> },
    { id: 'details', label: 'Titles, Hook & CTA', icon: <ArticleIcon /> },
    { id: 'takeaways', label: 'Takeaways', icon: <TipsIcon /> },
    { id: 'guest', label: 'Guest Talking Points', icon: <PersonIcon /> },
  ];

  const tabButtonStyles = (isActive: boolean) => ({
    background: isActive 
      ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" 
      : "#f8fafc",
    color: isActive ? "#fff" : "#475569",
    border: isActive 
      ? "none" 
      : "1px solid #e2e8f0",
    borderRadius: 2.5,
    px: 2.5,
    py: 1.25,
    fontSize: "0.8rem",
    fontWeight: 600,
    textTransform: "none" as const,
    transition: "all 0.25s ease",
    boxShadow: isActive 
      ? "0 4px 12px rgba(102, 126, 234, 0.3)" 
      : "0 1px 2px rgba(0, 0, 0, 0.05)",
    "&:hover": {
      background: isActive 
        ? "linear-gradient(135deg, #764ba2 0%, #667eea 100%)" 
        : "#e2e8f0",
      transform: isActive ? "translateY(-1px)" : "none",
      boxShadow: isActive 
        ? "0 6px 16px rgba(102, 126, 234, 0.35)" 
        : "0 2px 4px rgba(0, 0, 0, 0.08)",
    },
    "&:active": {
      transform: "translateY(0)",
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
            {/* Bible Button */}
            {bible && (
              <Tooltip title="Podcast Bible - Hyper-personalized context">
                <IconButton
                  onClick={(e) => setBibleAnchorEl(e.currentTarget)}
                  sx={{
                    bgcolor: bibleAnchorEl ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" : "rgba(102, 126, 234, 0.1)",
                    border: "1px solid",
                    borderColor: bibleAnchorEl ? "transparent" : "rgba(102, 126, 234, 0.3)",
                    borderRadius: 2,
                    p: 1,
                    transition: "all 0.2s ease",
                    "&:hover": {
                      background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                      borderColor: "transparent",
                    },
                  }}
                >
                  <BibleIcon sx={{ color: bibleAnchorEl ? "#fff" : "#667eea", fontSize: 20 }} />
                </IconButton>
              </Tooltip>
            )}
            
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
              voiceName={voiceName}
              podcastMode={podcastMode}
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

          {activeTab === 'details' && (
            <EpisodeDetailsTab 
              analysis={currentAnalysis} 
              isEditing={isEditing}
              handleRemoveTitle={handleRemoveTitle}
              handleAddTitle={handleAddTitle}
            />
          )}

          {activeTab === 'takeaways' && (
            <TakeawaysTab analysis={currentAnalysis} />
          )}

          {activeTab === 'guest' && (
            <GuestTab analysis={currentAnalysis} />
          )}
        </Box>

        {/* Bible Popover */}
        <Popover
          open={Boolean(bibleAnchorEl)}
          anchorEl={bibleAnchorEl}
          onClose={() => setBibleAnchorEl(null)}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          PaperProps={{
            sx: {
              mt: 1,
              maxWidth: 420,
              borderRadius: 3,
              background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
              border: "1px solid rgba(102, 126, 234, 0.3)",
              boxShadow: "0 10px 40px rgba(102, 126, 234, 0.25)",
            },
          }}
        >
          <Box sx={{ p: 2.5 }}>
            <Stack spacing={2}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <BibleIcon sx={{ color: "#a78bfa", fontSize: 24 }} />
                <Typography variant="h6" sx={{ color: "#fff", fontWeight: 700 }}>
                  Podcast Bible
                </Typography>
                <Tooltip title="Hyper-personalized context derived from your onboarding data. This grounds all research and script generation.">
                  <IconButton size="small" sx={{ ml: 'auto' }}>
                    <Typography variant="caption" sx={{ color: "#94a3b8" }}>ℹ️</Typography>
                  </IconButton>
                </Tooltip>
              </Stack>

              {/* Host Persona */}
              <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)" }}>
                <Typography variant="caption" sx={{ color: "#a78bfa", fontWeight: 600, mb: 0.5, display: "block" }}>
                  Host Persona
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)", fontSize: "0.8rem" }}>
                  {bible?.host?.name || "Not set"} • {bible?.host?.background || "No background"} • {bible?.host?.vocal_style || "No style"}
                </Typography>
              </Box>

              {/* Audience DNA */}
              <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(34, 197, 94, 0.1)", border: "1px solid rgba(34, 197, 94, 0.2)" }}>
                <Typography variant="caption" sx={{ color: "#22c55e", fontWeight: 600, mb: 0.5, display: "block" }}>
                  Audience DNA
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)", fontSize: "0.8rem" }}>
                  {bible?.audience?.expertise_level || "General"} • {(bible?.audience?.interests || []).slice(0, 3).join(", ") || "Various interests"}
                </Typography>
              </Box>

              {/* Brand DNA */}
              <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(249, 115, 22, 0.1)", border: "1px solid rgba(249, 115, 22, 0.2)" }}>
                <Typography variant="caption" sx={{ color: "#f97316", fontWeight: 600, mb: 0.5, display: "block" }}>
                  Brand DNA
                </Typography>
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.8)", fontSize: "0.8rem" }}>
                  {bible?.brand?.industry || "No industry"} • {bible?.brand?.tone || "No tone"} • {bible?.brand?.communication_style || "No style"}
                </Typography>
              </Box>

              <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.5)", textAlign: "center", fontSize: "0.7rem" }}>
                Podcast Bible personalizes all AI generation for your unique voice
              </Typography>
            </Stack>
          </Box>
        </Popover>
      </Stack>
    </GlassyCard>
  );
};

