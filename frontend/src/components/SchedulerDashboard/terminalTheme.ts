/**
 * Terminal Theme Styling
 * Shared terminal-themed styles for scheduler dashboard components
 */

import { styled } from '@mui/material/styles';
import { Box, Paper, Card, CardContent, Typography, Chip, TableCell, TableRow, Alert, Accordion } from '@mui/material';

export const TerminalPaper = styled(Paper)({
  backgroundColor: '#0a0a0a',
  border: '1px solid #00ff00',
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  padding: 16,
  minHeight: '200px', // Ensure minimum height for visibility
  '& *': {
    fontFamily: 'inherit',
    color: 'inherit', // Ensure all text inherits the green color
  }
});

export const TerminalCard = styled(Card)({
  backgroundColor: '#0a0a0a',
  border: '1px solid #00ff00',
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  transition: 'all 0.2s',
  minHeight: '120px', // Ensure cards have minimum height
  '&:hover': {
    borderColor: '#00ff88',
    boxShadow: '0 0 15px rgba(0, 255, 0, 0.3)',
    transform: 'translateY(-2px)',
  },
  '& *': {
    fontFamily: 'inherit',
    color: 'inherit', // Ensure all text inherits the green color
  }
});

export const TerminalCardContent = styled(CardContent)({
  color: '#00ff00',
  '&:last-child': {
    paddingBottom: 16,
  }
});

export const TerminalTypography = styled(Typography)<{ component?: React.ElementType }>(({ theme }) => ({
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
}));

export const TerminalChip = styled(Chip)({
  backgroundColor: '#1a1a1a',
  color: '#00ff00',
  border: '1px solid #00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '4px 8px',
  },
  '& .MuiChip-icon': {
    color: '#00ff00',
  }
});

export const TerminalChipSuccess = styled(Chip)({
  backgroundColor: '#0a2a0a',
  color: '#00ff00',
  border: '1px solid #00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '4px 8px',
  },
  '& .MuiChip-icon': {
    color: '#00ff00',
  }
});

export const TerminalChipError = styled(Chip)({
  backgroundColor: '#2a0a0a',
  color: '#ff4444',
  border: '1px solid #ff4444',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '4px 8px',
  },
  '& .MuiChip-icon': {
    color: '#ff4444',
  }
});

export const TerminalChipWarning = styled(Chip)({
  backgroundColor: '#2a2a0a',
  color: '#ffd700',
  border: '1px solid #ffd700',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  fontSize: '0.75rem',
  '& .MuiChip-label': {
    padding: '4px 8px',
  },
  '& .MuiChip-icon': {
    color: '#ffd700',
  }
});

export const TerminalTableCell = styled(TableCell)({
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  borderColor: '#004400',
  fontSize: '0.875rem',
});

export const TerminalTableRow = styled(TableRow)({
  '&:hover': {
    backgroundColor: 'rgba(0, 255, 0, 0.05)',
  },
  '&:nth-of-type(even)': {
    backgroundColor: 'rgba(0, 255, 0, 0.02)',
  }
});

export const TerminalAlert = styled(Alert)({
  backgroundColor: '#1a1a1a',
  color: '#ff4444',
  border: '1px solid #ff4444',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  '& .MuiAlert-icon': {
    color: '#ff4444',
  },
  '&.MuiAlert-standardSuccess': {
    color: '#00ff00',
    borderColor: '#00ff00',
    '& .MuiAlert-icon': {
      color: '#00ff00',
    }
  },
  '&.MuiAlert-standardWarning': {
    color: '#ffd700',
    borderColor: '#ffd700',
    '& .MuiAlert-icon': {
      color: '#ffd700',
    }
  },
  '&.MuiAlert-standardInfo': {
    color: '#00ffff',
    borderColor: '#00ffff',
    '& .MuiAlert-icon': {
      color: '#00ffff',
    }
  }
});

export const TerminalAccordion = styled(Accordion)({
  backgroundColor: '#1a1a1a',
  border: '1px solid #00ff00',
  color: '#00ff00',
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  '&:before': {
    display: 'none',
  },
  '&.Mui-expanded': {
    margin: 0,
  }
});

export const TerminalBox = styled(Box)({
  fontFamily: '"Courier New", "Monaco", "Consolas", "Fira Code", monospace',
  color: '#00ff00',
});

// Color constants
export const terminalColors = {
  primary: '#00ff00',
  secondary: '#00ff88',
  error: '#ff4444',
  warning: '#ffd700',
  info: '#00ffff',
  success: '#00ff00',
  background: '#0a0a0a',
  backgroundLight: '#1a1a1a',
  backgroundHover: 'rgba(0, 255, 0, 0.05)',
  backgroundSecondary: 'rgba(0, 255, 0, 0.05)',
  text: '#00ff00',
  textSecondary: '#00ff88',
  border: '#00ff00',
};

