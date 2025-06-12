import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Divider,
  Paper
} from '@mui/material';
import {
  ShoppingCart,
  Security,
  CheckCircle,
  Warning,
  Error,
  PlayArrow
} from '@mui/icons-material';
import axios from 'axios';

const TransactionSimulator = () => {
  const [formData, setFormData] = useState({
    amount: '',
    merchant: '',
    transaction_type: 'purchase'
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const merchants = [
    'Amazon', 'Walmart', 'Target', 'Best Buy', 'Home Depot',
    'Starbucks', 'McDonald\'s', 'Uber', 'Netflix', 'Spotify',
    'Apple Store', 'Google Play', 'Steam', 'PayPal', 'Venmo'
  ];

  const transactionTypes = [
    { value: 'purchase', label: 'Purchase' },
    { value: 'refund', label: 'Refund' },
    { value: 'transfer', label: 'Transfer' },
    { value: 'subscription', label: 'Subscription' },
    { value: 'withdrawal', label: 'Withdrawal' }
  ];

  const presetScenarios = [
    {
      name: 'Normal Purchase',
      description: 'Typical online shopping transaction',
      amount: '89.99',
      merchant: 'Amazon',
      transaction_type: 'purchase'
    },
    {
      name: 'Large Purchase',
      description: 'High-value transaction that may trigger review',
      amount: '1299.99',
      merchant: 'Best Buy',
      transaction_type: 'purchase'
    },
    {
      name: 'Rapid Transactions',
      description: 'Multiple quick transactions (suspicious pattern)',
      amount: '49.99',
      merchant: 'Steam',
      transaction_type: 'purchase'
    },
    {
      name: 'Unusual Merchant',
      description: 'Transaction with unfamiliar merchant',
      amount: '199.99',
      merchant: 'Unknown Store XYZ',
      transaction_type: 'purchase'
    }
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setResult(null);
    setError('');
  };

  const loadPresetScenario = (scenario) => {
    setFormData({
      amount: scenario.amount,
      merchant: scenario.merchant,
      transaction_type: scenario.transaction_type
    });
    setResult(null);
    setError('');
  };

  const simulateTransaction = async () => {
    if (!formData.amount || !formData.merchant) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await axios.post('/api/transaction/analyze', formData);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Transaction analysis failed');
      console.error('Transaction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getDecisionIcon = (decision) => {
    switch (decision) {
      case 'allow':
        return <CheckCircle color="success" />;
      case 'verify':
        return <Warning color="warning" />;
      case 'block':
        return <Error color="error" />;
      default:
        return <Security />;
    }
  };

  const getDecisionColor = (decision) => {
    switch (decision) {
      case 'allow':
        return 'success';
      case 'verify':
        return 'warning';
      case 'block':
        return 'error';
      default:
        return 'default';
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low':
        return 'success';
      case 'medium':
        return 'warning';
      case 'high':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Transaction Simulator
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Test the fraud detection system with different transaction scenarios
      </Typography>

      <Grid container spacing={3}>
        {/* Transaction Form */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Transaction Details
              </Typography>

              <TextField
                fullWidth
                label="Amount ($)"
                type="number"
                value={formData.amount}
                onChange={(e) => handleInputChange('amount', e.target.value)}
                margin="normal"
                required
                inputProps={{ min: 0, step: 0.01 }}
              />

              <FormControl fullWidth margin="normal">
                <InputLabel>Merchant</InputLabel>
                <Select
                  value={formData.merchant}
                  onChange={(e) => handleInputChange('merchant', e.target.value)}
                  label="Merchant"
                >
                  {merchants.map((merchant) => (
                    <MenuItem key={merchant} value={merchant}>
                      {merchant}
                    </MenuItem>
                  ))}
                  <MenuItem value="custom">Custom Merchant...</MenuItem>
                </Select>
              </FormControl>

              {formData.merchant === 'custom' && (
                <TextField
                  fullWidth
                  label="Custom Merchant Name"
                  value={formData.customMerchant || ''}
                  onChange={(e) => handleInputChange('merchant', e.target.value)}
                  margin="normal"
                  required
                />
              )}

              <FormControl fullWidth margin="normal">
                <InputLabel>Transaction Type</InputLabel>
                <Select
                  value={formData.transaction_type}
                  onChange={(e) => handleInputChange('transaction_type', e.target.value)}
                  label="Transaction Type"
                >
                  {transactionTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                fullWidth
                variant="contained"
                onClick={simulateTransaction}
                disabled={loading || !formData.amount || !formData.merchant}
                startIcon={loading ? <CircularProgress size={20} /> : <PlayArrow />}
                sx={{ mt: 3 }}
              >
                {loading ? 'Analyzing...' : 'Simulate Transaction'}
              </Button>

              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Preset Scenarios */}
          <Card sx={{ mt: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Preset Scenarios
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Click on a scenario to auto-fill the form
              </Typography>

              <Grid container spacing={2}>
                {presetScenarios.map((scenario, index) => (
                  <Grid item xs={12} key={index}>
                    <Paper
                      sx={{
                        p: 2,
                        cursor: 'pointer',
                        '&:hover': { backgroundColor: 'action.hover' }
                      }}
                      onClick={() => loadPresetScenario(scenario)}
                    >
                      <Typography variant="subtitle2" gutterBottom>
                        {scenario.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {scenario.description}
                      </Typography>
                      <Typography variant="caption" color="primary">
                        ${scenario.amount} • {scenario.merchant} • {scenario.transaction_type}
                      </Typography>
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Results */}
        <Grid item xs={12} md={6}>
          {result ? (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Analysis Results
                </Typography>

                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    {getDecisionIcon(result.decision)}
                    <Typography variant="h5">
                      Transaction {result.decision.charAt(0).toUpperCase() + result.decision.slice(1)}
                    </Typography>
                  </Box>

                  <Chip
                    label={`Decision: ${result.decision}`}
                    color={getDecisionColor(result.decision)}
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label={`Risk: ${result.risk_level}`}
                    color={getRiskColor(result.risk_level)}
                    sx={{ mr: 1, mb: 1 }}
                  />
                  <Chip
                    label={`Trust Score: ${result.trust_score}/100`}
                    color={result.trust_score >= 70 ? 'success' : result.trust_score >= 40 ? 'warning' : 'error'}
                    sx={{ mb: 1 }}
                  />
                </Box>

                <Divider sx={{ my: 2 }} />

                <Typography variant="subtitle1" gutterBottom>
                  Explanation
                </Typography>
                <Typography variant="body2" sx={{ mb: 2 }}>
                  {result.explanation}
                </Typography>

                {result.requires_verification && (
                  <Alert severity="warning" sx={{ mb: 2 }}>
                    Additional verification required before processing
                  </Alert>
                )}

                {result.recommended_actions && result.recommended_actions.length > 0 && (
                  <>
                    <Typography variant="subtitle1" gutterBottom>
                      Recommended Actions
                    </Typography>
                    <Box component="ul" sx={{ pl: 2, mb: 2 }}>
                      {result.recommended_actions.map((action, index) => (
                        <Typography component="li" variant="body2" key={index}>
                          {action}
                        </Typography>
                      ))}
                    </Box>
                  </>
                )}

                {result.transaction_id && (
                  <Typography variant="caption" color="text.secondary">
                    Transaction ID: {result.transaction_id}
                  </Typography>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent sx={{ textAlign: 'center', py: 8 }}>
                <ShoppingCart sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" color="text.secondary">
                  Enter transaction details and click "Simulate Transaction" to see the fraud detection analysis
                </Typography>
              </CardContent>
            </Card>
          )}
        </Grid>
      </Grid>
    </Box>
  );
};

export default TransactionSimulator;
