import React from "react";
import { Stack, Box, Typography, Divider, Chip, Paper, alpha } from "@mui/material";
import { Psychology as PsychologyIcon, Insights as InsightsIcon, Search as SearchIcon } from "@mui/icons-material";
import { PodcastAnalysis } from "./types";
import { GlassyCard, glassyCardSx, SecondaryButton } from "./ui";
import { Refresh as RefreshIcon } from "@mui/icons-material";

interface AnalysisPanelProps {
  analysis: PodcastAnalysis | null;
  onRegenerate?: () => void;
}

export const AnalysisPanel: React.FC<AnalysisPanelProps> = ({ analysis, onRegenerate }) => {
  if (!analysis) return null;
  return (
    <GlassyCard
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#0f172a",
      }}
      aria-label="analysis-panel"
    >
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start">
          <Box>
            <Typography
              variant="h6"
              sx={{
                color: "#0f172a",
                fontWeight: 800,
                mb: 0.5,
                display: "flex",
                alignItems: "center",
                gap: 1,
              }}
            >
              <PsychologyIcon />
              AI Analysis
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Insights derived from AI analysis of your topic and content preferences
            </Typography>
          </Box>
          <SecondaryButton onClick={onRegenerate} startIcon={<RefreshIcon />} tooltip="Regenerate analysis with different parameters">
            Regenerate
          </SecondaryButton>
        </Stack>

        <Divider sx={{ borderColor: "rgba(0,0,0,0.06)" }} />

        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 3 }}>
          <Stack spacing={2}>
            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, display: "flex", alignItems: "center", gap: 0.5 }}>
                <InsightsIcon fontSize="small" sx={{ color: "#4f46e5" }} />
                Target Audience
              </Typography>
              <Typography variant="body2" sx={{ color: "#0f172a" }}>
                {analysis.audience}
              </Typography>
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Content Type</Typography>
              <Chip label={analysis.contentType} size="small" sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }} />
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Top Keywords</Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                {analysis.topKeywords.map((k) => (
                  <Chip
                    key={k}
                    label={k}
                    size="small"
                    variant="outlined"
                    sx={{
                      borderColor: "rgba(0,0,0,0.1)",
                      color: "#0f172a",
                      background: "#f8fafc",
                    }}
                  />
                ))}
              </Stack>
            </Box>
          </Stack>

          <Stack spacing={2}>
            {analysis.exaSuggestedConfig && (
              <Box>
                <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", display: "flex", alignItems: "center", gap: 0.5 }}>
                  <SearchIcon fontSize="small" sx={{ color: "#4f46e5" }} />
                  Exa Research Suggestions
                </Typography>
                <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap sx={{ mb: 1 }}>
                  {analysis.exaSuggestedConfig.exa_search_type && (
                    <Chip
                      label={`Search: ${analysis.exaSuggestedConfig.exa_search_type}`}
                      size="small"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  )}
                  {analysis.exaSuggestedConfig.exa_category && (
                    <Chip
                      label={`Category: ${analysis.exaSuggestedConfig.exa_category}`}
                      size="small"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  )}
                  {analysis.exaSuggestedConfig.date_range && (
                    <Chip
                      label={`Date: ${analysis.exaSuggestedConfig.date_range}`}
                      size="small"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  )}
                  {typeof analysis.exaSuggestedConfig.include_statistics === "boolean" && (
                    <Chip
                      label={analysis.exaSuggestedConfig.include_statistics ? "Include stats" : "No stats needed"}
                      size="small"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  )}
                  {analysis.exaSuggestedConfig.max_sources && (
                    <Chip
                      label={`Max sources: ${analysis.exaSuggestedConfig.max_sources}`}
                      size="small"
                      sx={{ background: "#eef2ff", color: "#0f172a", border: "1px solid rgba(0,0,0,0.06)" }}
                    />
                  )}
                </Stack>

                {(analysis.exaSuggestedConfig.exa_include_domains?.length || analysis.exaSuggestedConfig.exa_exclude_domains?.length) && (
                  <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap>
                    {analysis.exaSuggestedConfig.exa_include_domains?.length ? (
                      <Box>
                        <Typography variant="caption" sx={{ color: "#475569", fontWeight: 600, display: "block", mb: 0.5 }}>
                          Prefer domains
                        </Typography>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                          {analysis.exaSuggestedConfig.exa_include_domains.map((d) => (
                            <Chip key={d} label={d} size="small" sx={{ background: "#f8fafc", color: "#0f172a", border: "1px solid rgba(0,0,0,0.08)" }} />
                          ))}
                        </Stack>
                      </Box>
                    ) : null}

                    {analysis.exaSuggestedConfig.exa_exclude_domains?.length ? (
                      <Box>
                        <Typography variant="caption" sx={{ color: "#475569", fontWeight: 600, display: "block", mb: 0.5 }}>
                          Avoid domains
                        </Typography>
                        <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                          {analysis.exaSuggestedConfig.exa_exclude_domains.map((d) => (
                            <Chip key={d} label={d} size="small" sx={{ background: "#fff7ed", color: "#b45309", border: "1px solid rgba(180,83,9,0.25)" }} />
                          ))}
                        </Stack>
                      </Box>
                    ) : null}
                  </Stack>
                )}
              </Box>
            )}

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Suggested Episode Outlines</Typography>
              <Stack spacing={1.5}>
                {analysis.suggestedOutlines.map((o) => (
                  <Paper
                    key={o.id}
                    sx={{
                      p: 1.5,
                      background: "#f8fafc",
                      border: "1px solid rgba(0,0,0,0.06)",
                      wordBreak: "break-word",
                    }}
                  >
                    <Typography variant="body2" sx={{ fontWeight: 700, mb: 0.5, color: "#0f172a", wordBreak: "break-word" }}>
                      {o.title}
                    </Typography>
                    <Typography variant="caption" sx={{ color: "#475569", display: "block", wordBreak: "break-word" }}>
                      {o.segments.join(" • ")}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </Box>

            <Box>
              <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a" }}>Title Suggestions</Typography>
              <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                {analysis.titleSuggestions.map((t) => (
                  <Chip
                    key={t}
                    label={t}
                    size="small"
                    sx={{
                      cursor: "pointer",
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
                      "&:hover": {
                        background: alpha("#667eea", 0.15),
                        border: "1px solid rgba(102,126,234,0.35)",
                      },
                    }}
                  />
                ))}
              </Stack>
            </Box>
          </Stack>
        </Box>
      </Stack>
    </GlassyCard>
  );
};

