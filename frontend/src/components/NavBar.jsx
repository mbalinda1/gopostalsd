
import React from 'react';
import { AppBar, Toolbar, Box, Typography, Stack, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png';

const Navbar = () => {
  return (
    <AppBar position="static" sx={{ backgroundColor: '#02305e', width: '100%', borderBottom: 'solid 5px #ccc' }}>
      <Toolbar>
        {/* Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', marginRight: '1rem', border: 'solid 0.5px' }}>
          <img
            src={logo}
            alt="GoPostal SD Logo"
            style={{ height: '62px', width: 'auto' }} // Adjust size here
          />
        </Box>
        {/* App Name */}
        <Typography variant="h6" sx={{ flexGrow: 1, userSelect: 'none'}}>
          GOPOSTAL - PRINTING
        </Typography>
        {/* Navbar Links */}
        <Stack direction="row" spacing={2}>
          <Button color="inherit" component={Link} to="/">
            Home
          </Button>
          <Button color="inherit" component={Link} to="/admin">
            Admin
          </Button>
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
