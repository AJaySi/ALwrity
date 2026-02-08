import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Alert
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  CheckCircle as CheckIcon,
  DataUsage as DataIcon,
  SmartToy as SmartToyIcon
} from '@mui/icons-material';

interface ComingSoonSectionProps {
  contentCalendar?: any[];
}

export const ComingSoonSection: React.FC<ComingSoonSectionProps> = ({
  contentCalendar = []
}) => {
  const [openModal, setOpenModal] = useState(false);
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);

  const features = [
    {
      id: 'test-persona',
      title: 'Test Your Persona',
      description: 'Generate content with different personas to see the difference',
      icon: <PsychologyIcon />,
      status: 'Coming Soon',
      color: '#3b82f6',
      details: [
        'Compare content generated with and without your persona',
        'Test Brand, Blog, and LinkedIn brand voices side-by-side',
        'Directly apply Brand Voice to any Alwrity tool',
        'AI-powered feedback on brand voice consistency'
      ]
    },
    {
      id: 'deep-crawl',
      title: 'Deep Website Analysis',
      description: 'Crawl 10+ pages for comprehensive persona generation',
      icon: <DataIcon />,
      status: 'In Development',
      color: '#10b981',
      details: [
        'Analyze multiple blog posts and pages',
        'Extract comprehensive writing patterns',
        'Understand content themes and topics',
        'Generate more accurate personas',
        'Better brand voice detection'
      ]
    },
    {
      id: 'fine-tuning',
      title: 'Personal AI Fine-Tuning',
      description: 'Train a custom AI model specifically for your brand',
      icon: <SmartToyIcon />,
      status: 'Planned',
      color: '#8b5cf6',
      details: [
        'Fine-tune Google Gemma model with your data',
        'Create your personal AI marketing team',
        'Learn from your website, social media, and analytics',
        'Generate content that sounds authentically like you',
        'Private model - your data stays secure'
      ]
    }
  ];

  const handleFeatureClick = (featureId: string) => {
    setSelectedFeature(featureId);
    setOpenModal(true);
  };

  const selectedFeatureData = features.find(f => f.id === selectedFeature);

  return (
    <>
      <Box sx={{ mt: 4, mb: 2 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, color: '#1e293b', mb: 1.5 }}>
          🚀 Coming Soon
        </Typography>
        <Typography variant="body1" sx={{ color: '#64748b', mb: 4, fontSize: '1.1rem' }}>
          Exciting features in development to make your AI writing even more powerful
        </Typography>

        <Grid container spacing={2}>
          {features.map((feature) => (
            <Grid item xs={12} md={4} key={feature.id}>
              <Card
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease',
                  border: '2px solid #e2e8f0',
                  backgroundColor: '#ffffff',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: '0 12px 30px rgba(0, 0, 0, 0.15)',
                    borderColor: feature.color,
                    '& .feature-icon': {
                      transform: 'scale(1.1)',
                      backgroundColor: `${feature.color}20`
                    }
                  }
                }}
                onClick={() => handleFeatureClick(feature.id)}
              >
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Box
                      className="feature-icon"
                      sx={{
                        p: 2,
                        borderRadius: 3,
                        backgroundColor: `${feature.color}15`,
                        color: feature.color,
                        mr: 2,
                        transition: 'all 0.3s ease',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                    >
                      {feature.icon}
                    </Box>
                    <Box sx={{ flex: 1 }}>
                      <Typography variant="h6" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
                        {feature.title}
                      </Typography>
                      <Chip
                        label={feature.status}
                        size="small"
                        sx={{
                          backgroundColor: `${feature.color}20`,
                          color: feature.color,
                          fontWeight: 600,
                          fontSize: '0.75rem',
                          height: 24,
                          '& .MuiChip-label': {
                            px: 1.5
                          }
                        }}
                      />
                    </Box>
                  </Box>
                  
                  <Typography variant="body1" sx={{ color: '#64748b', mb: 3, lineHeight: 1.6 }}>
                    {feature.description}
                  </Typography>

                  <Button
                    variant="outlined"
                    size="medium"
                    sx={{
                      borderColor: feature.color,
                      color: feature.color,
                      fontWeight: 600,
                      px: 3,
                      py: 1,
                      borderRadius: 2,
                      textTransform: 'none',
                      '&:hover': {
                        backgroundColor: `${feature.color}15`,
                        borderColor: feature.color,
                        transform: 'translateY(-1px)'
                      }
                    }}
                  >
                    Learn More
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        <Alert 
          severity="info" 
          sx={{ 
            mt: 4, 
            backgroundColor: '#f0f9ff',
            border: '2px solid #0ea5e9',
            borderRadius: 3,
            '& .MuiAlert-icon': {
              color: '#0ea5e9',
              fontSize: '1.5rem'
            }
          }}
        >
          <Typography variant="body1" sx={{ color: '#0c4a6e', fontWeight: 500 }}>
            <strong>What's Next:</strong> These features will be available in upcoming releases. 
            Your current persona is already powerful and ready to use!
          </Typography>
        </Alert>
      </Box>

      {/* Feature Details Modal */}
      <Dialog
        open={openModal}
        onClose={() => setOpenModal(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ pb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 3 }}>
            {selectedFeatureData && (
              <>
                <Box
                  sx={{
                    p: 2,
                    borderRadius: 3,
                    backgroundColor: `${selectedFeatureData.color}20`,
                    color: selectedFeatureData.color,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                >
                  {selectedFeatureData.icon}
                </Box>
                <Box>
                  <Typography variant="h5" sx={{ fontWeight: 700, color: '#1e293b', mb: 1 }}>
                    {selectedFeatureData.title}
                  </Typography>
                  <Chip
                    label={selectedFeatureData.status}
                    size="medium"
                    sx={{
                      backgroundColor: `${selectedFeatureData.color}20`,
                      color: selectedFeatureData.color,
                      fontWeight: 600,
                      fontSize: '0.875rem'
                    }}
                  />
                </Box>
              </>
            )}
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {selectedFeatureData && (
            <>
              <Typography variant="body1" sx={{ color: '#64748b', mb: 4, fontSize: '1.1rem', lineHeight: 1.6 }}>
                {selectedFeatureData.description}
              </Typography>

              <Typography variant="h6" sx={{ fontWeight: 700, mb: 3, color: '#1e293b' }}>
                Key Features:
              </Typography>

              <List sx={{ pl: 0 }}>
                {selectedFeatureData.details.map((detail, index) => (
                  <ListItem key={index} sx={{ pl: 0, py: 1 }}>
                    <ListItemIcon sx={{ minWidth: 32 }}>
                      <CheckIcon sx={{ color: selectedFeatureData.color, fontSize: 20 }} />
                    </ListItemIcon>
                    <ListItemText 
                      primary={detail}
                      primaryTypographyProps={{
                        variant: 'body1',
                        color: '#374151',
                        fontWeight: 500
                      }}
                    />
                  </ListItem>
                ))}
              </List>

              {selectedFeatureData.id === 'test-persona' && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: '#f8fafc', borderRadius: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#1e293b' }}>
                    How It Works:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Select a topic from your content calendar, then generate content using different personas 
                    to see how your AI adapts its writing style. Compare the results and provide feedback 
                    to continuously improve your persona.
                  </Typography>
                </Box>
              )}

              {selectedFeatureData.id === 'fine-tuning' && (
                <Box sx={{ mt: 3, p: 2, backgroundColor: '#f0f9ff', borderRadius: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#1e293b' }}>
                    Privacy & Security:
                  </Typography>
                  <Typography variant="body2" sx={{ color: '#64748b' }}>
                    Your data is used exclusively to train your private AI model. It's never shared 
                    or used for any other purpose. You own your AI, and it works only for you.
                  </Typography>
                </Box>
              )}
            </>
          )}
        </DialogContent>
        
        <DialogActions sx={{ p: 3, pt: 1 }}>
          <Button 
            onClick={() => setOpenModal(false)}
            variant="outlined"
          >
            Close
          </Button>
          <Button 
            onClick={() => setOpenModal(false)}
            variant="contained"
            sx={{
              backgroundColor: selectedFeatureData?.color || '#3b82f6',
              '&:hover': {
                backgroundColor: selectedFeatureData?.color || '#3b82f6',
                opacity: 0.9
              }
            }}
          >
            Notify Me When Ready
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ComingSoonSection;
