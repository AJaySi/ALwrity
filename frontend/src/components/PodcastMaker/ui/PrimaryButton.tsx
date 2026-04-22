import React from "react";
import { Button, CircularProgress, Tooltip, alpha, SxProps, Theme } from "@mui/material";

interface PrimaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  tooltip?: string;
  ariaLabel?: string;
  sx?: SxProps<Theme>;
  size?: "small" | "medium" | "large";
}

export const PrimaryButton = React.forwardRef<HTMLButtonElement, PrimaryButtonProps>(({
  children,
  onClick,
  disabled = false,
  loading = false,
  startIcon,
  endIcon,
  tooltip,
  ariaLabel,
  sx,
  size = "medium",
}, ref) => {
  const sizeStyles = {
    small: { px: 1.5, py: 0.5, fontSize: "0.75rem" },
    medium: { px: 3, py: 1, fontSize: "0.875rem" },
    large: { px: 4, py: 1.5, fontSize: "1rem" },
  };

  const button = (
    <Button
      ref={ref}
      variant="contained"
      onClick={onClick}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={16} /> : startIcon}
      endIcon={loading ? undefined : endIcon}
      aria-label={ariaLabel}
      sx={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        color: "white",
        fontWeight: 600,
        textTransform: "none",
        ...sizeStyles[size],
        "&:hover": {
          background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
        },
        "&:disabled": {
          background: alpha("#9ca3af", 0.3),
          color: alpha("#fff", 0.5),
        },
        ...sx,
      }}
    >
      {children}
    </Button>
  );

  return tooltip ? (
    <Tooltip title={tooltip} arrow>
      {button}
    </Tooltip>
  ) : (
    button
  );
});

PrimaryButton.displayName = "PrimaryButton";

