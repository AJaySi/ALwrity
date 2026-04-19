import React from "react";
import { Stack, Box, Typography, Alert, Paper } from "@mui/material";
import { Info as InfoIcon, ExpandMore as ExpandMoreIcon, ExpandLess as ExpandLessIcon } from "@mui/icons-material";
import { useScriptEditor } from "../ScriptEditorContext";

interface FormatItem {
  num: string;
  title: string;
  desc: string;
}

const formatItems: FormatItem[] = [
  { num: "1", title: "Natural Pauses & Rhythm", desc: "The script includes strategic pauses between lines and when speakers change. This creates natural breathing patterns and conversation flow." },
  { num: "2", title: "Emphasis Markers", desc: "Lines marked with emphasis help highlight important points, statistics, or key insights." },
  { num: "3", title: "Short, Conversational Sentences", desc: "The script uses shorter sentences written in a conversational style that matches how people actually speak." },
  { num: "4", title: "Scene-Specific Emotions", desc: "Each scene has an emotional tone that guides the AI voice's delivery." },
  { num: "5", title: "Optimized for Podcast Narration", desc: "The script is optimized with slightly slower pacing and natural pronunciation settings." },
];

export const ScriptEditorInfoPanel: React.FC = () => {
  const { showScriptFormatInfo, setShowScriptFormatInfo } = useScriptEditor();

  return (
    <Paper
      sx={{
        p: 3,
        background: "linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%)",
        border: "1px solid rgba(99, 102, 241, 0.15)",
        borderRadius: 2,
      }}
    >
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: showScriptFormatInfo ? 2 : 0 }}>
        <Stack direction="row" alignItems="center" spacing={1.5}>
          <Box sx={{ width: 40, height: 40, borderRadius: "50%", background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <InfoIcon sx={{ color: "#ffffff", fontSize: "1.5rem" }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "1.1rem" }}>
              Why This Script Format?
            </Typography>
            <Typography variant="body2" sx={{ color: "#64748b", mt: 0.25 }}>
              Understanding how your script creates natural, human-like audio
            </Typography>
          </Box>
        </Stack>
        <Box
          sx={{
            color: "#6366f1",
            cursor: "pointer",
            p: 0.5,
            borderRadius: 1,
            "&:hover": { background: "rgba(99, 102, 241, 0.1)" },
          }}
          onClick={() => setShowScriptFormatInfo(!showScriptFormatInfo)}
        >
          {showScriptFormatInfo ? <ExpandLessIcon /> : <ExpandMoreIcon />}
        </Box>
      </Stack>

      {showScriptFormatInfo && (
        <Stack spacing={2.5}>
          <Typography variant="body2" sx={{ color: "#0f172a", lineHeight: 1.8 }}>
            Our AI script generator creates scripts specifically optimized for <strong style={{ fontWeight: 600 }}>high-quality text-to-speech</strong>. The format you see here is designed to produce audio that sounds natural and human-like, not robotic.
          </Typography>
          <Stack spacing={2}>
            {formatItems.map((item) => (
              <Box key={item.num} sx={{ display: "flex", gap: 2 }}>
                <Box sx={{ minWidth: 32, height: 32, borderRadius: "8px", background: "linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  <Typography variant="body2" sx={{ color: "#6366f1", fontWeight: 700 }}>{item.num}</Typography>
                </Box>
                <Box>
                  <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600, mb: 0.5 }}>{item.title}</Typography>
                  <Typography variant="body2" sx={{ color: "#475569", lineHeight: 1.7 }}>{item.desc}</Typography>
                </Box>
              </Box>
            ))}
          </Stack>
          <Alert severity="info" sx={{ background: "rgba(99, 102, 241, 0.06)", border: "1px solid rgba(99, 102, 241, 0.15)", "& .MuiAlert-icon": { color: "#6366f1" } }}>
            <Typography variant="body2" sx={{ color: "#0f172a", lineHeight: 1.7 }}>
              <strong style={{ fontWeight: 600 }}>Tip:</strong> You can edit any line or scene to match your preferences. The format will be preserved when rendering.
            </Typography>
          </Alert>
        </Stack>
      )}
    </Paper>
  );
};