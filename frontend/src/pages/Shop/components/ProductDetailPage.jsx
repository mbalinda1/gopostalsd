import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Paper,
  Divider,
  Alert,
  CircularProgress,
  Chip,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  CloudUpload as CloudUploadIcon,
  LocalShipping as LocalShippingIcon,
  Calculate as CalculateIcon,
  ShoppingCart as ShoppingCartIcon,
  Close as CloseIcon,
  CheckCircle as CheckCircleIcon,
  Info as InfoIcon
} from '@mui/icons-material';
import {
  fetchProductOptions,
  calculateProductPrice,
  getShippingEstimates,
  addItemToCart,
  getOrCreateCart
} from '../../../services/product_service';
import logoImage from '../../../assets/logo.png';

const ProductDetailPage = ({ product, onBack }) => {
  const [options, setOptions] = useState([]);
  const [selectedOptions, setSelectedOptions] = useState({});
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pricingLoading, setPricingLoading] = useState(false);
  const [error, setError] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [activeStep, setActiveStep] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [shippingInfo, setShippingInfo] = useState({
    country: 'US',
    state: 'CA',
    city: 'San Diego',
    zip: '92101'
  });
  const [shippingEstimates, setShippingEstimates] = useState([]);
  const [shippingLoading, setShippingLoading] = useState(false);
  const [showShippingDialog, setShowShippingDialog] = useState(false);

  // Load product options when component mounts
  useEffect(() => {
    const loadOptions = async () => {
      if (!product.vendor_product_id) return;
      
      setLoading(true);
      try {
        console.log('Loading options for product:', product.vendor_product_id);
        const productOptions = await fetchProductOptions(parseInt(product.vendor_product_id), 6); // Canada store
        console.log('Product options loaded:', productOptions);
        setOptions(productOptions);
      } catch (error) {
        console.error('Error loading product options:', error);
        setError('Failed to load product options');
      } finally {
        setLoading(false);
      }
    };

    loadOptions();
  }, [product.vendor_product_id]);

  // Calculate price when options change
  useEffect(() => {
    const calculatePrice = async () => {
      console.log('Price calculation triggered');
      console.log('Product vendor ID:', product.vendor_product_id);
      console.log('Selected options:', selectedOptions);
      console.log('Available options:', options);
      
      if (!product.vendor_product_id || Object.keys(selectedOptions).length === 0) {
        console.log('No vendor ID or no selected options, setting pricing to null');
        setPricing(null);
        return;
      }

      // Check if all required option groups have selections
      const hasAllRequiredOptions = options.every(optionGroup => 
        selectedOptions[optionGroup.group] && selectedOptions[optionGroup.group] !== ''
      );

      console.log('Has all required options:', hasAllRequiredOptions);

      if (!hasAllRequiredOptions) {
        console.log('Not all required options selected, setting pricing to null');
        setPricing(null);
        return;
      }

      // Generate the option key in the correct order
      const optionIds = options.map(optionGroup => 
        selectedOptions[optionGroup.group]
      ).filter(id => id && id !== '');

      console.log('Generated option IDs:', optionIds);

      if (optionIds.length === 0) {
        console.log('No option IDs generated, setting pricing to null');
        setPricing(null);
        return;
      }

      setPricingLoading(true);
      try {
        console.log('Calculating price for product:', product.vendor_product_id, 'with options:', optionIds);
        const priceData = await calculateProductPrice(parseInt(product.vendor_product_id), optionIds, 6);
        console.log('Price data received:', priceData);
        setPricing(priceData);
        setError(null);
      } catch (error) {
        console.error('Error calculating price:', error);
        setError('Failed to calculate price');
        setPricing(null);
      } finally {
        setPricingLoading(false);
      }
    };

    calculatePrice();
  }, [selectedOptions, product.vendor_product_id, options]);

  const handleOptionChange = (group, optionId) => {
    console.log('Option changed:', group, 'to', optionId);
    setSelectedOptions(prev => {
      const newOptions = {
        ...prev,
        [group]: optionId
      };
      console.log('New selected options:', newOptions);
      return newOptions;
    });
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const removeFile = (index) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleShippingEstimate = async () => {
    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please configure your product options first');
      return;
    }

    setShippingLoading(true);
    try {
      // Generate options in the correct format for Sinalite API
      const optionsObject = {};
      options.forEach(optionGroup => {
        const selectedId = selectedOptions[optionGroup.group];
        if (selectedId && selectedId !== '') {
          optionsObject[optionGroup.group] = selectedId;
        }
      });

      const items = [{
        productId: parseInt(product.vendor_product_id),
        options: optionsObject
      }];

      const estimates = await getShippingEstimates(items, shippingInfo);
      setShippingEstimates(estimates);
      setShowShippingDialog(true);
    } catch (error) {
      console.error('Error getting shipping estimates:', error);
      setError('Failed to get shipping estimates');
    } finally {
      setShippingLoading(false);
    }
  };

  const handleAddToCart = async () => {
    if (!pricing || Object.keys(selectedOptions).length === 0) {
      setError('Please select all required options');
      return;
    }

    try {
      // Get or create cart
      const sessionId = `session_${Date.now()}`;
      const cart = await getOrCreateCart(sessionId, null, 6);
      
      if (!cart) {
        setError('Failed to create cart');
        return;
      }

      // Generate option IDs in the correct order
      const optionIds = options.map(optionGroup => 
        selectedOptions[optionGroup.group]
      ).filter(id => id && id !== '');

      const cartItem = await addItemToCart(
        cart.id,
        parseInt(product.vendor_product_id),
        product.name,
        product.sku,
        optionIds,
        quantity
      );

      if (cartItem) {
        setError(null);
        // Show success message or redirect
        alert('Item added to cart successfully!');
      } else {
        setError('Failed to add item to cart');
      }
    } catch (error) {
      console.error('Error adding to cart:', error);
      setError('Failed to add item to cart');
    }
  };

  const formatPrice = (price) => {
    if (!price) return 'Price not available';
    return `$${parseFloat(price).toFixed(2)}`;
  };

  const getTotalPrice = () => {
    if (!pricing) return 0;
    return parseFloat(pricing.price) * quantity;
  };

  const getEstimatedShipDate = () => {
    const today = new Date();
    const shipDate = new Date(today);
    shipDate.setDate(today.getDate() + 3); // 3 business days
    return shipDate.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    });
  };

  const steps = [
    'Configure Product',
    'Upload Artwork',
    'Shipping & Checkout'
  ];

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Button
          startIcon={<CloseIcon />}
          onClick={onBack}
          sx={{ mb: 2 }}
        >
          Back to Products
        </Button>
        <Typography variant="h4" component="h1" gutterBottom>
          {product.name}
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {product.description}
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={4}>
        {/* Left Column - Product Image */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box sx={{ textAlign: 'center' }}>
                <img
                  src={product.image || logoImage}
                  alt={product.name}
                  style={{
                    width: '100%',
                    maxWidth: '400px',
                    height: 'auto',
                    borderRadius: '8px'
                  }}
                />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Right Column - Configuration */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Price this item:
            </Typography>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
                <CircularProgress />
              </Box>
            ) : (
              <Box sx={{ mb: 3 }}>
                {options.map((optionGroup, index) => (
                  <FormControl key={index} fullWidth sx={{ mb: 2 }}>
                    <InputLabel>{optionGroup.group}</InputLabel>
                    <Select
                      value={selectedOptions[optionGroup.group] || ''}
                      onChange={(e) => handleOptionChange(optionGroup.group, e.target.value)}
                      label={optionGroup.group}
                    >
                      <MenuItem value="">
                        <em>Select {optionGroup.group}</em>
                      </MenuItem>
                      {optionGroup.options.map((option) => (
                        <MenuItem key={option.id} value={option.id}>
                          {option.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                ))}
              </Box>
            )}

            {/* Quantity */}
            <TextField
              label="Quantity"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              inputProps={{ min: 1 }}
              fullWidth
              sx={{ mb: 3 }}
            />

            {/* Pricing Display */}
            <Box sx={{ mb: 3, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              {pricingLoading ? (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography variant="body2">Calculating price...</Typography>
                </Box>
              ) : pricing ? (
                <Box>
                  <Typography variant="h6" color="primary" gutterBottom>
                    Regular Price: {formatPrice(pricing.price)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Order now and this item is estimated to be ready to ship by {getEstimatedShipDate()} at 5 PM
                  </Typography>
                  <Typography variant="caption" color="text.secondary" display="block" sx={{ mt: 1 }}>
                    * Please note that this is just an estimate. Actual production time may vary.
                  </Typography>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  Select options to see price
                </Typography>
              )}
            </Box>

            {/* Package Information */}
            {pricing?.packageInfo && (
              <Accordion sx={{ mb: 3 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="subtitle1">Package Information</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    {Object.entries(pricing.packageInfo).map(([key, value]) => (
                      <ListItem key={key}>
                        <ListItemText
                          primary={key}
                          secondary={value}
                        />
                      </ListItem>
                    ))}
                  </List>
                </AccordionDetails>
              </Accordion>
            )}

            {/* Action Buttons */}
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
              <Button
                variant="contained"
                startIcon={<ShoppingCartIcon />}
                onClick={handleAddToCart}
                disabled={!pricing || pricingLoading}
                sx={{ flexGrow: 1 }}
              >
                Add to Cart
              </Button>
              <Button
                variant="outlined"
                startIcon={<LocalShippingIcon />}
                onClick={handleShippingEstimate}
                disabled={!pricing || shippingLoading}
              >
                {shippingLoading ? <CircularProgress size={20} /> : 'Estimate Shipping'}
              </Button>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Stepper for Additional Steps */}
      <Box sx={{ mt: 4 }}>
        <Stepper activeStep={activeStep} orientation="vertical">
          <Step>
            <StepLabel>Upload your artwork</StepLabel>
            <StepContent>
              <Box sx={{ mb: 2 }}>
                <input
                  accept="image/*,.pdf"
                  style={{ display: 'none' }}
                  id="file-upload"
                  multiple
                  type="file"
                  onChange={handleFileUpload}
                />
                <label htmlFor="file-upload">
                  <Button
                    variant="outlined"
                    component="span"
                    startIcon={<CloudUploadIcon />}
                    sx={{ mb: 2 }}
                  >
                    Upload Files
                  </Button>
                </label>
                
                {uploadedFiles.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Uploaded Files:
                    </Typography>
                    {uploadedFiles.map((file, index) => (
                      <Chip
                        key={index}
                        label={file.name}
                        onDelete={() => removeFile(index)}
                        sx={{ mr: 1, mb: 1 }}
                      />
                    ))}
                  </Box>
                )}
              </Box>
              <Button
                variant="contained"
                onClick={() => setActiveStep(1)}
                sx={{ mt: 1, mr: 1 }}
              >
                Continue
              </Button>
            </StepContent>
          </Step>

          <Step>
            <StepLabel>Calculate shipping cost</StepLabel>
            <StepContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Enter your destination to get a shipping estimate.
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>Country</InputLabel>
                      <Select
                        value={shippingInfo.country}
                        onChange={(e) => setShippingInfo(prev => ({ ...prev, country: e.target.value }))}
                        label="Country"
                      >
                        <MenuItem value="US">United States</MenuItem>
                        <MenuItem value="CA">Canada</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                      <InputLabel>State/Province</InputLabel>
                      <Select
                        value={shippingInfo.state}
                        onChange={(e) => setShippingInfo(prev => ({ ...prev, state: e.target.value }))}
                        label="State/Province"
                      >
                        <MenuItem value="CA">California</MenuItem>
                        <MenuItem value="NY">New York</MenuItem>
                        <MenuItem value="TX">Texas</MenuItem>
                        <MenuItem value="ON">Ontario</MenuItem>
                        <MenuItem value="BC">British Columbia</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="City"
                      value={shippingInfo.city}
                      onChange={(e) => setShippingInfo(prev => ({ ...prev, city: e.target.value }))}
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <TextField
                      fullWidth
                      label="Zip/Postal Code"
                      value={shippingInfo.zip}
                      onChange={(e) => setShippingInfo(prev => ({ ...prev, zip: e.target.value }))}
                    />
                  </Grid>
                </Grid>
              </Box>
              <Button
                variant="contained"
                onClick={handleShippingEstimate}
                disabled={shippingLoading}
                sx={{ mt: 1, mr: 1 }}
              >
                {shippingLoading ? <CircularProgress size={20} /> : 'Get a Quote'}
              </Button>
            </StepContent>
          </Step>
        </Stepper>
      </Box>

      {/* Shipping Estimates Dialog */}
      <Dialog
        open={showShippingDialog}
        onClose={() => setShowShippingDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            Shipping Options
            <IconButton onClick={() => setShowShippingDialog(false)}>
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent>
          {shippingEstimates.length > 0 ? (
            <List>
              {shippingEstimates.map((option, index) => (
                <ListItem key={index} divider>
                  <ListItemIcon>
                    <LocalShippingIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText
                    primary={`${option.carrier_name} ${option.method_name}`}
                    secondary={`${option.shipping_days} - Days Shipping`}
                  />
                  <Typography variant="h6" color="primary">
                    {formatPrice(option.price)}
                  </Typography>
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography color="text.secondary">
              No shipping options available
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowShippingDialog(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProductDetailPage;
