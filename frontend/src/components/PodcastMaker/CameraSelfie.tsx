import React, { memo, useCallback } from 'react';
import { RobustCamera } from './RobustCamera';

interface CameraSelfieProps {
  onCapture: (imageDataUrl: string) => void;
  onClose: () => void;
  open: boolean;
}

// Memoize to prevent re-renders when parent updates
export const CameraSelfie: React.FC<CameraSelfieProps> = memo(({ onCapture, onClose, open }) => {
  // Memoize callbacks to prevent unnecessary effect triggers in child
  const handleCapture = useCallback((dataUrl: string) => {
    onCapture(dataUrl);
  }, [onCapture]);

  const handleClose = useCallback(() => {
    onClose();
  }, [onClose]);

  return <RobustCamera onCapture={handleCapture} onClose={handleClose} open={open} />;
}, (prevProps, nextProps) => {
  // Custom comparison - only re-render if open state changes
  return prevProps.open === nextProps.open &&
         prevProps.onCapture === nextProps.onCapture &&
         prevProps.onClose === nextProps.onClose;
});
