import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Alert,
  Paper
} from '@mui/material';
import {
  CreditCard,
  Warning,
  ArrowForward
} from '@mui/icons-material';

interface SubscriptionExpiredModalProps {
  open: boolean;
  onClose: () => void;
  onRenewSubscription: () => void;
  subscriptionData?: {
    plan?: string;
    tier?: string;
    limits?: any;
  } | null;
  errorData?: {
    provider?: string;
    usage_info?: any;
    message?: string;
  } | null;
}

const SubscriptionExpiredModal: React.FC<SubscriptionExpiredModalProps> = ({
  open,
  onClose,
  onRenewSubscription,
  subscriptionData,
  errorData
}) => {
  // Debug logging to verify modal state
  React.useEffect(() => {
    console.log('SubscriptionExpiredModal: State update', {
      open,
      errorData,
      hasUsageInfo: !!errorData?.usage_info,
      errorDataKeys: errorData ? Object.keys(errorData) : null
    });
    if (open) {
      console.log('SubscriptionExpiredModal: Modal should be visible now', {
        open,
        errorData,
        hasUsageInfo: !!errorData?.usage_info
      });
    } else {
      console.log('SubscriptionExpiredModal: Modal is closed');
    }
  }, [open, errorData]);
  
  const handleDialogClose = (_event: object, reason?: string) => {
    if (reason === 'backdropClick') {
      console.log('SubscriptionExpiredModal: Ignoring backdrop click close');
      return;
    }
    onClose();
  };

  const handleRenewClick = () => {
    onRenewSubscription();
    onClose();
  };

  return (
    <Dialog
      open={open}
      onClose={handleDialogClose}
      maxWidth="sm"
      fullWidth
      disableEscapeKeyDown
      PaperProps={{
        sx: {
          borderRadius: 3,
          background: 'linear-gradient(135deg, #fff 0%, #f8fafc 100%)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
          zIndex: 9999, // Ensure modal appears above everything
        }
      }}
      sx={{
        zIndex: 9999, // Ensure modal backdrop appears above everything
      }}
    >
      <DialogTitle sx={{ textAlign: 'center', pb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2 }}>
          <CreditCard sx={{ fontSize: 32, color: 'warning.main' }} />
          <Typography variant="h4" sx={{ fontWeight: 600, color: 'text.primary' }}>
            {errorData?.usage_info ? 'Usage Limit Reached' : 'Subscription Expired'}
          </Typography>
        </Box>
      </DialogTitle>
      
      <DialogContent sx={{ textAlign: 'center', px: 4, py: 2 }}>
        <Alert 
          severity="warning" 
          sx={{ 
            mb: 3, 
            borderRadius: 2,
            background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)',
            border: '1px solid #f59e0b'
          }}
          icon={<Warning sx={{ color: '#d97706' }} />}
        >
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#92400e' }}>
            {errorData?.usage_info ? 'You\'ve reached your API usage limit' : 'Your subscription has expired'}
          </Typography>
        </Alert>

        <Paper 
          elevation={0} 
          sx={{ 
            p: 3, 
            mb: 3, 
            background: 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)',
            border: '1px solid #cbd5e1',
            borderRadius: 2
          }}
        >
          {/* Main error message */}
          <Typography variant="body1" sx={{ mb: 2, color: 'text.secondary', lineHeight: 1.6 }}>
            {errorData?.message || (errorData?.usage_info 
              ? 'You\'ve reached your monthly usage limit for this plan. Upgrade your plan to get higher limits.'
              : 'To continue using Alwrity and access all features, you need to renew your subscription.'
            )}
          </Typography>
          
          {/* Detailed usage information */}
          {errorData?.usage_info && (
            <Box sx={{ mb: 2, p: 2.5, background: 'rgba(255,255,255,0.9)', borderRadius: 2, border: '1px solid #e2e8f0' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: 'text.primary', display: 'flex', alignItems: 'center', gap: 1 }}>
                <Warning sx={{ fontSize: 18, color: 'warning.main' }} />
                Usage Information:
              </Typography>
              
              {/* Provider and operation type */}
              <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                {errorData.provider && (
                  <Box sx={{ 
                    flex: '1 1 auto',
                    px: 2, 
                    py: 1.5, 
                    background: 'linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)', 
                    borderRadius: 1.5,
                    border: '1px solid #a5b4fc'
                  }}>
                    <Typography variant="caption" sx={{ color: '#4338ca', fontWeight: 600, display: 'block', mb: 0.5 }}>
                      Provider:
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#312e81', fontWeight: 700 }}>
                      {errorData.provider}
                    </Typography>
                  </Box>
                )}
                
                {errorData.usage_info.operation_type && (
                  <Box sx={{ 
                    flex: '1 1 auto',
                    px: 2, 
                    py: 1.5, 
                    background: 'linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)', 
                    borderRadius: 1.5,
                    border: '1px solid #fbbf24'
                  }}>
                    <Typography variant="caption" sx={{ color: '#92400e', fontWeight: 600, display: 'block', mb: 0.5 }}>
                      Operation:
                    </Typography>
                    <Typography variant="body2" sx={{ color: '#78350f', fontWeight: 700, textTransform: 'capitalize' }}>
                      {errorData.usage_info.operation_type.replace(/_/g, ' ')}
                    </Typography>
                  </Box>
                )}
              </Box>
              
              {/* Token usage details (if available) */}
              {(errorData.usage_info.current_tokens !== undefined || errorData.usage_info.current_calls !== undefined) && (
                <Box sx={{ 
                  p: 2, 
                  background: 'linear-gradient(135deg, #fee2e2 0%, #fecaca 100%)', 
                  borderRadius: 1.5,
                  border: '1px solid #f87171',
                  mb: 2
                }}>
                  {errorData.usage_info.current_tokens !== undefined && (
                    <>
                      <Typography variant="body2" sx={{ color: '#7f1d1d', fontWeight: 600, mb: 1 }}>
                        Token Usage:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1, mb: 0.5 }}>
                        <Typography variant="h6" sx={{ color: '#991b1b', fontWeight: 700 }}>
                          {errorData.usage_info.current_tokens?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#7f1d1d' }}>
                          / {errorData.usage_info.limit?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#7f1d1d', ml: 'auto' }}>
                          ({((errorData.usage_info.current_tokens / errorData.usage_info.limit) * 100).toFixed(1)}% used)
                        </Typography>
                      </Box>
                      
                      {errorData.usage_info.requested_tokens && (
                        <Typography variant="caption" sx={{ color: '#7f1d1d', display: 'block', mt: 1 }}>
                          Requested: {errorData.usage_info.requested_tokens.toLocaleString()} tokens
                          {errorData.usage_info.current_tokens + errorData.usage_info.requested_tokens > errorData.usage_info.limit && (
                            <span style={{ fontWeight: 700, marginLeft: 4 }}>
                              (Would exceed by: {((errorData.usage_info.current_tokens + errorData.usage_info.requested_tokens) - errorData.usage_info.limit).toLocaleString()} tokens)
                            </span>
                          )}
                        </Typography>
                      )}
                    </>
                  )}
                  
                  {errorData.usage_info.current_calls !== undefined && (
                    <>
                      <Typography variant="body2" sx={{ color: '#7f1d1d', fontWeight: 600, mb: 1, mt: errorData.usage_info.current_tokens !== undefined ? 2 : 0 }}>
                        API Call Usage:
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 1 }}>
                        <Typography variant="h6" sx={{ color: '#991b1b', fontWeight: 700 }}>
                          {errorData.usage_info.current_calls?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="body2" sx={{ color: '#7f1d1d' }}>
                          / {errorData.usage_info.call_limit?.toLocaleString() || 0}
                        </Typography>
                        <Typography variant="caption" sx={{ color: '#7f1d1d', ml: 'auto' }}>
                          ({((errorData.usage_info.current_calls / errorData.usage_info.call_limit) * 100).toFixed(1)}% used)
                        </Typography>
                      </Box>
                    </>
                  )}
                </Box>
              )}
              
              {/* Error type badge */}
              {errorData.usage_info.error_type && (
                <Box sx={{ display: 'flex', justifyContent: 'center' }}>
                  <Box sx={{ 
                    px: 2, 
                    py: 0.5, 
                    background: '#dc2626', 
                    borderRadius: 1,
                    display: 'inline-block'
                  }}>
                    <Typography variant="caption" sx={{ color: 'white', fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                      {errorData.usage_info.error_type.replace(/_/g, ' ')}
                    </Typography>
                  </Box>
                </Box>
              )}
            </Box>
          )}
          
          {/* Current plan information */}
          {subscriptionData && (
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 2, flexWrap: 'wrap' }}>
              {subscriptionData.plan && (
                <Box sx={{ 
                  px: 3, 
                  py: 1.5, 
                  background: 'rgba(255,255,255,0.9)', 
                  borderRadius: 1.5,
                  border: '2px solid #e2e8f0'
                }}>
                  <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600, display: 'block', mb: 0.5 }}>
                    Current Plan:
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'text.primary', fontWeight: 700, textTransform: 'capitalize' }}>
                    {subscriptionData.plan}
                  </Typography>
                </Box>
              )}
            </Box>
          )}
        </Paper>

        <Typography variant="body2" sx={{ color: 'text.secondary', mb: 1 }}>
          Renewing your subscription will restore access to:
        </Typography>
        
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, textAlign: 'left', maxWidth: 300, mx: 'auto' }}>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            ✓ AI Content Generation
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            ✓ Website Analysis
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            ✓ Research Tools
          </Typography>
          <Typography variant="body2" sx={{ color: 'text.secondary' }}>
            ✓ All Premium Features
          </Typography>
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 4, pb: 4, gap: 2 }}>
        <Button
          variant="outlined"
          onClick={onClose}
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 600,
            px: 3,
            py: 1.5,
            borderColor: 'rgba(0,0,0,0.2)',
            color: 'text.primary',
            '&:hover': {
              borderColor: 'rgba(0,0,0,0.4)',
              background: 'rgba(0,0,0,0.04)',
            }
          }}
        >
          Maybe Later
        </Button>
        
        <Button
          variant="contained"
          onClick={handleRenewClick}
          startIcon={<CreditCard />}
          endIcon={<ArrowForward />}
          sx={{
            borderRadius: 2,
            textTransform: 'none',
            fontWeight: 600,
            px: 4,
            py: 1.5,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
              transform: 'translateY(-1px)',
              boxShadow: '0 6px 16px rgba(102, 126, 234, 0.4)',
            }
          }}
        >
          Renew Subscription
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default SubscriptionExpiredModal;
