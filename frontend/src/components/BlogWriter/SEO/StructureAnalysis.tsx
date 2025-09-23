/**
 * Structure Analysis Component
 * 
 * Displays comprehensive content structure analysis including structure overview,
 * content elements detection, and heading structure analysis.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip
} from '@mui/material';
import { 
  BarChart
} from '@mui/icons-material';

interface StructureAnalysisProps {
  detailedAnalysis?: {
    content_structure?: {
      total_sections: number;
      total_paragraphs: number;
      total_sentences: number;
      has_introduction: boolean;
      has_conclusion: boolean;
      has_call_to_action: boolean;
      structure_score: number;
      recommendations: string[];
    };
    heading_structure?: {
      h1_count: number;
      h2_count: number;
      h3_count: number;
      h1_headings: string[];
      h2_headings: string[];
      h3_headings: string[];
      heading_hierarchy_score: number;
      recommendations: string[];
    };
  };
}

export const StructureAnalysis: React.FC<StructureAnalysisProps> = ({ detailedAnalysis }) => {
  // Debug logging
  console.log('🏗️ StructureAnalysis received data:', detailedAnalysis);
  console.log('📊 Content Structure:', detailedAnalysis?.content_structure);
  console.log('📋 Heading Structure:', detailedAnalysis?.heading_structure);
  
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <BarChart sx={{ color: 'primary.main' }} />
        <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
          Content Structure Analysis
        </Typography>
      </Box>
      <Grid container spacing={3}>
        {/* Content Structure Overview */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Structure Overview
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Total Sections</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_sections || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Total Paragraphs</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_paragraphs || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Total Sentences</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_sentences || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Structure Score</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.structure_score || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Content Elements */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Content Elements
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Has Introduction</Typography>
                <Chip 
                  label={detailedAnalysis?.content_structure?.has_introduction ? 'Yes' : 'No'}
                  color={detailedAnalysis?.content_structure?.has_introduction ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Has Conclusion</Typography>
                <Chip 
                  label={detailedAnalysis?.content_structure?.has_conclusion ? 'Yes' : 'No'}
                  color={detailedAnalysis?.content_structure?.has_conclusion ? 'success' : 'error'}
                  size="small"
                />
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Has Call to Action</Typography>
                <Chip 
                  label={detailedAnalysis?.content_structure?.has_call_to_action ? 'Yes' : 'No'}
                  color={detailedAnalysis?.content_structure?.has_call_to_action ? 'success' : 'error'}
                  size="small"
                />
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Heading Structure */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Heading Structure Analysis
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, background: 'rgba(76, 175, 80, 0.1)', borderRadius: 2, border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
                    H1 Headings ({detailedAnalysis?.heading_structure?.h1_count || 0})
                  </Typography>
                  {detailedAnalysis?.heading_structure?.h1_headings?.map((heading: string, index: number) => (
                    <Typography key={index} variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                      • {heading}
                    </Typography>
                  ))}
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, background: 'rgba(33, 150, 243, 0.1)', borderRadius: 2, border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 1 }}>
                    H2 Headings ({detailedAnalysis?.heading_structure?.h2_count || 0})
                  </Typography>
                  {detailedAnalysis?.heading_structure?.h2_headings?.slice(0, 3).map((heading: string, index: number) => (
                    <Typography key={index} variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                      • {heading}
                    </Typography>
                  ))}
                  {detailedAnalysis?.heading_structure?.h2_headings && detailedAnalysis.heading_structure.h2_headings.length > 3 && (
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      ... and {detailedAnalysis.heading_structure.h2_headings.length - 3} more
                    </Typography>
                  )}
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box sx={{ p: 2, background: 'rgba(156, 39, 176, 0.1)', borderRadius: 2, border: '1px solid rgba(156, 39, 176, 0.3)' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'secondary.main', mb: 1 }}>
                    H3 Headings ({detailedAnalysis?.heading_structure?.h3_count || 0})
                  </Typography>
                  {detailedAnalysis?.heading_structure?.h3_headings?.slice(0, 3).map((heading: string, index: number) => (
                    <Typography key={index} variant="caption" sx={{ display: 'block', mb: 0.5 }}>
                      • {heading}
                    </Typography>
                  ))}
                  {detailedAnalysis?.heading_structure?.h3_headings && detailedAnalysis.heading_structure.h3_headings.length > 3 && (
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      ... and {detailedAnalysis.heading_structure.h3_headings.length - 3} more
                    </Typography>
                  )}
                </Box>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2, p: 2, background: 'rgba(0,0,0,0.02)', borderRadius: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                Heading Hierarchy Score: {detailedAnalysis?.heading_structure?.heading_hierarchy_score || 'N/A'}
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
