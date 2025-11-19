import React from 'react';
import { Box, Tooltip } from '@mui/material';
import EditNoteIcon from '@mui/icons-material/EditNote';
import TipsAndUpdatesIcon from '@mui/icons-material/TipsAndUpdates';

interface OutlineHoverActionsProps {
  onEdit: () => void;
  onImprove: () => void;
}

const OutlineHoverActions: React.FC<OutlineHoverActionsProps> = ({
  onEdit,
  onImprove,
}) => {
  return (
    <Box
      className="outline-actions"
      sx={{
        position: 'absolute',
        top: 16,
        right: 16,
        display: 'flex',
        gap: 1,
        opacity: 0,
        pointerEvents: 'none',
        transition: 'opacity 0.2s ease',
      }}
    >
      <Tooltip title="Edit this section">
        <Box
          role="button"
          aria-label="Edit section"
          onClick={(e) => {
            e.stopPropagation();
            onEdit();
          }}
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #7F5AF0 0%, #2CB67D 100%)',
            boxShadow: '0 8px 16px rgba(127,90,240,0.3)',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          <EditNoteIcon />
        </Box>
      </Tooltip>
      <Tooltip title="Improve with AI (2 suggestions)">
        <Box
          role="button"
          aria-label="AI improve section"
          onClick={(e) => {
            e.stopPropagation();
            onImprove();
          }}
          sx={{
            width: 40,
            height: 40,
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #5d3b24 0%, #a36c3b 45%, #f1c27d 100%)',
            boxShadow: '0 8px 16px rgba(93,59,36,0.35)',
            color: 'white',
            cursor: 'pointer',
          }}
        >
          <TipsAndUpdatesIcon />
        </Box>
      </Tooltip>
    </Box>
  );
};

export default OutlineHoverActions;

