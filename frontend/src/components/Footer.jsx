// src/components/Footer.js
import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer = () => {
  return (
    <Box
      sx={{
        width: '100%',
        padding: '1rem',
        textAlign: 'center',
        borderTop: 'solid 2px #ccc',
        backgroundColor: '#ddd',
        color: 'black',
        position: 'absolute',
        bottom: 0,
      }}
    >
      <Typography variant="body2">
        © {new Date().getFullYear()} GoPostal SD. All rights reserved.
      </Typography>
    </Box>
  );
};

export default Footer;
