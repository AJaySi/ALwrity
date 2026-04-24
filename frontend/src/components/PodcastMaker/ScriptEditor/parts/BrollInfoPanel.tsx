import React, { useState } from "react";
import { Stack, Box, Typography, Paper, Button, CircularProgress, Chip, IconButton, Tooltip, Accordion, AccordionSummary, AccordionDetails, Dialog, DialogContent, DialogTitle } from "@mui/material";
import { BarChart as BarChartIcon, AutoAwesome as AutoAwesomeIcon, Refresh as RefreshIcon, DeleteOutline as DeleteIcon, Fullscreen as FullscreenIcon, ExpandMore as ExpandMoreIcon, Close as CloseIcon, ZoomOutMap as ZoomOutMapIcon } from "@mui/icons-material";
import { useScriptEditor } from "../ScriptEditorContext";
import { Script } from "../../types";

interface BrollInfoPanelProps {
  activeScript?: Script | null;
  generatingChartId?: string | null;
  generateChartPreviews?: () => Promise<void>;
  regenerateChart?: (sceneId: string) => Promise<void>;
  removeChart?: (sceneId: string) => void;
  scenesWithCharts?: number;
}

export const BrollInfoPanel: React.FC<BrollInfoPanelProps> = (props) => {
  const [expanded, setExpanded] = useState(false);
  const [previewModal, setPreviewModal] = useState<{ url: string; title: string } | null>(null);
  const ctx = useScriptEditor();

  const { 
    activeScript: ctxActiveScript, 
    generatingChartId: ctxGeneratingChartId, 
    generateChartPreviews: ctxGenerateChartPreviews,
    regenerateChart: ctxRegenerateChart,
    removeChart: ctxRemoveChart,
    scenesWithCharts: ctxScenesWithCharts 
  } = ctx;

  const resolvedActiveScript = props.activeScript ?? ctxActiveScript;
  const resolvedGeneratingChartId = props.generatingChartId ?? ctxGeneratingChartId;
  const resolvedGenerateChartPreviews = props.generateChartPreviews ?? ctxGenerateChartPreviews;
  const resolvedRegenerateChart = props.regenerateChart ?? ctxRegenerateChart;
  const resolvedRemoveChart = props.removeChart ?? ctxRemoveChart;

  if (!resolvedActiveScript || resolvedActiveScript.scenes.length === 0) {
    return null;
  }

  const scenesWithData = resolvedActiveScript.scenes.filter(s => s.chart_data && Object.keys(s.chart_data).length > 0);
  const hasChartData = scenesWithData.length > 0;
  const resolvedScenesWithCharts = props.scenesWithCharts ?? ctxScenesWithCharts ?? scenesWithData.length;

  const openPreview = (url: string, title: string) => {
    setPreviewModal({ url, title });
  };

  const closePreview = () => {
    setPreviewModal(null);
  };

  return (
    <>
      <Accordion 
        expanded={expanded} 
        onChange={(_, isExpanded) => setExpanded(isExpanded)}
        sx={{
          background: "linear-gradient(135deg, rgba(34, 197, 94, 0.03) 0%, rgba(16, 185, 129, 0.03) 100%)",
          border: "1px solid rgba(34, 197, 94, 0.15)",
          borderRadius: 2,
          '&:before': {
            display: 'none',
          },
          '&.MuiAccordion-root': {
            borderRadius: 2,
          },
          '& .MuiAccordionSummary-root': {
            borderRadius: 2,
          },
        }}
      >
        <AccordionSummary
          expandIcon={<ExpandMoreIcon sx={{ color: '#22c55e' }} />}
          sx={{
            '& .MuiAccordionSummary-content': {
              alignItems: 'center',
              justifyContent: 'space-between',
            },
          }}
        >
          <Stack direction="row" alignItems="center" spacing={1.5}>
            <Box sx={{ 
              p: 0.75, 
              borderRadius: 1.5, 
              background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center"
            }}>
              <BarChartIcon sx={{ fontSize: 18, color: "#fff" }} />
            </Box>
            <Box>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, color: "#0f172a", lineHeight: 1.2 }}>
                Podcast Charts
              </Typography>
              <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.7rem" }}>
                {resolvedScenesWithCharts} chart{resolvedScenesWithCharts !== 1 ? 's' : ''} for visual storytelling
              </Typography>
            </Box>
          </Stack>
        </AccordionSummary>
        
        <AccordionDetails sx={{ pt: 0 }}>
          {hasChartData && (
            <Box sx={{ mb: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                variant="contained"
                size="small"
                startIcon={resolvedGeneratingChartId ? <CircularProgress size={14} color="inherit" /> : <AutoAwesomeIcon sx={{ fontSize: 16 }} />}
                onClick={(e) => {
                  e.stopPropagation();
                  resolvedGenerateChartPreviews?.();
                }}
                disabled={!!resolvedGeneratingChartId}
                sx={{
                  background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)",
                  fontSize: "0.75rem",
                  py: 0.5,
                  px: 1.5,
                  textTransform: "none",
                  fontWeight: 600,
                  boxShadow: "0 2px 8px rgba(34, 197, 94, 0.3)",
                  "&:hover": {
                    background: "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
                  },
                  "&:disabled": {
                    background: "rgba(34, 197, 94, 0.5)",
                  }
                }}
              >
                {resolvedGeneratingChartId ? "Generating..." : "Generate Charts"}
              </Button>
            </Box>
          )}

          {hasChartData ? (
            <Stack spacing={1.5}>
              {scenesWithData.map((scene) => {
                const chartData = scene.chart_data;
                const hasPreview = !!scene.broll_preview_url;
                
                return (
                  <Box
                    key={scene.id}
                    sx={{
                      p: 1.5,
                      background: "#fff",
                      borderRadius: 1.5,
                      border: "1px solid rgba(0,0,0,0.06)",
                      display: "flex",
                      alignItems: "center",
                      gap: 2,
                      transition: "all 0.2s ease",
                      "&:hover": {
                        borderColor: "rgba(34, 197, 94, 0.3)",
                        boxShadow: "0 2px 8px rgba(0,0,0,0.04)",
                      }
                    }}
                  >
                    {/* Thumbnail */}
                    <Box 
                      onClick={() => hasPreview && scene.broll_preview_url && openPreview(scene.broll_preview_url, scene.title)}
                      sx={{ 
                        width: 72, 
                        height: 48, 
                        flexShrink: 0,
                        borderRadius: 1,
                        overflow: "hidden",
                        background: hasPreview ? "rgba(0,0,0,0.04)" : "linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)",
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        cursor: hasPreview ? "pointer" : "default",
                        transition: "all 0.2s ease",
                        position: "relative",
                        "&:hover": hasPreview ? {
                          transform: "scale(1.05)",
                          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                          "& .zoom-overlay": {
                            opacity: 1,
                          },
                        } : {}
                      }}
                    >
                      {resolvedGeneratingChartId === scene.id ? (
                        <CircularProgress size={24} sx={{ color: "#22c55e" }} />
                      ) : hasPreview && scene.broll_preview_url ? (
                        <>
                          <Box 
                            component="img" 
                            src={scene.broll_preview_url} 
                            alt={`Chart for ${scene.title}`}
                            sx={{ 
                              width: "100%", 
                              height: "100%", 
                              objectFit: "cover",
                            }}
                          />
                          <Box
                            className="zoom-overlay"
                            sx={{
                              position: "absolute",
                              inset: 0,
                              background: "rgba(0,0,0,0.4)",
                              display: "flex",
                              alignItems: "center",
                              justifyContent: "center",
                              opacity: 0,
                              transition: "opacity 0.2s ease",
                              borderRadius: 1,
                            }}
                          >
                            <ZoomOutMapIcon sx={{ color: "#fff", fontSize: 18 }} />
                          </Box>
                        </>
                      ) : (
                        <BarChartIcon sx={{ fontSize: 20, color: "#94a3b8" }} />
                      )}
                    </Box>

                    {/* Chart Info */}
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="subtitle2" sx={{ 
                        fontWeight: 600, 
                        color: "#1e293b", 
                        fontSize: "0.8rem",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}>
                        {scene.title}
                      </Typography>
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mt: 0.25 }}>
                        <Chip 
                          label={chartData?.type || "chart"} 
                          size="small"
                          sx={{ 
                            height: 18, 
                            fontSize: "0.65rem",
                            background: "rgba(34, 197, 94, 0.1)",
                            color: "#16a34a",
                            fontWeight: 600,
                          }}
                        />
                        <Typography variant="caption" sx={{ color: "#64748b", fontSize: "0.7rem" }}>
                          {chartData?.labels?.length || 0} labels
                        </Typography>
                        {hasPreview && (
                          <Chip 
                            label="Ready" 
                            size="small"
                            sx={{ 
                              height: 18, 
                              fontSize: "0.65rem",
                              background: "rgba(34, 197, 94, 0.15)",
                              color: "#16a34a",
                              fontWeight: 600,
                            }}
                          />
                        )}
                      </Stack>
                    </Box>

                    {/* Takeaway */}
                    {chartData?.takeaway && (
                      <Box sx={{ 
                        flex: 1.5, 
                        display: { xs: "none", md: "block" },
                        px: 1,
                        py: 0.5,
                        background: "rgba(34, 197, 94, 0.04)",
                        borderRadius: 1,
                      }}>
                        <Typography variant="caption" sx={{ 
                          color: "#475569", 
                          fontSize: "0.7rem",
                          fontStyle: "italic",
                          display: "-webkit-box",
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: "vertical",
                          overflow: "hidden",
                        }}>
                          "{chartData.takeaway}"
                        </Typography>
                      </Box>
                    )}

                    {/* Actions */}
                    <Stack direction="row" spacing={0.5}>
                      {hasPreview && (
                        <Tooltip title="View fullsize">
                          <IconButton 
                            size="small"
                            onClick={() => scene.broll_preview_url && openPreview(scene.broll_preview_url, scene.title)}
                            sx={{ 
                              color: "#64748b",
                              "&:hover": { color: "#22c55e", background: "rgba(34, 197, 94, 0.1)" }
                            }}
                          >
                            <FullscreenIcon sx={{ fontSize: 18 }} />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Regenerate">
                        <IconButton 
                          size="small"
                          onClick={() => resolvedRegenerateChart?.(scene.id)}
                          disabled={!resolvedRegenerateChart || !!resolvedGeneratingChartId}
                          sx={{ 
                            color: "#64748b",
                            "&:hover": { color: "#f59e0b", background: "rgba(245, 158, 11, 0.1)" }
                          }}
                        >
                          <RefreshIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Remove chart">
                        <IconButton 
                          size="small"
                          onClick={() => resolvedRemoveChart?.(scene.id)}
                          disabled={!resolvedRemoveChart}
                          sx={{ 
                            color: "#64748b",
                            "&:hover": { color: "#ef4444", background: "rgba(239, 68, 68, 0.1)" }
                          }}
                        >
                          <DeleteIcon sx={{ fontSize: 18 }} />
                        </IconButton>
                      </Tooltip>
                    </Stack>
                  </Box>
                );
              })}
            </Stack>
          ) : (
            <Box sx={{ py: 3, textAlign: "center" }}>
              <BarChartIcon sx={{ fontSize: 36, color: "#cbd5e1", mb: 1 }} />
              <Typography variant="body2" sx={{ color: "#64748b", fontSize: "0.8rem" }}>
                No chart data yet. Add chart data to scenes to generate B-roll visuals.
              </Typography>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Full-size chart preview modal */}
      <Dialog
        open={!!previewModal}
        onClose={closePreview}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            borderRadius: 3,
            background: "#0f172a",
            overflow: "hidden",
          }
        }}
      >
        {previewModal && (
          <>
            <DialogTitle sx={{ 
              display: "flex", 
              alignItems: "center", 
              justifyContent: "space-between",
              background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
              color: "#f1f5f9",
              py: 1.5,
              px: 2,
            }}>
              <Stack direction="row" alignItems="center" spacing={1}>
                <BarChartIcon sx={{ fontSize: 20, color: "#22c55e" }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: "#f1f5f9" }}>
                  {previewModal.title}
                </Typography>
              </Stack>
              <IconButton 
                onClick={closePreview}
                size="small"
                sx={{ color: "#94a3b8", "&:hover": { color: "#f1f5f9" } }}
              >
                <CloseIcon fontSize="small" />
              </IconButton>
            </DialogTitle>
            <DialogContent sx={{ p: 0, display: "flex", justifyContent: "center", alignItems: "center", minHeight: 300, background: "#0f172a" }}>
              <Box
                component="img"
                src={previewModal.url}
                alt={`Chart: ${previewModal.title}`}
                sx={{
                  maxWidth: "100%",
                  maxHeight: "70vh",
                  objectFit: "contain",
                  p: 2,
                }}
              />
            </DialogContent>
          </>
        )}
      </Dialog>
    </>
  );
};