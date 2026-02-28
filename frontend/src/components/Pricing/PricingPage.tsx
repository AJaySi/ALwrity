import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Switch,
  FormControlLabel,
  Alert,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Modal,
  Fade,
  Backdrop,
  Snackbar,
} from '@mui/material';
import { Warning } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../../api/client';
import { restoreNavigationState, saveCurrentPhaseForTool } from '../../utils/navigationState';
import PlanCard from './PricingPage/PlanCard';

export interface SubscriptionPlan {
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

    // Get selected plan details
    const plan = plans.find(p => p.id === selectedPlan);
    if (!plan) return;

    try {
      setSubscribing(true);
      const userId = localStorage.getItem('user_id') || 'anonymous';

      // Check if Stripe is configured
      if (process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY) {
        console.log('[PricingPage] Initiating Stripe Checkout');

        const response = await apiClient.post('/api/subscription/create-checkout-session', {
          tier: plan.tier,
          billing_cycle: yearlyBilling ? 'yearly' : 'monthly',
          success_url: `${window.location.origin}/dashboard?subscription=success`,
          cancel_url: `${window.location.origin}/pricing?subscription=cancel`,
        });

        if (response.data.url) {
          window.location.href = response.data.url;
          return;
        }
      }

      console.log('[PricingPage] Making legacy subscription API call:', {
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
            <PlanCard
              plan={plan}
              yearlyBilling={yearlyBilling}
              selectedPlanId={selectedPlan}
              subscribing={subscribing}
              onSelectPlan={setSelectedPlan}
              onSubscribe={handleSubscribe}
              openKnowMoreModal={openKnowMoreModal}
            />
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
