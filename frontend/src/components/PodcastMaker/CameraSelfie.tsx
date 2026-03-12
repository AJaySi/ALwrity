import React from 'react';
import { RobustCamera } from './RobustCamera';

interface CameraSelfieProps {
  onCapture: (imageDataUrl: string) => void;
  onClose: () => void;
  open: boolean;
}

export const CameraSelfie: React.FC<CameraSelfieProps> = ({ onCapture, onClose, open }) => {
  return <RobustCamera onCapture={onCapture} onClose={onClose} open={open} />;
};
