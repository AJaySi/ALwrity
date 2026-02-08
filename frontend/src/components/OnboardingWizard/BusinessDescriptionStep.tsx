import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  TextField, 
  Typography, 
  Card, 
  CardContent, 
  CircularProgress, 
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  CardActionArea,
  Tooltip,
  InputAdornment,
  IconButton,
  Chip
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon, 
  Save as SaveIcon, 
  CheckCircle as CheckCircleIcon,
  HelpOutline as HelpIcon,
  Lightbulb as LightbulbIcon,
  AutoAwesome as AutoAwesomeIcon
} from '@mui/icons-material';
import { businessInfoApi, BusinessInfo } from '../../api/businessInfo';
import { onboardingCache } from '../../services/onboardingCache';

interface BusinessDescriptionStepProps {
  onBack: () => void;
  onContinue: (businessData?: BusinessInfo) => void;
}

const BUSINESS_EXAMPLES = [
  {
    title: "SaaS Tech Startup",
    description: "We provide AI-powered project management tools for remote teams to boost productivity and collaboration. Our platform integrates with popular tools like Slack and Jira.",
    industry: "Technology / Software",
    target_audience: "Remote-first companies, Project Managers, Product Owners, Startups",
    business_goals: "Increase user acquisition by 20% in Q3, improve user retention, and launch a new mobile app."
  },
  {
    title: "Artisanal Coffee Shop",
    description: "A cozy local coffee shop specializing in single-origin beans and homemade pastries, serving the downtown community with a focus on sustainability.",
    industry: "Food & Beverage / Hospitality",
    target_audience: "Local residents, office workers, coffee enthusiasts, students",
    business_goals: "Build a loyal customer base, increase foot traffic during weekdays, and expand catering services for local offices."
  },
  {
    title: "Digital Marketing Agency",
    description: "A full-service digital marketing agency helping small businesses grow their online presence through SEO, PPC, and content marketing strategies.",
    industry: "Marketing & Advertising",
    target_audience: "Small to medium-sized business owners, e-commerce stores, local service providers",
    business_goals: "Acquire 10 new monthly retainer clients, expand service offerings to include video marketing, and become a thought leader."
  }
];

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
  const [showExamples, setShowExamples] = useState(false);

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

  const handleExampleSelect = (example: typeof BUSINESS_EXAMPLES[0]) => {
    setFormData({
      business_description: example.description,
      industry: example.industry,
      target_audience: example.target_audience,
      business_goals: example.business_goals,
    });
    setShowExamples(false);
    setSuccess('Example data populated! You can now edit it to fit your needs.');
    setTimeout(() => setSuccess(null), 3000);
  };

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
        onContinue(response);
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
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
        <Box>
          <Typography variant="h5" gutterBottom sx={{ fontWeight: 600, color: '#111827' }}>
            Tell us about your business
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Provide details about your business to help ALwrity tailor its services.
          </Typography>
        </Box>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<LightbulbIcon />}
          onClick={() => setShowExamples(true)}
          sx={{ textTransform: 'none', borderRadius: '8px', whiteSpace: 'nowrap', ml: 2 }}
        >
          See Examples
        </Button>
      </Box>

      <Card sx={{ 
        p: 3, 
        mb: 3,
        bgcolor: '#FFFFFF',
        color: '#0B1220',
        border: '1px solid #E5E7EB',
        boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        borderRadius: '16px'
      }}>
        <CardContent>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          {success && <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircleIcon fontSize="inherit" />}>{success}</Alert>}

          <Tooltip title="Describe what your business does, your unique value proposition, and your key products or services." arrow placement="top">
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
              placeholder="e.g., We provide AI-powered project management tools for remote teams..."
              helperText={`${formData.business_description.length}/1000 characters`}
              inputProps={{ maxLength: 1000 }}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start" sx={{ mt: -3 }}>
                    <HelpIcon color="action" fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#F9FAFB',
                  color: '#111827',
                  borderRadius: '12px',
                  transition: 'all 0.2s',
                  '& fieldset': { borderColor: '#E5E7EB' },
                  '&:hover fieldset': { borderColor: '#6C5CE7' },
                  '&.Mui-focused fieldset': { borderColor: '#6C5CE7', borderWidth: '2px' },
                  '&.Mui-focused': { bgcolor: '#FFFFFF', boxShadow: '0 0 0 4px rgba(108, 92, 231, 0.1)' }
                },
                '& .MuiInputLabel-root': { color: '#6B7280' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6C5CE7' },
              }}
            />
          </Tooltip>

          <Tooltip title="What industry or sector does your business operate in?" arrow placement="top">
            <TextField
              label="Industry"
              name="industry"
              value={formData.industry}
              onChange={handleChange}
              fullWidth
              margin="normal"
              placeholder="e.g., Technology, Retail, Healthcare..."
              helperText={`${(formData.industry || '').length}/100 characters`}
              inputProps={{ maxLength: 100 }}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <HelpIcon color="action" fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#F9FAFB',
                  color: '#111827',
                  borderRadius: '12px',
                  transition: 'all 0.2s',
                  '& fieldset': { borderColor: '#E5E7EB' },
                  '&:hover fieldset': { borderColor: '#6C5CE7' },
                  '&.Mui-focused fieldset': { borderColor: '#6C5CE7', borderWidth: '2px' },
                  '&.Mui-focused': { bgcolor: '#FFFFFF', boxShadow: '0 0 0 4px rgba(108, 92, 231, 0.1)' }
                },
                '& .MuiInputLabel-root': { color: '#6B7280' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6C5CE7' },
              }}
            />
          </Tooltip>

          <Tooltip title="Who are your ideal customers? Be specific about demographics, interests, or roles." arrow placement="top">
            <TextField
              label="Target Audience"
              name="target_audience"
              value={formData.target_audience}
              onChange={handleChange}
              fullWidth
              multiline
              rows={2}
              margin="normal"
              placeholder="e.g., Small business owners, marketing managers, eco-conscious consumers..."
              helperText={`${(formData.target_audience || '').length}/500 characters`}
              inputProps={{ maxLength: 500 }}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start" sx={{ mt: -1 }}>
                    <HelpIcon color="action" fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#F9FAFB',
                  color: '#111827',
                  borderRadius: '12px',
                  transition: 'all 0.2s',
                  '& fieldset': { borderColor: '#E5E7EB' },
                  '&:hover fieldset': { borderColor: '#6C5CE7' },
                  '&.Mui-focused fieldset': { borderColor: '#6C5CE7', borderWidth: '2px' },
                  '&.Mui-focused': { bgcolor: '#FFFFFF', boxShadow: '0 0 0 4px rgba(108, 92, 231, 0.1)' }
                },
                '& .MuiInputLabel-root': { color: '#6B7280' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6C5CE7' },
              }}
            />
          </Tooltip>

          <Tooltip title="What are your main objectives for the next 6-12 months?" arrow placement="top">
            <TextField
              label="Business Goals"
              name="business_goals"
              value={formData.business_goals}
              onChange={handleChange}
              fullWidth
              multiline
              rows={3}
              margin="normal"
              placeholder="e.g., Increase brand awareness, generate more leads, launch a new product..."
              helperText={`${(formData.business_goals || '').length}/1000 characters`}
              inputProps={{ maxLength: 1000 }}
              disabled={loading}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start" sx={{ mt: -2 }}>
                    <HelpIcon color="action" fontSize="small" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: '#F9FAFB',
                  color: '#111827',
                  borderRadius: '12px',
                  transition: 'all 0.2s',
                  '& fieldset': { borderColor: '#E5E7EB' },
                  '&:hover fieldset': { borderColor: '#6C5CE7' },
                  '&.Mui-focused fieldset': { borderColor: '#6C5CE7', borderWidth: '2px' },
                  '&.Mui-focused': { bgcolor: '#FFFFFF', boxShadow: '0 0 0 4px rgba(108, 92, 231, 0.1)' }
                },
                '& .MuiInputLabel-root': { color: '#6B7280' },
                '& .MuiInputLabel-root.Mui-focused': { color: '#6C5CE7' },
              }}
            />
          </Tooltip>
        </CardContent>
      </Card>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button
          variant="outlined"
          color="inherit"
          onClick={onBack}
          startIcon={<ArrowBackIcon />}
          disabled={loading}
          sx={{ color: 'text.secondary', borderColor: 'text.disabled' }}
        >
          Back
        </Button>
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveAndContinue}
          endIcon={loading ? <CircularProgress size={20} color="inherit" /> : <SaveIcon />}
          disabled={loading || !formData.business_description}
          sx={{ 
            boxShadow: '0 4px 6px -1px rgba(108, 92, 231, 0.4), 0 2px 4px -1px rgba(108, 92, 231, 0.2)',
            '&:hover': { boxShadow: '0 10px 15px -3px rgba(108, 92, 231, 0.4), 0 4px 6px -2px rgba(108, 92, 231, 0.2)' }
          }}
        >
          {loading ? 'Saving...' : 'Save & Continue'}
        </Button>
      </Box>

      {/* Examples Modal */}
      <Dialog 
        open={showExamples} 
        onClose={() => setShowExamples(false)}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: { borderRadius: '16px' }
        }}
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, borderBottom: '1px solid #F3F4F6' }}>
          <AutoAwesomeIcon color="primary" />
          <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
            Select an Example
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto' }}>
            Click a card to populate the form
          </Typography>
        </DialogTitle>
        <DialogContent sx={{ bgcolor: '#F9FAFB', p: 3 }}>
          <Grid container spacing={2}>
            {BUSINESS_EXAMPLES.map((example, index) => (
              <Grid item xs={12} md={4} key={index}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    border: '1px solid #E5E7EB',
                    transition: 'all 0.2s',
                    '&:hover': {
                      borderColor: '#6C5CE7',
                      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
                      transform: 'translateY(-2px)'
                    }
                  }}
                >
                  <CardActionArea 
                    onClick={() => handleExampleSelect(example)}
                    sx={{ height: '100%', p: 2, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start' }}
                  >
                    <Chip 
                      label={example.title} 
                      color="primary" 
                      size="small" 
                      variant="filled" 
                      sx={{ mb: 2, fontWeight: 600, bgcolor: '#EEF2FF', color: '#6C5CE7' }} 
                    />
                    
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5, color: '#374151' }}>
                      Description:
                    </Typography>
                    <Typography variant="body2" color="text.secondary" paragraph sx={{ 
                      display: '-webkit-box',
                      WebkitLineClamp: 4,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      mb: 2,
                      fontSize: '0.875rem'
                    }}>
                      {example.description}
                    </Typography>
                    
                    <Box sx={{ mt: 'auto', width: '100%' }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 0.5, color: '#374151' }}>
                        Industry:
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {example.industry}
                      </Typography>
                    </Box>
                  </CardActionArea>
                </Card>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions sx={{ borderTop: '1px solid #F3F4F6', p: 2 }}>
          <Button onClick={() => setShowExamples(false)} color="inherit">Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default BusinessDescriptionStep;
