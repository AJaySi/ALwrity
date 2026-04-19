import React from "react";
import { Stack, Box, Typography, Paper, LinearProgress } from "@mui/material";
import { AudioFile as AudioFileIcon } from "@mui/icons-material";
import { useScriptEditor } from "../ScriptEditorContext";
import { PrimaryButton } from "../../ui";

export const ScriptEditorAudioPanel: React.FC = () => {
  const { activeScript, needsAudioGeneration, generatingBatchAudio, batchAudioProgress, generateAllAudio } = useScriptEditor();

  if (!(needsAudioGeneration ?? false)) {
    return null;
  }

  return (
    <Paper
      sx={{
        p: 2,
        background: "linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.08) 100%)",
        border: "1px solid rgba(16, 185, 129, 0.2)",
        borderRadius: 2,
      }}
    >
      <Stack direction={{ xs: "column", sm: "row" }} spacing={2} alignItems="center" justifyContent="space-between">
        <Box>
          <Typography variant="subtitle1" sx={{ color: "#059669", fontWeight: 600, display: "flex", alignItems: "center", gap: 1 }}>
            <AudioFileIcon /> Generate All Audio
          </Typography>
          <Typography variant="body2" sx={{ color: "#64748b", mt: 0.5 }}>
            {activeScript && `${activeScript.scenes.filter(s => !s.audioUrl).length} scenes need audio`}
          </Typography>
        </Box>
        <PrimaryButton
          onClick={generateAllAudio}
          disabled={generatingBatchAudio}
          loading={generatingBatchAudio}
          startIcon={<AudioFileIcon />}
          sx={{ background: "linear-gradient(135deg, #10b981 0%, #059669 100%)" }}
        >
          {generatingBatchAudio 
            ? (batchAudioProgress ? `Generating ${batchAudioProgress.completed}/${batchAudioProgress.total}...` : "Generating...") 
            : "Generate All Audio"}
        </PrimaryButton>
      </Stack>
      {(batchAudioProgress !== null && batchAudioProgress !== undefined) && (
        <LinearProgress 
          variant="determinate" 
          value={(batchAudioProgress.completed / batchAudioProgress.total) * 100} 
          sx={{ mt: 2, height: 8, borderRadius: 4 }} 
        />
      )}
    </Paper>
  );
};