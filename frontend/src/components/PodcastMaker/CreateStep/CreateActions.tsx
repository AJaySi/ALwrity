import React, { useState, useEffect } from "react";
import {
  Stack,
  Alert,
  Typography,
  alpha,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Box,
  LinearProgress,
} from "@mui/material";
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  AutoAwesome as AutoAwesomeIcon,
  CheckCircle as CheckCircleIcon,
  Analytics as AnalyticsIcon,
  Title as TitleIcon,
  ListAlt as ListAltIcon,
  Psychology as PsychologyIcon,
  RecordVoiceOver as RecordVoiceOverIcon,
} from "@mui/icons-material";
import { PrimaryButton, SecondaryButton } from "../ui";

interface CreateActionsProps {
  reset: () => void;
  submit: () => void;
  canSubmit: boolean;
  isSubmitting: boolean;
}

// ============================================================================
// Constants & Data
// ============================================================================

const ANALYSIS_FEATURES = [
  { icon: <AnalyticsIcon />, text: "Target audience & content type analysis" },
  { icon: <ListAltIcon />, text: "5 high-impact keywords for discoverability" },
  { icon: <TitleIcon />, text: "3 catchy episode title suggestions" },
  { icon: <PsychologyIcon />, text: "2 detailed episode outlines with segments" },
  { icon: <RecordVoiceOverIcon />, text: "4-6 research queries for AI-powered research" },
  { icon: <CheckCircleIcon />, text: "Episode hook, key takeaways & listener CTA" },
];

const ANALYSIS_PROGRESS_STEPS = [
  "Analyzing target audience & content type",
  "Generating keywords & title suggestions",
  "Creating episode outlines",
  "Generating research queries",
  "Creating hook, takeaways & CTA",
];

const INFO_BANNER_TEXT =
  "Podcast avatar Image is required. Brand avatar is default. You can choose from asset library or upload your picture. If not, AI Avatar will be generated automatically.";

// ============================================================================
// Styles
// ============================================================================

const styles = {
  dialog: {
    background: "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
    border: "1px solid rgba(167, 139, 250, 0.3)",
    borderRadius: 3,
  },
  infoAlert: {
    background: alpha("#f0f4ff", 0.6),
    border: "1px solid rgba(99, 102, 241, 0.15)",
    borderRadius: 2,
    boxShadow: "0 1px 3px rgba(99, 102, 241, 0.08)",
  },
  progressDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    bgcolor: "#a78bfa",
  },
  dialogContent: {
    color: "rgba(255,255,255,0.8)",
    minHeight: 200,
    py: 3,
  },
};

// ============================================================================
// Sub-Components
// ============================================================================

const InfoBanner: React.FC<{ showInfo: boolean; setShowInfo: (v: boolean) => void }> = ({
  showInfo,
  setShowInfo,
}) => (
  <Collapse in={showInfo}>
    <Alert
      severity="info"
      icon={<InfoIcon sx={{ color: "#6366f1", fontSize: "1.125rem" }} />}
      onClose={() => setShowInfo(false)}
      sx={styles.infoAlert}
    >
      <Typography variant="body2" sx={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, fontWeight: 400 }}>
        {INFO_BANNER_TEXT}
      </Typography>
    </Alert>
  </Collapse>
);

const ShowTipsLink: React.FC<{ onClick: () => void }> = ({ onClick }) => (
  <Stack direction="row" alignItems="center" spacing={1}>
    <InfoIcon sx={{ fontSize: 16, color: "#6366f1" }} />
    <Typography variant="caption" sx={{ color: "#6366f1", cursor: "pointer", "&:hover": { textDecoration: "underline" } }} onClick={onClick}>
      Show tips
    </Typography>
  </Stack>
);

const AnalysisProgressView: React.FC = () => (
  <Stack spacing={3} alignItems="center" sx={styles.dialogContent} justifyContent="center">
    <Box sx={{ position: "relative", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <CircularProgress size={80} thickness={3} sx={{ color: "#a78bfa" }} />
      <Box sx={{ position: "absolute", display: "flex", flexDirection: "column", alignItems: "center" }}>
        <AutoAwesomeIcon sx={{ color: "#a78bfa", fontSize: 32 }} />
      </Box>
    </Box>

    <Typography variant="h6" sx={{ color: "#fff", textAlign: "center" }}>
      Analyzing Your Podcast Idea
    </Typography>

    <LinearProgress
      sx={{
        width: "100%",
        height: 8,
        borderRadius: 4,
        bgcolor: "rgba(255,255,255,0.1)",
        "& .MuiLinearProgress-bar": { bgcolor: "#a78bfa", borderRadius: 4 },
      }}
    />

    <Stack spacing={1} sx={{ width: "100%" }}>
      <Typography variant="body2" sx={{ color: "rgba(255,255,255,0.7)", textAlign: "center" }}>
        This may take a few moments...
      </Typography>
      <Stack spacing={0.5} alignItems="flex-start" sx={{ pl: 2 }}>
        {ANALYSIS_PROGRESS_STEPS.map((step, idx) => (
          <Typography key={idx} variant="caption" sx={{ color: "rgba(255,255,255,0.5)", display: "flex", alignItems: "center", gap: 0.5 }}>
            <Box sx={styles.progressDot} /> {step}
          </Typography>
        ))}
      </Stack>
    </Stack>
  </Stack>
);

const WhatYoullGetView: React.FC = () => (
  <>
    <Typography variant="body2" sx={{ mb: 2, color: "rgba(255,255,255,0.7)" }}>
      Click "Start Analysis" to begin AI-powered podcast planning. Here's what we'll generate for you:
    </Typography>
    <List>
      {ANALYSIS_FEATURES.map((feature, index) => (
        <ListItem key={index} sx={{ px: 0, py: 0.5 }}>
          <ListItemIcon sx={{ minWidth: 36, color: "#a78bfa" }}>{feature.icon}</ListItemIcon>
          <ListItemText
            primary={feature.text}
            primaryTypographyProps={{ sx: { color: "rgba(255,255,255,0.9)", fontSize: "0.9rem" } }}
          />
        </ListItem>
      ))}
    </List>
  </>
);

// ============================================================================
// Main Component
// ============================================================================

export const CreateActions: React.FC<CreateActionsProps> = ({ reset, submit, canSubmit, isSubmitting }) => {
  const [showInfo, setShowInfo] = useState(true);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisStarted, setAnalysisStarted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowInfo(false), 8000);
    return () => clearTimeout(timer);
  }, []);

  // Close modal when analysis completes
  useEffect(() => {
    if (!isSubmitting && analysisStarted) {
      setShowAnalysisModal(false);
      setAnalysisStarted(false);
    }
  }, [isSubmitting, analysisStarted]);

  const handleSubmitClick = () => {
    if (canSubmit && !isSubmitting) setShowAnalysisModal(true);
  };

  const handleStartAnalysis = () => {
    setAnalysisStarted(true);
    submit();
  };

  const showProgressInModal = showAnalysisModal && (analysisStarted || isSubmitting);

  return (
    <Stack spacing={2}>
      <InfoBanner showInfo={showInfo} setShowInfo={setShowInfo} />
      {!showInfo && <ShowTipsLink onClick={() => setShowInfo(true)} />}

      <Stack direction="row" justifyContent="flex-end" spacing={1}>
        <SecondaryButton onClick={reset} startIcon={<RefreshIcon />}>
          Reset
        </SecondaryButton>
        <PrimaryButton
          onClick={handleSubmitClick}
          disabled={!canSubmit || isSubmitting}
          loading={isSubmitting}
          startIcon={<AutoAwesomeIcon />}
          tooltip={!canSubmit ? "Enter an idea/URL and add a podcast avatar to continue" : "We'll start AI analysis after this click"}
        >
          {isSubmitting ? "Analyzing..." : "Analyze & Continue"}
        </PrimaryButton>
      </Stack>

      <Dialog
        open={showAnalysisModal}
        onClose={() => !isSubmitting && setShowAnalysisModal(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: styles.dialog }}
      >
        <DialogTitle sx={{ color: "#fff", display: "flex", alignItems: "center", gap: 1 }}>
          {isSubmitting ? (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <CircularProgress size={24} sx={{ color: "#a78bfa" }} />
              Analyzing Your Podcast Idea
            </Box>
          ) : (
            <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
              <AutoAwesomeIcon sx={{ color: "#a78bfa" }} />
              What You'll Get
            </Box>
          )}
        </DialogTitle>

        <DialogContent sx={styles.dialogContent}>
          {showProgressInModal ? <AnalysisProgressView /> : <WhatYoullGetView />}
        </DialogContent>

        <DialogActions sx={{ px: 3, pb: 3 }}>
          {showProgressInModal ? null : (
            <>
              <SecondaryButton onClick={() => setShowAnalysisModal(false)}>Cancel</SecondaryButton>
              <PrimaryButton onClick={handleStartAnalysis} startIcon={<AutoAwesomeIcon />}>
                Start Analysis
              </PrimaryButton>
            </>
          )}
        </DialogActions>
      </Dialog>
    </Stack>
  );
};
