import React, { useMemo } from "react";
import { Stack, Typography, Chip, Divider, Box, alpha, Paper } from "@mui/material";
import {
  Insights as InsightsIcon,
  Search as SearchIcon,
  AttachMoney as AttachMoneyIcon,
  EditNote as EditNoteIcon,
  Article as ArticleIcon,
} from "@mui/icons-material";
import { Research } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton } from "../ui";
import { FactCard } from "../FactCard";

interface ResearchSummaryProps {
  research: Research;
  canGenerateScript: boolean;
  onGenerateScript: () => void;
}

export const ResearchSummary: React.FC<ResearchSummaryProps> = ({
  research,
  canGenerateScript,
  onGenerateScript,
}) => {
  // Extract key insights from summary if it's long
  const summaryParts = useMemo(() => {
    const fullSummary = research.summary || "";
    if (fullSummary.length > 500) {
      // Try to split into paragraphs or sentences
      const sentences = fullSummary.split(/[.!?]\s+/).filter(s => s.trim().length > 20);
      const keyPoints = sentences.slice(0, 3);
      const remainingText = sentences.slice(3).join(". ") + (sentences.length > 3 ? "." : "");
      return { keyPoints, remainingText };
    }
    return { keyPoints: [], remainingText: fullSummary };
  }, [research.summary]);

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="flex-start" flexWrap="wrap" gap={2}>
          <Box sx={{ flex: 1, minWidth: { xs: "100%", md: "60%" } }}>
            <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, mb: 1.5 }}>
              <InsightsIcon />
              Research Summary
            </Typography>
            
            {/* Key Insights */}
            {summaryParts.keyPoints.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", fontWeight: 600, display: "flex", alignItems: "center", gap: 0.5 }}>
                  <ArticleIcon fontSize="small" />
                  Key Insights
                </Typography>
                <Stack spacing={1}>
                  {summaryParts.keyPoints.map((point, idx) => (
                    <Paper
                      key={idx}
                      sx={{
                        p: 1.25,
                        background: alpha("#667eea", 0.05),
                        border: "1px solid rgba(102, 126, 234, 0.15)",
                        borderRadius: 1.5,
                      }}
                    >
                      <Typography variant="body2" sx={{ color: "#0f172a", lineHeight: 1.6, fontSize: "0.875rem" }}>
                        {point}
                      </Typography>
                    </Paper>
                  ))}
                </Stack>
              </Box>
            )}

            {/* Full Summary Text */}
            <Typography 
              variant="body2" 
              color="text.secondary" 
              sx={{ 
                mb: 2, 
                lineHeight: 1.7,
                fontSize: "0.875rem",
                color: "#475569",
              }}
            >
              {summaryParts.remainingText || research.summary}
            </Typography>

            {/* Research Metadata */}
            <Stack direction="row" spacing={2} flexWrap="wrap" useFlexGap sx={{ mb: 2 }}>
              {research.searchQueries && research.searchQueries.length > 0 && (
                <Chip
                  icon={<SearchIcon />}
                  label={`${research.searchQueries.length} search${research.searchQueries.length > 1 ? "es" : ""}`}
                  size="small"
                  sx={{
                    background: alpha("#667eea", 0.1),
                    color: "#667eea",
                    fontWeight: 600,
                    border: "1px solid rgba(102, 126, 234, 0.2)",
                  }}
                />
              )}
              {research.searchType && (
                <Chip
                  label={`${research.searchType.charAt(0).toUpperCase() + research.searchType.slice(1)} search`}
                  size="small"
                  sx={{
                    background: alpha("#10b981", 0.1),
                    color: "#059669",
                    fontWeight: 600,
                    border: "1px solid rgba(16, 185, 129, 0.2)",
                  }}
                />
              )}
              {research.sourceCount !== undefined && (
                <Chip
                  label={`${research.sourceCount} source${research.sourceCount !== 1 ? "s" : ""}`}
                  size="small"
                  sx={{
                    background: alpha("#6366f1", 0.1),
                    color: "#4f46e5",
                    fontWeight: 600,
                    border: "1px solid rgba(99, 102, 241, 0.2)",
                  }}
                />
              )}
              {research.cost !== undefined && (
                <Chip
                  icon={<AttachMoneyIcon sx={{ fontSize: "0.875rem !important" }} />}
                  label={`$${research.cost.toFixed(3)}`}
                  size="small"
                  sx={{
                    background: alpha("#f59e0b", 0.1),
                    color: "#d97706",
                    fontWeight: 600,
                    border: "1px solid rgba(245, 158, 11, 0.2)",
                  }}
                />
              )}
            </Stack>

            {/* Search Queries Used */}
            {research.searchQueries && research.searchQueries.length > 0 && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ mb: 1, color: "#0f172a", fontWeight: 600 }}>
                  Search Queries Used
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {research.searchQueries.map((query, idx) => (
                    <Chip
                      key={idx}
                      label={query}
                      size="small"
                      variant="outlined"
                      sx={{
                        borderColor: "rgba(102, 126, 234, 0.3)",
                        color: "#475569",
                        background: alpha("#f8fafc", 0.8),
                        fontSize: "0.8125rem",
                      }}
                    />
                  ))}
                </Stack>
              </Box>
            )}
          </Box>
          <PrimaryButton
            onClick={onGenerateScript}
            disabled={!canGenerateScript}
            startIcon={<EditNoteIcon />}
            tooltip={!canGenerateScript ? "Complete research to generate script" : "Generate AI-powered script from research"}
          >
            Generate Script
          </PrimaryButton>
        </Stack>

        {research.factCards.length > 0 && (
          <>
            <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
            <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1.5, flexWrap: "wrap", gap: 1 }}>
              <Typography variant="subtitle2" sx={{ color: "#0f172a", fontWeight: 600 }}>
                Research Sources & Facts ({research.factCards.length})
              </Typography>
              <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.75rem" }}>
                Click to expand • Hover to see source
              </Typography>
            </Stack>
            <Box 
              sx={{ 
                display: "grid", 
                gridTemplateColumns: { xs: "1fr", sm: "repeat(2, 1fr)", md: "repeat(3, 1fr)", lg: "repeat(4, 1fr)" }, 
                gap: 1.5,
                width: "100%",
                overflow: "hidden",
              }}
            >
              {research.factCards.map((fact) => (
                <FactCard key={fact.id} fact={fact} />
              ))}
            </Box>
          </>
        )}
      </Stack>
    </GlassyCard>
  );
};

