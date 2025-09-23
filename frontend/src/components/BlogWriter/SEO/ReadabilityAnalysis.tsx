/**
 * Readability Analysis Component
 * 
 * Displays comprehensive readability analysis including readability metrics,
 * content statistics, sentence/paragraph analysis, and target audience information.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  MenuBook
} from '@mui/icons-material';

interface ReadabilityAnalysisProps {
  detailedAnalysis?: {
    readability_analysis?: {
      metrics: Record<string, number>;
      avg_sentence_length: number;
      avg_paragraph_length: number;
      readability_score: number;
      target_audience: string;
      recommendations: string[];
    };
    content_quality?: {
      word_count: number;
      unique_words: number;
      vocabulary_diversity: number;
      transition_words_used: number;
      content_depth_score: number;
      flow_score: number;
      recommendations: string[];
    };
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
  };
  visualizationData?: {
    content_stats: {
      word_count: number;
      sections: number;
      paragraphs: number;
    };
  };
}

export const ReadabilityAnalysis: React.FC<ReadabilityAnalysisProps> = ({ 
  detailedAnalysis, 
  visualizationData 
}) => {
  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
        <MenuBook sx={{ color: 'primary.main' }} />
        <Typography variant="h6" component="h3" sx={{ fontWeight: 600 }}>
          Readability Analysis
        </Typography>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                Readability Metrics
              </Typography>
              <Tooltip
                title={
                  <Box sx={{ p: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                      Readability Analysis
                    </Typography>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      Measures how easy your content is to read and understand.
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                      <strong>Flesch Reading Ease:</strong> 90-100 (Very Easy), 80-89 (Easy), 70-79 (Fairly Easy), 60-69 (Standard)
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', mb: 1 }}>
                      <strong>Average Sentence Length:</strong> 15-20 words is optimal
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      <strong>Average Syllables per Word:</strong> 1.5-1.7 is ideal
                    </Typography>
                  </Box>
                }
                arrow
              >
                <IconButton size="small" sx={{ color: 'primary.main' }}>
                  <MenuBook />
                </IconButton>
              </Tooltip>
            </Box>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {detailedAnalysis?.readability_analysis?.metrics && Object.keys(detailedAnalysis.readability_analysis.metrics).length > 0 ? (
                Object.entries(detailedAnalysis.readability_analysis.metrics).map(([metric, value]) => {
                  const getReadabilityTooltip = (metric: string, value: number) => {
                    const tooltips = {
                      flesch_reading_ease: {
                        description: "Measures how easy text is to read (0-100 scale)",
                        interpretation: value >= 80 ? "Very Easy" : value >= 60 ? "Standard" : "Difficult"
                      },
                      flesch_kincaid_grade: {
                        description: "U.S. grade level needed to understand the text",
                        interpretation: value <= 8 ? "Easy" : value <= 12 ? "Moderate" : "Difficult"
                      },
                      gunning_fog: {
                        description: "Years of formal education needed to understand the text",
                        interpretation: value <= 12 ? "Easy" : value <= 16 ? "Moderate" : "Difficult"
                      },
                      smog_index: {
                        description: "Simple Measure of Gobbledygook - readability formula",
                        interpretation: value <= 8 ? "Easy" : value <= 12 ? "Moderate" : "Difficult"
                      },
                      automated_readability: {
                        description: "Automated Readability Index based on character count",
                        interpretation: value <= 8 ? "Easy" : value <= 12 ? "Moderate" : "Difficult"
                      },
                      coleman_liau: {
                        description: "Readability test based on average sentence length and characters per word",
                        interpretation: value <= 8 ? "Easy" : value <= 12 ? "Moderate" : "Difficult"
                      }
                    };
                    return tooltips[metric as keyof typeof tooltips] || { description: "Readability metric", interpretation: "N/A" };
                  };
                  
                  const tooltip = getReadabilityTooltip(metric, value);
                  return (
                    <Tooltip
                      key={metric}
                      title={
                        <Box sx={{ p: 1 }}>
                          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
                            {metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </Typography>
                          <Typography variant="body2" sx={{ mb: 1 }}>
                            {tooltip.description}
                          </Typography>
                          <Typography variant="caption">
                            <strong>Interpretation:</strong> {tooltip.interpretation}
                          </Typography>
                        </Box>
                      }
                      arrow
                    >
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1, borderRadius: 1, background: 'rgba(0,0,0,0.02)', cursor: 'help' }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {metric.replace('_', ' ')}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {value.toFixed(1)}
                        </Typography>
                      </Box>
                    </Tooltip>
                  );
                })
              ) : (
                <Typography variant="body2" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                  No readability metrics available. This may indicate an issue with the content analysis.
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Content Statistics
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Word Count</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.word_count || visualizationData?.content_stats.word_count}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Sections</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_sections || visualizationData?.content_stats.sections}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Paragraphs</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_paragraphs || visualizationData?.content_stats.paragraphs}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Sentences</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_structure?.total_sentences || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Unique Words</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.unique_words || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Vocabulary Diversity</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.vocabulary_diversity ? 
                    (detailedAnalysis.content_quality.vocabulary_diversity * 100).toFixed(1) + '%' : 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Additional Readability Metrics */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Sentence & Paragraph Analysis
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Avg Sentence Length</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.readability_analysis?.avg_sentence_length?.toFixed(1) || 'N/A'} words
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Avg Paragraph Length</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.readability_analysis?.avg_paragraph_length?.toFixed(1) || 'N/A'} words
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Transition Words</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.transition_words_used || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, background: 'rgba(255,255,255,0.8)', border: '1px solid rgba(0,0,0,0.1)' }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
              Target Audience
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Reading Level</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.readability_analysis?.target_audience || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Content Depth Score</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.content_depth_score || 'N/A'}
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">Flow Score</Typography>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {detailedAnalysis?.content_quality?.flow_score || 'N/A'}
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
