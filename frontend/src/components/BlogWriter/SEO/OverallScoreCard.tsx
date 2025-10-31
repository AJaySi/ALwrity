/**
 * OverallScoreCard Component
 *
 * Renders the compact overall SEO score summary with grade chip and
 * category score tiles.
 */

import React from 'react';
import {
  Card,
  CardHeader,
  CardContent,
  Typography,
  Box,
  Tooltip,
  Paper,
  Chip,
  Avatar
} from '@mui/material';

interface MetricTooltip {
  title: string;
  description: string;
  methodology: string;
  score_meaning: string;
  examples: string;
}

interface OverallScoreCardProps {
  overallScore: number;
  overallGrade: string;
  statusLabel: string;
  categoryScores: Record<string, number>;
  getMetricTooltip: (category: string) => MetricTooltip;
  getScoreColor: (score: number) => string;
}

const getGradeMeta = (grade: string) => {
  switch (grade) {
    case 'A':
      return {
        color: '#16a34a',
        background: 'linear-gradient(135deg, rgba(34,197,94,0.12), rgba(22,163,74,0.18))',
        tooltip: 'Grade A: Outstanding SEO health with only minor optimizations needed.'
      };
    case 'B':
      return {
        color: '#0ea5e9',
        background: 'linear-gradient(135deg, rgba(14,165,233,0.12), rgba(2,132,199,0.18))',
        tooltip: 'Grade B: Strong SEO foundation with several opportunities to optimize further.'
      };
    case 'C':
      return {
        color: '#d97706',
        background: 'linear-gradient(135deg, rgba(251,191,36,0.14), rgba(217,119,6,0.2))',
        tooltip: 'Grade C: Moderate SEO performance. Prioritize improvements in weaker categories.'
      };
    case 'D':
      return {
        color: '#ea580c',
        background: 'linear-gradient(135deg, rgba(251,113,133,0.14), rgba(249,115,22,0.2))',
        tooltip: 'Grade D: Significant SEO gaps detected. Address critical issues promptly.'
      };
    default:
      return {
        color: '#475569',
        background: 'linear-gradient(135deg, rgba(148,163,184,0.14), rgba(100,116,139,0.2))',
        tooltip: 'SEO grade unavailable. Review analysis details for more information.'
      };
  }
};

export const OverallScoreCard: React.FC<OverallScoreCardProps> = ({
  overallScore,
  overallGrade,
  statusLabel,
  categoryScores,
  getMetricTooltip,
  getScoreColor
}) => {
  const gradeMeta = getGradeMeta(overallGrade);

  return (
    <Card
      sx={{
        mb: 3,
        background: 'rgba(255,255,255,0.95)',
        border: '1px solid rgba(0,0,0,0.08)',
        boxShadow: '0 8px 24px rgba(15,23,42,0.04)',
        borderRadius: 3
      }}
    >
      <CardHeader
        sx={{
          pb: 0,
          '& .MuiCardHeader-content': {
            overflow: 'hidden'
          }
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            variant="subtitle1"
            sx={{ fontWeight: 700, letterSpacing: 0.2, color: '#0f172a' }}
          >
            Overall SEO Performance Snapshot
          </Typography>
        </Box>
      </CardHeader>

      <CardContent
        sx={{
          pt: 2,
          pb: { xs: 2.5, md: 3 },
          px: { xs: 2, md: 3 }
        }}
      >
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            gap: { xs: 3, md: 4 },
            alignItems: { xs: 'stretch', md: 'flex-start' }
          }}
        >
          <Box
            sx={{
              flexShrink: 0,
              minWidth: { md: 240 },
              display: 'flex',
              flexDirection: 'column',
              alignItems: { xs: 'flex-start', md: 'center' },
              gap: 1.5,
              background: 'linear-gradient(145deg, rgba(241,245,249,0.7), rgba(255,255,255,0.95))',
              borderRadius: 2,
              p: { xs: 1.5, md: 2 }
            }}
          >
            <Box sx={{ textAlign: { xs: 'left', md: 'center' } }}>
              <Typography
                component="span"
                sx={{
                  display: 'inline-flex',
                  alignItems: 'baseline',
                  gap: 1,
                  fontWeight: 800,
                  fontSize: { xs: '2.4rem', md: '2.8rem' },
                  lineHeight: 1,
                  background: 'linear-gradient(120deg, #22c55e, #4ade80)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent'
                }}
              >
                {overallScore}
                <Typography
                  component="span"
                  variant="caption"
                  sx={{ color: '#64748b', fontWeight: 600 }}
                >
                  /100
                </Typography>
              </Typography>
              <Typography variant="caption" sx={{ color: '#64748b', display: 'block', mt: 0.5 }}>
                Overall Score
              </Typography>
            </Box>
            <Tooltip title={gradeMeta.tooltip} arrow placement="top">
              <Chip
                label={statusLabel}
                avatar={
                  <Avatar
                    sx={{
                      bgcolor: '#fff',
                      color: gradeMeta.color,
                      fontWeight: 700
                    }}
                  >
                    {overallGrade}
                  </Avatar>
                }
                sx={{
                  fontWeight: 600,
                  px: 2.2,
                  py: 0.5,
                  letterSpacing: 0.3,
                  color: gradeMeta.color,
                  background: gradeMeta.background
                }}
              />
            </Tooltip>
          </Box>

          <Box sx={{ flex: 1 }}>
            <Box
              sx={{
                display: 'grid',
                gridTemplateColumns: { xs: 'repeat(2, minmax(110px, 1fr))', sm: 'repeat(3, minmax(110px, 1fr))' },
                gap: 1.5
              }}
            >
              {Object.entries(categoryScores).map(([category, score]) => {
                const tooltip = getMetricTooltip(category);
                return (
                  <Tooltip
                    key={category}
                    title={
                      <Box sx={{ p: 1 }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: '#0f172a' }}>
                          {tooltip.title}
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 0.75, color: '#475569' }}>
                          {tooltip.description}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5, color: '#64748b' }}>
                          <strong>Methodology:</strong> {tooltip.methodology}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', mb: 0.5, color: '#64748b' }}>
                          <strong>Score Meaning:</strong> {tooltip.score_meaning}
                        </Typography>
                        <Typography variant="caption" sx={{ display: 'block', color: '#64748b' }}>
                          <strong>Examples:</strong> {tooltip.examples}
                        </Typography>
                      </Box>
                    }
                    arrow
                    placement="top"
                  >
                    <Paper
                      sx={{
                        p: 1.4,
                        textAlign: 'center',
                        borderRadius: 2,
                        backgroundColor: '#ffffff',
                        border: '1px solid #e2e8f0',
                        boxShadow: '0 8px 18px rgba(15,23,42,0.06)',
                        cursor: 'help'
                      }}
                    >
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 800, color: getScoreColor(score), mb: 0.35 }}
                      >
                        {score}
                      </Typography>
                      <Typography
                        variant="caption"
                        sx={{ color: '#64748b', textTransform: 'capitalize', fontWeight: 600 }}
                      >
                        {category.replace('_', ' ')}
                      </Typography>
                    </Paper>
                  </Tooltip>
                );
              })}
            </Box>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

export default OverallScoreCard;
