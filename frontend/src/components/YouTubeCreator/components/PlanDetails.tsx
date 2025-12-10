/**
 * Plan Details Component
 */

import React from 'react';
import { Paper, Typography, Stack, Box, Grid, Chip } from '@mui/material';
import { VideoPlan } from '../../../services/youtubeApi';
import { YT_BORDER, YT_TEXT } from '../constants';

interface PlanDetailsProps {
  plan: VideoPlan;
}

export const PlanDetails: React.FC<PlanDetailsProps> = React.memo(({ plan }) => {
  return (
    <Paper
      elevation={0}
      sx={{
        mb: 3,
        p: 2.5,
        border: `1px solid ${YT_BORDER}`,
        backgroundColor: '#fff',
        borderRadius: 2,
      }}
    >
      <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 1, color: YT_TEXT }}>
        Plan Details
      </Typography>
      <Stack spacing={1.25}>
        {plan.video_summary && (
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
              Summary
            </Typography>
            <Typography variant="body2" color="text.secondary">
              {plan.video_summary}
            </Typography>
          </Box>
        )}
        <Grid container spacing={2}>
          {plan.target_audience && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
                Target Audience
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {plan.target_audience}
              </Typography>
            </Grid>
          )}
          {plan.video_goal && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
                Goal
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {plan.video_goal}
              </Typography>
            </Grid>
          )}
        </Grid>
        <Grid container spacing={2}>
          {plan.key_message && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
                Key Message
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {plan.key_message}
              </Typography>
            </Grid>
          )}
          {plan.call_to_action && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
                Call to Action
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {plan.call_to_action}
              </Typography>
            </Grid>
          )}
        </Grid>
        <Grid container spacing={2}>
          {plan.hook_strategy && (
            <Grid item xs={12} md={6}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
                Hook Strategy
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {plan.hook_strategy}
              </Typography>
            </Grid>
          )}
          <Grid item xs={12} md={6}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT }}>
              Style & Tone
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Visual Style: {plan.visual_style || '—'} | Tone: {plan.tone || '—'}
            </Typography>
          </Grid>
        </Grid>

        {plan.seo_keywords && plan.seo_keywords.length > 0 && (
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT, mb: 0.5 }}>
              SEO Keywords
            </Typography>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              {plan.seo_keywords.map((kw, idx) => (
                <Chip key={`${kw}-${idx}`} label={kw} size="small" />
              ))}
            </Stack>
          </Box>
        )}

        {plan.content_outline && plan.content_outline.length > 0 && (
          <Box>
            <Typography variant="body2" sx={{ fontWeight: 600, color: YT_TEXT, mb: 0.5 }}>
              Content Outline
            </Typography>
            <Stack spacing={0.75}>
              {plan.content_outline.map((item, idx) => (
                <Typography key={idx} variant="body2" color="text.secondary">
                  • {item.section || `Section ${idx + 1}`} — {item.description || 'Description missing'} ({item.duration_estimate || 0}s)
                </Typography>
              ))}
            </Stack>
          </Box>
        )}
      </Stack>
    </Paper>
  );
});

PlanDetails.displayName = 'PlanDetails';

