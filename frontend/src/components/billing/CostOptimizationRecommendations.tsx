import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Tooltip,
  Button,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import { ExpandMore } from '@mui/icons-material';
import { motion } from 'framer-motion';
import { 
  Lightbulb,
  TrendingDown,
  DollarSign,
  ArrowRight,
  Info,
  Sparkles
} from 'lucide-react';

// Types
import { UsageLog } from '../../types/billing';

// Services
import { billingService, formatCurrency } from '../../services/billingService';

interface CostOptimizationRecommendationsProps {
  userId?: string;
  terminalTheme?: boolean;
}

interface OptimizationRecommendation {
  id: string;
  title: string;
  description: string;
  potentialSavings: number;
  savingsPercentage: number;
  category: 'model_switch' | 'provider_switch' | 'usage_pattern' | 'efficiency';
  priority: 'high' | 'medium' | 'low';
  actionItems: string[];
  currentCost: number;
  recommendedCost: number;
}

const CostOptimizationRecommendations: React.FC<CostOptimizationRecommendationsProps> = ({ 
  userId,
  terminalTheme = false 
}) => {
  const [usageLogs, setUsageLogs] = useState<UsageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsageLogs = async () => {
      try {
        setLoading(true);
        setError(null);
        const currentDate = new Date();
        const billingPeriod = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
        const response = await billingService.getUsageLogs(1000, 0, undefined, undefined, billingPeriod);
        setUsageLogs(response.logs || []);
      } catch (err) {
        console.error('[CostOptimizationRecommendations] Error fetching usage logs:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch usage logs');
      } finally {
        setLoading(false);
      }
    };

    fetchUsageLogs();
  }, [userId]);

  // Analyze usage patterns and generate recommendations
  const recommendations = useMemo(() => {
    if (usageLogs.length === 0) return [];

    const recs: OptimizationRecommendation[] = [];

    // 1. Model Switch Recommendations
    // Analyze if user is using expensive models when cheaper alternatives exist
    const modelUsage = usageLogs.reduce((acc, log) => {
      if (!log.model_used || log.cost_total === 0) return acc;
      
      const key = `${log.provider}:${log.model_used}`;
      if (!acc[key]) {
        acc[key] = { cost: 0, calls: 0, tokens: 0 };
      }
      acc[key].cost += log.cost_total;
      acc[key].calls += 1;
      acc[key].tokens += log.tokens_total;
      return acc;
    }, {} as Record<string, { cost: number; calls: number; tokens: number }>);

    // Check for Gemini Pro usage when Flash could work
    const geminiProUsage = Object.entries(modelUsage).find(([key]) => 
      key.includes('gemini') && key.includes('pro') && !key.includes('flash')
    );
    if (geminiProUsage) {
      const [_, data] = geminiProUsage;
      // Estimate Flash cost (typically 10-20x cheaper)
      const estimatedFlashCost = data.cost * 0.1; // Conservative estimate
      const savings = data.cost - estimatedFlashCost;
      
      if (savings > 0.01) { // Only show if savings > $0.01
        recs.push({
          id: 'gemini-pro-to-flash',
          title: 'Switch Gemini Pro to Flash for Simple Tasks',
          description: `You're using Gemini Pro for ${data.calls} calls. Consider using Gemini Flash for simpler tasks - it's 10x cheaper with similar quality for most use cases.`,
          potentialSavings: savings,
          savingsPercentage: (savings / data.cost) * 100,
          category: 'model_switch',
          priority: 'high',
          actionItems: [
            'Use Gemini Flash for content generation',
            'Use Gemini Flash for simple Q&A',
            'Reserve Gemini Pro for complex reasoning tasks only'
          ],
          currentCost: data.cost,
          recommendedCost: estimatedFlashCost
        });
      }
    }

    // 2. Provider Cost Analysis
    const providerCosts = usageLogs.reduce((acc, log) => {
      if (log.cost_total === 0) return acc;
      if (!acc[log.provider]) {
        acc[log.provider] = { cost: 0, calls: 0, avgCostPerCall: 0 };
      }
      acc[log.provider].cost += log.cost_total;
      acc[log.provider].calls += 1;
      acc[log.provider].avgCostPerCall = acc[log.provider].cost / acc[log.provider].calls;
      return acc;
    }, {} as Record<string, { cost: number; calls: number; avgCostPerCall: number }>);

    // Find expensive providers
    const sortedProviders = Object.entries(providerCosts)
      .sort(([, a], [, b]) => b.avgCostPerCall - a.avgCostPerCall);

    if (sortedProviders.length > 1) {
      const [mostExpensive, secondMost] = sortedProviders;
      const [expensiveProvider, expensiveData] = mostExpensive;
      const [alternativeProvider, alternativeData] = secondMost;

      // If expensive provider has significantly higher cost per call
      if (expensiveData.avgCostPerCall > alternativeData.avgCostPerCall * 1.5 && expensiveData.calls > 10) {
        const estimatedAlternativeCost = expensiveData.calls * alternativeData.avgCostPerCall;
        const savings = expensiveData.cost - estimatedAlternativeCost;

        if (savings > 0.01) {
          recs.push({
            id: `provider-switch-${expensiveProvider}`,
            title: `Consider ${alternativeProvider} for Some Operations`,
            description: `${expensiveProvider} costs $${expensiveData.avgCostPerCall.toFixed(4)} per call on average, while ${alternativeProvider} costs $${alternativeData.avgCostPerCall.toFixed(4)}. Consider switching for non-critical operations.`,
            potentialSavings: savings,
            savingsPercentage: (savings / expensiveData.cost) * 100,
            category: 'provider_switch',
            priority: 'medium',
            actionItems: [
              `Use ${alternativeProvider} for batch operations`,
              `Reserve ${expensiveProvider} for high-priority tasks only`,
              'Review operation requirements to identify switchable tasks'
            ],
            currentCost: expensiveData.cost,
            recommendedCost: estimatedAlternativeCost
          });
        }
      }
    }

    // 3. Usage Pattern Analysis - High Token Usage
    const highTokenUsage = usageLogs.filter(log => 
      log.tokens_total > 10000 && log.cost_total > 0.01
    );

    if (highTokenUsage.length > 5) {
      const totalHighTokenCost = highTokenUsage.reduce((sum, log) => sum + log.cost_total, 0);
      const avgTokensPerCall = highTokenUsage.reduce((sum, log) => sum + log.tokens_total, 0) / highTokenUsage.length;
      
      recs.push({
        id: 'optimize-high-token-usage',
        title: 'Optimize High Token Usage Operations',
        description: `You have ${highTokenUsage.length} operations using >10K tokens each. Consider breaking down large requests or using more efficient prompts.`,
        potentialSavings: totalHighTokenCost * 0.15, // Estimate 15% savings
        savingsPercentage: 15,
        category: 'usage_pattern',
        priority: 'medium',
        actionItems: [
          'Break down large requests into smaller chunks',
          'Use more concise prompts',
          'Implement result caching for repeated queries',
          `Average tokens per call: ${Math.round(avgTokensPerCall).toLocaleString()}`
        ],
        currentCost: totalHighTokenCost,
        recommendedCost: totalHighTokenCost * 0.85
      });
    }

    // 4. Efficiency - Failed Requests
    const failedRequests = usageLogs.filter(log => log.status === 'failed' && log.cost_total > 0);
    if (failedRequests.length > 0) {
      const failedCost = failedRequests.reduce((sum, log) => sum + log.cost_total, 0);
      const failureRate = (failedRequests.length / usageLogs.length) * 100;

      if (failureRate > 5) { // More than 5% failure rate
        recs.push({
          id: 'reduce-failed-requests',
          title: 'Reduce Failed API Requests',
          description: `${failedRequests.length} requests failed (${failureRate.toFixed(1)}% failure rate), costing $${failedCost.toFixed(4)}. Improve error handling and retry logic.`,
          potentialSavings: failedCost * 0.8, // Can save 80% by preventing failures
          savingsPercentage: 80,
          category: 'efficiency',
          priority: 'high',
          actionItems: [
            'Review and fix error-prone operations',
            'Implement better retry logic',
            'Add input validation before API calls',
            'Monitor error patterns and address root causes'
          ],
          currentCost: failedCost,
          recommendedCost: failedCost * 0.2
        });
      }
    }

    // Sort by priority and potential savings
    return recs.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      }
      return b.potentialSavings - a.potentialSavings;
    });
  }, [usageLogs]);

  const totalPotentialSavings = recommendations.reduce((sum, rec) => sum + rec.potentialSavings, 0);
  const totalCurrentCost = usageLogs.reduce((sum, log) => sum + log.cost_total, 0);

  if (loading) {
    return (
      <Card sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2, color: 'rgba(255,255,255,0.7)' }}>
          Analyzing usage patterns...
        </Typography>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Card>
    );
  }

  if (recommendations.length === 0) {
    return (
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <Sparkles size={48} color="#22c55e" style={{ marginBottom: 16 }} />
          <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#ffffff', mb: 1 }}>
            Great Job!
          </Typography>
          <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.7)' }}>
            Your usage patterns are already optimized. No recommendations at this time.
          </Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
        }}
      >
        <CardContent sx={{ pb: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 'bold', color: '#ffffff' }}>
              <Lightbulb size={20} />
              Cost Optimization Recommendations
            </Typography>
            <Tooltip title="AI-powered suggestions to reduce your API costs">
              <Info size={16} color="rgba(255,255,255,0.7)" />
            </Tooltip>
          </Box>

          {/* Summary */}
          <Box 
            sx={{ 
              p: 2.5,
              mb: 3,
              background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(22, 163, 74, 0.1) 100%)',
              borderRadius: 2,
              border: '1px solid rgba(34, 197, 94, 0.3)',
              textAlign: 'center'
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
              <TrendingDown size={24} color="#22c55e" />
              <Typography variant="h5" sx={{ fontWeight: 'bold', color: '#22c55e' }}>
                {formatCurrency(totalPotentialSavings)}
              </Typography>
            </Box>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)', mb: 0.5 }}>
              Potential Monthly Savings
            </Typography>
            <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
              {recommendations.length} recommendation{recommendations.length !== 1 ? 's' : ''} • 
              {totalCurrentCost > 0 ? ` ${((totalPotentialSavings / totalCurrentCost) * 100).toFixed(1)}% of current spending` : ''}
            </Typography>
          </Box>
        </CardContent>

        <CardContent sx={{ pt: 0 }}>
          {/* Recommendations List */}
          {recommendations.map((rec, index) => (
            <Accordion
              key={rec.id}
              sx={{
                mb: 2,
                backgroundColor: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 2,
                '&:before': { display: 'none' },
                boxShadow: 'none'
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMore sx={{ color: 'rgba(255,255,255,0.7)' }} />}
                sx={{ px: 2, py: 1.5 }}
              >
                <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 2 }}>
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: 'bold', color: '#ffffff' }}>
                        {rec.title}
                      </Typography>
                      <Chip
                        label={rec.priority}
                        size="small"
                        sx={{
                          backgroundColor: rec.priority === 'high' ? 'rgba(239, 68, 68, 0.2)' : 
                                         rec.priority === 'medium' ? 'rgba(245, 158, 11, 0.2)' : 
                                         'rgba(100, 116, 139, 0.2)',
                          color: rec.priority === 'high' ? '#ef4444' : 
                                rec.priority === 'medium' ? '#f59e0b' : 
                                '#64748b',
                          fontWeight: 'bold',
                          fontSize: '0.7rem',
                          height: 20
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)', display: 'block' }}>
                      {rec.description}
                    </Typography>
                  </Box>
                  <Box sx={{ textAlign: 'right', minWidth: 120 }}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', color: '#22c55e' }}>
                      {formatCurrency(rec.potentialSavings)}
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                      {rec.savingsPercentage.toFixed(1)}% savings
                    </Typography>
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails sx={{ px: 2, pb: 2 }}>
                <Box sx={{ mb: 2 }}>
                  <Grid container spacing={2}>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, backgroundColor: 'rgba(239, 68, 68, 0.1)', borderRadius: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          Current Cost
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#ef4444' }}>
                          {formatCurrency(rec.currentCost)}
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Box sx={{ p: 1.5, backgroundColor: 'rgba(34, 197, 94, 0.1)', borderRadius: 1 }}>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.7)' }}>
                          Recommended Cost
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 'bold', color: '#22c55e' }}>
                          {formatCurrency(rec.recommendedCost)}
                        </Typography>
                      </Box>
                    </Grid>
                  </Grid>
                </Box>
                
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 1, color: '#ffffff' }}>
                  Action Items:
                </Typography>
                <Box component="ul" sx={{ m: 0, pl: 2 }}>
                  {rec.actionItems.map((item, idx) => (
                    <li key={idx}>
                      <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.8)', mb: 0.5 }}>
                        {item}
                      </Typography>
                    </li>
                  ))}
                </Box>
              </AccordionDetails>
            </Accordion>
          ))}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default CostOptimizationRecommendations;
