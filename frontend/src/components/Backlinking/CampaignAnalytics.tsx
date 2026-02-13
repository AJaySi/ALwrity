import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import { Analytics as AnalyticsIcon } from '@mui/icons-material';

interface Campaign {
  campaign_id: string;
  user_id: string;
  name: string;
  keywords: string[];
  status: string;
  created_at: string;
  email_stats: {
    sent: number;
    replied: number;
    bounced: number;
  };
}

interface CampaignAnalyticsProps {
  open: boolean;
  onClose: () => void;
  campaign: Campaign;
}

export const CampaignAnalytics: React.FC<CampaignAnalyticsProps> = ({
  open,
  onClose,
  campaign,
}) => {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <AnalyticsIcon />
        Campaign Analytics - {campaign.name}
      </DialogTitle>

      <DialogContent>
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary.main">
                  {campaign.email_stats.sent}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Emails Sent
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {campaign.email_stats.replied}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Replies Received
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="error.main">
                  {campaign.email_stats.bounced}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Bounced Emails
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Campaign Details
                </Typography>
                <Typography variant="body2">
                  <strong>Status:</strong> {campaign.status}
                </Typography>
                <Typography variant="body2">
                  <strong>Keywords:</strong> {campaign.keywords.join(', ')}
                </Typography>
                <Typography variant="body2">
                  <strong>Created:</strong> {new Date(campaign.created_at).toLocaleDateString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose}>Close</Button>
      </DialogActions>
    </Dialog>
  );
};