import React from 'react';
import { Box, Typography, Link } from '@mui/material';

export const Footer = () => {
  return (
    <Box
      component="footer"
      sx={{
        py: 2,
        px: 2,
        mt: 'auto',
        borderTop: '1px solid',
        borderColor: 'divider',
        textAlign: 'center',
      }}
    >
      <Typography variant="body2" color="text.secondary">
        Ziggie Control Center - v1.0.0
      </Typography>
      <Typography variant="caption" color="text.secondary">
        Built with React + Material-UI
      </Typography>
    </Box>
  );
};

export default Footer;
