/**
 * ResearchQueriesSection Component
 * 
 * Accordion section for managing research queries (add, edit, delete, select).
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  Button,
  Divider,
  Chip,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Search as SearchIcon,
} from '@mui/icons-material';
import {
  ResearchQuery,
} from '../../../types/intent.types';
import { QueryEditor } from './QueryEditor';

interface ResearchQueriesSectionProps {
  queries: ResearchQuery[];
  selectedQueries: Set<number>;
  onQueriesChange: (queries: ResearchQuery[]) => void;
  onSelectionChange: (selected: Set<number>) => void;
}

export const ResearchQueriesSection: React.FC<ResearchQueriesSectionProps> = ({
  queries,
  selectedQueries,
  onQueriesChange,
  onSelectionChange,
}) => {
  const [expanded, setExpanded] = useState(true);

  const handleQueryToggle = (index: number) => {
    const newSelected = new Set(selectedQueries);
    if (newSelected.has(index)) {
      newSelected.delete(index);
    } else {
      newSelected.add(index);
    }
    onSelectionChange(newSelected);
  };

  const handleQueryEdit = (index: number, field: keyof ResearchQuery, value: any) => {
    const updated = [...queries];
    updated[index] = { ...updated[index], [field]: value };
    onQueriesChange(updated);
  };

  const handleDeleteQuery = (index: number) => {
    const updated = queries.filter((_, idx) => idx !== index);
    onQueriesChange(updated);
    
    const newSelected = new Set(selectedQueries);
    newSelected.delete(index);
    const adjusted = new Set<number>();
    newSelected.forEach(idx => {
      if (idx > index) {
        adjusted.add(idx - 1);
      } else if (idx < index) {
        adjusted.add(idx);
      }
    });
    onSelectionChange(adjusted);
  };

  const handleAddQuery = () => {
    const newQuery: ResearchQuery = {
      query: '',
      purpose: 'key_statistics',
      provider: 'exa',
      priority: 3,
      expected_results: '',
    };
    onQueriesChange([...queries, newQuery]);
    const newSelected = new Set(selectedQueries);
    newSelected.add(queries.length);
    onSelectionChange(newSelected);
  };

  return (
    <Accordion
      expanded={expanded}
      onChange={() => setExpanded(!expanded)}
      sx={{
        mb: 2,
        backgroundColor: '#ffffff',
        border: '1px solid #e5e7eb',
        '&:before': { display: 'none' },
        boxShadow: 'none',
      }}
    >
      <AccordionSummary
        expandIcon={<ExpandMoreIcon sx={{ color: '#666' }} />}
        sx={{
          backgroundColor: '#f9fafb',
          '&:hover': { backgroundColor: '#f3f4f6' },
        }}
      >
        <Box display="flex" alignItems="center" gap={1} flex={1}>
          <SearchIcon sx={{ color: '#666', fontSize: 20 }} />
          <Typography variant="subtitle2" fontWeight={600} color="#333">
            Research Queries ({queries.length})
          </Typography>
          <Chip
            size="small"
            label={`${selectedQueries.size} selected`}
            sx={{
              ml: 1,
              backgroundColor: '#e0f2fe',
              color: '#0369a1',
              fontSize: '0.7rem',
              height: 20,
              fontWeight: 500,
            }}
          />
        </Box>
      </AccordionSummary>
      <AccordionDetails sx={{ p: 0, backgroundColor: '#ffffff' }}>
        <List dense sx={{ backgroundColor: '#fafafa' }}>
          {queries.map((query, idx) => (
            <React.Fragment key={idx}>
              <QueryEditor
                query={query}
                index={idx}
                isSelected={selectedQueries.has(idx)}
                onToggle={() => handleQueryToggle(idx)}
                onEdit={(field, value) => handleQueryEdit(idx, field, value)}
                onDelete={() => handleDeleteQuery(idx)}
              />
              {idx < queries.length - 1 && <Divider />}
            </React.Fragment>
          ))}
          <Box sx={{ p: 1 }}>
            <Button
              fullWidth
              variant="outlined"
              size="small"
              onClick={handleAddQuery}
              sx={{
                borderStyle: 'dashed',
                borderColor: '#d1d5db',
                color: '#666',
                '&:hover': {
                  borderColor: '#0ea5e9',
                  backgroundColor: '#f0f9ff',
                },
              }}
            >
              + Add Query
            </Button>
          </Box>
        </List>
      </AccordionDetails>
    </Accordion>
  );
};
