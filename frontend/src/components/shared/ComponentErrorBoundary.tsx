import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Typography, Button, Alert, Stack } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';

interface ComponentErrorBoundaryProps {
  children: ReactNode;
  componentName: string;
  onReset?: () => void;
}

interface ComponentErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

/**
 * Lightweight Error Boundary for Individual Components
 * 
 * Use this to wrap specific components that might fail without crashing the entire app.
 * Shows a minimal error UI that doesn't take over the whole page.
 * 
 * Usage:
 * <ComponentErrorBoundary componentName="API Key Carousel">
 *   <ApiKeyCarousel />
 * </ComponentErrorBoundary>
 */
class ComponentErrorBoundary extends Component<
  ComponentErrorBoundaryProps,
  ComponentErrorBoundaryState
> {
  constructor(props: ComponentErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ComponentErrorBoundaryState> {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error(`Error in ${this.props.componentName}:`, error, errorInfo);
    
    // Log to backend or error tracking service
    this.logError(error, errorInfo);
  }

  logError(error: Error, errorInfo: ErrorInfo) {
    try {
      // Import error reporting utility
      import('../../utils/errorReporting').then(({ reportError }) => {
        reportError({
          error,
          context: `Component: ${this.props.componentName}`,
          metadata: {
            componentStack: errorInfo.componentStack,
            componentError: true,
          },
          severity: 'medium', // Component errors are medium severity
          timestamp: new Date().toISOString(),
        });
      }).catch(console.error);

      console.group(`🔴 Component Error: ${this.props.componentName}`);
      console.error('Error:', error.message);
      console.error('Stack:', error.stack);
      console.error('Component Stack:', errorInfo.componentStack);
      console.groupEnd();
    } catch (e) {
      console.error('Failed to log component error:', e);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <Alert
          severity="error"
          sx={{
            my: 2,
            borderRadius: 2,
          }}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={this.handleReset}
              startIcon={<RefreshIcon />}
            >
              Retry
            </Button>
          }
        >
          <Stack spacing={1}>
            <Typography variant="subtitle2" fontWeight={600}>
              {this.props.componentName} Error
            </Typography>
            <Typography variant="body2">
              {this.state.error?.message || 'An unexpected error occurred in this component.'}
            </Typography>
            {process.env.NODE_ENV === 'development' && this.state.error?.stack && (
              <Typography
                variant="caption"
                component="pre"
                sx={{
                  mt: 1,
                  p: 1,
                  bgcolor: 'rgba(0,0,0,0.05)',
                  borderRadius: 1,
                  fontSize: '0.7rem',
                  maxHeight: 100,
                  overflowY: 'auto',
                  overflowX: 'auto',
                }}
              >
                {this.state.error.stack}
              </Typography>
            )}
          </Stack>
        </Alert>
      );
    }

    return this.props.children;
  }
}

export default ComponentErrorBoundary;

