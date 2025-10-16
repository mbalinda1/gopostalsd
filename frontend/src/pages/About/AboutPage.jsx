/**
 * About Page for Go Postal SD Frontend
 * 
 * Professional about page showcasing Go Postal's services and information.
 */

import React from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Button
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const AboutPage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Main Content */}
      <Paper elevation={3} sx={{ p: 4, mb: 6 }}>
        <Typography variant="h4" gutterBottom color="primary" fontWeight="bold">
          About Go Postal
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
          Go Postal is your premier destination for printing services in Little Italy, San Diego, CA. 
          Conveniently located at 1501 India St Suite 103, San Diego, CA, our family-owned business is dedicated to providing 
          exceptional customer service and professional printing excellence.
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
          We prioritize saving you time and money by offering the right printing services at competitive prices. 
          Whether you need small black-and-white copies or large full-color prints, we handle everything with precision and care.
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
          As San Diego's premier copy, print, and document services center, we handle everything from small black-and-white copies 
          to large full-color prints. <strong>If it can be printed, Go Postal can do it!</strong> 
        </Typography>
        <Typography variant="body1" paragraph sx={{ fontSize: '1.1rem', lineHeight: 1.7 }}>
          Place printing orders online or in person. Our convenient online ordering system allows you to submit your printing 
          jobs from anywhere, while our in-person service provides immediate assistance and consultation for your printing needs. 
          Support local business and experience why shopping small means getting the best printing service around!
        </Typography>
        <Box sx={{ mt: 3, p: 3, backgroundColor: 'secondary.main', borderRadius: 2 }}>
          <Typography variant="h6" gutterBottom color="white" fontWeight="bold">
            Visit Go Postal Today
          </Typography>
          <Typography variant="body1" color="white">
            Let us help you with all your printing needs in San Diego!
          </Typography>
        </Box>
      </Paper>



      {/* Call to Action */}
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography variant="h5" gutterBottom color="primary" fontWeight="bold">
          Need To Print ?
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
          Place your printing order online or visit us in person!
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/')}
            sx={{ px: 4, py: 1.5 }}
          >
            Place Order Online
          </Button>
          <Button
            variant="outlined"
            size="large"
            href="https://maps.google.com/?q=1501+India+St+Suite+103+San+Diego+CA+92101"
            target="_blank"
            rel="noopener noreferrer"
            sx={{ px: 4, py: 1.5 }}
          >
            Place Order In Person
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default AboutPage;
