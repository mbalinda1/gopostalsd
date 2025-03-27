import React from 'react';
import {Typography, Box } from '@mui/material';
import Navbar from '../components/NavBar';
import Footer from '../components/Footer';

const AdminPage = () => {
  return (
    <>
      <Navbar />
      <Box
        sx={{
          width: '100%',
          height: 'calc(100vh - 4rem)', // Adjust height to leave room for footer
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          textAlign: 'center',
          backgroundColor: '#e0f7fa',
        }}
      >
        <Typography variant="h4" component="h1" color="text.secondary">
          Admin Page (Coming Soon!)
        </Typography>
      </Box>
      <Footer />
    </>
  );
};

export default AdminPage;
