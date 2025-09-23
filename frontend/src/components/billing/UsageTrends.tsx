import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  Chip,
} from '@mui/material';
import { motion } from 'framer-motion';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown,
  BarChart3,
  Calendar
} from 'lucide-react';

// Types
import { UsageTrends as UsageTrendsType, CostProjections } from '../../types/billing';

// Utils
import { 
  formatCurrency, 
  formatNumber,
  formatPercentage
} from '../../services/billingService';

interface UsageTrendsProps {
  trends: UsageTrendsType;
  projections: CostProjections;
}

const UsageTrends: React.FC<UsageTrendsProps> = ({ 
  trends, 
  projections 
}) => {
  // Transform data for charts
  const chartData = trends.periods.map((period, index) => ({
    period,
    calls: trends.total_calls[index] || 0,
    cost: trends.total_cost[index] || 0,
    tokens: trends.total_tokens[index] || 0,
  }));

  // Calculate growth rates (handle division by zero)
  const costGrowth = chartData.length > 1 
    ? chartData[0].cost > 0 
      ? ((chartData[chartData.length - 1].cost - chartData[0].cost) / chartData[0].cost) * 100
      : chartData[chartData.length - 1].cost > 0 ? 100 : 0
    : 0;
  
  const callsGrowth = chartData.length > 1 
    ? chartData[0].calls > 0 
      ? ((chartData[chartData.length - 1].calls - chartData[0].calls) / chartData[0].calls) * 100
      : chartData[chartData.length - 1].calls > 0 ? 100 : 0
    : 0;

  // Custom tooltip for charts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: 'white',
            padding: 2,
            borderRadius: 2,
            border: '1px solid rgba(255,255,255,0.1)'
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 1 }}>
            {label}
          </Typography>
          {payload.map((entry: any, index: number) => (
            <Typography key={index} variant="body2" sx={{ color: entry.color }}>
              {entry.name}: {entry.name === 'Cost' ? formatCurrency(entry.value) : formatNumber(entry.value)}
            </Typography>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      whileHover={{ scale: 1.02 }}
    >
      <Card 
        sx={{ 
          height: '100%',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 3,
          position: 'relative',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <CardContent sx={{ pb: 1 }}>
          <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1, fontWeight: 'bold', mb: 2 }}>
            <TrendingUp size={20} />
            Usage Trends & Projections
          </Typography>
        </CardContent>

        <CardContent sx={{ pt: 0 }}>
          {/* Growth Indicators */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3 }}
              >
                <Box
                  sx={{
                    p: 2,
                    backgroundColor: 'rgba(255,255,255,0.05)',
                    borderRadius: 2,
                    border: '1px solid rgba(255,255,255,0.1)',
                    textAlign: 'center'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                    {costGrowth >= 0 ? (
                      <TrendingUp size={16} color="#22c55e" />
                    ) : (
                      <TrendingDown size={16} color="#ef4444" />
                    )}
                    <Typography variant="body2" color="text.secondary">
                      Cost Growth
                    </Typography>
                  </Box>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 'bold',
                      color: costGrowth >= 0 ? '#22c55e' : '#ef4444'
                    }}
                  >
                    {costGrowth >= 0 ? '+' : ''}{costGrowth.toFixed(1)}%
                  </Typography>
                </Box>
              </motion.div>
            </Grid>
            
            <Grid item xs={6}>
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 }}
              >
                <Box
                  sx={{
                    p: 2,
                    backgroundColor: 'rgba(255,255,255,0.05)',
                    borderRadius: 2,
                    border: '1px solid rgba(255,255,255,0.1)',
                    textAlign: 'center'
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1, mb: 1 }}>
                    {callsGrowth >= 0 ? (
                      <TrendingUp size={16} color="#22c55e" />
                    ) : (
                      <TrendingDown size={16} color="#ef4444" />
                    )}
                    <Typography variant="body2" color="text.secondary">
                      Calls Growth
                    </Typography>
                  </Box>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 'bold',
                      color: callsGrowth >= 0 ? '#22c55e' : '#ef4444'
                    }}
                  >
                    {callsGrowth >= 0 ? '+' : ''}{callsGrowth.toFixed(1)}%
                  </Typography>
                </Box>
              </motion.div>
            </Grid>
          </Grid>

          {/* Cost Trend Chart */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', color: '#ffffff' }}>
              Monthly Cost Trend
            </Typography>
            <Box sx={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="costGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#667eea" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#667eea" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="period" 
                    stroke="rgba(255,255,255,0.9)"
                    fontSize={12}
                    tick={{ fill: 'rgba(255,255,255,0.9)' }}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.9)"
                    fontSize={12}
                    tick={{ fill: 'rgba(255,255,255,0.9)' }}
                    tickFormatter={(value) => `$${value.toFixed(0)}`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Area
                    type="monotone"
                    dataKey="cost"
                    stroke="#667eea"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#costGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </Box>

          {/* API Calls Trend Chart */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', color: '#ffffff' }}>
              API Calls Trend
            </Typography>
            <Box sx={{ height: 150 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                  <XAxis 
                    dataKey="period" 
                    stroke="rgba(255,255,255,0.6)"
                    fontSize={12}
                  />
                  <YAxis 
                    stroke="rgba(255,255,255,0.6)"
                    fontSize={12}
                    tickFormatter={(value) => formatNumber(value)}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Line
                    type="monotone"
                    dataKey="calls"
                    stroke="#764ba2"
                    strokeWidth={2}
                    dot={{ fill: '#764ba2', strokeWidth: 2, r: 4 }}
                    activeDot={{ r: 6, stroke: '#764ba2', strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </Box>

          {/* Projections */}
          <Box 
            sx={{ 
              p: 2, 
              backgroundColor: 'rgba(255,255,255,0.05)',
              borderRadius: 2,
              border: '1px solid rgba(255,255,255,0.1)'
            }}
          >
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
              <Calendar size={16} />
              Monthly Projections
            </Typography>
            
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Projected Cost
                  </Typography>
                  <Typography variant="h6" sx={{ fontWeight: 'bold', color: 'primary.main' }}>
                    {formatCurrency(projections.projected_monthly_cost)}
                  </Typography>
                </Box>
              </Grid>
              
              <Grid item xs={6}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 0.5 }}>
                    Usage %
                  </Typography>
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      fontWeight: 'bold',
                      color: projections.projected_usage_percentage > 80 ? 'error.main' : 
                             projections.projected_usage_percentage > 60 ? 'warning.main' : 'success.main'
                    }}
                  >
                    {formatPercentage(projections.projected_usage_percentage)}
                  </Typography>
                </Box>
              </Grid>
            </Grid>
            
            <Box sx={{ mt: 2, textAlign: 'center' }}>
              <Chip
                label={`Limit: ${formatCurrency(projections.cost_limit)}`}
                size="small"
                sx={{
                  backgroundColor: 'rgba(255,255,255,0.1)',
                  color: 'text.secondary',
                  fontWeight: 'bold'
                }}
              />
            </Box>
          </Box>
        </CardContent>

        {/* Decorative Elements */}
        <Box
          sx={{
            position: 'absolute',
            top: -50,
            right: -50,
            width: 100,
            height: 100,
            background: 'radial-gradient(circle, rgba(118, 75, 162, 0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}
        />
        <Box
          sx={{
            position: 'absolute',
            bottom: -30,
            left: -30,
            width: 60,
            height: 60,
            background: 'radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%)',
            borderRadius: '50%',
            pointerEvents: 'none'
          }}
        />
      </Card>
    </motion.div>
  );
};

export default UsageTrends;
