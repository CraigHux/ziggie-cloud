import React from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import ErrorOutlineIcon from '@mui/icons-material/ErrorOutline';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    this.setState({
      error: error,
      errorInfo: errorInfo,
    });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      return (
        <Paper
          elevation={3}
          sx={{
            p: 4,
            textAlign: 'center',
            bgcolor: 'background.paper',
            border: '2px solid',
            borderColor: 'error.main',
            borderRadius: 2,
          }}
        >
          <ErrorOutlineIcon
            sx={{ fontSize: 64, color: 'error.main', mb: 2 }}
          />
          <Typography variant="h5" gutterBottom color="error">
            Something went wrong
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </Typography>
          {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
            <Box
              sx={{
                textAlign: 'left',
                bgcolor: '#f5f5f5',
                p: 2,
                borderRadius: 1,
                mb: 3,
                maxHeight: 200,
                overflow: 'auto',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              }}
            >
              <Typography variant="caption" component="pre">
                {this.state.errorInfo.componentStack}
              </Typography>
            </Box>
          )}
          <Button
            variant="contained"
            onClick={this.handleReset}
            sx={{
              bgcolor: '#FF8C42',
              '&:hover': {
                bgcolor: '#E67E3A',
              },
            }}
          >
            Try Again
          </Button>
        </Paper>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
