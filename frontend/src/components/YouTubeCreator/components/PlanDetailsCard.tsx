/**
 * Reusable Plan Details Card Component
 */

import React from 'react';
import { Card, CardContent, Typography } from '@mui/material';

interface PlanDetailsCardProps {
  title: string;
  children: React.ReactNode;
  fullHeight?: boolean;
}

export const PlanDetailsCard: React.FC<PlanDetailsCardProps> = React.memo(({
  title,
  children,
  fullHeight = false,
}) => {
  return (
    <Card
      elevation={0}
      sx={{
        border: '1px solid #e5e7eb',
        borderRadius: 2,
        bgcolor: '#ffffff',
        height: fullHeight ? '100%' : 'auto',
        transition: 'all 0.2s ease-in-out',
        '&:hover': {
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        },
      }}
    >
      <CardContent sx={{ p: 2.5 }}>
        <Typography
          variant="body2"
          sx={{
            fontWeight: 700,
            color: '#1a1a1a',
            mb: 1.5,
            fontSize: '0.875rem',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
          }}
        >
          {title}
        </Typography>
        {children}
      </CardContent>
    </Card>
  );
});

PlanDetailsCard.displayName = 'PlanDetailsCard';

