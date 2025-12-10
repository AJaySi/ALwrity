import React from "react";
import { Button, Tooltip, alpha } from "@mui/material";

interface SecondaryButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
  startIcon?: React.ReactNode;
  tooltip?: string;
  ariaLabel?: string;
}

export const SecondaryButton: React.FC<SecondaryButtonProps> = ({
  children,
  onClick,
  disabled = false,
  startIcon,
  tooltip,
  ariaLabel,
}) => {
  const button = (
    <Button
      variant="outlined"
      onClick={onClick}
      disabled={disabled}
      startIcon={startIcon}
      aria-label={ariaLabel}
      sx={{
        borderColor: "rgba(255,255,255,0.2)",
        color: "rgba(255,255,255,0.9)",
        textTransform: "none",
        px: 2.5,
        py: 0.75,
        "&:hover": {
          borderColor: "rgba(255,255,255,0.4)",
          background: alpha("#fff", 0.05),
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

