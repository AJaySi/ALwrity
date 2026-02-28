import React from "react";
import { Stack, Alert, Typography, alpha } from "@mui/material";
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  AutoAwesome as AutoAwesomeIcon,
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
  return (
    <Stack spacing={3.5}>
      {/* Info Banner */}
      <Alert 
        severity="info" 
        icon={<InfoIcon sx={{ color: "#6366f1", fontSize: "1.125rem" }} />}
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
          Podcast avatar Image is required, brand avatar is Default, you can choose existing images from asset library Or Upload your Picture. If not, AI Avatar will be generated automatically.
        </Typography>
      </Alert>

      <Stack direction="row" justifyContent="flex-end" spacing={1}>
        <SecondaryButton onClick={reset} startIcon={<RefreshIcon />}>
          Reset
        </SecondaryButton>
        <PrimaryButton
          onClick={submit}
          disabled={!canSubmit || isSubmitting}
          loading={isSubmitting}
          startIcon={<AutoAwesomeIcon />}
          tooltip={!canSubmit ? "Enter an idea or URL to continue" : "We’ll start AI analysis after this click"}
        >
          {isSubmitting ? "Analyzing..." : "Analyze & Continue"}
        </PrimaryButton>
      </Stack>
    </Stack>
  );
};
