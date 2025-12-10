import React from "react";
import { Button, CircularProgress, Tooltip, alpha } from "@mui/material";

interface PrimaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  startIcon?: React.ReactNode;
  tooltip?: string;
  ariaLabel?: string;
}

export const PrimaryButton: React.FC<PrimaryButtonProps> = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  startIcon,
  tooltip,
  ariaLabel,
}) => {
  const button = (
    <Button
      variant="contained"
      onClick={onClick}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={16} /> : startIcon}
      aria-label={ariaLabel}
      sx={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        fontWeight: 600,
        textTransform: "none",
        px: 3,
        py: 1,
        "&:hover": {
          background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
        },
        "&:disabled": {
          background: alpha("#9ca3af", 0.3),
          color: alpha("#fff", 0.5),
        },
      }}
    >
      {children}
    </Button>
  );

  return tooltip ? (
    <Tooltip title={tooltip} arrow>
      <span>{button}</span>
    </Tooltip>
  ) : (
    button
  );
};

