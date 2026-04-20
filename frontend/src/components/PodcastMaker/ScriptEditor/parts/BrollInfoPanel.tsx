import React from "react";
import { Stack, Box, Typography, Alert, Paper, Button, CircularProgress, Chip } from "@mui/material";
import { BarChart as BarChartIcon, AutoAwesome as AutoAwesomeIcon, Refresh as RefreshIcon, DeleteOutline as DeleteIcon } from "@mui/icons-material";
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

  return (
    <Paper
      sx={{
        p: 3,
        background: "linear-gradient(135deg, rgba(34, 197, 94, 0.05) 0%, rgba(16, 185, 129, 0.05) 100%)",
        border: "1px solid rgba(34, 197, 94, 0.15)",
        borderRadius: 2,
      }}
    >
      <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 2 }}>
        <Box sx={{ width: 40, height: 40, borderRadius: "50%", background: "linear-gradient(135deg, #22c55e 0%, #10b981 100%)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <BarChartIcon sx={{ color: "#ffffff", fontSize: "1.5rem" }} />
        </Box>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ color: "#0f172a", fontWeight: 600, fontSize: "1.1rem" }}>
            B-Roll Charts
          </Typography>
          <Typography variant="body2" sx={{ color: "#64748b", mt: 0.25 }}>
            Programmatic charts extracted from research data
          </Typography>
        </Box>
        
        {hasChartData && (
          <Chip 
            label={`${resolvedScenesWithCharts} scene${resolvedScenesWithCharts > 1 ? 's' : ''} with charts`}
            size="small"
            sx={{ background: "rgba(34, 197, 94, 0.1)", color: "#16a34a", fontWeight: 600 }}
          />
        )}
      </Stack>

      {!hasChartData ? (
        <Alert severity="info" sx={{ background: "rgba(34, 197, 94, 0.06)", border: "1px solid rgba(34, 197, 94, 0.15)", "& .MuiAlert-icon": { color: "#22c55e" } }}>
          <Typography variant="body2" sx={{ color: "#0f172a", lineHeight: 1.7 }}>
            <strong style={{ fontWeight: 600 }}>No charts detected.</strong> If your research contains statistics or metrics, the script generation will automatically extract chart data for B-roll visualization.
          </Typography>
        </Alert>
      ) : (
        <Stack spacing={2}>
          <Typography variant="body2" sx={{ color: "#475569", lineHeight: 1.7 }}>
            Your script contains <strong style={{ fontWeight: 600 }}>{scenesWithData.length}</strong> scene(s) with chart data. 
            Click below to generate chart previews for the Write phase.
          </Typography>
          
          <Stack direction="row" spacing={2}>
            <Button
              variant="contained"
              startIcon={resolvedGeneratingChartId ? <CircularProgress size={16} color="inherit" /> : <AutoAwesomeIcon />}
              onClick={resolvedGenerateChartPreviews}
              disabled={!!resolvedGeneratingChartId || !resolvedGenerateChartPreviews}
              sx={{
                background: "linear-gradient(135deg, #22c55e 0%, #10b981 100%)",
                "&:hover": { background: "linear-gradient(135deg, #16a34a 0%, #059669 100%)" },
                textTransform: "none",
                fontWeight: 600,
              }}
            >
              {resolvedGeneratingChartId ? "Generating..." : "Generate Chart Previews"}
            </Button>
          </Stack>

          {scenesWithData.map((scene) => (
            <Box 
              key={scene.id}
              sx={{
                p: 2,
                background: "rgba(0,0,0,0.02)",
                borderRadius: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between"
              }}
            >
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {scene.title}
                </Typography>
                <Typography variant="caption" sx={{ color: "#64748b" }}>
                  {scene.chart_data?.type || "chart"} • {scene.chart_data?.labels?.length || 0} data points
                </Typography>
              </Box>
              
              <Stack direction="row" spacing={1}>
                {resolvedGeneratingChartId === scene.id ? (
                  <CircularProgress size={20} />
                ) : scene.broll_preview_url ? (
                  <>
                    <Chip 
                      label="Preview Ready" 
                      size="small" 
                      sx={{ background: "rgba(34, 197, 94, 0.1)", color: "#16a34a" }}
                    />
                    <Button 
                      size="small" 
                      startIcon={<RefreshIcon />}
                      onClick={() => resolvedRegenerateChart?.(scene.id)}
                      disabled={!resolvedRegenerateChart}
                    >
                      Regenerate
                    </Button>
                    <Button 
                      size="small" 
                      startIcon={<DeleteIcon />}
                      onClick={() => resolvedRemoveChart?.(scene.id)}
                      disabled={!resolvedRemoveChart}
                      sx={{ color: "#ef4444" }}
                    >
                      Remove
                    </Button>
                  </>
                ) : null}
              </Stack>
            </Box>
          ))}
        </Stack>
      )}
    </Paper>
  );
};
