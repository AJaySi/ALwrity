/**
 * Campaign Performance Page
 *
 * Dedicated page for viewing detailed campaign performance analytics
 */

import React from 'react';
import { Box, Container } from '@mui/material';
import { CampaignPerformanceDashboard } from '../components/Backlinking/CampaignPerformanceDashboard';
import { useParams } from 'react-router-dom';

const CampaignPerformance: React.FC = () => {
  const { campaignId } = useParams<{ campaignId: string }>();

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <CampaignPerformanceDashboard
        campaignId={campaignId}
        timeRange="30d"
        showExport={true}
      />
    </Container>
  );
};

export default CampaignPerformance;