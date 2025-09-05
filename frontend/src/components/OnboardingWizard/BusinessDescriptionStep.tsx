import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Card, CardContent, CircularProgress, Alert } from '@mui/material';
import { ArrowBack as ArrowBackIcon, Save as SaveIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import { businessInfoApi, BusinessInfo } from '../../api/businessInfo';
import { onboardingCache } from '../../services/onboardingCache';

interface BusinessDescriptionStepProps {
  onBack: () => void;
  onContinue: () => void;
}

const BusinessDescriptionStep: React.FC<BusinessDescriptionStepProps> = ({ onBack, onContinue }) => {
  const [formData, setFormData] = useState<BusinessInfo>({
    business_description: '',
    industry: '',
    target_audience: '',
    business_goals: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔄 BusinessDescriptionStep mounted. Loading cached data...');
    const cachedData = onboardingCache.getStepData(2)?.businessInfo;
    if (cachedData) {
      setFormData(cachedData);
      console.log('✅ Loaded cached business info:', cachedData);
    } else {
      console.log('ℹ️ No cached business info found.');
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSaveAndContinue = async () => {
    setError(null);
    setSuccess(null);
    setLoading(true);
    console.log('🚀 Attempting to save business info:', formData);

    try {
      // Simulate user_id for now, replace with actual user_id from auth context later
      const userId = 1; 
      const dataToSave = { ...formData, user_id: userId };

      const response = await businessInfoApi.saveBusinessInfo(dataToSave);
      console.log('✅ Business info saved to DB:', response);
      setSuccess('Business information saved successfully!');

      // Also save to cache for consistency with other steps
      onboardingCache.saveStepData(2, { businessInfo: response, hasWebsite: false });
      console.log('✅ Business info saved to cache.');

      setTimeout(() => {
        onContinue();
      }, 1500); // Give user time to see success message
    } catch (err) {
      console.error('❌ Error saving business info:', err);
      setError('Failed to save business information. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Tell us about your business
      </Typography>
      <Typography variant="body1" color="textSecondary" sx={{ mb: 3 }}>
        Since you don't have a website, please provide a description of your business. This will help ALwrity understand your brand and tailor its services.
      </Typography>

      <Card sx={{ p: 3, mb: 3 }}>
        <CardContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircleIcon fontSize="inherit" />}>{success}</Alert>}

          <TextField
            label="Business Description"
            name="business_description"
            value={formData.business_description}
            onChange={handleChange}
            fullWidth
            multiline
            rows={4}
            margin="normal"
            required
            helperText={`${formData.business_description?.length || 0}/1000 characters`}
            inputProps={{ maxLength: 1000 }}
            disabled={loading}
          />
          <TextField
            label="Industry"
            name="industry"
            value={formData.industry}
            onChange={handleChange}
            fullWidth
            margin="normal"
            helperText={`${formData.industry?.length || 0}/100 characters`}
            inputProps={{ maxLength: 100 }}
            disabled={loading}
          />
          <TextField
            label="Target Audience"
            name="target_audience"
            value={formData.target_audience}
            onChange={handleChange}
            fullWidth
            multiline
            rows={2}
            margin="normal"
            helperText={`${(formData.target_audience || '').length}/500 characters`}
            inputProps={{ maxLength: 500 }}
            disabled={loading}
          />
          <TextField
            label="Business Goals"
            name="business_goals"
            value={formData.business_goals}
            onChange={handleChange}
            fullWidth
            multiline
            rows={3}
            margin="normal"
            helperText={`${(formData.business_goals || '').length}/1000 characters`}
            inputProps={{ maxLength: 1000 }}
            disabled={loading}
          />
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          variant="outlined"
          color="secondary"
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
          disabled={loading}
        >
          Back
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveAndContinue}
          endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          disabled={loading || !formData.business_description}
        >
          {loading ? 'Saving...' : 'Save & Continue'}
        </Button>
      </Box>
    </Box>
  );
};

export default BusinessDescriptionStep;
