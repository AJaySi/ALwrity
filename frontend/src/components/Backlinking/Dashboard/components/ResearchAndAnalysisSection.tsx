/**
 * Research and Analysis Section Component
 *
 * Contains keyword research and prospect analysis panels
 */

import React from 'react';
import {
  Box,
  Typography,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { KeywordResearchPanel } from '../../KeywordResearchPanel';
import { ProspectAnalysisPanel } from '../../ProspectAnalysisPanel';

interface ResearchAndAnalysisSectionProps {
  onKeywordSelect?: (keywords: string[]) => void;
  onProspectSelect?: (prospect: any) => void;
  onProspectViewDetails?: (prospect: any) => void;
  onProspectContact?: (prospect: any) => void;
}

export const ResearchAndAnalysisSection: React.FC<ResearchAndAnalysisSectionProps> = ({
  onKeywordSelect,
  onProspectSelect,
  onProspectViewDetails,
  onProspectContact,
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{
          fontWeight: 700,
          color: '#F1F5F9',
          mb: 1,
          display: 'flex',
          alignItems: 'center',
          gap: 1,
        }}>
          <SearchIcon sx={{ color: '#A855F7' }} />
          Research & Analysis Tools
        </Typography>
        <Typography variant="body2" sx={{ color: 'rgba(203, 213, 225, 0.8)' }}>
          AI-powered keyword research and intelligent prospect analysis to discover high-quality backlinking opportunities
        </Typography>
      </Box>

      <Box sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', xl: '1fr 1fr' },
        gap: 3,
      }}>
        <KeywordResearchPanel onKeywordSelect={onKeywordSelect} />

        <ProspectAnalysisPanel
          onProspectSelect={onProspectSelect}
          onViewDetails={onProspectViewDetails}
          onContact={onProspectContact}
        />
      </Box>
    </Box>
  );
};