import React from "react";
import { Box, Stack, Typography, Tabs, Tab, Chip } from "@mui/material";
import { EditNote as EditNoteIcon, ArrowBack as ArrowBackIcon, AudioFile as AudioFileIcon, Videocam as VideocamIcon, Mic as MicIcon } from "@mui/icons-material";
import { PodcastMode, Knobs } from "../types";
import { SecondaryButton } from "../ui";
import { useScriptEditor } from "./ScriptEditorContext";

interface ScriptEditorLayoutProps {
  onBackToResearch: () => void;
  knobs?: Knobs;
}

// Helper function to get voice display name
const getVoiceDisplayName = (voiceId?: string): string => {
  if (!voiceId) return "Default";
  if (voiceId === "Wise_Woman") return "Wise Woman";
  if (voiceId === "Friendly_Person") return "Friendly Person";
  if (voiceId === "Deep_Voice_Man") return "Deep Voice Man";
  if (voiceId === "Calm_Woman") return "Calm Woman";
  return voiceId.replace(/_/g, " ");
};

export const ScriptEditorLayout: React.FC<ScriptEditorLayoutProps> = ({ onBackToResearch, knobs }) => {
  const { podcastMode, scriptTab, setScriptTab } = useScriptEditor();

  const showTabs = podcastMode === "audio_video";
  const voiceId = knobs?.voice_id;
  const isCustomVoice = Boolean(voiceId && !voiceId.startsWith("builtin:") && 
    !["Wise_Woman", "Friendly_Person", "Inspirational_girl", "Deep_Voice_Man", "Calm_Woman", 
      "Casual_Guy", "Lively_Girl", "Patient_Man", "Young_Knight", "Determined_Man",
      "Lovely_Girl", "Decent_Boy", "Imposing_Manner", "Elegant_Man", "Abbess", 
      "Sweet_Girl_2", "Exuberant_Girl"].includes(voiceId));
  const voiceName = isCustomVoice ? "My Voice Clone" : getVoiceDisplayName(voiceId);

  return (
    <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 4 }}>
      <SecondaryButton onClick={onBackToResearch} startIcon={<ArrowBackIcon />}>
        Back to Research
      </SecondaryButton>
      <Box sx={{ flex: 1 }}>
        <Typography
          variant="h4"
          sx={{
            background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            fontWeight: 700,
            letterSpacing: "-0.02em",
            display: "flex",
            alignItems: "center",
            gap: 1.5,
            fontSize: { xs: "1.75rem", md: "2rem" },
          }}
        >
          <EditNoteIcon sx={{ fontSize: "2rem" }} />
          Script Editor
          {voiceId && (
            <Chip
              icon={<MicIcon sx={{ fontSize: "14px !important" }} />}
              label={`Active Voice: ${voiceName}`}
              size="small"
              sx={{ 
                ml: 2,
                background: isCustomVoice ? "rgba(16, 185, 129, 0.1)" : "rgba(99, 102, 241, 0.1)", 
                color: isCustomVoice ? "#10b981" : "#6366f1", 
                border: `1px solid ${isCustomVoice ? "rgba(16, 185, 129, 0.3)" : "rgba(99, 102, 241, 0.2)"}`,
                '& .MuiChip-icon': { color: isCustomVoice ? "#10b981" : "#6366f1" },
                fontWeight: 600,
                fontSize: "0.75rem",
              }}
            />
          )}
          {showTabs && (
            <Tabs 
              value={scriptTab} 
              onChange={(_, v) => setScriptTab(v)}
              sx={{ 
                ml: 3,
                minHeight: 32,
                '& .MuiTab-root': { 
                  minHeight: 32, 
                  py: 0.5,
                  px: 2,
                  fontSize: '0.8rem',
                }
              }}
            >
              <Tab 
                value="audio" 
                label="Audio Script" 
                icon={<AudioFileIcon sx={{ fontSize: '1rem' }} />} 
                iconPosition="start"
              />
              <Tab 
                value="video" 
                label="Video Script" 
                icon={<VideocamIcon sx={{ fontSize: '1rem' }} />} 
                iconPosition="start"
              />
            </Tabs>
          )}
        </Typography>
        <Typography variant="body2" sx={{ color: "#64748b", mt: 0.5, ml: 5.5 }}>
          Review and refine your podcast script before rendering
        </Typography>
      </Box>
    </Stack>
  );
};