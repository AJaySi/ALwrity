import React, { useState, useEffect, useRef } from "react";
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
  ListItemIcon,
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
  CircularProgress,
  LinearProgress,
  Divider,
  useMediaQuery,
  useTheme,
} from "@mui/material";
import { Search as SearchIcon, AutoAwesome as AutoAwesomeIcon, Refresh as RefreshIcon, Edit as EditIcon, Delete as DeleteIcon, CheckCircle as CheckCircleIcon, Help as HelpIcon, TrendingUp as TrendingUpIcon, Psychology as PsychologyIcon, FactCheck as FactCheckIcon, MenuBook as MenuBookIcon } from "@mui/icons-material";
import { ResearchProvider } from "../../../services/blogWriterApi";
import { Query } from "../types";
import { GlassyCard, glassyCardSx, PrimaryButton, SecondaryButton } from "../ui";

const RESEARCH_FEATURES = [
  { icon: <TrendingUpIcon />, text: "Latest trends & statistics from the web" },
  { icon: <FactCheckIcon />, text: "Verified facts with source citations" },
  { icon: <MenuBookIcon />, text: "Case studies & real-world examples" },
  { icon: <PsychologyIcon />, text: "Audience insights & pain points" },
];

const RESEARCH_MESSAGES = [
  { title: "Connecting to Research Engine", message: "Initializing neural search to gather fresh insights..." },
  { title: "Searching the Web", message: "Scanning thousands of sources for relevant data..." },
  { title: "Analyzing Content", message: "Extracting key facts, statistics, and trends..." },
  { title: "Verifying Information", message: "Cross-referencing sources to ensure accuracy..." },
  { title: "Synthesizing Insights", message: "Compiling findings into actionable research cards..." },
  { title: "Finalizing Research", message: "Organizing insights for your podcast episode..." },
];

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
  researchAnnouncement?: string;
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
  researchAnnouncement,
}) => {
  const [showResearchModal, setShowResearchModal] = useState(false);
  const [researchStarted, setResearchStarted] = useState(false);
  const [progressIndex, setProgressIndex] = useState(0);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const prevIsResearchingRef = useRef(isResearching);
  const modalCloseTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Close modal only when research actually completes (transitions from true to false)
  // Prevent closing while research is in progress
  useEffect(() => {
    // Clear any pending close timeout when research starts
    if (researchStarted && isResearching) {
      if (modalCloseTimeoutRef.current) {
        clearTimeout(modalCloseTimeoutRef.current);
        modalCloseTimeoutRef.current = null;
      }
      return;
    }

    const wasResearching = prevIsResearchingRef.current;
    const nowNotResearching = !isResearching;
    
    if (showResearchModal && researchStarted && wasResearching && nowNotResearching) {
      modalCloseTimeoutRef.current = setTimeout(() => setShowResearchModal(false), 1000);
    }
    
    prevIsResearchingRef.current = isResearching;

    return () => {
      if (modalCloseTimeoutRef.current) {
        clearTimeout(modalCloseTimeoutRef.current);
      }
    };
  }, [isResearching, showResearchModal, researchStarted]);

  // Progress message cycling
  useEffect(() => {
    if (!isResearching || !researchStarted) {
      setProgressIndex(0);
      return;
    }
    const interval = setInterval(() => {
      setProgressIndex((prev) => (prev < RESEARCH_MESSAGES.length - 1 ? prev + 1 : prev));
    }, 4000);
    return () => clearInterval(interval);
  }, [isResearching, researchStarted]);

  const handleStartResearch = () => {
    setResearchStarted(true);
    setProgressIndex(0);
    onRunResearch();
  };

  const showProgressInModal = showResearchModal && (researchStarted || isResearching);
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
            onClick={() => setShowResearchModal(true)}
            disabled={selectedCount === 0 || isResearching}
            loading={isResearching}
            startIcon={<SearchIcon />}
            tooltip={
              selectedCount === 0
                ? "Select at least one query to run research"
                : `Run research with ${selectedCount} selected ${selectedCount === 1 ? "query" : "queries"}`
            }
          >
            {isResearching ? "Running Research..." : selectedCount === 0 ? "Next: Select Query" : "Start Neural Research"}
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

      {/* Research Progress Modal */}
      <Dialog
        open={showResearchModal}
        disableEscapeKeyDown={isResearching}
        onClose={(event, reason) => {
          // Only allow closing if NOT researching and research hasn't started
          if (!isResearching && !researchStarted) {
            setShowResearchModal(false);
          }
        }}
        maxWidth="sm"
        fullWidth
        fullScreen={isMobile}
        PaperProps={{
          sx: {
            background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
            border: "1px solid rgba(96, 165, 250, 0.3)",
            borderRadius: 3,
          },
        }}
      >
        <DialogTitle sx={{ color: "#fff", display: "flex", alignItems: "center", gap: 1, fontSize: isMobile ? "1rem" : "1.25rem" }}>
          {isResearching ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={20} sx={{ color: "#60a5fa" }} />
              Neural Research in Progress
            </Box>
          ) : (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <SearchIcon sx={{ color: "#60a5fa" }} />
              What You'll Get
            </Box>
          )}
        </DialogTitle>

        <DialogContent sx={{ color: "rgba(255,255,255,0.8)", minHeight: 200, py: 2, px: { xs: 2, sm: 3 }, maxHeight: { xs: "80vh", sm: "70vh" }, overflowY: "auto" }}>
          {showProgressInModal ? (
            <Stack spacing={2}>
              <Box sx={{ textAlign: "center" }}>
                <Box sx={{ position: "relative", display: "inline-flex", alignItems: "center", justifyContent: "center", mb: 2 }}>
                  <CircularProgress size={isMobile ? 50 : 60} thickness={3} sx={{ color: "#60a5fa" }} />
                  <Box sx={{ position: "absolute", display: "flex", flexDirection: "column", alignItems: "center" }}>
                    <SearchIcon sx={{ color: "#60a5fa", fontSize: isMobile ? 20 : 24 }} />
                  </Box>
                </Box>

                <Typography variant="subtitle1" sx={{ color: "#60a5fa", fontWeight: 600, mt: 1, fontSize: isMobile ? "0.85rem" : "0.95rem" }}>
                  {RESEARCH_MESSAGES[Math.min(progressIndex, RESEARCH_MESSAGES.length - 1)].title}
                </Typography>
                
                <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", mt: 0.5, fontSize: isMobile ? "0.75rem" : "0.85rem", px: 1 }}>
                  {RESEARCH_MESSAGES[Math.min(progressIndex, RESEARCH_MESSAGES.length - 1)].message}
                </Typography>

                {researchAnnouncement && researchAnnouncement !== RESEARCH_MESSAGES[Math.min(progressIndex, RESEARCH_MESSAGES.length - 1)].message && (
                  <Typography variant="caption" sx={{ color: "#10b981", mt: 0.5, display: "block", fontSize: "0.75rem" }}>
                    {researchAnnouncement}
                  </Typography>
                )}

                <LinearProgress
                  sx={{
                    width: "100%",
                    height: 4,
                    borderRadius: 2,
                    bgcolor: "rgba(255,255,255,0.1)",
                    mt: 2,
                    "& .MuiLinearProgress-bar": { bgcolor: "#60a5fa", borderRadius: 2 },
                  }}
                />
                
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.4)", mt: 0.5, display: "block" }}>
                  Step {Math.min(progressIndex, RESEARCH_MESSAGES.length - 1) + 1} of {RESEARCH_MESSAGES.length}
                </Typography>
              </Box>

              <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />

              <Box>
                <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.6)", textTransform: "uppercase", letterSpacing: "0.05em", fontSize: "0.65rem", mb: 1, display: "block" }}>
                  Why Neural Research?
                </Typography>
                <Stack spacing={1}>
                  {[
                    "Fresh web data — bypasses LLM training cutoff",
                    "Reduces AI hallucinations with verified sources",
                    "Real-time trends and current statistics",
                    "Citation-backed facts for credibility",
                  ].map((item, idx) => (
                    <Box key={idx} sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <CheckCircleIcon sx={{ fontSize: 14, color: "#10b981" }} />
                      <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)", fontSize: "0.75rem" }}>
                        {item}
                      </Typography>
                    </Box>
                  ))}
                </Stack>
              </Box>
            </Stack>
          ) : (
            <Stack spacing={2}>
              <Typography variant="body2" sx={{ mb: 2, color: "rgba(255,255,255,0.7)", fontSize: isMobile ? "0.85rem" : "0.9rem" }}>
                Click "Start Research" to gather AI-powered insights. Here's what we'll find for you:
              </Typography>
              <List>
                {RESEARCH_FEATURES.map((feature, index) => (
                  <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
                    <ListItemIcon sx={{ minWidth: 36, color: "#60a5fa" }}>{feature.icon}</ListItemIcon>
                    <ListItemText
                      primary={feature.text}
                      primaryTypographyProps={{ sx: { color: "rgba(255,255,255,0.9)", fontSize: isMobile ? "0.8rem" : "0.9rem" } }}
                    />
                  </ListItem>
                ))}
              </List>

              <Divider sx={{ borderColor: "rgba(255,255,255,0.15)" }} />

              <Box sx={{ p: 1.5, borderRadius: 2, bgcolor: "rgba(16, 185, 129, 0.1)", border: "1px solid rgba(16, 185, 129, 0.2)" }}>
                <Stack direction="row" spacing={1} alignItems="flex-start">
                  <CheckCircleIcon sx={{ color: "#10b981", fontSize: 18, mt: 0.25 }} />
                  <Box>
                    <Typography variant="body2" sx={{ color: "#10b981", fontWeight: 600, fontSize: "0.85rem" }}>
                      Research Benefits
                    </Typography>
                    <Typography variant="caption" sx={{ color: "rgba(255,255,255,0.7)", fontSize: "0.75rem", display: "block", mt: 0.5 }}>
                      • Up-to-date information beyond LLM training data<br/>
                      • Reduces fact-checking time significantly<br/>
                      • Credible sources boost listener trust<br/>
                      • Helps AI script sound expert and authoritative
                    </Typography>
                  </Box>
                </Stack>
              </Box>
            </Stack>
          )}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          {showProgressInModal ? null : (
            <>
              <SecondaryButton onClick={() => setShowResearchModal(false)}>Cancel</SecondaryButton>
              <PrimaryButton onClick={handleStartResearch} startIcon={<SearchIcon />}>
                Start Research
              </PrimaryButton>
            </>
          )}
        </DialogActions>
      </Dialog>
    </GlassyCard>
    );
  };

