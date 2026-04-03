import React from "react";
import { Stack, Box, Typography, Chip, TextField, IconButton } from "@mui/material";
import { ListAlt as ListAltIcon, Add as AddIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "../../types";
import { AnalysisTabContent } from "../AnalysisTabNav";

interface OutlineTabProps {
  analysis: PodcastAnalysis;
  isEditing?: boolean;
  onUpdateOutline?: (id: string | number, field: 'title' | 'segments', value: any) => void;
}

export const OutlineTab: React.FC<OutlineTabProps> = ({ analysis, isEditing, onUpdateOutline }) => {
  return (
    <AnalysisTabContent title="Episode Outline" icon={<ListAltIcon />}>
      <Stack spacing={3}>
        {analysis.suggestedOutlines?.map((outline: { id?: string | number; title: string; segments: string[] }, idx: number) => (
          <Box key={outline.id || idx} sx={{ p: 2, bgcolor: "#f8fafc", borderRadius: 2, border: "1px solid rgba(0,0,0,0.08)" }}>
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5 }}>
              <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 700 }}>
                Option {idx + 1}: {outline.title}
              </Typography>
            </Stack>
            <Stack spacing={1}>
              {outline.segments?.map((segment: string, sIdx: number) => (
                <Box key={sIdx} sx={{ display: "flex", alignItems: "flex-start", gap: 1 }}>
                  <Chip label={sIdx + 1} size="small" sx={{ minWidth: 24, bgcolor: "#4f46e5", color: "#fff" }} />
                  <Typography variant="body2" sx={{ color: "#475569" }}>
                    {segment}
                  </Typography>
                </Box>
              ))}
            </Stack>
          </Box>
        ))}
      </Stack>
    </AnalysisTabContent>
  );
};
