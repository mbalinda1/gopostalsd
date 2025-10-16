/**
 * Layout Component for Go Postal SD Frontend
 * 
 * This component provides the main layout structure including the navbar and footer.
 */

import React from 'react';
import { Box } from '@mui/material';
import { useLocation } from 'react-router-dom';
import Navbar from './NavBar';
import Footer from './Footer';
import ProfessionalFooter from './ProfessionalFooter';

const Layout = ({ children, showFooter = true }) => {
  const location = useLocation();
  const isAboutPage = location.pathname === '/about';

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <Navbar />
      <Box 
        component="main" 
        sx={{ 
          flex: 1,
          pt: 8, // Account for fixed navbar height
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        {children}
      </Box>
      {showFooter && (isAboutPage ? <ProfessionalFooter /> : <Footer />)}
    </Box>
  );
};

export default Layout;
