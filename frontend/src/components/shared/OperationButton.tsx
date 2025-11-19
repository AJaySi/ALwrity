import React, { useMemo } from 'react';
import {
  Button,
  ButtonProps,
  Tooltip,
  Box,
  Typography,
  CircularProgress,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import { SxProps, Theme } from '@mui/material/styles';
import { usePreflightCheck, UsePreflightCheckOptions } from '../../hooks/usePreflightCheck';
import { PreflightOperation } from '../../services/billingService';

export interface OperationButtonProps {
  // Operation definition
  operation: PreflightOperation;
  
  // Button configuration
  label: string; // Base label (e.g., "Generate HD Video")
  variant?: 'contained' | 'outlined' | 'text';
  size?: 'small' | 'medium' | 'large';
  color?: 'primary' | 'secondary' | 'success' | 'error';
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  
  // Pre-flight check behavior
  showCost?: boolean; // Show cost in label (default: true)
  checkOnHover?: boolean; // Check on hover (default: true)
  checkOnMount?: boolean; // Check on mount (default: false)
  
  // Callbacks
  onClick: () => void;
  onPreflightResult?: (canProceed: boolean) => void;
  
  // Customization
  disabled?: boolean; // Additional disabled state
  loading?: boolean; // Loading state override
  tooltipPlacement?: 'top' | 'bottom' | 'left' | 'right';
  
  // Styling
  sx?: SxProps<Theme>;
  fullWidth?: boolean;
  
  // Additional button props
  buttonProps?: Partial<ButtonProps>;
}

/**
 * Reusable button component with pre-flight check and cost estimation.
 * 
 * Features:
 * - Shows estimated cost in button label
 * - Performs pre-flight check on hover (debounced)
 * - Shows detailed tooltip with limits/remaining quota
 * - Disables button with messaging if blocked
 */
export const OperationButton: React.FC<OperationButtonProps> = ({
  operation,
  label,
  variant = 'contained',
  size = 'medium',
  color = 'primary',
  startIcon,
  endIcon,
  showCost = true,
  checkOnHover = true,
  checkOnMount = false,
  onClick,
  onPreflightResult,
  disabled: externalDisabled = false,
  loading: externalLoading = false,
  tooltipPlacement = 'top',
  sx,
  fullWidth = false,
  buttonProps = {},
}) => {
  const preflightOptions: UsePreflightCheckOptions = {
    operation,
    enabled: checkOnHover || checkOnMount,
    debounceMs: 300,
    cacheTtl: 5000,
  };

  const {
    canProceed,
    estimatedCost,
    limitInfo,
    loading: preflightLoading,
    error: preflightError,
    checkOnHover: triggerCheckOnHover,
    checkNow: triggerCheckNow,
  } = usePreflightCheck(preflightOptions);

  // Check on mount if requested
  React.useEffect(() => {
    if (checkOnMount) {
      triggerCheckNow();
    }
  }, [checkOnMount, triggerCheckNow]);

  // Notify parent of pre-flight result changes
  React.useEffect(() => {
    if (onPreflightResult) {
      onPreflightResult(canProceed);
    }
  }, [canProceed, onPreflightResult]);

  // Format cost as currency
  const formattedCost = useMemo(() => {
    if (!showCost || estimatedCost === 0) {
      return null;
    }
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(estimatedCost);
  }, [estimatedCost, showCost]);

  // Build button label with cost
  const buttonLabel = useMemo(() => {
    if (formattedCost) {
      return `${label} ${formattedCost}`;
    }
    return label;
  }, [label, formattedCost]);

  // Determine if button should be disabled
  const isDisabled = useMemo(() => {
    return externalDisabled || externalLoading || preflightLoading || !canProceed;
  }, [externalDisabled, externalLoading, preflightLoading, canProceed]);

  // Build tooltip content
  const tooltipContent = useMemo(() => {
    const content: React.ReactNode[] = [];

    if (preflightLoading) {
      content.push(
        <Typography key="loading" variant="body2" sx={{ mb: 1 }}>
          Checking limits...
        </Typography>
      );
    } else if (preflightError) {
      content.push(
        <Typography key="error" variant="body2" sx={{ mb: 1, color: 'error.main', fontWeight: 600 }}>
          {preflightError}
        </Typography>
      );
    } else if (limitInfo) {
      const { current_usage, limit, remaining } = limitInfo;
      const isUnlimited = limit === 0 || remaining === Infinity;
      
      content.push(
        <Box key="limits" sx={{ mb: 1 }}>
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
            {canProceed ? '✅ Operation Allowed' : '❌ Operation Blocked'}
          </Typography>
          {isUnlimited ? (
            <Typography variant="caption" sx={{ display: 'block' }}>
              Usage: {current_usage} / Unlimited
            </Typography>
          ) : (
            <Typography variant="caption" sx={{ display: 'block' }}>
              Usage: {current_usage} / {limit} ({remaining} remaining)
            </Typography>
          )}
          {formattedCost && (
            <Typography variant="caption" sx={{ display: 'block', mt: 0.5, fontWeight: 600 }}>
              Estimated Cost: {formattedCost}
            </Typography>
          )}
        </Box>
      );
    }

    if (preflightError && !canProceed) {
      content.push(
        <Typography key="message" variant="caption" sx={{ display: 'block', color: 'error.main' }}>
          {preflightError}
        </Typography>
      );
    }

    return content.length > 0 ? <Box sx={{ p: 0.5 }}>{content}</Box> : null;
  }, [canProceed, estimatedCost, formattedCost, limitInfo, preflightError, preflightLoading]);

  // Handle hover
  const handleMouseEnter = () => {
    if (checkOnHover) {
      triggerCheckOnHover();
    }
  };

  // Handle click
  const handleClick = () => {
    if (!isDisabled && canProceed) {
      onClick();
    }
  };

  // Determine button color based on state
  const buttonColor = useMemo(() => {
    if (!canProceed) {
      return 'error';
    }
    return color;
  }, [canProceed, color]);

  // Determine if we should show loading spinner
  const showLoading = externalLoading || (preflightLoading && checkOnMount);

  // Custom label override for loading state
  const displayLabel = useMemo(() => {
    if (externalLoading && buttonProps?.children) {
      return buttonProps.children;
    }
    if (showLoading && !externalLoading) {
      return 'Checking...';
    }
    if (!canProceed && preflightError) {
      return preflightError;
    }
    return buttonLabel;
  }, [externalLoading, showLoading, canProceed, preflightError, buttonLabel, buttonProps?.children]);

  // Build button with icon
  const button = (
    <Button
      variant={variant}
      size={size}
      color={buttonColor}
      startIcon={
        showLoading ? (
          <CircularProgress size={16} color="inherit" />
        ) : !canProceed ? (
          <WarningIcon fontSize="small" />
        ) : (
          startIcon
        )
      }
      endIcon={endIcon}
      onClick={handleClick}
      disabled={isDisabled}
      fullWidth={fullWidth}
      onMouseEnter={handleMouseEnter}
      sx={sx}
      {...buttonProps}
    >
      {displayLabel}
    </Button>
  );

  // Wrap with tooltip if we have content
  if (tooltipContent || checkOnHover) {
    return (
      <Tooltip
        title={tooltipContent || 'Hover to check limits'}
        arrow
        placement={tooltipPlacement}
        onOpen={handleMouseEnter}
      >
        <span style={{ display: 'inline-flex' }}>
          {button}
        </span>
      </Tooltip>
    );
  }

  return button;
};

