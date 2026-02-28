import React, { useState, useEffect } from "react";
import { Stack, Box, Typography, Divider, Chip, Paper, alpha, CircularProgress, TextField, IconButton, Tooltip, Select, MenuItem, FormControl, InputLabel, Switch, FormControlLabel } from "@mui/material";
import { Psychology as PsychologyIcon, Insights as InsightsIcon, Search as SearchIcon, Person as PersonIcon, AutoAwesome as AutoAwesomeIcon, Edit as EditIcon, Save as SaveIcon, Close as CloseIcon, Add as AddIcon, Delete as DeleteIcon, EditNote as EditNoteIcon } from "@mui/icons-material";
import { PodcastAnalysis, PodcastEstimate } from "./types";
import { GlassyCard, glassyCardSx, SecondaryButton } from "./ui";
import { Refresh as RefreshIcon } from "@mui/icons-material";
import { aiApiClient } from "../../api/client";

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
  onUpdateAnalysis
}) => {
  const [avatarBlobUrl, setAvatarBlobUrl] = useState<string | null>(null);
  const [avatarLoading, setAvatarLoading] = useState(false);
  const [avatarError, setAvatarError] = useState(false);
  
  // Edit states
  const [isEditing, setIsEditing] = useState(false);
  const [editedAnalysis, setEditedAnalysis] = useState<PodcastAnalysis | null>(null);

  // Sync editedAnalysis with analysis initially
  useEffect(() => {
    if (analysis && !editedAnalysis) {
      setEditedAnalysis(JSON.parse(JSON.stringify(analysis)));
    }
  }, [analysis]);

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

        {/* Inputs Section */}
        {(idea || duration || speakers || avatarUrl || avatarPrompt) && (
          <>
            <Box>
              <Typography
                variant="subtitle1"
                sx={{
                  color: "#0f172a",
                  fontWeight: 700,
                  mb: 1.5,
                  display: "flex",
                  alignItems: "center",
                  gap: 0.5,
                }}
              >
                Your Inputs
              </Typography>
              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: { xs: "1fr", md: avatarUrl ? "1fr 1fr" : "1fr" },
                  gap: 3,
                  alignItems: "flex-start",
                }}
              >
                {/* Left Column: Text Inputs */}
                <Stack spacing={1.5}>
                  {idea && (
                    <Box>
                      <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                        Podcast Idea
                      </Typography>
                      <Typography variant="body2" sx={{ color: "#0f172a", wordBreak: "break-word" }}>
                        {idea}
                      </Typography>
                    </Box>
                  )}
                  <Stack direction="row" spacing={2} flexWrap="wrap">
                    {duration !== undefined && (
                      <Box>
                        <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                          Duration
                        </Typography>
                        <Chip
                          label={`${duration} minutes`}
                          size="small"
                          sx={{ background: "#f1f5f9", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }}
                        />
                      </Box>
                    )}
                    {speakers !== undefined && (
                      <Box>
                        <Typography variant="caption" sx={{ color: "#64748b", fontWeight: 600, display: "block", mb: 0.5 }}>
                          Speakers
                        </Typography>
                        <Chip
                          label={`${speakers} ${speakers === 1 ? "speaker" : "speakers"}`}
                          size="small"
                          sx={{ background: "#f1f5f9", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }}
                        />
                      </Box>
                    )}
                  </Stack>
                  
                  {/* AI Prompt Used for Avatar Generation */}
                  {avatarUrl && (
                    <Box>
                      <Typography
                        variant="caption"
                        sx={{
                          color: "#64748b",
                          fontWeight: 600,
                          display: "flex",
                          alignItems: "center",
                          gap: 0.5,
                          mb: 0.75,
                        }}
                      >
                        <AutoAwesomeIcon sx={{ fontSize: 14 }} />
                        AI Generation Prompt
                      </Typography>
                      {avatarPrompt ? (
                        <Paper
                          sx={{
                            p: 1.5,
                            background: "#f8fafc",
                            border: "1px solid rgba(0,0,0,0.08)",
                            borderRadius: 1.5,
                            maxHeight: 200,
                            overflow: "auto",
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              color: "#475569",
                              fontFamily: "monospace",
                              fontSize: "0.75rem",
                              lineHeight: 1.6,
                              whiteSpace: "pre-wrap",
                              wordBreak: "break-word",
                              display: "block",
                            }}
                          >
                            {avatarPrompt}
                          </Typography>
                        </Paper>
                      ) : (
                        <Paper
                          sx={{
                            p: 1.5,
                            background: "#f1f5f9",
                            border: "1px solid rgba(0,0,0,0.08)",
                            borderRadius: 1.5,
                          }}
                        >
                          <Typography
                            variant="caption"
                            sx={{
                              color: "#64748b",
                              fontStyle: "italic",
                              fontSize: "0.75rem",
                            }}
                          >
                            Prompt not available (avatar was uploaded or generated before this feature was added)
                          </Typography>
                        </Paper>
                      )}
                    </Box>
                  )}
                </Stack>

                {/* Right Column: Presenter Avatar */}
                {avatarUrl && (
                  <Box>
                    <Typography
                      variant="caption"
                      sx={{
                        color: "#64748b",
                        fontWeight: 600,
                        display: "flex",
                        alignItems: "center",
                        gap: 0.5,
                        mb: 1,
                      }}
                    >
                      <PersonIcon sx={{ fontSize: 16 }} />
                      Presenter Avatar
                    </Typography>
                    <Box
                      sx={{
                        width: "100%",
                        maxWidth: { xs: "100%", md: 300 },
                        borderRadius: 2,
                        overflow: "hidden",
                        border: "1px solid rgba(102,126,234,0.2)",
                        background: alpha("#667eea", 0.05),
                        position: "relative",
                        aspectRatio: "1",
                        boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
                      }}
                    >
                      {avatarLoading ? (
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            height: "100%",
                            background: "#f8fafc",
                          }}
                        >
                          <CircularProgress size={40} />
                        </Box>
                      ) : avatarError ? (
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            height: "100%",
                            background: "#fef2f2",
                            color: "#dc2626",
                            p: 2,
                          }}
                        >
                          <Typography variant="caption" sx={{ textAlign: "center" }}>
                            Failed to load avatar
                          </Typography>
                        </Box>
                      ) : avatarBlobUrl ? (
                        <Box
                          component="img"
                          src={avatarBlobUrl}
                          alt="Podcast Presenter"
                          sx={{
                            width: "100%",
                            height: "100%",
                            objectFit: "cover",
                            display: "block",
                          }}
                          onError={(e) => {
                            console.error('[AnalysisPanel] Avatar image failed to load:', {
                              src: e.currentTarget.src,
                              avatarUrl,
                              avatarBlobUrl,
                            });
                            setAvatarError(true);
                          }}
                          onLoad={() => {
                            console.log('[AnalysisPanel] Avatar image loaded successfully');
                          }}
                        />
                      ) : null}
                    </Box>
                  </Box>
                )}
              </Box>
            </Box>
            <Divider sx={{ borderColor: "rgba(0,0,0,0.06)" }} />
          </>
        )}

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3 }}>
          <Stack spacing={3}>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, display: "flex", alignItems: "center", gap: 0.5 }}>
                <InsightsIcon fontSize="small" sx={{ color: "#4f46e5" }} />
                Target Audience
              </Typography>
              {isEditing ? (
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  size="small"
                  value={currentAnalysis.audience}
                  onChange={(e) => setEditedAnalysis({ ...currentAnalysis, audience: e.target.value })}
                  placeholder="Describe your target audience..."
                  sx={inputStyles}
                />
              ) : (
                <Typography variant="body2" sx={{ color: "#0f172a" }}>
                  {currentAnalysis.audience}
                </Typography>
              )}
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Content Type</Typography>
              {isEditing ? (
                <TextField
                  fullWidth
                  size="small"
                  value={currentAnalysis.contentType}
                  onChange={(e) => setEditedAnalysis({ ...currentAnalysis, contentType: e.target.value })}
                  placeholder="e.g. Interview, Narrative, Solo..."
                  sx={inputStyles}
                />
              ) : (
                <Chip label={currentAnalysis.contentType} size="small" sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }} />
              )}
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Top Keywords</Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
                {currentAnalysis.topKeywords.map((k) => (
                  <Chip
                    key={k}
                    label={k}
                    size="small"
                    variant="outlined"
                    onDelete={isEditing ? () => handleRemoveKeyword(k) : undefined}
                    sx={{
                      borderColor: "rgba(0,0,0,0.1)",
                      color: "#0f172a",
                      background: "#f8fafc",
                    }}
                  />
                ))}
              </Stack>
              {isEditing && (
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Add keyword and press Enter..."
                  sx={inputStyles}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddKeyword((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <IconButton size="small" onClick={(e) => {
                        const input = (e.currentTarget.parentElement?.parentElement?.querySelector('input') as HTMLInputElement);
                        handleAddKeyword(input.value);
                        input.value = '';
                      }}>
                        <AddIcon fontSize="small" sx={{ color: '#4f46e5' }} />
                      </IconButton>
                    )
                  }}
                />
              )}
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#111827", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                <EditNoteIcon fontSize="small" sx={{ color: "#4f46e5" }} />
                Suggested Episode Outlines
              </Typography>
              <Stack spacing={2}>
                {currentAnalysis.suggestedOutlines.map((o) => (
                  <Paper
                    key={o.id}
                    elevation={0}
                    sx={{
                      p: 2,
                      background: isEditing ? "#ffffff" : "#f8fafc",
                      border: "1px solid",
                      borderColor: isEditing ? "#e2e8f0" : "rgba(0,0,0,0.04)",
                      borderRadius: 2,
                      wordBreak: "break-word",
                      position: 'relative',
                      transition: "all 0.2s ease",
                      "&:hover": {
                        borderColor: "#4f46e5",
                        boxShadow: "0 4px 12px rgba(79, 70, 229, 0.05)"
                      }
                    }}
                  >
                    {isEditing ? (
                      <Stack spacing={2}>
                        <TextField
                          fullWidth
                          size="small"
                          label="Outline Title"
                          value={o.title}
                          onChange={(e) => handleUpdateOutline(o.id, 'title', e.target.value)}
                          sx={inputStyles}
                        />
                        <TextField
                          fullWidth
                          multiline
                          size="small"
                          label="Segments"
                          value={o.segments.join(' • ')}
                          onChange={(e) => handleUpdateOutline(o.id, 'segments', e.target.value.split(/•|,/).map(s => s.trim()).filter(Boolean))}
                          helperText="Use • or comma to separate segments"
                          sx={inputStyles}
                        />
                      </Stack>
                    ) : (
                      <>
                        <Typography variant="body1" sx={{ fontWeight: 800, mb: 1, color: "#111827" }}>
                          {o.title}
                        </Typography>
                        <Stack spacing={1}>
                          {o.segments.map((segment, idx) => (
                            <Box key={idx} sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
                              <Box sx={{ mt: 1, width: 6, height: 6, borderRadius: "50%", bgcolor: "#4f46e5", flexShrink: 0 }} />
                              <Typography variant="body2" sx={{ color: "#4b5563", lineHeight: 1.5 }}>
                                {segment}
                              </Typography>
                            </Box>
                          ))}
                        </Stack>
                      </>
                    )}
                  </Paper>
                ))}
              </Stack>
            </Box>
          </Stack>

          <Stack spacing={3}>
            {currentAnalysis.exaSuggestedConfig && (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", display: "flex", alignItems: "center", gap: 0.5 }}>
                  <SearchIcon fontSize="small" sx={{ color: "#4f46e5" }} />
                  Exa Research Suggestions
                </Typography>
                
                {isEditing ? (
                  <Stack spacing={2} sx={{ p: 2, border: '1px solid #e2e8f0', borderRadius: 2, bgcolor: '#ffffff' }}>
                    <Stack direction="row" spacing={2}>
                      <FormControl fullWidth size="small" sx={inputStyles}>
                        <InputLabel>Search Type</InputLabel>
                        <Select
                          value={currentAnalysis.exaSuggestedConfig.exa_search_type || 'auto'}
                          label="Search Type"
                          onChange={(e) => updateExaConfig('exa_search_type', e.target.value)}
                        >
                          <MenuItem value="auto">Auto</MenuItem>
                          <MenuItem value="neural">Neural</MenuItem>
                          <MenuItem value="keyword">Keyword</MenuItem>
                        </Select>
                      </FormControl>
                      <FormControl fullWidth size="small" sx={inputStyles}>
                        <InputLabel>Category</InputLabel>
                        <Select
                          value={currentAnalysis.exaSuggestedConfig.exa_category || 'news'}
                          label="Category"
                          onChange={(e) => updateExaConfig('exa_category', e.target.value)}
                        >
                          <MenuItem value="news">News</MenuItem>
                          <MenuItem value="research paper">Research Paper</MenuItem>
                          <MenuItem value="company">Company</MenuItem>
                          <MenuItem value="pdf">PDF</MenuItem>
                          <MenuItem value="tweet">Tweet</MenuItem>
                        </Select>
                      </FormControl>
                    </Stack>

                    <Stack direction="row" spacing={2} alignItems="center">
                      <FormControl fullWidth size="small" sx={inputStyles}>
                        <InputLabel>Date Range</InputLabel>
                        <Select
                          value={currentAnalysis.exaSuggestedConfig.date_range || 'all_time'}
                          label="Date Range"
                          onChange={(e) => updateExaConfig('date_range', e.target.value)}
                        >
                          <MenuItem value="all_time">All Time</MenuItem>
                          <MenuItem value="last_month">Last Month</MenuItem>
                          <MenuItem value="last_year">Last Year</MenuItem>
                        </Select>
                      </FormControl>
                      <TextField
                        type="number"
                        label="Max Sources"
                        size="small"
                        value={currentAnalysis.exaSuggestedConfig.max_sources || 10}
                        onChange={(e) => updateExaConfig('max_sources', parseInt(e.target.value))}
                        sx={{ ...inputStyles, width: 120 }}
                      />
                    </Stack>

                    <FormControlLabel
                      control={
                        <Switch 
                          size="small"
                          checked={currentAnalysis.exaSuggestedConfig.include_statistics || false} 
                          onChange={(e) => updateExaConfig('include_statistics', e.target.checked)}
                          sx={{ '& .MuiSwitch-track': { bgcolor: '#4f46e5' } }}
                        />
                      }
                      label={<Typography variant="body2" sx={{ color: '#111827', fontWeight: 500 }}>Include Statistics</Typography>}
                    />

                    <Stack spacing={1}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Prefer Domains"
                        placeholder="e.g. techcrunch.com, wired.com (press Enter)"
                        sx={inputStyles}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            const val = (e.target as HTMLInputElement).value.trim();
                            if (val) {
                              const domains = currentAnalysis.exaSuggestedConfig?.exa_include_domains || [];
                              updateExaConfig('exa_include_domains', [...domains, val]);
                              (e.target as HTMLInputElement).value = '';
                            }
                          }
                        }}
                      />
                      <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                        {(currentAnalysis.exaSuggestedConfig.exa_include_domains || []).map(d => (
                          <Chip key={d} label={d} size="small" onDelete={() => {
                            const domains = currentAnalysis.exaSuggestedConfig?.exa_include_domains?.filter(item => item !== d);
                            updateExaConfig('exa_include_domains', domains);
                          }} sx={{ bgcolor: '#f3f4f6', color: '#111827' }} />
                        ))}
                      </Stack>
                    </Stack>
                  </Stack>
                ) : (
                  <>
                    <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
                      {currentAnalysis.exaSuggestedConfig.exa_search_type && (
                        <Chip
                          label={`Search: ${currentAnalysis.exaSuggestedConfig.exa_search_type}`}
                          size="small"
                          sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                        />
                      )}
                      {currentAnalysis.exaSuggestedConfig.exa_category && (
                        <Chip
                          label={`Category: ${currentAnalysis.exaSuggestedConfig.exa_category}`}
                          size="small"
                          sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                        />
                      )}
                      {currentAnalysis.exaSuggestedConfig.date_range && (
                        <Chip
                          label={`Date: ${currentAnalysis.exaSuggestedConfig.date_range}`}
                          size="small"
                          sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                        />
                      )}
                      {typeof currentAnalysis.exaSuggestedConfig.include_statistics === "boolean" && (
                        <Chip
                          label={currentAnalysis.exaSuggestedConfig.include_statistics ? "Include stats" : "No stats needed"}
                          size="small"
                          sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                        />
                      )}
                      {currentAnalysis.exaSuggestedConfig.max_sources && (
                        <Chip
                          label={`Max sources: ${currentAnalysis.exaSuggestedConfig.max_sources}`}
                          size="small"
                          sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                        />
                      )}
                    </Stack>

                    {(currentAnalysis.exaSuggestedConfig.exa_include_domains?.length || currentAnalysis.exaSuggestedConfig.exa_exclude_domains?.length) && (
                      <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                        {currentAnalysis.exaSuggestedConfig.exa_include_domains?.length ? (
                          <Box>
                            <Typography variant="caption" sx={{ color: "#475569", fontWeight: 600, display: "block", mb: 0.5 }}>
                              Prefer domains
                            </Typography>
                            <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                              {currentAnalysis.exaSuggestedConfig.exa_include_domains.map((d) => (
                                <Chip key={d} label={d} size="small" sx={{ background: "#f8fafc", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }} />
                              ))}
                            </Stack>
                          </Box>
                        ) : null}

                        {currentAnalysis.exaSuggestedConfig.exa_exclude_domains?.length ? (
                          <Box>
                            <Typography variant="caption" sx={{ color: "#475569", fontWeight: 600, display: "block", mb: 0.5 }}>
                              Avoid domains
                            </Typography>
                            <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                              {currentAnalysis.exaSuggestedConfig.exa_exclude_domains.map((d) => (
                                <Chip key={d} label={d} size="small" sx={{ background: "#fff7ed", color: "#b45309", border: "1px solid rgba(180,83,9,0.25)" }} />
                              ))}
                            </Stack>
                          </Box>
                        ) : null}
                      </Stack>
                    )}
                  </>
                )}
              </Box>
            )}

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Title Suggestions</Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mb: isEditing ? 1.5 : 0 }}>
                {currentAnalysis.titleSuggestions.map((t) => (
                  <Chip
                    key={t}
                    label={t}
                    size="small"
                    onDelete={isEditing ? () => handleRemoveTitle(t) : undefined}
                    sx={{
                      cursor: isEditing ? "default" : "pointer",
                      color: "#0f172a",
                      background: "#f8fafc",
                      maxWidth: "100%",
                      whiteSpace: "normal",
                      height: "auto",
                      lineHeight: 1.3,
                      "& .MuiChip-label": {
                        whiteSpace: "normal",
                        wordBreak: "break-word",
                        textAlign: "left",
                        paddingTop: 0.25,
                        paddingBottom: 0.25,
                      },
                      "&:hover": isEditing ? {} : {
                        background: alpha("#667eea", 0.15),
                        border: "1px solid rgba(102,126,234,0.35)",
                      },
                    }}
                  />
                ))}
              </Stack>
              {isEditing && (
                <TextField
                  fullWidth
                  size="small"
                  placeholder="Add title suggestion..."
                  sx={inputStyles}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      handleAddTitle((e.target as HTMLInputElement).value);
                      (e.target as HTMLInputElement).value = '';
                    }
                  }}
                  InputProps={{
                    endAdornment: (
                      <IconButton size="small" onClick={(e) => {
                        const input = (e.currentTarget.parentElement?.parentElement?.querySelector('input') as HTMLInputElement);
                        handleAddTitle(input.value);
                        input.value = '';
                      }}>
                        <AddIcon fontSize="small" sx={{ color: '#4f46e5' }} />
                      </IconButton>
                    )
                  }}
                />
              )}
            </Box>
          </Stack>
        </Box>
      </Stack>
    </GlassyCard>
  );
};

