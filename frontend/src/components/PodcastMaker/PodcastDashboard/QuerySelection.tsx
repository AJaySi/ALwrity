import React, { useState } from "react";
import {
  Stack,
  Typography,
  Chip,
  Tooltip,
  Alert,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Box,
  alpha,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
} from "@mui/material";
import { Search as SearchIcon, AutoAwesome as AutoAwesomeIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon, CheckCircle as CheckCircleIcon, Help as HelpIcon } from "@mui/icons-material";
import { ResearchProvider } from "../../../services/blogWriterApi";
import { Query } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton, SecondaryButton } from "../ui";

interface QuerySelectionProps {
  queries: Query[];
  selectedQueries: Set<string>;
  researchProvider: ResearchProvider;
  isResearching: boolean;
  onToggleQuery: (id: string) => void;
  onProviderChange: (provider: ResearchProvider) => void;
  onRunResearch: () => void;
  onRegenerateQueries: (feedback: string) => Promise<void>;
  onUpdateQuery: (id: string, newQuery: string, newRationale: string) => void;
  onDeleteQuery: (id: string) => void;
  analysis: any;
  idea: string;
}

export const QuerySelection: React.FC<QuerySelectionProps> = ({
  queries,
  selectedQueries,
  researchProvider,
  isResearching,
  onToggleQuery,
  onProviderChange,
  onRunResearch,
  onRegenerateQueries,
  onUpdateQuery,
  onDeleteQuery,
  analysis,
  idea,
}) => {
  const [showRegenDialog, setShowRegenDialog] = useState(false);
  const [regenFeedback, setRegenFeedback] = useState("");
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editQuery, setEditQuery] = useState("");
  const [editRationale, setEditRationale] = useState("");
  const selectedCount = selectedQueries.size;

  const handleRegenerate = async () => {
    if (!regenFeedback.trim()) return;
    setIsRegenerating(true);
    try {
      await onRegenerateQueries(regenFeedback);
      setShowRegenDialog(false);
      setRegenFeedback("");
    } finally {
      setIsRegenerating(false);
    }
  };

  const startEdit = (q: Query) => {
    setEditingId(q.id);
    setEditQuery(q.query);
    setEditRationale(q.rationale);
  };

  const saveEdit = () => {
    if (editingId && editQuery.trim()) {
      onUpdateQuery(editingId, editQuery.trim(), editRationale.trim());
      setEditingId(null);
    }
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditQuery("");
    setEditRationale("");
  };

  return (
    <GlassyCard
      sx={{
        ...glassyCardSx,
        background: "#ffffff",
        border: "1px solid rgba(0,0,0,0.06)",
        boxShadow: "0 10px 28px rgba(15,23,42,0.06)",
        color: "#0f172a",
      }}
    >
      <Stack spacing={3}>
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={2}>
          <Stack direction="row" alignItems="center" spacing={1}>
            <Typography variant="h6" sx={{ display: "flex", alignItems: "center", gap: 1, color: "#0f172a", fontWeight: 700 }}>
              <SearchIcon />
              Research Queries
            </Typography>
            <Tooltip
              title={
                <Box sx={{ maxWidth: 320 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                    How it works:
                  </Typography>
                  <Typography variant="body2" component="div" sx={{ fontSize: "0.8125rem", lineHeight: 1.5 }}>
                    1. Select one or more research queries to focus your research.<br/><br/>
                    2. Click "Run Research" to gather web and semantic insights.<br/><br/>
                    3. The research results will be used to generate a factual, relevant podcast script.
                  </Typography>
                </Box>
              }
              arrow
              placement="top"
            >
              <HelpIcon fontSize="small" sx={{ color: "#94a3b8", cursor: "help", ml: 0.5 }} />
            </Tooltip>
            <Tooltip title="Regenerate research queries with custom feedback">
              <PrimaryButton
                size="small"
                startIcon={<RefreshIcon />}
                onClick={() => setShowRegenDialog(true)}
                sx={{ py: 0.5, px: 1.5, fontSize: "0.75rem" }}
              >
                Regenerate
              </PrimaryButton>
            </Tooltip>
          </Stack>
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 180 }}>
              <InputLabel>Provider</InputLabel>
              <Select
                value={researchProvider}
                onChange={(e) => onProviderChange(e.target.value as ResearchProvider)}
                label="Provider"
                disabled={isResearching}
                size="small"
                sx={{
                  backgroundColor: "#f8fafc",
                  "&:hover": {
                    backgroundColor: "#f1f5f9",
                  },
                }}
              >
                <MenuItem value="google">
                  <Stack direction="row" spacing={1} alignItems="center">
                    <SearchIcon fontSize="small" />
                    <span>Standard Research</span>
                  </Stack>
                </MenuItem>
                <MenuItem value="exa">
                  <Stack direction="row" spacing={1} alignItems="center">
                    <AutoAwesomeIcon fontSize="small" />
                    <span>Deep Research</span>
                  </Stack>
                </MenuItem>
              </Select>
            </FormControl>
            <Chip
              label={`${selectedCount} / ${queries.length} selected`}
              size="small"
              color={selectedCount > 0 ? "primary" : "default"}
            />
          </Stack>
        </Stack>

        <Tooltip
          title={
            researchProvider === "google"
              ? "Standard Research: Fast, fact-checked results with source citations"
              : "Deep Research: Comprehensive analysis with competitor insights and trending topics"
          }
          arrow
        >
          <Alert
            severity="info"
            sx={{
              background: "#e0f2fe",
              border: "1px solid #bae6fd",
              color: "#0f172a",
            }}
          >
            <Typography variant="caption" sx={{ color: "#0f172a" }}>
              {researchProvider === "google"
                ? "Select at least one query (recommended: 3+ for balanced coverage). Standard research provides fact-checked results with source citations."
                : "Select queries for deep research. This mode provides comprehensive analysis with competitor insights and trending topics."}
            </Typography>
          </Alert>
        </Tooltip>

        <List>
          {queries.map((q) => (
            <ListItem
              key={q.id}
              disablePadding
              secondaryAction={
                editingId === q.id ? (
                  <Stack direction="row" spacing={0.5}>
                    <IconButton size="small" onClick={saveEdit} sx={{ color: "#22c55e" }}>
                      <CheckCircleIcon />
                    </IconButton>
                    <IconButton size="small" onClick={cancelEdit} sx={{ color: "#ef4444" }}>
                      <DeleteIcon />
                    </IconButton>
                  </Stack>
                ) : (
                  <Stack direction="row" spacing={0.5} onClick={(e) => e.stopPropagation()}>
                    <IconButton size="small" onClick={() => startEdit(q)} sx={{ color: "#6366f1" }}>
                      <EditIcon />
                    </IconButton>
                    <IconButton size="small" onClick={() => onDeleteQuery(q.id)} sx={{ color: "#ef4444" }}>
                      <DeleteIcon />
                    </IconButton>
                  </Stack>
                )
              }
            >
              {editingId === q.id ? (
                <Box sx={{ width: "100%", p: 1.5, bgcolor: "#f0f9ff", borderRadius: 2, border: "1px solid #bae6fd" }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Query"
                    value={editQuery}
                    onChange={(e) => setEditQuery(e.target.value)}
                    sx={{ mb: 1 }}
                  />
                  <TextField
                    fullWidth
                    size="small"
                    label="Rationale"
                    value={editRationale}
                    onChange={(e) => setEditRationale(e.target.value)}
                  />
                </Box>
              ) : (
                <ListItemButton
                  onClick={() => onToggleQuery(q.id)}
                  disabled={isResearching}
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    border: "1px solid rgba(0,0,0,0.08)",
                    background: selectedQueries.has(q.id) ? alpha("#667eea", 0.08) : "#f8fafc",
                    "&:hover": { background: alpha("#667eea", 0.12) },
                  }}
                >
                  <Checkbox checked={selectedQueries.has(q.id)} edge="start" />
                  <ListItemText
                    primary={q.query}
                    secondary={q.rationale}
                    primaryTypographyProps={{ variant: "body2", fontWeight: 600, color: "#0f172a" }}
                    secondaryTypographyProps={{ variant: "caption", sx: { color: "#475569" } }}
                  />
                </ListItemButton>
              )}
            </ListItem>
          ))}
        </List>

        <Box sx={{ display: "flex", justifyContent: "flex-end", alignItems: "center", gap: 2, flexWrap: "wrap" }}>
          {selectedCount === 0 && (
            <Typography variant="caption" sx={{ color: "#64748b", fontStyle: "italic" }}>
              Select a query to continue
            </Typography>
          )}
          <PrimaryButton
            onClick={onRunResearch}
            disabled={selectedCount === 0 || isResearching}
            loading={isResearching}
            startIcon={<SearchIcon />}
            tooltip={
              selectedCount === 0
                ? "Select at least one query to run research"
                : `Run research with ${selectedCount} selected ${selectedCount === 1 ? "query" : "queries"}`
            }
          >
            {isResearching ? "Running Research..." : selectedCount === 0 ? "Next: Select Query" : "Run Research"}
          </PrimaryButton>
        </Box>
      </Stack>

      {/* Regenerate Queries Dialog */}
      <Dialog
        open={showRegenDialog}
        onClose={() => setShowRegenDialog(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{
          sx: {
            background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
            border: "1px solid rgba(167, 139, 250, 0.3)",
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle sx={{ color: "#fff", display: "flex", alignItems: "center", gap: 1 }}>
          <RefreshIcon sx={{ color: "#a78bfa" }} />
          Regenerate Research Queries
        </DialogTitle>
        <DialogContent sx={{ color: "rgba(255,255,255,0.8)" }}>
          <Typography variant="body2" sx={{ mb: 2, color: "rgba(255,255,255,0.7)" }}>
            Provide custom directions to regenerate research queries. You can specify:
          </Typography>
          <Box sx={{ pl: 2, mb: 2 }}>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", display: "block", mb: 0.5 }}>
              • Specific topics or angles you want to explore
            </Typography>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", display: "block", mb: 0.5 }}>
              • Questions you want answered
            </Typography>
            <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", display: "block", mb: 0.5 }}>
              • Areas where you need more depth
            </Typography>
          </Box>
          <TextField
            fullWidth
            multiline
            rows={4}
            placeholder="e.g., I want to focus more on competitive landscape and pricing strategies. Also need stats on market growth in 2025..."
            value={regenFeedback}
            onChange={(e) => setRegenFeedback(e.target.value)}
            sx={{
              "& .MuiOutlinedInput-root": {
                color: "#fff",
                "& fieldset": { borderColor: "rgba(255,255,255,0.2)" },
                "&:hover fieldset": { borderColor: "rgba(255,255,255,0.3)" },
                "&.Mui-focused fieldset": { borderColor: "#a78bfa" },
              },
            }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <SecondaryButton onClick={() => setShowRegenDialog(false)}>Cancel</SecondaryButton>
          <PrimaryButton
            onClick={handleRegenerate}
            disabled={!regenFeedback.trim() || isRegenerating}
            loading={isRegenerating}
            startIcon={<RefreshIcon />}
          >
            Generate New Queries
          </PrimaryButton>
        </DialogActions>
      </Dialog>
    </GlassyCard>
  );
};

