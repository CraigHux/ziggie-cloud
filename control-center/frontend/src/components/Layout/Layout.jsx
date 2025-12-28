import React from 'react';
import { Box, Toolbar } from '@mui/material';
import Navbar from './Navbar';
import Footer from './Footer';

const drawerWidth = 240;

export const Layout = ({ children, darkMode, onToggleDarkMode, wsConnected }) => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Navbar darkMode={darkMode} onToggleDarkMode={onToggleDarkMode} wsConnected={wsConnected} />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Toolbar />
        <Box sx={{ flexGrow: 1, p: 3 }}>
          {children}
        </Box>
        <Footer />
      </Box>
    </Box>
  );
};

export default Layout;
