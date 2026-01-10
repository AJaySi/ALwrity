/**
 * Blog Writer Cost Alerts Integration
 * 
 * Example integration of Priority 2 alerts (cost estimation, trends, OSS recommendations)
 * into the Blog Writer component.
 */

import React, { useEffect } from 'react';
import { Box, Alert, AlertTitle, Button, Collapse } from '@mui/material';
import { usePriority2Alerts, useCostEstimationAlert } from '../../../hooks/usePriority2Alerts';
import Priority2AlertBanner from '../../shared/Priority2AlertBanner';
import { useSubscription } from '../../../contexts/SubscriptionContext';
import { checkPreflight, PreflightOperation } from '../../../services/billingService';
import { showToastNotification } from '../../../utils/toastNotifications';

interface BlogWriterCostAlertsProps {
  userId?: string;
  onResearchStart?: () => void;
  onOutlineStart?: () => void;
  onContentStart?: () => void;
}

/**
 * Blog Writer Cost Alerts Component
 * 
 * Displays Priority 2 alerts and provides cost estimation before operations.
 * Integrates with Blog Writer's research, outline, and content generation workflows.
 */
export const BlogWriterCostAlerts: React.FC<BlogWriterCostAlertsProps> = ({
  userId,
  onResearchStart,
  onOutlineStart,
  onContentStart,
}) => {
  const { subscription } = useSubscription();
  const { alerts, refreshAlerts, dismissAlert } = usePriority2Alerts({
    userId,
    enabled: !!userId && subscription?.active,
    checkInterval: 120000, // Check every 2 minutes
  });

  const { showEstimationAlert } = useCostEstimationAlert();

  // Estimate cost for blog generation workflow
  const estimateBlogWorkflowCost = async (workflowType: 'research' | 'outline' | 'content') => {
    if (!userId) return;

    try {
      const operations: PreflightOperation[] = [];

      if (workflowType === 'research') {
        // Research typically involves: 3-5 Exa searches + 1 LLM call for analysis
        operations.push(
          {
            provider: 'exa',
            operation_type: 'research',
            tokens_requested: 0,
          },
          {
            provider: 'gemini',
            model: 'gemini-2.5-flash',
            operation_type: 'research',
            tokens_requested: 2000, // Estimated tokens for research analysis
          }
        );
      } else if (workflowType === 'outline') {
        // Outline generation: 1 LLM call
        operations.push({
          provider: 'gemini',
          model: 'gemini-2.5-flash',
          operation_type: 'outline_generation',
          tokens_requested: 1500, // Estimated tokens for outline
        });
      } else if (workflowType === 'content') {
        // Content generation: 2-3 LLM calls (one per section typically)
        operations.push(
          {
            provider: 'gemini',
            model: 'gemini-2.5-flash',
            operation_type: 'content_generation',
            tokens_requested: 3000, // Estimated tokens per section
          },
          {
            provider: 'gemini',
            model: 'gemini-2.5-flash',
            operation_type: 'content_generation',
            tokens_requested: 3000,
          }
        );
      }

      const preflightResult = await checkPreflight(operations[0]); // Check first operation
      const estimatedCost = preflightResult.estimated_cost || 0;

      if (estimatedCost > 0.01) {
        showEstimationAlert(
          estimatedCost,
          `${workflowType} generation`,
          () => {
            // User confirmed - proceed with operation
            if (workflowType === 'research' && onResearchStart) {
              onResearchStart();
            } else if (workflowType === 'outline' && onOutlineStart) {
              onOutlineStart();
            } else if (workflowType === 'content' && onContentStart) {
              onContentStart();
            }
          },
          () => {
            showToastNotification('Operation cancelled', 'info');
          }
        );
      }
    } catch (error) {
      console.error('[BlogWriterCostAlerts] Error estimating cost:', error);
      // Don't block operation on estimation failure
    }
  };

  // Filter alerts relevant to Blog Writer
  const blogWriterAlerts = alerts.filter(alert => 
    alert.type === 'cost_trend' || 
    alert.type === 'oss_recommendation' ||
    (alert.type === 'cost_estimation' && alert.message.includes('blog'))
  );

  return (
    <Box sx={{ mb: 2 }}>
      {/* Priority 2 Alert Banner */}
      {blogWriterAlerts.length > 0 && (
        <Priority2AlertBanner
          alerts={blogWriterAlerts}
          onDismiss={dismissAlert}
          maxAlerts={2}
        />
      )}

      {/* Cost Estimation Info Alert */}
      <Collapse in={blogWriterAlerts.length === 0}>
        <Alert 
          severity="info" 
          icon={<></>}
          sx={{ 
            mb: 2,
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.2)',
          }}
        >
          <AlertTitle sx={{ fontWeight: 'bold', mb: 0.5 }}>
            💡 Cost Transparency
          </AlertTitle>
          <Box sx={{ fontSize: '0.875rem' }}>
            Blog generation typically costs:
            <ul style={{ margin: '8px 0', paddingLeft: '20px' }}>
              <li><strong>Research</strong>: ~$0.01-0.02 (3-5 searches + analysis)</li>
              <li><strong>Outline</strong>: ~$0.005-0.01 (1 LLM call)</li>
              <li><strong>Content</strong>: ~$0.01-0.03 (2-3 LLM calls per section)</li>
            </ul>
            <strong>Total per blog</strong>: ~$0.03-0.06 (using OSS models)
          </Box>
        </Alert>
      </Collapse>
    </Box>
  );
};

/**
 * Hook for Blog Writer cost estimation
 * Use this in Blog Writer components before triggering operations
 */
export const useBlogWriterCostEstimation = () => {
  const { showEstimationAlert } = useCostEstimationAlert();

  const estimateAndProceed = async (
    workflowType: 'research' | 'outline' | 'content',
    onProceed: () => void,
    userId?: string
  ) => {
    if (!userId) {
      // No user ID - proceed without estimation
      onProceed();
      return;
    }

    try {
      const operations: PreflightOperation[] = [];

      // Define operations based on workflow type
      if (workflowType === 'research') {
        operations.push(
          { provider: 'exa', operation_type: 'research', tokens_requested: 0 },
          { 
            provider: 'gemini', 
            model: 'gemini-2.5-flash',
            operation_type: 'research', 
            tokens_requested: 2000 
          }
        );
      } else if (workflowType === 'outline') {
        operations.push({
          provider: 'gemini',
          model: 'gemini-2.5-flash',
          operation_type: 'outline_generation',
          tokens_requested: 1500,
        });
      } else if (workflowType === 'content') {
        operations.push(
          {
            provider: 'gemini',
            model: 'gemini-2.5-flash',
            operation_type: 'content_generation',
            tokens_requested: 3000,
          }
        );
      }

      if (operations.length > 0) {
        const preflightResult = await checkPreflight(operations[0]);
        const estimatedCost = preflightResult.estimated_cost || 0;

        if (estimatedCost > 0.01) {
          showEstimationAlert(
            estimatedCost,
            `${workflowType} generation`,
            onProceed,
            () => showToastNotification('Operation cancelled', 'info')
          );
        } else {
          // Low cost - proceed directly
          onProceed();
        }
      } else {
        onProceed();
      }
    } catch (error) {
      console.error('[BlogWriterCostEstimation] Error:', error);
      // On error, proceed anyway (don't block user)
      onProceed();
    }
  };

  return { estimateAndProceed };
};

export default BlogWriterCostAlerts;
