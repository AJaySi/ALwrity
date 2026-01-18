/**
 * Chart Modal Component
 * Displays charts in a modal overlay for expanded view
 */

import React from 'react';
import { Modal, IconButton } from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { TerminalTypography, TerminalPaper, terminalColors } from '../terminalTheme';

interface ChartModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const ChartModal: React.FC<ChartModalProps> = ({ open, onClose, title, children }) => {
  return (
    <Modal
      open={open}
      onClose={onClose}
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
      }}
    >
      <TerminalPaper
        sx={{
          position: 'relative',
          width: '90%',
          maxWidth: '1200px',
          maxHeight: '90vh',
          overflow: 'auto',
          p: 3,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <TerminalTypography variant="h5" sx={{ color: terminalColors.primary }}>
            {title}
          </TerminalTypography>
          <IconButton onClick={onClose} sx={{ color: terminalColors.primary }}>
            <CloseIcon />
          </IconButton>
        </div>
        {children}
      </TerminalPaper>
    </Modal>
  );
};