import React from "react";
import { Box, Typography, Chip } from "@mui/material";
import { useAnalysisPanel } from "../AnalysisPanelContext";

const AnalysisTabContent: React.FC<{ title: string; icon?: React.ReactNode; children: React.ReactNode }> = ({ title, icon, children }) => (
  <Box sx={{ p: 2 }}>
    <Box sx={{ display: "flex", gap: 1.5, alignItems: "center", mb: 2 }}>
      {icon}
      <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
        {title}
      </Typography>
    </Box>
    {children}
  </Box>
);

export const AnalysisPanelOutlineTab: React.FC = () => {
  const { currentAnalysis, isEditing, handleUpdateOutline } = useAnalysisPanel();

  if (!currentAnalysis || !currentAnalysis.suggestedOutlines) {
    return (
      <Box sx={{ p: 3, textAlign: "center" }}>
        <Typography variant="body1" sx={{ color: "#64748b" }}>
          No outline available. Please generate analysis first.
        </Typography>
      </Box>
    );
  }

  const analysis = currentAnalysis;

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: "flex", gap: 1.5, alignItems: "center", mb: 2 }}>
        <Typography variant="h6" sx={{ fontWeight: 600, color: "#0f172a" }}>
          Episode Outline
        </Typography>
      </Box>
      {analysis.suggestedOutlines?.map((outline: { id?: string | number; title: string; segments: string[] }, idx: number) => (
        <Box key={outline.id || idx} sx={{ p: 2, bgcolor: "#f8fafc", borderRadius: 2, border: "1px solid rgba(0,0,0,0.08)", mb: 2 }}>
          <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 700, mb: 1.5 }}>
            Option {idx + 1}: {outline.title}
          </Typography>
          {outline.segments?.map((segment: string, sIdx: number) => (
            <Box key={sIdx} sx={{ display: "flex", alignItems: "flex-start", gap: 1, mb: 1 }}>
              <Chip label={sIdx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#4f46e5", color: "#fff" }} />
              <Typography variant="body2" sx={{ color: "#475569" }}>
                {segment}
              </Typography>
            </Box>
          ))}
        </Box>
      ))}
    </Box>
  );
};