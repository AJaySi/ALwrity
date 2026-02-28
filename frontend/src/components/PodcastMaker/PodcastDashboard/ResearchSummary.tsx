import React, { useMemo, useCallback } from "react";
import { Stack, Typography, Chip, Divider, Box, alpha, Paper } from "@mui/material";
import {
  Insights as InsightsIcon,
  Search as SearchIcon,
  AttachMoney as AttachMoneyIcon,
  EditNote as EditNoteIcon,
  Article as ArticleIcon,
  AutoAwesome as AutoAwesomeIcon,
} from "@mui/icons-material";
import { Research, ResearchInsight } from "../types";
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
  // Simple markdown-to-HTML converter
  const renderMarkdown = useCallback((text: string) => {
    if (!text) return null;
    return text
      .split('\n')
      .filter(line => line.trim() !== '') // Remove empty lines
      .map((line, i) => {
        // Handle bold
        let processedLine = line.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        // Handle lists
        if (processedLine.trim().startsWith('- ') || processedLine.trim().startsWith('* ')) {
          return <li key={i} dangerouslySetInnerHTML={{ __html: processedLine.trim().substring(2) }} style={{ marginBottom: '4px', fontSize: '0.9rem' }} />;
        }
        // Handle headers - make them smaller
        if (processedLine.startsWith('### ')) {
          return <Typography key={i} variant="subtitle2" fontWeight={700} sx={{ mt: 1.5, mb: 0.5, color: '#1e293b' }}>{processedLine.substring(4)}</Typography>;
        }
        if (processedLine.startsWith('## ')) {
          return <Typography key={i} variant="subtitle1" fontWeight={700} sx={{ mt: 1.5, mb: 0.5, color: '#0f172a' }}>{processedLine.substring(3)}</Typography>;
        }
        // Paragraphs - compact spacing
        return processedLine.trim() ? <p key={i} dangerouslySetInnerHTML={{ __html: processedLine }} style={{ margin: '4px 0', fontSize: '0.9rem' }} /> : null;
      });
  }, []);

  return (
    <GlassyCard sx={glassyCardSx}>
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Stack direction="row" alignItems="center" spacing={2} sx={{ flex: 1 }}>
            <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
              <InsightsIcon />
              Research Summary
            </Typography>

            {/* Research Metadata - Moved alongside title */}
            <Stack direction="row" spacing={1.5} flexWrap="wrap">
              {research.searchQueries && research.searchQueries.length > 0 && (
                <Chip
                  icon={<SearchIcon sx={{ fontSize: "1rem !important" }} />}
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
          </Stack>

          <PrimaryButton
            onClick={onGenerateScript}
            disabled={!canGenerateScript}
            startIcon={<EditNoteIcon />}
            tooltip={!canGenerateScript ? "Complete research to generate script" : "Generate AI-powered script from research"}
          >
            Generate Script
          </PrimaryButton>
        </Stack>

        <Box sx={{ width: "100%" }}>
          {/* Main Summary */}
          {research.summary && (
            <Paper
              elevation={0}
              sx={{
                p: 2.5,
                mb: 3,
                background: "#f8fafc",
                border: "1px solid rgba(0,0,0,0.06)",
                borderRadius: 2,
              }}
            >
              <Typography variant="subtitle2" sx={{ mb: 1.5, color: "#64748b", fontWeight: 700, fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.05em", display: "flex", alignItems: "center", gap: 1 }}>
                <AutoAwesomeIcon fontSize="small" sx={{ color: "#667eea", fontSize: "1rem" }} />
                Executive Summary
              </Typography>
              <Box sx={{ 
                lineHeight: 1.6,
                fontSize: "0.9rem",
                color: "#334155",
                "& p": { m: 0, mb: 1 },
                "& ul": { m: 0, mb: 1, pl: 2.5 },
                "& li": { mb: 0.5 },
                "& strong": { color: "#0f172a", fontWeight: 600 }
              }}>
                {renderMarkdown(research.summary)}
              </Box>
            </Paper>
          )}

          {/* Deep Insights */}
          {(research.keyInsights && research.keyInsights.length > 0) ? (
            <Box sx={{ mb: 4 }}>
              <Typography variant="h6" sx={{ mb: 2, color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                <ArticleIcon sx={{ color: "#667eea" }} />
                Deep Insights
              </Typography>
              <Stack spacing={2.5}>
                {research.keyInsights.map((insight: ResearchInsight, idx: number) => (
                  <Paper
                    key={idx}
                    elevation={0}
                    sx={{
                      p: 2.5,
                      background: "#ffffff",
                      border: "1px solid rgba(0,0,0,0.06)",
                      boxShadow: "0 2px 12px rgba(0,0,0,0.03)",
                      borderRadius: 2,
                    }}
                  >
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1.5 }}>
                      <Typography variant="subtitle1" sx={{ color: "#0f172a", fontWeight: 700 }}>
                        {insight.title}
                      </Typography>
                      {insight.source_indices && insight.source_indices.length > 0 && (
                        <Stack direction="row" spacing={0.5}>
                          {insight.source_indices.map(sIdx => (
                            <Chip 
                              key={sIdx}
                              label={`S${sIdx}`} 
                              size="small" 
                              variant="outlined"
                              sx={{ 
                                height: 18, 
                                fontSize: '0.65rem', 
                                fontWeight: 700,
                                borderColor: alpha("#667eea", 0.3),
                                color: "#667eea",
                                bgcolor: alpha("#667eea", 0.05)
                              }} 
                            />
                          ))}
                        </Stack>
                      )}
                    </Stack>
                    <Box sx={{ 
                      color: "#475569", 
                      lineHeight: 1.7, 
                      fontSize: "0.9rem",
                      "& p": { m: 0, mb: 1.5 },
                      "& ul": { m: 0, mb: 1.5, pl: 2 }
                    }}>
                      {renderMarkdown(insight.content)}
                    </Box>
                  </Paper>
                ))}
              </Stack>
            </Box>
          ) : (
             /* Fallback if keyInsights is missing but we have summary paragraphs */
             research.summary && research.summary.length > 500 && !research.keyInsights && (
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ mb: 2, color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                  <ArticleIcon sx={{ color: "#667eea" }} />
                  Additional Insights
                </Typography>
                <Paper
                    elevation={0}
                    sx={{
                      p: 2.5,
                      background: "#ffffff",
                      border: "1px solid rgba(0,0,0,0.06)",
                      boxShadow: "0 2px 12px rgba(0,0,0,0.03)",
                      borderRadius: 2,
                    }}
                  >
                     <Box sx={{ 
                      color: "#475569", 
                      lineHeight: 1.7, 
                      fontSize: "0.9rem",
                    }}>
                      {/* Render parts of summary that might contain insights if structured data is missing */}
                      {renderMarkdown(research.summary.split('\n\n').slice(1).join('\n\n'))}
                    </Box>
                </Paper>
              </Box>
             )
          )}

          {/* Search Queries Used */}
          {research.searchQueries && research.searchQueries.length > 0 && (
            <Box sx={{ mt: 4, pt: 3, borderTop: "1px solid rgba(0,0,0,0.04)" }}>
              <Typography variant="subtitle2" sx={{ mb: 1.5, color: "#64748b", fontWeight: 700, fontSize: "0.7rem", textTransform: "uppercase", letterSpacing: "0.05em" }}>
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
                      borderColor: "rgba(102, 126, 234, 0.15)",
                      color: "#94a3b8",
                      background: alpha("#f8fafc", 0.3),
                      fontSize: "0.7rem",
                      borderRadius: 1,
                    }}
                  />
                ))}
              </Stack>
            </Box>
          )}
        </Box>

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

