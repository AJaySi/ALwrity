import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Alert,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  LinearProgress,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions
} from '@mui/material';
import {
  ExpandMore,
  Psychology,
  CheckCircle,
  Warning,
  Info,
  Visibility,
  ContentCopy,
  Download,
  Refresh,
  Twitter,
  LinkedIn,
  Instagram,
  Facebook,
  Article,
  Email
} from '@mui/icons-material';
import {
  checkPersonaReadiness,
  generatePersonaPreview,
  generateWritingPersona,
  getSupportedPlatforms,
  exportPersonaPrompt,
  PersonaReadinessResponse,
  PersonaPreviewResponse,
  PersonaGenerationResponse
} from '../../api/persona';

interface PersonaGenerationStepProps {
  onContinue: () => void;
  updateHeaderContent: (content: { title: string; description: string }) => void;
}

const PersonaGenerationStep: React.FC<PersonaGenerationStepProps> = ({ onContinue, updateHeaderContent }) => {
  const [loading, setLoading] = useState(false);
  const [readinessData, setReadinessData] = useState<PersonaReadinessResponse | null>(null);
  const [previewData, setPreviewData] = useState<PersonaPreviewResponse | null>(null);
  const [generationResult, setGenerationResult] = useState<PersonaGenerationResponse | null>(null);
  const [supportedPlatforms, setSupportedPlatforms] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [activeAccordion, setActiveAccordion] = useState<string>('readiness');
  const [showExportDialog, setShowExportDialog] = useState(false);
  const [exportedPrompt, setExportedPrompt] = useState<string>('');

  useEffect(() => {
    updateHeaderContent({
      title: 'AI Writing Persona Generation 🤖',
      description: 'Generate your personalized writing persona based on your onboarding data analysis'
    });
    
    loadInitialData();
  }, [updateHeaderContent]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load readiness check and supported platforms in parallel
      const [readiness, platforms] = await Promise.all([
        checkPersonaReadiness(),
        getSupportedPlatforms()
      ]);
      
      setReadinessData(readiness);
      setSupportedPlatforms(platforms.platforms);
      
      // If ready, automatically generate preview
      if (readiness.ready && readiness.data_sufficiency >= 70) {
        await handleGeneratePreview();
      }
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePreview = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const preview = await generatePersonaPreview();
      setPreviewData(preview);
      setActiveAccordion('preview');
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleGeneratePersona = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await generateWritingPersona();
      setGenerationResult(result);
      
      if (result.success) {
        setActiveAccordion('result');
      }
      
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExportPrompt = async (platform: string) => {
    try {
      const exportData = await exportPersonaPrompt(1, platform);
      setExportedPrompt(exportData.hardened_system_prompt);
      setShowExportDialog(true);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const getPlatformIcon = (platform: string) => {
    const icons: { [key: string]: React.ReactElement } = {
      twitter: <Twitter />,
      linkedin: <LinkedIn />,
      instagram: <Instagram />,
      facebook: <Facebook />,
      blog: <Article />,
      medium: <Article />,
      substack: <Email />
    };
    return icons[platform] || <Article />;
  };

  const getDataSufficiencyColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 85) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Readiness Check */}
      <Accordion 
        expanded={activeAccordion === 'readiness'} 
        onChange={() => setActiveAccordion(activeAccordion === 'readiness' ? '' : 'readiness')}
      >
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Psychology color="primary" />
            <Typography variant="h6">Persona Generation Readiness</Typography>
            {readinessData && (
              <Chip 
                label={readinessData.ready ? 'Ready' : 'Not Ready'} 
                color={readinessData.ready ? 'success' : 'warning'}
                size="small"
              />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {readinessData ? (
            <Box>
              <Grid container spacing={2} sx={{ mb: 2 }}>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Data Sufficiency
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress 
                          variant="determinate" 
                          value={readinessData.data_sufficiency} 
                          color={getDataSufficiencyColor(readinessData.data_sufficiency)}
                          sx={{ flexGrow: 1, height: 8, borderRadius: 1 }}
                        />
                        <Typography variant="body2" fontWeight="bold">
                          {readinessData.data_sufficiency.toFixed(1)}%
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom>
                        Status
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {readinessData.ready ? (
                          <CheckCircle color="success" />
                        ) : (
                          <Warning color="warning" />
                        )}
                        <Typography variant="body2">
                          {readinessData.message}
                        </Typography>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {readinessData.missing_steps.length > 0 && (
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" gutterBottom>
                    Missing Required Data:
                  </Typography>
                  <List dense>
                    {readinessData.missing_steps.map((step, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Warning fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={step} />
                      </ListItem>
                    ))}
                  </List>
                </Alert>
              )}

              {readinessData.recommendations && readinessData.recommendations.length > 0 && (
                <Alert severity="info">
                  <Typography variant="subtitle2" gutterBottom>
                    Recommendations:
                  </Typography>
                  <List dense>
                    {readinessData.recommendations.map((rec, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Info fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary={rec} />
                      </ListItem>
                    ))}
                  </List>
                </Alert>
              )}

              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button
                  variant="outlined"
                  onClick={handleGeneratePreview}
                  disabled={!readinessData.ready || loading}
                  startIcon={<Visibility />}
                >
                  Generate Preview
                </Button>
                <Button
                  variant="contained"
                  onClick={handleGeneratePersona}
                  disabled={!readinessData.ready || loading}
                  startIcon={<Psychology />}
                >
                  Generate Full Persona
                </Button>
              </Box>
            </Box>
          ) : (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress />
            </Box>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Preview Results */}
      {previewData && (
        <Accordion 
          expanded={activeAccordion === 'preview'} 
          onChange={() => setActiveAccordion(activeAccordion === 'preview' ? '' : 'preview')}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Visibility color="primary" />
              <Typography variant="h6">Persona Preview</Typography>
              <Chip 
                label={`${previewData.confidence_score.toFixed(1)}% Confidence`} 
                color={getConfidenceColor(previewData.confidence_score)}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Identity */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Persona Identity
                    </Typography>
                    <Typography variant="subtitle1" fontWeight="bold">
                      {previewData.preview.identity.persona_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Archetype: {previewData.preview.identity.archetype}
                    </Typography>
                    <Typography variant="body2">
                      {previewData.preview.identity.core_belief}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Linguistic Fingerprint */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Writing Style
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Sentence Length:</strong> {previewData.preview.linguistic_fingerprint.sentence_metrics?.average_sentence_length_words || 'N/A'} words avg
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Tone:</strong> {previewData.preview.tonal_range?.default_tone || 'N/A'}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Voice:</strong> {previewData.preview.linguistic_fingerprint.sentence_metrics?.preferred_sentence_type || 'N/A'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Sample Platform */}
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Sample Platform Adaptation: {previewData.preview.sample_platform.platform}
                    </Typography>
                    <Typography variant="body2">
                      This shows how your persona will be adapted for different platforms.
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                onClick={handleGeneratePersona}
                disabled={loading}
                startIcon={<Psychology />}
              >
                Generate Full Persona
              </Button>
              <Button
                variant="outlined"
                onClick={handleGeneratePreview}
                disabled={loading}
                startIcon={<Refresh />}
              >
                Refresh Preview
              </Button>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Generation Results */}
      {generationResult && (
        <Accordion 
          expanded={activeAccordion === 'result'} 
          onChange={() => setActiveAccordion(activeAccordion === 'result' ? '' : 'result')}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CheckCircle color="success" />
              <Typography variant="h6">Persona Generated Successfully</Typography>
              <Chip 
                label={`ID: ${generationResult.persona_id}`} 
                color="primary"
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={3}>
              {/* Generation Summary */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Generation Summary
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Confidence Score:</strong> {generationResult.confidence_score?.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      <strong>Data Sufficiency:</strong> {generationResult.data_sufficiency?.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2">
                      <strong>Platforms Generated:</strong> {generationResult.platforms_generated?.length || 0}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* Platform Support */}
              <Grid item xs={12} md={6}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Platform Support
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {generationResult.platforms_generated?.map((platform) => (
                        <Chip
                          key={platform}
                          icon={getPlatformIcon(platform)}
                          label={platform}
                          color="success"
                          size="small"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>

              {/* Export Options */}
              <Grid item xs={12}>
                <Card variant="outlined">
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Export Persona for External Use
                    </Typography>
                    <Typography variant="body2" gutterBottom>
                      Export hardened persona prompts for use in other AI systems (ChatGPT, Claude, etc.)
                    </Typography>
                    
                    <Grid container spacing={2} sx={{ mt: 1 }}>
                      {supportedPlatforms.slice(0, 4).map((platform) => (
                        <Grid item xs={6} md={3} key={platform.id}>
                          <Button
                            variant="outlined"
                            fullWidth
                            startIcon={getPlatformIcon(platform.id)}
                            onClick={() => handleExportPrompt(platform.id)}
                            size="small"
                          >
                            Export {platform.name}
                          </Button>
                        </Grid>
                      ))}
                    </Grid>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Button
                variant="contained"
                size="large"
                onClick={onContinue}
                startIcon={<CheckCircle />}
                color="success"
              >
                Continue to Final Step
              </Button>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}

      {/* Loading State */}
      {loading && !readinessData && (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', p: 4 }}>
          <CircularProgress size={60} />
          <Typography variant="body1" sx={{ mt: 2 }}>
            Analyzing your onboarding data...
          </Typography>
        </Box>
      )}

      {/* Action Buttons */}
      {readinessData && !generationResult && (
        <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center', gap: 2 }}>
          {readinessData.ready ? (
            <>
              {!previewData && (
                <Button
                  variant="outlined"
                  onClick={handleGeneratePreview}
                  disabled={loading}
                  startIcon={<Visibility />}
                >
                  Generate Preview
                </Button>
              )}
              <Button
                variant="contained"
                onClick={handleGeneratePersona}
                disabled={loading}
                startIcon={<Psychology />}
              >
                {loading ? <CircularProgress size={20} /> : 'Generate Persona'}
              </Button>
            </>
          ) : (
            <Alert severity="warning">
              <Typography variant="body2">
                {readinessData.message}
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                Please complete the missing onboarding steps to generate your writing persona.
              </Typography>
            </Alert>
          )}
        </Box>
      )}

      {/* Export Dialog */}
      <Dialog 
        open={showExportDialog} 
        onClose={() => setShowExportDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <Download />
            Hardened Persona Prompt
          </Box>
        </DialogTitle>
        <DialogContent>
          <Typography variant="body2" gutterBottom>
            Copy this prompt into any AI system to replicate your writing persona:
          </Typography>
          <Box 
            sx={{ 
              bgcolor: 'grey.100', 
              p: 2, 
              borderRadius: 1, 
              mt: 2,
              maxHeight: 400,
              overflow: 'auto',
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              whiteSpace: 'pre-wrap'
            }}
          >
            {exportedPrompt}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExportDialog(false)}>
            Close
          </Button>
          <Button 
            variant="contained" 
            onClick={() => copyToClipboard(exportedPrompt)}
            startIcon={<ContentCopy />}
          >
            Copy to Clipboard
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PersonaGenerationStep;