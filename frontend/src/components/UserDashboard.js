import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Alert,
  Chip,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  CircularProgress,
  Tab,
  Tabs
} from '@mui/material';
import {
  Security,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Refresh,
  ShoppingCart,
  AccountCircle
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar
} from 'recharts';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';

const UserDashboard = () => {
  const { user } = useAuth();
  const [trustData, setTrustData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [tabValue, setTabValue] = useState(0);

  const fetchTrustData = async () => {
    try {
      const response = await axios.get('/api/user/trust-score');
      setTrustData(response.data);
      setError('');
    } catch (err) {
      setError('Failed to load trust score data');
      console.error('Trust data error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrustData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchTrustData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTrustScoreColor = (score) => {
    if (score >= 70) return 'success';
    if (score >= 40) return 'warning';
    return 'error';
  };

  const getTrustScoreColorHex = (score) => {
    if (score >= 70) return '#4caf50';
    if (score >= 40) return '#ff9800';
    return '#f44336';
  };

  const getTrendIcon = (history) => {
    if (!history || history.length < 2) return <TrendingFlat />;
    
    const recent = history.slice(0, 3).reduce((sum, item) => sum + item.score, 0) / 3;
    const older = history.slice(3, 6).reduce((sum, item) => sum + item.score, 0) / 3;
    
    if (recent > older + 5) return <TrendingUp color="success" />;
    if (recent < older - 5) return <TrendingDown color="error" />;
    return <TrendingFlat color="info" />;
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  const trustScoreData = trustData?.current_score ? [
    {
      name: 'Trust Score',
      value: trustData.current_score,
      fill: getTrustScoreColorHex(trustData.current_score)
    }
  ] : [];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          My Trust Dashboard
        </Typography>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={fetchTrustData}
        >
          Refresh
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {trustData && (
        <>
          {/* Trust Score Overview */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent sx={{ textAlign: 'center' }}>
                  <Typography variant="h6" gutterBottom>
                    Current Trust Score
                  </Typography>
                  <Box sx={{ position: 'relative', display: 'inline-flex', mb: 2 }}>
                    <CircularProgress
                      variant="determinate"
                      value={trustData.current_score}
                      size={120}
                      thickness={4}
                      sx={{
                        color: getTrustScoreColorHex(trustData.current_score),
                      }}
                    />
                    <Box
                      sx={{
                        top: 0,
                        left: 0,
                        bottom: 0,
                        right: 0,
                        position: 'absolute',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <Typography variant="h4" component="div" color="text.secondary">
                        {trustData.current_score.toFixed(0)}
                      </Typography>
                    </Box>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                    <Chip
                      label={
                        trustData.current_score >= 70 ? 'Trusted User' :
                        trustData.current_score >= 40 ? 'Moderate Risk' : 'High Risk'
                      }
                      color={getTrustScoreColor(trustData.current_score)}
                    />
                    {getTrendIcon(trustData.history)}
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Trust Score Factors
                  </Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Device Trust
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={trustData.score_factors?.device_trust || 0}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption">
                        {(trustData.score_factors?.device_trust || 0).toFixed(1)}/100
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Location Trust
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={trustData.score_factors?.location_trust || 0}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption">
                        {(trustData.score_factors?.location_trust || 0).toFixed(1)}/100
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Behavior Trust
                      </Typography>
                      <LinearProgress
                        variant="determinate"
                        value={trustData.score_factors?.behavior_trust || 0}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption">
                        {(trustData.score_factors?.behavior_trust || 0).toFixed(1)}/100
                      </Typography>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary">
                        Account Age
                      </Typography>
                      <Typography variant="body1">
                        {trustData.score_factors?.account_age_days || 0} days
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Verified: {trustData.score_factors?.verification_status ? 'Yes' : 'No'}
                      </Typography>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Detailed Analytics */}
          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs value={tabValue} onChange={(e, newValue) => setTabValue(newValue)}>
              <Tab label="Trust Score History" />
              <Tab label="Recent Activities" />
              <Tab label="Security Tips" />
            </Tabs>
          </Box>

          {tabValue === 0 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Trust Score Trend (Last 30 Days)
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trustData.history?.slice().reverse()}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis 
                      dataKey="timestamp" 
                      tickFormatter={(value) => new Date(value).toLocaleDateString()}
                    />
                    <YAxis domain={[0, 100]} />
                    <Tooltip 
                      labelFormatter={(value) => new Date(value).toLocaleString()}
                      formatter={(value) => [value.toFixed(1), 'Trust Score']}
                    />
                    <Line
                      type="monotone"
                      dataKey="score"
                      stroke="#1976d2"
                      strokeWidth={2}
                      dot={{ fill: '#1976d2' }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {tabValue === 1 && (
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Recent Activities
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Action</TableCell>
                        <TableCell>Trust Score</TableCell>
                        <TableCell>Risk Level</TableCell>
                        <TableCell>Decision</TableCell>
                        <TableCell>Timestamp</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trustData.recent_activities?.slice(0, 10).map((activity, index) => (
                        <TableRow key={index}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {activity.action_type === 'login' ? <AccountCircle /> : <ShoppingCart />}
                              {activity.action_type}
                            </Box>
                          </TableCell>
                          <TableCell>{activity.trust_score.toFixed(1)}</TableCell>
                          <TableCell>
                            <Chip
                              label={activity.risk_level}
                              color={
                                activity.risk_level === 'high' ? 'error' :
                                activity.risk_level === 'medium' ? 'warning' : 'success'
                              }
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{activity.decision}</TableCell>
                          <TableCell>{formatTimestamp(activity.timestamp)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}

          {tabValue === 2 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="success.main">
                      How to Improve Your Trust Score
                    </Typography>
                    <Typography variant="body2" component="div">
                      <ul>
                        <li>Use consistent devices for transactions</li>
                        <li>Maintain regular activity patterns</li>
                        <li>Verify your email and phone number</li>
                        <li>Avoid rapid-fire transactions</li>
                        <li>Use secure networks (avoid public WiFi)</li>
                        <li>Keep your account information updated</li>
                      </ul>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={6}>
                <Card>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="warning.main">
                      Security Best Practices
                    </Typography>
                    <Typography variant="body2" component="div">
                      <ul>
                        <li>Enable two-factor authentication</li>
                        <li>Use strong, unique passwords</li>
                        <li>Monitor your account regularly</li>
                        <li>Report suspicious activity immediately</li>
                        <li>Keep your browser and apps updated</li>
                        <li>Be cautious with public computers</li>
                      </ul>
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          )}
        </>
      )}
    </Box>
  );
};

export default UserDashboard;
