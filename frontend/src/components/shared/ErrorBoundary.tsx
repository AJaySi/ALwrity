import React, { Component, ErrorInfo, ReactNode } from 'react';
import {
  Box,
  Button,
  Typography,
  Paper,
  Container,
  Stack,
  Alert,
  Collapse,
  Divider
} from '@mui/material';
import ErrorIcon from '@mui/icons-material/ErrorOutline';
import RefreshIcon from '@mui/icons-material/Refresh';
import HomeIcon from '@mui/icons-material/Home';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import BugReportIcon from '@mui/icons-material/BugReport';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
  showDetails?: boolean;
  context?: string; // Context for better error messages (e.g., "Onboarding Wizard")
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  showDetails: boolean;
}

/**
 * ErrorBoundary Component
 * 
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of blank screen.
 * 
 * Usage:
 * <ErrorBoundary context="Dashboard">
 *   <YourComponent />
 * </ErrorBoundary>
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log error details
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    // Update state with error info
    this.setState({
      error,
      errorInfo,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Send to error tracking service (Sentry, LogRocket, etc.)
    this.logErrorToService(error, errorInfo);
  }

  logErrorToService(error: Error, errorInfo: ErrorInfo) {
    try {
      // Import error reporting utility
      import('../../utils/errorReporting').then(({ reportError }) => {
        reportError({
          error,
          context: this.props.context || 'ErrorBoundary',
          metadata: {
            componentStack: errorInfo.componentStack,
            errorBoundary: true,
          },
          severity: 'high', // Rendering errors are high severity
          timestamp: new Date().toISOString(),
        });
      }).catch(console.error);

      // Log to console with detailed info
      console.group('🚨 Error Boundary - Error Details');
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.error('Component Stack:', errorInfo.componentStack);
      console.error('Context:', this.props.context || 'Global');
      console.error('Timestamp:', new Date().toISOString());
      console.groupEnd();
    } catch (loggingError) {
      console.error('Failed to log error:', loggingError);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false,
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  toggleDetails = () => {
    this.setState((prevState) => ({
      showDetails: !prevState.showDetails,
    }));
  };

  render() {
    if (this.state.hasError) {
      const { error } = this.state;


      // Custom fallback UI provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      const { errorInfo, showDetails } = this.state;
      const { context, showDetails: showDetailsDefault } = this.props;

      return (
        <Box
          sx={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            p: { xs: 2, md: 4 },
          }}
        >
          <Container maxWidth="md">
            <Paper
              elevation={24}
              sx={{
                p: { xs: 3, md: 5 },
                borderRadius: 4,
                background: 'rgba(255, 255, 255, 0.98)',
                backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255, 255, 255, 0.3)',
              }}
            >
              <Stack spacing={3} alignItems="center">
                {/* Error Icon */}
                <Box
                  sx={{
                    width: 80,
                    height: 80,
                    borderRadius: '50%',
                    background: 'linear-gradient(45deg, #f44336 30%, #e91e63 90%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: '0 8px 32px rgba(244, 67, 54, 0.3)',
                  }}
                >
                  <ErrorIcon sx={{ fontSize: 48, color: 'white' }} />
                </Box>

                {/* Error Title */}
                <Typography
                  variant="h4"
                  component="h1"
                  sx={{
                    fontWeight: 700,
                    color: '#1a1a1a',
                    textAlign: 'center',
                  }}
                >
                  Oops! Something went wrong
                </Typography>

                {/* Context Message */}
                {context && (
                  <Typography
                    variant="body1"
                    color="text.secondary"
                    sx={{ textAlign: 'center' }}
                  >
                    An error occurred in: <strong>{context}</strong>
                  </Typography>
                )}

                {/* User-friendly message */}
                <Typography
                  variant="body1"
                  color="text.secondary"
                  sx={{ textAlign: 'center', maxWidth: 600 }}
                >
                  We're sorry for the inconvenience. The error has been logged and our team will investigate.
                  In the meantime, you can try refreshing the page or returning to the home page.
                </Typography>

                {/* Action Buttons */}
                <Stack
                  direction={{ xs: 'column', sm: 'row' }}
                  spacing={2}
                  sx={{ mt: 2, width: '100%', maxWidth: 500 }}
                >
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<RefreshIcon />}
                    onClick={this.handleReload}
                    sx={{
                      flex: 1,
                      py: 1.5,
                      background: 'linear-gradient(45deg, #667eea 30%, #764ba2 90%)',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #5568d3 30%, #6a3f8f 90%)',
                      },
                    }}
                  >
                    Reload Page
                  </Button>

                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<HomeIcon />}
                    onClick={this.handleGoHome}
                    sx={{
                      flex: 1,
                      py: 1.5,
                      borderColor: '#667eea',
                      color: '#667eea',
                      '&:hover': {
                        borderColor: '#5568d3',
                        background: 'rgba(102, 126, 234, 0.05)',
                      },
                    }}
                  >
                    Go Home
                  </Button>
                </Stack>

                {/* Error Details Toggle (for developers/debugging) */}
                {(showDetailsDefault || process.env.NODE_ENV === 'development') && (
                  <>
                    <Divider sx={{ width: '100%', my: 2 }} />

                    <Button
                      variant="text"
                      size="small"
                      startIcon={<BugReportIcon />}
                      endIcon={
                        <ExpandMoreIcon
                          sx={{
                            transform: showDetails ? 'rotate(180deg)' : 'rotate(0deg)',
                            transition: 'transform 0.3s',
                          }}
                        />
                      }
                      onClick={this.toggleDetails}
                      sx={{ color: '#666' }}
                    >
                      {showDetails ? 'Hide' : 'Show'} Technical Details
                    </Button>

                    <Collapse in={showDetails} sx={{ width: '100%' }}>
                      <Alert
                        severity="error"
                        icon={<BugReportIcon />}
                        sx={{
                          textAlign: 'left',
                          '& .MuiAlert-message': {
                            width: '100%',
                          },
                        }}
                      >
                        <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                          Error Message:
                        </Typography>
                        <Typography
                          variant="body2"
                          sx={{
                            fontFamily: 'monospace',
                            fontSize: '0.85rem',
                            mb: 2,
                            p: 1,
                            bgcolor: 'rgba(0,0,0,0.05)',
                            borderRadius: 1,
                            overflowX: 'auto',
                          }}
                        >
                          {error?.toString()}
                        </Typography>

                        {error?.stack && (
                          <>
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                              Stack Trace:
                            </Typography>
                            <Typography
                              variant="body2"
                              component="pre"
                              sx={{
                                fontFamily: 'monospace',
                                fontSize: '0.75rem',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                                p: 1,
                                bgcolor: 'rgba(0,0,0,0.05)',
                                borderRadius: 1,
                                maxHeight: 200,
                                overflowY: 'auto',
                              }}
                            >
                              {error.stack}
                            </Typography>
                          </>
                        )}

                        {errorInfo?.componentStack && (
                          <>
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ mt: 2 }}>
                              Component Stack:
                            </Typography>
                            <Typography
                              variant="body2"
                              component="pre"
                              sx={{
                                fontFamily: 'monospace',
                                fontSize: '0.75rem',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                                p: 1,
                                bgcolor: 'rgba(0,0,0,0.05)',
                                borderRadius: 1,
                                maxHeight: 150,
                                overflowY: 'auto',
                              }}
                            >
                              {errorInfo.componentStack}
                            </Typography>
                          </>
                        )}
                      </Alert>
                    </Collapse>
                  </>
                )}

                {/* Help Text */}
                <Typography
                  variant="caption"
                  color="text.secondary"
                  sx={{ textAlign: 'center', mt: 2 }}
                >
                  Error ID: {Date.now().toString(36)} • Timestamp: {new Date().toLocaleString()}
                </Typography>
              </Stack>
            </Paper>
          </Container>
        </Box>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

export default ErrorBoundary;

