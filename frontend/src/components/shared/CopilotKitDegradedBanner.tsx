import React, { useState } from 'react';
import { Alert, AlertTitle, IconButton, Collapse } from '@mui/material';
import { Close as CloseIcon, Warning as WarningIcon } from '@mui/icons-material';
import { useCopilotKitHealth } from '../../hooks/useCopilotKitHealth';

interface CopilotKitDegradedBannerProps {
  /**
   * Position of the banner
   * @default 'top'
   */
  position?: 'top' | 'bottom';
  /**
   * Whether the banner is dismissible
   * @default true
   */
  dismissible?: boolean;
}

/**
 * Banner component that displays when CopilotKit is unavailable
 * Non-intrusive notification that chat is unavailable but app continues to work
 */
export const CopilotKitDegradedBanner: React.FC<CopilotKitDegradedBannerProps> = ({
  position = 'top',
  dismissible = true,
}) => {
  const { isAvailable, errorMessage, isChecking } = useCopilotKitHealth();
  const [dismissed, setDismissed] = useState(false);

  // Don't show if CopilotKit is available, checking, or dismissed
  if (isAvailable || isChecking || dismissed) {
    return null;
  }

  const handleDismiss = () => {
    setDismissed(true);
  };

  return (
    <Collapse in={!dismissed}>
      <Alert
        severity="warning"
        icon={<WarningIcon />}
        action={
          dismissible ? (
            <IconButton
              aria-label="close"
              color="inherit"
              size="small"
              onClick={handleDismiss}
            >
              <CloseIcon fontSize="inherit" />
            </IconButton>
          ) : null
        }
        sx={{
          position: 'fixed',
          [position]: 0,
          left: 0,
          right: 0,
          zIndex: 1300, // Above most content but below modals
          borderRadius: 0, // Full width banner
          boxShadow: 2,
        }}
      >
        <AlertTitle>Chat Unavailable</AlertTitle>
        {errorMessage || 'CopilotKit service is currently unavailable. You can still use all features with manual controls.'}
      </Alert>
    </Collapse>
  );
};

export default CopilotKitDegradedBanner;

