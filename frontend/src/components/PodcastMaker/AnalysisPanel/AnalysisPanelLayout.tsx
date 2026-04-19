import React from "react";
import { Box, Stack, Typography, Chip, Button, Divider } from "@mui/material";
import { Psychology as PsychologyIcon, Refresh as RefreshIcon, Edit as EditIcon, Save as SaveIcon, Close as CloseIcon, Mic as MicIcon } from "@mui/icons-material";
import { GlassyCard, glassyCardSx, SecondaryButton } from "../ui";
import { useAnalysisPanel, TabId } from "./AnalysisPanelContext";
import { PodcastEstimate } from "../types";

interface TabConfig {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

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

export const AnalysisPanelLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { 
    activeTab, 
    setActiveTab, 
    isEditing, 
    setIsEditing, 
    editedAnalysis, 
    setEditedAnalysis,
    analysis,
    estimate,
    onRegenerate,
    onUpdateAnalysis,
  } = useAnalysisPanel();

  const tabs: TabConfig[] = [
    { id: "inputs", label: "Your Inputs", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>📥</Box> },
    { id: "audience", label: "Audience & Keywords", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>👥</Box> },
    { id: "outline", label: "Outline", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>📋</Box> },
    { id: "details", label: "Titles, Hook & CTA", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>📄</Box> },
    { id: "takeaways", label: "Takeaways", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>💡</Box> },
    { id: "guest", label: "Guest Talking Points", icon: <Box component="span" sx={{ display: "flex", alignItems: "center" }}>👤</Box> },
  ];

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

  return (
    <GlassyCard
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#111827",
      }}
    >
      <Stack spacing={2.5}>
        {/* Header Section */}
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1}>
          <Stack direction="row" alignItems="center" gap={1.5} flex={1}>
            <Box
              sx={{
                width: 40,
                height: 40,
                borderRadius: 2,
                background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                boxShadow: "0 4px 12px rgba(102, 126, 234, 0.3)",
              }}
            >
              <PsychologyIcon sx={{ color: "#fff", fontSize: 22 }} />
            </Box>
            <Box>
              <Typography variant="h6" sx={{ fontWeight: 700, color: "#1e293b", fontSize: "1.1rem" }}>
                Personalize Your Podcast
              </Typography>
            </Box>

            {/* Estimate Display */}
            {estimate && (
              <Stack direction="row" alignItems="center" spacing={1.5} sx={{ ml: 2 }}>
                <Divider orientation="vertical" flexItem sx={{ height: 24, alignSelf: 'center', borderColor: "rgba(0,0,0,0.1)" }} />
                <Typography variant="subtitle2" fontWeight={700} sx={{ color: "#4f46e5" }}>
                  Est. Cost: ${estimate.total.toFixed(2)}
                </Typography>
                {estimate.voiceName && (
                  <Chip 
                    icon={<PsychologyIcon sx={{ fontSize: "12px !important" }} />}
                    label={estimate.voiceName}
                    size="small" 
                    variant="outlined" 
                    sx={{ 
                      height: 20, 
                      fontSize: '0.7rem', 
                      color: estimate.isCustomVoice ? "#10b981" : "#6366f1", 
                      borderColor: estimate.isCustomVoice ? "rgba(16, 185, 129, 0.3)" : "rgba(99, 102, 241, 0.2)",
                      bgcolor: estimate.isCustomVoice ? "rgba(16, 185, 129, 0.05)" : "rgba(99, 102, 241, 0.05)",
                      '& .MuiChip-icon': { color: estimate.isCustomVoice ? "#10b981" : "#6366f1" }
                    }} 
                  />
                )}
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

          <Stack direction="row" spacing={1.5} alignItems="center">
            {/* Regenerate Button */}
            <SecondaryButton
              startIcon={<RefreshIcon />}
              onClick={onRegenerate}
              sx={{
                background: "#fff",
                border: "1px solid #e2e8f0",
                color: "#475569",
                fontWeight: 600,
                fontSize: "0.8rem",
                px: 2,
                py: 0.75,
                "&:hover": {
                  background: "#f8fafc",
                  borderColor: "#cbd5e1",
                },
              }}
            >
              Regenerate
            </SecondaryButton>

            {/* Edit/Save/Cancel Buttons */}
            {isEditing ? (
              <Stack direction="row" spacing={1}>
                <Button
                  startIcon={<CloseIcon />}
                  onClick={handleCancel}
                  sx={{
                    color: "#64748b",
                    fontWeight: 600,
                    fontSize: "0.8rem",
                    px: 1.5,
                  }}
                >
                  Cancel
                </Button>
                <Button
                  startIcon={<SaveIcon />}
                  variant="contained"
                  onClick={handleSave}
                  sx={{
                    background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                    fontWeight: 600,
                    fontSize: "0.8rem",
                    px: 2,
                  }}
                >
                  Save
                </Button>
              </Stack>
            ) : (
              <Button
                startIcon={<EditIcon />}
                onClick={() => setIsEditing(true)}
                sx={{
                  color: "#667eea",
                  fontWeight: 600,
                  fontSize: "0.8rem",
                  px: 1.5,
                }}
              >
                Edit
              </Button>
            )}
          </Stack>
        </Stack>

        {/* Tab Navigation */}
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
          {tabs.map((tab) => (
            <Box
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              sx={tabButtonStyles(activeTab === tab.id)}
            >
              <Stack direction="row" spacing={1} alignItems="center">
                {tab.icon}
                <Box>{tab.label}</Box>
              </Stack>
            </Box>
          ))}
        </Stack>

        {/* Content Area - Render children (tab content) */}
        <Box sx={{ mt: 1 }}>
          {children}
        </Box>
      </Stack>
    </GlassyCard>
  );
};