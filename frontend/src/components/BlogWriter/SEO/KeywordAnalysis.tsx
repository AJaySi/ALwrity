/**
 * Keyword Analysis Component
 * 
 * Displays comprehensive keyword analysis including keyword types, densities,
 * missing keywords, over-optimization, and distribution analysis.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  GpsFixed,
  Search,
  Warning
} from '@mui/icons-material';

interface KeywordAnalysisProps {
  detailedAnalysis?: {
    keyword_analysis?: {
      primary_keywords: string[];
      long_tail_keywords: string[];
      semantic_keywords: string[];
      keyword_density: Record<string, number>;
      keyword_distribution: Record<string, any>;
      missing_keywords: string[];
      over_optimization: string[];
      recommendations: string[];
    };
  };
}

export const KeywordAnalysis: React.FC<KeywordAnalysisProps> = ({ detailedAnalysis }) => {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <GpsFixed sx={{ color: 'primary.main' }} />
        <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
          Keyword Analysis
        </Typography>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
        {/* Keyword Types Overview */}
        <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
            Keyword Types Found
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(76, 175, 80, 0.1)', borderRadius: 2, border: '1px solid rgba(76, 175, 80, 0.3)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'success.main', mb: 1 }}>
                  Primary Keywords
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {detailedAnalysis?.keyword_analysis?.primary_keywords?.length || 0} found
                </Typography>
                {detailedAnalysis?.keyword_analysis?.primary_keywords?.slice(0, 3).map((keyword: string) => (
                  <Chip key={keyword} label={keyword} size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(33, 150, 243, 0.1)', borderRadius: 2, border: '1px solid rgba(33, 150, 243, 0.3)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'primary.main', mb: 1 }}>
                  Long-tail Keywords
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {detailedAnalysis?.keyword_analysis?.long_tail_keywords?.length || 0} found
                </Typography>
                {detailedAnalysis?.keyword_analysis?.long_tail_keywords?.slice(0, 2).map((keyword: string) => (
                  <Chip key={keyword} label={keyword} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={4}>
              <Box sx={{ p: 2, background: 'rgba(156, 39, 176, 0.1)', borderRadius: 2, border: '1px solid rgba(156, 39, 176, 0.3)' }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: 'secondary.main', mb: 1 }}>
                  Semantic Keywords
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  {detailedAnalysis?.keyword_analysis?.semantic_keywords?.length || 0} found
                </Typography>
                {detailedAnalysis?.keyword_analysis?.semantic_keywords?.slice(0, 2).map((keyword: string) => (
                  <Chip key={keyword} label={keyword} size="small" variant="outlined" color="secondary" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Box>
            </Grid>
          </Grid>
        </Paper>

        {/* Keyword Densities */}
        <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Keyword Densities
            </Typography>
            <Tooltip
              title={
                <Box sx={{ p: 1 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    Keyword Density Analysis
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Shows how frequently each keyword appears in your content as a percentage of total words.
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                    <strong>Optimal Range:</strong> 1-3% for primary keywords
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                    <strong>Too Low (&lt;1%):</strong> Keyword may not be prominent enough
                  </Typography>
                  <Typography variant="caption" sx={{ display: 'block' }}>
                    <strong>Too High (&gt;3%):</strong> Risk of keyword stuffing
                  </Typography>
                </Box>
              }
              arrow
            >
              <IconButton size="small" sx={{ color: 'primary.main' }}>
                <Search />
              </IconButton>
            </Tooltip>
          </Box>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {detailedAnalysis?.keyword_analysis?.keyword_density && Object.keys(detailedAnalysis.keyword_analysis.keyword_density).length > 0 ? (
              Object.entries(detailedAnalysis.keyword_analysis.keyword_density).map(([keyword, density]) => (
                <Box key={keyword} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1, borderRadius: 1, background: 'rgba(0,0,0,0.02)' }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{keyword}</Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                      {density > 3 ? 'Over-optimized' : density < 1 ? 'Under-optimized' : 'Optimal'}
                    </Typography>
                    <Chip 
                      label={`${density.toFixed(1)}%`}
                      color={density > 3 ? 'error' : density < 1 ? 'warning' : 'success'}
                      size="small"
                    />
                  </Box>
                </Box>
              ))
            ) : (
              <Typography variant="body2" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                No keyword density data available. Make sure your research data includes target keywords.
              </Typography>
            )}
          </Box>
        </Paper>
        
        {/* Missing Keywords */}
        {detailedAnalysis?.keyword_analysis?.missing_keywords && detailedAnalysis.keyword_analysis.missing_keywords.length > 0 && (
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'error.main' }}>
                Missing Keywords
              </Typography>
              <Tooltip
                title="Keywords from your research that are not found in the content. Consider adding these to improve SEO."
                arrow
              >
                <IconButton size="small" sx={{ color: 'error.main' }}>
                  <Warning />
                </IconButton>
              </Tooltip>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {detailedAnalysis.keyword_analysis.missing_keywords.map((keyword: string) => (
                <Chip key={keyword} label={keyword} color="error" variant="outlined" />
              ))}
            </Box>
          </Paper>
        )}
        
        {/* Over-Optimized Keywords */}
        {detailedAnalysis?.keyword_analysis?.over_optimization && detailedAnalysis.keyword_analysis.over_optimization.length > 0 && (
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600, color: 'warning.main' }}>
                Over-Optimized Keywords
              </Typography>
              <Tooltip
                title="Keywords that appear too frequently (over 3% density). Consider reducing their usage to avoid keyword stuffing penalties."
                arrow
              >
                <IconButton size="small" sx={{ color: 'warning.main' }}>
                  <Warning />
                </IconButton>
              </Tooltip>
            </Box>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {detailedAnalysis.keyword_analysis.over_optimization.map((keyword: string) => (
                <Chip key={keyword} label={keyword} color="warning" variant="outlined" />
              ))}
            </Box>
          </Paper>
        )}

        {/* Keyword Distribution Analysis */}
        {detailedAnalysis?.keyword_analysis?.keyword_distribution && Object.keys(detailedAnalysis.keyword_analysis.keyword_distribution).length > 0 && (
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Keyword Distribution Analysis
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              {Object.entries(detailedAnalysis.keyword_analysis.keyword_distribution).map(([keyword, data]: [string, any]) => (
                <Box key={keyword} sx={{ p: 2, background: 'rgba(0,0,0,0.02)', borderRadius: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                    "{keyword}"
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        Density: {data.density?.toFixed(1)}%
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        In Headings: {data.in_headings ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" sx={{ color: 'text.secondary' }}>
                        First Occurrence: Character {data.first_occurrence || 'Not found'}
                      </Typography>
                    </Grid>
                  </Grid>
                </Box>
              ))}
            </Box>
          </Paper>
        )}
      </Box>
    </Box>
  );
};
