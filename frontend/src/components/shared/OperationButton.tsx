import React, { useMemo, useRef } from 'react';
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
    onBlocked: (response) => {
      // Handle blocked response if needed
    },
    onAllowed: (response) => {
      // Handle allowed response if needed
    },
  };

  const {
    canProceed,
    estimatedCost,
    limitInfo,
    loading: preflightLoading,
    error: preflightError,
    check: triggerCheck,
  } = usePreflightCheck(preflightOptions);

  // Check on mount if requested
  React.useEffect(() => {
    if (checkOnMount) {
      triggerCheck(operation);
    }
  }, [checkOnMount, triggerCheck, operation]);

  // Notify parent of pre-flight result changes
  React.useEffect(() => {
    if (onPreflightResult && canProceed !== null) {
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
  // NOTE: We do NOT disable when canProceed === false to allow users to click and see subscription modal
  // The API call will return 429, which triggers the subscription modal via global error handler
  const isDisabled = useMemo(() => {
    return externalDisabled || externalLoading || preflightLoading;
    // Removed: || (canProceed !== null && !canProceed)
    // This allows users to click even when limits are exceeded, so they can see subscription modal
  }, [externalDisabled, externalLoading, preflightLoading]);

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
            {(canProceed === null || canProceed) ? '✅ Operation Allowed' : '❌ Operation Blocked'}
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
  }, [canProceed, formattedCost, limitInfo, preflightError, preflightLoading]);

  // Debounce hover checks to prevent excessive API calls
  const hoverTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const lastCheckTimeRef = useRef<number>(0);
  const MIN_CHECK_INTERVAL = 5000; // Only check once every 5 seconds max
  
  // Handle hover with debouncing
  const handleMouseEnter = () => {
    if (checkOnHover) {
      const now = Date.now();
      const timeSinceLastCheck = now - lastCheckTimeRef.current;
      
      // If we checked recently, skip (use cache)
      if (timeSinceLastCheck < MIN_CHECK_INTERVAL) {
        return;
      }
      
      // Clear any existing timeout
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
      
      // Debounce the check by 300ms to prevent rapid-fire calls
      hoverTimeoutRef.current = setTimeout(() => {
      triggerCheck(operation);
        lastCheckTimeRef.current = Date.now();
      }, 300);
    }
  };

  // Handle click
  // Allow clicks even when canProceed === false to let users see subscription modal
  // The API will return 429, which triggers the subscription modal via global error handler
  const handleClick = () => {
    if (!isDisabled) {
      // Always allow click - if limits are exceeded, API will return 429 and show modal
      onClick();
    }
  };

  // Determine button color based on state
  const buttonColor = useMemo(() => {
    if (canProceed !== null && !canProceed) {
      return 'error';
    }
    return color;
  }, [canProceed, color]);

  // Determine if we should show loading spinner
  // Only show spinner for external loading (actual operation), not for preflight checks
  const showLoading = externalLoading;

  // Custom label override for loading state
  const displayLabel = useMemo(() => {
    if (externalLoading && buttonProps?.children) {
      return buttonProps.children;
    }
    // Don't show "Checking..." during preflight - keep label stable with cost
    // Preflight loading is handled by spinner in icon position only
    // Note: We don't override label when canProceed === false to keep button clickable
    // The tooltip will show the limit info, and clicking will trigger subscription modal
    return buttonLabel;
  }, [externalLoading, buttonLabel, buttonProps?.children]);

  // Build button with icon
  const button = (
    <Button
      variant={variant}
      size={size}
      color={buttonColor}
      startIcon={
        showLoading ? (
          <CircularProgress size={16} color="inherit" />
        ) : (preflightLoading && checkOnMount) ? (
          <CircularProgress size={16} color="inherit" />
        ) : (canProceed !== null && !canProceed) ? (
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

  // Cleanup timeout on unmount
  React.useEffect(() => {
    return () => {
      if (hoverTimeoutRef.current) {
        clearTimeout(hoverTimeoutRef.current);
      }
    };
  }, []);

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

