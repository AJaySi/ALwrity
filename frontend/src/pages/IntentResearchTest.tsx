/**
 * Intent Research Test Page
 * 
 * A test page to demonstrate the new intent-driven research system.
 */

import React from 'react';
import { Box, Container, Typography, Paper, Divider } from '@mui/material';
import { IntentResearchWizard } from '../components/Research/IntentResearchWizard';
import { IntentDrivenResearchResponse } from '../components/Research/types/intent.types';

const IntentResearchTest: React.FC = () => {
  const handleComplete = (result: IntentDrivenResearchResponse) => {
    console.log('[IntentResearchTest] Research complete:', result);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: 'linear-gradient(180deg, #f5f7fa 0%, #e4e9f2 100%)',
        py: 4,
      }}
    >
      <Container maxWidth="lg">
        {/* Header */}
        <Paper
          elevation={0}
          sx={{
            p: 4,
            mb: 4,
            borderRadius: 3,
            textAlign: 'center',
          }}
        >
          <Typography
            variant="h3"
            fontWeight={700}
            sx={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              color: 'transparent',
              mb: 2,
            }}
          >
            🧠 Intent-Driven Research
          </Typography>
          <Typography variant="h6" color="text.secondary" mb={2}>
            AI understands what you need, not just what you type
          </Typography>
          <Typography variant="body1" color="text.secondary" maxWidth={600} mx="auto">
            Traditional research gives you links to sift through. Intent-driven research
            gives you exactly what you need: statistics with citations, expert quotes,
            case studies, trends, and more — all organized by what you're trying to accomplish.
          </Typography>
        </Paper>

        {/* Features */}
        <Paper elevation={0} sx={{ p: 3, mb: 4, borderRadius: 3 }}>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            How it works:
          </Typography>
          <Box display="flex" gap={3} flexWrap="wrap" justifyContent="center">
            {[
              { icon: '🎯', title: 'Intent Analysis', desc: 'AI infers what you really want' },
              { icon: '🔍', title: 'Targeted Queries', desc: 'Multiple queries for each need' },
              { icon: '📊', title: 'Smart Extraction', desc: 'Pulls stats, quotes, case studies' },
              { icon: '✨', title: 'Organized Results', desc: 'Deliverables, not just links' },
            ].map((item, idx) => (
              <Box key={idx} textAlign="center" minWidth={150}>
                <Typography variant="h3">{item.icon}</Typography>
                <Typography variant="subtitle2" fontWeight={600}>
                  {item.title}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {item.desc}
                </Typography>
              </Box>
            ))}
          </Box>
        </Paper>

        <Divider sx={{ my: 4 }} />

        {/* Intent Research Wizard */}
        <IntentResearchWizard
          onComplete={handleComplete}
          showQuickMode={true}
        />
      </Container>
    </Box>
  );
};

export default IntentResearchTest;
