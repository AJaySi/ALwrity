/**
 * Email Campaigns Section Component
 *
 * Displays email campaigns management panel
 */

import React from 'react';
import { Box } from '@mui/material';
import { EmailCampaignsPanel } from '../../EmailCampaignsPanel';

interface EmailCampaignsSectionProps {
  onCampaignSelect?: (campaign: any) => void;
}

export const EmailCampaignsSection: React.FC<EmailCampaignsSectionProps> = ({
  onCampaignSelect,
}) => {
  return (
    <Box sx={{ mb: 4 }}>
      <EmailCampaignsPanel onCampaignSelect={onCampaignSelect} />
    </Box>
  );
};