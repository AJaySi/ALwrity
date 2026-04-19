import React from "react";
import { Stack, Typography, Paper, Alert, alpha } from "@mui/material";
import { Download as DownloadIcon, Refresh as RefreshIcon } from "@mui/icons-material";
import { useScriptEditor } from "../ScriptEditorContext";
import { PrimaryButton, SecondaryButton } from "../../ui";
import { InlineAudioPlayer } from "../../InlineAudioPlayer";
import { aiApiClient } from "../../../../api/client";

interface ScriptEditorDownloadPanelProps {
  projectId: string;
}

export const ScriptEditorDownloadPanel: React.FC<ScriptEditorDownloadPanelProps> = ({ projectId }) => {
  const { allScenesHaveAudio, scenesWithAudio, combiningAudio, combinedAudioResult, combineAudio, setCombinedAudioResult } = useScriptEditor();

  if (!(allScenesHaveAudio ?? false)) {
    return null;
  }

  const handleDownloadAgain = async () => {
    if (!combinedAudioResult) return;
    try {
      let audioPath = combinedAudioResult.url.startsWith('/') ? combinedAudioResult.url : `/${combinedAudioResult.url}`;
      if (!audioPath.includes('/api/podcast/audio/')) {
        const filename = audioPath.split('/').pop() || combinedAudioResult.filename;
        audioPath = `/api/podcast/audio/${filename}`;
      }
      audioPath = audioPath.split('?')[0];
      const response = await aiApiClient.get(audioPath, { responseType: 'blob' });
      const blob = response.data;
      const blobUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = blobUrl;
      link.download = combinedAudioResult.filename || `podcast-episode-${projectId.slice(-8)}.mp3`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setTimeout(() => URL.revokeObjectURL(blobUrl), 100);
    } catch (error) {
      console.error('Failed to download audio:', error);
    }
  };

  return (
    <Paper sx={{ p: 3, background: "linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%)", border: "1px solid rgba(102, 126, 234, 0.15)", borderRadius: 2 }}>
      <Stack spacing={3}>
        <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 600 }}>Download Audio-Only Podcast</Typography>
        {!combinedAudioResult ? (
          <>
            <PrimaryButton onClick={combineAudio} disabled={combiningAudio} loading={combiningAudio} startIcon={<DownloadIcon />} sx={{ minWidth: 280, fontSize: "1rem", py: 1.5, background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)" }}>
              {combiningAudio ? "Combining Audio..." : "Download Audio-Only Podcast"}
            </PrimaryButton>
            <Typography variant="caption" sx={{ color: "#64748b", fontStyle: "italic" }}>This will combine all {scenesWithAudio} scene audio files into one complete podcast episode.</Typography>
          </>
        ) : (
          <Stack spacing={2}>
            <Alert severity="success" sx={{ background: alpha("#10b981", 0.1), border: "1px solid rgba(16,185,129,0.3)", "& .MuiAlert-icon": { color: "#10b981" } }}>
              <Typography variant="body2" sx={{ color: "#059669", fontWeight: 500 }}>✅ Combined audio generated successfully! ({combinedAudioResult.sceneCount} scenes, {Math.round(combinedAudioResult.duration)}s)</Typography>
            </Alert>
            <InlineAudioPlayer audioUrl={combinedAudioResult.url} title="Complete Podcast Episode" />
            <Stack direction="row" spacing={2}>
              <SecondaryButton onClick={handleDownloadAgain} startIcon={<DownloadIcon />}>Download Again</SecondaryButton>
              <SecondaryButton onClick={() => { setCombinedAudioResult(null); combineAudio(); }} disabled={combiningAudio} loading={combiningAudio} startIcon={<RefreshIcon />}>Regenerate</SecondaryButton>
            </Stack>
          </Stack>
        )}
      </Stack>
    </Paper>
  );
};