import React, { useMemo, useCallback } from "react";
import { Stack, Typography, Chip, Divider, Box, alpha, Paper, Tooltip } from "@mui/material";
import {
  Insights as InsightsIcon,
  Search as SearchIcon,
  AttachMoney as AttachMoneyIcon,
  EditNote as EditNoteIcon,
  Article as ArticleIcon,
  AutoAwesome as AutoAwesomeIcon,
  FormatQuote as FormatQuoteIcon,
  Campaign as CampaignIcon,
  Explore as ExploreIcon,
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
                          {insight.source_indices.map(sIdx => {
                            const sourceIdx = sIdx - 1;
                            const fact = research.factCards[sourceIdx];
                            const sourceUrl = fact?.url;
                            const hasUrl = !!sourceUrl;
                            const hue = (sIdx * 47 + 220) % 360;
                            const gradientFrom = `hsl(${hue}, 70%, 55%)`;
                            const gradientTo = `hsl(${(hue + 30) % 360}, 80%, 65%)`;
                            return (
                              <Tooltip
                                key={sIdx}
                                title={hasUrl ? (
                                  <Box sx={{ maxWidth: 300, wordBreak: "break-all" }}>
                                    <Typography variant="caption" sx={{ color: "#fff", fontWeight: 600 }}>Source {sIdx}</Typography>
                                    <br />
                                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.8)", fontSize: "0.65rem" }}>{sourceUrl}</Typography>
                                  </Box>
                                ) : `Source ${sIdx}`}
                                arrow
                                placement="top"
                              >
                                <Chip 
                                  label={hasUrl ? `S${sIdx} ↗` : `S${sIdx}`}
                                  size="small"
                                  onClick={hasUrl ? () => window.open(sourceUrl, "_blank", "noopener,noreferrer") : undefined}
                                  sx={{ 
                                    height: 24,
                                    minWidth: 36,
                                    fontSize: '0.7rem', 
                                    fontWeight: 800,
                                    fontFamily: "'Inter', 'Roboto', monospace",
                                    letterSpacing: "0.02em",
                                    border: "none",
                                    background: hasUrl 
                                      ? `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`
                                      : `linear-gradient(135deg, ${alpha(gradientFrom, 0.3)}, ${alpha(gradientTo, 0.3)})`,
                                    color: hasUrl ? "#fff" : alpha("#fff", 0.7),
                                    cursor: hasUrl ? "pointer" : "default",
                                    borderRadius: "8px",
                                    px: 0.5,
                                    boxShadow: hasUrl 
                                      ? `0 2px 8px ${alpha(gradientFrom, 0.35)}, inset 0 1px 0 ${alpha("#fff", 0.2)}`
                                      : "none",
                                    transition: "all 0.2s ease",
                                    "&:hover": hasUrl ? {
                                      background: `linear-gradient(135deg, ${gradientTo}, ${gradientFrom})`,
                                      boxShadow: `0 4px 14px ${alpha(gradientFrom, 0.5)}, inset 0 1px 0 ${alpha("#fff", 0.3)}`,
                                      transform: "translateY(-1px)",
                                    } : {},
                                  }}
                                />
                              </Tooltip>
                            );
                          })}
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

          {/* Expert Quotes Section */}
          {research.expertQuotes && research.expertQuotes.length > 0 && (
            <Box sx={{ mt: 4, pt: 3, borderTop: "1px solid rgba(0,0,0,0.04)" }}>
              <Typography variant="h6" sx={{ mb: 2, color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                <FormatQuoteIcon sx={{ color: "#8b5cf6" }} />
                Expert Quotes ({research.expertQuotes.length})
              </Typography>
              <Stack spacing={2}>
                {research.expertQuotes.map((eq, idx) => (
                  <Paper
                    key={idx}
                    elevation={0}
                    sx={{
                      p: 2.5,
                      background: "linear-gradient(135deg, rgba(139, 92, 246, 0.04) 0%, rgba(99, 102, 241, 0.04) 100%)",
                      border: "1px solid rgba(139, 92, 246, 0.15)",
                      borderLeft: "4px solid #8b5cf6",
                      borderRadius: 2,
                    }}
                  >
                    <Stack direction="row" spacing={1.5} alignItems="flex-start">
                      <FormatQuoteIcon sx={{ color: "#8b5cf6", fontSize: "1.5rem", mt: -0.5, opacity: 0.7 }} />
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="body2" sx={{ color: "#1e293b", fontStyle: "italic", lineHeight: 1.7, fontSize: "0.95rem" }}>
                          &ldquo;{eq.quote}&rdquo;
                        </Typography>
                        {eq.source_index !== undefined && (() => {
                            const fact = research.factCards[eq.source_index - 1];
                            const sourceUrl = fact?.url;
                            const hasUrl = !!sourceUrl;
                            const hue = (eq.source_index * 47 + 270) % 360;
                            const gradientFrom = `hsl(${hue}, 70%, 55%)`;
                            const gradientTo = `hsl(${(hue + 30) % 360}, 80%, 65%)`;
                            return (
                              <Box sx={{ mt: 1 }}>
                                <Tooltip title={hasUrl ? (
                                  <Box sx={{ maxWidth: 300, wordBreak: "break-all" }}>
                                    <Typography variant="caption" sx={{ color: "#fff", fontWeight: 600 }}>Source {eq.source_index}</Typography>
                                    <br />
                                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.8)", fontSize: "0.65rem" }}>{sourceUrl}</Typography>
                                  </Box>
                                ) : `Source ${eq.source_index}`} arrow placement="top">
                                  <Chip
                                    label={hasUrl ? `Source ${eq.source_index} ↗` : `Source ${eq.source_index}`}
                                    size="small"
                                    onClick={hasUrl ? () => window.open(sourceUrl, "_blank", "noopener,noreferrer") : undefined}
                                    sx={{
                                      height: 24,
                                      fontSize: "0.7rem",
                                      fontWeight: 800,
                                      fontFamily: "'Inter', 'Roboto', monospace",
                                      border: "none",
                                      background: hasUrl 
                                        ? `linear-gradient(135deg, ${gradientFrom}, ${gradientTo})`
                                        : `linear-gradient(135deg, ${alpha(gradientFrom, 0.3)}, ${alpha(gradientTo, 0.3)})`,
                                      color: hasUrl ? "#fff" : alpha("#fff", 0.7),
                                      cursor: hasUrl ? "pointer" : "default",
                                      borderRadius: "8px",
                                      px: 1,
                                      boxShadow: hasUrl 
                                        ? `0 2px 8px ${alpha(gradientFrom, 0.35)}, inset 0 1px 0 ${alpha("#fff", 0.2)}`
                                        : "none",
                                      transition: "all 0.2s ease",
                                      "&:hover": hasUrl ? {
                                        background: `linear-gradient(135deg, ${gradientTo}, ${gradientFrom})`,
                                        boxShadow: `0 4px 14px ${alpha(gradientFrom, 0.5)}, inset 0 1px 0 ${alpha("#fff", 0.3)}`,
                                        transform: "translateY(-1px)",
                                      } : {},
                                    }}
                                  />
                                </Tooltip>
                              </Box>
                            );
                          })()}
                      </Box>
                    </Stack>
                  </Paper>
                ))}
              </Stack>
            </Box>
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

        {/* Listener CTA Section */}
        {research.listenerCta && research.listenerCta.length > 0 && (
          <>
            <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
            <Box>
              <Typography variant="h6" sx={{ mb: 2, color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                <CampaignIcon sx={{ color: "#f59e0b" }} />
                Listener Call-to-Action Ideas ({research.listenerCta.length})
              </Typography>
              <Stack spacing={1.5}>
                {research.listenerCta.map((cta, idx) => (
                  <Paper
                    key={idx}
                    elevation={0}
                    sx={{
                      p: 2,
                      background: "linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(251, 191, 36, 0.05) 100%)",
                      border: "1px solid rgba(245, 158, 11, 0.15)",
                      borderRadius: 2,
                      display: "flex",
                      alignItems: "flex-start",
                      gap: 1.5,
                    }}
                  >
                    <Chip
                      label={`#${idx + 1}`}
                      size="small"
                      sx={{
                        bgcolor: alpha("#f59e0b", 0.15),
                        color: "#b45309",
                        fontWeight: 700,
                        fontSize: "0.7rem",
                        height: 24,
                        minWidth: 32,
                      }}
                    />
                    <Typography variant="body2" sx={{ color: "#475569", lineHeight: 1.6, flex: 1, pt: 0.2 }}>
                      {cta}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </Box>
          </>
        )}

        {/* Mapped Angles Section */}
        {research.mappedAngles && research.mappedAngles.length > 0 && (
          <>
            <Divider sx={{ borderColor: "rgba(0,0,0,0.08)" }} />
            <Box>
              <Typography variant="h6" sx={{ mb: 2, color: "#0f172a", fontWeight: 700, display: "flex", alignItems: "center", gap: 1 }}>
                <ExploreIcon sx={{ color: "#06b6d4" }} />
                Content Angles ({research.mappedAngles.length})
              </Typography>
              <Stack spacing={2}>
                {research.mappedAngles.map((angle, idx) => (
                  <Paper
                    key={idx}
                    elevation={0}
                    sx={{
                      p: 2.5,
                      background: "#ffffff",
                      border: "1px solid rgba(0,0,0,0.06)",
                      borderLeft: "4px solid #06b6d4",
                      boxShadow: "0 2px 12px rgba(0,0,0,0.03)",
                      borderRadius: 2,
                    }}
                  >
                    <Stack direction="row" justifyContent="space-between" alignItems="flex-start" sx={{ mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ color: "#0f172a", fontWeight: 700 }}>
                        {angle.title}
                      </Typography>
                      {angle.mappedFactIds && angle.mappedFactIds.length > 0 && (
                        <Stack direction="row" spacing={0.5}>
                          {angle.mappedFactIds.slice(0, 4).map((fid: string) => (
                            <Chip
                              key={fid}
                              label={fid.replace("fact_", "F")}
                              size="small"
                              variant="outlined"
                              sx={{
                                height: 18,
                                fontSize: "0.6rem",
                                fontWeight: 700,
                                borderColor: alpha("#06b6d4", 0.3),
                                color: "#06b6d4",
                                bgcolor: alpha("#06b6d4", 0.05),
                              }}
                            />
                          ))}
                          {angle.mappedFactIds.length > 4 && (
                            <Chip
                              label={`+${angle.mappedFactIds.length - 4}`}
                              size="small"
                              sx={{ height: 18, fontSize: "0.6rem", color: "#64748b" }}
                            />
                          )}
                        </Stack>
                      )}
                    </Stack>
                    <Typography variant="body2" sx={{ color: "#475569", lineHeight: 1.7, fontSize: "0.9rem" }}>
                      {angle.why}
                    </Typography>
                  </Paper>
                ))}
              </Stack>
            </Box>
          </>
        )}
      </Stack>
    </GlassyCard>
  );
};

