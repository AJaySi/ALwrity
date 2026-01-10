import React, { useState, useEffect, useMemo } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
  Tooltip,
  CircularProgress,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  FileText,
  Image as ImageIcon,
  Video,
  Search,
  Mic,
  Code
} from 'lucide-react';

// Types
import { UsageLog } from '../../types/billing';

// Services
import { billingService } from '../../services/billingService';
import { formatCurrency, formatNumber } from '../../services/billingService';

interface ToolCostBreakdownProps {
  userId?: string;
  terminalTheme?: boolean;
}

// Map endpoints to tool names
const endpointToTool = (endpoint: string): string => {
  const endpointLower = endpoint.toLowerCase();
  
  if (endpointLower.includes('blog') || endpointLower.includes('blog-writer')) {
    return 'Blog Writer';
  }
  if (endpointLower.includes('story') || endpointLower.includes('story-writer')) {
    return 'Story Writer';
  }
  if (endpointLower.includes('podcast') || endpointLower.includes('podcast-maker')) {
    return 'Podcast Maker';
  }
  if (endpointLower.includes('image') || endpointLower.includes('image-studio')) {
    return 'Image Studio';
  }
  if (endpointLower.includes('video') || endpointLower.includes('video-studio')) {
    return 'Video Studio';
  }
  if (endpointLower.includes('research') || endpointLower.includes('researcher')) {
    return 'Research Tools';
  }
  if (endpointLower.includes('linkedin')) {
    return 'LinkedIn Writer';
  }
  if (endpointLower.includes('facebook')) {
    return 'Facebook Writer';
  }
  if (endpointLower.includes('seo')) {
    return 'SEO Tools';
  }
  if (endpointLower.includes('audio') || endpointLower.includes('tts')) {
    return 'Audio Generation';
  }
  
  return 'Other';
};

const getToolIcon = (tool: string) => {
  const toolLower = tool.toLowerCase();
  if (toolLower.includes('blog')) return <FileText size={18} />;
  if (toolLower.includes('story')) return <FileText size={18} />;
  if (toolLower.includes('podcast')) return <Mic size={18} />;
  if (toolLower.includes('image')) return <ImageIcon size={18} />;
  if (toolLower.includes('video')) return <Video size={18} />;
  if (toolLower.includes('research')) return <Search size={18} />;
  if (toolLower.includes('audio')) return <Mic size={18} />;
  return <Code size={18} />;
};

const ToolCostBreakdown: React.FC<ToolCostBreakdownProps> = ({ userId, terminalTheme = false }) => {
  const [usageLogs, setUsageLogs] = useState<UsageLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchUsageLogs = async () => {
      try {
        setLoading(true);
        setError(null);
        // Get current billing period
        const currentDate = new Date();
        const billingPeriod = `${currentDate.getFullYear()}-${String(currentDate.getMonth() + 1).padStart(2, '0')}`;
        
        // Fetch usage logs with high limit to get comprehensive data
        const response = await billingService.getUsageLogs(1000, 0, undefined, undefined, billingPeriod);
        setUsageLogs(response.logs || []);
      } catch (err) {
        console.error('[ToolCostBreakdown] Error fetching usage logs:', err);
        setError(err instanceof Error ? err.message : 'Failed to fetch usage logs');
      } finally {
        setLoading(false);
      }
    };

    fetchUsageLogs();
  }, [userId]);

  const toolCosts = useMemo(() => {
    const grouped = usageLogs.reduce((acc, log) => {
      const tool = endpointToTool(log.endpoint || '');
      if (!acc[tool]) {
        acc[tool] = { cost: 0, calls: 0, tokens: 0 };
      }
      acc[tool].cost += log.cost_total || 0;
      acc[tool].calls += 1;
      acc[tool].tokens += log.tokens_total || 0;
      return acc;
    }, {} as Record<string, { cost: number; calls: number; tokens: number }>);
    
    return Object.entries(grouped)
      .map(([tool, data]) => ({
        tool,
        ...data
      }))
      .sort((a, b) => b.cost - a.cost)
      .filter(item => item.cost > 0); // Only show tools with costs
  }, [usageLogs]);

  const totalCost = toolCosts.reduce((sum, item) => sum + item.cost, 0);

  if (loading) {
    return (
      <Card sx={{ 
        background: terminalTheme 
          ? 'transparent'
          : 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        border: terminalTheme ? '1px solid #00ff00' : '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3
      }}>
        <CardContent sx={{ textAlign: 'center', py: 4 }}>
          <CircularProgress size={24} sx={{ color: terminalTheme ? '#00ff00' : undefined }} />
          <Typography sx={{ mt: 2, color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.8)' }}>
            Loading tool costs...
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card sx={{ 
        background: terminalTheme 
          ? 'transparent'
          : 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        border: terminalTheme ? '1px solid #ff0000' : '1px solid rgba(255,107,107,0.3)',
        borderRadius: 3
      }}>
        <CardContent sx={{ textAlign: 'center', py: 2 }}>
          <Typography sx={{ color: terminalTheme ? '#ff0000' : '#ff6b6b', fontSize: '0.875rem' }}>
            {error}
          </Typography>
        </CardContent>
      </Card>
    );
  }

  if (toolCosts.length === 0) {
    return (
      <Card sx={{ 
        background: terminalTheme 
          ? 'transparent'
          : 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        border: terminalTheme ? `1px solid ${terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.1)'}` : '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2, color: terminalTheme ? '#00ff00' : '#ffffff', fontWeight: 'bold' }}>
            Cost by Tool
          </Typography>
          <Typography sx={{ color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.7)', fontSize: '0.875rem' }}>
            No usage data available yet. Costs will appear here as you use different tools.
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
      <Card sx={{ 
        height: '100%',
        background: terminalTheme 
          ? 'transparent'
          : 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
        backdropFilter: terminalTheme ? 'none' : 'blur(10px)',
        border: terminalTheme ? '1px solid #00ff00' : '1px solid rgba(255,255,255,0.1)',
        borderRadius: 3,
        position: 'relative',
        overflow: 'hidden'
      }}>
        <CardContent>
          <Typography variant="h6" sx={{ 
            mb: 3, 
            color: terminalTheme ? '#00ff00' : '#ffffff', 
            fontWeight: 'bold',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}>
            <Code size={20} />
            Cost by Tool
          </Typography>

          <Grid container spacing={2}>
            {toolCosts.map((item, index) => {
              const percentage = totalCost > 0 ? ((item.cost / totalCost) * 100).toFixed(1) : '0';
              
              return (
                <Grid item xs={12} sm={6} key={item.tool}>
                  <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                  >
                    <Tooltip 
                      title={
                        <Box>
                          <Typography variant="subtitle2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                            {item.tool} Usage
                          </Typography>
                          <Typography variant="body2">
                            Cost: {formatCurrency(item.cost)} ({percentage}%)
                          </Typography>
                          <Typography variant="body2">
                            Calls: {formatNumber(item.calls)}
                          </Typography>
                          <Typography variant="body2">
                            Tokens: {formatNumber(item.tokens)}
                          </Typography>
                          <Typography variant="caption" sx={{ mt: 1, display: 'block', opacity: 0.8 }}>
                            Avg cost per call: {formatCurrency(item.cost / item.calls)}
                          </Typography>
                        </Box>
                      }
                      arrow
                      placement="top"
                    >
                      <Box
                        sx={{
                          p: 2,
                          backgroundColor: terminalTheme 
                            ? 'rgba(0, 255, 0, 0.05)'
                            : 'rgba(255,255,255,0.05)',
                          borderRadius: 2,
                          border: terminalTheme 
                            ? '1px solid rgba(0, 255, 0, 0.2)'
                            : '1px solid rgba(255,255,255,0.1)',
                          position: 'relative',
                          cursor: 'help',
                          transition: 'all 0.2s ease',
                          '&:hover': {
                            transform: 'translateY(-2px)',
                            backgroundColor: terminalTheme 
                              ? 'rgba(0, 255, 0, 0.1)'
                              : 'rgba(255,255,255,0.08)',
                            border: terminalTheme 
                              ? '1px solid rgba(0, 255, 0, 0.4)'
                              : '1px solid rgba(255,255,255,0.2)'
                          }
                        }}
                      >
                        {/* Tool Header */}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5 }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ color: terminalTheme ? '#00ff00' : '#ffffff' }}>
                              {getToolIcon(item.tool)}
                            </Box>
                            <Typography variant="body2" sx={{ fontWeight: 'bold', color: terminalTheme ? '#00ff00' : '#ffffff' }}>
                              {item.tool}
                            </Typography>
                          </Box>
                          <Chip
                            label={`${percentage}%`}
                            size="small"
                            sx={{
                              backgroundColor: terminalTheme 
                                ? 'rgba(0, 255, 0, 0.2)'
                                : 'rgba(74, 222, 128, 0.2)',
                              color: terminalTheme ? '#00ff00' : '#4ade80',
                              fontWeight: 'bold',
                              border: terminalTheme 
                                ? '1px solid rgba(0, 255, 0, 0.3)'
                                : '1px solid rgba(74, 222, 128, 0.3)'
                            }}
                          />
                        </Box>

                        {/* Metrics */}
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" sx={{ color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.7)' }}>
                            Cost:
                          </Typography>
                          <Typography variant="caption" sx={{ fontWeight: 'bold', color: terminalTheme ? '#00ff00' : '#ffffff' }}>
                            {formatCurrency(item.cost)}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" sx={{ color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.7)' }}>
                            Calls:
                          </Typography>
                          <Typography variant="caption" sx={{ fontWeight: 'bold', color: terminalTheme ? '#00ff00' : '#ffffff' }}>
                            {formatNumber(item.calls)}
                          </Typography>
                        </Box>
                        
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="caption" sx={{ color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.7)' }}>
                            Tokens:
                          </Typography>
                          <Typography variant="caption" sx={{ fontWeight: 'bold', color: terminalTheme ? '#00ff00' : '#ffffff' }}>
                            {formatNumber(item.tokens)}
                          </Typography>
                        </Box>

                        {/* Progress bar */}
                        <Box sx={{ mt: 1 }}>
                          <Box
                            sx={{
                              height: 4,
                              backgroundColor: terminalTheme 
                                ? 'rgba(0, 255, 0, 0.1)'
                                : 'rgba(255,255,255,0.1)',
                              borderRadius: 2,
                              overflow: 'hidden'
                            }}
                          >
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${percentage}%` }}
                              transition={{ duration: 1, delay: index * 0.1 }}
                              style={{
                                height: '100%',
                                backgroundColor: terminalTheme ? '#00ff00' : '#4ade80',
                                borderRadius: 2
                              }}
                            />
                          </Box>
                        </Box>
                      </Box>
                    </Tooltip>
                  </motion.div>
                </Grid>
              );
            })}
          </Grid>

          {/* Summary */}
          <Box 
            sx={{ 
              mt: 3,
              p: 2, 
              backgroundColor: terminalTheme 
                ? 'rgba(0, 255, 0, 0.05)'
                : 'rgba(255,255,255,0.05)',
              borderRadius: 2,
              border: terminalTheme 
                ? '1px solid rgba(0, 255, 0, 0.2)'
                : '1px solid rgba(255,255,255,0.1)'
            }}
          >
            <Typography variant="body2" sx={{ mb: 1, color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.8)' }}>
              Total Tool Costs
            </Typography>
            <Typography variant="h5" sx={{ fontWeight: 'bold', color: terminalTheme ? '#00ff00' : '#ffffff' }}>
              {formatCurrency(totalCost)}
            </Typography>
            <Typography variant="caption" sx={{ color: terminalTheme ? '#00ff00' : 'rgba(255,255,255,0.7)' }}>
              Across {toolCosts.length} active tool{toolCosts.length !== 1 ? 's' : ''}
            </Typography>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ToolCostBreakdown;
