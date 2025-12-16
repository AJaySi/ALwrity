import React from "react";
import { Button, Tooltip, CircularProgress, alpha, SxProps, Theme } from "@mui/material";

interface SecondaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  loading?: boolean;
  startIcon?: React.ReactNode;
  tooltip?: string;
  ariaLabel?: string;
  sx?: SxProps<Theme>;
}

export const SecondaryButton: React.FC<SecondaryButtonProps> = ({
  children,
  onClick,
  disabled = false,
  loading = false,
  startIcon,
  tooltip,
  ariaLabel,
  sx,
}) => {
  const button = (
    <Button
      variant="outlined"
      onClick={onClick}
      disabled={disabled || loading}
      startIcon={loading ? <CircularProgress size={16} /> : startIcon}
      aria-label={ariaLabel}
      sx={[
        {
          borderColor: "rgba(255,255,255,0.2)",
          color: "rgba(255,255,255,0.9)",
          textTransform: "none",
          px: 2.5,
          py: 0.75,
          "&:hover": {
            borderColor: "rgba(255,255,255,0.4)",
            background: alpha("#fff", 0.05),
          },
        },
        ...(Array.isArray(sx) ? sx : sx ? [sx] : []),
      ]}
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

