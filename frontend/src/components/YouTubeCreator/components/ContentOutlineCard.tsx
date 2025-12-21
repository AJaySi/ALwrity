/**
 * Content Outline Card Component
 */

import React from 'react';
import { Stack, Box, Typography } from '@mui/material';
import { PlanDetailsCard } from './PlanDetailsCard';
import { VideoPlan } from '../../../services/youtubeApi';

interface ContentOutlineCardProps {
  contentOutline: VideoPlan['content_outline'];
}

type ContentOutlineItem = VideoPlan['content_outline'][number];

export const ContentOutlineCard: React.FC<ContentOutlineCardProps> = React.memo(({
  contentOutline,
}) => {
  if (!contentOutline || contentOutline.length === 0) {
    return null;
  }

  return (
    <PlanDetailsCard title="Content Outline">
      <Stack spacing={1.5}>
        {contentOutline.map((item: ContentOutlineItem, idx: number) => (
          <Box
            key={idx}
            sx={{
              pl: 2.5,
              borderLeft: '3px solid #e5e7eb',
              py: 1,
              transition: 'all 0.2s ease-in-out',
              '&:hover': {
                borderLeftColor: '#d1d5db',
                bgcolor: '#f9fafb',
                borderRadius: '0 4px 4px 0',
              },
            }}
          >
            <Typography
              variant="body1"
              sx={{
                color: '#1a1a1a',
                fontWeight: 600,
                fontSize: '0.9375rem',
                mb: 0.5,
              }}
            >
              {item.section || `Section ${idx + 1}`}
              <Box
                component="span"
                sx={{
                  ml: 1.5,
                  color: '#6b7280',
                  fontWeight: 500,
                  fontSize: '0.8125rem',
                }}
              >
                ({item.duration_estimate || 0}s)
              </Box>
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#4b5563',
                lineHeight: 1.6,
                fontSize: '0.875rem',
                fontWeight: 400,
              }}
            >
              {item.description || 'Description missing'}
            </Typography>
          </Box>
        ))}
      </Stack>
    </PlanDetailsCard>
  );
});

ContentOutlineCard.displayName = 'ContentOutlineCard';

