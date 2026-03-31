import React, { useState, useEffect } from "react";
import { Stack, Alert, Typography, alpha, IconButton, Collapse } from "@mui/material";
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  AutoAwesome as AutoAwesomeIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from "@mui/icons-material";
import { PrimaryButton, SecondaryButton } from "../ui";

interface CreateActionsProps {
  reset: () => void;
  submit: () => void;
  canSubmit: boolean;
  isSubmitting: boolean;
}

export const CreateActions: React.FC<CreateActionsProps> = ({
  reset,
  submit,
  canSubmit,
  isSubmitting,
}) => {
  const [showInfo, setShowInfo] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowInfo(false);
    }, 8000);
    return () => clearTimeout(timer);
  }, []);

  return (
    <Stack spacing={2}>
      {/* Collapsible Info Banner */}
      <Collapse in={showInfo}>
        <Alert 
          severity="info" 
          icon={<InfoIcon sx={{ color: "#6366f1", fontSize: "1.125rem" }} />}
          onClose={() => setShowInfo(false)}
          sx={{ 
            background: alpha("#f0f4ff", 0.6),
            border: "1px solid rgba(99, 102, 241, 0.15)",
            borderRadius: 2,
            boxShadow: "0 1px 3px rgba(99, 102, 241, 0.08)",
            "& .MuiAlert-message": {
              width: "100%",
            },
          }}
        >
          <Typography variant="body2" sx={{ fontSize: "0.875rem", color: "#475569", lineHeight: 1.6, fontWeight: 400 }}>
            Podcast avatar Image is required. Brand avatar is default. You can choose from asset library or upload your picture. If not, AI Avatar will be generated automatically.
          </Typography>
        </Alert>
      </Collapse>

      {!showInfo && (
        <Stack direction="row" alignItems="center" spacing={1}>
          <InfoIcon sx={{ fontSize: 16, color: "#6366f1" }} />
          <Typography 
            variant="caption" 
            sx={{ color: "#6366f1", cursor: "pointer", "&:hover": { textDecoration: "underline" } }}
            onClick={() => setShowInfo(true)}
          >
            Show tips
          </Typography>
        </Stack>
      )}

      <Stack direction="row" justifyContent="flex-end" spacing={1}>
        <SecondaryButton onClick={reset} startIcon={<RefreshIcon />}>
          Reset
        </SecondaryButton>
        <PrimaryButton
          onClick={submit}
          disabled={!canSubmit || isSubmitting}
          loading={isSubmitting}
          startIcon={<AutoAwesomeIcon />}
          tooltip={!canSubmit ? "Enter an idea/URL and add a podcast avatar to continue" : "We'll start AI analysis after this click"}
        >
          {isSubmitting ? "Analyzing..." : "Analyze & Continue"}
        </PrimaryButton>
      </Stack>
    </Stack>
  );
};
