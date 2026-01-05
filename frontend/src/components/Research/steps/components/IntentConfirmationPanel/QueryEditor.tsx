/**
 * QueryEditor Component
 * 
 * Individual query editor with provider, purpose, priority, and expected results.
 */

import React from 'react';
import {
  Box,
  TextField,
  FormControl,
  Select,
  MenuItem,
  Checkbox,
  IconButton,
  ListItem,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  Delete as DeleteIcon,
} from '@mui/icons-material';
import {
  ResearchQuery,
  ExpectedDeliverable,
  DELIVERABLE_DISPLAY,
} from '../../../types/intent.types';

interface QueryEditorProps {
  query: ResearchQuery;
  index: number;
  isSelected: boolean;
  onToggle: () => void;
  onEdit: (field: keyof ResearchQuery, value: any) => void;
  onDelete: () => void;
}

export const QueryEditor: React.FC<QueryEditorProps> = ({
  query,
  index,
  isSelected,
  onToggle,
  onEdit,
  onDelete,
}) => {
  return (
    <ListItem
      sx={{
        backgroundColor: isSelected ? '#e0f2fe' : '#ffffff',
        borderLeft: isSelected ? '3px solid #0ea5e9' : '3px solid transparent',
        '&:hover': { backgroundColor: isSelected ? '#bae6fd' : '#f9fafb' },
        py: 1.5,
      }}
    >
      <Checkbox
        checked={isSelected}
        onChange={onToggle}
        size="small"
        sx={{ mr: 1 }}
      />
      <Box flex={1}>
        <TextField
          fullWidth
          size="small"
          value={query.query}
          onChange={(e) => onEdit('query', e.target.value)}
          placeholder="Enter research query"
          sx={{
            mb: 1,
            backgroundColor: '#ffffff',
            '& .MuiOutlinedInput-root': {
              '&:hover fieldset': { borderColor: '#0ea5e9' },
              '&.Mui-focused fieldset': { borderColor: '#0ea5e9' },
            },
          }}
        />
        <Box display="flex" gap={1} flexWrap="wrap">
          <FormControl size="small" sx={{ minWidth: 100 }}>
            <Select
              value={query.provider}
              onChange={(e) => onEdit('provider', e.target.value)}
              sx={{
                backgroundColor: '#ffffff',
                fontSize: '0.75rem',
              }}
            >
              <MenuItem value="exa">Exa</MenuItem>
              <MenuItem value="tavily">Tavily</MenuItem>
              <MenuItem value="google">Google</MenuItem>
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 140 }}>
            <Select
              value={query.purpose}
              onChange={(e) => onEdit('purpose', e.target.value)}
              sx={{
                backgroundColor: '#ffffff',
                fontSize: '0.75rem',
              }}
            >
              {Object.entries(DELIVERABLE_DISPLAY).map(([key, label]) => (
                <MenuItem key={key} value={key}>{label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            size="small"
            type="number"
            value={query.priority}
            onChange={(e) => onEdit('priority', parseInt(e.target.value) || 1)}
            inputProps={{ min: 1, max: 5 }}
            sx={{
              width: 90,
              backgroundColor: '#ffffff',
              fontSize: '0.75rem',
            }}
            label="Priority"
          />
        </Box>
        <TextField
          fullWidth
          size="small"
          value={query.expected_results}
          onChange={(e) => onEdit('expected_results', e.target.value)}
          placeholder="What we expect to find"
          sx={{
            mt: 1,
            backgroundColor: '#ffffff',
            fontSize: '0.75rem',
            '& .MuiOutlinedInput-root': {
              '&:hover fieldset': { borderColor: '#0ea5e9' },
            },
          }}
        />
      </Box>
      <ListItemSecondaryAction>
        <IconButton
          edge="end"
          size="small"
          onClick={onDelete}
          sx={{
            color: '#dc2626',
            '&:hover': { backgroundColor: '#fee2e2' },
          }}
        >
          <DeleteIcon fontSize="small" />
        </IconButton>
      </ListItemSecondaryAction>
    </ListItem>
  );
};
