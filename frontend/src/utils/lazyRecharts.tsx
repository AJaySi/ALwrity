/**
 * Lazy-loaded Recharts wrapper
 * 
 * Recharts is a large library (~200+ KiB). This wrapper lazy-loads it
 * only when charts are actually needed, reducing initial bundle size.
 * 
 * Usage:
 *   import { LazyLineChart, Line, XAxis, YAxis } from '../../utils/lazyRecharts';
 *   import { Suspense } from 'react';
 *   
 *   <Suspense fallback={<ChartSkeleton />}>
 *     <LazyLineChart data={data}>
 *       <Line />
 *     </LazyLineChart>
 *   </Suspense>
 */

import React, { lazy } from 'react';
import { Box, CircularProgress } from '@mui/material';

// Loading fallback for charts
export const ChartLoadingFallback: React.FC = () => (
  <Box
    display="flex"
    alignItems="center"
    justifyContent="center"
    minHeight="200px"
    sx={{ bgcolor: 'rgba(0,0,0,0.02)', borderRadius: 1 }}
  >
    <CircularProgress size={40} />
  </Box>
);

// Lazy load recharts components - these are the heavy ones
export const LazyLineChart = lazy(() => 
  import('recharts').then(module => ({ default: module.LineChart }))
);

export const LazyBarChart = lazy(() => 
  import('recharts').then(module => ({ default: module.BarChart }))
);

export const LazyPieChart = lazy(() => 
  import('recharts').then(module => ({ default: module.PieChart }))
);

export const LazyAreaChart = lazy(() => 
  import('recharts').then(module => ({ default: module.AreaChart }))
);

export const LazyRadarChart = lazy(() => 
  import('recharts').then(module => ({ default: module.RadarChart }))
);

export const LazyComposedChart = lazy(() => 
  import('recharts').then(module => ({ default: module.ComposedChart }))
);

// These are lightweight, can be imported directly
export {
  Line,
  Bar,
  Pie,
  Area,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ReferenceLine
} from 'recharts';

