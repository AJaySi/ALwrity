/**
 * SEO Keywords Card Component
 */

import React from 'react';
import { Stack, Chip } from '@mui/material';
import { PlanDetailsCard } from './PlanDetailsCard';
import { VideoPlan } from '../../../services/youtubeApi';

interface SEOKeywordsCardProps {
  seoKeywords: VideoPlan['seo_keywords'];
}

export const SEOKeywordsCard: React.FC<SEOKeywordsCardProps> = React.memo(({
  seoKeywords,
}) => {
  if (!seoKeywords || seoKeywords.length === 0) {
    return null;
  }

  return (
    <PlanDetailsCard title="SEO Keywords">
      <Stack direction="row" spacing={1.5} flexWrap="wrap" useFlexGap>
        {seoKeywords.map((kw: string, idx: number) => (
          <Chip
            key={`${kw}-${idx}`}
            label={kw}
            size="medium"
            sx={{
              backgroundColor: '#f3f4f6',
              color: '#1f2937',
              fontWeight: 500,
              fontSize: '0.8125rem',
              height: 32,
              border: '1px solid #e5e7eb',
              '& .MuiChip-label': {
                px: 1.5,
              },
            }}
          />
        ))}
      </Stack>
    </PlanDetailsCard>
  );
});

SEOKeywordsCard.displayName = 'SEOKeywordsCard';

