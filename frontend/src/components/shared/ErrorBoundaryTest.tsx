import React, { useState } from 'react';
import { Box, Button, Typography, Stack, Alert, Paper } from '@mui/material';
import BugReportIcon from '@mui/icons-material/BugReport';
import ErrorBoundary from './ErrorBoundary';
import ComponentErrorBoundary from './ComponentErrorBoundary';

/**
 * Error Boundary Test Component
 * 
 * Use this component to test that error boundaries are working correctly.
 * Access via: http://localhost:3000/error-test (add route in App.tsx)
 * 
 * This should ONLY be used in development!
 */

// Component that intentionally crashes
const CrashingComponent: React.FC<{ shouldCrash: boolean }> = ({ shouldCrash }) => {
  if (shouldCrash) {
    throw new Error('Intentional error for testing ErrorBoundary');
  }
  return <Typography>Component is working normally</Typography>;
};

// Component that crashes after a delay
const DelayedCrashComponent: React.FC<{ shouldCrash: boolean }> = ({ shouldCrash }) => {
  const [count, setCount] = useState(0);

  if (count > 3 && shouldCrash) {
    throw new Error('Delayed crash after 3 clicks');
  }

  return (
    <Box>
      <Typography>Click count: {count}</Typography>
      <Button onClick={() => setCount(count + 1)} variant="outlined" size="small">
        Increment (crashes after 3)
      </Button>
    </Box>
  );
};

const ErrorBoundaryTest: React.FC = () => {
  const [globalCrash, setGlobalCrash] = useState(false);
  const [componentCrash, setComponentCrash] = useState(false);
  const [delayedCrash, setDelayedCrash] = useState(false);

  return (
    <Box sx={{ p: 4, maxWidth: 1200, mx: 'auto' }}>
      <Paper sx={{ p: 4, mb: 4, bgcolor: 'warning.light' }}>
        <Stack spacing={2}>
          <Stack direction="row" spacing={2} alignItems="center">
            <BugReportIcon sx={{ fontSize: 40 }} />
            <Typography variant="h4" fontWeight={700}>
              Error Boundary Testing
            </Typography>
          </Stack>
          <Alert severity="warning">
            <strong>Development Only:</strong> This page is for testing error boundaries.
            Remove this route before deploying to production!
          </Alert>
        </Stack>
      </Paper>

      <Stack spacing={4}>
        {/* Test 1: Global Error Boundary */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Test 1: Global Error Boundary
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This will crash the entire component tree. The global ErrorBoundary should catch it
            and show a full-page error screen with reload options.
          </Typography>
          
          <ErrorBoundary context="Global Error Test">
            <Box sx={{ p: 2, border: '1px dashed', borderColor: 'divider', borderRadius: 1, mb: 2 }}>
              <CrashingComponent shouldCrash={globalCrash} />
            </Box>
          </ErrorBoundary>

          <Button
            variant="contained"
            color="error"
            onClick={() => setGlobalCrash(true)}
            disabled={globalCrash}
          >
            Trigger Global Crash
          </Button>
        </Paper>

        {/* Test 2: Component-Level Error Boundary */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Test 2: Component Error Boundary
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This will crash only a specific component. The ComponentErrorBoundary should show
            a minimal error message inline without affecting the rest of the page.
          </Typography>

          <ComponentErrorBoundary 
            componentName="Test Component"
            onReset={() => setComponentCrash(false)}
          >
            <Box sx={{ p: 2, border: '1px dashed', borderColor: 'divider', borderRadius: 1, mb: 2 }}>
              <CrashingComponent shouldCrash={componentCrash} />
            </Box>
          </ComponentErrorBoundary>

          <Button
            variant="contained"
            color="warning"
            onClick={() => setComponentCrash(true)}
            disabled={componentCrash}
          >
            Trigger Component Crash
          </Button>

          {componentCrash && (
            <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
              Notice: Only the component crashed, not the entire page!
            </Typography>
          )}
        </Paper>

        {/* Test 3: Delayed Crash */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Test 3: Delayed Error (Simulates User Interaction)
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            This component crashes after user interaction (3 clicks). Tests that error boundaries
            work for runtime errors, not just initial render errors.
          </Typography>

          <ComponentErrorBoundary 
            componentName="Delayed Crash Component"
            onReset={() => setDelayedCrash(false)}
          >
            <Box sx={{ p: 2, border: '1px dashed', borderColor: 'divider', borderRadius: 1, mb: 2 }}>
              <DelayedCrashComponent shouldCrash={delayedCrash} />
            </Box>
          </ComponentErrorBoundary>

          <Button
            variant="contained"
            color="info"
            onClick={() => setDelayedCrash(true)}
            disabled={delayedCrash}
          >
            Enable Delayed Crash
          </Button>
        </Paper>

        {/* Test 4: API Error Simulation */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Test 4: Verify Error Boundary Doesn't Catch API Errors
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Error boundaries only catch rendering errors, not async errors.
            This is expected behavior - API errors should be handled with try/catch.
          </Typography>
          
          <Alert severity="info">
            Error boundaries do NOT catch:
            <ul>
              <li>Event handlers (onClick, onChange, etc.)</li>
              <li>Asynchronous code (setTimeout, fetch, promises)</li>
              <li>Server-side rendering errors</li>
              <li>Errors in the error boundary itself</li>
            </ul>
            These should be handled with try/catch blocks.
          </Alert>
        </Paper>

        {/* Instructions */}
        <Paper sx={{ p: 3, bgcolor: 'success.light' }}>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Testing Instructions
          </Typography>
          <Stack spacing={1}>
            <Typography variant="body2">
              1. <strong>Global Crash:</strong> Should show full-page error with "Reload Page" and "Go Home" buttons
            </Typography>
            <Typography variant="body2">
              2. <strong>Component Crash:</strong> Should show inline error alert with "Retry" button
            </Typography>
            <Typography variant="body2">
              3. <strong>Delayed Crash:</strong> Click increment 4 times to trigger error
            </Typography>
            <Typography variant="body2">
              4. <strong>Check Console:</strong> All errors should be logged with detailed stack traces
            </Typography>
          </Stack>
        </Paper>
      </Stack>
    </Box>
  );
};

export default ErrorBoundaryTest;

