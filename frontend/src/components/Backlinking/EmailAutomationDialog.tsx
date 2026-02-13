import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  TextField,
  Alert,
  Stepper,
  Step,
  StepLabel,
  Card,
  CardContent,
} from '@mui/material';
import { Email as EmailIcon, Send as SendIcon } from '@mui/icons-material';

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

interface EmailAutomationDialogProps {
  open: boolean;
  onClose: () => void;
  campaign: Campaign;
}

export const EmailAutomationDialog: React.FC<EmailAutomationDialogProps> = ({
  open,
  onClose,
  campaign,
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [smtpConfig, setSmtpConfig] = useState({
    server: 'smtp.gmail.com',
    port: 587,
    user: '',
    password: '',
  });
  const [imapConfig, setImapConfig] = useState({
    server: 'imap.gmail.com',
    user: '',
    password: '',
  });

  const steps = [
    'SMTP Configuration',
    'IMAP Configuration',
    'Review & Send'
  ];

  const handleNext = () => {
    setActiveStep((prevStep) => prevStep + 1);
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSendEmails = () => {
    // TODO: Implement email sending logic
    onClose();
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              SMTP Configuration
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Configure your email server settings to send outreach emails.
            </Typography>

            <TextField
              fullWidth
              label="SMTP Server"
              value={smtpConfig.server}
              onChange={(e) => setSmtpConfig(prev => ({ ...prev, server: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Port"
              type="number"
              value={smtpConfig.port}
              onChange={(e) => setSmtpConfig(prev => ({ ...prev, port: parseInt(e.target.value) }))}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={smtpConfig.user}
              onChange={(e) => setSmtpConfig(prev => ({ ...prev, user: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Password / App Password"
              type="password"
              value={smtpConfig.password}
              onChange={(e) => setSmtpConfig(prev => ({ ...prev, password: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                For Gmail, use "smtp.gmail.com" on port 587 and create an App Password in your Google Account settings.
              </Typography>
            </Alert>
          </Box>
        );

      case 1:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              IMAP Configuration
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Configure settings to check for email responses.
            </Typography>

            <TextField
              fullWidth
              label="IMAP Server"
              value={imapConfig.server}
              onChange={(e) => setImapConfig(prev => ({ ...prev, server: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={imapConfig.user}
              onChange={(e) => setImapConfig(prev => ({ ...prev, user: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <TextField
              fullWidth
              label="Password / App Password"
              type="password"
              value={imapConfig.password}
              onChange={(e) => setImapConfig(prev => ({ ...prev, password: e.target.value }))}
              sx={{ mb: 2 }}
            />

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2">
                For Gmail, use "imap.gmail.com" and the same App Password as SMTP.
              </Typography>
            </Alert>
          </Box>
        );

      case 2:
        return (
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Review Configuration
            </Typography>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Campaign: {campaign.name}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Keywords: {campaign.keywords.join(', ')}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {campaign.status}
                </Typography>
              </CardContent>
            </Card>

            <Card sx={{ mb: 2 }}>
              <CardContent>
                <Typography variant="subtitle1" sx={{ mb: 1 }}>
                  Email Configuration
                </Typography>
                <Typography variant="body2">
                  SMTP: {smtpConfig.server}:{smtpConfig.port}
                </Typography>
                <Typography variant="body2">
                  From: {smtpConfig.user}
                </Typography>
              </CardContent>
            </Card>

            <Alert severity="warning" sx={{ mt: 2 }}>
              <Typography variant="body2">
                This will generate and send personalized outreach emails to discovered opportunities.
                Make sure your email configuration is correct before proceeding.
              </Typography>
            </Alert>
          </Box>
        );

      default:
        return null;
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <EmailIcon />
        Email Automation Setup - {campaign.name}
      </DialogTitle>

      <DialogContent>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="inherit">
          Cancel
        </Button>

        {activeStep > 0 && (
          <Button onClick={handleBack}>
            Back
          </Button>
        )}

        {activeStep < steps.length - 1 ? (
          <Button onClick={handleNext} variant="contained">
            Next
          </Button>
        ) : (
          <Button
            onClick={handleSendEmails}
            variant="contained"
            startIcon={<SendIcon />}
          >
            Start Email Automation
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};