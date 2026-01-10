import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Chip,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import { 
  DollarSign,
  Info,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

// Types
import { PreflightCheckResponse, PreflightOperation } from '../../services/billingService';

// Services
import { billingService, formatCurrency, checkPreflightBatch } from '../../services/billingService';

interface CostEstimationModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  operations: PreflightOperation[];
  userId?: string;
}

const CostEstimationModal: React.FC<CostEstimationModalProps> = ({
  open,
  onClose,
  onConfirm,
  operations,
  userId
}) => {
  const [estimation, setEstimation] = useState<PreflightCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open && operations.length > 0) {
      fetchEstimation();
    } else {
      setEstimation(null);
      setError(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, JSON.stringify(operations)]);

  const fetchEstimation = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await checkPreflightBatch(operations);
      setEstimation(result);
    } catch (err) {
      console.error('[CostEstimationModal] Error fetching estimation:', err);
      setError(err instanceof Error ? err.message : 'Failed to estimate costs');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    if (estimation?.can_proceed) {
      onConfirm();
      onClose();
    }
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose}
      maxWidth="sm"
      fullWidth
      PaperProps={{
        sx: {
          background: 'linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(255,255,255,0.98) 100%)',
          borderRadius: 3,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
        }
      }}
    >
      <DialogTitle sx={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: 1.5,
        pb: 1,
        borderBottom: '1px solid rgba(0,0,0,0.1)'
      }}>
        <DollarSign size={24} color="#667eea" />
        <Box sx={{ flex: 1 }}>
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
            Cost Estimation
          </Typography>
          <Typography variant="caption" sx={{ color: '#64748b' }}>
            Estimated cost for this operation
          </Typography>
        </Box>
      </DialogTitle>

      <DialogContent sx={{ pt: 3 }}>
        {loading && (
          <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', py: 4 }}>
            <CircularProgress size={40} sx={{ color: '#667eea', mb: 2 }} />
            <Typography variant="body2" sx={{ color: '#64748b' }}>
              Calculating estimated costs...
            </Typography>
          </Box>
        )}

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {estimation && !loading && (
          <>
            {/* Overall Estimation */}
            <Box 
              sx={{ 
                p: 2.5,
                mb: 3,
                background: estimation.can_proceed 
                  ? 'linear-gradient(135deg, rgba(34, 197, 94, 0.1) 0%, rgba(22, 163, 74, 0.05) 100%)'
                  : 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%)',
                borderRadius: 2,
                border: `2px solid ${estimation.can_proceed ? '#22c55e' : '#ef4444'}`,
                textAlign: 'center'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                {estimation.can_proceed ? (
                  <CheckCircle size={24} color="#22c55e" />
                ) : (
                  <AlertTriangle size={24} color="#ef4444" />
                )}
                <Typography variant="h5" sx={{ fontWeight: 'bold', color: estimation.can_proceed ? '#22c55e' : '#ef4444' }}>
                  {formatCurrency(estimation.total_cost)}
                </Typography>
              </Box>
              <Typography variant="body2" sx={{ color: '#64748b', mb: 1 }}>
                Estimated Total Cost
              </Typography>
              {!estimation.can_proceed && (
                <Alert severity="error" sx={{ mt: 1 }}>
                  This operation cannot proceed. {estimation.operations.find(op => !op.allowed)?.message || 'Limit exceeded'}
                </Alert>
              )}
            </Box>

            {/* Operation Breakdown */}
            <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 2, color: '#1e293b' }}>
              Operation Breakdown
            </Typography>
            
            <Grid container spacing={2} sx={{ mb: 2 }}>
              {estimation.operations.map((op, index) => (
                <Grid item xs={12} key={index}>
                  <Box
                    sx={{
                      p: 2,
                      backgroundColor: op.allowed ? 'rgba(34, 197, 94, 0.05)' : 'rgba(239, 68, 68, 0.05)',
                      borderRadius: 2,
                      border: `1px solid ${op.allowed ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)'}`
                    }}
                  >
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                        {op.provider}
                      </Typography>
                      <Chip
                        label={op.allowed ? 'Allowed' : 'Blocked'}
                        size="small"
                        sx={{
                          backgroundColor: op.allowed ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                          color: op.allowed ? '#22c55e' : '#ef4444',
                          fontWeight: 'bold'
                        }}
                      />
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        Operation:
                      </Typography>
                      <Typography variant="caption" sx={{ fontWeight: 500, color: '#1e293b' }}>
                        {op.operation_type}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" sx={{ color: '#64748b' }}>
                        Estimated Cost:
                      </Typography>
                      <Typography variant="caption" sx={{ fontWeight: 'bold', color: '#667eea' }}>
                        {formatCurrency(op.cost)}
                      </Typography>
                    </Box>
                    {op.limit_info && (
                      <Box sx={{ mt: 1, pt: 1, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                        <Typography variant="caption" sx={{ color: '#64748b' }}>
                          Usage: {op.limit_info.current_usage} / {op.limit_info.limit} 
                          ({((op.limit_info.current_usage / op.limit_info.limit) * 100).toFixed(1)}%)
                        </Typography>
                      </Box>
                    )}
                    {op.message && (
                      <Typography variant="caption" sx={{ color: op.allowed ? '#22c55e' : '#ef4444', display: 'block', mt: 0.5 }}>
                        {op.message}
                      </Typography>
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>

            {/* Usage Summary */}
            {estimation.usage_summary && (
              <>
                <Divider sx={{ my: 2 }} />
                <Box sx={{ p: 2, backgroundColor: 'rgba(102, 126, 234, 0.05)', borderRadius: 2 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: '#1e293b' }}>
                    Current Usage Summary
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      Current Calls:
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                      {estimation.usage_summary.current_calls}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      Limit:
                    </Typography>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#1e293b' }}>
                      {estimation.usage_summary.limit}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" sx={{ color: '#64748b' }}>
                      Remaining:
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        fontWeight: 'bold',
                        color: estimation.usage_summary.remaining > 0 ? '#22c55e' : '#ef4444'
                      }}
                    >
                      {estimation.usage_summary.remaining}
                    </Typography>
                  </Box>
                </Box>
              </>
            )}

            {/* Info Note */}
            <Box sx={{ mt: 2, p: 1.5, backgroundColor: 'rgba(59, 130, 246, 0.05)', borderRadius: 1 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Info size={16} color="#3b82f6" style={{ marginTop: 2 }} />
                <Typography variant="caption" sx={{ color: '#64748b' }}>
                  This is an estimate. Actual costs may vary based on token usage and API response length.
                </Typography>
              </Box>
            </Box>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2, borderTop: '1px solid rgba(0,0,0,0.1)' }}>
        <Button onClick={onClose} sx={{ color: '#64748b' }}>
          Cancel
        </Button>
        <Button
          onClick={handleConfirm}
          variant="contained"
          disabled={loading || !estimation?.can_proceed}
          sx={{
            background: estimation?.can_proceed 
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : 'rgba(100, 116, 139, 0.3)',
            '&:hover': {
              background: estimation?.can_proceed 
                ? 'linear-gradient(135deg, #5568d3 0%, #6b3d91 100%)'
                : 'rgba(100, 116, 139, 0.3)'
            }
          }}
        >
          {loading ? 'Calculating...' : estimation?.can_proceed ? 'Proceed' : 'Cannot Proceed'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default CostEstimationModal;
