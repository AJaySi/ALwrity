import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Grid,
  Chip,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  CircularProgress,
  useTheme,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Modal,
  Fade,
  Backdrop,
  Snackbar,
} from '@mui/material';
import {
  Check as CheckIcon,
  Close as CloseIcon,
  Star as StarIcon,
  WorkspacePremium as PremiumIcon,
  Info as InfoIcon,
  Warning,
  Psychology,
  Search as SearchIcon,
  FactCheck,
  Edit,
  Assistant,
  Verified,
  Timeline,
  Analytics,
  Support,
  Business,
  Group,
} from '@mui/icons-material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import ImageIcon from '@mui/icons-material/Image';
import VideoIcon from '@mui/icons-material/VideoLibrary';
import AudioIcon from '@mui/icons-material/Audiotrack';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../api/client';
import { restoreNavigationState, saveCurrentPhaseForTool } from '../../utils/navigationState';

interface SubscriptionPlan {
  id: number;
  name: string;
  tier: string;
  price_monthly: number;
  price_yearly: number;
  description: string;
  features: string[];
  limits: {
    gemini_calls: number;
    openai_calls: number;
    anthropic_calls: number;
    mistral_calls: number;
    tavily_calls: number;
    serper_calls: number;
    metaphor_calls: number;
    firecrawl_calls: number;
    stability_calls: number;
    monthly_cost: number;
    // New limit fields (optional for backward compatibility)
    image_edit_calls?: number;
    video_calls?: number;
    audio_calls?: number;
    ai_text_generation_calls_limit?: number; // Unified limit for Basic tier
  };
}

const PricingPage: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [yearlyBilling, setYearlyBilling] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState<number | null>(null);
  const [subscribing, setSubscribing] = useState(false);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [showSignInPrompt, setShowSignInPrompt] = useState(false);
  const [successSnackbar, setSuccessSnackbar] = useState({ open: false, message: '', countdown: 3 });
  const [knowMoreModal, setKnowMoreModal] = useState<{ open: boolean; title: string; content: React.ReactNode }>({
    open: false,
    title: '',
    content: null
  });

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/api/subscription/plans');
      // Filter out any alpha plans and ensure we only show the 4 main tiers
      const filteredPlans = response.data.data.plans.filter(
        (plan: SubscriptionPlan) => !plan.name.toLowerCase().includes('alpha')
      );
      setPlans(filteredPlans);
    } catch (err) {
      console.error('Error fetching plans:', err);
      setError('Failed to load subscription plans');
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId: number) => {
    console.log('[PricingPage] handleSubscribe called', { planId });
    
    const plan = plans.find(p => p.id === planId);
    if (!plan) {
      console.error('[PricingPage] ❌ Plan not found for ID:', planId);
      return;
    }

    console.log('[PricingPage] Selected plan:', { id: plan.id, name: plan.name, tier: plan.tier });

    // Get user_id from localStorage (set by Clerk auth)
    const userId = localStorage.getItem('user_id');
    
    // Check if user is signed in
    if (!userId || userId === 'anonymous' || userId === '') {
      // User not signed in, show sign-in prompt
      console.warn('[PricingPage] User not signed in, showing prompt');
      setShowSignInPrompt(true);
      return;
    }

    // For alpha testing, only allow Free and Basic plans (Pro features not ready)
    if (plan.tier !== 'free' && plan.tier !== 'basic') {
      console.error('[PricingPage] Plan tier not available:', plan.tier);
      setError('This plan is not available for alpha testing');
      return;
    }

    if (plan.tier === 'free') {
      console.log('[PricingPage] Processing Free plan subscription directly');
      // For free plan, just create subscription
      try {
        setSubscribing(true);
        const userId = localStorage.getItem('user_id') || 'anonymous';

        await apiClient.post(`/api/subscription/subscribe/${userId}`, {
          plan_id: planId,
          billing_cycle: yearlyBilling ? 'yearly' : 'monthly'
        });

        // Refresh subscription status
        window.dispatchEvent(new CustomEvent('subscription-updated'));

        // After subscription, check if onboarding is complete
        // If not complete, redirect to onboarding; otherwise to dashboard
        const onboardingComplete = localStorage.getItem('onboarding_complete') === 'true';
        if (onboardingComplete) {
          navigate('/dashboard');
        } else {
          navigate('/onboarding');
        }
      } catch (err) {
        console.error('Error subscribing:', err);
        setError('Failed to process subscription');
      } finally {
        setSubscribing(false);
      }
    } else {
      // For Basic plan, show payment modal
      console.log('[PricingPage] Opening payment modal for Basic plan', { planId, planName: plan.name });
      setSelectedPlan(planId);  // ✅ Set selected plan before opening modal
      setPaymentModalOpen(true);
    }
  };

  const handlePaymentConfirm = async () => {
    console.log('[PricingPage] handlePaymentConfirm called', { selectedPlan, yearlyBilling });
    
    if (!selectedPlan) {
      console.error('[PricingPage] ❌ No selectedPlan set - cannot proceed with subscription');
      setError('No plan selected. Please select a plan and try again.');
      return;
    }

    try {
      setSubscribing(true);
      const userId = localStorage.getItem('user_id') || 'anonymous';

      console.log('[PricingPage] Making subscription API call:', {
        url: `/api/subscription/subscribe/${userId}`,
        plan_id: selectedPlan,
        billing_cycle: yearlyBilling ? 'yearly' : 'monthly',
        userId
      });

      const response = await apiClient.post(`/api/subscription/subscribe/${userId}`, {
        plan_id: selectedPlan,
        billing_cycle: yearlyBilling ? 'yearly' : 'monthly'
      });

      console.log('[PricingPage] ✅ Subscription renewed successfully:', response.data);

      // Refresh subscription status immediately
      window.dispatchEvent(new CustomEvent('subscription-updated'));
      
      // Also trigger user authenticated event to refresh subscription context
      window.dispatchEvent(new CustomEvent('user-authenticated'));

      setPaymentModalOpen(false);

      // Get plan name for success message
      const planName = plans.find(p => p.id === selectedPlan)?.name || 'subscription';
      
      // Show success message with countdown
      setSuccessSnackbar({ 
        open: true, 
        message: `🎉 ${planName} plan activated! Your usage limits have been reset. Returning to your work in 3 seconds...`,
        countdown: 3 
      });

      // Countdown timer
      let countdown = 3;
      const countdownInterval = setInterval(() => {
        countdown -= 1;
        if (countdown > 0) {
          setSuccessSnackbar(prev => ({ 
            ...prev, 
            message: `🎉 ${planName} plan activated! Your usage limits have been reset. Returning to your work in ${countdown} second${countdown !== 1 ? 's' : ''}...`,
            countdown 
          }));
        } else {
          clearInterval(countdownInterval);
        }
      }, 1000);

      // Auto-redirect after 3 seconds
      setTimeout(() => {
        clearInterval(countdownInterval);
        
        // After subscription, check if onboarding is complete
        // If not complete, redirect to onboarding; otherwise to dashboard
        const onboardingComplete = localStorage.getItem('onboarding_complete') === 'true';
        if (onboardingComplete) {
          // Restore navigation state (path, phase, tool) if available
          const navState = restoreNavigationState();
          
          if (navState && navState.path && navState.path !== '/pricing') {
            // Restore phase if applicable (e.g., Blog Writer)
            if (navState.tool === 'blog-writer' && navState.phase) {
              saveCurrentPhaseForTool('blog-writer', navState.phase);
              console.log('[PricingPage] Restored Blog Writer phase:', navState.phase);
            }
            
            console.log('[PricingPage] Redirecting to saved navigation state:', navState);
            navigate(navState.path);
          } else {
            // Fallback: try legacy referrer
            const referrer = sessionStorage.getItem('subscription_referrer');
            if (referrer && referrer !== '/pricing') {
              navigate(referrer);
            } else {
              navigate('/dashboard');
            }
          }
        } else {
          navigate('/onboarding');
        }
      }, 3000);
    } catch (err) {
      console.error('Error subscribing:', err);
      setError('Failed to process subscription');
      setSuccessSnackbar({ open: false, message: '', countdown: 0 });
    } finally {
      setSubscribing(false);
    }
  };

  const openKnowMoreModal = (title: string, content: React.ReactNode) => {
    setKnowMoreModal({
      open: true,
      title,
      content
    });
  };

  const getPlanIcon = (tier: string) => {
    switch (tier) {
      case 'free':
        return <CheckIcon color="success" />;
      case 'basic':
        return <StarIcon color="primary" />;
      case 'pro':
        return <PremiumIcon color="secondary" />;
      case 'enterprise':
        return <PremiumIcon sx={{ color: theme.palette.warning.main }} />;
      default:
        return <CheckIcon />;
    }
  };

  const getPlanColor = (tier: string) => {
    switch (tier) {
      case 'free':
        return 'success' as const;
      case 'basic':
        return 'primary' as const;
      case 'pro':
        return 'secondary' as const;
      case 'enterprise':
        return 'warning' as const;
      default:
        return undefined;
    }
  };

  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 8, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography variant="h6" sx={{ mt: 2 }}>
          Loading subscription plans...
        </Typography>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Alert severity="error" sx={{ mb: 4 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={fetchPlans}>
          Try Again
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Box sx={{ textAlign: 'center', mb: 6 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Choose Your Plan
        </Typography>
        <Typography variant="h6" color="text.secondary" sx={{ mb: 2 }}>
          Select the perfect plan for your AI content creation needs
        </Typography>
        <Alert severity="info" sx={{ maxWidth: 800, mx: 'auto', mb: 4, textAlign: 'left' }}>
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
            💡 Perfect for Content Creators, Marketers, Solopreneurs & Startups
          </Typography>
          <Typography variant="caption">
            All plans include access to every ALwrity tool. Limits reset monthly, and you're protected by automatic cost caps.
            {yearlyBilling && ' Save 20% with yearly billing!'}
          </Typography>
        </Alert>

        {/* Billing Toggle */}
        <FormControlLabel
          control={
            <Switch
              checked={yearlyBilling}
              onChange={(e) => setYearlyBilling(e.target.checked)}
              color="primary"
            />
          }
          label={yearlyBilling ? "Yearly Billing (Save 20%)" : "Monthly Billing"}
          sx={{ mb: 2 }}
        />
      </Box>

      <Grid container spacing={4} justifyContent="center">
        {plans.map((plan) => (
          <Grid item key={plan.id} xs={12} sm={6} md={3}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                position: 'relative',
                border: selectedPlan === plan.id ? `2px solid ${theme.palette.primary.main}` : '1px solid #e0e0e0',
                transform: selectedPlan === plan.id ? 'scale(1.02)' : 'scale(1)',
                transition: 'all 0.3s ease-in-out',
              }}
            >
              {/* Plan Badge */}
              {plan.tier === 'pro' && (
                <Chip
                  label="Most Popular"
                  color="primary"
                  size="small"
                  sx={{
                    position: 'absolute',
                    top: -8,
                    right: 16,
                    zIndex: 1,
                  }}
                />
              )}

              <CardContent sx={{ flexGrow: 1, textAlign: 'center' }}>
                <Box sx={{ mb: 2 }}>
                  {getPlanIcon(plan.tier)}
                </Box>

                <Typography variant="h5" component="h2" gutterBottom>
                  {plan.name}
                </Typography>

                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  {plan.description}
                </Typography>

                {/* Pricing */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h3" component="span">
                    ${yearlyBilling ? plan.price_yearly : plan.price_monthly}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    /{yearlyBilling ? 'year' : 'month'}
                  </Typography>
                  {yearlyBilling && (
                    <Typography variant="caption" color="success.main" sx={{ display: 'block' }}>
                      Save ${(plan.price_monthly * 12 - plan.price_yearly).toFixed(0)} yearly
                    </Typography>
                  )}
                </Box>

                {/* Features */}
                <List dense>
                  {/* All Tools Access - Free & Basic */}
                  {(plan.tier === 'free' || plan.tier === 'basic') && (
                    <>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="text.secondary" sx={{ px: 2, fontWeight: 600 }}>
                        ✨ All ALwrity Tools Included:
                      </Typography>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Edit color="primary" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="Blog Writer"
                            secondary="AI-powered blog post creation with SEO optimization"
                          />
                          <Tooltip title="Learn more about Blog Writer">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('Blog Writer', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>Blog Writer</Typography>
                                  <Typography variant="body2" paragraph>
                                    Create engaging blog posts with AI assistance. Includes SEO optimization,
                                    keyword research, and content structure suggestions.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• SEO-optimized content generation</Typography>
                                  <Typography variant="body2">• Keyword research integration</Typography>
                                  <Typography variant="body2">• Content structure suggestions</Typography>
                                  <Typography variant="body2">• Publishing assistance</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Business color="primary" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="LinkedIn Writer"
                            secondary="Professional LinkedIn content creation and posting"
                          />
                          <Tooltip title="Learn more about LinkedIn Writer">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('LinkedIn Writer', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>LinkedIn Writer</Typography>
                                  <Typography variant="body2" paragraph>
                                    Create professional LinkedIn posts, articles, and carousels that engage
                                    your network and showcase your expertise.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• Professional post generation</Typography>
                                  <Typography variant="body2">• Article writing assistance</Typography>
                                  <Typography variant="body2">• Carousel creation</Typography>
                                  <Typography variant="body2">• Network engagement optimization</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Group color="primary" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="Facebook Writer"
                            secondary="Engaging Facebook posts and content creation"
                          />
                          <Tooltip title="Learn more about Facebook Writer">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('Facebook Writer', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>Facebook Writer</Typography>
                                  <Typography variant="body2" paragraph>
                                    Create engaging Facebook posts, stories, and reels that drive
                                    engagement and grow your community.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• Post and story creation</Typography>
                                  <Typography variant="body2">• Reel script generation</Typography>
                                  <Typography variant="body2">• Community management</Typography>
                                  <Typography variant="body2">• Engagement optimization</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <MenuBookIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Story Writer"
                          secondary="Create stories with AI: outline, images, narration, and video"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <AudioIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Podcast Maker"
                          secondary="AI-powered research, scriptwriting, and voice narration"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <ImageIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Image Generator & Editor"
                          secondary="AI image creation and editing (background removal, inpainting)"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <VideoIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Video Studio & YouTube Creator"
                          secondary="AI video creation for social media and YouTube"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <SearchIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="All SEO Tools & Dashboards"
                          secondary="Keyword research, content optimization, SEO analytics"
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Timeline color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Content Planning & Strategy"
                          secondary="Content calendars, strategy planning, and analytics"
                        />
                      </ListItem>
                    </>
                  )}

                  {/* Platform Integrations - Pro & Free */}
                  {(plan.tier === 'free' || plan.tier === 'pro' || plan.tier === 'enterprise') && (
                    <>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="text.secondary" sx={{ px: 2 }}>
                        Platform Integrations:
                      </Typography>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Business color="success" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="Wix Integration"
                            secondary="Direct publishing to Wix websites"
                          />
                          <Tooltip title="Learn more about Wix integration">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('Wix Integration', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>Wix Integration</Typography>
                                  <Typography variant="body2" paragraph>
                                    Seamlessly publish your content directly to Wix websites.
                                    No manual copying required.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• Direct blog post publishing</Typography>
                                  <Typography variant="body2">• SEO metadata sync</Typography>
                                  <Typography variant="body2">• Image optimization</Typography>
                                  <Typography variant="body2">• Publishing queue management</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Edit color="success" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="WordPress Integration"
                            secondary="Publish to WordPress sites with API integration"
                          />
                          <Tooltip title="Learn more about WordPress integration">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('WordPress Integration', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>WordPress Integration</Typography>
                                  <Typography variant="body2" paragraph>
                                    Connect directly to WordPress sites for seamless content publishing.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• REST API integration</Typography>
                                  <Typography variant="body2">• Draft and publish modes</Typography>
                                  <Typography variant="body2">• Category and tag management</Typography>
                                  <Typography variant="body2">• Featured image handling</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Analytics color="success" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="Google Search Console"
                            secondary="SEO performance tracking and insights"
                          />
                          <Tooltip title="Learn more about GSC integration">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('Google Search Console', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>Google Search Console</Typography>
                                  <Typography variant="body2" paragraph>
                                    Monitor your website's SEO performance and get actionable insights
                                    for content optimization.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Features:</strong>
                                  </Typography>
                                  <Typography variant="body2">• Search performance tracking</Typography>
                                  <Typography variant="body2">• Keyword ranking insights</Typography>
                                  <Typography variant="body2">• Technical SEO monitoring</Typography>
                                  <Typography variant="body2">• Content optimization suggestions</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>
                    </>
                  )}

                  {/* Social Media & Website Management - Pro & Enterprise */}
                  {(plan.tier === 'pro' || plan.tier === 'enterprise') && (
                    <>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="text.secondary" sx={{ px: 2 }}>
                        Social Media & Website Management:
                      </Typography>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Group color="secondary" fontSize="small" />
                        </ListItemIcon>
                        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                          <ListItemText
                            primary="6 Major Social Platforms"
                            secondary="LinkedIn, Facebook, Instagram, Twitter, TikTok, YouTube"
                          />
                          <Tooltip title="Learn more about social media platforms">
                            <IconButton
                              size="small"
                              onClick={() => openKnowMoreModal('6 Major Social Platforms', (
                                <Box>
                                  <Typography variant="h6" gutterBottom>6 Major Social Platforms</Typography>
                                  <Typography variant="body2" paragraph>
                                    Comprehensive social media management across all major platforms
                                    with AI-powered content optimization.
                                  </Typography>
                                  <Typography variant="body2" gutterBottom>
                                    <strong>Platforms:</strong>
                                  </Typography>
                                  <Typography variant="body2">• LinkedIn (Professional networking)</Typography>
                                  <Typography variant="body2">• Facebook (Community building)</Typography>
                                  <Typography variant="body2">• Instagram (Visual storytelling)</Typography>
                                  <Typography variant="body2">• Twitter (Real-time engagement)</Typography>
                                  <Typography variant="body2">• TikTok (Short-form video)</Typography>
                                  <Typography variant="body2">• YouTube (Long-form video content)</Typography>
                                </Box>
                              ))}
                            >
                              <InfoIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Business color="secondary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Website Management"
                          secondary="Blogging platform with content scheduling and SEO tools"
                        />
                      </ListItem>
                    </>
                  )}

                  {/* AI Content Creation Capabilities */}
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" color="text.secondary" sx={{ px: 2 }}>
                    AI Content Creation:
                  </Typography>

                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <Edit color="primary" fontSize="small" />
                    </ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                      <ListItemText
                        primary="Text Generation"
                        secondary={plan.tier === 'free' || plan.tier === 'basic'
                          ? "AI-powered text content creation"
                          : "Advanced text generation with multimodal capabilities"
                        }
                      />
                      <Tooltip title="Learn more about text generation">
                        <IconButton
                          size="small"
                          onClick={() => openKnowMoreModal('Text Generation', (
                            <Box>
                              <Typography variant="h6" gutterBottom>AI Text Generation</Typography>
                              <Typography variant="body2" paragraph>
                                Generate high-quality text content with AI assistance. From blog posts
                                to social media updates, create engaging content effortlessly.
                              </Typography>
                              <Typography variant="body2" gutterBottom>
                                <strong>Capabilities:</strong>
                              </Typography>
                              <Typography variant="body2">• Blog posts and articles</Typography>
                              <Typography variant="body2">• Social media content</Typography>
                              <Typography variant="body2">• Email newsletters</Typography>
                              <Typography variant="body2">• Marketing copy</Typography>
                              {plan.tier === 'pro' || plan.tier === 'enterprise' && (
                                <>
                                  <Typography variant="body2">• Audio transcription</Typography>
                                  <Typography variant="body2">• Video script writing</Typography>
                                </>
                              )}
                            </Box>
                          ))}
                        >
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItem>

                  <ListItem>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <Assistant color="primary" fontSize="small" />
                    </ListItemIcon>
                    <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
                      <ListItemText
                        primary="Image Generation"
                        secondary={plan.tier === 'free' || plan.tier === 'basic'
                          ? "AI image creation for visual content"
                          : "Advanced image generation with video capabilities"
                        }
                      />
                      <Tooltip title="Learn more about image generation">
                        <IconButton
                          size="small"
                          onClick={() => openKnowMoreModal('Image Generation', (
                            <Box>
                              <Typography variant="h6" gutterBottom>AI Image Generation</Typography>
                              <Typography variant="body2" paragraph>
                                Create stunning visuals with AI-powered image generation.
                                Perfect for social media, blog posts, and marketing materials.
                              </Typography>
                              <Typography variant="body2" gutterBottom>
                                <strong>Capabilities:</strong>
                              </Typography>
                              <Typography variant="body2">• Social media graphics</Typography>
                              <Typography variant="body2">• Blog featured images</Typography>
                              <Typography variant="body2">• Marketing visuals</Typography>
                              <Typography variant="body2">• Custom illustrations</Typography>
                              {plan.tier === 'pro' || plan.tier === 'enterprise' && (
                                <>
                                  <Typography variant="body2">• Video thumbnail generation</Typography>
                                  <Typography variant="body2">• Animated graphics</Typography>
                                </>
                              )}
                            </Box>
                          ))}
                        >
                          <InfoIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </ListItem>

                  {/* Audio/Video for Basic, Pro & Enterprise */}
                  {(plan.tier === 'basic' || plan.tier === 'pro' || plan.tier === 'enterprise') && (
                    <>
                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <AudioIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Audio Generation"
                          secondary={plan.tier === 'basic' 
                            ? "AI voice synthesis for podcasts, stories, and narration"
                            : "AI-powered audio content creation and voice synthesis"
                          }
                        />
                      </ListItem>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <VideoIcon color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary="Video Generation"
                          secondary={plan.tier === 'basic'
                            ? "Create AI videos for YouTube, social media, and stories"
                            : "AI video creation with script writing and editing"
                          }
                        />
                      </ListItem>
                    </>
                  )}

                  {/* Advanced Features for Higher Tiers */}
                  {plan.tier !== 'free' && (
                    <>
                      <Divider sx={{ my: 1 }} />
                      <Typography variant="caption" color="text.secondary" sx={{ px: 2 }}>
                        Support & Analytics:
                      </Typography>

                      <ListItem>
                        <ListItemIcon sx={{ minWidth: 24 }}>
                          <Support color="primary" fontSize="small" />
                        </ListItemIcon>
                        <ListItemText primary="Priority Support" />
                      </ListItem>

                      {plan.tier === 'pro' && (
                        <ListItem>
                          <ListItemIcon sx={{ minWidth: 24 }}>
                            <Analytics color="primary" fontSize="small" />
                          </ListItemIcon>
                          <ListItemText primary="Advanced Analytics & Insights" />
                        </ListItem>
                      )}

                      {plan.tier === 'enterprise' && (
                        <>
                          <ListItem>
                            <ListItemIcon sx={{ minWidth: 24 }}>
                              <Business color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary="Custom Integrations" />
                          </ListItem>
                          <ListItem>
                            <ListItemIcon sx={{ minWidth: 24 }}>
                              <Support color="primary" fontSize="small" />
                            </ListItemIcon>
                            <ListItemText primary="Dedicated Account Manager" />
                          </ListItem>
                        </>
                      )}
                    </>
                  )}

                  {/* Usage Limits - User-Friendly Display */}
                  <Divider sx={{ my: 1 }} />
                  <Typography variant="caption" color="text.secondary" sx={{ px: 2, fontWeight: 600 }}>
                    Monthly Usage Limits:
                  </Typography>

                  {/* For Basic tier, show unified AI text generation limit */}
                  {plan.tier === 'basic' && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <Psychology color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary="50 AI Text Generations"
                        secondary="~16-25 blog posts or ~25-50 social posts per month"
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: 500 } }}
                      />
                    </ListItem>
                  )}

                  {/* For other tiers, show provider-specific limits */}
                  {plan.tier !== 'basic' && (
                    <>
                      {plan.limits.gemini_calls > 0 && (
                        <ListItem>
                          <ListItemText
                            primary={`${plan.limits.gemini_calls === 0 ? '∞' : plan.limits.gemini_calls} Gemini AI calls`}
                            sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem' } }}
                          />
                        </ListItem>
                      )}
                      {plan.limits.openai_calls > 0 && (
                        <ListItem>
                          <ListItemText
                            primary={`${plan.limits.openai_calls === 0 ? '∞' : plan.limits.openai_calls} OpenAI calls`}
                            sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem' } }}
                          />
                        </ListItem>
                      )}
                    </>
                  )}

                  {/* Image Generation */}
                  {plan.limits.stability_calls > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <ImageIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${plan.limits.stability_calls} AI Images`}
                        secondary={plan.tier === 'basic' ? "Powered by open-source models (25% cost savings)" : undefined}
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: plan.tier === 'basic' ? 500 : 400 } }}
                      />
                    </ListItem>
                  )}

                  {/* Image Editing */}
                  {(plan.limits.image_edit_calls ?? 0) > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <Edit color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${plan.limits.image_edit_calls ?? 0} Image Edits`}
                        secondary={plan.tier === 'basic' ? "Background removal, inpainting, recolor (50% cost savings with OSS)" : undefined}
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: plan.tier === 'basic' ? 500 : 400 } }}
                      />
                    </ListItem>
                  )}

                  {/* Video Generation */}
                  {(plan.limits.video_calls ?? 0) > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <VideoIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${plan.limits.video_calls ?? 0} AI Videos`}
                        secondary={plan.tier === 'basic' ? "~5-6 full video projects (5 scenes each) per month" : undefined}
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: plan.tier === 'basic' ? 500 : 400 } }}
                      />
                    </ListItem>
                  )}

                  {/* Audio Generation */}
                  {(plan.limits.audio_calls ?? 0) > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <AudioIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${plan.limits.audio_calls ?? 0} Audio Generations`}
                        secondary={plan.tier === 'basic' ? "Podcast narration, story audio, voice synthesis" : undefined}
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: plan.tier === 'basic' ? 500 : 400 } }}
                      />
                    </ListItem>
                  )}

                  {/* Research Queries */}
                  {plan.limits.tavily_calls > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <SearchIcon color="primary" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`${plan.limits.tavily_calls} Research Searches`}
                        secondary="Web research, fact-checking, content discovery"
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem' } }}
                      />
                    </ListItem>
                  )}

                  {/* Cost Cap Protection */}
                  {plan.limits.monthly_cost > 0 && (
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: 24 }}>
                        <Verified color="success" fontSize="small" />
                      </ListItemIcon>
                      <ListItemText
                        primary={`$${plan.limits.monthly_cost} Monthly Cost Cap`}
                        secondary="Automatic protection - you'll never exceed this amount"
                        sx={{ '& .MuiListItemText-primary': { fontSize: '0.875rem', fontWeight: 500, color: 'success.main' } }}
                      />
                    </ListItem>
                  )}

                  {/* OSS Model Notice for Basic Tier */}
                  {plan.tier === 'basic' && (
                    <Box sx={{ mt: 1, p: 1.5, bgcolor: 'info.lighter', borderRadius: 1, mx: 2 }}>
                      <Typography variant="caption" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, fontWeight: 500 }}>
                        <StarIcon fontSize="small" sx={{ color: 'info.main' }} />
                        Powered by Open-Source AI Models
                      </Typography>
                      <Typography variant="caption" sx={{ display: 'block', mt: 0.5, color: 'text.secondary' }}>
                        We use cost-effective open-source models to give you more value. 25-50% savings vs proprietary models.
                      </Typography>
                    </Box>
                  )}
                </List>
              </CardContent>

              <CardActions sx={{ justifyContent: 'center', pb: 3, flexDirection: 'column', gap: 1 }}>
                {/* For alpha testing: Only Free and Basic are selectable, Pro/Enterprise disabled */}
                {plan.tier === 'pro' ? (
                  <Button
                    variant="outlined"
                    size="large"
                    fullWidth
                    disabled
                    sx={{ mb: 1 }}
                  >
                    Coming Soon
                  </Button>
                ) : plan.tier === 'enterprise' ? (
                  <Button
                    variant="outlined"
                    size="large"
                    fullWidth
                    disabled
                    sx={{ mb: 1 }}
                  >
                    Contact Sales
                  </Button>
                ) : (
                  <>
                    <Button
                      variant={selectedPlan === plan.id ? "outlined" : "contained"}
                      color={getPlanColor(plan.tier)}
                      size="large"
                      fullWidth
                      disabled={subscribing}
                      onClick={() => setSelectedPlan(plan.id)}
                      sx={{ mb: 1 }}
                    >
                      {selectedPlan === plan.id ? 'Selected' : 'Select Plan'}
                    </Button>

                    {selectedPlan === plan.id && (
                      <Button
                        variant="contained"
                        color="success"
                        size="large"
                        fullWidth
                        disabled={subscribing}
                        onClick={() => handleSubscribe(plan.id)}
                      >
                        {subscribing ? <CircularProgress size={20} /> : `Subscribe to ${plan.name}`}
                      </Button>
                    )}
                  </>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Box sx={{ textAlign: 'center', mt: 6 }}>
        <Typography variant="body2" color="text.secondary">
          All plans include our core AI content creation features.
          <br />
          Need a custom plan? <Button variant="text" size="small">Contact us</Button>
        </Typography>
      </Box>

      {/* Payment Modal */}
      <Modal
        open={paymentModalOpen}
        onClose={() => setPaymentModalOpen(false)}
        closeAfterTransition
        BackdropComponent={Backdrop}
        BackdropProps={{
          timeout: 500,
        }}
      >
        <Fade in={paymentModalOpen}>
          <Box sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 450,
            bgcolor: 'background.paper',
            border: '2px solid #000',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}>
            <Typography variant="h6" component="h2" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Warning sx={{ color: 'warning.main' }} />
              Alpha Testing Subscription
            </Typography>
            
            {/* Alpha Testing Notice */}
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                ⚠️ Alpha Testing Mode - No Payment Required
              </Typography>
              <Typography variant="caption" sx={{ display: 'block' }}>
                Payment integration is coming soon. For now, subscriptions are activated without charge.
              </Typography>
            </Alert>
            
            <Typography variant="body1" sx={{ mb: 2 }}>
              Thank you for participating in our alpha testing! We're crediting the Basic plan ($29 value) to your account.
            </Typography>
            
            {/* TODO: Payment Integration Notice */}
            <Box sx={{ 
              p: 2, 
              mb: 3, 
              bgcolor: 'info.lighter', 
              borderRadius: 1, 
              border: '1px solid',
              borderColor: 'info.light'
            }}>
              <Typography variant="body2" color="info.dark">
                <strong>Coming in Production:</strong>
              </Typography>
              <Typography variant="caption" color="info.dark" sx={{ display: 'block', mt: 0.5 }}>
                • Secure Stripe/PayPal payment processing<br />
                • Automatic renewal management<br />
                • Payment verification & receipts<br />
                • Upgrade/downgrade options
              </Typography>
            </Box>
            
            {/* Note: Current behavior allows renewal without payment verification */}
            {/* This is intentional for alpha testing but will be secured in production */}
            
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button onClick={() => setPaymentModalOpen(false)} variant="outlined">
                Cancel
              </Button>
              <Button
                variant="contained"
                onClick={handlePaymentConfirm}
                disabled={subscribing}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                  }
                }}
              >
                {subscribing ? <CircularProgress size={20} sx={{ color: 'white' }} /> : 'Confirm Subscription'}
              </Button>
            </Box>
          </Box>
        </Fade>
      </Modal>

      {/* Know More Modal */}
      <Dialog
        open={knowMoreModal.open}
        onClose={() => setKnowMoreModal({ open: false, title: '', content: null })}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>{knowMoreModal.title}</DialogTitle>
        <DialogContent>
          {knowMoreModal.content}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setKnowMoreModal({ open: false, title: '', content: null })}>
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Sign In Prompt Modal */}
      <Dialog
        open={showSignInPrompt}
        onClose={() => setShowSignInPrompt(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Sign In Required</DialogTitle>
        <DialogContent>
          <Typography variant="body1" sx={{ mb: 2 }}>
            Please sign in to subscribe to a plan and start using ALwrity.
          </Typography>
          <Typography variant="body2" color="text.secondary">
            If you don't have an account, signing in will automatically create one for you.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSignInPrompt(false)}>
            Cancel
          </Button>
          <Button 
            variant="contained" 
            onClick={() => {
              // Redirect to landing page which has sign-in
              window.location.href = '/';
            }}
          >
            Sign In
          </Button>
        </DialogActions>
      </Dialog>

      {/* Success Snackbar */}
      <Snackbar
        open={successSnackbar.open}
        autoHideDuration={3000}
        onClose={() => setSuccessSnackbar({ open: false, message: '', countdown: 0 })}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        sx={{ 
          top: { xs: 16, sm: 24 },
          '& .MuiSnackbarContent-root': {
            minWidth: { xs: '90vw', sm: '500px' }
          }
        }}
      >
        <Alert 
          severity="success" 
          variant="filled"
          onClose={() => setSuccessSnackbar({ open: false, message: '', countdown: 0 })}
          sx={{ 
            width: '100%',
            fontSize: '1rem',
            alignItems: 'center',
            boxShadow: '0 8px 24px rgba(76, 175, 80, 0.4)',
            '& .MuiAlert-icon': {
              fontSize: '2rem'
            }
          }}
        >
          {successSnackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default PricingPage;
