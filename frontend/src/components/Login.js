import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Grid
} from '@mui/material';
import { Shield, Security, Person } from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [showMfa, setShowMfa] = useState(false);
  const [mfaChallenge, setMfaChallenge] = useState(null);
  const [trustScore, setTrustScore] = useState(null);
  const [riskLevel, setRiskLevel] = useState(null);

  const { login, verifyMfa } = useAuth();

  const demoAccounts = [
    { username: 'alice_normal', label: 'Normal User', color: 'success' },
    { username: 'bob_suspicious', label: 'Suspicious Activity', color: 'warning' },
    { username: 'charlie_fraudster', label: 'Fraudulent Patterns', color: 'error' },
    { username: 'diana_traveler', label: 'Frequent Traveler', color: 'info' },
    { username: 'admin_user', label: 'Administrator', color: 'primary' }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    const result = await login(username, password);

    if (result.success) {
      setSuccess('Login successful!');
      setTrustScore(result.trustScore);
      setRiskLevel(result.riskLevel);
    } else if (result.requiresMfa) {
      setShowMfa(true);
      setMfaChallenge(result.mfaChallenge);
      setSuccess('MFA code sent. Please check your device.');
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  const handleMfaSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await verifyMfa(mfaChallenge.challenge_id, mfaCode);

    if (result.success) {
      setSuccess('MFA verification successful!');
    } else {
      setError(result.message);
    }

    setLoading(false);
  };

  const fillDemoAccount = (account) => {
    setUsername(account.username);
    setPassword('SecurePass123!');
    setError('');
    setSuccess('');
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '80vh'
      }}
    >
      <Grid container spacing={4} maxWidth="lg">
        <Grid item xs={12} md={6}>
          <Card sx={{ maxWidth: 500, mx: 'auto' }}>
            <CardContent sx={{ p: 4 }}>
              <Box sx={{ textAlign: 'center', mb: 3 }}>
                <Shield sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
                <Typography variant="h4" component="h1" gutterBottom>
                  TrustAI Login
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Real-time Fraud Detection System
                </Typography>
              </Box>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {error}
                </Alert>
              )}

              {success && (
                <Alert severity="success" sx={{ mb: 2 }}>
                  {success}
                </Alert>
              )}

              {trustScore !== null && (
                <Alert severity={getRiskColor(riskLevel)} sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    Trust Score: {trustScore.toFixed(1)}/100 | Risk Level: {riskLevel}
                  </Typography>
                </Alert>
              )}

              {!showMfa ? (
                <form onSubmit={handleSubmit}>
                  <TextField
                    fullWidth
                    label="Username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: <Person sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                  />
                  <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    margin="normal"
                    required
                    InputProps={{
                      startAdornment: <Security sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                    disabled={loading}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Login'}
                  </Button>
                </form>
              ) : (
                <form onSubmit={handleMfaSubmit}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    Multi-factor authentication required. Enter the 6-digit code.
                  </Alert>
                  <TextField
                    fullWidth
                    label="MFA Code"
                    value={mfaCode}
                    onChange={(e) => setMfaCode(e.target.value)}
                    margin="normal"
                    required
                    inputProps={{ maxLength: 6 }}
                  />
                  <Button
                    type="submit"
                    fullWidth
                    variant="contained"
                    sx={{ mt: 3, mb: 2 }}
                    disabled={loading || mfaCode.length !== 6}
                  >
                    {loading ? <CircularProgress size={24} /> : 'Verify'}
                  </Button>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={() => {
                      setShowMfa(false);
                      setMfaCode('');
                      setMfaChallenge(null);
                    }}
                  >
                    Back to Login
                  </Button>
                </form>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent sx={{ p: 4 }}>
              <Typography variant="h5" gutterBottom>
                Demo Accounts
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                Click on any account below to auto-fill the login form and explore different user behaviors.
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {demoAccounts.map((account) => (
                  <Button
                    key={account.username}
                    variant="outlined"
                    onClick={() => fillDemoAccount(account)}
                    sx={{
                      justifyContent: 'flex-start',
                      textTransform: 'none',
                      p: 2
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {account.username}
                      </Typography>
                      <Chip
                        label={account.label}
                        color={account.color}
                        size="small"
                        sx={{ ml: 'auto' }}
                      />
                    </Box>
                  </Button>
                ))}
              </Box>

              <Divider sx={{ my: 3 }} />

              <Typography variant="body2" color="text.secondary">
                <strong>Password for all demo accounts:</strong> SecurePass123!
              </Typography>

              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  System Features
                </Typography>
                <Typography variant="body2" color="text.secondary" component="div">
                  • Real-time trust scoring (0-100)
                  • Behavioral pattern analysis
                  • Device fingerprinting
                  • Geolocation risk assessment
                  • Multi-factor authentication
                  • Explainable AI decisions
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Login;
