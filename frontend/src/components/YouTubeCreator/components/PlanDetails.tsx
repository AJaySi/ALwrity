/**
 * Plan Details Component
 * 
 * Displays comprehensive video plan information in a professional card-based layout.
 * Includes avatar display with enlarge modal, summary, and all plan details.
 */

import React from 'react';
import { Paper, Typography, Stack, Box, Grid } from '@mui/material';
import { VideoPlan } from '../../../services/youtubeApi';
import { YT_BORDER } from '../constants';
import { useAvatarBlobUrl } from '../hooks/useAvatarBlobUrl';
import { PlanDetailsCard } from './PlanDetailsCard';
import { AvatarCard } from './AvatarCard';
import { ContentOutlineCard } from './ContentOutlineCard';
import { SEOKeywordsCard } from './SEOKeywordsCard';

interface PlanDetailsProps {
  plan: VideoPlan;
  onAvatarRegenerate?: () => void;
  regeneratingAvatar?: boolean;
}

// Typography styles constants
const SECTION_TITLE_STYLES = {
  fontWeight: 700,
  color: '#1a1a1a',
  mb: 1.5,
  fontSize: '0.875rem',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.05em',
};

const CONTENT_TEXT_STYLES = {
  color: '#374151',
  lineHeight: 1.6,
  fontSize: '0.9375rem',
  fontWeight: 400,
};

const SUMMARY_TEXT_STYLES = {
  ...CONTENT_TEXT_STYLES,
  lineHeight: 1.7,
};

/**
 * PlanDetails Component
 * 
 * Displays video plan information in a professional, card-based layout.
 * Features:
 * - Avatar display with enlarge modal
 * - Summary and plan details in organized cards
 * - SEO keywords and content outline
 */
export const PlanDetails: React.FC<PlanDetailsProps> = React.memo(({ plan, onAvatarRegenerate, regeneratingAvatar = false }) => {
  const avatarUrl = plan.auto_generated_avatar_url;
  const { avatarBlobUrl, avatarLoading } = useAvatarBlobUrl(avatarUrl);

  const handleAvatarError = React.useCallback(() => {
    console.warn('[PlanDetails] Avatar image failed to load');
  }, []);

  return (
    <Paper
      elevation={0}
      sx={{
        mb: 3,
        p: 3,
        border: `1px solid ${YT_BORDER}`,
        backgroundColor: '#fff',
        borderRadius: 2,
      }}
    >
      <Typography
        variant="h6"
        sx={{
          fontWeight: 700,
          mb: 3,
          color: '#1a1a1a',
          fontSize: '1.125rem',
          letterSpacing: '-0.01em',
        }}
      >
        Plan Details
      </Typography>

      <Stack spacing={3}>
        {/* Avatar and Summary Section - Side by Side */}
        {(avatarUrl || plan.video_summary) && (
          <Grid container spacing={3}>
            {avatarUrl && (
              <Grid item xs={12} sm={4} md={3}>
                <AvatarCard
                  avatarUrl={avatarUrl}
                  avatarBlobUrl={avatarBlobUrl}
                  avatarLoading={avatarLoading}
                  avatarReused={plan.avatar_reused}
                  avatarPrompt={plan.avatar_prompt}
                  onImageError={handleAvatarError}
                  onRegenerate={onAvatarRegenerate}
                  regenerating={regeneratingAvatar}
                />
              </Grid>
            )}
            {plan.video_summary && (
              <Grid item xs={12} sm={avatarUrl ? 8 : 12} md={avatarUrl ? 9 : 12}>
                <PlanDetailsCard title="Summary">
                  <Typography variant="body1" sx={SUMMARY_TEXT_STYLES}>
                    {plan.video_summary}
                  </Typography>
                </PlanDetailsCard>
              </Grid>
            )}
          </Grid>
        )}

        {/* Target Audience and Goal Cards */}
        <Grid container spacing={3}>
          {plan.target_audience && (
            <Grid item xs={12} md={6}>
              <PlanDetailsCard title="Target Audience" fullHeight>
                <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                  {plan.target_audience}
                </Typography>
              </PlanDetailsCard>
            </Grid>
          )}
          {plan.video_goal && (
            <Grid item xs={12} md={6}>
              <PlanDetailsCard title="Goal" fullHeight>
                <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                  {plan.video_goal}
                </Typography>
              </PlanDetailsCard>
            </Grid>
          )}
        </Grid>

        {/* Key Message and Call to Action Cards */}
        <Grid container spacing={3}>
          {plan.key_message && (
            <Grid item xs={12} md={6}>
              <PlanDetailsCard title="Key Message" fullHeight>
                <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                  {plan.key_message}
                </Typography>
              </PlanDetailsCard>
            </Grid>
          )}
          {plan.call_to_action && (
            <Grid item xs={12} md={6}>
              <PlanDetailsCard title="Call to Action" fullHeight>
                <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                  {plan.call_to_action}
                </Typography>
              </PlanDetailsCard>
            </Grid>
          )}
        </Grid>

        {/* Hook Strategy and Style & Tone Cards */}
        <Grid container spacing={3}>
          {plan.hook_strategy && (
            <Grid item xs={12} md={6}>
              <PlanDetailsCard title="Hook Strategy" fullHeight>
                <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                  {plan.hook_strategy}
                </Typography>
              </PlanDetailsCard>
            </Grid>
          )}
          <Grid item xs={12} md={6}>
            <PlanDetailsCard title="Style & Tone" fullHeight>
              <Typography variant="body1" sx={CONTENT_TEXT_STYLES}>
                Visual Style: {plan.visual_style || '—'} | Tone: {plan.tone || '—'}
              </Typography>
            </PlanDetailsCard>
          </Grid>
        </Grid>

        {/* SEO Keywords Card */}
        <SEOKeywordsCard seoKeywords={plan.seo_keywords} />

        {/* Content Outline Card */}
        <ContentOutlineCard contentOutline={plan.content_outline} />
      </Stack>
    </Paper>
  );
});

PlanDetails.displayName = 'PlanDetails';
